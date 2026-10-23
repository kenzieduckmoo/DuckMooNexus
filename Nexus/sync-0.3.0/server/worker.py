#!/usr/bin/python3
"""Root-owned systemd worker. Never execute commands or options from upload data."""
import fcntl
import json
import os
import subprocess
import tempfile
import time
import sys
from pathlib import Path
from sync_core import HASH, atomic_json, verified_read, import_result
import hashlib
import shutil
from bundle import unpack_bundle

BASE = Path('/var/lib/duckmoo-sync')

def run_docker(args, timeout=30):
    return subprocess.run(['/usr/bin/docker', *args], check=True, capture_output=True,
                          text=True, timeout=timeout).stdout

def process(path, config):
    digest = path.stem
    receipt = BASE / 'receipts' / (digest + '.json')
    old = json.loads(receipt.read_text()) if receipt.exists() else {}
    if old.get('status') in ('imported', 'already_imported'):
        path.unlink(missing_ok=True)
        return
    if old.get('retry_after', 0) > time.time():
        return
    name = 'duckmoo-sync-import'
    try:
        raw = verified_read(path, digest)
        # Discover network from the configured existing PostgreSQL container every run.
        container = json.loads(run_docker(['inspect', config['postgres_container']]))[0]
        networks = container['NetworkSettings']['Networks']
        network = config.get('network')
        if not network:
            if len(networks) != 1:
                raise ValueError('Select one PostgreSQL Docker network in config.json')
            network = next(iter(networks))
        if network not in networks or network in ('host', 'none'):
            raise ValueError('Configured network is not a PostgreSQL bridge network')
        # Remove a leftover named importer after a killed worker, before starting another.
        subprocess.run(['/usr/bin/docker', 'rm', '-f', name], capture_output=True, timeout=30)
        with tempfile.TemporaryDirectory(dir=BASE / 'staging') as stage:
            folder = Path(stage)
            os.chmod(folder, 0o755)
            source = folder / 'Journalator.lua'
            source.write_bytes(raw)
            os.chown(source, config['uid'], config['gid'])
            os.chmod(source, 0o400)
            result = import_result(run_docker([
                'run', '--rm', '--name', name, '--user', f"{config['uid']}:{config['gid']}",
                '--network', network, '--env-file', config['env_file'],
                '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
                '--memory=768m', '--pids-limit=64', '--cpus=1',
                '--mount', f'type=bind,src={folder},dst=/input,readonly',
                'duckmoo-nexus:0.1.0', 'import', '/input/Journalator.lua',
                '--namespace', 'retail-main-account'], timeout=600))
        result.update(sha256=digest, completed_at=time.time())
        atomic_json(receipt, result)  # Only after successful DB commit and valid JSON.
        path.unlink(missing_ok=True)
        print(json.dumps(result), flush=True)
    except Exception as exc:
        # Never log stderr: database URLs or source data could appear there.
        subprocess.run(['/usr/bin/docker', 'rm', '-f', name], capture_output=True, timeout=30)
        attempts = old.get('attempts', 0) + 1
        result = dict(status='failed', sha256=digest, error=type(exc).__name__,
                      attempts=attempts, retry_after=time.time() + min(3600, 60 * 2 ** min(attempts, 6)))
        atomic_json(receipt, result)
        print(json.dumps(result), flush=True)


def process_bundle(path, config):
    digest=path.stem
    receipt=BASE/'receipts'/(digest+'.json')
    old=json.loads(receipt.read_text()) if receipt.exists() else {}
    if old.get('status') in ('imported','already_imported','archived'):
        path.unlink(missing_ok=True);return
    if old.get('retry_after',0)>time.time():return
    name='duckmoo-sync-source-import'
    try:
        h=hashlib.sha256()
        with path.open('rb') as inp:
            while block:=inp.read(1024**2):h.update(block)
        if h.hexdigest()!=digest:raise ValueError('Bundle checksum mismatch')
        container=json.loads(run_docker(['inspect',config['postgres_container']]))[0]
        networks=container['NetworkSettings']['Networks']
        network=config.get('network') or (next(iter(networks)) if len(networks)==1 else None)
        if network not in networks or network in ('host','none'):raise ValueError('Invalid PostgreSQL network')
        subprocess.run(['/usr/bin/docker','rm','-f',name],capture_output=True,timeout=30)
        with tempfile.TemporaryDirectory(dir=BASE/'staging') as stage:
            folder=Path(stage);os.chmod(folder,0o755)
            mf,manifest=unpack_bundle(path,folder)
            for source in folder.iterdir():
                os.chown(source,config['uid'],config['gid']);os.chmod(source,0o400)
            output=run_docker(['run','--rm','--name',name,'--user',f"{config['uid']}:{config['gid']}",
                '--network',network,'--env-file',config['env_file'],'--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=2g',
                '--cap-drop=ALL','--security-opt=no-new-privileges','--memory=2g','--pids-limit=64','--cpus=2',
                '--mount',f'type=bind,src={folder},dst=/input,readonly','--entrypoint','python',
                'duckmoo-nexus:0.3.0','source_importer.py','/input/manifest.json'],timeout=3600)
            result=json.loads(output)
            if result.get('status') not in ('archived','imported','already_imported') or type(result.get('snapshot_id')) is not int:
                raise ValueError('Unconfirmed source import')
        result.update(sha256=digest,source_sha256=manifest['sha256'],completed_at=time.time())
        atomic_json(receipt,result)
        path.unlink(missing_ok=True)
        print(json.dumps(result),flush=True)
    except Exception as exc:
        subprocess.run(['/usr/bin/docker','rm','-f',name],capture_output=True,timeout=30)
        attempts=old.get('attempts',0)+1
        atomic_json(receipt,dict(status='failed',sha256=digest,error=type(exc).__name__,attempts=attempts,
                                retry_after=time.time()+min(3600,60*2**min(attempts,6))))

def main(sources=False):
    os.umask(0o077)
    with (BASE / ('source-worker.lock' if sources else 'worker.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config = json.loads(Path('/etc/duckmoo-sync/config.json').read_text())
        if sources:
            for path in sorted((BASE/'inbox').glob('*.bundle'),key=lambda p:p.stat().st_mtime):
                if HASH.fullmatch(path.stem):process_bundle(path,config)
        else:
            for path in sorted((BASE / 'inbox').glob('*.lua'), key=lambda p: p.stat().st_mtime):
                if HASH.fullmatch(path.stem):
                    process(path, config)

if __name__ == '__main__':
    if sys.argv[1:] not in ([], ['--sources']):
        raise SystemExit('Usage: worker.py [--sources]')
    main(sources=sys.argv[1:] == ['--sources'])

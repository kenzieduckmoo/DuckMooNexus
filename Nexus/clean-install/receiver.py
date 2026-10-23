#!/usr/bin/python3
"""Forced-command SSH entrypoint; retains every valid transport packet."""
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path('/var/lib/duckmoo-nexus-sources')
STACK = Path('/opt/duckmoo-nexus-clean')


def known_receipts(digests):
    if not isinstance(digests,list) or len(digests)>10000 or any(not isinstance(d,str) or not re.fullmatch('[a-f0-9]{64}',d) for d in digests):
        raise ValueError('Expected up to 10000 packet identifiers')
    generation=hashlib.sha256((STACK/'.env').read_bytes()).hexdigest()
    committed=[]
    for digest in dict.fromkeys(digests):
        receipt_path=BASE/(digest+'.receipt.json')
        if not (BASE/(digest+'.bundle')).is_file():continue
        try:receipt=json.loads(receipt_path.read_text())
        except (FileNotFoundError,ValueError):continue
        if receipt.get('generation')==generation and receipt.get('sha256')==digest and receipt.get('status') in ('imported','already_imported','archived'):
            committed.append(digest)
    return {'committed':committed}


def main():
    parts = os.environ.get('SSH_ORIGINAL_COMMAND', '').split()
    if parts==['receipts']:
        request=sys.stdin.buffer.read(1024**2+1)
        if len(request)>1024**2:raise ValueError('Receipt request too large')
        with (BASE/'ingest.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            print(json.dumps(known_receipts(json.loads(request))))
        return
    if len(parts) != 3 or parts[0] != 'put' or not re.fullmatch('[a-f0-9]{64}', parts[1]):
        raise ValueError('Expected put SHA256 SIZE')
    size = int(parts[2])
    if not 0 < size <= 512 * 1024**2:
        raise ValueError('Invalid packet size')
    digest = parts[1]
    with (BASE / 'ingest.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        fd, temporary = tempfile.mkstemp(dir=BASE, prefix='.upload-')
        try:
            h = hashlib.sha256()
            with os.fdopen(fd, 'wb') as out:
                remaining = size
                while remaining:
                    block = sys.stdin.buffer.read(min(1024**2, remaining))
                    if not block:
                        raise ValueError('Truncated upload')
                    out.write(block)
                    h.update(block)
                    remaining -= len(block)
                if sys.stdin.buffer.read(1) or h.hexdigest() != digest:
                    raise ValueError('Invalid length or checksum')
                out.flush()
                os.fsync(out.fileno())
            packet = BASE / (digest + '.bundle')
            os.replace(temporary, packet)
            packet.chmod(0o644)
            generation = hashlib.sha256((STACK / '.env').read_bytes()).hexdigest()
            receipt_path = BASE / (digest + '.receipt.json')
            if receipt_path.exists():
                cached = json.loads(receipt_path.read_text())
                if cached.get('generation') == generation:
                    print(json.dumps(cached))
                    return
            result = subprocess.run(
                ['docker', 'compose', '--project-directory', str(STACK), 'run', '--rm', '-T',
                 'ingest', 'ingest', '/sources/' + packet.name],
                capture_output=True, text=True, timeout=3600)
            if result.returncode:
                raise RuntimeError(result.stderr + result.stdout)
            receipt = json.loads(result.stdout)
            receipt['sha256'] = digest
            receipt['generation'] = generation
            receipt_path.write_text(json.dumps(receipt))
            print(json.dumps(receipt))
        finally:
            Path(temporary).unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

"""Content-addressed, compressed raw snapshots, independent of parser completion."""
import argparse
import gzip
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SOURCES = ('Journalator', 'Journalator_Statistics', 'Auctionator', 'Syndicator',
           'DuckMooFolio', 'DuckMooPlanner', 'DuckMooWarband', 'WarbandNexus',
           'WarbandAccountant', 'TradeSkillMaster', 'TradeSkillMaster_AppHelper',
           'DuckMooCapture', 'DuckMooOmniCapture', 'CraftSim', 'AllTheThings', 'WoWthing_Collector', 'TSM_AppData')
MAX_BYTES = 2 * 1024**3


def capture(source, archive, namespace, source_name=None):
    source, archive = Path(source), Path(archive)
    identity = source_name or source.name.removesuffix('.bak')
    if identity.removesuffix('.lua') not in SOURCES or not identity.endswith('.lua'):
        raise ValueError('Unrecognized source')
    archive.mkdir(parents=True, exist_ok=True)
    before = source.stat()
    if not 0 < before.st_size <= MAX_BYTES:
        raise ValueError('Source outside 2 GiB bound')
    fd, name = tempfile.mkstemp(prefix='.capture-', dir=archive)
    try:
        h = hashlib.sha256()
        with source.open('rb') as inp, os.fdopen(fd, 'wb') as out:
            with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=6) as zipped:
                while block := inp.read(1024**2):
                    h.update(block); zipped.write(block)
            out.flush(); os.fsync(out.fileno())
        after = source.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('Source changed while capturing; retry')
        # Rehash the source to reject same-size writes during the copy.
        verify = hashlib.sha256()
        with source.open('rb') as inp:
            while block := inp.read(1024**2):
                verify.update(block)
        final = source.stat()
        if verify.digest() != h.digest() or (final.st_size, final.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('Source changed while verifying; retry')
        sha = h.hexdigest()
        dest = archive / (sha + '.lua.gz')
        os.replace(name, dest)
        stamp = datetime.now(timezone.utc).isoformat()
        manifest = dict(namespace=namespace, source=identity,
                        original_name=source.name, sha256=sha, raw_bytes=after.st_size,
                        saved_at=datetime.fromtimestamp(after.st_mtime, timezone.utc).isoformat(),
                        captured_at=stamp, archive=dest.name, encoding='gzip')
        # Each capture is a separate observation of a content-addressed blob.
        mf = archive / (sha + '-' + source.name + '-' + str(final.st_mtime_ns) + '.json')
        if not mf.exists():
            mf.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        return manifest
    finally:
        if os.path.exists(name):
            os.unlink(name)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('source_directory', type=Path)
    p.add_argument('archive_directory', type=Path)
    p.add_argument('--namespace', default='retail-main-account')
    p.add_argument('--include-backups', action='store_true')
    args = p.parse_args()
    for source in SOURCES:
        for suffix in ('.lua', '.lua.bak') if args.include_backups else ('.lua',):
            path = args.source_directory / (source + suffix)
            if path.exists():
                print(json.dumps(capture(path, args.archive_directory, args.namespace)), flush=True)

"""Normalize already archived Folio/Planner snapshots without re-upload/re-hashing."""
import argparse
import gzip
import json
import os
from pathlib import Path
import tempfile
import psycopg
from character_adapter import CHARACTER_SOURCES,CHARACTER_VERSION
from extended_import import normalize_extended

p=argparse.ArgumentParser()
p.add_argument('--latest-only',action='store_true')
a=p.parse_args()
with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    jobs=conn.execute('''SELECT id,namespace,source FROM nexus.source_snapshots
     WHERE source=ANY(%s) AND normalized_version IS DISTINCT FROM %s
     ORDER BY source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''',
     (list(CHARACTER_SOURCES),CHARACTER_VERSION)).fetchall()
    seen=set(); failures=[]
    for snapshot_id,namespace,source in jobs:
        key=(namespace,source)
        if a.latest_only and key in seen:continue
        seen.add(key)
        try:
            with tempfile.TemporaryDirectory() as folder:
                compressed=Path(folder)/'source.gz'; path=Path(folder)/source
                with compressed.open('wb') as out:
                    for (chunk,) in conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(snapshot_id,)):
                        out.write(chunk)
                with gzip.open(compressed,'rb') as inp,path.open('wb') as out:
                    while block:=inp.read(1024**2):out.write(block)
                with conn.transaction():
                    conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+source,))
                    current=conn.execute('SELECT normalized_version FROM nexus.source_snapshots WHERE id=%s',(snapshot_id,)).fetchone()[0]
                    if current==CHARACTER_VERSION:continue
                    inserted,records=normalize_extended(conn,path,source,namespace,snapshot_id)
                    conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(CHARACTER_VERSION,snapshot_id))
                print(json.dumps(dict(snapshot=snapshot_id,source=source,inserted=inserted,records=records)),flush=True)
        except Exception as exc:
            failures.append(dict(snapshot=snapshot_id,source=source,error=str(exc)))
            print(json.dumps(failures[-1]),flush=True)
    if failures:raise RuntimeError(f'{len(failures)} archived character snapshots could not be normalized; originals retained')

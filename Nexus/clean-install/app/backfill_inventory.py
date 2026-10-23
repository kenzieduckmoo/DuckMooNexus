"""Normalize preserved Syndicator snapshots without touching wallet observations."""
import argparse
import gzip
import json
import os
from pathlib import Path
import tempfile
import psycopg
from savedvariables import read_lua
from inventory_adapter import INVENTORY_SOURCE,INVENTORY_VERSION,normalize_inventory

parser=argparse.ArgumentParser();parser.add_argument('--latest-only',action='store_true');args=parser.parse_args()
with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    jobs=conn.execute('''SELECT id,namespace FROM nexus.source_snapshots WHERE source=%s
        AND normalized_version IS DISTINCT FROM %s ORDER BY source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''',
        (INVENTORY_SOURCE,INVENTORY_VERSION)).fetchall()
    seen=set();failures=[]
    for snapshot_id,namespace in jobs:
        if args.latest_only and namespace in seen:continue
        seen.add(namespace)
        try:
            with tempfile.TemporaryDirectory() as folder:
                archive=Path(folder)/'source.gz';path=Path(folder)/INVENTORY_SOURCE
                with archive.open('wb') as out:
                    for (chunk,) in conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(snapshot_id,)):
                        out.write(chunk)
                with gzip.open(archive,'rb') as inp,path.open('wb') as out:
                    while block:=inp.read(1024**2):out.write(block)
                data=read_lua(path)
            with conn.transaction():
                conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+INVENTORY_SOURCE,))
                if conn.execute('SELECT normalized_version FROM nexus.source_snapshots WHERE id=%s',(snapshot_id,)).fetchone()[0]==INVENTORY_VERSION:continue
                inserted,records=normalize_inventory(conn,data,namespace,snapshot_id)
                conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(INVENTORY_VERSION,snapshot_id))
            print(json.dumps({'snapshot':snapshot_id,'inserted':inserted,'records':records}),flush=True)
        except Exception as exc:
            failures.append(snapshot_id);print(json.dumps({'snapshot':snapshot_id,'error':str(exc)}),flush=True)
    if failures:raise RuntimeError(f'{len(failures)} inventory snapshots failed; originals retained')

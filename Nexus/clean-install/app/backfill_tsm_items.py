"""Normalize only the latest retained TSM item cache, preserving every raw snapshot."""
import gzip,os,tempfile
from pathlib import Path
import psycopg
from savedvariables import read_lua
from tsm_item_adapter import normalize_items,ITEM_SOURCE,ITEM_VERSION

with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    jobs=conn.execute('''SELECT DISTINCT ON(namespace) id,namespace,normalized_version FROM nexus.source_snapshots
      WHERE source=%s ORDER BY namespace,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''',(ITEM_SOURCE,)).fetchall()
    for snapshot_id,namespace,version in jobs:
        if version==ITEM_VERSION:continue
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'source.gz';raw=Path(folder)/ITEM_SOURCE
            with archive.open('wb') as out:
                for (chunk,) in conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(snapshot_id,)):out.write(chunk)
            with gzip.open(archive,'rb') as inp,raw.open('wb') as out:
                while block:=inp.read(1024**2):out.write(block)
            data=read_lua(raw)
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+ITEM_SOURCE,))
            count=normalize_items(conn,data,namespace,snapshot_id)
            conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(ITEM_VERSION,snapshot_id))
        print('TSM item metadata rows normalized:',count,'snapshot',snapshot_id,flush=True)

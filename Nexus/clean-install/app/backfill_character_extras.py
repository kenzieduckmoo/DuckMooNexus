"""Backfill only the latest snapshots for the three character-extra adapters."""
import gzip,os,tempfile
from pathlib import Path
import psycopg
from savedvariables import read_lua
from character_extras import EXTRA_SOURCES,EXTRA_VERSION,normalize_extras
with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    jobs=conn.execute('''SELECT DISTINCT ON(namespace,source) id,namespace,source,normalized_version FROM nexus.source_snapshots
      WHERE source=ANY(%s) ORDER BY namespace,source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''',(list(EXTRA_SOURCES),)).fetchall()
    for snapshot_id,namespace,source,version in jobs:
        if version==EXTRA_VERSION:continue
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'source.gz';raw=Path(folder)/source
            with archive.open('wb') as out:
                for (chunk,) in conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(snapshot_id,)):out.write(chunk)
            with gzip.open(archive,'rb') as inp,raw.open('wb') as out:
                while block:=inp.read(1024**2):out.write(block)
            data=read_lua(raw)
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+source,))
            count=normalize_extras(conn,data,source,namespace,snapshot_id)
            conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(EXTRA_VERSION,snapshot_id))
        print(source,'character extras normalized:',count,flush=True)

"""Add omitted scan-status observations from the latest preserved Capture file."""
from datetime import datetime,timezone
import gzip
import hashlib
import os
from pathlib import Path
import tempfile
import psycopg
from financials import canonical
from savedvariables import read_lua

with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    jobs=conn.execute('''SELECT DISTINCT ON(namespace) id,namespace FROM nexus.source_snapshots
      WHERE source='DuckMooCapture.lua' AND normalized_version IS NOT NULL
      ORDER BY namespace,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''').fetchall()
    for snapshot_id,namespace in jobs:
        if conn.execute("SELECT 1 FROM nexus.snapshot_crafting l JOIN nexus.crafting_observations o ON o.id=l.observation_id WHERE l.snapshot_id=%s AND o.kind='scan_status' LIMIT 1",(snapshot_id,)).fetchone():continue
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'source.gz';raw=Path(folder)/'DuckMooCapture.lua'
            with archive.open('wb') as out:
                for (chunk,) in conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(snapshot_id,)):out.write(chunk)
            with gzip.open(archive,'rb') as inp,raw.open('wb') as out:
                while block:=inp.read(1024**2):out.write(block)
            data=read_lua(raw)['DuckMooCaptureDB']
        count=0
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':DuckMooCapture.lua',))
            for guid,c in data.get('characters',{}).items():
                rows=[('scan_status',str(pid),row) for pid,row in c.get('scanStatus',{}).items()]
                if c.get('captureStatus'):rows.append(('capture_status','status',c['captureStatus']))
                for kind,key,payload in rows:
                    stamp=payload.get('observedAt');identity=hashlib.sha256(canonical([namespace,guid,None,kind,key,stamp,payload]).encode()).hexdigest()
                    conn.execute('''INSERT INTO nexus.crafting_observations VALUES(%s,%s,%s,NULL,%s,%s,%s,%s::jsonb) ON CONFLICT DO NOTHING''',
                      (identity,namespace,guid,kind,key,datetime.fromtimestamp(stamp,timezone.utc) if stamp else None,canonical(payload)))
                    conn.execute('INSERT INTO nexus.snapshot_crafting VALUES(%s,%s) ON CONFLICT DO NOTHING',(snapshot_id,identity));count+=1
        print('Capture status observations added:',count,'from snapshot',snapshot_id,flush=True)

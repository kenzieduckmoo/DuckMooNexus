"""Re-normalize archived Omni snapshots without altering their original bytes."""
import gzip,os,tempfile
from pathlib import Path
import psycopg
from savedvariables import read_lua
from omni_adapter import OMNI_SOURCE,OMNI_VERSION,normalize_omni


def main():
    with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
        snapshots=conn.execute("SELECT id,namespace FROM nexus.source_snapshots WHERE source=%s AND normalized_version IS DISTINCT FROM %s ORDER BY id",(OMNI_SOURCE,OMNI_VERSION)).fetchall()
        for snapshot_id,namespace in snapshots:
            with conn.transaction():
                conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+OMNI_SOURCE,))
                chunks=conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(snapshot_id,)).fetchall()
                if not chunks:raise ValueError('Missing raw archive chunks')
                with tempfile.TemporaryDirectory() as folder:
                    path=Path(folder)/OMNI_SOURCE
                    path.write_bytes(gzip.decompress(b''.join(bytes(row[0]) for row in chunks)))
                    inserted,count=normalize_omni(conn,read_lua(path),namespace,snapshot_id)
                conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(OMNI_VERSION,snapshot_id))
            print(f'Omni archive {snapshot_id}: {count} records, {inserted} new; raw retained',flush=True)

if __name__=='__main__':main()

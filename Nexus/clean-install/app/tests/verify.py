"""Run against a disposable PostgreSQL database and a real SavedVariables file.
python tests/verify.py /path/Journalator.lua
Requires DATABASE_URL. Writes only namespace verification-<random UUID>.
"""
import json, os, sys, uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import psycopg
from decode import parse, decode
from importer import ingest, records, digest

raw=Path(sys.argv[1]).read_bytes()
namespace='verification-'+str(uuid.uuid4())
with psycopg.connect(os.environ['DATABASE_URL']) as conn:
    conn.execute((Path(__file__).resolve().parents[1]/'sql/001_initial.sql').read_text())
    conn.commit()
    first=ingest(conn,raw,'Journalator.lua',namespace)
    second=ingest(conn,raw,'renamed.lua',namespace)
    # Byte-different snapshot, identical archive content.
    third=ingest(conn,raw+b'\n','next-snapshot.lua',namespace)
    assert first['inserted']==first['records']>0
    assert second['inserted']==third['inserted']==0
    with conn.cursor() as c:
        c.execute('SELECT count(*) FROM nexus.transactions WHERE namespace=%s',(namespace,))
        assert c.fetchone()[0]==first['records']
        c.execute('SELECT raw_file FROM nexus.imports WHERE id=%s',(first['import_id'],))
        assert bytes(c.fetchone()[0])==raw
        c.execute('SELECT count(*) FROM nexus.observations o JOIN nexus.imports i ON i.id=o.import_id WHERE i.namespace=%s',(namespace,))
        assert c.fetchone()[0]==2*first['records']
        # A conflicting existing location must roll back the new snapshot entirely.
        c.execute('UPDATE nexus.transactions SET payload_sha256=%s WHERE id=(SELECT id FROM nexus.transactions WHERE namespace=%s LIMIT 1)',('conflict',namespace))
    conn.commit()
    try: ingest(conn,raw+b'\n\n','conflicting.lua',namespace)
    except ValueError: pass
    else: raise AssertionError('Conflict was not rejected')
    assert conn.execute('SELECT count(*) FROM nexus.imports WHERE namespace=%s',(namespace,)).fetchone()[0]==2
    # Remove only test namespace rows, preserving all normal imports.
    conn.execute('DELETE FROM nexus.observations WHERE import_id IN (SELECT id FROM nexus.imports WHERE namespace=%s)',(namespace,))
    conn.execute('DELETE FROM nexus.archives WHERE import_id IN (SELECT id FROM nexus.imports WHERE namespace=%s)',(namespace,))
    conn.execute('DELETE FROM nexus.transactions WHERE namespace=%s',(namespace,))
    conn.execute('DELETE FROM nexus.imports WHERE namespace=%s',(namespace,))
    conn.commit()
for bad in (b'JOURNALATOR_ARCHIVE = os.execute("bad")',raw[:-20],b'while true do end'):
    try: list(decode(bad))
    except (ValueError,KeyError,IndexError): pass
    else: raise AssertionError('Invalid input accepted')
stores=list(decode(raw)); rows=list(records(stores,namespace))
sid,encoded,data=next(s for s in stores if s[2])
category=next(k for k,v in data.items() if isinstance(v,dict) and v)
entry=data[category][1]
duplicates=list(records([(sid,encoded,{'Version':15,category:{1:entry,2:entry}})],namespace))
assert duplicates[0][0]!=duplicates[1][0]
print(json.dumps({'source_sha256':digest(raw),'first':first,'second':second,'changed_bytes_same_records':third,
 'checks':['raw byte preservation','PostgreSQL migration','same-file double import','overlapping snapshot','provenance observations','conflict rollback','data-only parser rejection','identical legitimate records retained']},indent=2))

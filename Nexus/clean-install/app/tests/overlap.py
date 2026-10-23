"""Actual backup->current overlap test; use only a disposable database."""
import os,sys,json,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import psycopg
from importer import ingest
namespace='overlap-'+str(uuid.uuid4())
with psycopg.connect(os.environ['DATABASE_URL']) as c:
    results=[ingest(c,Path(f).read_bytes(),Path(f).name,namespace) for f in sys.argv[1:]]
    results.append(ingest(c,Path(sys.argv[-1]).read_bytes(),'repeat.lua',namespace))
    assert results[-1]['inserted']==0
    assert sum(r['inserted'] for r in results)==results[-1]['records']
    dashboard=json.loads((Path(__file__).resolve().parents[1]/'grafana-dashboard.json').read_text())
    for panel in dashboard['panels']:
        sql=panel['targets'][0]['rawSql'].replace('${account:sqlstring}',"'"+namespace+"'").replace('$__timeFilter(occurred_at)','TRUE')
        c.execute(sql).fetchall()
    print(json.dumps({'imports':results,'dashboard_queries_executed':len(dashboard['panels'])},indent=2))
    c.execute('DELETE FROM nexus.observations WHERE import_id IN (SELECT id FROM nexus.imports WHERE namespace=%s)',(namespace,))
    c.execute('DELETE FROM nexus.archives WHERE import_id IN (SELECT id FROM nexus.imports WHERE namespace=%s)',(namespace,))
    c.execute('DELETE FROM nexus.transactions WHERE namespace=%s',(namespace,))
    c.execute('DELETE FROM nexus.imports WHERE namespace=%s',(namespace,))

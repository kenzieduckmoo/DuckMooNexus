"""Exercise the actual refresh SQL against synthetic temporary PostgreSQL rows."""
import ast,os
from pathlib import Path
import psycopg
tree=ast.parse(Path('/app/craftingdesk/nexus_snapshot.py').read_text())
query=next(n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call)
    and isinstance(n.func,ast.Attribute) and n.func.attr=='execute' and n.args
    and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)
    and "'crafting-0.9.3'" in n.args[0].value)
query=query.replace('nexus.source_snapshots','test_refresh_sources').replace('nexus.api_snapshots','test_refresh_api')
with psycopg.connect(os.environ['DATABASE_URL']) as conn:
    conn.execute('CREATE TEMP TABLE test_refresh_sources(id int,namespace text,source text,normalized_version text,source_saved_at timestamptz,captured_at timestamptz) ON COMMIT DROP')
    conn.execute('CREATE TEMP TABLE test_refresh_api(id int,region text) ON COMMIT DROP')
    for row in [(1,'DuckMooCapture.lua','ready'),(2,'DuckMooCapture.lua',None),(3,'DuckMooOmniCapture.lua','ready'),(4,'TradeSkillMaster.lua',None)]:
        conn.execute("INSERT INTO test_refresh_sources VALUES(%s,'fixture',%s,%s,to_timestamp(%s),to_timestamp(%s))",(*row,row[0],row[0]))
    before=conn.execute(query,('fixture',)).fetchone()[0]
    assert before[1]==[['DuckMooCapture.lua',1,'ready'],['DuckMooOmniCapture.lua',3,'ready'],['TradeSkillMaster.lua',4,None]]
    conn.execute("UPDATE test_refresh_sources SET normalized_version='ready' WHERE id=2")
    after=conn.execute(query,('fixture',)).fetchone()[0]
    assert before!=after and after[1][0][1]==2
    assert conn.execute('SELECT max(id) FROM test_refresh_sources').fetchone()[0]==4
    conn.rollback()
print('Refresh detects a finishing import below the raw max ID; pending observations stay excluded and raw-only TSM stays usable. Temporary rows rolled back.')

"""Run ONLY against the disposable PostgreSQL container in verify-stack.sh.

Uses real archived source files. No fake records are written to a user database.
"""
from pathlib import Path
import gzip
import hashlib
import json
import os
import re
import sys
import psycopg
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from source_importer import ingest_source
from importer import ingest

if os.environ.get('NEXUS_DISPOSABLE_TEST')!='yes':
    raise SystemExit('Use verify-stack.sh; refuses an unmarked database')
root=Path(__file__).resolve().parents[1];fixtures=Path('/fixtures')
with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    for repeat in range(2):
        for sql in sorted((root/'sql').glob('*.sql')):conn.execute(sql.read_text())
    conn.execute('CREATE ROLE nexus_test_importer');conn.execute('CREATE ROLE nexus_test_grafana')
    grants=(root/'sql/grant_roles.psql').read_text().replace(':"importer_role"','nexus_test_importer').replace(':"grafana_role"','nexus_test_grafana')
    conn.execute(grants)
    manifests=[json.loads(p.read_text()) for p in fixtures.glob('*.json') if 'sha256' in json.loads(p.read_text())]
    selected=[m for m in manifests if m['source'] in ('WarbandAccountant.lua','Syndicator.lua','Auctionator.lua','TSM_AppData.lua','DuckMooCapture.lua')]
    assert {m['source'] for m in selected} == {'WarbandAccountant.lua','Syndicator.lua','Auctionator.lua','TSM_AppData.lua','DuckMooCapture.lua'}, 'Required real-source fixtures missing'
    results=[]
    for m in selected:
        archive=fixtures/(m['sha256']+'.lua.gz')
        conn.execute('SET ROLE nexus_test_importer')
        first=ingest_source(conn,archive,m);again=ingest_source(conn,archive,m)
        conn.execute('RESET ROLE')
        assert again['inserted']==0
        chunks=conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(first['snapshot_id'],)).fetchall()
        assert hashlib.sha256(gzip.decompress(b''.join(bytes(r[0]) for r in chunks))).hexdigest()==m['sha256']
        results.append(first)
    journalator=next(m for m in manifests if m['source']=='Journalator.lua' and m['original_name']=='Journalator.lua')
    raw=gzip.decompress((fixtures/journalator['archive']).read_bytes())
    first=ingest(conn,raw,'Journalator.lua','retail-main-account')
    assert ingest(conn,raw,'Journalator.lua','retail-main-account')['inserted']==0
    bank=conn.execute("SELECT copper FROM nexus.warbank_history WHERE namespace='retail-main-account' ORDER BY observed_at DESC LIMIT 1").fetchone()[0]
    assert bank>0
    query_count=0
    conn.execute('SET ROLE nexus_test_grafana')
    for path in (root/'grafana').glob('*.json'):
        dashboard=json.loads(path.read_text())
        for variable in dashboard['templating']['list']:
            if variable['type']=='query':
                conn.execute(variable['query']).fetchall()
                query_count+=1
        for panel in dashboard['panels']:
            for target in panel.get('targets',[]):
                sql=target['rawSql'].replace('${account:sqlstring}',"'retail-main-account'").replace('${item:sqlstring}',"'241281'").replace('${__to}','1792486800000')
                sql=re.sub(r'\$__timeFilter\(([^)]+)\)',r"\1 BETWEEN '2026-01-01'::timestamptz AND '2027-01-01'::timestamptz",sql)
                conn.execute(sql).fetchall();query_count+=1
    # Reader cannot retrieve preserved source bytes or change snapshots.
    assert not conn.execute("SELECT has_table_privilege(current_user,'nexus.snapshot_chunks','SELECT')").fetchone()[0]
    assert not conn.execute("SELECT has_table_privilege(current_user,'nexus.source_snapshots','INSERT')").fetchone()[0]
    conn.execute('SELECT * FROM nexus.warbank_history LIMIT 1').fetchall()
    conn.execute('SELECT * FROM nexus.financial_components LIMIT 1').fetchall()
    conn.execute('RESET ROLE')
    print(json.dumps(dict(source_imports=results,journalator=first,latest_warbank_copper=bank,dashboard_queries=query_count,
                          checks=['migrations repeatable','source archive bytes exact','source imports under restricted role','source repeat imports insert zero','Journalator regression','all dashboard and variable SQL under Grafana role','Grafana raw archive and write access denied']),indent=2))

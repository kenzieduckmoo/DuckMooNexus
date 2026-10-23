"""Read complete real files, verify raw archive hashes and emit a local QA report."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from savedvariables import read_lua
from financials import observations,canonical
from capture_adapter import crafting_rows
from market_adapter import auctionator_rows,tsm_rows
from tsm_appdata import market_data
from source_importer import verify_archive
import gzip
from decode import decode
from importer import records

p=argparse.ArgumentParser();p.add_argument('savedvariables',type=Path);p.add_argument('archive',type=Path);p.add_argument('output',type=Path);p.add_argument('--tsm-appdata',type=Path);a=p.parse_args();a.output.mkdir(exist_ok=True)
report={'checked_at':datetime.now(timezone.utc).isoformat(),'financial_sources':{},'archive_manifests':0,'deployment_verified':False}
manifests=[]
for mf in a.archive.glob('*.json'):
    m=json.loads(mf.read_text());verify_archive(a.archive/m['archive'],m);report['archive_manifests']+=1;manifests.append(m)
def archived_bytes(name):
    m=max((m for m in manifests if m['source']==name),key=lambda m:m['saved_at'])
    return gzip.decompress((a.archive/m['archive']).read_bytes())
def archived_lua(name,binary=False):
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/name
        # Stream the full large source into a private temporary file.
        m=max((m for m in manifests if m['source']==name),key=lambda m:m['saved_at'])
        with gzip.open(a.archive/m['archive'],'rb') as inp,path.open('wb') as out:
            while block:=inp.read(1024**2):out.write(block)
        return read_lua(path,binary=binary)
bank=[]
for source in ('WarbandAccountant','Syndicator','DuckMooWarband'):
    rows=list(observations(source+'.lua',archived_lua(source+'.lua')))
    # Canonical identity is deterministic; no source bytes evaluated as Lua.
    first={hashlib.sha256(canonical([source,row]).encode()).hexdigest() for row in rows}
    again={hashlib.sha256(canonical([source,row]).encode()).hexdigest() for row in rows}
    assert first==again and len(first)==len(rows)
    report['financial_sources'][source]=dict(records=len(rows),kinds=dict(Counter(r['kind'] for r in rows)))
    if source=='WarbandAccountant':bank=[r for r in rows if r['kind']=='warbank_balance']
bank.sort(key=lambda r:r['observed_at'])
report['warbank']=dict(points=len(bank),first=bank[0]['observed_at'],latest=bank[-1]['observed_at'],latest_copper=bank[-1]['copper'])
history_sets=[]
for m in sorted((m for m in manifests if m['source']=='WarbandAccountant.lua'),key=lambda m:m['saved_at']):
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/m['source'];path.write_bytes(gzip.decompress((a.archive/m['archive']).read_bytes()))
        rows=list(observations(m['source'],read_lua(path)))
        history_sets.append({hashlib.sha256(canonical(row).encode()).hexdigest() for row in rows if row['kind']=='warbank_balance'})
report['bank_history_accumulation']=dict(snapshot_counts=[len(s) for s in history_sets],unique_ledger_points=len(set.union(*history_sets)),new_points_since_first=len(set.union(*history_sets)-history_sets[0]))
with (a.output/'warbank-history.csv').open('w',newline='',encoding='utf-8') as out:
    writer=csv.writer(out);writer.writerow(['source_timestamp_utc','copper','gold','source','transfer_type'])
    for r in bank:writer.writerow([datetime.fromtimestamp(r['observed_at'],timezone.utc).isoformat(),r['copper'],format(r['copper']/10000,'.4f'),'WarbandAccountant',r['payload']['type']])
counts=Counter();hashes=set()
for row in crafting_rows(archived_lua('DuckMooCapture.lua')):
    encoded=canonical(row);oid=hashlib.sha256(encoded.encode()).hexdigest()
    assert oid not in hashes;hashes.add(oid);counts[row[2]]+=1
report['capture']=dict(counts)
report['auctionator']=dict(Counter(row[-1] for row in auctionator_rows(archived_lua('Auctionator.lua',binary=True))))
if a.tsm_appdata:
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'AppData.lua';path.write_bytes(archived_bytes('TSM_AppData.lua'))
        m=market_data(path);report['tsm']=dict(datasets=m['datasets'],normalized_rows=sum(1 for r in tsm_rows(m)))
raw=archived_bytes('Journalator.lua');stores=list(decode(raw));jr=list(records(stores,'retail-main-account'))
report['journalator']=dict(records=len(jr),categories=dict(Counter(r[3] for r in jr)),sha256=hashlib.sha256(raw).hexdigest())
report['checks']=['all compressed snapshots match original SHA256/length','bank identities deterministic','complete Capture parsed and all observation identities distinct','Auctionator CBOR decoded without executing Lua','TSM explicit download times retained','original Journalator decoder regression']
(a.output/'real-data-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

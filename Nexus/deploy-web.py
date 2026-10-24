from datetime import datetime,timezone
from pathlib import Path
import os,secrets,shutil,subprocess
root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True)
for name in ['web','compose.web.yaml']:
 if (root/name).exists():
  if (root/name).is_dir():shutil.copytree(root/name,backup/name)
  else:shutil.copy2(root/name,backup/name)
for name in ['api_worker.py','item_media.py','source_importer.py','tsm_item_adapter.py','item_cache.py']:
 if (root/'app'/name).exists():shutil.copy2(root/'app'/name,backup/name)
subprocess.run(['tar','-xzf','/home/kenzieduckmoo/nexus-web-current.tar.gz','-C',str(root)],check=True)
private=root/'web.env'
if not private.exists():
 password=secrets.token_hex(32)
 private.touch(mode=0o600);private.write_text('DATABASE_URL=postgresql://nexus_web:'+password+'@postgres/nexus\n')
else:password=private.read_text().split('nexus_web:',1)[1].split('@',1)[0]
private.chmod(0o600)
query="DO $$ BEGIN IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname='nexus_web') THEN CREATE ROLE nexus_web LOGIN PASSWORD '"+password+"'; END IF; END $$;\n"
query+=(root/'app/sql/012_item_quality.sql').read_text()+'\nGRANT SELECT ON nexus.item_quality_evidence,nexus.item_qualities TO grafana;\n'
query+='ALTER ROLE nexus_web SET default_transaction_read_only=on; GRANT USAGE ON SCHEMA nexus TO nexus_web; GRANT SELECT ON '
query+=','.join('nexus.'+n for n in ['character_roster','character_professions','item_catalog','latest_api_snapshots','warbank_history','source_snapshots','auction_listings','api_item_metadata','api_snapshots','current_inventory','market_observations','item_qualities'])+' TO nexus_web;'
if (root/'app/sql/019_buying_advisor.sql').is_file():query+=(root/'app/sql/019_buying_advisor.sql').read_text()
subprocess.run(['docker','compose','--project-directory',str(root),'exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=query,text=True,check=True)
subprocess.run(['docker','compose','--project-directory',str(root),'build','--quiet','ingest'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(['docker','compose','--project-directory',str(root),'run','--rm','-T','--entrypoint','python','ingest','/app/backfill_tsm_items.py'],stdin=subprocess.DEVNULL,check=True)
with (backup/'icon-enrichment.log').open('w') as log:
 subprocess.Popen(['docker','compose','--project-directory',str(root),'-f',str(root/'compose.yaml'),'-f',str(root/'compose.api.yaml'),'run','--rm','-T','--entrypoint','python','api','/app/item_media.py'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
compose=['docker','compose','--ansi','never','--project-directory',str(root),'-f',str(root/'compose.yaml'),'-f',str(root/'compose.web.yaml')]
subprocess.run(compose+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Nexus website deployed: http://10.20.30.239',flush=True)
print('Backup:',backup,flush=True)

"""Run as administrator on Nexus; preserve runtime state and back up changed code."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,tarfile,shutil
r=Path('/opt/duckmoo-nexus-clean')
bundle=Path('/home/kenzieduckmoo/nexus-character-craft.tar.gz')
b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-character-craft');b.mkdir(parents=True)
with tarfile.open(bundle) as archive:
 for member in archive.getmembers():
  old=r/member.name
  if old.is_file():
   dest=b/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
base=['docker','compose','--ansi','never','--project-directory',str(r)]
def sql(query):subprocess.run(base+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=query,text=True,check=True)
sql((r/'app/sql/013_character_profiles.sql').read_text()+'\n'+(r/'app/sql/014_character_extras.sql').read_text()+'''
GRANT SELECT ON nexus.current_character_extras,nexus.crafting_documents TO nexus_web;
UPDATE nexus.character_api_documents d SET profile_observed_at=to_timestamp((s.payload->>'last_login_timestamp')::numeric/1000)
FROM nexus.character_api_documents s WHERE d.profile_observed_at IS NULL AND s.namespace=d.namespace AND s.character_guid=d.character_guid
AND s.endpoint='summary' AND s.status=200 AND s.payload ? 'last_login_timestamp'
AND s.last_checked_at=(SELECT max(t.last_checked_at) FROM nexus.character_api_documents t WHERE t.namespace=d.namespace AND t.character_guid=d.character_guid AND t.endpoint='summary' AND t.status=200 AND t.last_checked_at<=d.last_checked_at);
''')
subprocess.run(base+['build','--quiet','ingest'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(base+['run','--rm','-T','--entrypoint','python','ingest','/app/backfill_character_extras.py'],stdin=subprocess.DEVNULL,check=True)
compose=base+sum((['-f',str(r/f)] for f in ['compose.yaml','compose.crafting.yaml','compose.engine.yaml','compose.web.yaml']),[])
subprocess.run(compose+['build','craft-engine','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','crafting','craft-engine','web'],stdin=subprocess.DEVNULL,check=True)
print('Character sheets and native Crafting Desk deployed. Backup:',b,flush=True)

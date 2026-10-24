"""Refresh profession-resource plumbing without touching saved crafting choices."""
from pathlib import Path
from datetime import datetime,timezone
import tarfile,shutil,subprocess
r=Path('/opt/duckmoo-nexus-clean');b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-profession-resources');b.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-profession-resources.tar.gz') as archive:
 for entry in archive.getmembers():
  if not entry.name.startswith(('web/','app/')) or '..' in Path(entry.name).parts:raise ValueError('Unexpected source path')
  old=r/entry.name
  if old.is_file():
   dest=b/entry.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
for name in ('local-data.json.gz','source-signature.json'):
 p=Path('/var/lib/duckmoo-crafting')/name
 if p.is_file():shutil.copy2(p,b/name)
base=['docker','compose','--ansi','never','--project-directory',str(r)]
subprocess.run(base+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=(r/'app/sql/018_crafting_omni_resources.sql').read_text(),text=True,check=True)
subprocess.run(base+['build','ingest'],stdin=subprocess.DEVNULL,check=True)
craft=base+['-f',str(r/'compose.yaml'),'-f',str(r/'compose.crafting.yaml')]
subprocess.run(craft+['run','--rm','-T','--no-deps','crafting-refresh'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(craft+['up','-d','--no-deps','crafting'],stdin=subprocess.DEVNULL,check=True)
web=base+['-f',str(r/'compose.yaml'),'-f',str(r/'compose.web.yaml')]
subprocess.run(web+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(web+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Profession resource model and board deployed. Saved choices untouched. Backup:',b,flush=True)

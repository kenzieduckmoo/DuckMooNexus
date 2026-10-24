"""Apply the prepared read-only buying advisor website update with source backup."""
from pathlib import Path
from datetime import datetime,timezone
import tarfile,shutil,subprocess
r=Path('/opt/duckmoo-nexus-clean')
b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-buying-advisor');b.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-buying-advisor.tar.gz') as archive:
 for entry in archive.getmembers():
  if not (entry.name.startswith(('web/','app/sql/')) or entry.name=='app/item_names.py') or '..' in Path(entry.name).parts:raise ValueError('Unexpected website update path')
  old=r/entry.name
  if old.is_file():
   dest=b/entry.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
subprocess.run(['docker','compose','--project-directory',str(r),'exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=(r/'app/sql/019_buying_advisor.sql').read_text(),text=True,check=True)
subprocess.run(['docker','compose','--project-directory',str(r),'build','ingest'],stdin=subprocess.DEVNULL,check=True)
web=['docker','compose','--ansi','never','--project-directory',str(r),'-f',str(r/'compose.yaml'),'-f',str(r/'compose.web.yaml')]
subprocess.run(web+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(web+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Buying advisor deployed. Backup:',b,flush=True)

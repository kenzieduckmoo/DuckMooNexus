"""Apply the prepared website update, retaining replaced sources for rollback."""
from pathlib import Path
from datetime import datetime,timezone
import tarfile,shutil,subprocess
r=Path('/opt/duckmoo-nexus-clean')
b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-profession-board');b.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-profession-board.tar.gz') as archive:
 for entry in archive.getmembers():
  if not entry.name.startswith('web/') or '..' in Path(entry.name).parts:raise ValueError('Unexpected website update path')
  old=r/entry.name
  if old.is_file():
   dest=b/entry.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
web=['docker','compose','--ansi','never','--project-directory',str(r),'-f',str(r/'compose.yaml'),'-f',str(r/'compose.web.yaml')]
subprocess.run(web+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(web+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Profession board website deployed. Backup:',b,flush=True)

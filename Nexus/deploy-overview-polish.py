"""Update only the Nexus website; preserve existing code and runtime data."""
from pathlib import Path
from datetime import datetime,timezone
import shutil,subprocess,tarfile
root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-overview-polish')
backup.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-overview-polish.tar.gz') as archive:
 for member in archive.getmembers():
  path=root/member.name
  if path.is_file():
   destination=backup/member.name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,destination)
 archive.extractall(root,filter='data')
compose=['docker','compose','--ansi','never','--project-directory',str(root),'-f',str(root/'compose.yaml'),'-f',str(root/'compose.web.yaml')]
subprocess.run(compose+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Website polish deployed. Backup:',backup,flush=True)

from pathlib import Path
from datetime import datetime,timezone
import tarfile,shutil,subprocess
root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-character-progress')
backup.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-character-progress.tar.gz') as archive:
 for entry in archive.getmembers():
  previous=root/entry.name
  if previous.is_file():
   target=backup/entry.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(previous,target)
 archive.extractall(root,filter='data')
compose=['docker','compose','--ansi','never','--project-directory',str(root),'-f',str(root/'compose.yaml'),'-f',str(root/'compose.web.yaml')]
subprocess.run(compose+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Character progress deployed. Backup:',backup,flush=True)

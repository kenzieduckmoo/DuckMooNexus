"""Deploy roster profession-slot display without modifying saved game data."""
from pathlib import Path
from datetime import datetime,timezone
import shutil,subprocess,tarfile
root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-profession-slots')
backup.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-profession-slots.tar.gz') as archive:
    for member in archive.getmembers():
        if member.name.startswith('/') or '..' in Path(member.name).parts:raise ValueError('Invalid path')
        existing=root/member.name
        if existing.is_file():
            dest=backup/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(existing,dest)
    archive.extractall(root,filter='data')
compose=['docker','compose','--project-directory',str(root)]
for name in ['compose.yaml','compose.crafting.yaml','compose.engine.yaml','compose.web.yaml']:compose+=['-f',str(root/name)]
subprocess.run(compose+['build','web'],check=True,stdin=subprocess.DEVNULL)
subprocess.run(compose+['up','-d','--no-deps','web'],check=True,stdin=subprocess.DEVNULL)
print('Profession slot roster deployed. Source backup:',backup,flush=True)

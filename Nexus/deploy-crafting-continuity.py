"""Fix cross-character crafting continuity without altering saved documents."""
from pathlib import Path
from datetime import datetime, timezone
import shutil, subprocess, tarfile

root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-crafting-continuity')
backup.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-crafting-continuity.tar.gz') as archive:
    for member in archive.getmembers():
        if member.name.startswith('/') or '..' in Path(member.name).parts:
            raise ValueError('Invalid update path')
        old=root/member.name
        if old.is_file():
            saved=backup/member.name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,saved)
    archive.extractall(root,filter='data')
for name in ('local-data.json.gz','source-signature.json','status.json'):
    path=Path('/var/lib/duckmoo-crafting')/name
    if path.exists():shutil.copy2(path,backup/name)
base=['docker','compose','--ansi','never','--project-directory',str(root)]
compose=base+sum((['-f',str(root/f)] for f in ['compose.yaml','compose.crafting.yaml','compose.engine.yaml','compose.web.yaml']),[])
subprocess.run(compose+['build','ingest','craft-engine','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['run','--rm','-T','--no-deps','crafting-refresh'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','craft-engine','web'],stdin=subprocess.DEVNULL,check=True)
print('Crafting continuity deployed. Saved documents untouched. Backup:',backup,flush=True)

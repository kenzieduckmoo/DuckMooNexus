from pathlib import Path
from datetime import datetime,timezone
import shutil,subprocess,tarfile
root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-auction-recovery')
backup.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-auction-recovery.tar.gz') as archive:
    for member in archive.getmembers():
        if member.name.startswith('/') or '..' in Path(member.name).parts:raise ValueError('Invalid path')
        existing=root/member.name
        if existing.is_file():
            dest=backup/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(existing,dest)
    archive.extractall(root,filter='data')
compose=['docker','compose','--project-directory',str(root),'-f',str(root/'compose.yaml'),'-f',str(root/'compose.api.yaml')]
subprocess.run(compose+['build','ingest'],check=True,stdin=subprocess.DEVNULL)
# The API timer uses the rebuilt shared ingest image, without restarting unrelated services.
subprocess.run(['systemctl','start','duckmoo-nexus-api.timer'],check=True)
subprocess.run(['systemctl','start','--no-block','duckmoo-nexus-api.service'],check=True)
print('Auction recovery deployed. Source backup:',backup,flush=True)

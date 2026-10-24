from pathlib import Path
from datetime import datetime,timezone
import tarfile,shutil,subprocess
r=Path('/opt/duckmoo-nexus-clean');b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-omni-capture');b.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-omni-capture.tar.gz') as archive:
 for entry in archive.getmembers():
  old=r/entry.name
  if old.is_file():
   dest=b/entry.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
base=['docker','compose','--ansi','never','--project-directory',str(r)]
sql=(r/'app/sql/015_omni_capture.sql').read_text()+(r/'app/sql/016_omni_logout_recovery.sql').read_text()+(r/'app/sql/017_omni_rotated_recovery.sql').read_text()+'\nGRANT SELECT ON nexus.current_omni_records TO nexus_web;'
subprocess.run(base+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=sql,text=True,check=True)
subprocess.run(base+['build','ingest'],stdin=subprocess.DEVNULL,check=True)
web=base+['-f',str(r/'compose.yaml'),'-f',str(r/'compose.web.yaml')]
subprocess.run(web+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(web+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Omni ingestion and website deployed. Backup:',b,flush=True)

"""Deploy the independent Forever ingest channel and Adventure Journal."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,tarfile,shutil
r=Path('/opt/duckmoo-nexus-clean');b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-forever-ready');b.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-forever-ready.tar.gz') as a:
 for member in a.getmembers():
  old=r/member.name
  if old.is_file():
   dest=b/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 a.extractall(r,filter='data')
base=['docker','compose','--ansi','never','--project-directory',str(r)]
subprocess.run(base+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input='BEGIN;\n'+(r/'app/sql/021_omni_lives.sql').read_text()+'\nCOMMIT;\n',text=True,check=True)
compose=base+sum((['-f',str(r/f)] for f in ['compose.yaml','compose.crafting.yaml','compose.engine.yaml','compose.web.yaml']),[])
subprocess.run(compose+['build','ingest','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Forever ingest and Adventure Journal deployed. Backup:',b,flush=True)

from pathlib import Path
from datetime import datetime,timezone
import subprocess,tarfile,shutil
r=Path('/opt/duckmoo-nexus-clean');bundle=Path('/home/kenzieduckmoo/nexus-profession-guides.tar.gz')
b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-profession-guides');b.mkdir(parents=True)
with tarfile.open(bundle) as archive:
 for member in archive.getmembers():
  if member.name.startswith('/') or '..' in Path(member.name).parts:raise ValueError('Invalid update path')
  old=r/member.name
  if old.is_file():
   dest=b/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
base=['docker','compose','--ansi','never','--project-directory',str(r)]
subprocess.run(base+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input='BEGIN;\n'+(r/'app/sql/020_guide_progress.sql').read_text()+'\nCOMMIT;\n',text=True,check=True)
compose=base+sum((['-f',str(r/f)] for f in ['compose.yaml','compose.crafting.yaml','compose.engine.yaml','compose.web.yaml']),[])
subprocess.run(compose+['build','ingest','craft-engine','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','crafting'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','craft-engine','web'],stdin=subprocess.DEVNULL,check=True)
print('Profession guides deployed. Source backup:',b,flush=True)

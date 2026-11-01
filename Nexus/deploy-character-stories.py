"""Deploy character writing and evidence views; never modify captured history."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse,unquote
import os,secrets,shutil,subprocess,tarfile
root=Path('/opt/duckmoo-nexus-clean')
backup=root/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-character-stories')
backup.mkdir(parents=True,mode=0o700)
with tarfile.open('/home/kenzieduckmoo/nexus-character-stories.tar.gz') as archive:
    for member in archive.getmembers():
        if member.name.startswith('/') or '..' in Path(member.name).parts:raise ValueError('Invalid path')
        existing=root/member.name
        if existing.is_file():
            dest=backup/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(existing,dest)
    archive.extractall(root,filter='data')
private=root/'web.env'
shutil.copy2(private,backup/'web.env')
env=private.read_text()
line=next((s for s in env.splitlines() if s.startswith('STORY_DATABASE_URL=')),None)
password=unquote(urlparse(line.split('=',1)[1]).password or '') if line else secrets.token_hex(32)
if not password:raise ValueError('Story storage credential is empty')
query=(root/'app/sql/022_character_stories.sql').read_text()
query+="\nDO $$ BEGIN IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname='nexus_story_writer') THEN CREATE ROLE nexus_story_writer LOGIN PASSWORD '"+password.replace("'","''")+"'; END IF; END $$;\n"
query+='GRANT USAGE ON SCHEMA nexus TO nexus_story_writer; GRANT SELECT,INSERT,UPDATE ON nexus.character_stories TO nexus_story_writer;'
compose=['docker','compose','--project-directory',str(root)]
for name in ['compose.yaml','compose.crafting.yaml','compose.engine.yaml','compose.web.yaml']:compose+=['-f',str(root/name)]
result=subprocess.run(compose+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=query,text=True,capture_output=True)
(backup/'migration.log').write_text(result.stdout+result.stderr)
if result.returncode:raise RuntimeError('Story migration failed; inspect the private migration log')
if not line:
    temporary=private.with_suffix('.stories.tmp')
    fd=os.open(temporary,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w') as out:out.write(env.rstrip()+'\nSTORY_DATABASE_URL=postgresql://nexus_story_writer:'+password+'@postgres/nexus\n')
    temporary.replace(private)
private.chmod(0o600)
subprocess.run(compose+['build','web'],check=True,stdin=subprocess.DEVNULL)
subprocess.run(compose+['up','-d','--no-deps','web'],check=True,stdin=subprocess.DEVNULL)
print('Character stories deployed. Source and private configuration backup:',backup,flush=True)

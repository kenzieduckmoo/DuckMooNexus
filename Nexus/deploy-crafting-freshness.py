"""Deploy normalized-source refresh tracking, preserving sources and saved choices."""
from pathlib import Path
from datetime import datetime,timezone
import shutil,subprocess
r=Path('/opt/duckmoo-nexus-clean');b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-crafting-freshness');b.mkdir(parents=True)
p=r/'app/craftingdesk/nexus_snapshot.py';shutil.copy2(p,b/'nexus_snapshot.py')
for name in ('local-data.json.gz','source-signature.json','status.json'):
 q=Path('/var/lib/duckmoo-crafting')/name
 if q.is_file():shutil.copy2(q,b/name)
shutil.copy2('/home/kenzieduckmoo/nexus_snapshot.py',p)
shutil.copy2('/home/kenzieduckmoo/test-crafting-refresh-signature.py',r/'app/craftingdesk/test_refresh_signature.py')
base=['docker','compose','--ansi','never','--project-directory',str(r)]
subprocess.run(base+['build','ingest'],stdin=subprocess.DEVNULL,check=True)
craft=base+['-f',str(r/'compose.yaml'),'-f',str(r/'compose.crafting.yaml')]
subprocess.run(craft+['run','--rm','-T','--no-deps','--entrypoint','python','crafting-refresh','/app/craftingdesk/test_refresh_signature.py'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(craft+['run','--rm','-T','--no-deps','crafting-refresh'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(craft+['up','-d','--no-deps','crafting'],stdin=subprocess.DEVNULL,check=True)
print('Crafting freshness deployed. Backup:',b,flush=True)

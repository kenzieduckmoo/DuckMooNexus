"""Add the native read-only financial workspace to the existing Nexus website."""
from pathlib import Path
from datetime import datetime,timezone
import tarfile,shutil,subprocess
r=Path('/opt/duckmoo-nexus-clean');b=r/'web-update-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-native-finances');b.mkdir(parents=True)
with tarfile.open('/home/kenzieduckmoo/nexus-native-finances.tar.gz') as archive:
 for member in archive.getmembers():
  old=r/member.name
  if old.is_file():
   dest=b/member.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 archive.extractall(r,filter='data')
base=['docker','compose','--ansi','never','--project-directory',str(r)]
query='GRANT SELECT ON nexus.recorded_cash_events,nexus.cash_financial_components,nexus.crafting_order_financials,nexus.auction_deposit_events,nexus.character_records TO nexus_web;'
subprocess.run(base+['exec','-T','postgres','psql','-U','nexus','-d','nexus','-v','ON_ERROR_STOP=1','-q'],input=query,text=True,check=True)
compose=base+['-f',str(r/'compose.yaml'),'-f',str(r/'compose.web.yaml')]
subprocess.run(compose+['build','web'],stdin=subprocess.DEVNULL,check=True)
subprocess.run(compose+['up','-d','--no-deps','web'],stdin=subprocess.DEVNULL,check=True)
print('Native financial workspace deployed. Backup:',b,flush=True)

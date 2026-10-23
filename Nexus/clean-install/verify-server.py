"""Called after source upload, never treats a running container as success."""
import base64
import argparse
import getpass
import json
import pathlib
import subprocess
import time
import urllib.request
import urllib.error

root = pathlib.Path('/opt/duckmoo-nexus-clean')
parser=argparse.ArgumentParser()
parser.add_argument('--prompt-grafana-password',action='store_true')
args=parser.parse_args()
subprocess.run(['docker','compose','--project-directory',str(root),'run','--rm','-T','ingest','verify'],check=True)
env = dict(line.split('=',1) for line in (root/'.env').read_text().splitlines())
password=getpass.getpass('Grafana password: ') if args.prompt_grafana_password else env['GRAFANA_PASSWORD']
auth = base64.b64encode(('admin:'+password).encode()).decode()
for attempt in range(60):
    try:
        for uid in ('duckmoo-warband-financials','duckmoo-azeroth-stock-exchange'):
            request = urllib.request.Request('http://127.0.0.1:3000/api/dashboards/uid/'+uid,headers={'Authorization':'Basic '+auth})
            with urllib.request.urlopen(request,timeout=5) as response:
                dashboard = json.load(response)
                # UI-owned dashboards are valid; provisioning is not required.
                assert dashboard['dashboard'].get('editable', True), uid
        request = urllib.request.Request('http://127.0.0.1:3000/api/datasources/uid/duckmoo-postgres/health',headers={'Authorization':'Basic '+auth})
        with urllib.request.urlopen(request,timeout=10) as response:
            health=json.load(response)
            if health.get('status') != 'OK': raise RuntimeError(health)
        break
    except urllib.error.HTTPError as exc:
        if exc.code in (401,403):
            raise RuntimeError('Grafana login rejected; use --prompt-grafana-password for the current login.') from None
        if attempt == 59:raise
        time.sleep(2)
    except Exception:
        if attempt == 59: raise
        time.sleep(2)
print('Verified: PostgreSQL contains source records; both dashboards exist and datasource is healthy.')

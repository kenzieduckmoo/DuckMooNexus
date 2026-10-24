"""Nexus-hosted Crafting Desk; desktop server.py remains an optional fallback."""
import gzip
import json
import os
import shutil
import signal
import sys
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
from nexus_storage import read_document,read_document_versioned,save_document,DocumentConflict
from setups import validate_setups,validate_plan
from guide_workspace import validate_guides
from nexus_data_api import Handler as NexusAuthorization

BASE=Path(__file__).resolve().parent
STATE=Path(os.environ.get('CRAFTING_STATE','/crafting-state'))
LOCK=threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def authorized(self):
        if os.environ.get('CRAFTING_ACCESS','grafana')!='lan':
            return NexusAuthorization.authorized(self)
        # Only explicitly configured hostnames may access the unauthenticated LAN app.
        # This also prevents a hostile webpage from using DNS rebinding to reach it.
        allowed=set(os.environ.get('CRAFTING_ORIGINS','http://10.20.30.239:8765').split(','))
        if 'http://'+self.headers.get('Host','') in allowed:return True
        self.send(b'{"error":"Use the configured Nexus address."}',status=403)
        return False
    def send(self,body,kind='application/json',status=200,headers=None):
        self.send_response(status);self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        if status==401:self.send_header('WWW-Authenticate','Basic realm="DuckMoo Nexus"')
        for key,value in (headers or {}).items():self.send_header(key,value)
        self.end_headers();self.wfile.write(body)
    def snapshot(self):
        compressed=STATE/'local-data.json.gz'
        if not compressed.exists():return self.send(b'{"error":"Nexus is preparing the first crafting snapshot. Refresh shortly."}',status=503)
        if 'gzip' in self.headers.get('Accept-Encoding',''):
            self.send_response(200);self.send_header('Content-Type','application/json')
            self.send_header('Content-Encoding','gzip');self.send_header('Content-Length',str(compressed.stat().st_size))
            self.send_header('Cache-Control','no-store');self.end_headers()
            with compressed.open('rb') as inp:shutil.copyfileobj(inp,self.wfile)
        else:
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
            with gzip.open(compressed,'rb') as inp:shutil.copyfileobj(inp,self.wfile)
    def do_GET(self):
        if not self.authorized():
            if os.environ.get('CRAFTING_ACCESS','grafana')!='lan':self.send(b'{"error":"Sign in with your existing Nexus login."}',status=401)
            return
        path=urlsplit(self.path).path
        if path in ('/api/setups','/api/plan','/api/guides'):
            value,revision=read_document_versioned(path.rsplit('/',1)[1])
            return self.send(json.dumps(value,ensure_ascii=False).encode(),headers={'ETag':'"'+revision+'"'})
        if path=='/api/data':return self.snapshot()
        if path=='/api/status':return self.send((STATE/'status.json').read_bytes() if (STATE/'status.json').exists() else b'{}')
        if path=='/':return self.send((BASE/'index.html').read_bytes(),'text/html; charset=utf-8')
        name=path.removeprefix('/')
        if '/' not in name and name.endswith('.js') and (BASE/name).is_file():
            return self.send((BASE/name).read_bytes(),'text/javascript; charset=utf-8')
        if '/' not in name and name.startswith('DuckMooCapture-') and name.endswith('.zip') and (BASE/'downloads'/name).is_file():
            return self.send((BASE/'downloads'/name).read_bytes(),'application/zip')
        self.send(b'{}',status=404)
    def do_POST(self):
        if not self.authorized():
            if os.environ.get('CRAFTING_ACCESS','grafana')!='lan':self.send(b'{"error":"Sign in with your existing Nexus login."}',status=401)
            return
        if self.path not in ('/api/import','/api/setups','/api/plan','/api/guides'):return self.send(b'{}',status=404)
        allowed=set(os.environ.get('CRAFTING_ORIGINS','http://10.20.30.239:8765').split(','))
        if self.headers.get('Origin') is not None and self.headers['Origin'] not in allowed:return self.send(b'{}',status=403)
        try:
            with LOCK:
                if self.path in ('/api/setups','/api/plan','/api/guides'):
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0<length<=1000000:raise ValueError('Invalid saved-plan request size')
                    validator=validate_guides if self.path=='/api/guides' else validate_plan if self.path=='/api/plan' else validate_setups
                    value=validator(json.loads(self.rfile.read(length)))
                    value,revision=save_document(self.path.rsplit('/',1)[1],value,expected_revision=self.headers.get('If-Match','').strip('"') or None,include_revision=True)
                    return self.send(json.dumps(value,ensure_ascii=False,allow_nan=False).encode(),headers={'ETag':'"'+revision+'"'})
                from nexus_snapshot import refresh
                refresh(STATE);return self.snapshot()
        except DocumentConflict as exc:self.send(json.dumps({'error':str(exc)}).encode(),status=409)
        except ValueError as exc:self.send(json.dumps({'error':str(exc)}).encode(),status=400)
        except Exception as exc:
            print('Crafting request failed: '+type(exc).__name__,flush=True)
            self.send(b'{"error":"Nexus could not complete that request. Existing saved choices are preserved."}',status=503)


if __name__=='__main__':
    signal.signal(signal.SIGTERM,lambda *_:sys.exit(0))
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('CRAFTING_PORT','8765'))),Handler).serve_forever()

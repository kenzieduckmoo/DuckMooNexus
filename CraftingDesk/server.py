import json
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from importer import collect
from setups import validate_setups, validate_plan
from nexus_connection import fetch as nexus_fetch

BASE=Path(__file__).resolve().parent
CACHE=BASE/'local-data.json'
SETUPS=BASE/'saved-setups.json'
PLAN=BASE/'daily-plan.json'
LOCK=threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def send(self, body, kind='application/json', status=200):
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path.startswith('/api/nexus/'):
            status,body=nexus_fetch(self.path,self.headers.get('Authorization'))
            return self.send(body,status=status)
        if self.path=='/': self.send((BASE/'index.html').read_bytes(),'text/html; charset=utf-8')
        elif self.path in ('/leveling-plan.js','/leveling-ui.js','/acquisition.js','/profession-guides.js','/guide-planner.js','/tailoring-route.js','/profession-route.js','/concentration-ready.js','/guide-ui.js','/recipe-investments.js'): self.send((BASE/self.path[1:]).read_bytes(),'text/javascript; charset=utf-8')
        elif self.path=='/DuckMooCapture-0.7.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.7.0.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.6.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.6.0.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.5.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.5.0.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.4.1.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.4.1.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.4.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.4.0.zip').read_bytes(),'application/zip')
        elif self.path=='/material-ui.js': self.send((BASE/'material-ui.js').read_bytes(),'text/javascript; charset=utf-8')
        elif self.path=='/profit-ui.js': self.send((BASE/'profit-ui.js').read_bytes(),'text/javascript; charset=utf-8')
        elif self.path=='/daily-plan.js': self.send((BASE/'daily-plan.js').read_bytes(),'text/javascript; charset=utf-8')
        elif self.path=='/daily-ui.js': self.send((BASE/'daily-ui.js').read_bytes(),'text/javascript; charset=utf-8')
        elif self.path=='/DuckMooCapture-0.1.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.1.0.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.2.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.2.0.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.3.1.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.3.1.zip').read_bytes(),'application/zip')
        elif self.path=='/DuckMooCapture-0.3.0.zip': self.send((BASE/'downloads'/'DuckMooCapture-0.3.0.zip').read_bytes(),'application/zip')
        elif self.path=='/api/setups': self.send(SETUPS.read_bytes() if SETUPS.exists() else b'{"version":1,"setups":[]}')
        elif self.path=='/api/plan': self.send(PLAN.read_bytes() if PLAN.exists() else b'{"version":1,"setups":[]}')
        elif self.path=='/api/data': self.send(CACHE.read_bytes() if CACHE.exists() else b'{}')
        else: self.send(b'{}',status=404)
    def do_POST(self):
        if self.path not in ('/api/import','/api/setups','/api/plan'): return self.send(b'{}',status=404)
        if self.headers.get('Origin') not in (None,f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
            return self.send(b'{}',status=403)
        try:
            with LOCK:
                if self.path in ('/api/setups','/api/plan'):
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0 < length <= 1000000: raise ValueError('Invalid setup request size')
                    validator=validate_plan if self.path=='/api/plan' else validate_setups
                    value=validator(json.loads(self.rfile.read(length)))
                    payload=json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
                    destination=PLAN if self.path=='/api/plan' else SETUPS
                    temp=destination.with_suffix('.tmp'); temp.write_bytes(payload); temp.replace(destination)
                    return self.send(payload)
                data=collect()
                if not data['sources']: raise ValueError('No sources could be read. Existing import was preserved.')
                payload=json.dumps(data,ensure_ascii=False).encode()
                temp=CACHE.with_suffix('.tmp'); temp.write_bytes(payload); temp.replace(CACHE)
            self.send(payload)
        except Exception as e: self.send(json.dumps({'error':str(e)}).encode(),status=500)

if __name__=='__main__':
    print('Crafting Desk: http://127.0.0.1:8765',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()

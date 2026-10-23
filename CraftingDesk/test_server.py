import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import server

class LocalOriginTests(unittest.TestCase):
    def test_preview_port_accepts_only_its_loopback_origins(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory, patch.object(server, 'PLAN', Path(directory)/'plan.json'):
            body=json.dumps({'version':1,'setups':[],'completed':[]}).encode()
            for origin,status in [('http://127.0.0.1:8768',200),('http://localhost:8768',200),('https://example.com',403),('http://127.0.0.1:1',403)]:
                handler=object.__new__(server.Handler)
                handler.server=SimpleNamespace(server_port=8768)
                handler.path='/api/plan'
                handler.headers={'Origin':origin,'Content-Length':str(len(body))}
                handler.rfile=io.BytesIO(body)
                responses=[]
                handler.send=lambda body,kind='application/json',status=200:responses.append((status,body))
                handler.do_POST()
                self.assertEqual(responses[0][0],status)
            self.assertEqual(json.loads(server.PLAN.read_text()),{'version':1,'setups':[],'completed':[]})

if __name__=='__main__':unittest.main()

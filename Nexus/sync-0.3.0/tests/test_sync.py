import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
if os.name != 'posix':
    sys.modules['fcntl'] = types.SimpleNamespace()  # Unit tests do not call Linux flock.
import sync_core as core
import worker

class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.raw = b'JOURNALATOR = { }\n'
        self.digest = hashlib.sha256(self.raw).hexdigest()
    def tearDown(self):
        self.temp.cleanup()
    def test_command_allowlist(self):
        self.assertEqual(core.parse_command('status ' + self.digest), ('status', self.digest, 0))
        self.assertEqual(core.parse_command(f'put {self.digest} 17')[2], 17)
        for command in ['sh', 'put ../a 2', f'put {self.digest} 0', f'put {self.digest} {core.LIMIT+1}',
                        f'status {self.digest};id', f'status {self.digest} extra']:
            with self.assertRaises(ValueError): core.parse_command(command)
    def test_atomic_receive(self):
        core.receive(io.BytesIO(self.raw), self.base, self.digest, len(self.raw))
        self.assertEqual((self.base / (self.digest + '.lua')).read_bytes(), self.raw)
        self.assertEqual(len(list(self.base.iterdir())), 1)
    def test_truncated_upload(self):
        with self.assertRaises(ValueError): core.receive(io.BytesIO(self.raw[:-1]), self.base, self.digest, len(self.raw))
        self.assertEqual(list(self.base.iterdir()), [])
    def test_extra_bytes(self):
        with self.assertRaises(ValueError): core.receive(io.BytesIO(self.raw+b'x'), self.base, self.digest, len(self.raw))
        self.assertEqual(list(self.base.iterdir()), [])
    def test_wrong_hash(self):
        with self.assertRaises(ValueError): core.receive(io.BytesIO(self.raw), self.base, 'a'*64, len(self.raw))
        self.assertEqual(list(self.base.iterdir()), [])
    def test_repeat_upload(self):
        for _ in range(2): core.receive(io.BytesIO(self.raw), self.base, self.digest, len(self.raw))
        self.assertEqual(len(list(self.base.iterdir())), 1)
    def test_spool_tampering(self):
        path = self.base / 'input'
        path.write_bytes(self.raw)
        self.assertEqual(core.verified_read(path, self.digest), self.raw)
        path.write_bytes(b'bad')
        with self.assertRaises(ValueError): core.verified_read(path, self.digest)
    def test_receipt_validation(self):
        for text in ['{}', 'not-json', '{"status":"pending"}', '{"status":"imported","inserted":true}']:
            with self.assertRaises((ValueError, TypeError)): core.import_result(text)
        self.assertEqual(core.import_result('{"status":"already_imported","inserted":0,"records":19581,"import_id":1}')['inserted'], 0)
    def test_atomic_receipt(self):
        path = self.base / 'receipt.json'
        core.atomic_json(path, {'status':'pending'})
        core.atomic_json(path, {'status':'imported'})
        self.assertEqual(json.loads(path.read_text())['status'], 'imported')
        self.assertEqual(len(list(self.base.iterdir())), 1)
    def worker_case(self, fail=False, networks=None):
        for folder in ('inbox','receipts','staging'): (self.base / folder).mkdir()
        path = self.base / 'inbox' / (self.digest + '.lua')
        path.write_bytes(self.raw)
        config = dict(postgres_container='postgres', network='', uid=1000, gid=1000, env_file='/private/.env')
        calls = []
        def docker(args, timeout=30):
            calls.append(args)
            if args[0] == 'inspect': return json.dumps([{'NetworkSettings':{'Networks':networks or {'nexus_default':{}}}}])
            if fail: raise RuntimeError('secret database URL must not be logged')
            return '{"status":"imported","inserted":12,"records":12,"import_id":2}'
        with patch.object(worker, 'BASE', self.base), patch.object(worker, 'run_docker', side_effect=docker), \
             patch.object(worker.subprocess, 'run'), patch.object(worker.os, 'chown', create=True):
            worker.process(path, config)
            receipt = json.loads((self.base / 'receipts' / (self.digest+'.json')).read_text())
            before = len(calls)
            worker.process(path, config)  # Success skips; failure observes retry backoff.
            self.assertEqual(len(calls), before)
        return path, receipt, calls
    def test_worker_success(self):
        path, receipt, calls = self.worker_case()
        self.assertFalse(path.exists())
        self.assertEqual(receipt['status'], 'imported')
        self.assertIn('retail-main-account', calls[-1])
        self.assertIn('duckmoo-nexus:0.1.0', calls[-1])
    def test_worker_failure_preserves_input(self):
        path, receipt, calls = self.worker_case(fail=True)
        self.assertTrue(path.exists())
        self.assertEqual(receipt['status'], 'failed')
        self.assertNotIn('secret', json.dumps(receipt))
    def test_ambiguous_network_fails_closed(self):
        path, receipt, calls = self.worker_case(networks={'a':{},'b':{}})
        self.assertTrue(path.exists())
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual(len(calls), 1)

if __name__ == '__main__': unittest.main(verbosity=2)

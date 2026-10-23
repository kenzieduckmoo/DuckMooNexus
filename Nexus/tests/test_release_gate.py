import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gate', ROOT/'release_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def test_code_changes_invalidate_verification_but_python_cache_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ('duckmoo-nexus', 'sync-0.3.0', 'sync-reference'):
                (root/folder).mkdir()
            for name in ('upgrade-server.sh','rollback-server.sh','verify-stack.sh','preflight.sh','release_gate.py'):
                (root/name).write_text('original')
            source=root/'duckmoo-nexus/importer.py'
            source.write_text('original')
            before=gate.fingerprint(root)
            cache=root/'duckmoo-nexus/__pycache__'
            cache.mkdir();(cache/'importer.pyc').write_bytes(b'cache')
            self.assertEqual(before,gate.fingerprint(root))
            source.write_text('changed')
            self.assertNotEqual(before,gate.fingerprint(root))


if __name__ == '__main__':
    unittest.main()

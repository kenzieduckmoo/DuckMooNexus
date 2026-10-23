import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from bundle import unpack_bundle


class CleanInstallTests(unittest.TestCase):
    def test_collector_includes_journalator_backups_and_retries(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'SavedVariables'
            source.mkdir()
            state = root / 'state'
            for name in ('Journalator.lua', 'Journalator.lua.bak', 'WarbandAccountant.lua'):
                path = source / name
                path.write_text('DB = {}')
                os.utime(path, (time.time() - 60, time.time() - 60))
            command = [sys.executable, str(APP / 'collect_sources.py'), str(source), str(state)]
            first = subprocess.run(command, capture_output=True, text=True, check=True)
            packets = json.loads(first.stdout)
            self.assertEqual(len(packets), 3)
            identities = []
            for packet in packets:
                with tempfile.TemporaryDirectory() as staging:
                    _, manifest = unpack_bundle(packet['path'], staging)
                    identities.append(manifest['source'])
            self.assertEqual(identities.count('Journalator.lua'), 2)
            again = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertEqual({p['hash'] for p in packets}, {p['hash'] for p in json.loads(again.stdout)})
            self.assertEqual((source / 'Journalator.lua').read_text(), 'DB = {}')

    def test_invalid_source_path_is_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(APP / 'collect_sources.py'),
                str(Path(folder)/'missing'), str(Path(folder)/'state')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('does not exist', result.stderr)

    def test_capture_error_is_not_silenced(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'SavedVariables'
            source.mkdir()
            path = source / 'Journalator.lua'
            path.write_bytes(b'')
            os.utime(path, (time.time()-60, time.time()-60))
            result = subprocess.run([sys.executable, str(APP / 'collect_sources.py'),
                str(source), str(root/'state')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('outside', result.stderr)

    def test_dashboard_datasources_are_bound(self):
        for path in (APP / 'grafana').glob('*.json'):
            text = path.read_text()
            self.assertNotIn('${DS_POSTGRES}', text)
            self.assertNotIn('__inputs', json.loads(text))
            self.assertIn('duckmoo-postgres', text)


if __name__ == '__main__':
    unittest.main()

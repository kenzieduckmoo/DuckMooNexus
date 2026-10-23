import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'duckmoo-nexus'))
if os.name!='posix':sys.modules['fcntl']=types.SimpleNamespace()
import worker
from snapshots import capture
from bundle import create_bundle


class BundleWorkerTests(unittest.TestCase):
    def test_worker_queues_use_separate_locks_and_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'inbox').mkdir()
            (root/'inbox'/('a'*64+'.lua')).write_bytes(b'lua')
            (root/'inbox'/('b'*64+'.bundle')).write_bytes(b'bundle')
            # Supply config only for its absolute path; real lock files stay local.
            original_read=Path.read_text
            def read(path,*args,**kwargs):
                if str(path).replace('\\','/')=='/etc/duckmoo-sync/config.json':return '{}'
                return original_read(path,*args,**kwargs)
            fake_lock=types.SimpleNamespace(flock=lambda *args:None,LOCK_EX=1,LOCK_NB=2)
            with patch.object(worker,'BASE',root),patch.object(worker,'fcntl',fake_lock),patch.object(Path,'read_text',read),patch.object(worker,'process') as journal,patch.object(worker,'process_bundle') as sources:
                worker.main()
                journal.assert_called_once();sources.assert_not_called()
                worker.main(sources=True)
                sources.assert_called_once();self.assertEqual(journal.call_count,1)
            self.assertTrue((root/'worker.lock').exists())
            self.assertTrue((root/'source-worker.lock').exists())
    def run_case(self,status='imported',fail=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for folder in ('inbox','receipts','staging','raw'):(root/folder).mkdir()
            source=root/'raw/Syndicator.lua';source.write_bytes(b'A = {\n}\n')
            manifest=capture(source,root/'archive','retail-main-account')
            mf=next((root/'archive').glob('*.json'));packet=root/'inbox/packet.tmp'
            digest=create_bundle(mf,packet);path=packet.with_name(digest+'.bundle');packet.replace(path)
            calls=[]
            def docker(args,timeout=30):
                calls.append(args)
                if args[0]=='inspect':return json.dumps([{'NetworkSettings':{'Networks':{'nexus_internal':{}}}}])
                if fail:raise RuntimeError('do not log secret')
                return json.dumps(dict(status=status,snapshot_id=1,source='Syndicator.lua',inserted=1))
            config=dict(postgres_container='postgres',network='nexus_internal',uid=1000,gid=1000,env_file='/private/.env')
            with patch.object(worker,'BASE',root),patch.object(worker,'run_docker',side_effect=docker),patch.object(worker.os,'chown',create=True),patch.object(worker.subprocess,'run'):
                worker.process_bundle(path,config)
                receipt=json.loads((root/'receipts'/(digest+'.json')).read_text())
                before=len(calls);worker.process_bundle(path,config);self.assertEqual(len(calls),before)
            self.assertEqual(path.exists(),fail)
            self.assertNotIn('secret',json.dumps(receipt))
            return receipt
    def test_source_commit_receipt(self):self.assertEqual(self.run_case()['status'],'imported')
    def test_archive_only_receipt(self):self.assertEqual(self.run_case(status='archived')['status'],'archived')
    def test_failed_import_preserves_packet(self):self.assertEqual(self.run_case(fail=True)['status'],'failed')


if __name__=='__main__':unittest.main()

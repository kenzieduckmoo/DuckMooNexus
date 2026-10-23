import hashlib,importlib.util,json,sys,tempfile,types,unittest
from pathlib import Path
sys.modules['fcntl']=types.SimpleNamespace()
spec=importlib.util.spec_from_file_location('receiver','Nexus/clean-install/receiver.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class ReceiptChecks(unittest.TestCase):
 def test_cached_packet_and_recovery(self):
  with tempfile.TemporaryDirectory(dir='Nexus/test-tmp') as t:
   r.BASE=r.STACK=Path(t);(r.STACK/'.env').write_text('generation-one')
   d='a'*64;packet=r.BASE/(d+'.bundle');packet.write_bytes(b'retained')
   receipt=r.BASE/(d+'.receipt.json');receipt.write_text(json.dumps(dict(generation=hashlib.sha256(b'generation-one').hexdigest(),sha256=d,status='imported')))
   self.assertEqual(r.known_receipts([d,d,'b'*64]),{'committed':[d]})
   (r.STACK/'.env').write_text('generation-two');self.assertEqual(r.known_receipts([d]),{'committed':[]})
   (r.STACK/'.env').write_text('generation-one');packet.unlink();self.assertEqual(r.known_receipts([d]),{'committed':[]})
 def test_invalid_paths_and_receipts(self):
  with tempfile.TemporaryDirectory(dir='Nexus/test-tmp') as t:
   r.BASE=r.STACK=Path(t);(r.STACK/'.env').write_text('generation')
   with self.assertRaises(ValueError):r.known_receipts(['../secret'])
   d='c'*64;(r.BASE/(d+'.bundle')).write_bytes(b'retained');(r.BASE/(d+'.receipt.json')).write_text('{broken')
   self.assertEqual(r.known_receipts([d]),{'committed':[]})
unittest.main()

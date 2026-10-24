"""Client-channel isolation and first-save enrollment; no game or server needed."""
import json,os,sys,tempfile,time,subprocess,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bundle import unpack_bundle
APP=Path(__file__).resolve().parents[1]
class Channels(unittest.TestCase):
 def test_forever_enrollment_namespace_and_state_isolation(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);sv=root/'SavedVariables';sv.mkdir();state=root/'state'
   source=sv/'DuckMooOmniCapture.lua';source.write_text('DuckMooOmniCaptureDB = {\n}\n');now=time.time();os.utime(source,(now-100,now-100))
   command=[sys.executable,str(APP/'collect_sources.py'),str(sv),str(state),'--namespace','forever-main-account','--minimum-saved-at',str(now-50)]
   self.assertEqual(json.loads(subprocess.check_output(command)),[])
   os.utime(source,(now-20,now-20));packets=json.loads(subprocess.check_output(command));self.assertEqual(len(packets),1)
   target=root/'unpacked';target.mkdir()
   with self.assertRaises(ValueError):unpack_bundle(packets[0]['path'],target)
   _,manifest=unpack_bundle(packets[0]['path'],target,namespace=None);self.assertEqual(manifest['namespace'],'forever-main-account')
   different=command.copy();different[different.index('forever-main-account')]='retail-main-account'
   result=subprocess.run(different,capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertIn('another client namespace',result.stderr)
   self.assertIn('DuckMooOmniCaptureDB',source.read_text())
if __name__=='__main__':unittest.main()

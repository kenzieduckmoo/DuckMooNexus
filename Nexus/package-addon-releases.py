"""Package owned addons from TOC runtime lists; never read installed player data."""
from pathlib import Path
import re,zipfile,json
root=Path(__file__).resolve().parents[1]
out=root/'releases'/'curseforge-ready-2026-10-24';out.mkdir(parents=True,exist_ok=True)
manifest=[]
for name in ('DuckMooCapture','DuckMooFolio','DuckMooPlanner','DuckMooWarband','DuckMooOmniCapture','FiammaCollector'):
 addon=root/'AddOns'/name;toc=addon/(name+'.toc');text=toc.read_text(encoding='utf-8-sig')
 assert re.findall(r'^## Category:.*$',text,re.M)==['## Category: DuckMoo Media']
 version=re.search(r'^## Version:\s*(\S+)',text,re.M)[1]
 files={toc,addon/'USER-GUIDE.txt',*addon.glob('*_Camelot.toc')}
 runtime=[x.strip().replace('\\','/') for x in text.splitlines() if x.strip() and not x.lstrip().startswith('#')]
 for entry in runtime:
  p=(addon/entry).resolve();assert p.is_relative_to(addon.resolve()) and p.is_file(),entry;files.add(p)
 for folder in ('Media','media'):
  if (addon/folder).is_dir():files.update(p for p in (addon/folder).rglob('*') if p.is_file())
 for filename in ('LICENSE','LICENSE.txt','NOTICE.txt','README.md','CHANGELOG.md'):
  if (addon/filename).is_file():files.add(addon/filename)
 target=out/f'{name}-{version}.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(files):z.write(p,Path(name)/p.relative_to(addon))
 with zipfile.ZipFile(target) as z:
  names=z.namelist();assert z.testzip() is None
  assert all(p.startswith(name+'/') for p in names)
  assert not any(part in {'.git','.github','tests','tools','__pycache__','SavedVariables'} for p in names for part in p.split('/'))
  if name=='DuckMooOmniCapture':
   receipt=z.read(name+'/Acknowledgements.lua').decode('utf-8')
   assert re.search(r'characters\s*=\s*\{\s*\}',receipt) and 'Player-' not in receipt
 manifest.append({'addon':name,'version':version,'zip':target.name,'files':len(names),'guide_words':len((addon/'USER-GUIDE.txt').read_text(encoding='utf-8').split())})
(out/'PACKAGES.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))

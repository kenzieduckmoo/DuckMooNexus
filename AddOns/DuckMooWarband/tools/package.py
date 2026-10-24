"""Package runtime files and user documentation without development/player data."""
from pathlib import Path
import re
import zipfile
root=Path(__file__).resolve().parents[1]
version=re.search(r'^## Version:\s*(\S+)',(root/'DuckMooWarband.toc').read_text(),re.M).group(1)
destination=root/'dist';destination.mkdir(exist_ok=True)
output=destination/f'DuckMooWarband-{version}.zip'
toc=root/'DuckMooWarband.toc'
runtime=[s.strip().replace('\\','/') for s in toc.read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')]
files={toc,root/'USER-GUIDE.txt',root/'README.md'}
for name in runtime:
    path=(root/name).resolve()
    assert path.is_relative_to(root) and path.is_file(),name
    files.add(path)
for filename in ('LICENSE','NOTICE.txt'):
    if (root/filename).is_file():files.add(root/filename)
if (root/'Media').is_dir():files.update(p for p in (root/'Media').rglob('*') if p.is_file())
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(files):archive.write(path,Path('DuckMooWarband')/path.relative_to(root))
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert 'DuckMooWarband/DuckMooWarband.toc' in archive.namelist()
print(output)

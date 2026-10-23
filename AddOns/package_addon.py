"""Package a development addon without rewriting its documentation."""
from pathlib import Path
import re
import sys
from zipfile import ZipFile, ZIP_DEFLATED

root=Path(__file__).resolve().parent
folder=sys.argv[1]
if not re.fullmatch(r'DuckMoo[A-Za-z]+',folder):
    raise SystemExit('Use a DuckMoo addon folder name.')
source=root/folder
manifest=(source/(folder+'.toc')).read_text(encoding='utf-8')
version=re.search(r'^## Version: ([\d.]+)$',manifest,re.M).group(1)
destination=root.parent/'releases'/(folder+'-'+version+'-preview.zip')
destination.parent.mkdir(exist_ok=True)
with ZipFile(destination,'w',ZIP_DEFLATED) as archive:
    for item in source.rglob('*'):
        if item.is_file() and not any(part in {'.git','__pycache__'} for part in item.parts):
            archive.write(item,item.relative_to(root))
with ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert all(name.startswith(folder+'/') for name in archive.namelist())
    for filename in manifest.splitlines():
        if filename.endswith('.lua'):
            assert folder+'/'+filename in archive.namelist()
print(destination)

"""Package this addon and its source/testing docs in an installable folder."""
from pathlib import Path
import re
import zipfile
root=Path(__file__).resolve().parents[1]
version=re.search(r'^## Version:\s*(\S+)',(root/'DuckMooFolio.toc').read_text(),re.M).group(1)
output=root.parent/f'DuckMooFolio-{version}.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            archive.write(path,Path('DuckMooFolio')/path.relative_to(root))
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert 'DuckMooFolio/DuckMooFolio.toc' in archive.namelist()
print(output)

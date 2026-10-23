import json
import sys
from pathlib import Path
p=Path(sys.argv[1]);state=json.loads(p.read_text())
for row in state.values():
    if row.get('packet')==sys.argv[2]:row['acknowledged']=True
temp=p.with_suffix('.tmp');temp.write_text(json.dumps(state));temp.replace(p)

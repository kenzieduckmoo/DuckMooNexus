"""Windows-side collector using the same v2 receiver, with v3 packet extension."""
import argparse
import json
import time
from pathlib import Path
from snapshots import capture,SOURCES
from bundle import create_bundle


def main():
    p=argparse.ArgumentParser();p.add_argument('savedvariables',type=Path);p.add_argument('state',type=Path)
    p.add_argument('--tsm-appdata',type=Path);p.add_argument('--namespace',choices=['retail-main-account','forever-main-account'],default='retail-main-account');p.add_argument('--minimum-saved-at',type=float,default=0);a=p.parse_args()
    a.state.mkdir(parents=True,exist_ok=True)
    queue=a.state/'packets';queue.mkdir(exist_ok=True)
    binding=a.state/'namespace.txt'
    if binding.exists() and binding.read_text().strip()!=a.namespace:raise ValueError('State directory belongs to another client namespace')
    if not binding.exists():binding.write_text(a.namespace)
    if not a.savedvariables.is_dir():
        raise ValueError('SavedVariables directory does not exist')
    sources=[(a.savedvariables/(name+suffix),name+'.lua') for name in SOURCES if name != 'TSM_AppData'
             for suffix in ('.lua.bak', '.lua')]
    if a.tsm_appdata:sources.append((a.tsm_appdata,'TSM_AppData.lua'))
    state_path=a.state/'source-checkpoints.json'
    previous=json.loads(state_path.read_text()) if state_path.exists() else {}
    for path,name in sources:
        if not path.exists():continue
        info=path.stat()
        if info.st_mtime<a.minimum_saved_at or time.time()-info.st_mtime<15:continue
        fingerprint=[info.st_size,info.st_mtime_ns]
        key=str(path.resolve())
        old=previous.get(key,{})
        # Pending durable packets are retried even when the source has not changed.
        if old.get('fingerprint')==fingerprint and (queue/(old.get('packet','')+'.bundle')).exists():continue
        if old.get('fingerprint')==fingerprint and old.get('manifest'):
            # Rebuild a small transport packet from the retained gzip, then query
            # the server receipt each run. A recovered DB must not be hidden by
            # a permanent client-side same-hash skip.
            staging=queue/'packet.tmp'
            digest=create_bundle(Path(old['manifest']),staging)
            staging.replace(queue/(digest+'.bundle'))
            continue
        manifest=capture(path,a.state/'archives',a.namespace,source_name=name)
        manifests=[x for x in (a.state/'archives').glob(manifest['sha256']+'-*.json')
                   if json.loads(x.read_text())['source']==name]
        # Select the manifest for this source save, not an earlier same-content save.
        mf=next(x for x in manifests if json.loads(x.read_text())['saved_at']==manifest['saved_at'])
        staging=queue/'packet.tmp'
        digest=create_bundle(mf,staging)
        staging.replace(queue/(digest+'.bundle'))
        previous[key]=dict(fingerprint=fingerprint,packet=digest,manifest=str(mf),acknowledged=False)
    temporary=state_path.with_suffix('.tmp');temporary.write_text(json.dumps(previous));temporary.replace(state_path)
    print(json.dumps([dict(hash=p.stem,bytes=p.stat().st_size,path=str(p)) for p in queue.glob('*.bundle')]))


if __name__=='__main__':main()

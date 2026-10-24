"""A v3 upload is one ZIP_STORED packet: validated manifest + raw gzip blob."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from snapshots import SOURCES, MAX_BYTES

MAX_PACKET = 512*1024**2


def create_bundle(manifest_path, destination):
    manifest_path=Path(manifest_path)
    manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    archive=manifest_path.parent/(manifest['sha256']+'.lua.gz')
    if archive.stat().st_size>MAX_PACKET-32768:
        raise ValueError('Compressed source exceeds transport bound')
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_STORED) as packet:
        # Fixed ZIP timestamps make retries content-addressed across collection runs.
        packet.writestr(zipfile.ZipInfo('manifest.json'),json.dumps(manifest,sort_keys=True))
        with archive.open('rb') as source, packet.open(zipfile.ZipInfo('source.lua.gz'),'w') as target:
            shutil.copyfileobj(source,target,1024**2)
    h=hashlib.sha256()
    with open(destination,'rb') as stream:
        while block:=stream.read(1024**2):h.update(block)
    return h.hexdigest()


def unpack_bundle(path, destination, namespace='retail-main-account'):
    destination=Path(destination)
    if Path(path).stat().st_size>MAX_PACKET:
        raise ValueError('Oversized packet')
    with zipfile.ZipFile(path) as packet:
        infos=packet.infolist()
        if len(infos)!=2 or {x.filename for x in infos}!={'manifest.json','source.lua.gz'}:
            raise ValueError('Unexpected bundle members')
        if any(x.compress_type!=zipfile.ZIP_STORED for x in infos):
            raise ValueError('Bundle must use stored ZIP members')
        if packet.getinfo('manifest.json').file_size>16384 or packet.getinfo('source.lua.gz').file_size>MAX_PACKET:
            raise ValueError('Oversized member')
        manifest=json.loads(packet.read('manifest.json'))
        if manifest['namespace'] not in ({'retail-main-account','forever-main-account'} if namespace is None else {namespace}) or manifest['source'].removesuffix('.lua') not in SOURCES or not manifest['source'].endswith('.lua'):
            raise ValueError('Invalid source or namespace')
        digest=manifest['sha256']
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid raw hash')
        if type(manifest['raw_bytes']) is not int or not 0<manifest['raw_bytes']<=MAX_BYTES:
            raise ValueError('Invalid raw size')
        target=destination/(digest+'.lua.gz')
        with packet.open('source.lua.gz') as inp,target.open('wb') as out:
            while block:=inp.read(1024**2):out.write(block)
        # Fixed safe target name; no path from uploaded JSON is used for extraction.
        mf=destination/'manifest.json';mf.write_text(json.dumps(manifest))
        return mf,manifest

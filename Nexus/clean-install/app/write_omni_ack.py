"""Publish bounded Lua receipts from a server-confirmed packet, never live SV edits."""
import argparse
import gzip
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from savedvariables import read_lua


def acknowledgement_rows(db):
    if db.get('schema') != 1:raise ValueError('Unsupported Omni schema')
    result={}
    for guid,c in db.get('characters',{}).items():
        journal=c.get('journalID')
        if not journal:continue  # Legacy histories get identities on their next addon load.
        if not re.fullmatch(r'Player-\d+-[0-9A-Fa-f]+',guid) or not re.fullmatch(r'[A-Za-z0-9:_-]{1,160}',journal):raise ValueError('Invalid Omni journal identity')
        raw=c.get('events',{})
        events=list(raw.values()) if isinstance(raw,dict) else raw
        if not isinstance(events,list):raise ValueError('Invalid Omni event journal')
        previous=None
        for event in events:
            eid,at=event.get('id'),event.get('at')
            if type(eid) is not int or not 0<eid<2**53 or type(at) is not int or not 0<at<4102444800:raise ValueError('Invalid Omni event marker')
            if previous is not None and eid!=previous+1:raise ValueError('Non-contiguous Omni journal; retain locally')
            if event.get('journalID',journal)!=journal:raise ValueError('Mixed Omni journal identities')
            previous=eid
        if events:
            last=events[-1]
            if type(c.get('sequence')) is not int or c['sequence']!=last['id']:raise ValueError('Omni sequence does not match retained events')
            result[guid]={'journalID':journal,'through':last['id'],'at':last['at']}
    return result


def publish(savedvariables,state):
    savedvariables,state=Path(savedvariables).resolve(),Path(state).resolve()
    source=savedvariables/'DuckMooOmniCapture.lua'
    checkpoints=json.loads((state/'source-checkpoints.json').read_text(encoding='utf-8-sig'))
    current=checkpoints.get(str(source))
    committed=json.loads((state/'omni-committed-packets.json').read_text(encoding='utf-8-sig'))
    if not current or current.get('packet') not in committed:return {'status':'awaiting_confirmed_archive'}
    digest=current['packet']
    if not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('Invalid committed packet identifier')
    with zipfile.ZipFile(state/'packets'/(digest+'.bundle')) as packet:
        manifest=json.loads(packet.read('manifest.json'))
        if manifest.get('source')!='DuckMooOmniCapture.lua' or manifest.get('original_name')!='DuckMooOmniCapture.lua' or manifest.get('namespace')!='retail-main-account':raise ValueError('Receipt does not cover the primary Omni source')
        if not 0<manifest.get('raw_bytes',0)<=256*1024**2:raise ValueError('Omni acknowledgement source exceeds bound')
        with tempfile.TemporaryDirectory(dir=state) as folder:
            path=Path(folder)/'confirmed.lua'
            with packet.open('source.lua.gz') as compressed,gzip.GzipFile(fileobj=compressed) as inp,path.open('wb') as out:
                total=0
                while block:=inp.read(1024**2):
                    total+=len(block)
                    if total>manifest['raw_bytes']:raise ValueError('Omni source length exceeds manifest')
                    out.write(block)
            if total!=manifest['raw_bytes']:raise ValueError('Truncated Omni source')
            rows=acknowledgement_rows(read_lua(path)['DuckMooOmniCaptureDB'])
    # Infer only the normal WoW client layout; never accept an uploaded destination.
    if savedvariables.name!='SavedVariables' or savedvariables.parent.parent.name!='Account' or savedvariables.parent.parent.parent.name!='WTF':raise ValueError('Unrecognized WoW SavedVariables layout')
    addon=savedvariables.parents[3]/'Interface'/'AddOns'/'DuckMooOmniCapture'
    toc=addon/'DuckMooOmniCapture.toc'
    if not toc.is_file() or 'Acknowledgements.lua' not in toc.read_text(encoding='utf-8-sig'):return {'status':'awaiting_addon_update'}
    lines=['local _,O=...','-- Generated only from an archive confirmed by Nexus. Do not edit.','O.acknowledgements={schema=1,characters={']
    for guid,row in sorted(rows.items()):
        lines.append(f'[{json.dumps(guid)}]={{journalID={json.dumps(row["journalID"])},through={row["through"]},at={row["at"]}}},')
    lines.append('}}\n')
    content='\n'.join(lines)
    dest=addon/'Acknowledgements.lua'
    if dest.exists() and dest.read_text(encoding='utf-8')==content:return {'status':'unchanged','journals':len(rows)}
    fd,name=tempfile.mkstemp(prefix='.omni-ack-',suffix='.tmp',dir=addon)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as out:out.write(content);out.flush();os.fsync(out.fileno())
        os.replace(name,dest)
    finally:Path(name).unlink(missing_ok=True)
    return {'status':'published','journals':len(rows)}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('savedvariables');parser.add_argument('state');args=parser.parse_args()
    print(json.dumps(publish(args.savedvariables,args.state)))

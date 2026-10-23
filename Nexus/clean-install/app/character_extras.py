"""Preserve character-associated sections from existing addon archives.

GUID keys are exact. Name/realm keys match an unambiguous captured identity.
Account-wide tables are not assigned to an individual character.
"""
import hashlib,re
from datetime import datetime,timezone
from financials import canonical
EXTRA_SOURCES=('WarbandNexus.lua','WoWthing_Collector.lua','DuckMooWarband.lua')
EXTRA_VERSION='0.5.0-character-extras1'

def json_data(value):
    if isinstance(value,dict):
        result={}
        for key,entry in value.items():
            label=str(key)
            if not isinstance(key,str) and label in value:label='[lua-number:'+label+']'
            result[label]=json_data(entry)
        return result
    if isinstance(value,(tuple,list)):return [json_data(v) for v in value]
    return value
def extra_rows(data,known):
    names={}
    for guid,row in known.items():
        if row.get('name') and row.get('realm'):
            key=(row['name']+'-'+row['realm']).replace(' ','').casefold();names.setdefault(key,set()).add(guid)
    result={}
    def walk(value,path=(),depth=0):
        if not isinstance(value,dict) or depth>12:return
        for key,row in value.items():
            label=str(key);guid=None
            if re.fullmatch(r'Player-\d+-[0-9A-Fa-f]+',label):guid=label
            else:
                matches=names.get(label.replace(' ','').casefold(),set())
                if len(matches)==1:guid=next(iter(matches))
            if guid:
                entry=result.setdefault(guid,{'identity':dict(known.get(guid,{})),'records':{}})
                entry['records'][' / '.join((*path,label))]=row
                if isinstance(row,dict) and row.get('name') and row.get('realm'):
                    entry['identity'].update({k:row[k] for k in ('name','realm','class','classFile','level','race','faction','lastSeen') if k in row})
                continue
            walk(row,(*path,label),depth+1)
    walk(data)
    return result

def normalize_extras(conn,data,source,namespace,snapshot_id):
    known={r[0]:{'name':r[1],'realm':r[2]} for r in conn.execute('SELECT character_guid,name,realm FROM nexus.character_roster WHERE namespace=%s',(namespace,))}
    # Some archives contain identities absent from Folio; retain exact GUIDs too.
    for root in data.values():
        if isinstance(root,dict):
            for pool in (root.get('characters',{}),root.get('global',{}).get('characters',{}),root.get('chars',{})):
                for guid,c in pool.items():
                    if str(guid).startswith('Player-') and isinstance(c,dict) and c.get('name') and c.get('realm'):known.setdefault(guid,{'name':c['name'],'realm':c['realm']})
    rows=extra_rows(data,known)
    for guid,payload in rows.items():
        payload=json_data(payload)
        stamp=payload['identity'].get('lastSeen');stamp=stamp if type(stamp) is int and stamp>0 else None
        oid=hashlib.sha256(canonical([namespace,source,guid,payload]).encode()).hexdigest()
        conn.execute('INSERT INTO nexus.character_extras VALUES(%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT DO NOTHING',(oid,namespace,source,guid,datetime.fromtimestamp(stamp,timezone.utc) if stamp else None,canonical(payload)))
        conn.execute('INSERT INTO nexus.snapshot_character_extras VALUES(%s,%s) ON CONFLICT DO NOTHING',(snapshot_id,oid))
    return len(rows)

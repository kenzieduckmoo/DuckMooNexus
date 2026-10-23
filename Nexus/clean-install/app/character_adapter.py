"""Folio/Planner observations with explicit source timestamps and full payloads."""
from collections.abc import Mapping

CHARACTER_SOURCES=('DuckMooFolio.lua','DuckMooPlanner.lua')
CHARACTER_VERSION='0.5.0-characters1'


def stamp(value):
    return value if type(value) is int and value>0 else None


def character_rows(source,data):
    if source not in CHARACTER_SOURCES:raise ValueError('Unsupported character source')
    key='DuckMooFolioDB' if source=='DuckMooFolio.lua' else 'DuckMooPlannerDB'
    db=data.get(key)
    if not isinstance(db,Mapping):raise ValueError('Missing '+key)
    expected=1 if source=='DuckMooFolio.lua' else 3
    if db.get('version' if source=='DuckMooFolio.lua' else 'schema')!=expected:
        raise ValueError('Unsupported character source schema')
    chars=db.get('characters',{})
    if not isinstance(chars,Mapping):raise ValueError('Malformed character roster')
    for guid,c in chars.items():
        if not isinstance(c,Mapping) or not str(guid).startswith('Player-'):
            raise ValueError('Malformed character record')
        if not c.get('name') or not c.get('realm'):raise ValueError('Missing character identity')
        yield str(guid),'profile','profile',stamp(c.get('lastSeen')),'character_seen',dict(c)
        if source=='DuckMooFolio.lua':
            for pid,p in c.get('professions',{}).items():
                if not isinstance(p,Mapping):raise ValueError('Malformed profession')
                if not p.get('name') or not p.get('id',pid):continue
                for eid,e in p.get('expansions',{}).items():
                    if not isinstance(e,Mapping):raise ValueError('Malformed profession expansion')
                    body={'profession_id':p.get('id',pid),'profession':p['name'],**dict(e)}
                    yield str(guid),'profession',str(e.get('id',eid)),stamp(e.get('seenAt') or p.get('seenAt')),'profession_seen',body
            for rid,r in c.get('reputations',{}).items():
                if not isinstance(r,Mapping):raise ValueError('Malformed reputation')
                yield str(guid),'reputation',str(rid),stamp(c.get('repSeenAt')),'reputation_batch',dict(r)
        else:
            for pid,p in c.get('professions',{}).items():
                if not isinstance(p,Mapping):raise ValueError('Malformed concentration record')
                if not p.get('name'):continue
                yield str(guid),'concentration',str(p.get('skillLineID',pid)),stamp(p.get('observedAt')),'concentration_sample',dict(p)


def normalize_characters(conn,data,source,namespace,snapshot_id):
    import hashlib
    from datetime import datetime,timezone
    from financials import canonical
    records=0
    with conn.cursor() as cur:
        cur.execute('CREATE TEMP TABLE character_stage (LIKE nexus.character_records) ON COMMIT DROP')
        with cur.copy('COPY character_stage FROM STDIN') as out:
            for guid,kind,key,when,precision,payload in character_rows(source,data):
                identity=canonical([namespace,source,guid,kind,key,when,precision,payload])
                oid=hashlib.sha256(identity.encode()).hexdigest()
                out.write_row((oid,namespace,source,guid,kind,key,
                    datetime.fromtimestamp(when,timezone.utc) if when else None,precision,canonical(payload)))
                records+=1
        cur.execute('INSERT INTO nexus.character_records SELECT DISTINCT ON(id) * FROM character_stage ON CONFLICT DO NOTHING')
        inserted=cur.rowcount
        cur.execute('INSERT INTO nexus.snapshot_characters SELECT %s,id FROM character_stage GROUP BY id ON CONFLICT DO NOTHING',(snapshot_id,))
    return inserted,records

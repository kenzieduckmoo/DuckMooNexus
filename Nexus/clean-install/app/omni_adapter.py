"""Independent Omni Capture source; raw archival is handled by source_importer."""
import re
from collections.abc import Mapping

OMNI_SOURCE='DuckMooOmniCapture.lua'
OMNI_VERSION='0.1.0-omni1'
SECTIONS={'profile','currencies','vault','lockouts','keystone','equipment','quests','knowledge','inventory','reputations'}

def omni_rows(data):
    db=data.get('DuckMooOmniCaptureDB')
    if not isinstance(db,Mapping) or db.get('schema')!=1:raise ValueError('Unsupported Omni Capture schema')
    chars=db.get('characters',{})
    if not isinstance(chars,Mapping):raise ValueError('Malformed Omni Capture characters')
    for guid,c in chars.items():
        if not re.fullmatch(r'Player-\d+-[0-9A-Fa-f]+',str(guid)) or not isinstance(c,Mapping):raise ValueError('Invalid Omni identity')
        if not c.get('name') or not c.get('realm'):raise ValueError('Missing Omni character name/realm')
        sections=c.get('sections',{})
        if not isinstance(sections,Mapping):raise ValueError('Malformed Omni sections')
        identity={k:c.get(k) for k in ('guid','name','realm','lastSeen','sequence','droppedEvents')}
        yield guid,'omni_identity','identity',c.get('lastSeen'),'character_seen',identity
        for key,section in sections.items():
            if key not in SECTIONS or not isinstance(section,Mapping):raise ValueError('Unsupported Omni section')
            if section.get('status') not in ('captured','partial','unavailable'):raise ValueError('Unknown Omni coverage')
            yield guid,'omni_section',key,section.get('observedAt'),'section_seen',dict(section)
        events=c.get('events',{})
        entries=events.values() if isinstance(events,Mapping) else events if isinstance(events,list) else None
        if entries is None:raise ValueError('Malformed Omni event journal')
        for event in entries:
            if not isinstance(event,Mapping) or type(event.get('id')) is not int or event['id']<=0 or type(event.get('at')) is not int:raise ValueError('Malformed Omni event')
            if event.get('kind') not in ('session_start','session_end','level','quest_completed','loot','death','achievement','encounter'):raise ValueError('Unsupported Omni event')
            yield guid,'omni_event',str(event['id']),event['at'],'event_seen',dict(event)

def normalize_omni(conn,data,namespace,snapshot_id):
    import hashlib
    from datetime import datetime,timezone
    from character_extras import json_data
    from financials import canonical
    count=0
    with conn.cursor() as cur:
        cur.execute('CREATE TEMP TABLE omni_stage (LIKE nexus.character_records) ON COMMIT DROP')
        with cur.copy('COPY omni_stage FROM STDIN') as out:
            for guid,kind,key,when,precision,payload in omni_rows(data):
                if when is not None and (type(when) is not int or not 0<when<4102444800):raise ValueError('Invalid Omni observation timestamp')
                payload=json_data(payload)
                identity=canonical([namespace,OMNI_SOURCE,guid,kind,key,when,payload])
                out.write_row((hashlib.sha256(identity.encode()).hexdigest(),namespace,OMNI_SOURCE,guid,kind,key,datetime.fromtimestamp(when,timezone.utc) if when else None,precision,canonical(payload)))
                count+=1
        cur.execute('INSERT INTO nexus.character_records SELECT DISTINCT ON(id) * FROM omni_stage ON CONFLICT DO NOTHING')
        inserted=cur.rowcount
        cur.execute('INSERT INTO nexus.snapshot_characters SELECT %s,id FROM omni_stage GROUP BY id ON CONFLICT DO NOTHING',(snapshot_id,))
    return inserted,count

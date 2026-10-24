"""Independent Omni Capture source; raw archival is handled by source_importer."""
import re
from collections.abc import Mapping

OMNI_SOURCE='DuckMooOmniCapture.lua'
OMNI_VERSION='0.1.3-omni3'
SECTIONS={'profile','currencies','vault','lockouts','keystone','equipment','quests','knowledge','inventory','reputations'}

def omni_rows(data,recovered_profiles=None):
    db=data.get('DuckMooOmniCaptureDB')
    if not isinstance(db,Mapping) or db.get('schema')!=1:raise ValueError('Unsupported Omni Capture schema')
    chars=db.get('characters',{})
    if not isinstance(chars,Mapping):raise ValueError('Malformed Omni Capture characters')
    for guid,c in chars.items():
        if not re.fullmatch(r'Player-\d+-[0-9A-Fa-f]+',str(guid)) or not isinstance(c,Mapping):raise ValueError('Invalid Omni identity')
        if not c.get('name') or not c.get('realm'):raise ValueError('Missing Omni character name/realm')
        sections=c.get('sections',{})
        if not isinstance(sections,Mapping):raise ValueError('Malformed Omni sections')
        events=c.get('events',{})
        entries=list(events.values()) if isinstance(events,Mapping) else events if isinstance(events,list) else None
        if entries is None:raise ValueError('Malformed Omni event journal')
        # Versions 0.1.0/1 scanned during PLAYER_LOGOUT after APIs were cleared.
        # Only repair a profile that exactly matches a zero-valued session-end.
        # Raw archives and the original event remain intact; recovered values keep
        # their actual earlier timestamp, never the later logout time.
        profile=sections.get('profile',{})
        body=profile.get('data',{})
        terminal=any(isinstance(e,Mapping) and e.get('kind')=='session_end' and e.get('at')==profile.get('observedAt') and e.get('data')==body for e in entries)
        prior=(recovered_profiles or {}).get(guid)
        recovered=prior if prior and prior.get('discardedLogoutAt')==profile.get('observedAt') else None
        shutdown=body.get('ilvl')==0 and body.get('money')==0 and (terminal or recovered is not None)
        if shutdown:
            sections={k:dict(v) for k,v in sections.items()}
            candidates=[e for e in entries if isinstance(e,Mapping) and e.get('kind') in ('session_start','session_end') and isinstance(e.get('data'),Mapping) and (e['data'].get('ilvl',0)>0 or e['data'].get('money',0)>0) and e.get('at',0)<profile.get('observedAt',0)]
            if recovered is not None:
                sections['profile']=dict(recovered)
            elif candidates:
                earlier=max(candidates,key=lambda e:e['at'])
                sections['profile']={**profile,'data':dict(earlier['data']),'observedAt':earlier['at'],'status':'partial','detail':'Recovered earlier session observation; legacy logout cleared live APIs. Original raw capture retained.','recoveredFromEvent':earlier['id'],'discardedLogoutAt':profile.get('observedAt')}
            else:
                sections['profile']={**profile,'data':{k:v for k,v in body.items() if k not in ('ilvl','avgIlvl','money','health')},'status':'partial','detail':'Legacy logout cleared live APIs; zero wallet and item-level readings are unknown.'}
            for key in ('equipment','quests'):
                sec=sections.get(key)
                if sec and sec.get('observedAt')==profile.get('observedAt'):
                    sections[key]={**sec,'data':None,'status':'unavailable','detail':'Legacy logout read after live APIs cleared; awaiting an in-world observation.'}
        identity={k:c.get(k) for k in ('guid','name','realm','lastSeen','sequence','droppedEvents')}
        yield guid,'omni_identity','identity',c.get('lastSeen'),'character_seen',identity
        for key,section in sections.items():
            if key not in SECTIONS or not isinstance(section,Mapping):raise ValueError('Unsupported Omni section')
            if section.get('status') not in ('captured','partial','unavailable'):raise ValueError('Unknown Omni coverage')
            yield guid,'omni_section',key,section.get('observedAt'),'section_seen',dict(section)
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
        # Rotation removes archived events from the current addon queue, not
        # their history in PostgreSQL. Keep an already-proven legacy recovery
        # when an unvisited character still has that exact old logout section.
        recoveries={}
        for guid,c in data.get('DuckMooOmniCaptureDB',{}).get('characters',{}).items():
            profile=c.get('sections',{}).get('profile',{})
            body=profile.get('data') or {}
            if body.get('ilvl')==0 and body.get('money')==0 and profile.get('observedAt'):
                cur.execute("SELECT payload FROM nexus.character_records WHERE namespace=%s AND source=%s AND character_guid=%s AND record_kind='omni_section' AND record_key='profile' AND payload->>'discardedLogoutAt'=%s AND payload ? 'recoveredFromEvent' ORDER BY observed_at DESC,id DESC LIMIT 1",(namespace,OMNI_SOURCE,guid,str(profile['observedAt'])))
                prior=cur.fetchone()
                if prior:recoveries[guid]=prior[0]
        cur.execute('CREATE TEMP TABLE omni_stage (LIKE nexus.character_records) ON COMMIT DROP')
        with cur.copy('COPY omni_stage FROM STDIN') as out:
            for guid,kind,key,when,precision,payload in omni_rows(data,recoveries):
                if when is not None and (type(when) is not int or not 0<when<4102444800):raise ValueError('Invalid Omni observation timestamp')
                payload=json_data(payload)
                identity=canonical([namespace,OMNI_SOURCE,guid,kind,key,when,payload])
                out.write_row((hashlib.sha256(identity.encode()).hexdigest(),namespace,OMNI_SOURCE,guid,kind,key,datetime.fromtimestamp(when,timezone.utc) if when else None,precision,canonical(payload)))
                count+=1
        cur.execute('INSERT INTO nexus.character_records SELECT DISTINCT ON(id) * FROM omni_stage ON CONFLICT DO NOTHING')
        inserted=cur.rowcount
        cur.execute('DELETE FROM nexus.snapshot_characters l USING nexus.character_records r WHERE l.snapshot_id=%s AND l.observation_id=r.id AND r.source=%s',(snapshot_id,OMNI_SOURCE))
        cur.execute('INSERT INTO nexus.snapshot_characters SELECT %s,id FROM omni_stage GROUP BY id ON CONFLICT DO NOTHING',(snapshot_id,))
    return inserted,count

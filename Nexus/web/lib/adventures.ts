import {rows} from './db';
export async function adventures(client:string,guid:string,beforeAt:string|null=null,beforeId:string|null=null){
 const namespace=client==='forever'?'forever-main-account':'retail-main-account';
 const characters=await rows(`SELECT i.character_guid,i.payload->>'name' AS name,i.payload->>'realm' AS realm,p.payload->'data' AS profile,l.payload->'data' AS life,i.observed_at
 FROM nexus.current_omni_records i LEFT JOIN nexus.current_omni_records p ON p.namespace=i.namespace AND p.character_guid=i.character_guid AND p.record_kind='omni_section' AND p.record_key='profile'
 LEFT JOIN nexus.current_omni_records l ON l.namespace=i.namespace AND l.character_guid=i.character_guid AND l.record_kind='omni_section' AND l.record_key='life'
 WHERE i.namespace=$1 AND i.record_kind='omni_identity' ORDER BY i.payload->>'name'`,[namespace]);
 const selected=characters.find(c=>c.character_guid===guid)??(!guid?characters[0]:null);
 const events=selected?await rows(`WITH unique_events AS (
 SELECT DISTINCT ON(coalesce(payload->>'journalID','legacy'),record_key,observed_at) id,observed_at,payload FROM nexus.character_records
 WHERE namespace=$1 AND character_guid=$2 AND source='DuckMooOmniCapture.lua' AND record_kind='omni_event'
 ORDER BY coalesce(payload->>'journalID','legacy'),record_key,observed_at,id DESC)
 SELECT * FROM unique_events WHERE ($3::timestamptz IS NULL OR (observed_at,id)<($3::timestamptz,$4::text)) ORDER BY observed_at DESC,id DESC LIMIT 251`,[namespace,selected.character_guid,beforeAt,beforeId]):[];
 const last=events[249];return {client,characters,selected,events:events.slice(0,250),limited:events.length>250,next:events.length>250?{at:last.observed_at,id:last.id}:null,asOf:new Date().toISOString()};
}

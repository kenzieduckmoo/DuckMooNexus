import 'server-only';
import {rows,account as defaultAccount} from './db';
import {professionSlots} from './profession-slots';
const clean=(s:unknown)=>typeof s==='string'?s.replace(/\|c[0-9a-fA-F]{8}|\|r/g,'').replace(/\|A:.*?\|a|\|T.*?\|t/g,''):s;
export async function roster(account=defaultAccount){
 const base=await rows(`SELECT c.character_guid,c.name,c.realm,c.class,c.class_name,c.race,c.faction,c.level,c.item_level,
 c.specialization,c.hero_specialization,c.role,c.zone,c.guild,c.last_seen,c.payload->'tags' AS tags,
 media.payload->'assets' AS media,refresh.status AS api_status,refresh.last_attempt AS api_checked_at
 FROM nexus.character_roster c LEFT JOIN LATERAL (
 SELECT payload FROM nexus.character_api_documents WHERE namespace=c.namespace AND character_guid=c.character_guid
 AND endpoint='media' AND status=200 ORDER BY last_checked_at DESC,id DESC LIMIT 1) media ON true
 LEFT JOIN nexus.character_api_refresh refresh ON refresh.namespace=c.namespace AND refresh.character_guid=c.character_guid
 WHERE c.namespace=$1 ORDER BY c.name,c.realm`,[account]);
 const omni=await rows(`SELECT character_guid,payload->'data' AS profile,observed_at FROM nexus.current_omni_records WHERE namespace=$1 AND record_kind='omni_section' AND record_key='profile'`,[account]);
 for(const o of omni){const p=o.profile;if(!p)continue;const found=base.find(c=>c.character_guid===o.character_guid);if(!found)base.push({...p,character_guid:o.character_guid,class:p.class,class_name:p.className,item_level:p.ilvl,specialization:p.specName,last_seen:o.observed_at,snapshot_only:true,source:'DuckMooOmniCapture.lua'});else if(o.observed_at&&(!found.last_seen||new Date(o.observed_at)>new Date(found.last_seen)))Object.assign(found,{level:p.level??found.level,item_level:p.ilvl??found.item_level,last_seen:o.observed_at});}
 const seen=new Set(base.map(c=>c.character_guid));
 const extras=await rows(`SELECT DISTINCT ON(character_guid) character_guid,payload->'identity' AS identity,observed_at,source FROM nexus.current_character_extras WHERE namespace=$1 ORDER BY character_guid,observed_at DESC NULLS LAST`,[account]);
 for(const e of extras)if(!seen.has(e.character_guid)&&e.identity?.name&&e.identity?.realm){base.push({...e.identity,character_guid:e.character_guid,class:e.identity.classFile??e.identity.class,last_seen:e.observed_at,snapshot_only:true,source:e.source});seen.add(e.character_guid);}
 const [folioProfessions,apiProfessions]=await Promise.all([
  rows(`SELECT character_guid,jsonb_build_object('primaryProfessions',payload->'primaryProfessions','profSeenAt',payload->'profSeenAt','professions',(SELECT jsonb_object_agg(p.key,jsonb_build_object('id',p.value->'id','name',p.value->'name')) FROM jsonb_each(CASE WHEN jsonb_typeof(payload->'professions')='object' THEN payload->'professions' ELSE '{}'::jsonb END) p)) AS payload FROM nexus.current_character_records WHERE namespace=$1 AND source='DuckMooFolio.lua' AND record_kind='profile'`,[account]),
  rows(`SELECT DISTINCT ON(character_guid) character_guid,jsonb_build_object('character',jsonb_build_object('id',payload->'character'->'id')) || CASE WHEN jsonb_typeof(payload->'primaries')='array' THEN jsonb_build_object('primaries',jsonb_path_query_array(payload,'$.primaries[*].profession')) WHEN payload ? 'primaries' THEN jsonb_build_object('primaries',payload->'primaries') ELSE '{}'::jsonb END AS payload,profile_observed_at,last_checked_at FROM nexus.character_api_documents WHERE namespace=$1 AND endpoint='professions' AND status=200 ORDER BY character_guid,last_checked_at DESC,id DESC`,[account])
 ]);
 const folioMap=new Map(folioProfessions.map(r=>[r.character_guid,r])),apiMap=new Map(apiProfessions.map(r=>[r.character_guid,r]));
 for(const c of base)c.professionSlots=professionSlots(folioMap.get(c.character_guid)??null,apiMap.get(c.character_guid)??null);
 return base;
}
export async function character(guid:string,account=defaultAccount){
 const [profiles,api,apiStatus,inventory,wallets,captures,extras,omniRows,questEvents]=await Promise.all([
 rows(`SELECT source,record_kind,record_key,observed_at,source_saved_at,captured_at,payload FROM nexus.current_character_records WHERE namespace=$1 AND character_guid=$2 ORDER BY source,record_kind,record_key`,[account,guid]),
 rows(`SELECT DISTINCT ON(endpoint) endpoint,payload,last_checked_at,first_fetched_at,response_modified_at,profile_observed_at FROM nexus.character_api_documents WHERE namespace=$1 AND character_guid=$2 AND status=200 ORDER BY endpoint,last_checked_at DESC,id DESC`,[account,guid]),
 rows(`SELECT endpoint,status,last_checked_at,response_modified_at FROM nexus.latest_character_api WHERE namespace=$1 AND character_guid=$2 ORDER BY endpoint`,[account,guid]),
 rows(`SELECT i.item_id,coalesce(i.name,c.name,'Item '||i.item_id) AS name,i.quantity,i.owner_kind,i.owner_key,i.location,i.slot_key,i.rarity,i.crafting_quality,i.is_bound,i.item_link,i.snapshot_file_saved_at,m.payload->>'_nexus_icon' AS icon
 FROM nexus.current_inventory i LEFT JOIN nexus.item_catalog c ON c.namespace=i.namespace AND c.item_id=i.item_id LEFT JOIN nexus.api_item_metadata m ON m.region='us' AND m.item_id=i.item_id AND $1='retail-main-account'
 WHERE i.namespace=$1 AND lower(replace(i.owner_key,' ','')) IN(SELECT lower(replace((payload->>'name')||'-'||(payload->>'realm'),' ','')) FROM nexus.current_character_records WHERE namespace=$1 AND character_guid=$2 AND record_kind='profile') ORDER BY i.location,i.name`,[account,guid]),
 rows(`WITH latest AS (SELECT DISTINCT ON(source) id,source,source_saved_at FROM nexus.source_snapshots WHERE namespace=$1 AND source IN('WarbandAccountant.lua','Syndicator.lua','DuckMooWarband.lua') ORDER BY source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC)
 SELECT o.source,o.copper,o.observed_at,o.quality,s.source_saved_at FROM latest s JOIN nexus.snapshot_observations l ON l.snapshot_id=s.id JOIN nexus.source_observations o ON o.id=l.observation_id
 WHERE o.kind='character_balance' AND o.namespace=$1 AND lower(replace(o.entity,' ','')) IN(SELECT lower(replace((payload->>'name')||'-'||(payload->>'realm'),' ','')) FROM nexus.current_character_records WHERE namespace=$1 AND character_guid=$2 AND record_kind='profile') ORDER BY o.observed_at DESC NULLS LAST,s.source_saved_at DESC`,[account,guid]),
 rows(`WITH latest AS (SELECT id FROM nexus.source_snapshots WHERE namespace=$1 AND source='DuckMooCapture.lua' AND normalized_version IS NOT NULL ORDER BY source_saved_at DESC NULLS LAST,captured_at DESC,id DESC LIMIT 1)
 SELECT o.kind,count(*) AS count,max(o.observed_at) AS observed_at FROM latest s JOIN nexus.snapshot_crafting l ON l.snapshot_id=s.id JOIN nexus.crafting_observations o ON o.id=l.observation_id WHERE o.character_guid=$2 GROUP BY o.kind`,[account,guid]),
 rows(`SELECT source,source_saved_at,observed_at,payload FROM nexus.current_character_extras WHERE namespace=$1 AND character_guid=$2 ORDER BY source`,[account,guid]),
 rows(`SELECT record_kind,record_key,payload,observed_at FROM nexus.current_omni_records WHERE namespace=$1 AND character_guid=$2 AND record_kind<>'omni_event'`,[account,guid]),
 rows(`SELECT id,observed_at,payload FROM nexus.character_records WHERE namespace=$1 AND character_guid=$2 AND source='DuckMooOmniCapture.lua' AND record_kind='omni_event' AND payload->>'kind'='quest_completed' ORDER BY observed_at DESC,id DESC LIMIT 40`,[account,guid])
 ]);
 const folio=profiles.find(r=>r.source==='DuckMooFolio.lua'&&r.record_kind==='profile'),planner=profiles.find(r=>r.source==='DuckMooPlanner.lua'&&r.record_kind==='profile');
 const omni=Object.fromEntries(omniRows.filter(r=>r.record_kind==='omni_section').map(r=>[r.record_key,r.payload]));const own=omni.profile?.data??{},ownAt=omni.profile?.observedAt?new Date(omni.profile.observedAt*1000).toISOString():null;
 if(!folio&&!planner&&!extras.length&&!omniRows.length)return null;
 const extraProfile=extras.flatMap(e=>Object.values(e.payload?.records??{})).find((r:any)=>r&&typeof r==='object'&&r.name&&r.realm) as any;
 const apiMap=Object.fromEntries(api.map(a=>[a.endpoint,a])),f=folio?.payload??extraProfile??extras[0]?.payload?.identity??own,summary=apiMap.summary?.payload??{};
 const apiAt=summary.last_login_timestamp?new Date(summary.last_login_timestamp).toISOString():null,folioAt=folio?.observed_at??extras[0]?.observed_at??null;
 const fields:Record<string,any>={};
 function choose(key:string,fv:unknown,av:unknown,observed=apiAt){const mapping:Record<string,string>={itemLevel:'ilvl',specialization:'specName',health:'health'};const ov=own[mapping[key]??key];if(ov!=null&&ov!==''&&ownAt&&(!folioAt||new Date(ownAt)>new Date(folioAt))&&(!observed||new Date(ownAt)>new Date(observed)||av==null)){fields[key]={value:clean(ov),source:'DuckMoo Omni Capture',observedAt:ownAt};return fields[key].value;}const hasF=fv!==undefined&&fv!==null&&fv!=='',hasA=av!==undefined&&av!==null&&av!=='';const useA=hasA&&(!hasF||observed&&(!folioAt||new Date(observed)>new Date(folioAt)));fields[key]={value:clean(useA?av:hasF?fv:null),source:useA?'Blizzard API':hasF?folio?'DuckMoo Folio':extras[0]?.source:'Not captured',observedAt:useA?observed:folioAt};return fields[key].value;}
 const merged={name:choose('name',f.name,summary.name),realm:choose('realm',f.realm,summary.realm?.name),class:choose('class',f.classFile??f.class,summary.character_class?.name?.toUpperCase().replace(/ /g,'')),className:choose('className',f.className,summary.character_class?.name),race:choose('race',f.race,summary.race?.name),level:choose('level',f.level,summary.level),faction:choose('faction',f.faction,summary.faction?.name),specialization:choose('specialization',f.specName,summary.active_spec?.name),itemLevel:choose('itemLevel',f.ilvl,summary.equipped_item_level),guild:choose('guild',f.guild,summary.guild?.name),title:choose('title',f.title,summary.active_title?.name),health:choose('health',f.health,apiMap.statistics?.payload.health,apiMap.statistics?.profile_observed_at??null),heroSpec:f.heroSpec,zone:choose('zone',f.zone,null),subzone:choose('subzone',f.subzone,null),role:f.role,bind:f.bind};
 const ownBags=Object.values(omni.inventory?.data?.bags??{}) as any[];
 const ownItems=ownBags.flatMap((b:any)=>Object.values(b.items??{}).filter((r:any)=>r!=null&&Number.isSafeInteger(r.itemID)&&r.itemID>0).map((r:any)=>({...r,bagID:b.bagID,bagName:b.name})));
 const apiEquipment=apiMap.equipment?.payload.equipped_items??[],slotNames=['','HEAD','NECK','SHOULDER','SHIRT','CHEST','WAIST','LEGS','FEET','WRIST','HANDS','FINGER_1','FINGER_2','TRINKET_1','TRINKET_2','BACK','MAIN_HAND','OFF_HAND','RANGED','TABARD'],ownEquipment=omni.equipment,apiEquipmentAt=apiMap.equipment?.profile_observed_at;
 const preferOwn=ownEquipment?.data&&(!apiEquipment.length||ownEquipment.observedAt&&(!apiEquipmentAt||ownEquipment.observedAt*1000>new Date(apiEquipmentAt).getTime()));
 const equipment=preferOwn?Object.entries(ownEquipment.data).flatMap(([slot,r]:[string,any])=>r?.itemID&&slotNames[Number(slot)]?[{slot:{type:slotNames[Number(slot)],name:slotNames[Number(slot)].replace(/_/g,' ')},item:{id:r.itemID},name:clean(r.link)||'Item '+r.itemID,source:'DuckMoo Omni Capture',level:r.itemLevel?{value:r.itemLevel,display_string:'Item Level '+r.itemLevel}:undefined}]:[]):apiEquipment,ids=[...new Set([...equipment.map((e:any)=>e.item?.id),...ownItems.map((r:any)=>r.itemID)].filter(Boolean))];
 const icons=account===defaultAccount&&ids.length?await rows(`SELECT item_id,payload->>'_nexus_icon' AS icon FROM nexus.api_item_metadata WHERE region='us' AND item_id=ANY($1::bigint[])`,[ids]):[];
 const iconMap=Object.fromEntries(icons.map(i=>[i.item_id,i.icon]));
 return {guid,gameClient:account===defaultAccount?'retail':'forever',merged,fields,omni,questEvents,omniIdentity:omniRows.find(r=>r.record_kind==='omni_identity')?.payload??null,omniObservedAt:ownAt,folio:f,planner:planner?.payload??{},profiles,api:apiMap,apiStatus,apiObservedAt:apiAt,folioObservedAt:folioAt,
 omniBagItems:ownItems.map((r:any)=>({...r,icon:iconMap[r.itemID]??null})),
 equipmentSource:preferOwn?'DuckMoo Omni Capture':'Blizzard profile',equipmentObservedAt:preferOwn?new Date(ownEquipment.observedAt*1000).toISOString():apiEquipmentAt,equipment:equipment.map((e:any)=>({...e,icon:iconMap[e.item?.id]??null})),inventory,wallets,captures,extras,
 professions:profiles.filter(r=>r.record_kind==='profession'),reputations:profiles.filter(r=>r.record_kind==='reputation'),concentration:profiles.filter(r=>r.record_kind==='concentration')};
}

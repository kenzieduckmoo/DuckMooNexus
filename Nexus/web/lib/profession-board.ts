import 'server-only';
import {rows,account} from './db';
import {roster} from './characters';
import {buildProfessionBoard} from './profession-board-model';
export async function professionBoard(days:number){
 const [characters,records,omni,knowledge,earnings,daily,bounds]=await Promise.all([
  roster(),
  rows(`SELECT character_guid,record_kind,record_key,payload-'knowledge' AS payload,observed_at,source FROM nexus.current_character_records WHERE namespace=$1 AND record_kind IN('profession','concentration')`,[account]),
  rows(`SELECT character_guid,record_key,payload FROM nexus.current_omni_records WHERE namespace=$1 AND record_kind='omni_section' AND record_key IN('knowledge','currencies')`,[account]),
  rows(`SELECT r.character_guid,e.value->'knowledgeData' AS data FROM nexus.current_character_extras r CROSS JOIN LATERAL jsonb_each(r.payload->'records') e WHERE r.namespace=$1 AND r.source='WarbandNexus.lua' AND e.key='WarbandNexusDB / global / characters / '||r.character_guid`,[account]),
  rows(`SELECT character,realm,profession,count(*)::int AS orders,sum(net_copper) AS net,count(*) FILTER(WHERE NOT gold_complete)::int AS incomplete,max(occurred_at) AS last_order FROM nexus.crafting_order_financials WHERE namespace=$1 AND order_type='3' AND occurred_at>=now()-($2::int*interval '1 day') AND occurred_at<=now() GROUP BY character,realm,profession`,[account,days]),
  rows(`SELECT (occurred_at AT TIME ZONE 'America/Chicago')::date::text AS day,character,realm,profession,count(*)::int AS orders,sum(net_copper) AS net,count(*) FILTER(WHERE NOT gold_complete)::int AS incomplete FROM nexus.crafting_order_financials WHERE namespace=$1 AND order_type='3' AND occurred_at>=now()-($2::int*interval '1 day') AND occurred_at<=now() GROUP BY 1,character,realm,profession ORDER BY 1`,[account,days]),
  rows(`SELECT d::date::text AS day FROM generate_series((now()-($1::int*interval '1 day')) AT TIME ZONE 'America/Chicago',now() AT TIME ZONE 'America/Chicago',interval '1 day') d`,[days])
 ]);
 return {rows:buildProfessionBoard(characters,records,omni,knowledge),characters:characters.map(c=>({guid:c.character_guid,name:c.name,realm:c.realm})),earnings,daily,days:bounds.map(r=>r.day),range:days,asOf:new Date().toISOString()};
}

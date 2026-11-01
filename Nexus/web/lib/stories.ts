import 'server-only';
import {Pool} from 'pg';
import {rows} from './db';
import {adventures} from './adventures';
import {blankStory} from './story-model';
export const storyNamespace=(client:string)=>client==='forever'?'forever-main-account':'retail-main-account';
const unique=`SELECT DISTINCT ON(coalesce(payload->>'journalID','legacy'),record_key,observed_at) id,observed_at,payload FROM nexus.character_records WHERE namespace=$1 AND character_guid=$2 AND source='DuckMooOmniCapture.lua' AND record_kind='omni_event' ORDER BY coalesce(payload->>'journalID','legacy'),record_key,observed_at,id DESC`;
export async function captureHealth(client:string,guid=''){
 const ns=storyNamespace(client);
 const [snapshots,identities,sections]=await Promise.all([
  rows(`SELECT id,source_saved_at,captured_at,imported_at,normalized_version FROM nexus.source_snapshots WHERE namespace=$1 AND source='DuckMooOmniCapture.lua' ORDER BY source_saved_at DESC NULLS LAST,captured_at DESC,id DESC LIMIT 1`,[ns]),
  rows(`SELECT character_guid,payload,observed_at FROM nexus.current_omni_records WHERE namespace=$1 AND record_kind='omni_identity' AND ($2='' OR character_guid=$2) ORDER BY payload->>'name'`,[ns,guid]),
  rows(`SELECT character_guid,record_key,payload->>'status' AS status,payload->>'detail' AS detail,payload->'omitted' AS omitted,observed_at FROM nexus.current_omni_records WHERE namespace=$1 AND record_kind='omni_section' AND ($2='' OR character_guid=$2) ORDER BY character_guid,record_key`,[ns,guid])
 ]);
 return {client,snapshot:snapshots[0]??null,identities,sections,asOf:new Date().toISOString()};
}
export async function storyData(client:string,guid:string){
 const data=await adventures(client,guid);if(!data.selected)return {...data,document:blankStory(),revision:0,summary:{},highlights:[],health:await captureHealth(client,guid)};
 const ns=storyNamespace(client),id=data.selected.character_guid;
 const [summary,highlights,documents,gaps,health]=await Promise.all([
  rows(`WITH events AS (${unique}) SELECT count(*)::int AS total,min(observed_at) AS first_at,max(observed_at) AS last_at,count(*) FILTER(WHERE payload->>'kind'='quest_completed')::int AS quests,count(*) FILTER(WHERE payload->>'kind'='encounter' AND payload#>>'{data,success}'='1')::int AS victories,count(*) FILTER(WHERE payload->>'kind'='achievement')::int AS achievements,max(CASE WHEN payload->>'kind'='level' AND payload#>>'{data,level}' ~ '^[0-9]+$' THEN (payload#>>'{data,level}')::int END) AS highest_level FROM events`,[ns,id]),
  rows(`WITH events AS (${unique}) SELECT id,observed_at,payload FROM (SELECT *,row_number() OVER(PARTITION BY payload->>'kind' ORDER BY observed_at DESC,id DESC) AS choice FROM events) ranked WHERE choice<=8 AND payload->>'kind' IN('level','death','achievement','encounter','quest_completed') ORDER BY CASE payload->>'kind' WHEN 'death' THEN 0 WHEN 'level' THEN 1 WHEN 'achievement' THEN 2 WHEN 'encounter' THEN 3 ELSE 4 END,observed_at DESC,id DESC LIMIT 40`,[ns,id]),
  rows('SELECT document,revision,updated_at FROM nexus.character_stories WHERE namespace=$1 AND character_guid=$2',[ns,id]),
  rows(`SELECT coalesce(sum(n),0)::int AS possible_gaps FROM (SELECT greatest(0,max(record_key::bigint)-min(record_key::bigint)+1-count(DISTINCT record_key::bigint)) AS n FROM nexus.character_records WHERE namespace=$1 AND character_guid=$2 AND source='DuckMooOmniCapture.lua' AND record_kind='omni_event' AND payload ? 'journalID' AND record_key ~ '^[0-9]{1,15}$' GROUP BY payload->>'journalID') g`,[ns,id]),
  captureHealth(client,id)
 ]);
 return {...data,document:documents[0]?.document??blankStory(),revision:documents[0]?.revision??0,updatedAt:documents[0]?.updated_at??null,summary:{...summary[0],possible_gaps:gaps[0]?.possible_gaps??0},highlights:highlights.sort((a,b)=>new Date(a.observed_at).getTime()-new Date(b.observed_at).getTime()),health};
}
let writer:Pool|undefined;
export async function saveStory(client:string,guid:string,document:any,revision:number){
 if(!process.env.STORY_DATABASE_URL)throw Error('Story storage unavailable');
 writer??=new Pool({connectionString:process.env.STORY_DATABASE_URL,max:2,connectionTimeoutMillis:4000,options:'-c statement_timeout=5000'});
 const ns=storyNamespace(client);
 // The dedicated role can only read/write personal stories, never source data.
 const result=revision===0?await writer.query(`INSERT INTO nexus.character_stories(namespace,character_guid,document) VALUES($1,$2,$3) ON CONFLICT DO NOTHING RETURNING revision,updated_at`,[ns,guid,document]):await writer.query(`UPDATE nexus.character_stories SET document=$3,revision=revision+1,updated_at=now() WHERE namespace=$1 AND character_guid=$2 AND revision=$4 RETURNING revision,updated_at`,[ns,guid,document,revision]);
 return result.rows[0]??null;
}

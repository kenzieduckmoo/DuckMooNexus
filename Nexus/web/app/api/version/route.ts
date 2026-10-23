import {NextResponse} from 'next/server';
import {rows,account} from '@/lib/db';
export const dynamic='force-dynamic';
export async function GET(){try{
 const [version]=await rows(`SELECT
   (SELECT max(id)::text FROM nexus.source_snapshots WHERE namespace=$1) AS sources,
   (SELECT max(id)::text FROM nexus.api_snapshots) AS market,
   (SELECT max(last_checked_at)::text FROM nexus.character_api_documents WHERE namespace=$1) AS characters,
   (SELECT max(updated_at)::text FROM nexus.crafting_documents WHERE namespace=$1) AS documents`,[account]);
 let crafting='';try{const response=await fetch('http://craft-engine:8766/status',{cache:'no-store',signal:AbortSignal.timeout(2000)});if(response.ok)crafting=(await response.json()).version??'';}catch{}
 return NextResponse.json({...version,crafting},{headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({error:'Freshness check unavailable'},{status:503});}}

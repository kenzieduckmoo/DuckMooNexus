import {NextRequest,NextResponse} from 'next/server';
import {storyData,captureHealth,saveStory,storyNamespace} from '@/lib/stories';
import {storyExport,validateStory} from '@/lib/story-model';
import {rows} from '@/lib/db';
export const dynamic='force-dynamic';
function scope(r:NextRequest){const client=r.nextUrl.searchParams.get('client')||'retail',guid=r.nextUrl.searchParams.get('character')||'';if(!['retail','forever'].includes(client)||guid&&!/^Player-\d+-[A-Fa-f0-9]+$/.test(guid))throw Error('Choose a valid client and character.');return {client,guid};}
export async function GET(r:NextRequest){
 let s;try{s=scope(r);}catch{return NextResponse.json({error:'Choose a valid client and character.'},{status:400});}
 try{
  if(r.nextUrl.searchParams.get('view')==='health')return NextResponse.json(await captureHealth(s.client,s.guid),{headers:{'Cache-Control':'no-store'}});
  const data=await storyData(s.client,s.guid),format=r.nextUrl.searchParams.get('export');
  if(format){if(!['text','outline','json'].includes(format))return NextResponse.json({error:'Choose a valid export.'},{status:400});if(!data.selected)return NextResponse.json({error:'This character has no captured story yet.'},{status:404});
   const name=String(data.selected.name).replace(/[^A-Za-z0-9_-]/g,'_')||'character';
   return new NextResponse(format==='json'?JSON.stringify({...data,exportCoverage:'Summary covers the retained archive. Highlights and recent events are selected subsets; next supplies the history cursor.'},null,2):storyExport(data,data.document,format),{headers:{'Content-Type':format==='json'?'application/json; charset=utf-8':'text/plain; charset=utf-8','Content-Disposition':`attachment; filename="${name}-${format==='outline'?'documentary-outline':'biography'}.${format==='json'?'json':'txt'}"`,'Cache-Control':'no-store'}});
  }
  return NextResponse.json(data,{headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({error:'Character stories are reconnecting. Your saved writing is preserved.'},{status:503});}
}
export async function POST(r:NextRequest){
 let s;try{s=scope(r);}catch{return NextResponse.json({error:'Choose a valid client and character.'},{status:400});}
 if(!s.guid)return NextResponse.json({error:'Choose a captured character.'},{status:400});
 const origin=r.headers.get('origin'),host=r.headers.get('host');if(!host||!origin||!['http://'+host,'https://'+host].includes(origin))return NextResponse.json({error:'Open the character story on Nexus to save changes.'},{status:403});
 if(!r.headers.get('content-type')?.startsWith('application/json'))return NextResponse.json({error:'Use a JSON story request.'},{status:415});
 if(Number(r.headers.get('content-length')||0)>1000000)return NextResponse.json({error:'This story is too large.'},{status:413});
 let document,revision;
 try{const raw=await r.text();if(raw.length>1000000)return NextResponse.json({error:'This story is too large.'},{status:413});const body=JSON.parse(raw);document=validateStory(body.document);revision=body.revision;if(!Number.isSafeInteger(revision)||revision<0)throw Error('Reload the saved story before editing.');}catch(e){return NextResponse.json({error:e instanceof Error?e.message:'Choose a valid story.'},{status:400});}
 try{
  const ns=storyNamespace(s.client),exists=await rows(`SELECT 1 FROM nexus.current_omni_records WHERE namespace=$1 AND character_guid=$2 AND record_kind='omni_identity' LIMIT 1`,[ns,s.guid]);if(!exists.length)return NextResponse.json({error:'This character has not been captured yet.'},{status:404});
  const ids=[...new Set(document.moments.map((m:any)=>m.eventID).filter(Boolean))];
  if(ids.length){const evidence=await rows(`SELECT id,observed_at FROM nexus.character_records WHERE namespace=$1 AND character_guid=$2 AND source='DuckMooOmniCapture.lua' AND record_kind='omni_event' AND id=ANY($3::text[])`,[ns,s.guid,ids]);if(evidence.length!==ids.length)return NextResponse.json({error:'One selected event does not belong to this character.'},{status:400});const dates=new Map(evidence.map(e=>[e.id,new Date(e.observed_at).toISOString()]));document.moments=document.moments.map((m:any)=>m.eventID?{...m,at:dates.get(m.eventID)!}:m);}
  const result=await saveStory(s.client,s.guid,document,revision);if(!result)return NextResponse.json({error:'This story changed in another tab or device. Your unsaved text is still here. Download your draft before reloading.'},{status:409});
  return NextResponse.json({...result,document},{headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({error:'The story could not be saved. Your draft is still on this page; download it before leaving.'},{status:503});}
}

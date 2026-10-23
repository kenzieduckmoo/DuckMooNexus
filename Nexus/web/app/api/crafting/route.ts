import {NextRequest,NextResponse} from 'next/server';
export const dynamic='force-dynamic';
export const maxDuration=120;
const engine='http://craft-engine:8766/';
async function forward(request:NextRequest,body?:string){try{const r=await fetch(engine+request.nextUrl.search,{method:body===undefined?'GET':'POST',body,headers:body===undefined?{}:{'Content-Type':'application/json'},cache:'no-store',signal:AbortSignal.timeout(120000)});return new NextResponse(await r.text(),{status:r.status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});}catch{return NextResponse.json({error:'The crafting workspace is reconnecting. Your saved choices are preserved.'},{status:503});}}
export async function GET(request:NextRequest){return forward(request);}
export async function POST(request:NextRequest){
 const origin=request.headers.get('origin'),host=request.headers.get('host');
 if(!origin||!host||origin!=='http://'+host)return NextResponse.json({error:'Open the Crafting Desk on Nexus to save changes.'},{status:403});
 if(!request.headers.get('content-type')?.startsWith('application/json'))return NextResponse.json({error:'Use a JSON crafting request.'},{status:415});
 if(Number(request.headers.get('content-length')??0)>1000000)return NextResponse.json({error:'The saved change is too large.'},{status:413});
 const raw=await request.text();if(raw.length>1000000)return NextResponse.json({error:'The saved change is too large.'},{status:413});
 try{JSON.parse(raw);}catch{return NextResponse.json({error:'Invalid crafting request.'},{status:400});}
 return forward(request,raw);
}

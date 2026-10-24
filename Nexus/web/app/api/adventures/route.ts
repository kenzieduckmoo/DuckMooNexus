import {NextRequest,NextResponse} from 'next/server';
import {adventures} from '@/lib/adventures';
export const dynamic='force-dynamic';
export async function GET(r:NextRequest){const client=r.nextUrl.searchParams.get('client')||'retail',guid=r.nextUrl.searchParams.get('character')||'',beforeAt=r.nextUrl.searchParams.get('beforeAt'),beforeId=r.nextUrl.searchParams.get('beforeId');
 if((beforeAt||beforeId)&&(!beforeAt||beforeAt.length>40||!Number.isFinite(Date.parse(beforeAt))||!beforeId||!/^[a-f0-9]{64}$/.test(beforeId)))return NextResponse.json({error:'Choose a valid history position.'},{status:400});
 if(!['retail','forever'].includes(client)||guid&&!/^Player-\d+-[A-Fa-f0-9]+$/.test(guid))return NextResponse.json({error:'Choose a valid client and character.'},{status:400});
 try{return NextResponse.json(await adventures(client,guid,beforeAt,beforeId),{headers:{'Cache-Control':'no-store'}});}catch{return NextResponse.json({error:'The adventure journal is reconnecting.'},{status:503});}}

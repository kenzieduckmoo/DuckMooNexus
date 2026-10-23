import {NextRequest,NextResponse} from 'next/server';
import {roster,character} from '@/lib/characters';
export const dynamic='force-dynamic';
export async function GET(request:NextRequest){const guid=request.nextUrl.searchParams.get('guid');if(guid&&!/^Player-\d+-[A-Fa-f0-9]+$/.test(guid))return NextResponse.json({error:'Choose a valid character.'},{status:400});try{const data=guid?await character(guid):await roster();return NextResponse.json(data??{error:'Character not found.'},{status:data?200:404,headers:{'Cache-Control':'no-store'}});}catch(e){console.error('Character read failed',e instanceof Error?e.name:'Error');return NextResponse.json({error:'Character data is temporarily unavailable.'},{status:503});}}

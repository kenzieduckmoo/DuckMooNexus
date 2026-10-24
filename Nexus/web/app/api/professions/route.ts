import {NextRequest,NextResponse} from 'next/server';
import {professionBoard} from '@/lib/profession-board';
export const dynamic='force-dynamic';
export async function GET(request:NextRequest){const days=Number(request.nextUrl.searchParams.get('days')??30);if(![7,30,90].includes(days))return NextResponse.json({error:'Choose 7, 30 or 90 days.'},{status:400});try{return NextResponse.json(await professionBoard(days),{headers:{'Cache-Control':'no-store'}});}catch(e){console.error('Profession board unavailable',e instanceof Error?e.message:'Unknown');return NextResponse.json({error:'The profession board is reconnecting. Your captured data is preserved.'},{status:503});}}

import {NextRequest,NextResponse} from 'next/server';
import {rows} from '@/lib/db';
export const dynamic='force-dynamic';
export async function GET(request:NextRequest){const raw=request.nextUrl.searchParams.get('ids')??'';if(raw.length>2500||!/^\d+(,\d+)*$/.test(raw))return NextResponse.json({},{status:400});const ids=[...new Set(raw.split(',').map(Number))];if(ids.length>200||ids.some(n=>!Number.isSafeInteger(n)||n<1))return NextResponse.json({},{status:400});try{const data=await rows(`SELECT item_id,payload->>'_nexus_icon' AS icon FROM nexus.api_item_metadata WHERE region='us' AND item_id=ANY($1::bigint[])`,[ids]);return NextResponse.json(Object.fromEntries(data.filter(r=>r.icon).map(r=>[r.item_id,r.icon])));}catch{return NextResponse.json({},{status:503});}}

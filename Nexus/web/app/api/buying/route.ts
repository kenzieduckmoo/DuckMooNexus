import {NextRequest,NextResponse} from 'next/server';
import {buyingAdvisor} from '@/lib/buying';
export const dynamic='force-dynamic';
let cached:{key:string;at:number;data:unknown}|null=null;
export async function GET(request:NextRequest){
 const days=Number(request.nextUrl.searchParams.get('days')??30),horizon=Number(request.nextUrl.searchParams.get('horizon')??7);
 if(![30,90].includes(days)||![7,14].includes(horizon))return NextResponse.json({error:'Choose a valid purchase and planning range.'},{status:400});
 try{const key=days+'|'+horizon;if(!cached||cached.key!==key||Date.now()-cached.at>30000)cached={key,at:Date.now(),data:await buyingAdvisor(days,horizon)};return NextResponse.json(cached.data,{headers:{'Cache-Control':'no-store'}});}
 catch(e){console.error('Buying advisor unavailable',e instanceof Error?e.name:'Error');return NextResponse.json({error:'Buying advice is reconnecting. Your records are preserved.'},{status:503});}
}

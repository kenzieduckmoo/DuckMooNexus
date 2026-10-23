import { NextRequest, NextResponse } from 'next/server';
import { overview, search, item, scopes } from '@/lib/db';
export const dynamic='force-dynamic';
export async function GET(request: NextRequest) {
  const p=request.nextUrl.searchParams,view=p.get('view')??'overview',scope=p.get('scope')??'commodities',q=(p.get('q')??'').trim();
  if(q.length>100||! /^(commodities|connected-realm:[0-9]{1,6})$/.test(scope))return NextResponse.json({error:'Choose a valid search and market.'},{status:400});
  try {
    let data;
    if(view==='overview')data=await overview();
    else if(view==='scopes')data=await scopes();
    else if(view==='search')data=await search(q,scope,p.get('sort')??'name');
    else if(view==='item'){
      const id=Number(p.get('id')),days=Number(p.get('days')??7),variant=p.get('variant')??'';
      if(!Number.isSafeInteger(id)||id<1||![1,7,30].includes(days)||variant.length>4000)return NextResponse.json({error:'Choose a valid item and time range.'},{status:400});
      if(variant){try{const parsed=JSON.parse(variant);if(parsed===null||typeof parsed!=='object'||Array.isArray(parsed))throw Error();}catch{return NextResponse.json({error:'Choose a valid listing variant.'},{status:400});}}
      data=await item(id,scope,days,variant);
    } else return NextResponse.json({error:'Unknown view.'},{status:404});
    return NextResponse.json(data,{headers:{'Cache-Control':'private, max-age=15','X-Content-Type-Options':'nosniff'}});
  }catch(error){console.error('Nexus read failed',error instanceof Error?error.name:'Error');return NextResponse.json({error:'Nexus could not load this data. Try again shortly.'},{status:503});}
}

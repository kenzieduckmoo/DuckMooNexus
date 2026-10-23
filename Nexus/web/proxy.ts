import { NextRequest,NextResponse } from 'next/server';
export function proxy(request:NextRequest){
 const allowed=['10.20.30.239','10.20.30.239:80','10.20.30.239:3001','localhost:3000','localhost:3001','127.0.0.1:3000','127.0.0.1:3001'];
 if(!allowed.includes(request.headers.get('host')??''))return new NextResponse('Use the configured Nexus address.',{status:403});
 const response=NextResponse.next();response.headers.set('X-Content-Type-Options','nosniff');response.headers.set('Referrer-Policy','same-origin');return response;
}

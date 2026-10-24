'use strict';
const http=require('node:http'),{Worker}=require('node:worker_threads'),crypto=require('node:crypto');
const worker=new Worker(require('node:path').join(__dirname,'worker.cjs'));
let sequence=0,status={ready:false,version:''},mutations=Promise.resolve();const pending=new Map(),undo=new Map();
worker.on('message',message=>{if(message.status&&typeof message.status==='object'){status=message.status;return;}const call=pending.get(message.id);if(!call)return;pending.delete(message.id);clearTimeout(call.timeout);if(message.error){const e=Error(message.error);e.status=message.status;call.reject(e);}else call.resolve(message.result);});
worker.on('error',()=>{console.error('Craft calculation worker failed.');process.exit(1);});
function calculate(action,payload){return new Promise((resolve,reject)=>{const id=++sequence;const timeout=setTimeout(()=>{pending.delete(id);const e=Error('Calculation timed out; please try again.');e.status=503;reject(e);},120000);pending.set(id,{resolve,reject,timeout});worker.postMessage({id,action,payload});});}
const backend=process.env.CRAFTING_BACKEND||'http://crafting:8765';
function backendRequest(key,value,etag){return new Promise((resolve,reject)=>{const raw=value===undefined?null:JSON.stringify(value);const request=http.request(new URL('/api/'+key,backend),{method:raw===null?'GET':'POST',headers:{Host:'10.20.30.239:8765',...(raw===null?{}:{Origin:'http://10.20.30.239:8765','Content-Type':'application/json','Content-Length':Buffer.byteLength(raw)}),...(etag?{'If-Match':etag}:{})}},response=>{let data='';response.on('data',chunk=>{data+=chunk;if(data.length>2000000)request.destroy(Error('Saved document exceeds the supported size.'));});response.on('end',()=>{try{const value=JSON.parse(data);if(response.statusCode<200||response.statusCode>=300){const e=Error(value.error||'Saved choices are temporarily unavailable.');e.status=response.statusCode;reject(e);}else resolve({value,etag:response.headers.etag});}catch(e){reject(e);}});});request.setTimeout(15000,()=>request.destroy(Error('Saved choices timed out.')));request.on('error',reject);request.end(raw);});}
async function document(key){return backendRequest(key);}
async function save(key,value,etag){return backendRequest(key,value,etag);}
async function context(){const [plan,saved,guides]=await Promise.all([document('plan'),document('setups'),document('guides')]);return {plan,saved,guides,payload:{planDoc:plan.value,savedDoc:saved.value,guideDoc:guides.value}};}
async function mutate(input){
 const docs=await context();
 if(input.operation==='undo'){
  const previous=undo.get(input.token);if(!previous||previous.expires<Date.now()){const e=Error('Undo is no longer available. Your saved data is unchanged.');e.status=409;throw e;}
  const current=previous.key==='plan'?docs.plan:previous.key==='guides'?docs.guides:docs.saved;
  if(current.etag!==previous.expected){const e=Error('Another page changed this document. Undo was stopped to preserve the newer changes.');e.status=409;throw e;}
  await save(previous.key,previous.value,current.etag);undo.delete(input.token);return {ok:true};
 }
 const prepared=await calculate('prepare',{...input,...docs.payload}),before=prepared.key==='plan'?docs.plan:prepared.key==='guides'?docs.guides:docs.saved;
 const committed=await save(prepared.key,prepared.value,before.etag),token=crypto.randomUUID();
 for(const [key,value] of undo)if(value.expires<Date.now())undo.delete(key);
 undo.set(token,{key:prepared.key,value:before.value,expected:committed.etag,expires:Date.now()+1800000});
 return {ok:true,undoToken:token};
}
function send(response,code,data){const raw=JSON.stringify(data);response.writeHead(code,{'Content-Type':'application/json; charset=utf-8','Content-Length':Buffer.byteLength(raw),'Cache-Control':'no-store'});response.end(raw);}
http.createServer(async(request,response)=>{try{
 const url=new URL(request.url,'http://engine');
 if(request.method==='GET'&&url.pathname==='/status')return send(response,200,status);
 if(request.method==='GET'){
  const action=url.searchParams.get('view')||'init',input=Object.fromEntries(url.searchParams);
  if(!['init','products','batch','ready','guide','plan','saved'].includes(action))return send(response,404,{error:'Unknown crafting view.'});
  const docs=['init','products'].includes(action)?{payload:{}}:await context();
  return send(response,200,await calculate(action,{...input,...docs.payload}));
 }
 if(request.method==='POST'){
  let raw='';for await(const chunk of request){raw+=chunk;if(Buffer.byteLength(raw)>1000000)return send(response,413,{error:'The saved change is too large.'});}
  const input=JSON.parse(raw);const current=mutations.then(()=>mutate(input));mutations=current.catch(()=>{});return send(response,200,await current);
 }
 send(response,405,{error:'Unsupported method.'});
 }catch(e){const code=e.status||503;send(response,code,{error:code>=500?'Crafting data is being prepared. Existing saved choices are preserved.':e.message});}}).listen(8766,'0.0.0.0',()=>console.log('Nexus crafting engine listening.'));

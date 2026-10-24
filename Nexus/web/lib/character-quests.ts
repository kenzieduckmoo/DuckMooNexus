import {gameText,values} from './character-style';

type D=Record<string,any>;
const validID=(id:unknown):id is number=>typeof id==='number'&&Number.isSafeInteger(id)&&id>0;
export function questSamples(data:D){
 const api=data.api?.['quests/completed'],own=data.omni?.quests;
 const apiRows=values(api?.payload?.quests).filter((q:D)=>q&&validID(q.id));
 const names=new Map<number,string>();
 for(const q of apiRows)if(gameText(q.name))names.set(q.id,gameText(q.name));
 for(const e of data.questEvents??[]){const q=e.payload?.data;if(q&&validID(q.questID)&&gameText(q.name)&&!names.has(q.questID))names.set(q.questID,gameText(q.name));}
 const makeRows=(ids:number[])=>[...new Set(ids)].map(id=>({id,name:names.get(id)??null})).sort((a,b)=>a.name&&b.name?a.name.localeCompare(b.name):a.name?-1:b.name?1:a.id-b.id);
 const samples=[];
 if(api?.payload&&api.payload.quests!=null)samples.push({id:'api',name:'Blizzard API',at:api.profile_observed_at??null,status:'captured',rows:makeRows(apiRows.map((q:D)=>q.id))});
 if(own?.data!=null&&['captured','partial','unavailable'].includes(own.status)){
  const at=typeof own.observedAt==='number'?new Date(own.observedAt*1000).toISOString():null;
  samples.push({id:'omni',name:'DuckMoo Omni Capture',at,status:own.status,rows:makeRows(values(own.data).filter(validID))});
 }
 return samples.sort((a,b)=>(b.at?Date.parse(b.at):0)-(a.at?Date.parse(a.at):0));
}

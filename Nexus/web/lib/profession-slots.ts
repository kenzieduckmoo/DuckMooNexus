type D=Record<string,any>;
const primaryIDs=new Set([171,164,333,202,182,773,755,165,186,393,197]);
const entries=(v:any):any[]=>Array.isArray(v)?v:v&&typeof v==='object'?Object.values(v):[];
const at=(v:any)=>typeof v==='number'?v*1000:Date.parse(String(v??''));
export function professionSlots(folio:D|null,api:D|null){
 const samples:D[]=[];
 const p=folio?.payload??{},explicit=p.primaryProfessions;
 if(explicit?.complete===true&&Number.isInteger(explicit.count)&&explicit.count>=0&&explicit.count<=2&&explicit.seenAt){
  samples.push({count:explicit.count,names:entries(explicit.professions).map(x=>x.name).filter(Boolean),observedAt:new Date(explicit.seenAt*1000).toISOString(),source:'DuckMoo Folio'});
 }else if(p.profSeenAt&&p.professions&&typeof p.professions==='object'){
  const known=new Map<number,string>();for(const [key,v] of Object.entries(p.professions) as [string,D][]){const id=Number(v.id??key);if(primaryIDs.has(id))known.set(id,v.name);}
  if(known.size<=2)samples.push({count:known.size,names:[...known.values()],observedAt:new Date(p.profSeenAt*1000).toISOString(),source:'DuckMoo Folio'});
 }
 const omittedEmpty=!!api&&api.payload?.character?.id>0&&!Object.hasOwn(api.payload,'primaries');
 if(api&&(Array.isArray(api.payload?.primaries)||omittedEmpty)){
  const list=api.payload.primaries??[],seen=new Map<number,string>();
  for(const row of list){const id=Number(row.profession?.id??row.skill_line?.id??row.id);if(primaryIDs.has(id))seen.set(id,row.profession?.name??row.skill_line?.name??row.name);}
  // A malformed or unknown primary ID is not evidence of an empty slot.
  if(seen.size===list.length&&seen.size<=2)samples.push({count:seen.size,names:[...seen.values()],observedAt:api.profile_observed_at??api.last_checked_at,source:'Blizzard API'});
 }
 const best=samples.filter(s=>Number.isFinite(at(s.observedAt))).sort((a,b)=>at(b.observedAt)-at(a.observedAt))[0];
 return best?{...best,open:2-best.count}:{count:null,open:null,names:[],observedAt:null,source:null};
}
export const hasOpenProfession=(c:D)=>Number(c.level)>=80&&c.professionSlots?.open!=null&&c.professionSlots.open>0;

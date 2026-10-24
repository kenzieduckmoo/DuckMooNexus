import {gameText,values,characterSort} from './character-style';
import {knowledgeRows} from './character-progress';
type D=Record<string,any>;
export const professionKey=(name:unknown)=>gameText(name).replace(/^(Midnight|Khaz Algar|Dragon Isles|Shadowlands|Kul Tiran|Zandalari|Legion|Draenor|Pandaria|Cataclysm|Northrend|Outland|Classic)\s+/i,'').trim();
export const ownerKey=(name:unknown,realm:unknown)=>String(name??'').normalize('NFC').toLowerCase()+'|'+String(realm??'').normalize('NFC').replace(/[\s-]/g,'').toLowerCase();
export const earningsKey=(name:unknown,realm:unknown,profession:unknown)=>ownerKey(name,realm)+'|'+professionKey(profession).toLowerCase();
const finite=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v);
const iso=(v:unknown)=>finite(v)&&v>0&&v<4102444800?new Date(v*1000).toISOString():null;

export function concentrationProjection(sample:D|null,now=Date.now()/1000){
 if(!sample||!finite(sample.amount)||sample.amount<0||!finite(sample.max)||sample.max<=0||sample.amount>sample.max||!finite(sample.observedAt)||sample.observedAt<=0||sample.observedAt>now+300)return null;
 const rate=finite(sample.secondsPerPoint)&&sample.secondsPerPoint>0?sample.secondsPerPoint:null;
 const projected=rate?Math.min(sample.max,sample.amount+Math.max(0,now-sample.observedAt)/rate):null;
 return {observed:sample.amount,max:sample.max,projected,ratio:(projected??sample.amount)/sample.max,fullAt:rate?iso(sample.observedAt+(sample.max-sample.amount)*rate):null,at:iso(sample.observedAt),source:sample.source,status:sample.status??'captured'};
}

export function buildProfessionBoard(roster:D[],records:D[],omniRecords:D[],knowledgeRecords:D[]){
 const canonical=new Map<string,D>();
 const known=new Set(['Alchemy','Blacksmithing','Enchanting','Engineering','Inscription','Jewelcrafting','Leatherworking','Tailoring','Herbalism','Mining','Skinning','Cooking','Fishing','Archaeology','First Aid']);
 // Older collectors sometimes stored a child expansion under the open UI's
 // other parent profession. Its own expansion name/ID still identifies it.
 for(const record of records.filter(r=>r.record_kind==='profession')){const p=record.payload,base=professionKey(p?.name);if(p&&known.has(base)){const id=String(p.id??record.record_key),old=canonical.get(id);if(!old||Date.parse(record.observed_at??'')>Date.parse(old.at??''))canonical.set(id,{name:gameText(p.name),profession:base,at:record.observed_at});}}
 const byChar=new Map<string,D[]>();for(const r of records){const a=byChar.get(r.character_guid)??[];a.push(r);byChar.set(r.character_guid,a);}
 const ownByChar=new Map<string,D>();for(const r of omniRecords){const o=ownByChar.get(r.character_guid)??{};o[r.record_key]=r.payload;ownByChar.set(r.character_guid,o);}
 const wnByChar=new Map(knowledgeRecords.map(r=>[r.character_guid,r.data]));
 const result:D[]=[];
 for(const c of roster){
  const own=ownByChar.get(c.character_guid)??{},all=byChar.get(c.character_guid)??[],entries=new Map<string,D>();
  const ensure=(id:string,name:string,profession:string,expansion?:string)=>{const meta=canonical.get(id);if(meta){name=meta.name;profession=meta.profession;expansion=undefined;}let r=entries.get(id);if(!r){r={id,guid:c.character_guid,name,profession,expansion:expansion??(name.startsWith('Midnight ')?'Midnight':name!==profession?name.slice(0,-profession.length).trim():'Not captured'),character:{guid:c.character_guid,name:c.name,realm:c.realm,class:c.class,tags:c.tags,level:c.level,item_level:c.item_level},skill:null,concentration:null,knowledge:null};entries.set(id,r);}return r;};
  for(const record of all.filter(r=>r.record_kind==='profession')){const p=record.payload;if(!p)continue;const base=gameText(p.profession)||professionKey(p.name),r=ensure(String(p.id??record.record_key),gameText(p.name)||base,base);if(!r.skill||Date.parse(record.observed_at??'')>Date.parse(r.skill.at??'')||Date.parse(record.observed_at??'')===Date.parse(r.skill.at??'')&&!r.skill.ownerMatched&&base===r.profession)r.skill={rank:finite(p.rank)?p.rank:null,max:finite(p.max)?p.max:null,recipes:finite(p.recipes)&&base===r.profession?p.recipes:null,ownerMatched:base===r.profession,at:record.observed_at,source:record.source.replace('.lua','')};}
  for(const record of all.filter(r=>r.record_kind==='concentration')){
   const p=record.payload;if(!p)continue;const base=professionKey(p.name),name=p.expansion?`${p.expansion} ${base}`:base,r=ensure(String(p.skillLineID??record.record_key),name,base,p.expansion);
   r.concentration={...p,source:'DuckMoo Planner'};
   const currency=own.currencies?.data?.[p.currencyID],at=own.currencies?.observedAt;
   if(currency&&finite(currency.quantity)&&finite(currency.maxQuantity)&&finite(at)&&at>Number(p.observedAt??0)){
    const cycle=currency.rechargingCycleDurationMS,amount=currency.rechargingAmountPerCycle;
    r.concentration={amount:currency.quantity,max:currency.maxQuantity,observedAt:at,secondsPerPoint:finite(cycle)&&cycle>0&&finite(amount)&&amount>0?cycle/1000/amount:null,currencyID:p.currencyID,source:'DuckMoo Omni Capture',status:own.currencies.status};
   }
   if(p.patron)r.patronCheck={...p.patron,source:'DuckMoo Planner'};
  }
  for(const record of values(own.knowledge?.data)){
   const meta=record?.data,p=meta?.concentration;if(!p||!meta.skillLineID)continue;
   const name=gameText(meta.profession?.professionName??meta.profession?.name)||'Profession '+meta.skillLineID,r=ensure(String(meta.skillLineID),name,professionKey(name));
   if(!r.concentration||Number(p.observedAt)>Number(r.concentration.observedAt??0))r.concentration={...p,source:'DuckMoo Omni Capture'};
   const currency=own.currencies?.data?.[p.currencyID],at=own.currencies?.observedAt;
   if(currency&&finite(currency.quantity)&&finite(currency.maxQuantity)&&finite(at)&&at>Number(r.concentration.observedAt??0))r.concentration={amount:currency.quantity,max:currency.maxQuantity,observedAt:at,secondsPerPoint:finite(currency.rechargingCycleDurationMS)&&currency.rechargingCycleDurationMS>0&&finite(currency.rechargingAmountPerCycle)&&currency.rechargingAmountPerCycle>0?currency.rechargingCycleDurationMS/1000/currency.rechargingAmountPerCycle:null,currencyID:p.currencyID,source:'DuckMoo Omni Capture',status:own.currencies.status};
  }
  const knowledge=knowledgeRows({guid:c.character_guid,omni:own,extras:[{source:'WarbandNexus.lua',payload:{records:{['WarbandNexusDB / global / characters / '+c.character_guid]:{knowledgeData:wnByChar.get(c.character_guid)}}}}]});
  for(const k of knowledge){const name=gameText(k.expansionName??k.professionName),base=professionKey(k.professionName),r=ensure(String(k.skillLineID),name,professionKey(name)||base);r.knowledge={spent:finite(k.spentPoints)?k.spentPoints:null,unspent:finite(k.unspentPoints)?k.unspentPoints:null,at:iso(k.lastUpdate),source:k.source??'WarbandNexus'};}
  for(const r of entries.values()){
   r.key=r.guid+'|'+r.id;r.earningsKey=earningsKey(c.name,c.realm,r.profession);
   const times=[r.skill?.at,r.knowledge?.at,iso(r.concentration?.observedAt)].filter(Boolean).map(t=>new Date(t).toISOString()).sort();r.lastObservedAt=times.at(-1)??null;
   r.craftingProfession=['Alchemy','Blacksmithing','Enchanting','Engineering','Inscription','Jewelcrafting','Leatherworking','Tailoring'].includes(r.profession);
   result.push(r);
  }
 }
 return result.sort((a,b)=>characterSort(a.character,b.character)||a.profession.localeCompare(b.profession)||a.name.localeCompare(b.name));
}

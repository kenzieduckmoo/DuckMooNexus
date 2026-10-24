import {values} from './character-style';

type D=Record<string,any>;
export const numeric=(v:unknown):number|null=>typeof v==='number'&&Number.isFinite(v)?v:null;
export const stamp=(v:unknown):string|null=>typeof v==='number'&&Number.isFinite(v)&&v>0&&v<8640000000000?new Date(v*1000).toISOString():null;
export function progressSources(data:D){
 const records=(source:string)=>data.extras?.find((e:D)=>e.source===source)?.payload?.records??{};
 const wn=records('WarbandNexus.lua');
 const section=(path:string)=>Object.entries(wn).find(([key])=>key===`WarbandNexusDB / global / ${path} / ${data.guid}`)?.[1] as D|undefined;
 const wwt=values(records('WoWthing_Collector.lua')).find((r:D)=>r&&typeof r==='object'&&r.scanTimes)??{};
 const character=section('characters')??{};
 return {wn,section,character,wwt};
}
export function weeklySamples(data:D){
 const {section,character,wwt}=progressSources(data),activity=section('pveCache / greatVault / activities'),reward=section('pveCache / greatVault / rewards');
 const rows=[{id:'wowthing',name:'WoWthing Collector',at:stamp(wwt.scanTimes?.vault),reset:stamp(wwt.weeklyReset),
  available:typeof wwt.vaultAvailableRewards==='boolean'?wwt.vaultAvailableRewards:null,
  tracks:[['t1','Dungeons'],['t3','Raids'],['t6','World activities']].map(([key,name])=>({name,slots:values(wwt.vaultV2?.[key]?.tiers)})),
  keyLevel:numeric(wwt.keystoneLevel),keyName:null,keyId:numeric(wwt.keystoneInstance),keyAt:stamp(wwt.scanTimes?.mythicPlus),
  lockouts:values(wwt.lockouts).map((l:D)=>({...l,progress:numeric(l.defeatedBosses),total:numeric(l.maxBosses),resetAt:stamp(l.resetTime),bosses:values(l.bosses).flatMap((b:unknown)=>{if(typeof b!=='string'||!/^([01]):/.test(b))return [];return [{name:b.slice(2),done:b[0]==='1'}];})})),
  lockoutAt:stamp(wwt.scanTimes?.lockouts),hasLockouts:wwt.lockouts!=null},
 {id:'warbandnexus',name:'WarbandNexus',at:stamp(activity?.lastUpdate),reset:stamp(activity?.weeklyResetTime),
  available:typeof reward?.hasAvailableRewards==='boolean'?reward.hasAvailableRewards:null,
  tracks:[['mythicPlus','Dungeons'],['raids','Raids'],['world','World activities'],['pvp','PvP']].map(([key,name])=>({name,slots:values(activity?.[key])})),
  keyLevel:numeric(character.mythicKey?.level),keyName:character.mythicKey?.dungeonName??null,keyId:numeric(character.mythicKey?.mapID),keyAt:stamp(character.mythicKey?.scanTime),
  lockouts:['raids','dungeons'].flatMap(kind=>values(section('pveCache / lockouts / '+kind)).map((l:D)=>({...l,progress:numeric(l.encounterProgress),total:numeric(l.numEncounters),resetAt:stamp(l.resetAt),bosses:values(l.encounters).map((b:D)=>({name:b.name,done:b.isKilled===true||b.killed===true}))}))),
  lockoutAt:null,hasLockouts:section('pveCache / lockouts / raids')!=null||section('pveCache / lockouts / dungeons')!=null}];
 const o=data.omni??{},v=o.vault?.data,k=o.keystone?.data;
 if(v||k||o.lockouts?.data)rows.push({id:'omni',name:'DuckMoo Omni Capture',at:stamp(o.vault?.observedAt),reset:stamp(v?.weeklyResetTime),available:typeof v?.hasAvailableRewards==='boolean'?v.hasAvailableRewards:null,
 tracks:[['mythicPlus','Dungeons'],['raids','Raids'],['world','World activities'],['other','Other activities']].map(([key,name])=>({name,slots:values(v?.tracks?.[key])})),keyLevel:numeric(k?.level),keyName:k?.name??null,keyId:numeric(k?.mapID),keyAt:stamp(o.keystone?.observedAt),lockouts:values(o.lockouts?.data).map((r:D)=>({...r,progress:numeric(r.encounterProgress),total:numeric(r.numEncounters),resetAt:stamp(r.resetAt),bosses:values(r.encounters).map((b:D)=>({name:b.name,done:b.killed===true}))})),lockoutAt:stamp(o.lockouts?.observedAt),hasLockouts:o.lockouts?.data!=null});
 return rows.filter(r=>r.at||r.hasLockouts||r.keyLevel!=null).sort((a,b)=>Date.parse(b.at??'1970-01-01')-Date.parse(a.at??'1970-01-01'));
}
export function currencySamples(data:D){
 const {wwt,section}=progressSources(data);
 const wn=section('currencyData / currencies');
 const samples=[];
 if(wwt.currencies){samples.push({id:'wowthing',name:'WoWthing Collector',at:stamp(wwt.scanTimes?.currencies),rows:Object.entries(wwt.currencies).flatMap(([id,value])=>{
  if(!/^\d+$/.test(id)||Number(id)===0||typeof value!=='string'||!/^\d+(?::\d+){6}$/.test(value))return [];
  const [quantity,cap,weekly,earned,weeklyCap,useTotal,total]=value.split(':').map(Number);
  return [{id,quantity,cap:cap>0?cap:null,earned:weekly===1?earned:null,weeklyCap:weekly===1&&weeklyCap>0?weeklyCap:null,total,useTotal:useTotal===1}];
 })});}
 if(wn)samples.push({id:'warbandnexus',name:'WarbandNexus',at:null,rows:Object.entries(wn).flatMap(([id,value])=>/^\d+$/.test(id)&&Number(id)>0&&numeric(value)!=null?[{id,quantity:Number(value),cap:null,earned:null,weeklyCap:null,total:null,useTotal:false}]:[])});
 const own=data.omni?.currencies;
 if(own?.data)samples.unshift({id:'omni',name:'DuckMoo Omni Capture',at:stamp(own.observedAt),rows:Object.entries(own.data).flatMap(([id,r]:[string,any])=>numeric(r.quantity)!=null?[{id,name:r.name,iconFileID:r.iconFileID,accountWide:r.isAccountWide,quantity:r.quantity,cap:r.maxQuantity>0?r.maxQuantity:null,earned:r.canEarnPerWeek?r.quantityEarnedThisWeek:null,weeklyCap:r.maxWeeklyQuantity>0?r.maxWeeklyQuantity:null,total:numeric(r.totalEarned),useTotal:r.useTotalEarnedForMaxQty===true}]:[])});
 return samples.sort((a,b)=>Date.parse(b.at??'1970-01-01')-Date.parse(a.at??'1970-01-01'));
}
export function encounterRows(data:D,kind:string){
 return values(data.api?.['encounters/'+kind]?.payload?.expansions).flatMap((exp:D)=>values(exp.instances).flatMap((instance:D)=>values(instance.modes).map((mode:D)=>({
  id:[exp.expansion?.id,instance.instance?.id,mode.difficulty?.type].join('-'),name:instance.instance?.name??'Unnamed instance',expansion:exp.expansion?.name??'Unknown expansion',difficulty:mode.difficulty?.name??'Unknown difficulty',completed:numeric(mode.progress?.completed_count),total:numeric(mode.progress?.total_count),encounters:values(mode.progress?.encounters)
 }))));
}
export function knowledgeRows(data:D){
 const rows=values(progressSources(data).character.knowledgeData).filter((r:D)=>r&&typeof r==='object'&&r.professionName);
 for(const record of values(data.omni?.knowledge?.data)){
  const r=record?.data;if(!r)continue;
  const tabs=values(r.tabs),currency=tabs.flatMap((t:D)=>values(t.currencies).filter((c:D)=>t.spendCurrency!=null&&c.traitCurrencyID===t.spendCurrency)).find((c:D)=>numeric(c.quantity)!=null&&numeric(c.spent)!=null);
  const specTabs=tabs.map((t:D)=>{const nodes=values(t.nodes).filter((n:D)=>numeric(n.maxRanks)!=null&&numeric(n.currentRank??n.activeRank)!=null);return {tabID:t.tabID,name:t.name,spentRanks:nodes.length?nodes.reduce((n:number,r:D)=>n+(r.currentRank??r.activeRank),0):null,totalRanks:nodes.length?nodes.reduce((n:number,r:D)=>n+r.maxRanks,0):null};});
  const own={skillLineID:r.skillLineID,professionName:r.profession?.professionName??r.profession?.name??'Profession '+r.skillLineID,expansionName:r.profession?.professionName??r.profession?.name??'Profession '+r.skillLineID,lastUpdate:record.observedAt,spentPoints:currency?.spent,unspentPoints:currency?.quantity,specTabs,source:'DuckMoo Omni Capture'};
  const existing=rows.findIndex((p:D)=>String(p.skillLineID)===String(r.skillLineID));if(existing<0)rows.push(own);else if(Number(record.observedAt)>Number(rows[existing].lastUpdate??0))rows[existing]=own;
 }
 return rows.sort((a:D,b:D)=>Number(String(b.expansionName).startsWith('Midnight'))-Number(String(a.expansionName).startsWith('Midnight'))||String(a.expansionName).localeCompare(String(b.expansionName)));
}

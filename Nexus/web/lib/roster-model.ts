type D=Record<string,any>;
export const levelBands=['1-9','10-19','20-29','30-39','40-49','50-59','60-69','70-79','80-89','90+','80+'];
const list=(v:any):any[]=>Array.isArray(v)?v:v&&typeof v==='object'?Object.values(v):[];
const clean=(s:any)=>String(s??'').replace(/\|c[0-9a-fA-F]{8}|\|r/g,'').replace(/\|A:.*?\|a|\|T.*?\|t/g,'');
const token=(v:any)=>String(v??'').toUpperCase().replace(/[^A-Z]/g,'');
const healers=new Set(['PRIEST','SHAMAN','PALADIN','DRUID','MONK','EVOKER']);
const tanks=new Set(['WARRIOR','PALADIN','DRUID','DEATHKNIGHT','MONK','DEMONHUNTER']);
export const band=(c:D)=>c.level==null?'Unknown':Number(c.level)>=90?'90+':Number(c.level)<10?'1-9':Math.floor(Number(c.level)/10)*10+'-'+(Math.floor(Number(c.level)/10)*10+9);
export const xpFraction=(c:D)=>c.roster?.xpMax>0&&c.roster?.xp!=null?Math.min(.99999,Math.max(0,Number(c.roster.xp??0)/c.roster.xpMax)):null;
export const restedFraction=(c:D)=>c.roster?.xpMax>0&&c.roster.rested!=null?Number(c.roster.rested)/c.roster.xpMax:null;
export const tags=(c:D)=>list(c.tags??c.roster?.tags).map(clean);
export function professions(c:D){
 const out=list(c.professionRecords).filter(p=>p&&p.name&&Number(p.id)!==794);
 for(const name of c.professionSlots?.names??[])if(!out.some(p=>p.name===name))out.push({name,expansions:{}});
 return out;
}
export function matches(c:D,f:D){
 for(const key of ['class','race','faction','realm'])if(f[key]&&String(c[key]??'')!==f[key])return false;
 if(f.region&&c.roster?.realmRegion!==f.region)return false;
 if(f.role==='HEALER'&&!healers.has(token(c.class))||f.role==='TANK'&&!tanks.has(token(c.class)))return false;
 if(f.tag&&!tags(c).includes(f.tag))return false;
 if(f.levelBand){const parts=f.levelBand.split('-'),lo=parseInt(parts[0],10),hi=parts[1]?Number(parts[1]):Infinity;if(c.level==null||Number(c.level)<lo||Number(c.level)>(hi||Infinity))return false;}
 const open=c.professionSlots?.open;
 if(f.slots==='open80'&&!(Number(c.level)>=80&&open>0)||f.slots==='open'&&!(open>0)||f.slots==='full'&&open!==0||f.slots==='unknown'&&open!=null)return false;
 if(f.profession||f.expansion)if(!professions(c).some(p=>(!f.profession||p.name===f.profession)&&(!f.expansion||list(p.expansions).some(e=>e.name===f.expansion))))return false;
 if(f.reputation&&!list(c.roster?.reputations).some(r=>r.name===f.reputation))return false;
 const haystack=[c.name,c.realm,c.specialization,c.race,...tags(c),...list(c.roster?.notes)].join(' ').toLowerCase();
 return !f.search||haystack.includes(f.search.toLowerCase());
}
export function sortRoster(rows:D[],sort='level',role=''){
 return [...rows].sort((a,b)=>{
  if(role&&String(a.role).toUpperCase()!==String(b.role).toUpperCase()){if(String(a.role).toUpperCase()===role)return -1;if(String(b.role).toUpperCase()===role)return 1;}
  const score=(c:D)=>sort==='ilvl'?Number(c.item_level??-1):sort==='rested'?restedFraction(c)??-1:Number(c.level??-1)+(xpFraction(c)??0);
  return (sort==='name'?0:score(b)-score(a))||String(a.name).localeCompare(String(b.name))||String(a.realm).localeCompare(String(b.realm));
 });
}
export function census(rows:D[]){
 const result:Record<string,Record<string,number>>={faction:{},class:{},race:{},profession:{},levelBand:{},realm:{},tag:{},region:{}};
 for(const c of rows){
  const values:D={faction:[c.faction||'Unknown'],class:[c.class||'Unknown'],race:[c.race||'Unknown'],profession:professions(c).map(p=>p.name),levelBand:[band(c)],realm:[c.realm||'Unknown'],tag:tags(c),region:[c.roster?.realmRegion||'Unknown']};
  for(const [key,items]of Object.entries(values))for(const name of new Set(items as string[]))if(name)result[key][name]=(result[key][name]??0)+1;
 }
 return result;
}

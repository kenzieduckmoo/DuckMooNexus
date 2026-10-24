/* One requested-count evaluator for product choices and concentration batches. */
const batchDaily=typeof module!=='undefined'?require('./daily-plan.js'):{evaluateDailyPlan,poolKey};
const CHARACTER_ORDER=['Rolla','Stormlesbian','Hammeredchic','Stabbiechick','Kenziemoo','Pandaquack','Fearfulchick','Pandachicken','Kaidiellicia','Meepkin','Bloodchicken','Voidchicken','Kaissiriah','Zaraevelina','Trunktix','Darayeda','Kyootchick','Risharika','Duckmoochick'];
function characterCompare(a,b){const rank=c=>{const i=CHARACTER_ORDER.indexOf(c.name);return i<0?1000:i;};return rank(a)-rank(b)||a.name.localeCompare(b.name)||a.realm.localeCompare(b.realm);}
function recipeIdentity(setup){return Number(setup.recipeKey.match(/^(?:c|r):(\d+)/)?.[1]);}
const availabilityIndexes=new WeakMap();
function availability(snapshot,entry,existing=[],now=Date.now()/1000){
 let index=availabilityIndexes.get(snapshot);if(!index){index=new Map();for(const r of snapshot.catalog||[]){const k=r.guid+'|'+r.recipeID,old=index.get(k);if(!old||r.observedAt>old.observedAt)index.set(k,r);}availabilityIndexes.set(snapshot,index);}
 const id=recipeIdentity(entry.setup),guid=entry.recipe?.crafters.find(c=>c.name===entry.setup.crafterName&&c.realm===entry.setup.realm)?.guid;
 const r=index.get(guid+'|'+id);
 if(!r||r.learned!==true)return {limit:0,wait:null,reason:'This character needs a learned-recipe capture.'};
 if(r.disabled)return {limit:0,wait:null,reason:r.disabledReason||'The captured recipe is unavailable.'};
 const cd=r.cooldown;
 if(!r.cooldownCaptured||!cd||!Number.isFinite(cd.observedAt)||cd.observedAt>now+300||now-cd.observedAt>86400*3||!Number.isFinite(cd.seconds)||cd.seconds<0)
  return {limit:0,wait:null,reason:'Open the profession to refresh recipe availability.'};
 const queued=[...existing,...(snapshot.pendingCompleted||[]).filter(s=>s.completedAt>=cd.observedAt)].filter(s=>batchDaily.poolKey(s)===batchDaily.poolKey(entry.setup)&&recipeIdentity(s)===id).reduce((n,s)=>n+s.count,0);
 const wait=Math.max(0,cd.observedAt+cd.seconds-now);
 let limit=10000;
 if(cd.maxCharges>0)limit=Math.min(cd.maxCharges,Math.max(0,Math.floor(cd.charges||0))+(cd.seconds>0&&wait===0?1:0));
 else if(cd.seconds>0)limit=wait===0?1:0;
 else if(cd.isDay)limit=1;
 if(limit<10000)limit=Math.max(0,limit-queued);
 return {limit,wait:limit?0:wait>0?wait:null,reason:limit?null:wait>0?'Recipe is on cooldown.':'Available recipe uses are already reserved.'};
}
function evaluateBatch(snapshot,entry,count,existing=[],now=Date.now()/1000){
 if(!Number.isInteger(count)||count<1||count>10000)throw Error('Enter a whole number of crafts from 1 to 10,000.');
 const state=availability(snapshot,entry,existing,now),issues=[];
 if(state.limit<count)issues.push(state.reason||'The requested batch exceeds known recipe charges.');
 const plan=batchDaily.evaluateDailyPlan(snapshot,[...existing,{...entry.setup,count}],now),line=plan.lines.at(-1);
 // Other saved lines keep their own warnings and resource reservations. They
 // must not veto an otherwise valid craft on an unrelated character.
 if(line?.result.error)issues.push(line.result.error);
 if(line?.result.plan?.unresolved?.length)issues.push('The requested craft has incomplete reagent choices.');
 if(entry.setup.concentration>0){const pool=plan.pools.find(p=>p.key===batchDaily.poolKey(entry.setup));if(pool?.available==null)issues.push('Concentration availability unknown');else if(pool.required>pool.available)issues.push(pool.name+': needs '+Math.ceil(pool.required-pool.available)+' more concentration');}
 if(line?.result.finance?.profit==null)issues.push('A sale or material price is missing.');
 return {entry,count,plan,rows:line?.reservedRows||[],profit:line?.result.finance?.profit??null,
  materialCost:line?.result.plan?.materialCost??null,buy:(line?.reservedRows||[]).some(r=>r.missing>0&&!r.price)?null:
    (line?.reservedRows||[]).reduce((n,r)=>n+r.missing*(r.price?.price||0),0),
  output:entry.setup.quantity*count,spent:entry.setup.concentration*count,issues:[...new Set(issues)],
  feasible:issues.length===0,availability:state};
}
function bestProductBatch(snapshot,entries,count,mode,quality,existing=[],now=Date.now()/1000){
 const candidates=entries.filter(e=>(mode==='with'?e.setup.concentration>0:e.setup.concentration===0)&&(!quality||String(e.recipe?.capture?.quality)===String(quality)));
 const evaluated=candidates.map(e=>evaluateBatch(snapshot,e,count,existing,now));
 evaluated.sort((a,b)=>Number(b.feasible)-Number(a.feasible)||(b.profit??-Infinity)-(a.profit??-Infinity)||(a.buy??Infinity)-(b.buy??Infinity)||a.entry.setup.crafterName.localeCompare(b.entry.setup.crafterName));
 return {best:evaluated.find(e=>e.feasible)||null,alternatives:evaluated,mode,count};
}
function productGroups(recipes){
 const groups=new Map();
 for(const recipe of recipes){
  if(/Cooking|Fishing|Archaeology|First Aid/i.test(recipe.profession||''))continue;
  const key=(recipe.name||recipe.output).toLocaleLowerCase()+'|'+(recipe.profession||'').toLocaleLowerCase();
  const group=groups.get(key)||{key,name:recipe.name,profession:recipe.profession,recipes:[],keys:new Set()};
  group.recipes.push(recipe);group.keys.add(recipe.key);groups.set(key,group);
 }
 return [...groups.values()].sort((a,b)=>(a.name||'').localeCompare(b.name||''));
}
if(typeof module!=='undefined')module.exports={CHARACTER_ORDER,characterCompare,recipeIdentity,availability,evaluateBatch,bestProductBatch,productGroups};

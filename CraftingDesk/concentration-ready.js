const readyProfit=typeof module!=='undefined'?require('./profit-ui.js'):{concentrationBudget};
const readyDaily=typeof module!=='undefined'?require('./daily-plan.js'):{filterDaily,poolKey,evaluateDailyPlan};
function readyBatch(entry,available,limit=10000){
 const cost=entry.setup.concentration,profit=entry.result.finance?.perCraft;
 if(!Number.isFinite(cost)||cost<=0||!Number.isFinite(profit)||profit<=0||!Number.isFinite(available)||available<0)return null;
 const count=Math.min(10000,Math.max(0,Math.floor(limit)),Math.floor(available/cost));
 return count>0?{entry,count,profit:count*profit,spent:count*cost,left:available-count*cost}:null;
}
const readyShared=typeof module!=='undefined'?require('./batch-evaluation.js'):{availability,evaluateBatch,characterCompare};
function concentrationReady(snapshot,entries,options={},existing=[],now=Date.now()/1000){
 const current=readyDaily.evaluateDailyPlan(snapshot,existing,now),reserved=new Map(current.pools.map(p=>[p.key,p.required]));
 const eligible=readyDaily.filterDaily(entries,{...options,owner:'',profession:'',search:'',mode:'with',positive:true,ready:false},now);
 const byPool=new Map();for(const e of eligible){const key=readyDaily.poolKey(e.setup);if(!byPool.has(key))byPool.set(key,[]);byPool.get(key).push(e);}
 const allByPool=new Map();for(const e of entries)if(e.setup.concentration>0){const key=readyDaily.poolKey(e.setup);if(!allByPool.has(key))allByPool.set(key,[]);allByPool.get(key).push(e);}
 const rows=[];
 for(const c of snapshot.characters||[])for(const p of c.professions||[]){
  if(options.expansion!=='all'&&!p.name?.startsWith('Midnight '))continue;
  if(/Cooking|Fishing|Archaeology|First Aid/i.test(p.name||''))continue;
  const record=p.concentration;if(!record||!(record.max>0)||record.observedAt>now+300)continue;
  const budget=readyProfit.concentrationBudget(record,1,1,now);if(!budget)continue;
  const key=(c.name+'-'+c.realm).replaceAll(' ','').toLowerCase()+'|'+p.id;
  const available=Math.max(0,Math.floor(budget.available-(reserved.get(key)||0))),reasons=new Set(),batches=[],waits=[];
  for(const e of byPool.get(key)||[]){
   if(e.result.error||e.result.plan?.unresolved?.length)continue;
   const state=readyShared.availability(snapshot,e,existing,now),cost=e.setup.concentration;
   const need=Math.max(0,cost-available),conWait=need===0?0:cost<=record.max-(reserved.get(key)||0)&&record.secondsPerPoint>0?need*record.secondsPerPoint:null;
   if(state.limit===0||need>0){
    if(state.reason)reasons.add(state.reason);
    if(need>0)reasons.add('Needs '+Math.ceil(need)+' more concentration for an eligible craft.');
    if(conWait!=null&&(state.limit>0||state.wait!=null))waits.push(Math.max(conWait,state.wait||0));
    continue;
   }
   let raw=readyBatch(e,available,state.limit);if(!raw)continue;
   if(options.stockOnly){
    let lo=0,hi=raw.count;
    while(lo<hi){const mid=Math.ceil((lo+hi)/2),checked=readyShared.evaluateBatch(snapshot,e,mid,existing,now);if(checked.feasible&&!checked.rows.some(r=>r.missing>0))lo=mid;else hi=mid-1;}
    raw=readyBatch(e,available,lo);
    if(!raw){reasons.add('Owned materials are already reserved or insufficient.');continue;}
   }
   const batch=readyShared.evaluateBatch(snapshot,e,raw.count,existing,now);
   if(!batch.feasible){for(const issue of batch.issues)reasons.add(issue);continue;}
   batch.left=available-batch.spent;batches.push(batch);
  }
  batches.sort((a,b)=>b.profit-a.profit||a.spent-b.spent||a.entry.setup.name.localeCompare(b.entry.setup.name));
  if(!byPool.get(key)?.length){
   const raw=allByPool.get(key)||[];
   if(!raw.length)reasons.add('No captured concentration outcomes for this profession. Open it in-game, save, then refresh Nexus.');
   else{
    const old=raw.filter(e=>options.maxAge&&(!Number.isFinite(e.observedAt)||now-e.observedAt>options.maxAge*3600)).length;
    const missing=raw.filter(e=>e.result.finance?.profit==null).length;
    const loss=raw.filter(e=>e.result.finance?.profit!=null&&e.result.finance.profit<=0).length;
    const margin=raw.filter(e=>options.minMargin>0&&!(e.margin>=options.minMargin)).length;
    const sale=raw.filter(e=>options.minSaleRate>0&&!(e.sales?.saleRate>=options.minSaleRate)).length;
    const sold=raw.filter(e=>options.minDailySold>0&&!(e.sales?.dailySold>=options.minDailySold)).length;
    if(old)reasons.add(old+' choices exceed the '+options.maxAge+'-hour capture filter.');
    if(missing)reasons.add(missing+' choices need sale or material prices.');
    if(loss)reasons.add(loss+' choices currently lose gold.');
    if(margin)reasons.add(margin+' choices fail the minimum margin.');
    if(sale)reasons.add(sale+' choices fail the sale-rate filter or lack sales data.');
    if(sold)reasons.add(sold+' choices fail the regional daily-sold filter or lack sales data.');
   }
  }
  rows.push({character:c,profession:p,available,cap:record.max,reserved:reserved.get(key)||0,observedAt:record.observedAt,
   projected:record.amount<record.max,best:batches[0]||null,alternatives:batches.slice(1,4),reasons:[...reasons],
   readyAt:!batches.length&&waits.length?now+Math.min(...waits):null,
   reason:reasons.size?[...reasons].join(' '):'No captured craft passes the profit, sale-rate and age filters.'});
 }
 return rows.sort((a,b)=>readyShared.characterCompare(a.character,b.character)||a.profession.name.localeCompare(b.profession.name));
}
if(typeof module!=='undefined')module.exports={readyBatch,concentrationReady};

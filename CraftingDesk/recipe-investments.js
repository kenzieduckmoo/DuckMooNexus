const investmentMath=typeof module!=='undefined'?require('./daily-plan.js'):{dailyCandidates};
const investmentCache=new WeakMap();
function investmentQualifies(e,now){return !e.result.error&&e.margin>20&&e.sales?.saleRate>0.1&&e.result.finance?.profit>0&&e.setup.quantity>0&&now-e.observedAt<=86400&&e.observedAt<=now+300;}
function investmentRecovery(price,profit,quantity){return price>=0&&profit>0&&quantity>0?Math.ceil(price/(profit/quantity)):null;}
function recipeInvestments(snapshot,profession,now=Date.now()/1000,learner=null){
 const clean=s=>String(s||'').replace(/^(recipe|pattern|plans|schematic|design|formula|technique):\s*/i,'').toLowerCase().replace(/[^a-z0-9]/g,'');
 const items=new Map();for(const [item,name]of Object.entries(snapshot.inventory?.names||{}))if(/^(recipe|pattern|plans|schematic|design|formula|technique):\s*/i.test(name)){const key=clean(name);if(!items.has(key))items.set(key,[]);items.get(key).push({item,name});}
 let cache=investmentCache.get(snapshot);if(!cache||now-cache.at>60){cache={at:now,entries:investmentMath.dailyCandidates(snapshot,[],5,now)};investmentCache.set(snapshot,cache);}
 const candidates=cache.entries.filter(e=>e.profession===profession&&investmentQualifies(e,now));
 const best=new Map();for(const e of candidates){const key=JSON.stringify([e.setup.crafterName,e.setup.realm,clean(e.recipe.name),e.setup.concentration>0]);if(!best.has(key)||e.result.finance.profit>best.get(key).result.finance.profit)best.set(key,e);}
 const rows=[];
 for(const e of best.values()){
   const target=learner?(snapshot.catalog||[]).filter(r=>r.guid===learner.guid&&clean(r.name)===clean(e.recipe.name)&&r.profession?.parentProfessionName===profession).sort((a,b)=>b.observedAt-a.observedAt)[0]:null;
   if(target?.learned===true)continue;
   const matches=items.get(clean(e.recipe.name))||[];if(matches.length!==1)continue;
   const item=matches[0],price=(typeof quote==='function'?quote:require('./material-ui.js').quote)(snapshot.market,item.item,learner?.realm||e.setup.realm);
   const vendors=(snapshot.acquisitionOffers||[]).filter(o=>o.kind==='vendor'&&'i:'+o.itemID===item.item&&now-o.observedAt<=7*86400&&o.observedAt<=now+300&&o.isPurchasable===true&&o.numAvailable!==0&&o.stackCount>0&&Number.isFinite(o.price)&&o.price>=0&&(o.hasExtendedCost===false||o.costsComplete===true));
   if(!price&&!vendors.length)continue;
   const perItem=e.result.finance.profit/e.setup.quantity;
   rows.push({entry:e,item,price,vendors,learner,learningKnown:target?.learned===false,profitPerItem:perItem,salesToRecover:price?investmentRecovery(price.price,e.result.finance.profit,e.setup.quantity):null});
 }
 return rows.sort((a,b)=>(a.salesToRecover??Infinity)-(b.salesToRecover??Infinity)||b.entry.result.finance.profit-a.entry.result.finance.profit);
}
if(typeof module!=='undefined')module.exports={recipeInvestments,investmentQualifies,investmentRecovery};

function acquisitionStatus(offer,now=Date.now()/1000){
  if(!Number.isFinite(offer.observedAt)||now-offer.observedAt>86400||offer.observedAt>now+300)return 'Older observation — revisit to check';
  if(offer.kind==='trainer'){
    if(offer.status==='used')return 'Already trained at visit';
    if(offer.status==='unavailable'||offer.hasSkill===false||(offer.requirements||[]).some(r=>r.met===false))return 'Requirements unmet at visit';
    if(offer.status==='available'){
      if(offer.isProfession)return 'Profession training — check available profession slots';
      if(!Number.isFinite(offer.price)||!Number.isFinite(offer.money))return 'Listed by trainer — cost or funds unknown';
      return offer.money>=offer.price?'Trainer listed available; gold covered at visit':'Trainer listed available; short on gold at visit';
    }
  }else{
    if(offer.numAvailable===0)return 'Out of stock at visit';
    if(offer.isPurchasable===false)return 'Purchase restricted at visit';
    if(offer.canAfford===false)return 'Insufficient payment at visit';
    if(offer.isPurchasable===true&&offer.canAfford===true)return 'Purchasable at visit — learning requirements still need checking';
  }
  return 'Availability not confirmed';
}
function recipeOffers(snapshot,record){
  return (snapshot.acquisitionOffers||[]).filter(o=>offerRecipeMatch(snapshot,o,record));
}
const acquisitionCatalogIndexes=new WeakMap();
function offerRecipeMatch(snapshot,offer,record){
  if(offer.guid!==record.guid)return null;
  if(Number.isInteger(offer.recipeID))return offer.recipeID===record.recipeID?'Exact recipe ID':null;
  if(offer.kind!=='trainer'||offer.isProfession)return null;
  const item=Number(offer.link?.match(/(?:^|\|H)item:(\d+)/)?.[1]);
  if(!item||!offer.skill||!offer.name)return null;
  let index=acquisitionCatalogIndexes.get(snapshot);
  if(!index){
    index=new Map();
    for(const r of snapshot.catalog||[]){const key=JSON.stringify([r.guid,r.schematic?.outputItemID,r.name,r.profession?.professionName]);if(!index.has(key))index.set(key,new Set());index.get(key).add(r.recipeID);}
    acquisitionCatalogIndexes.set(snapshot,index);
  }
  const ids=index.get(JSON.stringify([offer.guid,item,offer.name,offer.skill]));
  return ids?.size===1&&ids.has(record.recipeID)?'Unique output item + name + profession match':null;
}
const learningMath=typeof module!=='undefined'?require('./leveling-plan.js'):{levelingGuide,levelingRoadmap};
function learningOpportunities(snapshot,guide,now=Date.now()/1000){
  if(!guide.character||!Number.isInteger(guide.skill)||guide.skill>=guide.target)return [];
  // Evaluate the unlearned schematics as conditional estimates, without changing ownership.
  const preview={...snapshot,catalog:(snapshot.catalog||[]).map(r=>r.guid===guide.character.guid&&r.learned===false?{...r,learned:true}:r)};
  const estimates=learningMath.levelingGuide(preview,guide.character.guid,guide.professionID,guide.target,now);
  const byID=new Map(estimates.choices.map(c=>[c.record.recipeID,c]));
  return guide.locked.map(record=>{
    const offers=recipeOffers(snapshot,record).filter(o=>o.kind==='trainer').sort((a,b)=>b.observedAt-a.observedAt||(a.price??Infinity)-(b.price??Infinity));
    const offer=offers[0],choice=byID.get(record.recipeID);let reason;
    if(!offer)reason='No matching trainer offer; check the recipe source (it may require a vendor, drop or other unlock)';
    else if(!record.build||offer.build!==record.build)reason='Trainer and profession observations need matching game builds';
    else if(!Number.isFinite(offer.observedAt)||now-offer.observedAt>86400||offer.observedAt>now+300)reason='Revisit the trainer; observation is older than one day or has an invalid time';
    else if(offer.isProfession)reason='Profession training needs a separate slot check';
    else if(offer.status==='used')reason='Trainer says already learned; refresh the profession catalog';
    else if(offer.status!=='available'||offer.hasSkill===false||(offer.requirements||[]).some(r=>r.met===false))reason='Trainer requirements were unmet or availability was not confirmed';
    else if(!Number.isFinite(offer.price)||offer.price<0)reason='Training price is unknown';
    else if(!Number.isFinite(offer.money)||offer.money<offer.price)reason='Training funds were insufficient or unknown at the visit';
    else if(!choice||record.observedAt>now+300)reason='Needs a fresh, supported skill-up schematic and complete reagent prices';
    else if(!choice.guaranteed)reason='Chance-based skill-up; no guaranteed savings comparison';
    else if(!record.cooldownCaptured||record.cooldown?.seconds>0||record.cooldown?.isDay||record.cooldown?.maxCharges>0)reason='Cooldown availability needs checking';
    const ready=!reason;
    let baseline=null;
    if(ready){const route=learningMath.levelingRoadmap(snapshot,{...guide,target:guide.skill+choice.points},now);if(route.complete)baseline=route.materialCost;}
    const total=ready?offer.price+choice.plan.materialCost:null;
    return {record,offer,match:offer&&offerRecipeMatch(snapshot,offer,record),choice,ready,reason,
      total,baseline,savings:baseline===null?null:baseline-total,
      buyCost:ready?offer.price+choice.plan.buyCost:null};
  }).sort((a,b)=>Number(b.ready)-Number(a.ready)||(b.savings??-Infinity)-(a.savings??-Infinity)||(a.total??Infinity)-(b.total??Infinity)||a.record.name.localeCompare(b.record.name));
}
function learningChecklist(guide,option,names={},tiers={}){
  if(!option.ready)return option.reason;
  return [`${guide.character.name}: investigate learning ${option.record.name}`,
    `Visit ${option.offer.npcName||'the recorded trainer'}${option.offer.mapID?' (map '+option.offer.mapID+')':''}. Training price: ${option.offer.price/10000} g.`,
    `Association: ${option.match}. Confirm the recipe and requirements in-game before paying.`,
    'After learning: open the profession, save and import again to confirm the craft and update the route.',
    `Conditional first craft: up to ${option.choice.points} skill points. Training + material value: ${option.total/10000} g; training + missing purchases: ${option.buyCost/10000} g.`,
    ...option.choice.plan.rows.map(r=>`${r.needed} x ${names[r.item]||r.item}${tiers[r.item]?' · Quality '+tiers[r.item]:''}; buy missing ${r.missing}`),
    option.savings===null?'No complete learned-recipe comparison for the same skill gain.':`Difference versus supported learned route to the same skill: ${option.savings/10000} g saved (negative means more expensive).`,
    'Separate alternative, not added to your crafting plan. Costs exclude travel and resale. Prices and availability are saved observations.'].join('\n');
}
if(typeof module!=='undefined')module.exports={acquisitionStatus,recipeOffers,offerRecipeMatch,learningOpportunities,learningChecklist};

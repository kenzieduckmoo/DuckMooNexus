/* Skill-up advice uses observations at the character's recorded rank only. */
const levelingMath=typeof module!=='undefined'?require('./material-ui.js'):{quote,materialPlan};
function levelingGuide(snapshot,guid,professionID,target=100,now=Date.now()/1000){
  const character=(snapshot.characters||[]).find(c=>c.guid===guid);
  const catalog=(snapshot.catalog||[]).filter(r=>r.guid===guid&&r.profession?.professionID===Number(professionID));
  const roster=character?.professions?.find(p=>p.id===Number(professionID));
  const newest=[...catalog].sort((a,b)=>b.observedAt-a.observedAt)[0];
  const useCatalog=newest&&(!roster||newest.observedAt>roster.seenAt);
  const skill=useCatalog?newest.profession.skillLevel:roster?.rank;
  const cap=useCatalog?newest.profession.maxSkillLevel:roster?.max;
  const result={character,professionID:Number(professionID),skill,cap,target:Math.min(Number(target),cap||100),choices:[],locked:[],excluded:{},catalogCount:catalog.length};
  const skip=reason=>result.excluded[reason]=(result.excluded[reason]||0)+1;
  if(!Number.isInteger(skill)||skill<1){result.message='Open this profession in-game, then save and import to capture its current skill.';return result;}
  if(!Number.isInteger(result.target)||result.target<1){result.message='Enter a whole-number target skill.';return result;}
  if(skill>=result.target){result.message='Target reached at the recorded skill.';return result;}
  for(const r of catalog){
    if(!r.learned){result.locked.push(r);continue;}
    if(r.disabled){skip('Disabled recipes');continue;}
    if(r.profession.skillLevel!==skill||!r.observedAt||now-r.observedAt>86400){skip('Needs a fresh observation at current skill');continue;}
    if(!r.canSkillUp||r.relativeDifficulty===3){skip('No recorded skill-up');continue;}
    if(![0,1,2].includes(r.relativeDifficulty)||!Number.isInteger(r.numSkillUps)||r.numSkillUps<1){skip('Missing skill-up details');continue;}
    const schema=r.schematic;
    if(!schema||schema.isRecraft||schema.recipeType!==1||schema.quantityMin!==schema.quantityMax){skip('Unsupported or missing reagent schematic');continue;}
    const cooldown=r.cooldown;
    if(cooldown?.seconds>0&&!(cooldown.charges>0)){skip('Recorded cooldown; refresh in-game');continue;}
    const materials={},selections={};let invalid=false;
    for(const slot of Object.values(schema.reagentSlotSchematics||{})){
      if(!slot.required)continue;
      if(!Number.isInteger(slot.quantityRequired)||slot.quantityRequired<1){invalid=true;break;}
      const options=Object.values(slot.reagents||{});
      if(!options.length||options.some(o=>!o.itemID||o.currencyID)||options.length>1&&slot.dataSlotType!==2){invalid=true;break;}
      const priced=options.map(o=>({item:'i:'+o.itemID,price:levelingMath.quote(snapshot.market,'i:'+o.itemID,character.realm)})).filter(o=>o.price&&Number.isFinite(o.price.price)&&o.price.price>=0).sort((a,b)=>a.price.price-b.price.price||a.item.localeCompare(b.item));
      // An unknown alternative could be cheaper: never call that a complete comparison.
      if(priced.length!==options.length){invalid=true;break;}
      const item=priced[0].item;materials[item]=(materials[item]||0)+slot.quantityRequired;selections[item]=item;
    }
    if(invalid||!Object.keys(materials).length){skip('Missing reagent prices or unsupported costs');continue;}
    const plan=levelingMath.materialPlan({materials},selections,1,{name:character.name,realm:character.realm},snapshot.inventory||{},snapshot.market||{});
    const points=Math.min(r.numSkillUps,result.target-skill);
    result.choices.push({record:r,plan,points,guaranteed:r.relativeDifficulty===0,costPerPoint:plan.materialCost/points,materials,selections});
  }
  result.choices.sort((a,b)=>Number(b.guaranteed)-Number(a.guaranteed)||a.costPerPoint-b.costPerPoint||a.record.name.localeCompare(b.record.name));
  result.message=result.choices.length?'Craft one batch, check your skill, then save and import to update the next step.':'No supported skill-up craft is ready to recommend. Refresh the profession catalog or inspect the missing-data reasons below.';
  return result;
}
function levelingText(guide,choice,names={},tiers={}){
  if(!choice)return guide.message;
  const label=item=>(names[item]||item)+(tiers[item]?' · Quality '+tiers[item]:'');
  return [`${guide.character.name} — skill ${guide.skill} toward ${guide.target}`,`Next step: 1 craft of ${choice.record.name}`,`${choice.guaranteed?'Recorded orange recipe':'Chance-based skill-up'}: up to ${choice.points} points. Recheck skill after crafting.`,
    'Reagents for one craft:',...choice.plan.rows.map(r=>`${r.needed} x ${label(r.item)}; buy missing ${r.missing}`),
    'No concentration required by this material plan. Output quality and sale proceeds are not predicted.',
    'This is the next supported step, not a guaranteed complete route to the target.'].join('\n');
}
if(typeof module!=='undefined')module.exports={levelingGuide,levelingText};
/* Routes stop at the first unsupported skill range; no yellow/green odds invented. */
function levelingRoadmap(snapshot,guide,now=Date.now()/1000){
  const start=guide.skill,target=guide.target;
  const empty={steps:[],start,reached:start,target,complete:start>=target,materialCost:0,buyCost:0,shopping:[]};
  if(!Number.isInteger(start)||!Number.isInteger(target)||target<=start)return empty;
  const choices=guide.choices.filter(c=>c.guaranteed&&!c.record.cooldown?.isDay&&!(c.record.cooldown?.maxCharges>0)&&!(c.record.cooldown?.seconds>0));
  const available=choices.map(choice=>{
    const r=choice.record;
    const evidence=[{rank:start,points:r.numSkillUps,character:r.character}];
    // Cross-character observations require matching build, profession and modifiers.
    if(r.build)for(const other of snapshot.catalog||[]){
      if(other.recipeID!==r.recipeID||other.profession?.professionID!==r.profession.professionID||other.build!==r.build||other.profession?.skillModifier!==r.profession.skillModifier)continue;
      const samples={...(other.skillHistory||{})};
      samples[other.profession.skillLevel]={difficulty:other.relativeDifficulty,numSkillUps:other.numSkillUps,canSkillUp:other.canSkillUp,observedAt:other.observedAt,skillModifier:other.profession.skillModifier};
      for(const [rank,s]of Object.entries(samples))if(Number.isInteger(Number(rank))&&Number(rank)>=start&&Number(rank)<=1000&&s.difficulty===0&&s.canSkillUp&&Number.isInteger(s.numSkillUps)&&s.numSkillUps>0&&s.skillModifier===r.profession.skillModifier&&Number.isFinite(s.observedAt)&&now-s.observedAt<=7*86400)evidence.push({rank:Number(rank),points:s.numSkillUps,character:other.character});
    }
    return {choice,evidence};
  });
  const best=new Map([[start,{cost:0,steps:[]}]]);
  for(let skill=start;skill<target;skill++){
    const prior=best.get(skill);if(!prior)continue;
    for(const {choice,evidence}of available){
      const covering=evidence.filter(e=>e.rank>=skill);if(!covering.length)continue;
      // Orange at a higher observed rank bounds a usable range, not its exact end.
      const points=Math.min(...covering.map(e=>e.points)),next=Math.min(target,skill+points);
      const cost=prior.cost+choice.plan.materialCost;
      if(!best.has(next)||cost<best.get(next).cost)best.set(next,{cost,steps:[...prior.steps,{choice,from:skill,to:next,reference:covering.sort((a,b)=>a.rank-b.rank)[0]}]});
    }
  }
  const reached=Math.max(...best.keys()),path=best.get(reached),materials={};
  for(const step of path.steps)for(const [item,n]of Object.entries(step.choice.materials))materials[item]=(materials[item]||0)+n;
  const plan=levelingMath.materialPlan({materials},Object.fromEntries(Object.keys(materials).map(i=>[i,i])),1,{name:guide.character.name,realm:guide.character.realm},snapshot.inventory||{},snapshot.market||{});
  return {...empty,reached,complete:reached>=target,steps:path.steps,materialCost:path.cost,buyCost:plan.buyCost,shopping:plan.rows.map(r=>({...r,scope:r.price?.scope||guide.character.realm}))};
}
function levelingRoadmapText(guide,route,names={},tiers={}){
  const label=i=>(names[i]||i)+(tiers[i]?' · Quality '+tiers[i]:'');
  return [`${guide.character.name}: supported route ${route.start} → ${route.reached} (target ${route.target})`,
    'Estimated route within recorded orange skill ranges. Verify skill and recipe color after each step; cross-character evidence is a planning assumption.',
    ...route.steps.map((s,i)=>`${i+1}. Skill ${s.from} → ${s.to}: 1 craft of ${s.choice.record.name} (orange observed at ${s.reference.rank} on ${s.reference.character})`),
    ...(route.complete?[]:[`STOP at ${route.reached}: no supported orange continuation. Refresh observations or investigate additional recipes. Chance-based alternatives are not included.`]),
    'Combined reagents:',...route.shopping.map(r=>`${r.needed} x ${label(r.item)}; buy missing ${r.missing}`),
    'Stock allocated once within this route; separate from your daily plan. Training, unlocks and resale are excluded.'].join('\n');
}
if(typeof module!=='undefined')Object.assign(module.exports,{levelingRoadmap,levelingRoadmapText});

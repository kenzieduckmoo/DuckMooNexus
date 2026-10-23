// Guide sequence + captured schematics; quantities remain estimates for yellow/green skill-ups.
const tailoringHelpers=typeof module!=='undefined'?require('./guide-planner.js'):{guideIndex,guideNorm,guideItem,guideRecipe,guideTrainerRecipes};
const tailoringMath=typeof module!=='undefined'?require('./material-ui.js'):{materialPlan,quote};
function tailoringSkill(character){return character.professions?.find(p=>p.name==='Midnight Tailoring')?.rank??null;}
function tailoringUnlock(data,c,name){
 const h=tailoringHelpers,records=(data.catalog||[]).filter(r=>h.guideNorm(r.name)===h.guideNorm(name)&&r.profession?.professionName==='Midnight Tailoring');
 const own=records.filter(r=>r.guid===c.guid).sort((a,b)=>b.observedAt-a.observedAt)[0];
 if(own?.learned)return {gold:0,text:'Already learned'};
 const matches=(h.guideIndex(data).get(h.guideNorm('Pattern: '+name))||[]).map(id=>[id,data.inventory.names[id]]);
 if(name.startsWith('Elegant Artisan'))return {gold:0,currency:150,text:"Buy from the Tailoring supply vendor: 150 Artisan Tailor’s Moxie. Confirm access before shopping."};
 if(matches.length===1){const item=h.guideItem(data,c,matches[0][1]);const own=tailoringMath.materialPlan({materials:{[item.item]:1}},{[item.item]:item.item},1,c,data.inventory||{},data.market||{}).rows[0].own;return {gold:own>=1?0:item.price?.price??null,item:{...item,own},text:'Buy '+matches[0][1]+' on the AH; confirm the recipe before buying.'};}
 const record=own||records[0],source=record?.sourceText||'';
 if(source.includes('Profession Trainer:')){
  let gold=0,found=false;for(const [kind,mult]of [['GOLD',10000],['SILVER',100],['COPPER',1]]){const match=source.match(new RegExp('(\\d+)\\|T[^|]*UI-'+kind+'ICON','i'));if(match){gold+=Number(match[1])*mult;found=true;}}
  return {gold:found?gold:null,text:'Learn from Galana when available'+(found?' (captured tooltip price; discounts may differ).':'.')};
 }
 return {gold:null,text:'Confirm training/unlock cost in game.'};
}
function tailoringRoute(data,c,options={}){
 const h=tailoringHelpers,g={name:'Tailoring',early:35},skill=Math.max(1,Math.min(100,Number(options.skill??tailoringSkill(c)??1))),steps=[],issues=[];
 const add=(from,to,name,count,fixed=false)=>{if(skill>=to)return;steps.push({id:from+':'+name,from:Math.max(from,skill),to,name,count:fixed?count:Math.max(1,Math.ceil(count*(to-Math.max(from,skill))/(to-from))),fixed});};
 add(1,25,'Bright Linen Bolt',66,true);add(25,40,'Imbued Bright Linen Bolt',14);
 if(skill<45){const trainers=h.guideTrainerRecipes(data,c,g).filter(r=>r.name!=='Imbued Bright Linen Bolt');if(!trainers.length)issues.push('Trainer first-craft catalog is missing for skill 40–45');for(const r of trainers)add(40,45,r.name,1,true);}
 add(45,50,'Courtly Shoulders',6);add(50,65,'Bright Linen Spellthread',30);
 const liningCount=skill>=90?0:Math.max(1,Math.ceil(28*(90-Math.max(65,skill))/25));
 const choices=['Arcanoweave Lining','Sunfire Silk Lining'].map(name=>{const plan=h.guideRecipe(data,c,g,name,liningCount),unlock=tailoringUnlock(data,c,name);return {name,plan,unlock,cost:plan.error||unlock.gold===null?null:plan.total+unlock.gold};});
 const alternatives=typeof module!=='undefined'?require('./profession-route.js').routeAlternatives:routeAlternatives;
 if(skill>=65&&skill<90&&skill===tailoringSkill(c))for(const alt of alternatives(data,c,g,choices.map(x=>x.name),skill,90)){const plan=h.guideRecipe(data,c,g,alt.name,liningCount),unlock=tailoringUnlock(data,c,alt.name);if(!plan.error&&plan.total>0)choices.push({...alt,name:alt.name,plan,unlock,cost:plan.total,alternative:true});}
 const ranked=[...choices].sort((a,b)=>(a.cost??Infinity)-(b.cost??Infinity));
 const selected=options.lining?choices.find(x=>x.name===options.lining):ranked[0];
 const chosen=selected||ranked[0];add(65,90,chosen.name,28);
 const gearCount=skill>=100?0:Math.max(1,Math.ceil(13*(100-Math.max(90,skill))/10));
 const gearNames=[...new Set((data.catalog||[]).filter(r=>r.profession?.professionName==='Midnight Tailoring'&&r.name.startsWith("Elegant Artisan's ")&&r.maxTrivialLevel>=100&&r.sourceText?.includes('150|Hcurrency:3266')).map(r=>r.name))];
 if(!gearNames.includes("Elegant Artisan's Cooking Hat"))gearNames.push("Elegant Artisan's Cooking Hat");
 const gearChoices=gearNames.map(name=>{const plan=h.guideRecipe(data,c,g,name,gearCount),unlock=tailoringUnlock(data,c,name);return {name,plan,unlock,cost:plan.error||unlock.gold===null?null:plan.total+unlock.gold};}).sort((a,b)=>(a.unlock.currency||0)-(b.unlock.currency||0)||(a.cost??Infinity)-(b.cost??Infinity));
 const gear=(options.gear&&gearChoices.find(x=>x.name===options.gear))||gearChoices.find(x=>x.cost!==null)||gearChoices[0];
 add(90,100,gear.name,13);
 const demand=new Map(),produced=new Map(),unlocks=new Map();
 for(const step of steps){
  const records=(data.catalog||[]).filter(r=>h.guideNorm(r.name)===h.guideNorm(step.name)&&r.profession?.professionName==='Midnight Tailoring'&&r.schematic&&!r.schematic.isRecraft).sort((a,b)=>Number(b.guid===c.guid)-Number(a.guid===c.guid)||b.observedAt-a.observedAt);
  const r=records[0];step.unlock=tailoringUnlock(data,c,step.name);unlocks.set(step.name,step.unlock);
  if(!r){issues.push('Missing recipe details: '+step.name);continue;}
  step.materials=[];
  for(const slot of Object.values(r.schematic.reagentSlotSchematics||{})){
   if(!slot.required)continue;
   const reagents=Object.values(slot.reagents||{});
   if(!reagents.length||reagents.some(x=>!x.itemID)||!(slot.quantityRequired>0)){issues.push('Unsupported requirement: '+step.name);continue;}
   const candidates=reagents.map(x=>{const item='i:'+x.itemID,name=data.inventory?.names?.[item]||item;return {item,name,tier:data.inventory?.tiers?.[item],...((()=>{const found=h.guideItem(data,c,name);return {price:found.item===item?found.price:tailoringMath.quote(data.market,item,c.realm)};})())};});
   // Generated intermediate quality is unknown, but every offered quality in this slot is accepted.
   const generated=candidates.find(x=>(produced.get(h.guideNorm(x.name))||0)>0&&(h.guideIndex(data).get(h.guideNorm(x.name))||[]).every(id=>candidates.some(candidate=>candidate.item===id)));
   const best=[...candidates].sort((a,b)=>(a.price?.price??Infinity)-(b.price?.price??Infinity))[0];
   let needed=slot.quantityRequired*step.count;step.materials.push({name:best.name,quantity:needed});
   if(generated){const key=h.guideNorm(generated.name),take=Math.min(needed,produced.get(key));needed-=take;produced.set(key,produced.get(key)-take);}
   if(!needed)continue;
   const vendor=['Silverleaf Thread','Embroidery Floss'].includes(best.name),row=demand.get(best.item)||{...best,needed:0,vendor};row.needed+=needed;demand.set(best.item,row);
  }
  if(['Bright Linen Bolt','Imbued Bright Linen Bolt'].includes(step.name)){const n=Number(r.schematic.quantityMin);if(n>0)produced.set(h.guideNorm(step.name),(produced.get(h.guideNorm(step.name))||0)+n*step.count);else issues.push('Missing intermediate yield: '+step.name);}
 }
 const rows=[...demand.values()].map(row=>{const stock=tailoringMath.materialPlan({materials:{[row.item]:row.needed}},{[row.item]:row.item},1,c,data.inventory||{},data.market||{}).rows[0];return {...row,own:stock.own,missing:stock.missing,scope:row.price?.scope||c.realm,price:row.vendor?{...row.price,price:row.price?.source==='vendor'?row.price.price:null,source:'vendor'}:row.price};});
 const goldKnown=[...unlocks.values()].every(x=>x.gold!==null),unlockGold=[...unlocks.values()].reduce((n,x)=>n+(x.gold||0),0);
 const sum=(field)=>!issues.length&&rows.every(r=>!r[field]||Number.isFinite(r.price?.price))?rows.reduce((n,r)=>n+r[field]*(r.price?.price||0),0):null;
 const recipes=[...unlocks].filter(([name,u])=>u.item).map(([name,u])=>({...u.item,needed:1,own:u.item.own||0,missing:Math.max(0,1-(u.item.own||0)),scope:u.item.price?.scope||c.realm}));
 return {skill,steps,rows,choices,gearChoices,gear:gear.name,chosen:chosen.name,issues,unlocks:[...unlocks],unlockGold:goldKnown?unlockGold:null,knownUnlockGold:unlockGold,currency:[...unlocks.values()].reduce((n,u)=>n+(u.currency||0),0),total:sum('needed'),buy:sum('missing'),recipes,complete:!issues.length};
}
if(typeof module!=='undefined')module.exports={tailoringRoute,tailoringSkill,tailoringUnlock};

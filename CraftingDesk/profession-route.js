// Concrete stage plans. Random conversion yields and undiscovered/order recipes are checkpoints.
const routeHelpers=typeof module!=='undefined'?require('./guide-planner.js'):{guideNorm,guideIndex,guideItem,guideRecipe,guideShopping,guideTrainerRecipes};
const routeMath=typeof module!=='undefined'?require('./material-ui.js'):{materialPlan,quote};
function routeSource(text){return String(text||'').replace(/\|T.*?\|t/g,'').replace(/\|H[^|]*\|h(.*?)\|h/g,'$1').replace(/\|c[\da-fA-F]{8}|\|r/g,'').replace(/\|n/g,' · ');}
function routeUnlock(data,c,g,name){
 const h=routeHelpers,records=(data.catalog||[]).filter(r=>h.guideNorm(r.name)===h.guideNorm(name)&&r.profession?.parentProfessionName===g.name&&r.profession?.expansionName==='Midnight').sort((a,b)=>Number(b.guid===c.guid)-Number(a.guid===c.guid)||b.observedAt-a.observedAt),r=records[0];
 if(r?.guid===c.guid&&r.learned)return {gold:0,text:'Already learned',learned:true};
 const source=r?.sourceText||'';
 if(source.includes('Profession Trainer:')){let gold=0,found=false;for(const [kind,mult]of [['GOLD',10000],['SILVER',100],['COPPER',1]]){const m=source.match(new RegExp('(\\d+)\\|T[^|]*UI-'+kind+'ICON','i'));if(m){gold+=Number(m[1])*mult;found=true;}}return {gold:found?gold:null,text:routeSource(source),trainer:true};}
 const matches=Object.entries(data.inventory?.names||{}).filter(([id,n])=>/^(recipe|pattern|plans|schematic|design|formula|technique):\s*/i.test(n)&&h.guideNorm(n.replace(/^[^:]+:\s*/,''))===h.guideNorm(name));
 if(matches.length===1){const [id,n]=matches[0],price=routeMath.quote(data.market,id,c.realm),own=routeMath.materialPlan({materials:{[id]:1}},{[id]:id},1,c,data.inventory||{},data.market||{}).rows[0].own;return {gold:own?0:price?.price??null,text:own?'Recipe item owned; learn it before crafting.':'Acquire '+n+'. '+routeSource(source),item:{item:id,name:n,price,own,needed:1,missing:Math.max(0,1-own),scope:price?.scope||c.realm}};}
 return {gold:null,text:routeSource(source)||'Recipe source has not been captured. Confirm its unlock in game.'};
}
function routeAlternatives(data,c,g,names,skill,target,now=Date.now()/1000){
 const latest=new Map();for(const r of data.catalog||[]){if(r.guid!==c.guid||r.profession?.expansionName!=='Midnight'||r.profession?.parentProfessionName!==g.name)continue;const old=latest.get(r.recipeID);if(!old||r.observedAt>old.observedAt)latest.set(r.recipeID,r);}
 const fresh=r=>r.profession.skillLevel===skill&&Number.isFinite(r.observedAt)&&now-r.observedAt<=86400&&r.observedAt<=now+300;
 const fingerprint=r=>[r.build,r.profession.skillModifier,r.relativeDifficulty,r.numSkillUps,r.maxTrivialLevel,r.schematic?.recipeType].join('|');
 const baselines=[...latest.values()].filter(r=>names.includes(r.name)&&fresh(r)&&r.canSkillUp&&r.numSkillUps>0&&r.relativeDifficulty<3&&r.maxTrivialLevel>=target);
 const fingerprints=new Set(baselines.map(fingerprint));
 return [...latest.values()].filter(r=>!names.includes(r.name)&&fresh(r)&&r.learned===true&&!r.disabled&&r.canSkillUp&&r.numSkillUps>0&&[1,3].includes(r.schematic?.recipeType)&&!r.schematic.isRecraft&&fingerprints.has(fingerprint(r))&&r.cooldownCaptured&&r.cooldown&&r.cooldown.seconds===0&&!r.cooldown.isDay&&!(r.cooldown.maxCharges>0)&&now-r.cooldown.observedAt<=86400&&r.cooldown.observedAt<=now+300).map(r=>({name:r.name,reference:baselines.find(b=>fingerprint(b)===fingerprint(r)).name,observedAt:r.observedAt}));
}
function professionRoute(data,c,g,options={}){
 const h=routeHelpers,imported=c.professions?.find(p=>p.name==='Midnight '+g.name)?.rank??null,skill=Math.max(1,Math.min(100,Number(options.skill??imported??1))),steps=[],issues=[],choices=[];
 function add(from,to,name,count,note='',extra={}){if(skill>=to)return;steps.push({id:from+':'+name+':'+steps.length,from:Math.max(skill,from),to,name,count,note,...extra});}
 function gate(from,to,name,note,requirements){add(from,to,name,null,note,{gate:true,requirements});}
 function trainers(from,to,max,exclude=[]){const list=h.guideTrainerRecipes(data,c,{...g,early:max}).filter(r=>!exclude.includes(r.name));if(!list.length)issues.push('Missing trainer recipe list for '+from+'–'+to);for(const r of list)add(from,to,r.name,1,'Learn at skill '+r.skill+'. '+(r.firstCraft===true?'First-craft bonus recorded as available.':r.firstCraft===false?'No first-craft bonus recorded; craft only if it still grants skill.':'Confirm first-craft bonus and skill gains in game.'),{first:true});}
 function choose(from,to,names,counts,note){
  if(skill>=to)return;
  const countFor=(name,i)=>{const n=Array.isArray(counts)?counts[i]:counts;return n>10&&skill>from?Math.max(1,Math.ceil(n*(to-skill)/(to-from))):n;};
  const batchCost=(plan,unlock)=>plan.error||unlock.gold==null||plan.rows.some(r=>g.vendor.includes(r.name)&&(!r.tier||r.tier===1)&&r.price?.source!=='vendor')?null:plan.total+unlock.gold;
  const candidates=names.map((name,i)=>{const count=countFor(name,i),plan=h.guideRecipe(data,c,g,name,count),unlock=routeUnlock(data,c,g,name);return {name,count,plan,unlock,cost:batchCost(plan,unlock)};});
  if(skill>=from&&skill===imported){for(const alt of routeAlternatives(data,c,g,names,skill,to)){const reference=candidates.find(x=>x.name===alt.reference),plan=h.guideRecipe(data,c,g,alt.name,reference.count),unlock=routeUnlock(data,c,g,alt.name);if(!plan.error&&plan.total>0)candidates.push({...alt,count:reference.count,plan,unlock,cost:batchCost(plan,unlock),alternative:true});}}
  const selected=candidates.find(x=>x.name===(options.choices?.[from]||options.finish))||[...candidates].sort((a,b)=>(a.cost??Infinity)-(b.cost??Infinity)||Number(b.unlock.learned||b.unlock.trainer)-Number(a.unlock.learned||a.unlock.trainer))[0];
  choices.push(...candidates.map(x=>({...x,from,to})));add(from,to,selected.name,selected.count,note,{chosen:true,alternative:selected.alternative,reference:selected.reference});
 }
 function knownFinish(from,to,fallback){
  if(skill>=to)return;
  if(skill<from||skill!==imported){gate(from,to,'Finish with an unlocked recipe or orders',fallback);return;}
  const now=Date.now()/1000,latest=new Map();for(const r of data.catalog||[]){if(r.guid!==c.guid||r.profession?.expansionName!=='Midnight'||r.profession?.parentProfessionName!==g.name)continue;const old=latest.get(r.recipeID);if(!old||r.observedAt>old.observedAt)latest.set(r.recipeID,r);}
  const candidates=[];for(const r of latest.values()){
   if(!r.learned||r.disabled||r.profession.skillLevel!==skill||!Number.isFinite(r.observedAt)||now-r.observedAt>86400||r.observedAt>now+300||!r.canSkillUp||![0,1,2].includes(r.relativeDifficulty)||!(r.numSkillUps>0)||r.maxTrivialLevel<to||![1,3].includes(r.schematic?.recipeType)||r.schematic.isRecraft||!r.cooldownCaptured||!r.cooldown||r.cooldown.seconds!==0||r.cooldown.isDay||r.cooldown.maxCharges>0||!Number.isFinite(r.cooldown.observedAt)||now-r.cooldown.observedAt>86400||r.cooldown.observedAt>now+300)continue;
   const count=Math.ceil(Math.min(10,to-skill)/r.numSkillUps),plan=h.guideRecipe(data,c,g,r.name,count),unlock=routeUnlock(data,c,g,r.name);
   if(plan.error||!(plan.total>0)||plan.rows.some(row=>g.vendor.includes(row.name)&&(!row.tier||row.tier===1)&&row.price?.source!=='vendor'))continue;
   candidates.push({name:r.name,count,plan,unlock,cost:plan.total,from,to,finishBatch:true,color:r.relativeDifficulty,points:r.numSkillUps,perPoint:plan.total/count/r.numSkillUps});
  }
  candidates.sort((a,b)=>a.color-b.color||a.perPoint-b.perPoint||a.name.localeCompare(b.name));
  const selected=candidates.find(x=>x.name===options.choices?.[from])||candidates[0];
  if(!selected){gate(from,to,'Capture an available finishing recipe','No fully priced, available finishing recipe is recorded at this character’s current skill. '+fallback);return;}
  choices.push(...candidates);add(from,to,selected.name,selected.count,'Small finishing batch from your learned recipes. '+(selected.color===0?'Recorded orange at your current skill.':'Recorded yellow/green: skill gains are chance-based.')+' Check skill after each craft and stop at 100; import before buying another batch.',{chosen:true,finishBatch:true});
 }
 switch(g.name){
 case 'Enchanting':
  add(1,25,'Runed Refulgent Copper Rod',30,'Disenchant the rods after crafting.');
  gate(1,25,'Disenchant rods and import','Disenchanting returns are random. Import the new dust and skill before buying the following stages.');
  for(const name of ['Enchant Helm - Rune of Avoidance','Thalassian Phoenix Oil'])add(25,27,name,1);
  for(const name of ["Enchant Ring - Nature's Wrath",'Illusory Adornment - Blooming Light'])add(27,38,name,1);
  choose(27,38,["Enchant Ring - Nature's Wrath",'Illusory Adornment - Blooming Light'],13,'Repeat the cheaper available recipe; stop at 38.');
  for(const name of ['Enchant Shoulders - Flight of the Eagle','Enchant Helm - Hex of Leeching'])add(38,40,name,1);
  add(40,52,"Thalassian Spellweaver's Wand",4);
  for(const name of ['Enchant Ring - Amani Mastery','Enchant Helm - Blessing of Speed','Enchant Shoulders - Thalassian Recovery'])add(52,55,name,1);
  add(55,62,'Enchant Ring - Amani Mastery',9);
  choose(62,100,['Enchant Weapon - Worldsoul Aegis'],38,'One point per craft in the baseline route. Enchant vellum; check recipe color and top up if skill gains miss.');break;
 case 'Cooking':
  add(1,25,'Spiced Biscuits',50,'Keep the food for Hearty Food later.');add(25,35,'Felberry Figs',10);
  gate(35,100,'Convert food with Hearty Food','Use your biscuits as the target. When you run out, make another 25 biscuit crafts, then convert them. At skill 35 or higher this guide shows the 25-craft top-up shopping batch. Repeat until 100; import between batches. No exact full-route count is promised.',skill>=35?{"A Big Ol' Stick of Butter":25,'Pouch of Spices':75}:null);break;
 case 'Alchemy':
  add(1,7,'Silvermoon Health Potion',6,'Keep the potions for recycling.');
  gate(7,20,'Recycle Silvermoon Health Potions','Begin with 10 recycling operations on the potions you made. Buy 20 Oil of Heartwood. Stop at 20 and import the recovered reagents before the next purchases.',{'Oil of Heartwood':20});
  {for(const name of ['Refreshing Serum','Lightfused Mana Potion',"Primal Philosopher's Stone",'Transmute: Mote of Wild Magic','Composite Flora','Enlightenment Tonic','Entropic Extract'])add(20,27,name,1,name==='Refreshing Serum'?"Research the stone and mana potion at Camberon's Cauldron first. Research payments are additional; confirm them before shopping. Make the stone before transmutes.":'');}
  add(27,32,'Entropic Extract',8);add(32,50,'Silvermoon Health Potion',30);
  choose(50,100,g.finish.map(x=>x.recipe),g.finish.map(x=>x.count),'Acquire the selected research recipe first. Stop at 100; yellow crafts may require a top-up.');break;
 case 'Blacksmithing':
  add(1,15,'Refulgent Copper Ingot',25,'Keep the ingots for subsequent steps.',{intermediate:true});trainers(15,50,45,['Refulgent Copper Ingot','Sterling Alloy']);add(50,70,'Sterling Alloy',50,'Keep the alloy.',{intermediate:true});
  choose(70,100,g.finish.map(x=>x.recipe),10,'Ten-craft shopping batch. Requires Craftsmithing unlock. Check skill after each batch; yellow/green gains vary. Repeat until 100.');break;
 case 'Jewelcrafting':
  {const opts=['Refulgent Copper Ore','Umbral Tin Ore','Brilliant Silver Ore'].map(n=>h.guideItem(data,c,n)).sort((a,b)=>(a.price?.price??Infinity)-(b.price?.price??Infinity));gate(1,14,'Prospect ore and make four lenses','Prospect 60 '+opts[0].name+', then make four Sin\'dorei Lens crafts from the results. Import the gems and dust before buying the next stage.',{[opts[0].name]:60});}
  trainers(14,50,45,["Sin'dorei Lens",'Midnight Prospecting']);add(50,65,"Monologuer's Chalice",40);
  choose(65,100,g.finish.map(x=>x.recipe),10,'Ten-craft shopping batch. Acquire the design first; repeat batches to 100, checking skill before buying more.');break;
 case 'Inscription':
  gate(1,20,'Mill the starter herbs','Mill these herbs and keep the pigments. Import your resulting inventory and skill before buying inks or later supplies.',{'Tranquility Bloom':360,Argentleaf:100,'Mana Lily':90,Sanguithorn:90});
  add(20,30,'Munsell Ink',11,'Keep the ink.',{intermediate:true});add(20,30,'Sienna Ink',12,'Keep the ink.',{intermediate:true});
  trainers(30,50,45,['Midnight Milling','Munsell Ink','Sienna Ink']);add(42,50,'Thalassian Treatise on Inscription',6,'Choose Calm Hands at 25 to unlock the treatise.');choose(50,100,['Thalassian Treatise on Inscription'],64,'Green gains near 100 can need top-ups. Use the selected learned treatise.');break;
 case 'Leatherworking':
  trainers(1,60,55);choose(60,91,g.finish.map(x=>x.recipe),35,'Confirm the quest, specialization or pattern unlock before shopping. Stop at 91.');
  knownFinish(91,100,'The baseline uses three epic crafts/orders that grant three points each. Open your learned recipes and import; order availability and customer-provided materials are not captured.');break;
 case 'Engineering':
  add(1,16,'Song Gear',8,'Keep the gears.');
  {const opts=['Powder Pigment','Refulgent Copper Ingot','Bright Linen Bolt'].map(n=>h.guideItem(data,c,n)).sort((a,b)=>(a.price?.price??Infinity)-(b.price?.price??Infinity));gate(1,16,'Recycle seven times','Use five '+opts[0].name+' per recycling operation. Import after recycling; keep the recovered parts.',{[opts[0].name]:35});}
  for(const name of ['Evercore Shade','Evercore Vision Guard'])add(16,20,name,1,'First craft only.');
  for(const name of ['Evercore Dome Dinger','Evercore Zoomshroud','Evercore Reconnaissance'])add(20,25,name,1,'First craft only.');
  add(25,39,'Soul Sprocket',10,'Spend 10 Knowledge in Recycling for discoveries.');for(const name of ['Perfected Cogwheel','Greased Cogwheel','Consistent Cogwheel','Flux Cogwheel'])add(25,39,name,1);
  {const opts=['Powder Pigment','Refulgent Copper Ingot','Bright Linen Bolt'].map(n=>h.guideItem(data,c,n)).sort((a,b)=>(a.price?.price??Infinity)-(b.price?.price??Infinity));gate(39,45,'Recycle and finish trainer first crafts','Recycle about 20 more times using '+opts[0].name+'; finish trainer first crafts. Import when a Quel’dorei equipment recipe is discovered.',{[opts[0].name]:100});}
  choose(45,80,["Quel'dorei Guards"],60,'Requires this Recycling discovery; do not buy before unlocking.');
  knownFinish(80,100,'Continue Recycling until you discover a suitable decor recipe, or use available equipment orders. Unlock and capture the recipe before buying its ingredients.');break;
 }
 // Purchase through the next random-yield or availability checkpoint, never guess its outputs.
 const stop=steps.findIndex(s=>s.gate),purchased=stop<0?steps:steps.slice(0,stop+1),demand=new Map(),produced=new Map(),unlocks=new Map();
 const put=row=>{const key=row.item||row.name,old=demand.get(key)||{...row,needed:0};old.needed+=row.needed;demand.set(key,old);};
 for(const step of purchased){
  if(step.gate){for(const row of h.guideShopping(data,c,step.requirements||{}).rows)put(row);continue;}
  const plan=h.guideRecipe(data,c,g,step.name,step.count);step.materials=plan.rows;step.unlock=routeUnlock(data,c,g,step.name);unlocks.set(step.name,step.unlock);
  if(plan.error){issues.push(step.name+': '+plan.error);continue;}
  for(const row of plan.rows){let needed=row.needed;const key=h.guideNorm(row.name),credit=produced.get(key);if(credit&&(h.guideIndex(data).get(key)||[]).every(id=>Object.values(plan.record.schematic.reagentSlotSchematics||{}).some(slot=>slot.required&&Object.values(slot.reagents||{}).some(r=>'i:'+r.itemID===row.item)&&Object.values(slot.reagents||{}).some(r=>'i:'+r.itemID===id)))){const take=Math.min(credit,needed);needed-=take;produced.set(key,credit-take);}if(needed)put({...row,needed});}
  if(plan.record.schematic.recipeType===3){const vellum=h.guideItem(data,c,'Enchanting Vellum');put({...vellum,needed:step.count});}
  if(step.intermediate){const n=Number(plan.record.schematic.quantityMin);if(n>0)produced.set(h.guideNorm(step.name),(produced.get(h.guideNorm(step.name))||0)+n*step.count);}
 }
 const rows=[...demand.values()].map(row=>{const stock=row.item?routeMath.materialPlan({materials:{[row.item]:row.needed}},{[row.item]:row.item},1,c,data.inventory||{},data.market||{}).rows[0]:{own:0,missing:row.needed};const vendor=g.vendor.includes(row.name)&&(!row.tier||row.tier===1);return {...row,own:stock.own,missing:stock.missing,scope:row.price?.scope||c.realm,vendor,price:vendor?{...row.price,source:'vendor',price:row.price?.source==='vendor'?row.price.price:null}:row.price};});
 const recipes=[...unlocks.values()].filter(u=>u.item).map(u=>u.item),sum=field=>!issues.length&&rows.every(r=>!r[field]||Number.isFinite(r.price?.price))?rows.reduce((n,r)=>n+r[field]*(r.price?.price||0),0):null;
 return {skill,imported,steps,purchased,checkpoint:stop>=0?steps[stop]:null,choices,rows,recipes,unlocks:[...unlocks],issues,complete:!issues.length,total:sum('needed'),buy:sum('missing'),unlockGold:[...unlocks.values()].every(u=>u.gold!=null)?[...unlocks.values()].reduce((n,u)=>n+u.gold,0):null};
}
if(typeof module!=='undefined')module.exports={professionRoute,routeUnlock,routeSource,routeAlternatives};

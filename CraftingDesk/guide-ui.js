{
 const main=document.querySelector('main'),panel=document.createElement('section');panel.className='panel';panel.id='professionGuide';
 const nav=document.createElement('nav');nav.className='filters desk-tabs';nav.innerHTML='<button id="showGuides">Profession guides</button><button id="showCrafts">Crafting & profit</button><button id="showReady">Concentration ready</button>';main.prepend(nav);nav.after(panel);
 panel.innerHTML='<h2>Set up a profession</h2><p>Choose a character and follow the Midnight route from 1 to 100. Review the route and its unlocks, buy the missing supplies, then follow the crafting steps.</p><div class="daily-filters"><div><label for="guideCharacter">Character</label><select id="guideCharacter"></select></div><div><label for="guideProfession">Profession</label><select id="guideProfession"></select></div></div><div id="guideBody"></div>';
 const money=n=>n==null?'Price incomplete':(n/10000).toLocaleString(undefined,{maximumFractionDigits:2})+' g';
 const el=(parent,tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
 const readyPanel=document.createElement('section');readyPanel.className='panel';readyPanel.id='concentrationReadyPanel';panel.after(readyPanel);
 let activeTab='guides';
 function mode(tab){activeTab=tab;for(const child of main.children)if(child!==nav&&child.id!=='errors')child.hidden=child===panel?tab!=='guides':child===readyPanel?tab!=='ready':tab!=='crafts';for(const [id,name]of [['showGuides','guides'],['showCrafts','crafts'],['showReady','ready']])$(id).setAttribute('aria-pressed',String(tab===name));if(tab==='ready')renderReady();}
 $('showGuides').onclick=()=>mode('guides');$('showCrafts').onclick=()=>mode('crafts');$('showReady').onclick=()=>mode('ready');mode('guides');
 let readyStockOnly=false;
 let readyOptions={minMargin:15,minSaleRate:0.15,minDailySold:0,maxAge:24};
 function renderReady(){
  readyPanel.replaceChildren();el(readyPanel,'h2','Concentration ready');
  el(readyPanel,'p','Spend each character’s currently available concentration on the most profitable repeated-craft batch. Your saved plan reserves concentration and stock.');
  const controls=el(readyPanel,'div');controls.className='daily-filters';
  for(const [key,label,step] of [['minMargin','Minimum margin (%)','1'],['minSaleRate','Minimum sale rate','0.01'],['minDailySold','Minimum daily sold','0.1']]){
   const box=el(controls,'div'),caption=el(box,'label',label),input=el(box,'input');input.type='number';input.min='0';input.step=step;input.value=readyOptions[key];input.setAttribute('aria-label',label);input.onchange=()=>{readyOptions[key]=Math.max(0,Number(input.value)||0);renderReady();};
  }
  const ageBox=el(controls,'div');el(ageBox,'label','Craft capture age');const age=el(ageBox,'select');for(const [value,label] of [[24,'Within 24 hours'],[72,'Within 3 days'],[0,'Any age']])age.add(new Option(label,value));age.value=readyOptions.maxAge;age.onchange=()=>{readyOptions.maxAge=Number(age.value);renderReady();};
  const actions=el(readyPanel,'div');actions.className='filters';const refresh=el(actions,'button','Refresh concentration batches');refresh.onclick=renderReady;
  const label=el(actions,'label'),stock=el(label,'input');stock.type='checkbox';stock.style.minWidth='0';stock.style.width='auto';stock.checked=readyStockOnly;label.append(' Owned materials only');stock.onchange=()=>{readyStockOnly=stock.checked;renderReady();};
  const context=window.getDailyPlanningContext?.();if(!context?.loaded){el(readyPanel,'p','Loading your saved crafting plan…');return;}
  const options={...readyOptions,stockOnly:readyStockOnly},now=Date.now()/1000;
  const entries=dailyCandidates(data,window.getSavedCraftingSetups?.()||[],Number($('dailyFee').value),now),rows=concentrationReady(data,entries,options,context.planned,now);
  if(!rows.length){el(readyPanel,'p','No valid Midnight concentration samples yet. Open your professions in-game, save, then refresh Nexus data.');return;}
  let identity=null,section=null;
  for(const row of rows){
   if(identity!==row.character.guid){identity=row.character.guid;section=el(readyPanel,'section');section.className='panel';el(section,'h3',row.character.name+' · '+row.character.realm);}
   const card=el(section,'article');card.className='daily-card';el(card,'h4',row.profession.name);
   el(card,'p',`${row.available} available / ${row.cap} maximum · ${row.reserved} reserved · Skill ${row.profession.rank??'?'} / ${row.profession.max??'?'}`);
   el(card,'small','Concentration sample: '+new Date(row.observedAt*1000).toLocaleString());
   if(!row.best){el(card,'p',row.reason);if(row.readyAt)el(card,'p','Next known opportunity: '+new Date(row.readyAt*1000).toLocaleString());continue;}
   const b=row.best,e=b.entry;el(card,'h4',`${b.count} × ${e.setup.name}`);
   el(card,'p',`${money(b.profit)} net batch profit · ${b.spent} concentration · ${b.left} left. Buy missing: ${money(b.buy)}.`);
   renderBatchShopping(card,b);
   const status=el(card,'p');status.setAttribute('role','status');const buttons=el(card,'div');buttons.className='filters';
   const add=el(buttons,'button','Add batch to my plan');add.onclick=async()=>{add.disabled=true;try{await window.addReadyConcentrationBatch({...e.setup,count:b.count});renderReady();}catch(error){status.textContent=error.message;add.disabled=false;}};
   const inspect=el(buttons,'button','View craft details');inspect.onclick=()=>{mode('crafts');(window.openCraftBatch||window.restoreCraftingSetup)?.({...e.setup,count:b.count});};
   if(row.alternatives.length){const details=el(card,'details');el(details,'summary','Other eligible batches');for(const alt of row.alternatives)el(details,'p',`${alt.count} × ${alt.entry.setup.name}: ${money(alt.profit)} net · ${alt.spent} concentration.`);}
  }
 }
 function shopping(parent,plan,label,includeImport=true){
   el(parent,'p',`Listed supplies: ${money(plan.total)} · Buy missing: ${money(plan.buy)}. Uses your imported inventory and prices; excludes unlisted supplies and recipe unlock costs.`);
   const table=el(parent,'table');table.style.width='100%';table.innerHTML='<thead><tr><th align="left">Supply</th><th>Need</th><th>Have</th><th>Buy</th><th>Source</th></tr></thead>';
   const body=el(table,'tbody');for(const r of plan.rows){const row=el(body,'tr');for(const text of [r.name+(r.tier?' · Quality '+r.tier:''),r.needed,r.own,r.missing,r.price?.source==='vendor'?r.price.npc||'Vendor':r.price?'AH':'Price unknown']){const cell=el(row,'td',String(text));cell.style.padding='6px';}}
   if(!includeImport)return;
   const result=guideImport(plan.rows,label,data.inventory),button=el(parent,'button','Copy Auctionator import');button.disabled=!result.text;
   const status=el(parent,'p','');status.setAttribute('role','status');
   const importDetails=el(parent,'details');el(importDetails,'summary','View import text');
   const fallback=el(importDetails,'textarea');fallback.value=result.text;fallback.readOnly=true;fallback.style.width='100%';fallback.rows=3;fallback.setAttribute('aria-label',label+' Auctionator import');
   button.onclick=async()=>{try{await copyCraftText(result.text);status.textContent='Copied. Paste into Auctionator → Shopping → Import.';}catch{importDetails.open=true;fallback.focus();fallback.select();status.textContent='Select and copy the import below (Ctrl+C).';}};
   if(result.omitted.length)el(parent,'p','Search manually: '+result.omitted.map(r=>`${r.missing} × ${r.name}`).join(', '));
   el(parent,'small','Only missing AH materials are copied. Vendor supplies are separate. Import replaces a list with the same name.');
 }
 const tailoringSelections=new Map();
 function renderTailoring(out,c){
   const options=tailoringSelections.get(c.guid)||{},plan=tailoringRoute(data,c,options);
   el(out,'p','Follow this route from your current skill to 100. Quantities are planning batches: stop at each target and top up if yellow or green crafts miss a point. Keep the bolts you make for the following steps.');
   const controls=el(out,'div');controls.className='daily-filters';controls.style.gridTemplateColumns='repeat(auto-fit,minmax(220px,1fr))';
   const skillLabel=el(controls,'label','Starting skill '),skill=el(skillLabel,'input');skill.type='number';skill.min=1;skill.max=100;skill.value=plan.skill;skill.setAttribute('aria-label','Tailoring starting skill');
   const routeLabel=el(controls,'label','65–90 recipe '),route=el(routeLabel,'select');route.setAttribute('aria-label','Tailoring lining route');
   route.add(new Option('Lowest known materials + recipe cost',''));
   for(const choice of plan.choices)route.add(new Option(choice.name+(choice.cost==null?' · unlock/price incomplete':' · '+money(choice.cost)),choice.name));route.value=options.lining||'';
   const gearLabel=el(controls,'label','90–100 recipe '),gearSelect=el(gearLabel,'select');gearSelect.setAttribute('aria-label','Tailoring final recipe');gearSelect.add(new Option('Prefer learned, then cheapest materials',''));for(const x of plan.gearChoices)gearSelect.add(new Option(x.name+' · '+money(x.cost)+(x.unlock.currency?' + 150 Moxie':''),x.name));gearSelect.value=options.gear||'';gearSelect.onchange=()=>{tailoringSelections.set(c.guid,{...options,gear:gearSelect.value});renderGuide();};
   const skillActions=el(out,'div');skillActions.className='filters';const resetSkill=el(skillActions,'button','Use imported skill');resetSkill.onclick=()=>{const next={...options};delete next.skill;tailoringSelections.set(c.guid,next);renderGuide();};
   skill.onchange=()=>{if(!skill.checkValidity())return;tailoringSelections.set(c.guid,{...options,skill:Number(skill.value)});renderGuide();};
   const applySkill=el(skillActions,'button','Update starting skill');applySkill.onclick=skill.onchange;
   route.onchange=()=>{tailoringSelections.set(c.guid,{...options,lining:route.value});renderGuide();};
   el(out,'small',tailoringSkill(c)==null?'No imported Midnight Tailoring rank. Using starting skill '+plan.skill+'; confirm the profession is learned.':'Imported skill: '+tailoringSkill(c)+'. Import after crafting to refresh skill and inventory before buying more.');
   if(!plan.steps.length){el(out,'h3','Tailoring is already at 100');el(out,'p','No leveling supplies needed. Change starting skill to review a new-character route.');return;}
   if(plan.choices.some(x=>x.alternative))el(out,'p','Captured alternatives are already learned and match the baseline’s current skill-up color, points and grey cutoff. Batch counts are estimates; later skill-up chances may differ.');
   if(plan.skill<90)el(out,'p','Selected: '+plan.chosen+'. Comparison includes the lining pattern price when unlearned.'+(plan.choices.some(x=>x.cost==null)?' Missing acquisition prices prevent a confirmed cheapest comparison.':''));
   el(out,'h3','1. Unlocks before you buy');
   const trainerUnlocks=el(out,'details');trainerUnlocks.hidden=!plan.unlocks.some(([n,u])=>u.text.startsWith('Learn from Galana'));el(trainerUnlocks,'summary','Trainer recipes and training costs');
   for(const [name,u]of plan.unlocks.filter(([n,u])=>u.text!=='Already learned'))el(u.text.startsWith('Learn from Galana')?trainerUnlocks:out,'p',name+' — '+u.text+(u.item?' '+money(u.gold):''));
   el(out,'p','Training and recipe gold: '+money(plan.unlockGold)+(plan.unlockGold===null?' (known portion '+money(plan.knownUnlockGold)+')':'')+'.'+(plan.currency?' Additional currency: '+plan.currency+' Artisan Tailor’s Moxie.':''));
   el(out,'h3','2. One shopping list for the remaining route');
   el(out,'p',plan.buy!==null&&plan.unlockGold!==null?'Estimated remaining purchase cost: '+money(plan.buy+plan.unlockGold)+' including training and patterns, plus any listed Moxie.':'A full gold total needs the missing vendor or training prices below; known AH purchases remain priced.');
   el(out,'p','Includes all required slots from the captured recipes. Bolts produced by earlier steps are reused; existing inventory is deducted once across the whole route. Vendor supplies are excluded from the Auctionator import even when their vendor price is missing.');
   if(plan.issues.length)el(out,'p','Incomplete recipe data: '+plan.issues.join('; '));
   const ahRows=plan.rows.filter(r=>!r.vendor),sumAH=field=>ahRows.every(r=>!r[field]||Number.isFinite(r.price?.price))?ahRows.reduce((n,r)=>n+r[field]*(r.price?.price||0),0):null;shopping(out,{rows:ahRows,total:sumAH('needed'),buy:sumAH('missing')},'Tailoring remaining route',false);
   el(out,'h4','Buy from the Tailoring supply vendor');for(const r of plan.rows.filter(r=>r.vendor))el(out,'p',`${r.name}: ${r.needed} needed · ${r.own} owned · buy ${r.missing}${Number.isFinite(r.price?.price)?' · '+money(r.missing*r.price.price):' · vendor price not captured'}`);
   if(plan.recipes.length){el(out,'h4','Patterns to acquire');for(const r of plan.recipes)el(out,'p',r.name+' — '+money(r.price?.price));}
   const all=guideImport([...plan.rows,...plan.recipes],'Tailoring materials and patterns',data.inventory);
   if(all.omitted.length)el(out,'p','Search manually: '+all.omitted.map(r=>r.missing+' × '+r.name).join(', '));
   el(out,'small','Import replaces the Auctionator list with the same name. Vendor supplies stay in the separate list above.');
   const copy=el(out,'button','Copy materials + patterns to Auctionator');copy.disabled=!plan.complete||!all.text;
   const copyStatus=el(out,'p');copyStatus.setAttribute('role','status');
   const details=el(out,'details');el(details,'summary','View combined import');const text=el(details,'textarea');text.value=all.text;text.readOnly=true;text.rows=4;text.style.width='100%';
   copy.onclick=async()=>{try{await copyCraftText(all.text);copyStatus.textContent='Copied materials and patterns. Paste into Auctionator Shopping → Import.';}catch{details.open=true;text.focus();text.select();copyStatus.textContent='Copy the selected import with Ctrl+C.';}};
   el(out,'h3','3. Craft in this order');
   const list=el(out,'ol');for(const step of plan.steps){const row=el(list,'li');row.style.padding='8px';const doneLabel=el(row,'label');const done=el(doneLabel,'input');done.type='checkbox';done.setAttribute('aria-label','Done: '+step.name+' '+step.from+'–'+step.to);const doneKey='tailoring-done:'+c.guid+':'+plan.skill+':'+step.id;try{done.checked=localStorage.getItem(doneKey)==='1';}catch{}done.onchange=()=>{try{localStorage.setItem(doneKey,done.checked?'1':'0');}catch{}};doneLabel.append(' Done ');el(row,'b',`${step.from}–${step.to}: ${step.count} × ${step.name}`);el(row,'p',step.materials?.map(m=>m.quantity+' × '+m.name).join(', ')||'Recipe details missing.');if(step.name==='Bright Linen Bolt')el(row,'small','Make this preparation batch even after the recipe turns grey; later steps use the bolts.');}
   el(out,'p','Checkmarks save your place only; import after crafting to recalculate remaining purchases from updated skill and inventory. The first-craft section includes captured trainer recipes learned by skill 35. If a first-craft bonus is already completed, skip it and refresh your skill before the next batch. This route does not spend concentration or assume multicraft/resourcefulness returns.');
 }
 const routeSelections=new Map();
 function renderProfession(out,c,g){
  const key=c.guid+':'+g.name,options=routeSelections.get(key)||{},plan=professionRoute(data,c,g,options);
  const controls=el(out,'div');controls.className='daily-filters';
  const label=el(controls,'label','Starting skill '),skill=el(label,'input');skill.type='number';skill.min=1;skill.max=100;skill.value=plan.skill;skill.setAttribute('aria-label',g.name+' starting skill');
  const update=()=>{if(skill.checkValidity()){routeSelections.set(key,{...options,skill:Number(skill.value)});renderGuide();}};skill.onchange=update;el(controls,'button','Update starting skill').onclick=update;
  el(controls,'button','Use imported skill').onclick=()=>{const next={...options};delete next.skill;routeSelections.set(key,next);renderGuide();};
  el(out,'p',plan.imported==null?'No imported Midnight rank. Using starting skill '+plan.skill+'.':`Imported skill: ${plan.imported}. Import after crafting to refresh skill and stock.`);
  if(!plan.steps.length){el(out,'h3',g.name+' is already at 100');return;}
  if(plan.choices.length){
   const groups=new Map();for(const x of plan.choices){if(!groups.has(x.from))groups.set(x.from,[]);groups.get(x.from).push(x);}
   for(const [from,choices]of groups){const label=el(out,'label',from+'–'+choices[0].to+' recipe '),select=el(label,'select');select.setAttribute('aria-label',g.name+' route choice '+from);select.add(new Option(choices.some(x=>x.finishBatch)?'Prefer orange, then cost per potential skill point':'Lowest known materials + recipe gold',''));for(const x of choices)select.add(new Option(x.name+' · '+money(x.cost)+(x.alternative?' · captured alternative':x.unlock.learned?' · learned':''),x.name));select.value=options.choices?.[from]||'';select.onchange=()=>{routeSelections.set(key,{...options,choices:{...options.choices,[from]:select.value}});renderGuide();};}
   el(out,'p','Comparison includes known recipe gold and material value. Unknown unlock or vendor prices cannot establish the cheapest choice. Currency, quest and specialization requirements must be met before buying. Captured alternatives match the current color, points per craft and grey cutoff, but future skill-up chances may differ.');
  }
  for(const step of plan.steps.filter(s=>s.chosen)){const choice=plan.choices.find(x=>x.name===step.name&&x.to===step.to),baseline=plan.choices.filter(x=>!x.alternative&&x.to===step.to&&x.cost!=null).sort((a,b)=>a.cost-b.cost)[0];el(out,'p',`Selected for ${step.from}–${step.to}: ${step.count} crafts of ${step.name}. Estimated materials and recipe gold: ${money(choice?.cost)}.`+(choice?.alternative&&baseline&&choice.cost!=null&&baseline.cost>choice.cost?' '+money(baseline.cost-choice.cost)+' less than '+baseline.name+' for the compared planning batch.':''));}
  el(out,'h3','1. Learn before buying');
  const unlocks=el(out,'details');el(unlocks,'summary','Recipes needed for this shopping batch');for(const [name,u]of plan.unlocks)el(unlocks,'p',name+' — '+u.text);
  el(out,'p','Training and recipe gold for this batch: '+money(plan.unlockGold)+'. Currency and unlock requirements are listed with the recipes.');
  el(out,'h3',plan.checkpoint?'2. Shopping through the next checkpoint':'2. Combined shopping list');
  if(plan.checkpoint)el(out,'p','Buy through “'+plan.checkpoint.name+'”. '+plan.checkpoint.note+' Later steps remain below; their purchases are recalculated after you import the result.');
  el(out,'p','These are planning batches, not guaranteed skill gains. Stop at each target and import before topping up. Trainer steps show first-craft status when present in your import; skip grey recipes with no remaining bonus. Material stock is deducted once across this shopping batch.');
  if(plan.issues.length)el(out,'p','Shopping is incomplete: '+plan.issues.join('; '));
  const ah=plan.rows.filter(r=>!r.vendor),sum=field=>ah.every(r=>!r[field]||Number.isFinite(r.price?.price))?ah.reduce((n,r)=>n+r[field]*(r.price?.price||0),0):null;shopping(out,{rows:ah,total:sum('needed'),buy:sum('missing')},g.name+' route',false);
  if(plan.rows.some(r=>r.vendor)){el(out,'h4','Buy from the supply vendor');for(const r of plan.rows.filter(r=>r.vendor))el(out,'p',`${r.name}${r.tier?' · Quality '+r.tier:''}: ${r.needed} needed · ${r.own} owned · buy ${r.missing} · ${money(r.missing===0?0:r.price?.price==null?null:r.price.price*r.missing)}`);}
  if(plan.recipes.length){el(out,'h4','Recipe items');for(const r of plan.recipes)el(out,'p',r.name+' · buy '+r.missing+' · '+money(r.price?.price));}
  const result=guideImport([...plan.rows,...plan.recipes],g.name+' route',data.inventory),copy=el(out,'button','Copy shopping to Auctionator');copy.disabled=!plan.complete||!result.text;
  const status=el(out,'p');status.setAttribute('role','status');const details=el(out,'details');el(details,'summary','View combined import');const text=el(details,'textarea');text.value=result.text;text.readOnly=true;text.rows=4;text.style.width='100%';
  copy.onclick=async()=>{try{await copyCraftText(result.text);status.textContent='Copied. Paste into Auctionator Shopping → Import.';}catch{details.open=true;text.focus();text.select();status.textContent='Copy the selected text with Ctrl+C.';}};
  if(result.omitted.length)el(out,'p','Manual purchases: '+result.omitted.map(r=>r.missing+' × '+r.name).join(', '));
  el(out,'small','Only missing AH items and recipe items are copied, with their selected quality. Vendor supplies stay above. Import replaces a list with the same name.');
  el(out,'h3','3. Craft in this order');const list=el(out,'ol');for(const step of plan.steps){const li=el(list,'li');li.style.padding='8px';const label=el(li,'label'),done=el(label,'input');done.type='checkbox';const id='route-done:'+key+':'+plan.skill+':'+step.id;try{done.checked=localStorage.getItem(id)==='1';}catch{}done.onchange=()=>{try{localStorage.setItem(id,done.checked?'1':'0');}catch{}};label.append(' Done ');el(li,'b',`${step.from}–${step.to}: ${step.count?step.count+' × ':''}${step.name}`);if(step.alternative)el(li,'p','Captured alternative to '+step.reference+': same current skill-up color, points per craft and grey cutoff. Uses the same estimated batch size; future skill-up luck may differ.');if(step.note)el(li,'p',step.note);if(step.materials)el(li,'p',step.materials.map(r=>r.needed+' × '+r.name).join(', '));}
  el(out,'small','Checkmarks save your place; they do not change inventory or skill. Counts are craft operations, not output item counts. The app does not assume random resourcefulness, multicraft or recycled-material returns.');
 }
 function renderInvestments(out,g,c){
   const investments=el(out,'details');el(investments,'summary','Recipe investments · separate from leveling');
   el(investments,'p','Requires over 20% profit on material value after a 5% selling fee, and TSM sale rate over 0.1. Uses recent, captured crafts from your warband. An unlearned character’s outcome cannot be predicted from another character’s stats; the reference crafter is named below.');
   const opportunities=recipeInvestments(data,g.name,Date.now()/1000,c);
   if(!opportunities.length)el(investments,'p','No recent captured craft meets both filters with a uniquely matched, priced recipe item or recorded vendor offer. Unlearned crafts have no reliable output-quality capture yet, so their profit is not guessed.');
   for(const o of opportunities.slice(0,12)){
     const box=el(investments,'div');box.className='daily-card';const e=o.entry;
     el(box,'p',o.learningKnown?'Not learned on '+c.name+'.':'Learning status on '+c.name+' is unknown; open the profession and import.');
     el(box,'b',e.recipe.name+' · '+(e.setup.concentration>0?'with concentration':'without concentration'));
     el(box,'p',`${e.setup.crafterName} (${e.setup.realm}) reference: ${money(e.result.finance.profit)} profit per craft · ${e.margin==null?'unknown':e.margin.toFixed(1)}% · Sale rate ${e.sales.saleRate} · Regional daily sold ${e.sales.dailySold??'unknown'}.`);
     el(box,'p',o.price?`AH recipe on ${c.realm}: ${money(o.price.price)}. Conditional recovery at the reference crafter’s results: ${o.salesToRecover} individual output items sold at ${money(o.profitPerItem)} profit each.`:'No AH recipe price; vendor acquisition only.');
     if(o.price){
       const owner=(c.name+'-'+c.realm).replaceAll(' ','').toLowerCase();
       const own=(data.inventory?.items?.[o.item.item]||[]).filter(p=>p.location==='warband'||p.bound===false||p.owner.replaceAll(' ','').toLowerCase()===owner).reduce((n,p)=>n+p.quantity,0);
       shopping(box,{total:o.price.price,buy:own>0?0:o.price.price,rows:[{item:o.item.item,name:o.item.name,needed:1,own,missing:own>0?0:1,scope:o.price.scope||c.realm,price:o.price}]},'Recipe investment');
     }
     for(const v of o.vendors.slice(0,3))el(box,'p',`${v.npcName||'Vendor'}: ${money(v.price/v.stackCount)} per recipe${(v.costs||[]).map(x=>' + '+(x.amount/v.stackCount)+' '+(x.name||x.link||'payment')).join('')} · checked on ${v.character}. ${v.canAfford===true?'Affordable at that visit.':'Check currency and requirements.'}`);
     if(o.vendors.length){
       const instructions=o.vendors.map(v=>`Buy ${o.item.name} from ${v.npcName||'the recorded vendor'}${v.zone?' in '+v.zone:''}: ${money(v.price/v.stackCount)}${(v.costs||[]).map(x=>' + '+(x.amount/v.stackCount)+' '+(x.name||x.link||'payment')).join('')}. Check learning requirements and currency on ${c.name}.`).join('\n');
       const copy=el(box,'button','Copy vendor purchase instructions'),status=el(box,'p');status.setAttribute('role','status');copy.onclick=async()=>{try{await copyCraftText(instructions);status.textContent='Purchase instructions copied.';}catch{const text=el(box,'textarea');text.value=instructions;text.select();status.textContent='Copy the selected instructions with Ctrl+C.';}};
     }
     el(box,'small','Recipe association is by unique recipe-item name; confirm before buying. Break-even assumes these prices persist and every listed item sells. Currency costs are not converted to gold.');
   }
 }
 function renderGuide(){
   const old=$('guideCharacter').value;$('guideCharacter').replaceChildren();for(const c of (data.characters||[]).slice().sort(characterCompare))$('guideCharacter').add(new Option(c.name+' · '+c.realm,c.guid));if((data.characters||[]).some(c=>c.guid===old))$('guideCharacter').value=old;
   if(!$('guideProfession').options.length)for(const g of professionGuides.filter(g=>!['Cooking','Fishing','Archaeology','First Aid'].includes(g.name)))$('guideProfession').add(new Option(g.name,g.name));
   const g=professionGuides.find(g=>g.name===$('guideProfession').value),c=(data.characters||[]).find(c=>c.guid===$('guideCharacter').value),out=$('guideBody');out.replaceChildren();if(!g||!c){el(out,'p','Import your character snapshots to price the guide.');return;}
   el(out,'h3',g.name+' · 1–100');const source=el(out,'p');const link=el(source,'a','WoW-Professions baseline guide');link.href=g.url;link.target='_blank';link.rel='noopener noreferrer';source.append(' · Reviewed '+(g.name==='Tailoring'?'2026-10-18':g.reviewed));
   if(g.name==='Tailoring'){renderTailoring(out,c);renderInvestments(out,g,c);return;}
   el(out,'p',`Start with ${g.trainer} in Silvermoon City. Learn new trainer recipes as their skill requirements are reached.`);
   renderProfession(out,c,g);
   renderInvestments(out,g,c);
 }
 $('guideCharacter').onchange=renderGuide;$('guideProfession').onchange=renderGuide;
 const previous=render;render=function(){previous();renderGuide();if(activeTab==='ready')renderReady()};renderGuide();
}

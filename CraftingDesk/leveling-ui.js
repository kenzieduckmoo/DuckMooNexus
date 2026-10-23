{
  const guidePanel=document.createElement('section');guidePanel.className='panel';guidePanel.id='levelingDesk';
  guidePanel.innerHTML=`<span class="eyebrow">Develop a profession</span><h2>Dynamic leveling guide</h2><p><a href="/DuckMooCapture-0.6.0.zip">Download DuckMoo Capture 0.6.0</a> to collect leveling observations and trainer/vendor visits passively.</p><p>Compare learned recipes at your recorded skill. Unlearned recipes and visits are research notes until learning is confirmed in a new import.</p><div class="daily-filters"><div><label for="levelCharacter">Leveling character</label><select id="levelCharacter"></select></div><div><label for="levelProfession">Leveling profession</label><select id="levelProfession"></select></div><div><label for="levelTarget">Target skill</label><input id="levelTarget" type="number" min="1" max="1000" step="1" value="100"></div></div><div id="levelSummary" role="status"></div><div id="levelRoadmap"></div><div id="levelChoices"></div><div id="levelLearning"></div><details><summary>Coverage and recipes to investigate</summary><div id="levelCoverage"></div><label for="levelLearnSearch">Find an unlearned recipe</label><input id="levelLearnSearch" placeholder="Recipe name"><div id="levelLearnSources"></div></details><details><summary>Trainer and recipe-vendor visits</summary><p>Visits belong to the selected character, across all professions. Only entries exposed by the in-game filters are captured. Purchase availability does not confirm that a recipe can be learned. Currency costs stay in their original units.</p><label for="levelOfferSearch">Find a visited offer</label><input id="levelOfferSearch" placeholder="Recipe, trainer or vendor"><div id="levelOffers"></div></details><p class="muted">Routes cover supported orange ranges and stop at missing evidence. Yellow/green crafts can fail to award skill. Stock is not reserved against your daily plan. Route costs exclude resale, training and unlock costs.</p>`;
  document.querySelector('section.workspace').before(guidePanel);
  const gold=n=>(n/10000).toLocaleString(undefined,{maximumFractionDigits:2})+' g';
  const clean=text=>String(text??'').replace(/\|c[0-9a-fA-F]{8}|\|r/g,'').replace(/\|H[^|]*\|h(.*?)\|h/g,'$1').replace(/\|[TA][^|]*\|[ta]/g,'');
  function paragraph(parent,text,tag='p'){const el=document.createElement(tag);el.textContent=text;parent.append(el);return el;}
  function chooseOptions(select,values){const old=select.value;select.replaceChildren();for(const [key,label]of values)select.add(new Option(label,key));if(values.some(([key])=>String(key)===old))select.value=old;}
  function download(parent,label,filename,text){const b=document.createElement('button');b.textContent=label;b.onclick=()=>{const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};parent.append(b);}
  function offerCard(parent,o){
    const card=document.createElement('div');card.className='daily-card';parent.append(card);
    paragraph(card,clean(o.name)+' — '+acquisitionStatus(o),'b');
    paragraph(card,`${o.kind==='trainer'?'Trainer':'Recipe vendor'}: ${o.npcName||'unknown'}${o.mapID?' · map '+o.mapID:''} · Observed ${date(o.observedAt)}`);
    const costs=[];if(Number.isFinite(o.price))costs.push(gold(o.price));
    for(const c of o.costs||[])costs.push(`${c.amount??'?'} × ${clean(c.name||c.link||'unknown payment')}`);
    paragraph(card,`Recorded price: ${costs.join(' + ')||'unknown'}${o.kind==='vendor'?' per purchase of '+(o.stackCount??'?')+' item(s)':''}${o.kind==='vendor'&&!o.costsComplete?' · Payment details incomplete':''}`);
    if(o.skill)paragraph(card,`Requires ${o.skill} ${o.requiredSkill??'?'}${o.hasSkill===false?' — unmet at visit':''}`);
    if(o.requiredLevel>1)paragraph(card,'Required character level: '+o.requiredLevel);
    for(const r of o.requirements||[])paragraph(card,`${clean(r.name)} — ${r.met===true?'met':r.met===false?'unmet':'unknown'} at visit`);
    if(o.description)paragraph(card,clean(o.description));
    if(o.tooltip?.length){const detail=document.createElement('details');paragraph(detail,'Recorded game tooltip','summary');for(const line of o.tooltip)paragraph(detail,clean(line));card.append(detail);}
    paragraph(card,o.recipeID?'Exact recipe identifier captured. Learning still requires a fresh profession import.':o.kind==='trainer'?'Trainer item links may be associated by a unique output item, name and profession match. Confirm the association before training.':'Vendor item has no confirmed crafting recipe link. Purchase availability does not prove learnability.','small');
  }
  function renderLearning(guide){
    const panel=$('levelLearning');panel.replaceChildren();
    if(!guide.character||guide.skill>=guide.target)return;
    paragraph(panel,'Recipes worth learning','h3');
    paragraph(panel,'Conditional trainer comparisons include the training fee once and the materials for one craft. Compare against a supported learned-recipe route to the same skill. Learning is not assumed until you train, save and import again.');
    const options=learningOpportunities(data,guide),ready=options.filter(o=>o.ready);
    paragraph(panel,`${ready.length} supported trainer comparisons · ${options.length-ready.length} recipes need more evidence`);
    for(const o of ready.slice(0,8)){
      const card=document.createElement('div');card.className='daily-card';panel.append(card);
      paragraph(card,o.record.name,'b');
      paragraph(card,`Train + one craft: ${gold(o.total)} material value · ${gold(o.buyCost)} in training and missing purchases · Up to ${o.choice.points} skill points.`);
      paragraph(card,o.savings===null?'No complete learned route supports a cost comparison for the same skill gain.':o.savings>0?`${gold(o.savings)} less than the supported learned route to skill ${guide.skill+o.choice.points}.`:`No saving on this first craft (${gold(-o.savings)} more than the supported learned route). Later crafts may change the comparison.`);
      paragraph(card,`${o.offer.npcName||'Trainer'} · Training ${gold(o.offer.price)} · ${o.match} · Visit ${date(o.offer.observedAt)}`);
      const shopping=o.choice.plan.rows.map(r=>({item:r.item,missing:r.missing,scope:r.price?.scope||guide.character.realm}));
      download(card,'Download learning checklist','DuckMoo-learning-checklist.txt',learningChecklist(guide,o,data.inventory?.names,data.inventory?.tiers)+'\n\n'+auctionatorImportText({requirementsKnown:true,shopping},data.inventory?.names,data.inventory?.tiers));
    }
    if(!ready.length)paragraph(panel,'No trainer recipe has enough current evidence for a cost comparison yet. Check the reasons below; vendor and drop recipes remain research options.');
    const gaps=document.createElement('details');paragraph(gaps,'What is missing?','summary');
    const counts=new Map();for(const o of options.filter(o=>!o.ready))counts.set(o.reason,(counts.get(o.reason)||0)+1);
    for(const [reason,count]of counts)paragraph(gaps,`${count}: ${reason}`);
    const matched=options.filter(o=>!o.ready&&o.offer).slice(0,20);
    for(const o of matched)paragraph(gaps,`${o.record.name}: ${o.reason}${o.offer.requiredSkill?' · Requires '+o.offer.skill+' '+o.offer.requiredSkill:''} · ${o.offer.npcName||'trainer'}`);
    panel.append(gaps);
  }
  function renderLeveling(){
    chooseOptions($('levelCharacter'),(data.characters||[]).map(c=>[c.guid,c.name+' · '+c.realm]));
    const character=(data.characters||[]).find(c=>c.guid===$('levelCharacter').value);
    const professions=new Map((character?.professions||[]).map(p=>[p.id,p.name]));
    for(const r of data.catalog||[])if(r.guid===character?.guid)professions.set(r.profession.professionID,r.profession.professionName);
    chooseOptions($('levelProfession'),[...professions].sort((a,b)=>Number(b[1]?.includes('Midnight'))-Number(a[1]?.includes('Midnight'))||String(a[1]).localeCompare(String(b[1]))));
    const guide=levelingGuide(data,character?.guid,Number($('levelProfession').value),Number($('levelTarget').value));
    $('levelSummary').textContent=`Recorded skill: ${guide.skill??'unknown'} / ${guide.cap??'unknown'} · Target: ${guide.target}. ${guide.message}`;
    const route=levelingRoadmap(data,guide),road=$('levelRoadmap');road.replaceChildren();
    if(route.steps.length){
      paragraph(road,`Supported route: ${route.start} → ${route.reached} of ${route.target}`,'h3');
      paragraph(road,`${route.steps.length} crafts · Material value ${gold(route.materialCost)} · Buy missing ${gold(route.buyCost)}. ${route.complete?'Target covered by recorded orange ranges.':'Route stops here: the next orange skill range is not recorded.'} Cheapest by full material value among supported paths, excluding resale and learning costs.`);
      const steps=document.createElement('ol');for(const step of route.steps)paragraph(steps,`${step.from} → ${step.to}: ${step.choice.record.name} · orange observed at ${step.reference.rank} on ${step.reference.character}`,'li');road.append(steps);
      paragraph(road,'Orange at a higher observed rank is a range estimate. Cross-character comparisons require matching game build, profession and skill modifier. Verify recipe color and skill as you go; new imports recalculate the route.');
      download(road,'Download route and shopping list','DuckMoo-leveling-route.txt',levelingRoadmapText(guide,route,data.inventory?.names,data.inventory?.tiers)+'\n\n'+auctionatorImportText({requirementsKnown:true,shopping:route.shopping},data.inventory?.names,data.inventory?.tiers));
    }else if(guide.skill<guide.target)paragraph(road,'No orange route is supported yet. Review the next-craft alternatives and recipe sources below.');
    $('levelChoices').replaceChildren();
    for(const [index,choice]of guide.choices.slice(0,8).entries()){
      const r=choice.record,row=document.createElement('div');row.className='daily-card';
      paragraph(row,(index===0?'Suggested next craft: ':'')+r.name,'b');
      paragraph(row,`${choice.guaranteed?'Orange at recorded skill':'Chance-based: '+(r.relativeDifficulty===1?'yellow':'green')} · Up to ${choice.points} skill points. Material value ${gold(choice.plan.materialCost)} / craft · Buy missing ${gold(choice.plan.buyCost)}. ${gold(choice.costPerPoint)} per ${choice.guaranteed?'recorded':'potential'} skill point${choice.guaranteed?'':' — failed skill-ups cost extra'}`);
      for(const x of choice.plan.rows)paragraph(row,`${x.needed} × ${qualityLabel(x.item,data.inventory?.names,data.inventory?.tiers)} (buy ${x.missing})`);
      paragraph(row,`Observed ${date(r.observedAt)}${r.cooldownCaptured?'':' · Check cooldown availability in-game'}`,'small');
      const shopping=choice.plan.rows.map(r=>({item:r.item,missing:r.missing,scope:r.price?.scope||character.realm}));
      download(row,'Download next-step checklist','DuckMoo-leveling-next-step.txt',levelingText(guide,choice,data.inventory?.names,data.inventory?.tiers)+'\n\n'+auctionatorImportText({requirementsKnown:true,shopping},data.inventory?.names,data.inventory?.tiers));
      $('levelChoices').append(row);
    }
    renderLearning(guide);
    $('levelCoverage').textContent=`${guide.catalogCount} catalog recipes; ${guide.choices.length} supported skill-up choices. ${Object.entries(guide.excluded).map(([reason,count])=>count+' '+reason.toLowerCase()).join('; ')}. Unlearned recipes are not included in route costs. Source text is a clue, not proof that requirements are met.`;
    $('levelLearnSources').replaceChildren();
    const locked=guide.locked.filter(r=>r.name?.toLowerCase().includes($('levelLearnSearch').value.toLowerCase()));
    paragraph($('levelLearnSources'),`${locked.length} matches · showing up to 30`);
    for(const r of locked.slice(0,30)){
      paragraph($('levelLearnSources'),r.name+' — '+(r.sourceText?clean(r.sourceText)+' (observed '+date(r.sourceObservedAt)+')':'Source not captured. Open this profession with Capture 0.6.0, save and import.'));
      for(const o of recipeOffers(data,r))offerCard($('levelLearnSources'),o);
    }
    $('levelOffers').replaceChildren();
    const q=$('levelOfferSearch').value.toLowerCase();
    const offers=(data.acquisitionOffers||[]).filter(o=>o.guid===character?.guid&&((o.name||'')+' '+(o.npcName||'')).toLowerCase().includes(q)).sort((a,b)=>b.observedAt-a.observedAt);
    paragraph($('levelOffers'),offers.length?`${offers.length} matching visits · showing up to 30`:'No matching visits recorded. With Capture 0.6.0 installed, open a trainer or recipe vendor, then reload/logout and import. Hidden or unvisited offers remain unknown.');
    for(const o of offers.slice(0,30))offerCard($('levelOffers'),o);
  }
  $('levelCharacter').onchange=()=>{$('levelProfession').replaceChildren();renderLeveling()};
  $('levelProfession').onchange=renderLeveling;
  for(const id of ['levelTarget','levelLearnSearch','levelOfferSearch'])$(id).oninput=renderLeveling;
  const prior=render;render=function(){prior();renderLeveling()};renderLeveling();
}

{

  let planned=[],completed=[],loaded=false,busy=false,undo=null,visibleEntries=[];

  const money=n=>n==null?'Unknown':(n/10000).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+' g';

  const panel=document.createElement('section');panel.className='panel daily-desk';panel.id='dailyDesk';

  panel.innerHTML=`<span class="eyebrow">Plan your next session</span><h2>Daily crafting shortlist</h2><p>Compare captured operations and saved crafts, then reserve materials and concentration for a concrete plan. All values are estimates from your latest import.</p>

  <div class="daily-filters"><div><label for="dailyCharacter">Character</label><select id="dailyCharacter"><option value="">All characters</option></select></div><div><label for="dailyProfession">Profession</label><select id="dailyProfession"><option value="">All professions</option></select></div><div><label for="dailyMode">Crafting mode</label><select id="dailyMode"><option value="">Both modes</option><option value="with">With concentration</option><option value="without">Without concentration</option></select></div><div><label for="dailySort">Rank by</label><select id="dailySort"><option value="profit">Profit per craft</option><option value="incremental">Extra profit per concentration point</option></select></div></div>

  <div class="daily-filters"><div><label for="dailySearch">Find a craft</label><input id="dailySearch" placeholder="Recipe or character"></div><div><label for="dailyAge">Outcome observation age</label><select id="dailyAge"><option value="24">Within 24 hours</option><option value="72">Within 3 days</option><option value="0">Any age</option></select></div><div><label for="dailyFee">Selling fee assumption (%)</label><input id="dailyFee" type="number" min="0" max="99.99" step="0.01" value="5"></div><div><label for="dailyLimit">Suggestion limit per craft</label><input id="dailyLimit" type="number" min="1" max="10000" step="1" value="10"></div></div>

  <div class="daily-filters"><div><label for="dailyMargin">Minimum profit / material cost (%)</label><input id="dailyMargin" type="number" min="0" step="1" value="15"></div><div><label for="dailySaleRate">Minimum TSM sale rate</label><input id="dailySaleRate" type="number" min="0" max="1" step="0.01" value="0.15"></div><div><label for="dailySold">Minimum regional daily sold</label><input id="dailySold" type="number" min="0" step="0.01" value="0"></div></div><p class="muted">Profit percentage = profit after selling fee / full material value. Missing sales data fails an enabled sales filter. Daily sold is regional activity, not your expected sales; use it to judge batch sizes.</p><div class="daily-toggles"><label><input id="dailyGroup" type="checkbox" checked> Show the best setup per character, recipe and mode</label><label><input id="dailyPositive" type="checkbox" checked> Positive estimated profit only</label><label><input id="dailyReady" type="checkbox" checked> Enough concentration for one craft</label></div>

  <p><button id="suggestDaily">Add concentration suggestions</button> <button id="refreshDaily">Refresh estimates</button></p><p class="muted">Suggestions maximize estimated total profit among the filtered setups within each projected concentration pool and your craft limit. Purchases are allowed; your share of sales demand, crafting bonuses, cooldowns, and unlock requirements are not modeled. This is a shortlist of recorded choices, not every possible craft.</p>

  <div id="dailyStatus" role="status"></div><div class="daily-columns"><div><h3>Shortlist</h3><p id="dailyMatchCount"></p><div id="dailyResults"></div></div><div><h3>Your plan</h3><p id="dailyTotals"></p><div id="dailyWarnings" role="status"></div><div id="dailyQueue"></div><div id="dailyPools"></div><div id="dailyDemand"></div><p><button id="undoDaily" disabled>Undo last plan change</button> <button id="exportDaily">Download checklist</button></p></div></div>

  <details id="dailyShopping" open><summary>Combined shopping list</summary><p>Stock is allocated once across this plan. Bound items stay with their owner; transferable and warband stock can be shared. Realm-priced shopping rows remain separate.</p><div id="dailyShoppingRows"></div></details><details><summary>Where to collect your materials</summary><div id="dailyTransfers"></div></details><p class="muted">This is a saved plan, not an in-game reservation or crafting command. After crafting or spending concentration, save and import fresh game snapshots before planning another batch.</p>`;

  document.querySelector('section.workspace').before(panel);

  const itemLabel=item=>qualityLabel(item,data.inventory?.names||{},data.inventory?.tiers||{});
  const history=document.createElement('details');history.innerHTML='<summary>Completed crafts</summary><div id="dailyCompleted"></div><button id="clearCompleted">Clear completed history</button>';panel.append(history);

  function controls(){panel.querySelectorAll('button').forEach(b=>b.disabled=busy||!loaded);$('undoDaily').disabled=busy||!loaded||!undo;}

  async function commit(next,keepUndo=true,nextCompleted=completed){

    if(busy||!loaded)return;

    busy=true;controls();$('dailyStatus').textContent='Saving your plan…';

    try{

      const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({version:1,setups:next,completed:nextCompleted})});

      const body=await response.json();if(!response.ok)throw Error(body.error||'Could not save plan');

      if(keepUndo)undo={setups:planned,completed};else undo=null;

      planned=body.setups;completed=body.completed||[];$('dailyStatus').textContent='Plan saved.';return true;

    }catch(e){$('dailyStatus').textContent=e.message;return false;}

    finally{busy=false;renderDaily();}

  }

  function addToPlan(additions){
    if(completionNeedsImport(data,completed))throw Error('Save in WoW and import updated inventory and concentration before adding more crafts.');

    const next=planned.map(s=>({...s,selections:{...s.selections}}));

    for(const addition of additions){

      const match=next.find(s=>planKey(s)===planKey(addition));

      if(match){if(match.count+addition.count>10000)throw Error('A setup cannot exceed 10,000 crafts.');match.count+=addition.count;}

      else next.push({...addition,id:crypto.randomUUID()});

    }

    if(next.length>200)throw Error('Keep at most 200 setups in the plan.');

    return next;

  }

  function filterOptions(){return {owner:$('dailyCharacter').value,profession:$('dailyProfession').value,search:$('dailySearch').value,mode:$('dailyMode').value,positive:$('dailyPositive').checked,ready:$('dailyReady').checked,maxAge:Number($('dailyAge').value),minMargin:Number($('dailyMargin').value),minSaleRate:Number($('dailySaleRate').value),minDailySold:Number($('dailySold').value)};}

  function updateOptions(id,values,label){

    const select=$(id),old=select.value;select.replaceChildren(new Option(label,''));

    for(const [value,text] of values)select.add(new Option(text,value));

    if(values.some(([value])=>value===old))select.value=old;

  }

  window.getDailyPlanningContext=()=>({options:filterOptions(),planned,completed,loaded});
  window.addReadyConcentrationBatch=async setup=>{if(!loaded||busy)throw Error('Wait for the saved plan to load.');const next=addToPlan([setup]);const checked=evaluateDailyPlan(data,next);if(checked.issues.length)throw Error(checked.issues.join(' '));if(!await commit(next))throw Error($('dailyStatus').textContent||'Could not save plan.');};
  function renderDaily(){

    const now=Date.now()/1000,fee=Number($('dailyFee').value);

    const candidates=dailyCandidates(data,window.getSavedCraftingSetups?.()||[],fee,now);

    updateOptions('dailyCharacter',[...new Map(candidates.map(e=>[e.owner,e.setup.crafterName+' · '+e.setup.realm])).entries()].sort((a,b)=>a[1].localeCompare(b[1])),'All characters');

    updateOptions('dailyProfession',[...new Set(candidates.map(e=>e.profession))].sort().map(x=>[x,x]),'All professions');

    const options=filterOptions();
    const bothModes=filterDaily(candidates,{...options,mode:''},now);
    const withoutCount=bothModes.filter(e=>e.setup.concentration===0).length;
    visibleEntries=filterDaily(candidates,options,now);
    $('suggestDaily').disabled=options.mode==='without';
    $('dailySort').disabled=options.mode==='without';
    if(options.mode==='without')$('dailySort').value='profit';

    const metric=e=>$('dailySort').value==='incremental'?(e.gain?.perPoint??-Infinity):(e.result.finance?.perCraft??-Infinity);

    visibleEntries.sort((a,b)=>metric(b)-metric(a)||a.setup.name.localeCompare(b.setup.name));

    const displayEntries=$('dailyGroup').checked?groupDaily(visibleEntries):visibleEntries;
    const target=$('dailyResults');target.replaceChildren();

    const validFee=$('dailyFee').value!==''&&Number.isFinite(fee)&&fee>=0&&fee<100&&['dailyMargin','dailySaleRate','dailySold'].every(id=>$(id).value!==''&&$(id).checkValidity());

    if(!validFee){visibleEntries=[];$('dailyMatchCount').textContent='Enter valid, nonnegative thresholds, a sale rate from 0 to 1, and a selling fee below 100%.';}

    else $('dailyMatchCount').textContent=`${visibleEntries.length} matching choices · ${displayEntries.length} displayed choices · showing up to 40. With your other filters: ${withoutCount} without concentration, ${bothModes.length-withoutCount} with concentration.`;

    if(validFee&&!visibleEntries.length){
      const modeEntries=filterDaily(candidates,{owner:options.owner,profession:options.profession,search:options.search,mode:options.mode},now);
      const positive=modeEntries.filter(e=>e.result.finance?.profit>0).length;
      target.textContent=`No crafts pass these filters. ${modeEntries.length} recorded choices match this character, profession, search and mode; ${positive} have positive estimated profit before margin, sales, age and availability filters. Refresh estimates recalculates the existing import; use Import game snapshots to load newly saved recipe scans. Changing filters does not change Your plan. Add qualifying crafts using Add one craft.`;
    }

    for(const entry of (validFee?displayEntries:[]).slice(0,40)){

      const s=entry.setup,r=entry.result,row=document.createElement('div');row.className='daily-card';

      row.innerHTML=`<b>${esc(s.name)}</b>${entry.alternativeCount?'<p class="muted">'+entry.alternativeCount+' other matching choices grouped here. Uncheck the grouping option to compare them.</p>':''}<p>${esc(s.crafterName)} · ${esc(s.realm)} · ${esc(entry.profession)}<br>${s.concentration?s.concentration+' concentration per craft':'Without concentration'} · ${s.quantity} items per craft</p><strong>${money(r.finance?.perCraft)} estimated profit / craft</strong><p>${entry.margin==null?'Unknown':entry.margin.toFixed(1)+'%'} profit / cost · TSM sale rate ${entry.sales?.saleRate?.toFixed(3)??'Unknown'}<br>Regional daily sold: ${entry.sales?.dailySold?.toLocaleString()??'Unknown'}<br><small>${esc(entry.salesBasis)} · Sales data ${esc(date(entry.sales?.at))}</small></p><p>${s.concentration?r.budget?'~'+Math.floor(r.budget.available)+' concentration projected; '+r.budget.crafts+' crafts before plan reservations':'Concentration availability unknown':'Set your desired quantity in the plan.'}${entry.gain?'<br>'+money(entry.gain.perPoint)+' extra profit per concentration point':''}</p><small>Outcome ${esc(date(entry.observedAt))}<br>${s.salePrice==null?'Output price '+esc(date(r.price?.at))+' · '+esc(r.price?.source||'Unknown source'):'Manual sale-price assumption'}${entry.recipe?.capture?.source==='schematic-preview'?' · Background reagent preview':entry.recipe?.capture?.source==='recipe-scan'?' · Recipe scan'+(entry.recipe.capture.scanLimited?' (combination limit reached)':''):''}</small>${r.error?'<p>'+esc(r.error)+'</p>':''}`;

      const actions=document.createElement('p'),add=document.createElement('button');add.textContent='Add one craft';

      add.onclick=()=>{try{if(r.error||r.plan.unresolved.length)throw Error('Complete or refresh this setup first.');void commit(addToPlan([{...s,count:1}]))}catch(e){$('dailyStatus').textContent=e.message}};

      const inspect=document.createElement('button');inspect.textContent='Inspect';inspect.style.marginLeft='8px';inspect.onclick=()=>{try{window.restoreCraftingSetup(s);$('detail').scrollIntoView({behavior:'smooth'})}catch(e){$('dailyStatus').textContent=e.message}};

      actions.append(add,inspect);row.append(actions);target.append(row);

    }

    renderPlan(now);controls();if(!validFee||options.mode==='without'||completionNeedsImport(data,completed))$('suggestDaily').disabled=true;

  }

  function renderPlan(now){

    const plan=evaluateDailyPlan(data,planned,now);

    $('dailyTotals').textContent=planned.length?`${planned.reduce((n,s)=>n+s.count,0)} crafts · Estimated profit ${money(plan.profit)} · Buy missing ${money(plan.buyCost)}`:'No crafts planned yet.';

    $('dailyWarnings').replaceChildren();
    if(completionNeedsImport(data,completed)){const p=document.createElement('p');p.className='notice';p.textContent='Crafts marked completed. Remaining shopping and concentration estimates still use your earlier game snapshot. Reload/logout in WoW, then Import game snapshots before buying or planning more. New suggestions are paused.';$('dailyWarnings').append(p);}
    $('dailyCompleted').textContent=completed.map(s=>s.crafterName+' · '+s.count+' × '+s.name+' · '+date(s.completedAt)).join(' / ')||'No crafts marked completed.';
    if(completed.length&&!completionNeedsImport(data,completed)){const p=document.createElement('p');p.textContent='Newer inventory and concentration files imported. Remaining estimates have been recalculated; review the shopping list and any warnings below. Completion history records your checkmarks, not verified crafting or sales.';$('dailyWarnings').append(p);}

    for(const issue of plan.issues){const p=document.createElement('p');p.className='notice';p.textContent=issue;$('dailyWarnings').append(p);}

    const target=$('dailyQueue');target.replaceChildren();

    for(const [index,s] of planned.entries()){

      const row=document.createElement('div');row.className='daily-card';

      row.innerHTML=`<b>${esc(s.name)}</b><p>${esc(s.crafterName)} · ${esc(s.realm)} · ${s.concentration?'With':'Without'} concentration<br><small>${s.fee}% saved fee assumption</small></p><label for="planCount${index}">Crafts for ${esc(s.crafterName)} — ${esc(s.name)}</label><input id="planCount${index}" type="number" min="1" max="10000" step="1" value="${s.count}">`;
      const ingredients=document.createElement('p');ingredients.textContent=(plan.lines[index]?.result.plan?.rows||[]).map(r=>r.needed+' × '+itemLabel(r.item)).join(' / ');row.append(ingredients);

      const actions=document.createElement('p'),update=document.createElement('button');update.textContent='Update quantity';

      update.onclick=()=>{const count=Number($('planCount'+index).value);if(!Number.isInteger(count)||count<1||count>10000){$('dailyStatus').textContent='Enter a whole number from 1 to 10,000.';return;}void commit(planned.map((item,i)=>i===index?{...item,count}:item));};

      const remove=document.createElement('button');remove.textContent='Remove from plan';remove.style.marginLeft='8px';remove.onclick=()=>void commit(planned.filter((_,i)=>i!==index));const done=document.createElement('button');done.textContent='Mark quantity completed';done.onclick=()=>{try{const next=completePlanCrafts(planned,completed,s.id,Number($('planCount'+index).value));void commit(next.setups,true,next.completed);}catch(e){$('dailyStatus').textContent=e.message}};actions.append(update,done,remove);row.append(actions);target.append(row);

    }

    const outputs=new Map();
    for(const s of planned)outputs.set(s.output,(outputs.get(s.output)||0)+s.quantity*s.count);
    $('dailyDemand').innerHTML=[...outputs].map(([item,units])=>{
      const sales=data.market?.sales?.[item]||data.market?.sales?.[item.match(/^i:\d+/)?.[0]];
      return `<p><b>${esc(itemLabel(item))}</b><br>${units} items planned across all characters · ${sales?.dailySold?.toLocaleString()??'Unknown'} regional daily sold${sales?.dailySold>0?' · '+(units/sales.dailySold*100).toFixed(2)+'% of regional daily volume':''}</p>`;
    }).join('');
    $('dailyPools').innerHTML=plan.pools.map(p=>`<p><b>${esc(p.name)}</b><br>${p.required} concentration planned / ${p.available==null?'unknown':Math.floor(p.available)} projected</p>`).join('');

    $('dailyShoppingRows').innerHTML=(!plan.requirementsKnown?'<p class="notice">Partial list: resolve plan warnings before treating these quantities as complete.</p>':'')+plan.shopping.map(r=>`<div class="row"><div><b>${esc(itemLabel(r.item))}</b><br><small>Need ${r.needed} · Stock allocated ${r.used} · Buy ${r.missing}<br>${esc(r.scope)} · ${esc(r.forCharacters.join(', '))}<br>Price snapshot ${esc(date(r.at))}</small></div><b>${r.missing===0?money(0):money(r.price==null?null:r.price*r.missing)}</b></div>`).join('');

    $('dailyTransfers').innerHTML=plan.allocations.map(a=>`<p>${a.quantity} × ${esc(itemLabel(a.item))}<br><small>${esc(a.owner)} / ${esc(a.location)} → ${esc(a.crafter)} · ${esc(a.realm)}</small></p>`).join('')||'<p>No recorded stock allocated.</p>';

  }

  for(const id of ['dailyCharacter','dailyProfession','dailyMode','dailySort','dailyAge','dailyPositive','dailyReady','dailyGroup','dailyMargin','dailySaleRate','dailySold'])$(id).onchange=renderDaily;

  $('dailySearch').oninput=renderDaily;$('dailyFee').onchange=renderDaily;

  $('refreshDaily').onclick=renderDaily;

  $('suggestDaily').onclick=()=>{try{

    renderDaily();const additions=suggestConcentration(data,visibleEntries,planned,Number($('dailyLimit').value));

    if(!additions.length){$('dailyStatus').textContent='No additional profitable concentration crafts fit the filtered setups, remaining pools, and craft limit.';return;}

    void commit(addToPlan(additions));

  }catch(e){$('dailyStatus').textContent=e.message}};

  $('undoDaily').onclick=()=>{if(undo)void commit(undo.setups,false,undo.completed)};
  $('clearCompleted').onclick=()=>{if(completionNeedsImport(data,completed)){$('dailyStatus').textContent='Import updated game snapshots before clearing completed history.';return;}void commit(planned,true,[])};

  $('exportDaily').onclick=()=>{

    const plan=evaluateDailyPlan(data,planned);
    if(completionNeedsImport(data,completed)){plan.requirementsKnown=false;plan.issues.unshift('Inventory and concentration predate completed crafts. Save in WoW and import before using shopping quantities.');}
    const text=dailyPlanText(plan,data.inventory?.names||{},data.inventory?.tiers||{})+'\n\nCompleted (marked by you; not verified sales):\n'+completed.map(s=>s.crafterName+': '+s.count+' x '+s.name+' · '+date(s.completedAt)).join('\n'),blob=new Blob([text],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='DuckMoo-crafting-plan.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);

  };

  document.addEventListener('crafting-setups-updated',renderDaily);

  const previousRender=render;render=function(){previousRender();renderDaily()};

  fetch('/api/plan').then(async response=>{if(!response.ok)throw Error('Restart Crafting Desk to enable daily plans.');const body=await response.json();if(body.version!==1||!Array.isArray(body.setups))throw Error('Unsupported daily plan file');planned=body.setups;completed=body.completed||[];loaded=true;renderDaily();}).catch(e=>{$('dailyStatus').textContent=e.message;controls();});

  renderDaily();

}


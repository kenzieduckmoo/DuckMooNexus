/* Outcomes are entered by the user; no quality or bonus simulation is implied. */
const craftingMath=typeof module!=='undefined'?require('./material-ui.js'):{materialPlan,quote};
function concentrationBudget(record, perCraft, count, now=Date.now()/1000){
  if(perCraft===0)return {available:null,crafts:null,wait:0,overCap:false};
  if(!record||!Number.isFinite(record.amount)||!Number.isFinite(record.max)||!record.observedAt)return null;
  const rate=record.secondsPerPoint;
  if(record.amount<record.max&&!(rate>0))return null;
  const available=Math.max(0,Math.min(record.max,record.amount+(rate>0?Math.max(0,now-record.observedAt)/rate:0)));
  const need=perCraft*count;
  return {available,crafts:Math.floor(available/perCraft),wait:need<=available?0:rate>0?(need-available)*rate:null,overCap:need>record.max};
}
function financialEstimate(materialCost,quantity,count,unitPrice,fee,concentration){
  const net=unitPrice==null?null:unitPrice*quantity*count*(1-fee/100);
  const profit=materialCost==null||net==null?null:net-materialCost;
  return {net,profit,perCraft:profit==null?null:profit/count,breakEven:materialCost==null?null:materialCost/(quantity*count*(1-fee/100)),goldPerPoint:profit==null||!concentration?null:profit/(count*concentration)};
}
const evaluationIndexes=new WeakMap();
function buildEvaluationIndex(snapshot){
  const old=evaluationIndexes.get(snapshot);
  if(old&&old.recipeSource===snapshot.recipes&&old.length===snapshot.recipes?.length&&old.characterSource===snapshot.characters)return old;
  const index={recipeSource:snapshot.recipes,length:snapshot.recipes?.length,characterSource:snapshot.characters,
    recipes:new Map((snapshot.recipes||[]).map(r=>[JSON.stringify([r.key,r.scope]),r])),characters:new Map((snapshot.characters||[]).map(c=>[c.guid,c]))};
  evaluationIndexes.set(snapshot,index);return index;
}
function evaluateSetup(snapshot,setup,now,index){
  const recipe=index?index.recipes.get(JSON.stringify([setup.recipeKey,setup.scope])):(snapshot.recipes||[]).find(r=>r.key===setup.recipeKey&&r.scope===setup.scope);
  if(!recipe)return {error:'Recipe is missing from the latest import.'};
  if(recipe.capture&&setup.capturedAt!==recipe.capture.observedAt)return {error:'This operation was recaptured. Open its recipe and save a fresh setup.'};
  if(JSON.stringify(Object.entries(recipe.materials).sort())!==setup.materialSignature)return {error:'Recipe requirements changed. Create a fresh setup.'};
  const crafter=recipe.crafters.find(c=>c.name===setup.crafterName&&c.realm===setup.realm);
  if(!crafter)return {error:'Crafter is missing from this recipe record.'};
  const plan=craftingMath.materialPlan(recipe,setup.selections,setup.count,crafter,snapshot.inventory||{},snapshot.market||{});
  const price=recipe.capture?.manualSalePrice?null:craftingMath.quote(snapshot.market,setup.output,crafter.realm);
  const unitPrice=setup.salePrice??price?.price??null;
  const character=index?index.characters.get(crafter.guid):(snapshot.characters||[]).find(c=>c.guid===crafter.guid);
  const profession=character?.professions.find(p=>p.id===setup.professionId);
  return {plan,price,unitPrice,finance:financialEstimate(plan.materialCost,setup.quantity,setup.count,unitPrice,setup.fee,setup.concentration),budget:concentrationBudget(profession?.concentration,setup.concentration,setup.count,now),profession};
}
function concentrationGain(entry,entries){
  if(!entry.setup.concentration||entry.result.finance?.perCraft==null)return null;
  const s=entry.setup;
  const candidates=entries.filter(e=>e.setup.concentration===0&&e.setup.crafterName===s.crafterName&&e.setup.realm===s.realm&&e.setup.recipeKey.split(':q')[0]===s.recipeKey.split(':q')[0]&&e.result.finance?.perCraft!=null);
  candidates.sort((a,b)=>b.result.finance.perCraft-a.result.finance.perCraft);
  if(!candidates.length)return null;
  const baseline=candidates[0],extra=entry.result.finance.perCraft-baseline.result.finance.perCraft;
  return {baseline:baseline.setup.name,extra,perPoint:extra/s.concentration};
}
function assignConcentrationGains(entries){
  const key=s=>JSON.stringify([s.crafterName,s.realm,s.recipeKey.split(':q')[0]]),best=new Map();
  for(const e of entries)if(e.setup.concentration===0&&e.result.finance?.perCraft!=null){
    const k=key(e.setup),prior=best.get(k);if(!prior||e.result.finance.perCraft>prior.result.finance.perCraft)best.set(k,e);
  }
  for(const e of entries){
    const baseline=best.get(key(e.setup));e.gain=null;
    if(e.setup.concentration>0&&e.result.finance?.perCraft!=null&&baseline){const extra=e.result.finance.perCraft-baseline.result.finance.perCraft;e.gain={baseline:baseline.setup.name,extra,perPoint:extra/e.setup.concentration};}
  }
  return entries;
}
function setupFromCapture(recipe,fee=5){
  const c=recipe.crafters[0],capture=recipe.capture;
  return {id:recipe.key,name:recipe.name,recipeKey:recipe.key,scope:recipe.scope,crafterName:c.name,realm:c.realm,
    selections:Object.fromEntries(Object.keys(recipe.materials).map(k=>[k,k])),count:1,
    materialSignature:JSON.stringify(Object.entries(recipe.materials).sort()),output:recipe.output,quantity:recipe.quantity,
    fee,salePrice:null,concentration:capture.concentration,professionId:capture.skillLineID,
    capturedAt:capture.observedAt,savedAt:new Date(capture.observedAt*1000).toISOString()};
}
if(typeof module!=='undefined')module.exports={buildEvaluationIndex,assignConcentrationGains,financialEstimate,concentrationBudget,evaluateSetup,concentrationGain,setupFromCapture};
if(typeof document!=='undefined'){
  let setups=[],ready=false,saveBusy=false,context=null;
  window.getSavedCraftingSetups=()=>setups;
  const gold=value=>value==null?'Unknown':(value/10000).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+' g';
  const board=document.createElement('section');board.className='panel';board.style.marginTop='24px';board.innerHTML='<span class="eyebrow">Your crafting scenarios</span><h2>Saved crafts</h2><p>Save a character’s reagent choices and an outcome checked in-game. Saved crafts use the latest imported prices and stock. They are alternatives, not a combined production queue.</p><div id="setupStatus" role="status"></div><div id="setupList"></div>';
  document.querySelector('footer').before(board);
  const capturedBoard=document.createElement('details');capturedBoard.className='panel';capturedBoard.style.marginTop='24px';
  capturedBoard.innerHTML='<summary>All captured choices — reference view</summary><p>This unfiltered reference includes losing and incomplete setups. Use the Daily crafting shortlist above for opportunities that pass your profit and sale-rate filters. Negative profit here means the recorded setup costs more to craft than its estimated sale proceeds. Materials and concentration are not reserved across these rows.</p><label for="captureFee">Selling fee assumption (%)</label><input id="captureFee" type="number" min="0" max="99.99" step="0.01" value="5"><label for="captureSort">Rank captured choices by</label><select id="captureSort"><option value="perCraft">Estimated profit per craft</option><option value="incremental">Extra profit per concentration point</option></select><div id="capturedList"></div>';
  board.before(capturedBoard);$('captureFee').oninput=renderCaptured;$('captureSort').onchange=renderCaptured;
  const catalogPanel=document.createElement('details');catalogPanel.innerHTML='<summary>Passively collected recipe catalog</summary><p>Recipes can be recorded without owning their materials. A catalog record is not a complete quality or profit calculation.</p><label for="catalogSearch">Find a catalog recipe or character</label><input id="catalogSearch" placeholder="Recipe or character name"><div id="catalogList"></div>';capturedBoard.append(catalogPanel);
  $('catalogSearch').oninput=renderCatalog;
  const scanPanel=document.createElement('details');scanPanel.open=true;scanPanel.innerHTML='<summary>Recipe scan coverage</summary><div id="scanCoverage"></div>';catalogPanel.before(scanPanel);
  function renderCatalog(){
    $('scanCoverage').innerHTML=(data.scanCoverage||[]).map(s=>`<p><b>${esc(s.character)} · ${esc(s.realm)} · ${esc((data.characters||[]).find(c=>c.name===s.character&&c.realm===s.realm)?.professions?.find(p=>p.id===s.professionID)?.name||'Profession '+s.professionID)}</b><br>${esc(s.state)} at last game save · ${s.checked} / ${s.total} catalog entries checked<br>${s.outcomes} outcomes recorded · ${s.skipped} outside scope or unavailable · ${s.limited} recipes reached the combination limit · ${s.unavailable} outcome queries unavailable<br><small>Observed ${esc(date(s.observedAt))}; this is a saved snapshot, not live progress.</small></p>`).join('')||'<p>No recipe scan imported yet. Install <a href="/DuckMooCapture-0.6.0.zip">DuckMoo Capture 0.6.0</a>, open a profession, then reload/logout and import. The scanner compares up to 256 required-reagent combinations per recipe in the active expansion. Optional reagents and bonus-proc profit are not modeled. The scanner needs live comparison against CraftSim.</p>';

    const search=$('catalogSearch').value.toLowerCase();
    const rows=(data.catalog||[]).filter(r=>(r.name+' '+r.character+' '+r.realm).toLowerCase().includes(search));
    $('catalogList').innerHTML=`<p>${rows.length} recipe records · showing up to 40</p>`+rows.slice(0,40).map(r=>`<div class="row"><div><b>${esc(r.name)}</b><br><small>${esc(r.character)} · ${esc(r.realm)} · ${r.learned===true?'Learned':r.learned===false?'Not learned':'Learning status unknown'}<br>Observed ${esc(date(r.observedAt))} · ${r.schematic?'Reagents recorded':'Reagent data unavailable'}</small></div></div>`).join('');
    const diagnostics=document.createElement('details');diagnostics.innerHTML='<summary>Latest capture status by character</summary>'+(data.captureDiagnostics||[]).map(d=>`<p><b>${esc(d.character)} · ${esc(d.realm)}</b><br>${esc(d.text)}<br><small>${esc(date(d.observedAt))}</small></p>`).join('');$('catalogList').append(diagnostics);
  }
  const sortLabel=document.createElement('label');sortLabel.htmlFor='setupSort';sortLabel.textContent='Rank saved crafts by';
  const sort=document.createElement('select');sort.id='setupSort';sort.add(new Option('Estimated profit per craft','perCraft'));sort.add(new Option('Estimated profit per concentration point','goldPerPoint'));sort.onchange=renderSaved;
  $('setupList').before(sortLabel,sort);
  async function persist(next){
    if(!ready||saveBusy)throw Error('Saved crafts are not ready. Please try again.');
    saveBusy=true;
    try{
      const response=await fetch('/api/setups',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({version:1,setups:next})});
      const body=await response.json();if(!response.ok)throw Error(body.error||'Could not save setups');
      setups=body.setups;renderSaved();
    }finally{saveBusy=false;}
  }
  function budgetText(result,setup){
    if(!setup.concentration)return 'Without concentration';
    if(!result.budget)return 'Concentration availability unknown';
    const b=result.budget;
    return `~${Math.floor(b.available)} concentration projected · ${b.crafts} crafts available now`+(b.overCap?' · Batch exceeds the concentration cap; split it over time':b.wait>0?` · ~${(b.wait/3600).toFixed(1)} hours to afford this batch`:'');
  }
  function renderSaved(){
    if(!$('setupList'))return;
    document.dispatchEvent(new Event('crafting-setups-updated'));
    renderCaptured();
    const ranked=setups.map(setup=>({setup,result:evaluateSetup(data,setup)}));
    const metric=$('setupSort').value;
    ranked.sort((a,b)=>(b.result.finance?.[metric]??-Infinity)-(a.result.finance?.[metric]??-Infinity));
    $('setupList').replaceChildren();
    if(!ranked.length)$('setupList').textContent='Open a recipe to save your first setup.';
    for(const {setup,result} of ranked){
      const row=document.createElement('div');row.className='row';
      row.innerHTML=`<div><b>${esc(setup.name)}</b><br><small>${esc(setup.crafterName)} · ${esc(setup.realm)} · ${setup.count} crafts · ${setup.concentration?'With':'Without'} concentration<br>Outcome entered ${esc(new Date(setup.savedAt).toLocaleString())}</small>${result.error?`<p>${esc(result.error)}</p>`:`<p>Estimated profit ${gold(result.finance.profit)} · ${gold(result.finance.perCraft)} per craft<br>Buy missing ${gold(result.plan.buyCost)}${setup.concentration?'<br>Estimated profit per concentration point '+gold(result.finance.goldPerPoint):''}<br>${esc(budgetText(result,setup))}</p><small>${setup.salePrice==null?'Sale price from snapshot '+esc(date(result.price?.at)):'Manual sale price'} · ${setup.fee}% fee assumption · ${result.plan.unresolved.length?'Incomplete reagent choices':'Current imported material prices'}</small>`}</div>`;
      const actions=document.createElement('div');
      if(setup.concentration&&!result.error){
        const gain=concentrationGain({setup,result},ranked),explanation=document.createElement('p');
        explanation.textContent=gain?`Extra profit versus “${gain.baseline}”: ${gold(gain.extra)} per craft · ${gold(gain.perPoint)} per concentration point.`:'Save a no-concentration setup for this character and recipe to compare the extra profit from concentration.';
        row.firstElementChild.append(explanation);
      }
      const open=document.createElement('button');open.textContent='Open saved craft';open.style.marginBottom='8px';
      open.onclick=()=>{try{
        if(result.error)throw Error(result.error);
        window.restoreCraftingSetup(setup);
        $('setupName').value=setup.name;$('outcome').value=setup.output;$('saleFee').value=setup.fee;$('saleOverride').value=setup.salePrice==null?'':setup.salePrice/10000;
        $('useConcentration').checked=setup.concentration>0;$('useConcentration').onchange();$('concentrationCost').value=setup.concentration||'';$('concentrationProfession').value=setup.professionId||'';
        $('saveOutcome').textContent='Save as new saved craft';preview();$('detail').scrollIntoView({behavior:'smooth'});
      }catch(e){$('setupStatus').textContent=e.message}};
      const remove=document.createElement('button');remove.textContent='Remove';remove.onclick=async()=>{remove.disabled=true;try{await persist(setups.filter(s=>s.id!==setup.id));$('setupStatus').textContent='Saved craft removed.'}catch(e){$('setupStatus').textContent=e.message;remove.disabled=false}};
      actions.append(open,document.createElement('br'),remove);row.append(actions);$('setupList').append(row);
    }
  }
  function renderCaptured(){
    renderCatalog();
    const fee=Number($('captureFee').value),target=$('capturedList');target.replaceChildren();
    if($('captureFee').value===''||!Number.isFinite(fee)||fee<0||fee>=100){target.textContent='Enter a fee assumption from 0 to 99.99%.';return;}
    const index=buildEvaluationIndex(data);
    const entries=(data.recipes||[]).filter(r=>r.capture).map(recipe=>{const setup=setupFromCapture(recipe,fee);return {recipe,setup,result:evaluateSetup(data,setup,undefined,index)}});
    assignConcentrationGains(entries);
    const incremental=$('captureSort').value==='incremental';
    entries.sort((a,b)=>(incremental?(b.gain?.perPoint??-Infinity):(b.result.finance?.perCraft??-Infinity))-(incremental?(a.gain?.perPoint??-Infinity):(a.result.finance?.perCraft??-Infinity)));
    if(!entries.length){target.innerHTML='<p>No crafting operations imported yet. Install <a href="/DuckMooCapture-0.2.0.zip">DuckMoo Capture 0.2.0</a>, browse professions normally, then reload WoW to save and import here. Recipe catalogs and supported operation previews are collected automatically; /dmcap is optional. Passive capture is mock-tested; live-client validation is pending.</p>';return;}
    const summary=document.createElement('p');summary.textContent=`${entries.length} captured outcomes · showing up to 20 · ${fee}% fee assumption`;target.append(summary);
    for(const entry of entries.slice(0,20)){
      const {recipe,setup,result,gain}=entry,row=document.createElement('div');row.className='row';
      row.innerHTML=`<div><b>${esc(recipe.name)} · ${esc(setup.crafterName)}</b><br><small>${esc(setup.realm)} · Quality ${esc(recipe.capture.quality)} · ${setup.concentration?'With':'Without'} concentration · Captured ${esc(date(setup.capturedAt))}</small><p>${result.error?esc(result.error):'Estimated profit '+gold(result.finance.profit)+' per craft · Buy missing '+gold(result.plan.buyCost)+'<br>'+esc(budgetText(result,setup))}${gain?'<br>Extra profit per concentration point '+gold(gain.perPoint):''}</p>${recipe.capture.manualSalePrice?'<small>Exact output sale price needs manual entry; generic realm prices are not substituted.</small>':''}</div>`;
      const open=document.createElement('button');open.textContent='Open captured craft';open.onclick=()=>{showRecipe(recipe);$('saleFee').value=fee;$('detail').scrollIntoView({behavior:'smooth'})};row.append(open);target.append(row);
      const origin=document.createElement('small');origin.textContent=recipe.capture.source==='schematic-preview'?`Background reagent preset ${recipe.capture.preset}; queried without requiring inventory. Sampled configuration, not an exhaustive optimum.`:recipe.capture.source==='recipe-scan'?'Background recipe scan'+(recipe.capture.scanLimited?'; combination limit reached.':'; required reagent combinations checked.'):'Captured selected reagent configuration.';row.firstElementChild.append(origin);
    }
  }
  function readSetup(){
    const {recipe,crafter,selections,count}=context;
    const form=$('outcomeForm');if(!form.reportValidity())return null;
    const output=$('outcome').value;
    const selected=(data.recipes||[]).find(r=>r.output===output&&r.key.split(':q')[0]===recipe.key.split(':q')[0]);
    if(!selected)throw Error('Choose a recorded output.');
    return {id:crypto.randomUUID(),name:$('setupName').value.trim()||recipe.name,recipeKey:recipe.key,scope:recipe.scope,crafterName:crafter.name,realm:crafter.realm,selections:{...selections},count,materialSignature:JSON.stringify(Object.entries(recipe.materials).sort()),output,quantity:recipe.capture?recipe.quantity:selected.quantity,fee:Number($('saleFee').value),salePrice:$('saleOverride').value===''?null:Math.round(Number($('saleOverride').value)*10000),concentration:$('useConcentration').checked?Number($('concentrationCost').value):0,professionId:Number($('concentrationProfession').value)||null,capturedAt:recipe.capture?.observedAt??null,savedAt:new Date().toISOString()};
  }
  function preview(){
    try{
      const setup=readSetup();if(!setup)return;
      const result=evaluateSetup(data,setup);
      if(result.error){$('outcomeResult').textContent=result.error;return;}
      const f=result.finance;
      $('outcomeResult').innerHTML=`<div class="row"><span>Sale proceeds after assumed fee</span><b>${gold(f.net)}</b></div><div class="row"><span>Estimated profit after full material value</span><b>${gold(f.profit)}</b></div><div class="row"><span>Break-even sale price per item</span><b>${gold(f.breakEven)}</b></div><p>${esc(budgetText(result,setup))}${setup.concentration?'<br>Estimated profit per concentration point '+gold(f.goldPerPoint):''}</p><small>${setup.salePrice==null?'Output price snapshot: '+esc(date(result.price?.at)):'Using your manual sale price.'}</small>`;
    }catch(e){$('outcomeResult').textContent=e.message;}
  }
  document.addEventListener('crafting-plan-changed',event=>{
    context=event.detail;
    let panel=$('outcomePanel');if(panel)panel.remove();
    panel=document.createElement('div');panel.id='outcomePanel';panel.style.marginTop='24px';$('detail').append(panel);
    const {recipe,crafter}=context;
    const outputs=[...new Map((data.recipes||[]).filter(r=>r.key.split(':q')[0]===recipe.key.split(':q')[0]).map(r=>[r.output,r])).values()];
    const character=(data.characters||[]).find(c=>c.guid===crafter.guid);
    const professions=(character?.professions||[]).filter(p=>p.baseName===recipe.profession&&p.concentration);
    panel.innerHTML=`<h3>Check a crafting outcome</h3><p>Enter the outcome shown in-game for this character and these exact reagents. Changing the batch, crafter, or reagents resets this form.</p><form id="outcomeForm"><label for="setupName">Setup name</label><input id="setupName" maxlength="120" placeholder="e.g. Daily concentration flask" style="width:100%"><label for="outcome">Output you expect to make</label><select id="outcome" required><option value="">Choose the outcome checked in-game…</option>${outputs.map(r=>`<option value="${esc(r.output)}">${esc(data.inventory?.names?.[r.output]||r.name)} · ${esc(r.key)} · ${r.quantity} per craft</option>`).join('')}</select><label for="saleFee">Selling fee assumption (%)</label><input id="saleFee" type="number" min="0" max="99.99" step="0.01" value="5" required><label for="saleOverride">Sale price per item in gold (leave blank for imported price)</label><input id="saleOverride" type="number" min="0" step="0.0001" placeholder="Use imported price"><label><input id="useConcentration" type="checkbox" style="min-width:0"> Use concentration for this outcome</label><div id="concentrationFields" hidden><label for="concentrationCost">Concentration cost per craft shown in-game</label><input id="concentrationCost" type="number" min="1" max="100000" step="1" disabled><label for="concentrationProfession">Concentration pool</label><select id="concentrationProfession"><option value="">Unknown / not captured</option>${professions.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('')}</select></div><p><button type="button" id="previewOutcome">Calculate estimate</button> <button type="submit" id="saveOutcome">Save setup</button></p></form><div id="outcomeResult" role="status"></div><div class="notice">Scenario estimate from your entered outcome. No multicraft, resourcefulness, ingenuity refunds, deposits, relisting costs, or sale-speed adjustment. Owned materials retain their market value. Estimated profit is not recorded gold earned.</div>`;
    $('useConcentration').onchange=()=>{const checked=$('useConcentration').checked;$('concentrationFields').hidden=!checked;$('concentrationCost').disabled=!checked;$('concentrationCost').required=checked;$('outcomeResult').replaceChildren()};
    $('outcomeForm').oninput=()=>$('outcomeResult').replaceChildren();
    $('previewOutcome').onclick=preview;
    $('outcomeForm').onsubmit=async event=>{event.preventDefault();try{const setup=readSetup();if(!setup)return;if(context.plan.unresolved.length)throw Error('Select every required reagent before saving.');$('saveOutcome').disabled=true;await persist([...setups,setup]);$('outcomeResult').textContent='Saved below. Future imports reprice this setup.'}catch(e){$('outcomeResult').textContent=e.message}finally{if($('saveOutcome'))$('saveOutcome').disabled=false}};
    if(recipe.capture){
      const capture=recipe.capture;
      const note=document.createElement('div');note.className='notice';note.textContent=`Captured in-game ${date(capture.observedAt)} · build ${capture.build||'unknown'}. Exact captured reagents and outcome; recapture after changing gear, talents, or buffs.`;panel.prepend(note);
      const facts=document.createElement('details'),operation=capture.operation||{};
      if(capture.source==='schematic-preview')note.textContent+=` Background reagent preset ${capture.preset}; queried from the recipe schematic, not a claim that these materials are owned. Only sampled presets are compared, not every possible reagent combination.`;
      const skill=Number.isFinite(operation.baseSkill)&&Number.isFinite(operation.bonusSkill)?operation.baseSkill+operation.bonusSkill:null;
      const difficulty=Number.isFinite(operation.baseDifficulty)&&Number.isFinite(operation.bonusDifficulty)?operation.baseDifficulty+operation.bonusDifficulty:null;
      facts.innerHTML=`<summary>Captured crafting details</summary><p>Output quality ${esc(capture.quality)} · ${recipe.quantity} items per craft<br>Operation skill ${esc(skill)} · Difficulty ${esc(difficulty)}<br>Concentration spent per craft: ${capture.concentration}</p>`;
      for(const stat of Object.values(operation.bonusStats||{})){
        const line=document.createElement('p');line.textContent=`${stat.bonusStatName||'Crafting bonus'}: ${stat.bonusStatValue??'unknown'}${Number.isFinite(stat.ratingPct)?' · '+stat.ratingPct.toFixed(1)+'%':''}. ${stat.ratingDescription||''}`;facts.append(line);
      }
      const caveat=document.createElement('small');caveat.textContent='These are the captured operation values. Bonus chances and refunds are shown for inspection and are not yet included in the profit estimate.';facts.append(caveat);note.after(facts);
      $('setupName').value=recipe.name+(capture.applyConcentration?' · Concentration':' · No concentration');
      $('outcome').value=recipe.output;$('outcome').disabled=true;
      $('useConcentration').checked=capture.applyConcentration;$('useConcentration').onchange();$('useConcentration').disabled=true;
      $('concentrationCost').value=capture.concentration;$('concentrationCost').readOnly=true;
      if(capture.skillLineID){
        if(![...$('concentrationProfession').options].some(o=>o.value===String(capture.skillLineID)))$('concentrationProfession').add(new Option('Captured profession pool',String(capture.skillLineID)));
        $('concentrationProfession').value=String(capture.skillLineID);
      }
      $('concentrationProfession').disabled=true;
      if(capture.manualSalePrice){$('saleOverride').required=true;$('saleOverride').placeholder='Enter price for the exact output variant';}
    }
  });
  const oldRender=render;render=function(){oldRender();renderSaved()};
  fetch('/api/setups').then(async response=>{if(!response.ok)throw Error('Restart the app to enable saved crafts.');const body=await response.json();if(body.version!==1||!Array.isArray(body.setups))throw Error('Unsupported saved setup file');setups=body.setups;ready=true;renderSaved()}).catch(e=>{$('setupStatus').textContent=e.message});
}


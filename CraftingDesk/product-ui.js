/* Product -> requested batch -> best feasible crafter, with independent modes. */
{
 let model=null,groups=[],active=null,entries=null,entryData=null,entrySaved=null,entryMinute=0;
 const money=n=>n==null?'Unknown':(n/10000).toLocaleString(undefined,{maximumFractionDigits:2})+' g';
 const controls=document.createElement('div');controls.className='daily-filters';
 controls.innerHTML='<div><label for="productCount">Number of crafts</label><input id="productCount" type="number" value="1" min="1" max="10000" step="1"></div><div><label for="productMode">Crafting mode</label><select id="productMode"><option value="without">Without concentration</option><option value="with">With concentration</option></select></div><div><label for="productQuality">Output quality</label><select id="productQuality"><option value="">Best available quality</option></select></div>';
 $('detail').before(controls);
 const workspace=$('search').closest('section.workspace');if(workspace&&$('dailyDesk'))$('dailyDesk').before(workspace);
 const area=document.createElement('div');area.className='product-columns';$('results').before(area);area.append($('results'));
 const side=document.createElement('div');area.append(side);side.append(controls,$('detail'));
 controls.style.gridTemplateColumns='repeat(auto-fit,minmax(150px,1fr))';
 function getEntries(){const saved=window.getSavedCraftingSetups?.()||[],minute=Math.floor(Date.now()/60000);if(entryData!==data||entrySaved!==saved||entryMinute!==minute){entries=dailyCandidates(data,saved,5);entryData=data;entrySaved=saved;entryMinute=minute;}return entries||[];}
 function inspect(group){
  active=group;$('productQuality').replaceChildren(new Option('Best available quality',''));
  for(const quality of [...new Set(group.recipes.map(r=>r.capture?.quality).filter(q=>q!=null))].sort((a,b)=>a-b))$('productQuality').add(new Option('Quality '+quality,String(quality)));
  draw();
 }
 function draw(){
  if(!active)return;
  const out=$('detail');out.replaceChildren();const h=document.createElement('h3');h.textContent=active.name;out.append(h);
  const count=Number($('productCount').value);if(!Number.isInteger(count)||count<1||count>10000){out.append('Enter a whole craft count from 1 to 10,000.');return;}
  const owner=current(),eligible=getEntries().filter(e=>active.keys.has(e.recipe?.key)&&(!$('only').checked||!owner||e.setup.crafterName===owner.name&&e.setup.realm.replaceAll(' ','')===owner.realm.replaceAll(' ','')));
  const existing=window.getDailyPlanningContext?.()?.planned||[];
  const result=bestProductBatch(data,eligible,count,$('productMode').value,$('productQuality').value,existing);
  const best=result.best;
  if(!best){const p=document.createElement('p');p.textContent=result.alternatives.length?[...new Set(result.alternatives.flatMap(x=>x.issues))].join(' '):'No captured outcome for this mode and quality. Try the other mode or open this recipe in-game and refresh Nexus data.';out.append(p);return;}
  const s=best.entry.setup,summary=document.createElement('div');
  summary.innerHTML=`<h4>${esc(s.crafterName)} · ${esc(s.realm)}</h4><p>${count} crafts → ${best.output} items${best.entry.recipe.capture?.quality?' · Quality '+best.entry.recipe.capture.quality:''}</p><div class="row"><span>Net batch profit after selling fee and all materials</span><strong>${money(best.profit)}</strong></div><div class="row"><span>Full material value</span><b>${money(best.materialCost)}</b></div><div class="row"><span>Buy missing materials</span><b>${money(best.buy)}</b></div><p>${best.spent?best.spent+' concentration':'No concentration'} · ${s.fee}% selling fee</p>`;
  out.append(summary);renderBatchShopping(out,best);
  const observed=document.createElement('small');observed.textContent='Craft captured '+date(s.capturedAt)+' · Sale price '+date(best.entry.result.price?.at);summary.append(observed);
  const status=document.createElement('p');status.setAttribute('role','status');
  const add=document.createElement('button');add.textContent='Add this batch to my plan';add.onclick=async()=>{add.disabled=true;try{await window.addReadyConcentrationBatch({...s,count});status.textContent='Batch saved on Nexus.';draw();}catch(e){status.textContent=e.message;add.disabled=false;}};out.append(add,status);
  const alternatives=document.createElement('details'),title=document.createElement('summary');title.textContent='Other crafters and reagent choices';alternatives.append(title);
  const shown=new Set();for(const choice of result.alternatives){const key=choice.entry.setup.crafterName+'|'+choice.entry.setup.realm+'|'+choice.entry.setup.output;if(shown.has(key))continue;shown.add(key);const p=document.createElement('p');p.textContent=choice.entry.setup.crafterName+' · '+choice.entry.setup.realm+': '+(choice.feasible?money(choice.profit)+' net profit · '+money(choice.buy)+' missing purchases':choice.issues.join(' '));alternatives.append(p);if(shown.size>=20)break;}out.append(alternatives);
 }
 renderRecipes=function(){
  if(model!==data){groups=productGroups(data.recipes||[]);model=data;active=null;}
  const q=$('search').value.toLocaleLowerCase(),owner=current();
  const found=groups.filter(g=>(g.name+' '+g.profession).toLocaleLowerCase().includes(q)&&(!$('only').checked||!owner||g.recipes.some(r=>r.crafters.some(c=>c.guid===owner.guid))));
  $('recipes').textContent=groups.length.toLocaleString();$('resultCount').textContent=found.length+' products · '+Math.min(60,found.length)+' shown';$('results').replaceChildren();
  for(const group of found.slice(0,60)){const button=document.createElement('button');button.className='recipe';button.innerHTML='<b>'+esc(group.name)+'</b><br><small>'+esc(group.profession)+'</small>';button.onclick=()=>inspect(group);$('results').append(button);}
  if(active&&found.includes(active))draw();else $('detail').replaceChildren();
 };
 $('search').oninput=()=>renderRecipes();$('only').onchange=()=>renderRecipes();$('character').onchange=()=>renderRecipes();
 for(const id of ['productCount','productMode','productQuality'])$(id).onchange=draw;
 document.addEventListener('crafting-setups-updated',()=>{if(active)draw();});
 window.openCraftBatch=setup=>{renderRecipes();const group=groups.find(g=>g.keys.has(setup.recipeKey));if(!group)return;inspect(group);$('productCount').value=setup.count;$('productMode').value=setup.concentration>0?'with':'without';draw();};
}

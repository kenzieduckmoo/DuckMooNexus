function quote(market, item, realm) {
  const key=realm.replaceAll(' ','').toLowerCase();
  const tsm=market?.commodities?.[item]||market?.realms?.[key]?.[item];
  const auctionator=market?.auctionator?.commodities?.[item]||market?.auctionator?.realms?.[key]?.[item];
  // Day-only Auctionator observations win only when definitely newer.
  return auctionator&&(!tsm||auctionator.at>tsm.at)?auctionator:tsm||null;
}
function slotOptions(key) {
  const [type,,list] = key.split(':');
  if(type==='i') return [{item:key}];
  if(!['q','r','o','f'].includes(type)||!list) return [];
  return list.split(',').map((id,i)=>({item:'i:'+id,quality:type==='q'?i+1:null}));
}
function materialPlan(recipe, selections, count, crafter, inventory, market) {
  const required = new Map(), unresolved=[];
  for(const [key,quantity] of Object.entries(recipe.materials)) {
    const options=slotOptions(key), item=selections[key];
    if(!item) {if(!['o','f'].includes(key[0])) unresolved.push(key);continue;}
    if(!options.some(o=>o.item===item)) {unresolved.push(key);continue;}
    required.set(item,(required.get(item)||0)+quantity*count);
  }
  let materialCost=0,buyCost=0,missingCost=false,missingBuy=false;
  const owner=(crafter.name+'-'+crafter.realm).replaceAll(' ','').toLowerCase();
  const rows=[...required].map(([item,needed])=>{
    const places=inventory.items?.[item]||[];
    const accessible=places.filter(p=>p.location==='warband'||p.owner.replaceAll(' ','').toLowerCase()===owner||p.bound===false);
    const own=accessible.reduce((sum,p)=>sum+p.quantity,0), missing=Math.max(0,needed-own);
    const price=quote(market,item,crafter.realm);
    if(price) {materialCost+=needed*price.price;buyCost+=missing*price.price;}
    else {missingCost=true;if(missing)missingBuy=true;}
    return {item,needed,own,missing,price,places:accessible};
  });
  return {rows,materialCost:missingCost||unresolved.length?null:materialCost,buyCost:missingBuy||unresolved.length?null:buyCost,unresolved};
}
function compareCrafters(recipes, recipe, selections, count, inventory, market) {
  const signature=r=>JSON.stringify(Object.entries(r.materials).sort(([a],[b])=>a.localeCompare(b)));
  const seen=new Set(), rows=[];
  for(const candidate of recipes){
    if(candidate.key!==recipe.key||candidate.output!==recipe.output||candidate.quantity!==recipe.quantity||signature(candidate)!==signature(recipe))continue;
    for(const crafter of candidate.crafters){
      const id=crafter.guid||candidate.scope+'|'+crafter.name;
      if(seen.has(id))continue;
      seen.add(id);
      rows.push({recipe:candidate,crafter,plan:materialPlan(candidate,selections,count,crafter,inventory,market)});
    }
  }
  return rows.sort((a,b)=>(a.plan.buyCost??Infinity)-(b.plan.buyCost??Infinity)||a.crafter.name.localeCompare(b.crafter.name));
}
if(typeof module!=='undefined')module.exports={quote,slotOptions,materialPlan,compareCrafters};
if(typeof document!=='undefined') {
 const money=n=>n===null?'Incomplete':(n/10000).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+' g';
 const itemName=item=>(data.inventory?.names?.[item]||'Item '+item.slice(2))+(data.inventory?.tiers?.[item]?' · Quality '+data.inventory.tiers[item]:'');
 let active=null,selections={};
 window.restoreCraftingSetup=setup=>{
   const r=(data.recipes||[]).find(r=>r.key===setup.recipeKey&&r.scope===setup.scope);
   if(!r)throw Error('Recipe is missing from the current import.');
   const index=r.crafters.findIndex(c=>c.name===setup.crafterName&&c.realm===setup.realm);
   if(index<0)throw Error('Crafter is missing from the current import.');
   showRecipe(r);selections={...setup.selections};$('crafter').value=String(index);$('craftCount').value=setup.count;drawSlots();calculate();
 };
 showRecipe=function(r){
   active=r;selections={};
   const chosen=r.crafters.findIndex(c=>c.guid===current()?.guid);
   $('detail').innerHTML=`<h3>${esc(r.name)}</h3><label for="crafter">Plan for</label><select id="crafter">${r.crafters.map((c,i)=>`<option value="${i}" ${i===Math.max(0,chosen)?'selected':''}>${esc(c.name)} · ${esc(c.realm)}</option>`).join('')}</select><label for="craftCount">Number of crafts</label><input id="craftCount" type="number" min="1" max="10000" step="1" value="1" style="width:100%;margin:8px 0 18px"><p id="outputCount"></p><div id="materialSlots"></div><div id="costSummary"></div><div id="shopping"></div><div class="notice">Material estimate only. These reagent choices have not been checked against this crafter’s output quality or concentration cost. Prices are TSM minimum-buyout snapshots, not a guaranteed purchase quote.</div>`;
   $('crafter').onchange=()=>{drawSlots();calculate()};$('craftCount').oninput=calculate;
   const comparison=document.createElement('div');comparison.id='comparison';$('detail').append(comparison);
   drawSlots();calculate();
 };
 function drawSlots(){
   const c=active.crafters[Number($('crafter').value)],target=$('materialSlots');target.replaceChildren();
   Object.entries(active.materials).forEach(([key,amount],index)=>{
     const options=slotOptions(key),optional=['o','f'].includes(key[0]);
     if(!(key in selections))selections[key]=optional?'':options.length===1?options[0].item:'';
     const label=document.createElement('label');label.htmlFor='mat'+index;label.textContent=`${key[0]==='f'?'Finishing reagent (optional)':key[0]==='o'?'Optional reagent':key[0]==='q'?'Reagent quality':key[0]==='r'?'Required reagent choice':'Material'} · ${amount} per craft`;
     const select=document.createElement('select');select.id=label.htmlFor;
     if(optional||options.length!==1)select.add(new Option(optional?'None':'Choose a reagent…',''));
     for(const option of options){const p=quote(data.market,option.item,c.realm);select.add(new Option(itemName(option.item)+(option.quality?' · Quality '+option.quality:'')+' · '+(p?money(p.price):'Price unavailable'),option.item));}
     select.value=selections[key];select.onchange=()=>{selections[key]=select.value;calculate()};target.append(label,select);
   });
 }
 function calculate(){
   const input=$('craftCount'),count=Number(input.value);
   if(!Number.isInteger(count)||count<1||count>10000){$('costSummary').textContent='Enter a whole number of crafts from 1 to 10,000.';$('shopping').replaceChildren();$('comparison').replaceChildren();$('outcomePanel')?.remove();return;}
   const crafter=active.crafters[Number($('crafter').value)];if(!crafter)return;
   const plan=materialPlan(active,selections,count,crafter,data.inventory||{},data.market||{});
   $('outputCount').textContent=`Base output: ${count*active.quantity} items before crafting bonuses. Recorded crafter; current capability not yet verified.`;
   $('costSummary').innerHTML=`<div class="row"><span>Market value of materials</span><b>${money(plan.materialCost)}</b></div><div class="row"><span>Estimated gold to buy missing materials</span><b>${money(plan.buyCost)}</b></div>${plan.unresolved.length?'<p>Select all required reagents to finish the estimate.</p>':''}`;
   $('shopping').innerHTML='<h3>Materials & shopping</h3>'+plan.rows.map(row=>`<div class="row"><div><b>${esc(itemName(row.item))}</b><br><small>Need ${row.needed} · Recorded stock ${row.own} · Buy ${row.missing}</small><br><small>${row.price?esc(row.price.scope)+' snapshot · '+esc(date(row.price.at)):'No price recorded'}${row.price&&Date.now()/1000-row.price.at>86400?' · OVER 24 HOURS OLD':''}</small><details><summary>Recorded locations</summary>${row.places.map(p=>`<p>${esc(p.owner)} · ${esc(p.location)} · ${p.quantity}</p>`).join('')||'<p>No usable stock captured.</p>'}</details></div><b>${row.price?money(row.missing*row.price.price):row.missing?'Unknown':'0.00 g'}</b></div>`).join('')+'<small>Stock includes this character’s bags/bank, warband stock, and unbound materials on other characters. Transfers may be required. Guild, equipped, auction, and mail items are excluded. Empty or old snapshots may miss stock. Item names come from the TSM saved item cache and captured inventory; uncached items retain their IDs.</small>';
   const comparisons=compareCrafters(data.recipes||[],active,selections,count,data.inventory||{},data.market||{});
   $('comparison').innerHTML='<h3 style="margin-top:24px">Compare your recorded crafters</h3><p>Same recipe variant, batch size, and reagent choices. Ordered by estimated gold needed to buy missing materials. Each row is an alternative using the same shared stock.</p>';
   for(const row of comparisons){
     const box=document.createElement('div');box.className='row';
     box.innerHTML=`<div><b>${esc(row.crafter.name)} · ${esc(row.crafter.realm)}</b><br><small>Material value ${money(row.plan.materialCost)}<br>Buy missing ${money(row.plan.buyCost)}<br>${row.plan.rows.filter(r=>r.missing>0).length} material types to buy${row.plan.unresolved.length?' · Required choices incomplete':''}</small></div>`;
     const button=document.createElement('button');button.textContent='Plan with this character';
     button.onclick=()=>{const saved={...selections},batch=$('craftCount').value;showRecipe(row.recipe);selections=saved;$('crafter').value=String(row.recipe.crafters.indexOf(row.crafter));$('craftCount').value=batch;drawSlots();calculate()};
     box.append(button);$('comparison').append(box);
   }
   const note=document.createElement('p');note.textContent='This does not rank profit, achievable quality, or concentration efficiency. Unbound stock on other characters may need to be transferred.';$('comparison').append(note);
   document.dispatchEvent(new CustomEvent('crafting-plan-changed',{detail:{recipe:active,crafter,selections:{...selections},count,plan}}));
 }
}

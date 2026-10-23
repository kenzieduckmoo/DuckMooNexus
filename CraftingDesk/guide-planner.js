const guideMath=typeof module!=='undefined'?require('./material-ui.js'):{quote,materialPlan};
const guideNorm=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');
const guideNameIndexes=new WeakMap();
function guideIndex(data){const names=data.inventory?.names||{};if(guideNameIndexes.has(names))return guideNameIndexes.get(names);const index=new Map();for(const [item,name]of Object.entries(data.inventory?.names||{})){const key=guideNorm(name);if(!index.has(key))index.set(key,[]);index.get(key).push(item);}guideNameIndexes.set(names,index);return index;}
function guideItem(data,character,name,index=guideIndex(data),now=Date.now()/1000){
  const options=(index.get(guideNorm(name))||[]).map(item=>{
    const ah=guideMath.quote(data.market,item,character.realm);
    const vendor=(data.acquisitionOffers||[]).filter(o=>o.guid===character.guid&&o.kind==='vendor'&&'i:'+o.itemID===item&&o.hasExtendedCost===false&&o.isPurchasable===true&&o.numAvailable!==0&&o.stackCount>0&&Number.isFinite(o.price)&&o.price>=0&&now-o.observedAt<=7*86400&&o.observedAt<=now+300).sort((a,b)=>b.observedAt-a.observedAt)[0];
    const v=vendor?{price:vendor.price/vendor.stackCount,scope:character.realm,source:'vendor',npc:vendor.npcName,at:vendor.observedAt}:null;
    const price=v&&(!ah||v.price<ah.price)?v:ah;
    return {item,name:data.inventory.names[item],tier:data.inventory?.tiers?.[item],price};
  });
  return options.sort((a,b)=>(a.price?.price??Infinity)-(b.price?.price??Infinity)||a.item.localeCompare(b.item))[0]||{name,price:null};
}
function guideShopping(data,character,requirements){
  const index=guideIndex(data),merged=new Map();
  for(const [name,quantity]of Object.entries(requirements)){
    const item=guideItem(data,character,name,index),key=item.item||name;
    const prior=merged.get(key)||{...item,needed:0};prior.needed+=quantity;merged.set(key,prior);
  }
  const rows=[...merged.values()].map(row=>{
    const own=row.item?guideMath.materialPlan({materials:{[row.item]:row.needed}},{[row.item]:row.item},1,character,data.inventory||{},data.market||{}).rows[0].own:0;
    return {...row,own,missing:Math.max(0,row.needed-own),scope:row.price?.scope||character.realm};
  });
  return {rows,total:rows.every(r=>r.price)?rows.reduce((s,r)=>s+r.needed*r.price.price,0):null,buy:rows.every(r=>!r.missing||r.price)?rows.reduce((s,r)=>s+r.missing*(r.price?.price||0),0):null};
}
function guideStarter(data,character,guide){
  const requirements={...guide.supplies},choices=[];
  for(const group of guide.alternatives||[]){
    const candidates=group.names.map(name=>guideItem(data,character,name));
    const best=[...candidates].sort((a,b)=>(a.price?.price??Infinity)-(b.price?.price??Infinity))[0];
    requirements[best.name]=(requirements[best.name]||0)+group.count;
    choices.push({name:best.name,count:group.count,complete:candidates.every(c=>c.price),candidates});
  }
  return {...guideShopping(data,character,requirements),choices};
}
function guideRecipe(data,character,guide,name,count=1){
  const records=(data.catalog||[]).filter(r=>guideNorm(r.name)===guideNorm(name)&&r.profession?.expansionName==='Midnight'&&r.profession?.parentProfessionName===guide.name&&r.schematic&&!r.schematic.isRecraft);
  const record=records.sort((a,b)=>Number(b.guid===character.guid)-Number(a.guid===character.guid)||b.observedAt-a.observedAt)[0];
  if(!record)return {name,error:'No imported reagent schematic for this recipe. Open this profession and import its saved catalog.'};
  if(record.schematic.recipeType===2)return {name,error:'This operation consumes a target item not included in its reagent slots. Use the guide target list; a complete automatic material price is unavailable.'};
  const requirements={},selected=[];
  for(const slot of Object.values(record.schematic.reagentSlotSchematics||{})){
    if(!slot.required)continue;
    const reagents=Object.values(slot.reagents||{});
    if(!reagents.length||reagents.some(r=>!r.itemID||r.currencyID)||!(slot.quantityRequired>0))return {name,error:'This recipe has an unsupported reagent requirement.'};
    const options=reagents.map(r=>{const item='i:'+r.itemID,name=data.inventory?.names?.[item]||item;const exact=guideItem(data,character,name);return {...exact,item,name,tier:data.inventory?.tiers?.[item],price:exact.item===item?exact.price:guideMath.quote(data.market,item,character.realm)};});
    if(options.some(o=>!o.price))return {name,error:'One or more reagent prices are missing; a cheapest-material comparison is unavailable.'};
    const best=options.sort((a,b)=>a.price.price-b.price.price)[0];
    selected.push({...best,needed:slot.quantityRequired*count});
  }
  // Preserve chosen item IDs: name-based re-resolution could merge different quality slots.
  const sums=new Map();for(const row of selected){const prev=sums.get(row.item)||{...row,needed:0};prev.needed+=row.needed;sums.set(row.item,prev);}
  const rows=[...sums.values()].map(row=>{const p=guideMath.materialPlan({materials:{[row.item]:row.needed}},{[row.item]:row.item},1,character,data.inventory||{},data.market||{}).rows[0];return {...row,own:p.own,missing:p.missing,scope:row.price.scope||character.realm};});
  const own=records.find(r=>r.guid===character.guid);
  return {name,record,learned:own?.learned===true,count,rows,total:rows.reduce((s,r)=>s+r.needed*r.price.price,0),buy:rows.reduce((s,r)=>s+r.missing*r.price.price,0)};
}
function guideImport(rows,title='Profession supplies',inventory={}){
  const groups=new Map(),omitted=[];
  for(const r of rows.filter(r=>r.missing>0&&r.price?.source!=='vendor')){
    if(!r.item||!r.name||/^i:\d+$/.test(r.name)||/[;^"\r\n]/.test(r.name)){omitted.push(r);continue;}
    const identities=Object.entries(inventory.names||{}).filter(([id,name])=>name===r.name&&(inventory.tiers?.[id]??null)===(r.tier??null));
    if(identities.some(([id])=>id!==r.item)||rows.some(other=>other.item!==r.item&&other.name===r.name&&(other.tier??null)===(r.tier??null))){omitted.push(r);continue;}
    const scope=r.scope||'Market';if(!groups.has(scope))groups.set(scope,[]);
    const fields=Array(14).fill('');fields[0]='"'+r.name+'"';fields[11]=r.tier??'#';fields[13]=Math.ceil(r.missing);groups.get(scope).push(fields.join(';'));
  }
  return {text:[...groups].map(([scope,items])=>['DuckMoo '+title+' ('+scope.replace(/[;^\r\n]/g,' ')+')',...items].join('^')).join('\n'),omitted};
}
// Trainer source text describes the recipe unlock, not the character's current eligibility.
function guideTrainerRecipes(data,character,guide){
  const unique=new Map();
  for(const r of data.catalog||[]){
    if(r.profession?.expansionName!=='Midnight'||r.profession?.parentProfessionName!==guide.name||r.schematic?.isRecraft)continue;
    const source=String(r.sourceText||'').replace(/\|c[0-9a-fA-F]{8}|\|r/g,'');
    if(!source.includes('Profession Trainer:'))continue;
    const match=source.match(/Midnight [A-Za-z ]+\((\d+)\)/);
    if(!match||Number(match[1])>guide.early)continue;
    const key=r.recipeID||guideNorm(r.name),previous=unique.get(key);
    if(!previous||Number(r.guid===character.guid)>Number(previous.guid===character.guid)||((r.guid===character.guid)===(previous.guid===character.guid)&&r.observedAt>previous.observedAt))unique.set(key,r);
  }
  return [...unique.values()].map(r=>({name:r.name,recipeID:r.recipeID,skill:Number(String(r.sourceText).match(/Midnight [A-Za-z ]+\((\d+)\)/)[1]),learned:r.guid===character.guid&&r.learned===true,firstCraft:r.guid===character.guid?r.firstCraft:null})).sort((a,b)=>a.skill-b.skill||a.name.localeCompare(b.name));
}
if(typeof module!=='undefined')module.exports={guideIndex,guideNorm,guideItem,guideShopping,guideStarter,guideRecipe,guideImport,guideTrainerRecipes};

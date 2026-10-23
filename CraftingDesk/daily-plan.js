/* Shared-stock accounting and bounded concentration planning. All money is copper. */
const dailyMath=typeof module!=='undefined'?require('./profit-ui.js'):{evaluateSetup,setupFromCapture,concentrationGain,buildEvaluationIndex,assignConcentrationGains};
function qualityLabel(item,names={},tiers={}){return (names[item]||item)+(tiers[item]?' · Quality '+tiers[item]:'');}
function completePlanCrafts(setups,completed,id,count,at=Date.now()/1000){
  const setup=setups.find(s=>s.id===id);
  if(!setup||!Number.isInteger(count)||count<1||count>setup.count)throw Error('Enter completed crafts between 1 and the remaining quantity.');
  if(completed.length>=200)throw Error('Completion history is full. Export your history before starting another plan.');
  return {setups:setups.flatMap(s=>s.id!==id?[s]:s.count>count?[{...s,count:s.count-count}]:[]),
    completed:[...completed,{...setup,id:id+'-done-'+at,count,completedAt:at}]};
}
function completionNeedsImport(snapshot,completed){
  if(!completed.length)return false;
  const last=Math.max(...completed.map(s=>s.completedAt));
  return ['Syndicator','DuckMooPlanner'].some(name=>!(snapshot.sources||[]).some(s=>s.name===name&&s.savedAt>last));
}
function ownerKey(setup){return (setup.crafterName+'-'+setup.realm).replaceAll(' ','').toLowerCase();}
function poolKey(setup){return ownerKey(setup)+'|'+(setup.professionId??'unknown');}
function planKey(setup){return JSON.stringify([setup.recipeKey,setup.scope,ownerKey(setup),setup.output,setup.concentration,setup.fee,setup.salePrice??null,Object.entries(setup.selections).sort()]);}
function dailyCandidates(snapshot,saved=[],fee=5,now=Date.now()/1000){
  const sources=[...(snapshot.recipes||[]).filter(r=>r.capture).map(r=>dailyMath.setupFromCapture(r,fee)),...saved.map(s=>({...s,count:1,fee}))];
  const unique=new Map(),index=dailyMath.buildEvaluationIndex(snapshot);
  for(const setup of sources){
    const result=dailyMath.evaluateSetup(snapshot,setup,now,index);
    const recipe=index.recipes.get(JSON.stringify([setup.recipeKey,setup.scope]));
    const exactSales=snapshot.market?.sales?.[setup.output],baseItem=setup.output.match(/^i:\d+/)?.[0];
    const sales=exactSales||snapshot.market?.sales?.[baseItem]||null;
    const margin=result.finance?.profit!=null&&result.plan?.materialCost>0?result.finance.profit/result.plan.materialCost*100:null;
    const entry={setup,result,recipe,sales,margin,salesBasis:exactSales?'Exact item':'Base item fallback',owner:ownerKey(setup),profession:recipe?.profession||'Unknown',observedAt:setup.capturedAt||Date.parse(setup.savedAt)/1000};
    // Same outcome/materials may be saved manually and captured. Count that option once.
    const identity=JSON.stringify([setup.recipeKey.split(':q')[0],setup.scope,entry.owner,setup.output,setup.quantity,setup.concentration,setup.fee,setup.salePrice??null,Object.entries(setup.selections).sort()]);
    const prior=unique.get(identity);
    if(!prior||(!result.error&&prior.result.error)||(!result.error&&entry.observedAt>prior.observedAt))unique.set(identity,entry);
  }
  const entries=[...unique.values()];
  dailyMath.assignConcentrationGains(entries);
  return entries;
}
function groupDaily(entries){
  const groups=new Map();
  // Input is already ranked. Display one leader without pruning optimizer inputs.
  for(const e of entries){const key=JSON.stringify([e.owner,e.setup.recipeKey.split(':q')[0],e.setup.concentration>0]);
    const prior=groups.get(key);if(prior)prior.alternativeCount++;else groups.set(key,{...e,alternativeCount:0});
  }
  return [...groups.values()];
}
function filterDaily(entries,options={},now=Date.now()/1000){
  return entries.filter(e=>(!options.owner||e.owner===options.owner)&&(!options.profession||e.profession===options.profession)
    &&(!options.search||(e.setup.name+' '+e.setup.crafterName).toLowerCase().includes(options.search.toLowerCase()))
    &&(!(options.minMargin>0)||e.margin!=null&&e.margin+1e-9>=options.minMargin)
    &&(!(options.minSaleRate>0)||e.sales?.saleRate>=options.minSaleRate)
    &&(!(options.minDailySold>0)||e.sales?.dailySold>=options.minDailySold)
    &&(!options.positive||e.result.finance?.profit>0)
    &&(!options.ready||(!e.result.error&&(e.setup.concentration===0||(e.result.budget?.crafts??0)>=1)))
    &&(!options.maxAge||Number.isFinite(e.observedAt)&&Math.max(0,now-e.observedAt)<=options.maxAge*3600)
    &&(!options.mode||options.mode==='with'&&e.setup.concentration>0||options.mode==='without'&&e.setup.concentration===0));
}
function evaluateDailyPlan(snapshot,setups,now=Date.now()/1000){
  const lines=[],demands=[],pools=new Map(),issues=[];
  const evaluationIndex=dailyMath.buildEvaluationIndex(snapshot);
  let profit=0,profitKnown=true,requirementsKnown=true;
  for(const setup of setups){
    if(!Number.isInteger(setup.count)||setup.count<1||setup.count>10000){issues.push(setup.name+': invalid craft count');profitKnown=requirementsKnown=false;continue;}
    const result=dailyMath.evaluateSetup(snapshot,setup,now,evaluationIndex),line={setup,result};lines.push(line);
    if(result.error){issues.push(setup.name+': '+result.error);profitKnown=requirementsKnown=false;continue;}
    if(result.finance.profit==null)profitKnown=false;else profit+=result.finance.profit;
    if(result.plan.unresolved.length){requirementsKnown=false;issues.push(setup.name+': incomplete reagent choices');}
    for(const row of result.plan.rows)demands.push({...row,lineIndex:lines.length-1,owner:ownerKey(setup),crafter:setup.crafterName,realm:setup.realm,remaining:row.needed,used:0});
    if(setup.concentration>0){
      const key=poolKey(setup),pool=pools.get(key)||{key,name:setup.crafterName+' · '+(result.profession?.name||'Unknown profession pool'),required:0,available:result.budget?.available??null};
      pool.required+=setup.concentration*setup.count;
      pools.set(key,pool);
    }
  }
  const allocations=[];
  const allocate=(demand,place,quantity)=>{
    if(!quantity)return;
    demand.remaining-=quantity;demand.used+=quantity;place.remaining-=quantity;
    allocations.push({item:demand.item,owner:place.owner,location:place.location,crafter:demand.crafter,realm:demand.realm,quantity});
  };
  const stock=new Map();
  for(const item of new Set(demands.map(d=>d.item)))stock.set(item,(snapshot.inventory?.items?.[item]||[]).filter(p=>Number.isFinite(p.quantity)&&p.quantity>0).map(p=>({...p,remaining:p.quantity})));
  // Reserve each owner's bound stock first, before any shared material is consumed.
  for(const demand of demands){
    for(const place of stock.get(demand.item)){
      if(place.location!=='warband'&&place.bound!==false&&place.owner.replaceAll(' ','').toLowerCase()===demand.owner)allocate(demand,place,Math.min(demand.remaining,place.remaining));
    }
  }
  // Shared stock covers higher-priced needs first. Unknown prices get stock first
  // because their purchase cost cannot be estimated. This is a purchase estimate,
  // not a cross-realm trading or transfer-time optimizer.
  const ordered=[...demands].sort((a,b)=>(b.price?.price??Infinity)-(a.price?.price??Infinity));
  for(const demand of ordered){
    const places=stock.get(demand.item).filter(p=>p.location==='warband'||p.bound===false);
    places.sort((a,b)=>Number(b.owner.replaceAll(' ','').toLowerCase()===demand.owner)-Number(a.owner.replaceAll(' ','').toLowerCase()===demand.owner));
    for(const place of places)allocate(demand,place,Math.min(demand.remaining,place.remaining));
  }
  const shopping=new Map();let buyCost=0,buyKnown=requirementsKnown;
  for(let i=0;i<lines.length;i++)lines[i].reservedRows=demands.filter(d=>d.lineIndex===i).map(d=>({...d,own:d.used,missing:d.remaining}));
  for(const demand of demands){
    const scope=demand.price?.scope||demand.realm,key=JSON.stringify([demand.item,scope,demand.price?.price??null,demand.price?.source??null]);
    const row=shopping.get(key)||{item:demand.item,scope,price:demand.price?.price??null,priceSource:demand.price?.source??null,vendor:demand.price?.source==='vendor',needed:0,used:0,missing:0,forCharacters:new Set(),at:demand.price?.at};
    row.needed+=demand.needed;row.used+=demand.used;row.missing+=demand.remaining;row.forCharacters.add(demand.crafter+' · '+demand.realm);shopping.set(key,row);
    if(demand.remaining){if(demand.price)buyCost+=demand.remaining*demand.price.price;else buyKnown=false;}
  }
  for(const pool of pools.values()){
    if(pool.available==null)issues.push(pool.name+': concentration availability unknown');
    else if(pool.required>pool.available)issues.push(pool.name+': needs '+Math.ceil(pool.required-pool.available)+' more concentration');
  }
  return {lines,pools:[...pools.values()],shopping:[...shopping.values()].map(r=>({...r,forCharacters:[...r.forCharacters]})),allocations,issues,profit:profitKnown?profit:null,buyCost:buyKnown?buyCost:null,requirementsKnown};
}
function suggestConcentration(snapshot,entries,existing=[],maxPerSetup=10,now=Date.now()/1000){
  if(!Number.isInteger(maxPerSetup)||maxPerSetup<1||maxPerSetup>10000)throw Error('Enter a whole craft limit from 1 to 10,000.');
  const current=evaluateDailyPlan(snapshot,existing,now);
  if(current.issues.length)throw Error('Resolve the current plan warnings before adding suggestions.');
  const reserved=new Map(current.pools.map(p=>[p.key,p.required])),groups=new Map();
  for(const entry of entries){
    const s=entry.setup,r=entry.result;
    if(!(s.concentration>0)||!Number.isInteger(s.concentration)||s.professionId==null||r.error||!(r.finance?.perCraft>0)||r.budget?.available==null)continue;
    const key=poolKey(s),group=groups.get(key)||{available:Math.max(0,Math.floor(r.budget.available-(reserved.get(key)||0))),entries:[]};
    const already=existing.filter(x=>planKey(x)===planKey(s)).reduce((sum,x)=>sum+x.count,0);
    group.entries.push({entry,limit:Math.max(0,maxPerSetup-already)});groups.set(key,group);
  }
  const selected=[];
  for(const group of groups.values()){
    // Concentration pools in the captured data are small. Bound work if a future
    // schema supplies an unexpectedly large pool rather than freezing the UI.
    const capacity=Math.min(10000,group.available),values=new Float64Array(capacity+1),paths=Array(capacity+1).fill(null);
    values.fill(-Infinity);values[0]=0;
    for(const {entry,limit} of group.entries){
      let remaining=Math.min(limit,Math.floor(capacity/entry.setup.concentration)),chunk=1;
      while(remaining>0){
        const count=Math.min(chunk,remaining),weight=count*entry.setup.concentration,value=count*entry.result.finance.perCraft;
        for(let budget=capacity;budget>=weight;budget--){
          const candidate=values[budget-weight]+value;
          if(candidate>values[budget]+1e-7){values[budget]=candidate;paths[budget]={entry,count,previous:paths[budget-weight]};}
        }
        remaining-=count;chunk*=2;
      }
    }
    let best=0;for(let i=1;i<=capacity;i++)if(values[i]>values[best]+1e-7)best=i;
    const counts=new Map();
    for(let path=paths[best];path;path=path.previous){const key=planKey(path.entry.setup),record=counts.get(key)||{setup:path.entry.setup,count:0};record.count+=path.count;counts.set(key,record);}
    for(const row of counts.values())selected.push({...row.setup,count:row.count});
  }
  return selected;
}
function auctionatorImportText(plan,names={},tiers={}){
  if(!plan.requirementsKnown)return 'Auctionator import unavailable: resolve incomplete recipe requirements first.';
  const groups=new Map(),omitted=[],identities=new Map();
  for(const [item,name] of Object.entries(names))if(/^i:\d+$/.test(item)){
    const key=JSON.stringify([name,tiers[item]??null]);identities.set(key,(identities.get(key)||0)+1);
  }
  for(const row of plan.shopping.filter(r=>r.missing>0&&!r.vendor)){
    const name=names[row.item],tier=tiers[row.item];
    if(!/^i:\d+$/.test(row.item)||!name||/[;^\r\n]/.test(name)||(identities.get(JSON.stringify([name,tier??null]))||0)>1){
      omitted.push(`${row.missing} x ${name||row.item} (${row.item}, ${row.scope}) - search manually; exact name/quality is ambiguous or unavailable.`);continue;
    }
    const scope=row.scope||'Unknown realm',items=groups.get(scope)||new Map();
    const prior=items.get(row.item)||{name,tier,quantity:0};prior.quantity+=row.missing;items.set(row.item,prior);groups.set(scope,items);
  }
  const lines=[...groups].map(([scope,items])=>['DuckMoo - Buy missing ('+scope.replace(/[;^\r\n]/g,' ')+')',...[...items.values()].map(r=>{
    const fields=Array(14).fill('');fields[0]='"'+r.name+'"';fields[11]=r.tier??'#';fields[13]=r.quantity;return fields.join(';');
  })].join('^'));
  return ['Auctionator shopping-list import:',
    'Copy only the lines between BEGIN and END into Auctionator Shopping > Import.',
    'Quantities are missing materials only. Importing replaces existing lists with these same names.',
    'Lists are separated by pricing region/realm; buy each list in its appropriate market.',
    ...(lines.length?['BEGIN AUCTIONATOR IMPORT',...lines,'END AUCTIONATOR IMPORT']:['No importable purchases needed.']),
    ...(omitted.length?['Manual searches excluded from import:',...omitted]:[])].join('\n');
}
function dailyPlanText(plan,names={},tiers={}){
  return ['Crafting Desk — daily plan','Estimates from imported snapshots; transfers and purchases are not performed.',
    ...plan.lines.flatMap(l=>[`${l.setup.crafterName} (${l.setup.realm}): ${l.setup.count} x ${l.setup.name}${l.setup.concentration?' — '+l.setup.count*l.setup.concentration+' concentration':''}${l.result.error?' — NEEDS REVIEW: '+l.result.error:''}`,
      ...(l.result.plan?.rows||[]).map(r=>`  ${r.needed} x ${qualityLabel(r.item,names,tiers)} for this batch`)]),
    '',...plan.issues.map(x=>'REVIEW: '+x),'Shopping:',
    ...plan.shopping.filter(r=>r.missing>0).map(r=>`${r.missing} x ${qualityLabel(r.item,names,tiers)} (${r.scope})${r.price==null?' — price unknown':''}`),
    '', 'Stock allocation:',...plan.allocations.map(a=>`${a.quantity} x ${qualityLabel(a.item,names,tiers)}: ${a.owner} / ${a.location} → ${a.crafter} (${a.realm})`), '',auctionatorImportText(plan,names,tiers)].join('\n');
}
if(typeof module!=='undefined')module.exports={qualityLabel,completePlanCrafts,completionNeedsImport,auctionatorImportText,groupDaily,ownerKey,poolKey,planKey,dailyCandidates,filterDaily,evaluateDailyPlan,suggestConcentration,dailyPlanText};

// Bounded guide workflow, shared by the native site's calculation worker.
const {professionRoute}=require('./profession-route.js'),{tailoringRoute}=require('./tailoring-route.js'),h=require('./guide-planner.js');
function profileKey(owner,profession){return owner+'|'+profession;}
function routeFor(model,c,g,profile={},skill){const options={choices:profile.choices||{},lining:profile.lining,gear:profile.gear};if(skill!==undefined&&skill!=='')options.skill=Number(skill);return g.name==='Tailoring'?tailoringRoute(model,c,options):professionRoute(model,c,g,options);}
function workspace(model,c,g,profile={},skill){
 const route=routeFor(model,c,g,profile,skill),done=profile.done||{},groups=[];
 const compact=x=>({name:x.name,cost:x.cost??null,learned:!!x.unlock?.learned,source:x.unlock?.text||'',error:x.plan?.error||'',alternative:!!x.alternative});
 if(g.name==='Tailoring'){
  if(route.skill<90)groups.push({key:'lining',label:'65–90: lining recipe',selected:route.chosen,options:route.choices.map(compact)});
  if(route.skill<100)groups.push({key:'gear',label:'90–100: finishing equipment',selected:route.gear,options:route.gearChoices.map(compact)});
 }else{
  for(const from of [...new Set(route.choices.map(x=>x.from))]){const options=route.choices.filter(x=>x.from===from);groups.push({key:String(from),label:from+'–'+options[0].to+': recipe',selected:route.steps.find(s=>s.chosen&&s.from>=from&&s.to===options[0].to)?.name??options[0].name,options:options.map(compact)});}
 }
 const step=route.steps.find(s=>!done[s.id]);let next=null;
 if(step){
  if(step.gate){const p=h.guideShopping(model,c,step.requirements||{}),issues=[];
   for(const r of p.rows)if((g.vendor||[]).includes(r.name)&&(!r.tier||r.tier===1)&&r.price?.source!=='vendor'){r.price={source:'vendor',price:null};r.vendor=true;issues.push(r.name+': visit its vendor and capture the current price.');}
   next={...step,rows:p.rows,buy:issues.length?null:p.buy,total:issues.length?null:p.total,issues,checkpoint:true};}
  else{
   const count=Math.min(10,Math.max(1,step.count||1)),p=h.guideRecipe(model,c,g,step.name,count),issues=p.error?[p.error]:[],rows=[...(p.rows||[])];
   if(p.record?.schematic?.recipeType===3)rows.push(...h.guideShopping(model,c,{'Enchanting Vellum':count}).rows);
   // Vendor-only supplies must never be silently priced as auction purchases.
   for(const r of rows)if((g.vendor||[]).includes(r.name)&&(!r.tier||r.tier===1)&&r.price?.source!=='vendor'){r.price={source:'vendor',price:null};r.vendor=true;issues.push(r.name+': visit its vendor and capture the current price.');}
   const sum=field=>!issues.length&&rows.every(r=>!r[field]||Number.isFinite(r.price?.price))?rows.reduce((n,r)=>n+r[field]*(r.price?.price||0),0):null;
   if(step.unlock&&!step.unlock.learned&&step.unlock.text!=='Already learned')issues.push('Before crafting: '+step.unlock.text);
   next={...step,count,rows,buy:sum('missing'),total:sum('needed'),issues,checkpoint:false};
  }
 }
 return {route,groups,next,done};
}
function update(model,c,g,doc,input){
 const next=structuredClone(doc||{version:1,profiles:{}});next.profiles=next.profiles||{};
 const key=profileKey(c.guid,g.name),profile=next.profiles[key]||{choices:{},done:{}};
 profile.choices=profile.choices||{};profile.done=profile.done||{};
 const view=workspace(model,c,g,profile,input.skill);
 if(input.kind==='choice'){
  const group=view.groups.find(x=>x.key===String(input.group));
  if(!group||!group.options.some(x=>x.name===input.value))throw Error('Choose an available route recipe.');
  if(group.key==='lining'||group.key==='gear')profile[group.key]=input.value;else profile.choices[group.key]=input.value;
 }else if(input.kind==='checkpoint'){
  if(!view.route.steps.some(s=>s.id===input.step)||typeof input.done!=='boolean')throw Error('Choose a current guide step.');
  profile.done[input.step]=input.done;
 }else if(input.kind==='import'){
  for(const step of view.route.steps){const oldPrefix=step.id.replace(/:(repeat|first|craft)$/,'')+':';if(input.done?.[step.id]===true||Object.entries(input.done||{}).some(([id,v])=>v===true&&id.startsWith(oldPrefix)&&/^\d+$/.test(id.slice(oldPrefix.length))))profile.done[step.id]=true;}
 }else throw Error('Unknown guide change.');
 next.profiles[key]=profile;return next;
}
module.exports={profileKey,workspace,update};

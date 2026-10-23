const assert=require('node:assert/strict');
const {professionRoute}=require('./profession-route.js'),guides=require('./profession-guides.js'),{guideRecipe}=require('./guide-planner.js');
const c={guid:'a',name:'A',realm:'One',professions:[{name:'Midnight Cooking',rank:1}]};
const d={characters:[c],inventory:{names:{'i:1':"A Big Ol' Stick of Butter",'i:2':'Pouch of Spices','i:3':'Plant Protein','i:4':'Ripened Vegetable Assortment','i:5':'Mana-Wyrm Essence'},items:{'i:1':[{owner:'A-One',location:'bags',bound:true,quantity:30}]}},market:{commodities:Object.fromEntries([1,2,3,4,5].map(id=>['i:'+id,{price:10,scope:'US'}]))},catalog:[]};
function rec(name,requirements,type=1){return {name,guid:'a',learned:true,observedAt:1,profession:{parentProfessionName:'Cooking',expansionName:'Midnight'},schematic:{recipeType:type,reagentSlotSchematics:Object.fromEntries(Object.entries(requirements).map(([id,quantityRequired])=>[id,{required:true,quantityRequired,reagents:[{itemID:Number(id)}]}]))}};}
d.catalog=[rec('Spiced Biscuits',{1:1,2:3}),rec('Felberry Figs',{1:1,3:10,4:4,5:1}),rec('Hearty Food',{},2)];
const g=guides.find(g=>g.name==='Cooking');let p=professionRoute(d,c,g);
assert.equal(p.rows.find(r=>r.item==='i:1').needed,60);assert.equal(p.rows.find(r=>r.item==='i:1').missing,30);assert.equal(p.rows.find(r=>r.item==='i:2').needed,150);
assert.equal(p.rows.find(r=>r.item==='i:1').price.source,'vendor');assert.equal(p.buy,null);assert.equal(p.checkpoint.name,'Convert food with Hearty Food');
p=professionRoute(d,c,g,{skill:35});assert.equal(p.rows.length,2);assert.equal(p.rows.find(r=>r.item==='i:2').needed,75);
p=professionRoute(d,c,g,{skill:100});assert.deepEqual(p.rows,[]);assert.deepEqual(p.steps,[]);
assert.match(guideRecipe(d,c,g,'Hearty Food').error,/target item/);
const live=require('./local-data.json');
for(const g of guides.filter(g=>g.name!=='Tailoring')){const c=live.characters.find(c=>c.professions.some(p=>p.name==='Midnight '+g.name));for(const skill of [1,g.early,100]){const plan=professionRoute(live,c,g,{skill});assert.ok(plan.steps.every(s=>s.to>skill));assert.ok(plan.rows.every(r=>r.needed>0&&r.missing>=0));assert.equal(new Set(plan.rows.map(r=>r.item||r.name)).size,plan.rows.length);if(skill===100)assert.equal(plan.rows.length,0);if(plan.issues.length)console.log(g.name,skill,plan.issues);}}
console.log('Profession routes: shared inventory once, vendor exclusion, conversion targets, checkpoints, completed skill and all eight live catalogs passed.');
const {routeAlternatives}=require('./profession-route.js');
const now=Date.now()/1000;
const learner={guid:'learner',name:'Learner',realm:'One',professions:[{name:'Midnight Alchemy',rank:50}]};
const altGuide={name:'Alchemy',vendor:[],finish:[{recipe:'Baseline',count:80}]};
const record=(id,name,item)=>({guid:'learner',recipeID:id,name,learned:true,observedAt:now,build:'test',profession:{parentProfessionName:'Alchemy',expansionName:'Midnight',skillLevel:50,skillModifier:40},canSkillUp:true,relativeDifficulty:0,numSkillUps:1,maxTrivialLevel:100,cooldownCaptured:true,cooldown:{seconds:0,observedAt:now},schematic:{recipeType:1,reagentSlotSchematics:[{required:true,quantityRequired:1,reagents:[{itemID:item}]}]}});
const alternateData={inventory:{names:{'i:10':'Expensive','i:11':'Cheap'},items:{}},market:{commodities:{'i:10':{price:200},'i:11':{price:100}}},catalog:[record(10,'Baseline',10),record(11,'Cheaper learned recipe',11)]};
let optimized=professionRoute(alternateData,learner,altGuide);
assert.equal(optimized.steps[0].name,'Cheaper learned recipe');assert.equal(optimized.steps[0].count,80);assert.equal(optimized.buy,8000);
assert.equal(professionRoute(alternateData,learner,altGuide,{choices:{50:'Baseline'}}).steps[0].name,'Baseline');
for(const patch of [{learned:false},{observedAt:now-86401},{observedAt:now+301},{relativeDifficulty:1},{numSkillUps:2},{maxTrivialLevel:90},{build:'other'},{cooldownCaptured:false},{cooldown:{seconds:1,observedAt:now}}]){const changed={...alternateData,catalog:[alternateData.catalog[0],{...alternateData.catalog[1],...patch}]};assert.deepEqual(routeAlternatives(changed,learner,altGuide,['Baseline'],50,100,now),[]);}
assert.equal(professionRoute(alternateData,learner,altGuide,{skill:75}).steps[0].count,40);
console.log('Route substitutions: cheaper learned choice, manual override, partial-stage quantities and incompatible/stale/cooldown exclusions passed.');
const engineer={guid:'learner',name:'Learner',realm:'One',professions:[{name:'Midnight Engineering',rank:85}]};
const engineeringGuide=guides.find(g=>g.name==='Engineering');
const finishing={...alternateData,catalog:alternateData.catalog.map((r,i)=>({...r,profession:{...r.profession,parentProfessionName:'Engineering',skillLevel:85},relativeDifficulty:i===0?0:1}))};
let finish=professionRoute(finishing,engineer,engineeringGuide);
assert.equal(finish.checkpoint,null);assert.equal(finish.steps[0].name,'Baseline');assert.equal(finish.steps[0].count,10);assert.ok(finish.steps[0].finishBatch);
assert.equal(professionRoute(finishing,engineer,engineeringGuide,{choices:{80:'Cheaper learned recipe'}}).steps[0].name,'Cheaper learned recipe');
assert.ok(professionRoute({...finishing,catalog:[]},engineer,engineeringGuide).checkpoint);
console.log('Finishing routes: learned alternatives replace discovery placeholders; orange priority, override and missing-evidence checkpoint passed.');

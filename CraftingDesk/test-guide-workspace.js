const assert=require('node:assert/strict');
const {workspace,update}=require('./guide-workspace.js'),guides=require('./profession-guides.js');
const now=Date.now()/1000,c={guid:'Player-1-ABC',name:'Guide test',realm:'Test',professions:[{name:'Midnight Alchemy',rank:50}]},g={name:'Alchemy',vendor:[],finish:[{recipe:'Baseline',count:80}]};
const record=(id,name,price)=>({guid:c.guid,recipeID:id,name,learned:true,observedAt:now,build:'test',profession:{parentProfessionName:'Alchemy',expansionName:'Midnight',skillLevel:50},canSkillUp:true,relativeDifficulty:0,numSkillUps:1,maxTrivialLevel:100,cooldownCaptured:true,cooldown:{seconds:0,observedAt:now},schematic:{recipeType:1,reagentSlotSchematics:[{required:true,quantityRequired:2,reagents:[{itemID:id}]}]}});
const d={characters:[c],inventory:{names:{'i:1':'Expensive','i:2':'Cheap'},items:{}},market:{commodities:{'i:1':{price:200},'i:2':{price:100}}},catalog:[record(1,'Baseline'),record(2,'Alternative')]};
let doc={version:1,profiles:{'Player-2-DEF|Tailoring':{choices:{},done:{'some-step':true}}}},view=workspace(d,c,g);
assert.equal(view.route.steps[0].name,'Alternative');assert.equal(view.next.count,10);assert.equal(view.next.rows[0].needed,20);
doc=update(d,c,g,doc,{kind:'choice',group:'50',value:'Baseline'});view=workspace(d,c,g,doc.profiles[c.guid+'|Alchemy']);assert.equal(view.route.steps[0].name,'Baseline');assert.equal(doc.profiles['Player-2-DEF|Tailoring'].done['some-step'],true);
assert.throws(()=>update(d,c,g,doc,{kind:'choice',group:'50',value:'Uncaptured recipe'}),/available/);
const id=view.route.steps[0].id;doc=update(d,c,g,doc,{kind:'checkpoint',step:id,done:true});assert.equal(workspace(d,c,g,doc.profiles[c.guid+'|Alchemy']).next,null);
const advanced={...c,professions:[{name:'Midnight Alchemy',rank:55}]};assert.equal(workspace(d,advanced,g,{choices:{50:'Baseline'}}).route.steps[0].id,id,'Step identity survives changed skill/earlier steps');
const enchanter={...c,professions:[{name:'Midnight Enchanting',rank:62}]},eg=guides.find(x=>x.name==='Enchanting');
const ed={...d,inventory:{names:{'i:1':'Dust','i:3':'Enchanting Vellum'},items:{}},market:{commodities:{'i:1':{price:200},'i:3':{price:50}}},catalog:[{...record(1,'Enchant Weapon - Worldsoul Aegis'),profession:{parentProfessionName:'Enchanting',expansionName:'Midnight',skillLevel:62},schematic:{recipeType:3,reagentSlotSchematics:[{required:true,quantityRequired:2,reagents:[{itemID:1}]}]}}]};
assert.equal(workspace(ed,enchanter,eg).next.rows.find(r=>r.name==='Enchanting Vellum').needed,10);
assert.ok(guides.filter(g=>!['Cooking','Fishing'].includes(g.name)).every(g=>workspace(d,c,g,{},100).next===null));
console.log('Guide workflow passed: cross-character preservation, validated choices, bounded batches, progress, stable step IDs, enchant vellum and eight completed primary routes.');

const vendorGuide={...g,vendor:['Expensive']},vendorView=workspace(d,c,vendorGuide,{choices:{50:'Baseline'}});assert.equal(vendorView.next.rows[0].price.source,'vendor');assert.equal(require('./guide-planner.js').guideImport(vendorView.next.rows).text,'');assert.equal(vendorView.next.buy,null);console.log('Unobserved vendor supplies stay outside auction imports and known-cost totals.');

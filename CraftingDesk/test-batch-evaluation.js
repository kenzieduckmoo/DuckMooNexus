const assert=require('node:assert/strict');
const {dailyCandidates}=require('./daily-plan.js');
const {bestProductBatch,productGroups,characterCompare}=require('./batch-evaluation.js');
const {concentrationReady}=require('./concentration-ready.js');
const now=1000;
function recipe(id,name,realm,material,cost){return {key:`c:2:q1:capture:${id}`,scope:'Alliance - '+realm,name:'Test Potion',profession:'Alchemy',materials:{[material]:2},quantity:1,output:'i:9',crafters:[{name,realm,guid:name}],capture:{quality:1,observedAt:now,concentration:cost,skillLineID:1}};}
const recipes=[recipe('a','A','One','i:1',0),recipe('b','B','Two','i:2',0),recipe('c','A','One','i:3',200)];
const snapshot={recipes,characters:['A','B'].map(name=>({guid:name,name,realm:name==='A'?'One':'Two',professions:[{id:1,name:'Midnight Alchemy',concentration:{amount:300,max:1000,observedAt:now,secondsPerPoint:10}}]})),
 catalog:['A','B'].map(guid=>({guid,recipeID:2,learned:true,observedAt:now,cooldownCaptured:true,cooldown:{seconds:0,observedAt:now}})),
 market:{commodities:{'i:1':{price:10,scope:'US'},'i:2':{price:5,scope:'US'},'i:3':{price:1,scope:'US'},'i:9':{price:100,scope:'US'}}},
 inventory:{items:{'i:1':[{owner:'A-One',location:'bags',bound:true,quantity:4}]}}};
const entries=dailyCandidates(snapshot,[],5,now);
assert.equal(productGroups(recipes).length,1);
const ordinary=bestProductBatch(snapshot,entries,2,'without','',[],now).best;
assert.equal(ordinary.entry.setup.crafterName,'B');assert.equal(ordinary.count,2);
assert.equal(ordinary.materialCost,20);assert.equal(ordinary.buy,20);assert.equal(ordinary.profit,170);
const owned=bestProductBatch(snapshot,entries.filter(e=>e.setup.crafterName==='A'),2,'without','',[],now).best;
assert.equal(owned.buy,0);assert.equal(owned.materialCost,40);assert.equal(owned.profit,150);
assert.equal(bestProductBatch(snapshot,entries,2,'with','',[],now).best,null); // Never silently shrink 2 crafts to 1.
const concentrated=bestProductBatch(snapshot,entries,1,'with','',[],now).best;
assert.equal(concentrated.rows[0].item,'i:3');assert.equal(concentrated.count,1);
let ready=concentrationReady(snapshot,entries,{},[],now);
assert.equal(ready[0].available,300);assert.equal(ready[0].best.count,1);
snapshot.characters[0].professions[0].concentration.amount=100;
ready=concentrationReady(snapshot,entries,{},[],now);
assert.equal(ready[0].best,null);assert.equal(ready[0].readyAt,2000);
snapshot.catalog[0].cooldownCaptured=false;
assert.equal(concentrationReady(snapshot,entries,{},[],now)[0].readyAt,null);
assert.ok(characterCompare({name:'Rolla',realm:'One'},{name:'Stormlesbian',realm:'Two'})<0);
console.log('Shared batch: product dedupe, full requested count, best profit, owned versus purchased materials, independent modes, sub-cap concentration and known-only ETA passed.');

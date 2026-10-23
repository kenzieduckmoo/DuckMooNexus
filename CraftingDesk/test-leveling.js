const assert=require('node:assert/strict');
const {levelingGuide,levelingText}=require('./leveling-plan.js');
const row={guid:'a',character:'A',realm:'One',recipeID:1,name:'Practice',learned:true,observedAt:1000,profession:{professionID:9,skillLevel:10,maxSkillLevel:100},relativeDifficulty:0,canSkillUp:true,numSkillUps:3,schematic:{recipeType:1,quantityMin:1,quantityMax:1,reagentSlotSchematics:{1:{required:true,quantityRequired:2,dataSlotType:2,reagents:{1:{itemID:1},2:{itemID:2}}}}}};
const snapshot={characters:[{guid:'a',name:'A',realm:'One',professions:[{id:9,rank:10,max:100,seenAt:1000}]}],catalog:[row],market:{commodities:{'i:1':{price:100},'i:2':{price:20}}},inventory:{items:{'i:2':[{owner:'A-One',quantity:1,bound:true,location:'bags'}]}}};
let g=levelingGuide(snapshot,'a',9,12,1001);assert.equal(g.choices.length,1);assert.equal(g.choices[0].plan.materialCost,40);assert.equal(g.choices[0].plan.buyCost,20);assert.equal(g.choices[0].points,2);assert.equal(g.choices[0].costPerPoint,20);
assert.ok(levelingText(g,g.choices[0],{'i:2':'Herb'},{'i:2':2}).includes('Quality 2'));
function changed(fields){return {...snapshot,catalog:[{...row,...fields}]};}
for(const fields of [{learned:false},{disabled:true},{relativeDifficulty:3},{relativeDifficulty:undefined},{profession:{...row.profession,skillLevel:9}},{cooldown:{seconds:20,charges:0}}])assert.equal(levelingGuide(changed(fields),'a',9,100,1001).choices.length,0);
assert.equal(levelingGuide(changed({relativeDifficulty:1}),'a',9,100,1001).choices[0].guaranteed,false);
assert.equal(levelingGuide({...snapshot,market:{}},'a',9,100,1001).choices.length,0);
assert.equal(levelingGuide(snapshot,'a',9,10,1001).message,'Target reached at the recorded skill.');
const newer={...snapshot,characters:[{...snapshot.characters[0],professions:[{id:9,rank:11,max:100,seenAt:1002}]}]};assert.equal(levelingGuide(newer,'a',9,100,1003).choices.length,0);
console.log('Leveling checks passed: current skill, price completeness, quality choices, inventory, target caps, unavailable recipes and chance labels');

assert.equal(levelingGuide(snapshot,'a',9,100,90000).choices.length,0);
const {levelingRoadmap}=require('./leveling-plan.js');
const own={...row,build:'test',profession:{...row.profession,skillModifier:40},numSkillUps:1};
const reference={...own,guid:'b',character:'B',profession:{...own.profession,skillLevel:14},observedAt:1000};
const routeData={...snapshot,catalog:[own,reference]};
let guide=levelingGuide(routeData,'a',9,15,1001),route=levelingRoadmap(routeData,guide,1001);
assert.equal(route.reached,15);assert.equal(route.steps.length,5);assert.equal(route.materialCost,200);
assert.equal(route.shopping[0].needed,10);assert.equal(route.shopping[0].missing,9); // own stock once, not per step
for(const bad of [{build:'other'},{profession:{...reference.profession,skillModifier:0}},{observedAt:-999999},{relativeDifficulty:1}]){
 const d={...routeData,catalog:[own,{...reference,...bad}]};assert.equal(levelingRoadmap(d,levelingGuide(d,'a',9,15,1001),1001).reached,11);
}
const multi={...own,recipeID:2,name:'Three points',numSkillUps:3,schematic:{...row.schematic,reagentSlotSchematics:{1:{required:true,quantityRequired:5,dataSlotType:1,reagents:{1:{itemID:2}}}}}};
const cheapData={...routeData,catalog:[own,reference,multi]};
route=levelingRoadmap(cheapData,levelingGuide(cheapData,'a',9,13,1001),1001);assert.equal(route.materialCost,100);assert.equal(route.steps.length,1);
console.log('Route checks passed: cheapest supported path, reference isolation, explicit gaps, target clipping and stock allocation once');

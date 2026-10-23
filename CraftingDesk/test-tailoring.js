const assert=require('node:assert/strict');
const {tailoringRoute}=require('./tailoring-route.js');
const {guideImport}=require('./guide-planner.js');
const c={guid:'a',name:'A',realm:'One',professions:[{name:'Midnight Tailoring',rank:66}]};
const names={'i:1':'Cloth','i:2':'Embroidery Floss','i:3':'Pattern: Arcanoweave Lining','i:4':'Pattern: Sunfire Silk Lining'};
function recipe(name,learned,quantity=1){return {name,recipeID:name,guid:'a',learned,observedAt:100,profession:{professionName:'Midnight Tailoring',parentProfessionName:'Tailoring',expansionName:'Midnight'},schematic:{quantityMin:1,reagentSlotSchematics:{1:{required:true,quantityRequired:quantity,reagents:{1:{itemID:1}}},2:{required:true,quantityRequired:1,reagents:{1:{itemID:2}}}}}};}
const d={inventory:{names,items:{'i:1':[{owner:'A-One',quantity:5,location:'bags',bound:true}]}},market:{commodities:{'i:1':{price:10,scope:'US'},'i:2':{price:100,scope:'US'},'i:3':{price:10000,scope:'US'},'i:4':{price:20,scope:'US'}}},catalog:[recipe('Arcanoweave Lining',false),recipe('Sunfire Silk Lining',false,2),recipe("Elegant Artisan's Cooking Hat",true)]};
let p=tailoringRoute(d,c);
assert.equal(p.skill,66);assert.equal(p.chosen,'Sunfire Silk Lining');assert.equal(p.steps[0].count,27);assert.equal(p.steps.length,2);
assert.equal(p.rows.find(r=>r.item==='i:1').needed,67);assert.equal(p.rows.find(r=>r.item==='i:1').missing,62); // stock deducted once
assert.equal(p.unlockGold,20);assert.equal(p.currency,0);
assert.ok(!guideImport(p.rows).text.includes('Embroidery Floss'));assert.ok(guideImport(p.recipes).text.includes('Pattern: Sunfire Silk Lining'));
p=tailoringRoute(d,c,{lining:'Arcanoweave Lining'});assert.equal(p.chosen,'Arcanoweave Lining');assert.equal(p.unlockGold,10000);
p=tailoringRoute(d,c,{skill:100});assert.equal(p.steps.length,0);assert.equal(p.rows.length,0);assert.equal(p.unlockGold,0);
p=tailoringRoute({...d,catalog:d.catalog.filter(r=>!r.name.includes('Cooking'))},c);assert.ok(p.issues.length);assert.equal(p.complete,false);
// Produce two grades of the same accepted intermediate; only the guaranteed base yield counts.
const bolt=recipe('Bright Linen Bolt',true);bolt.schematic.outputItemID=10;
const imbued=recipe('Imbued Bright Linen Bolt',true);imbued.schematic.reagentSlotSchematics={1:{required:true,quantityRequired:2,reagents:{1:{itemID:10}}}};
const dd={...d,inventory:{names:{...names,'i:10':'Bright Linen Bolt'},items:{}},market:{commodities:{...d.market.commodities,'i:10':{price:10,scope:'US'}}},catalog:[...d.catalog,bolt,imbued]};
p=tailoringRoute(dd,c,{skill:1});assert.ok(!p.rows.some(r=>r.item==='i:10'));assert.equal(p.rows.find(r=>r.item==='i:1').needed,135);
console.log('Tailoring tests passed: remaining skill, acquisition-aware choice, override, shared stock once, vendor exclusion, owned unlocks, completed route, missing schematics and intermediate reuse.');
// An owned, unlearned pattern avoids a duplicate purchase and its acquisition cost.
const ownedPattern={...d,inventory:{...d.inventory,items:{...d.inventory.items,'i:3':[{owner:'A-One',quantity:1,location:'bags',bound:true}]}}};
p=tailoringRoute(ownedPattern,c,{lining:'Arcanoweave Lining'});assert.equal(p.unlockGold,0);assert.equal(p.recipes[0].missing,0);
const noPatternPrice={...d,market:{commodities:{'i:1':{price:10,scope:'US'},'i:2':{price:100,scope:'US'}}}};
p=tailoringRoute(noPatternPrice,c,{lining:'Arcanoweave Lining'});assert.equal(p.unlockGold,null);
console.log('Owned pattern and unknown acquisition price tests passed.');
const restricted={...dd,inventory:{...dd.inventory,names:{...dd.inventory.names,'i:11':'Bright Linen Bolt'}}};
p=tailoringRoute(restricted,c,{skill:1});assert.equal(p.rows.find(r=>r.item==='i:10').needed,28); // unknown produced grade cannot satisfy a restricted slot
assert.equal(p.buy,null); // missing early recipe details cannot produce a complete total
console.log('Restricted-quality intermediate and incomplete-total checks passed.');

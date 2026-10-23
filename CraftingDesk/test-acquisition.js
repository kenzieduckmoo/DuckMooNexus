const assert=require('node:assert/strict');
const {acquisitionStatus,recipeOffers}=require('./acquisition.js');
const offer={guid:'one',recipeID:123,kind:'trainer',observedAt:1000,status:'available',price:100,money:100};
assert.match(acquisitionStatus(offer,1001),/gold covered/);
assert.match(acquisitionStatus({...offer,money:99},1001),/short on gold/);
assert.match(acquisitionStatus({...offer,price:null},1001),/unknown/);
assert.match(acquisitionStatus({...offer,hasSkill:false},1001),/unmet/);
assert.match(acquisitionStatus({...offer,requirements:[{met:false}]},1001),/unmet/);
assert.match(acquisitionStatus(offer,90000),/Older/);
assert.match(acquisitionStatus({...offer,isProfession:true},1001),/slots/);
const vendor={kind:'vendor',observedAt:1000,isPurchasable:true,canAfford:true};
assert.match(acquisitionStatus(vendor,1001),/learning requirements still need checking/);
assert.match(acquisitionStatus({...vendor,numAvailable:0},1001),/Out of stock/);
assert.match(acquisitionStatus({...vendor,isPurchasable:false},1001),/restricted/);
assert.match(acquisitionStatus({...vendor,canAfford:false},1001),/Insufficient/);
assert.equal(recipeOffers({acquisitionOffers:[offer,{...offer,guid:'two'},{...vendor,name:'same',guid:'one',itemID:123}]},{guid:'one',recipeID:123}).length,1);
console.log('Acquisition checks passed: character isolation, exact IDs, unknown costs, stale observations, requirements and purchase/learning distinction');

const {offerRecipeMatch,learningOpportunities,learningChecklist}=require('./acquisition.js');
const {levelingGuide}=require('./leveling-plan.js');
const recipe={guid:'one',character:'A',realm:'Realm',recipeID:11,name:'New ink',learned:false,build:'test',observedAt:1000,
 profession:{professionID:9,professionName:'Test Inscription',skillLevel:10,maxSkillLevel:100,skillModifier:0},
 relativeDifficulty:0,canSkillUp:true,numSkillUps:1,cooldownCaptured:true,cooldown:{seconds:0},
 schematic:{outputItemID:55,recipeType:1,quantityMin:1,quantityMax:1,reagentSlotSchematics:{1:{required:true,quantityRequired:1,dataSlotType:1,reagents:{1:{itemID:1}}}}}};
const trainer={...offer,recipeID:undefined,build:'test',name:'New ink',skill:'Test Inscription',link:'|Hitem:55|h[New ink]|h',price:20,money:100,npcName:'Trainer'};
const known={...recipe,recipeID:12,name:'Known ink',learned:true,schematic:{...recipe.schematic,outputItemID:56,reagentSlotSchematics:{1:{required:true,quantityRequired:5,dataSlotType:1,reagents:{1:{itemID:1}}}}}};
const data={characters:[{guid:'one',name:'A',realm:'Realm',professions:[{id:9,rank:10,max:100,seenAt:1000}]}],catalog:[recipe,known],acquisitionOffers:[trainer],market:{commodities:{'i:1':{price:10}}},inventory:{items:{'i:1':[{owner:'A-Realm',quantity:1,bound:true,location:'bags'}]}}};
assert.match(offerRecipeMatch(data,trainer,recipe),/Unique output/);
for(const change of [{name:'Different'},{skill:'Another expansion'},{link:'item:99'},{guid:'other'},{kind:'vendor'},{isProfession:true}])assert.equal(offerRecipeMatch(data,{...trainer,...change},recipe),null);
assert.equal(offerRecipeMatch({...data,catalog:[...data.catalog,{...recipe,recipeID:99}]},trainer,recipe),null);
function evaluate(d=data,target=11){return learningOpportunities(d,levelingGuide(d,'one',9,target,1001),1001);}
const original=JSON.stringify(data);let opportunities=evaluate();assert.equal(opportunities.length,1);
let option=opportunities[0];assert.ok(option.ready);assert.equal(option.total,30);assert.equal(option.buyCost,20);assert.equal(option.baseline,50);assert.equal(option.savings,20);
assert.match(learningChecklist(levelingGuide(data,'one',9,11,1001),option,{'i:1':'Herb'},{'i:1':2}),/Quality 2/);
assert.equal(JSON.stringify(data),original);assert.equal(levelingGuide(data,'one',9,11,1001).choices.length,1);
for(const change of [{build:'old'},{observedAt:-90000},{observedAt:2000},{status:'unavailable'},{status:'used'},{price:null},{price:-1},{money:0},{hasSkill:false},{requirements:[{met:false}]}])assert.equal(evaluate({...data,acquisitionOffers:[{...trainer,...change}]})[0].ready,false);
for(const change of [{observedAt:-90000},{cooldownCaptured:false},{relativeDifficulty:1},{disabled:true},{cooldown:{seconds:10}},{profession:{...recipe.profession,skillLevel:9}}])assert.equal(evaluate({...data,catalog:[{...recipe,...change},known]})[0].ready,false);
assert.equal(evaluate({...data,market:{}})[0].ready,false);
assert.equal(evaluate({...data,catalog:[recipe]})[0].baseline,null);
assert.equal(evaluate({...data,acquisitionOffers:[trainer,{...trainer,status:'unavailable',observedAt:1001}]})[0].ready,false);
// Training is paid once; multi-point crafts compare against the same target, with stock used only once.
const multi={...recipe,numSkillUps:3};const reference={...known,guid:'two',character:'B',profession:{...known.profession,skillLevel:12}};
option=evaluate({...data,catalog:[multi,known,reference]},13)[0];assert.equal(option.baseline,150);assert.equal(option.total,30);assert.equal(option.savings,120);
assert.equal(evaluate({...data,catalog:[multi,known,reference]},11)[0].choice.points,1);
console.log('Learning checks passed: conditional ownership, unique trainer association, ambiguity rejection, same-target comparison, one training fee, unknown evidence and latest visit precedence');

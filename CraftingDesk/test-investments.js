const assert=require('node:assert/strict'),{recipeInvestments}=require('./recipe-investments.js');
const now=1000,c={guid:'a',name:'A',realm:'One',professions:[]};
const s={characters:[c],recipes:[{key:'c:2:q1',scope:'Alliance - One',name:'Thing',profession:'Alchemy',materials:{'i:1':1},quantity:2,output:'i:2',crafters:[c],capture:{observedAt:now,concentration:0,skillLineID:1}}],inventory:{names:{'i:3':'Recipe: Thing'},items:{}},market:{commodities:{'i:1':{price:100},'i:2':{price:100},'i:3':{price:900}},sales:{'i:2':{saleRate:.2,dailySold:4}}},catalog:[{guid:'b',name:'Thing',learned:false,observedAt:now,profession:{parentProfessionName:'Alchemy'}}]};
const learner={guid:'b',name:'B',realm:'Two'};
let rows=recipeInvestments(s,'Alchemy',now,learner);assert.equal(rows.length,1);assert.equal(rows[0].salesToRecover,20);assert.equal(rows[0].learningKnown,true);
s.catalog[0].learned=true;assert.equal(recipeInvestments(s,'Alchemy',now,learner).length,0);
s.catalog[0].learned=false;delete s.market.commodities['i:3'];
const offer={kind:'vendor',itemID:3,observedAt:now,price:0,stackCount:1,isPurchasable:true,numAvailable:-1,hasExtendedCost:true,costsComplete:true,costs:[{amount:150,name:'Moxie'}]};s.acquisitionOffers=[offer];assert.equal(recipeInvestments(s,'Alchemy',now,learner).length,1);
for(const patch of [{observedAt:now+301},{costsComplete:false},{numAvailable:0},{isPurchasable:false}]){s.acquisitionOffers=[{...offer,...patch}];assert.equal(recipeInvestments(s,'Alchemy',now,learner).length,0);}
console.log('Recipe investments: strict eligibility, per-output payback, learner known status and complete current vendor offers passed.');

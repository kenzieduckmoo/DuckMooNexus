from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'CraftingDesk'/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('NS={}; assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Model.lua'))
lua.execute(r'''
local M=NS.Model
local schema={reagentSlotSchematics={{dataSlotType=1,dataSlotIndex=1,required=true,quantityRequired=3}}}
local allocations={{dataSlotType=1,dataSlotIndex=1,reagent={itemID=1},quantity=1},{dataSlotType=1,dataSlotIndex=1,reagent={itemID=2},quantity=2}}
local result=M.ValidateReagents(schema,allocations)
assert(result.items[1]==1 and result.items[2]==2)
assert(not M.ValidateReagents(schema,{}))
assert(not M.ValidateReagents(schema,{{dataSlotType=1,dataSlotIndex=1,reagent={currencyID=1},quantity=3}}))
local c={}
for i=1,301 do M.Store(c,{recipeID=i,reagentSignature='same',applyConcentration=false,observedAt=i}) end
local count=0;for _ in pairs(c.operations) do count=count+1 end
assert(count==300 and not c.operations['1|same|false'])
assert(M.Copy({n=0,flag=false,bad=function()end}).flag==false)

printed={}; print=function(value)table.insert(printed,value)end
function InCombatLockdown() return false end
function UnitGUID() return 'Player-test' end
function UnitName() return 'Tester' end
function GetRealmName() return 'TestRealm' end
function UnitFactionGroup() return 'Alliance' end
function GetBuildInfo() return '12.1.0','69933','date',120100 end
function GetServerTime() return 1000 end
Enum={TradeskillRecipeType={Item=1},TradeskillSlotDataType={ModifiedReagent=1,Reagent=2,Currency=3}}
SlashCmdList={};C_Timer={After=function(_,fn)fn()end}
CreateFrame=function()return {RegisterEvent=function()end,SetScript=function()end}end
local txn={IsRecraft=function()return false end,
 CreateCraftingReagentInfoTbl=function()return {{dataSlotType=1,dataSlotIndex=1,reagent={itemID=11},quantity=2}}end,
 CreateReagentInfoTbl=function()return {{dataSlotType=2,dataSlotIndex=2,reagent={itemID=12},quantity=1}}end,
 GetAllocationItemGUID=function()return nil end}
local info={recipeID=123,name='Test recipe',learned=true,qualityIDs={10,20}}
local form={IsShown=function()return true end,GetTransaction=function()return txn end,GetRecipeInfo=function()return info end}
ProfessionsFrame={CraftingPage={IsShown=function()return true end,SchematicForm=form}}
C_TradeSkillUI={
 IsTradeSkillLinked=function()return false end,IsTradeSkillGuild=function()return false end,
 GetRecipeSchematic=function()return {recipeType=1,quantityMin=2,quantityMax=2,reagentSlotSchematics={{dataSlotType=1,dataSlotIndex=1,required=true,quantityRequired=2},{dataSlotType=2,dataSlotIndex=2,required=true,quantityRequired=1}}}end,
 GetProfessionInfoByRecipeID=function()return {professionID=2906,professionName='Alchemy'}end,
 GetCraftingOperationInfo=function(_,reagents,_,apply)
   assert(#reagents==1 and reagents[1].reagent.itemID==11)
   return {isQualityCraft=true,craftingQuality=apply and 2 or 1,concentrationCost=100}
 end,
 GetRecipeOutputItemData=function(_,_,_,quality)return {itemID=quality==20 and 101 or 100}end
}
''')
lua.execute('assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Core.lua'))
lua.execute(r'''
NS.Capture()
local c=DuckMooCaptureDB.characters['Player-test']
local count=0;for _,record in pairs(c.operations)do
 count=count+1;assert(record.quantity==2 and record.skillLineID==2906)
 assert(record.materials[11]==2 and record.materials[12]==1)
 assert(record.output.itemID==(record.applyConcentration and 101 or 100))
end
assert(count==2)
C_TradeSkillUI.GetCraftingOperationInfo=function()return nil end
NS.Capture()
local retained=0;for _ in pairs(c.operations)do retained=retained+1 end
assert(retained==2)
ProfessionsFrame.CraftingPage.IsShown=function()return false end
NS.Capture();assert(#printed>0)
''')
print('Lua 5.1 capture tests passed: both modes, exact allocations, mixed qualities, incomplete/currency rejection, prior-record retention, and record cap')
lua.execute(r'''
local form=ProfessionsFrame.CraftingPage.SchematicForm
ProfessionsFrame.IsShown=function()return true end
ProfessionsFrame.CraftingPage.IsShown=function()return true end
form.Init=function()end;form.UpdateDetailsStats=function()end
hooks={};hooksecurefunc=function(_,name,callback)hooks[name]=callback end
timers={};C_Timer.After=function(_,fn)table.insert(timers,fn)end
CreateFrame=function()
 passiveFrame={RegisterEvent=function()end,SetScript=function(self,_,callback)self.event=callback end}
 return passiveFrame
end
local txn=form:GetTransaction()
txn.CreateCraftingReagentInfoTbl=function()return {}end
txn.CreateReagentInfoTbl=function()return {}end
C_TradeSkillUI.GetRecipeSchematic=function()return {recipeType=1,quantityMin=2,quantityMax=2,reagentSlotSchematics={
 {dataSlotType=1,dataSlotIndex=1,required=true,quantityRequired=2,reagents={{itemID=11},{itemID=13}}},
 {dataSlotType=2,dataSlotIndex=2,required=true,quantityRequired=1,reagents={{itemID=12}}}}}end
queries=0
C_TradeSkillUI.GetCraftingOperationInfo=function(_,reagents,_,apply)
 queries=queries+1;assert(#reagents==1)
 return {isQualityCraft=true,craftingQuality=apply and 2 or 1,concentrationCost=100}
end
C_TradeSkillUI.GetAllRecipeIDs=function()return {123,124}end
C_TradeSkillUI.GetRecipeInfo=function(id)return {recipeID=id,name='Catalog '..id,learned=id==123}end
''')
lua.execute('assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Passive.lua'))
lua.execute(r'''
NS.HookForm();NS.HookForm();assert(hooks.Init and hooks.UpdateDetailsStats)
local before=#printed
for i=1,20 do hooks.Init() end
assert(#timers==1)
table.remove(timers,1)()
assert(queries==4 and #printed==before) -- both modes for two presets, no chat spam or materials
local c=DuckMooCaptureDB.characters['Player-test']
local preview=0;for _,r in pairs(c.operations)do if r.source=='schematic-preview' then preview=preview+1 end end
assert(preview==4)
NS.ScanCatalog();assert(c.recipes[123].info.learned and c.recipes[124].info.learned==false)
C_TradeSkillUI.IsTradeSkillLinked=function()return true end
hooks.Init();table.remove(timers,1)();assert(queries==4)
-- A catalog scan cannot attribute a linked profession to the current character.
c.recipes[124]=nil;NS.ScanCatalog();assert(c.recipes[124]==nil)
C_TradeSkillUI.IsTradeSkillLinked=function()return false end
hooks.Init();ProfessionsFrame.IsShown=function()return false end
table.remove(timers,1)();assert(queries==4)
''')
print('Passive tests passed: coalesced hooks, empty-bag previews, silent operation, catalog capture, linked-profession guard, and hidden-frame cancellation')
lua.execute('assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Combinations.lua'))
lua.execute(r'''
local schema=C_TradeSkillUI.GetRecipeSchematic()
local combos,total=NS.ReagentCombinations(schema,64)
assert(#combos==3 and total==3)
assert(#combos[3]==3) -- mixed modified slot plus a regular reagent
for _,combo in ipairs(combos)do assert(NS.Model.ValidateReagents(schema,combo)) end
local limited,full=NS.ReagentCombinations(schema,2);assert(#limited==2 and full==3)
schema.reagentSlotSchematics[1].quantityRequired=100
local bounded,total=NS.ReagentCombinations(schema,64);assert(#bounded==64 and total==101)
schema.reagentSlotSchematics[1].reagents[3]={itemID=14};schema.reagentSlotSchematics[1].quantityRequired=2
local three,full=NS.ReagentCombinations(schema,64);assert(#three==6 and full==6)
schema.reagentSlotSchematics[1].reagents[1]={currencyID=5}
assert(not NS.ReagentCombinations(schema,64))
ProfessionsFrame.IsShown=function()return true end
timers={};queries=0
C_TradeSkillUI.GetChildProfessionInfo=function()return {professionID=2906}end
C_TradeSkillUI.GetRecipeInfo=function(id)return {recipeID=id,name='Scanned '..id,learned=id==123,qualityIDs={10,20}}end
C_TradeSkillUI.GetCraftingOperationInfo=function(id,reagents,guid,apply)
 queries=queries+1;assert(id==123 and guid==nil)
 local n=0;for _,r in ipairs(reagents)do n=n+r.quantity end;assert(n==2)
 return {recipeID=id,isQualityCraft=true,craftingQuality=apply and 2 or 1,concentrationCost=100,bonusStats={{ratingPct=12}}}
end
''')
lua.execute('assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Scanner.lua'))
lua.execute(r'''
NS.StartScanner();NS.StartScanner();assert(#timers==1)
local function drain()
 local n=0
 while #timers>0 do n=n+1;assert(n<1000);table.remove(timers,1)() end
end
-- Close during queued work: no queries and no data loss.
ProfessionsFrame.IsShown=function()return false end;drain();assert(queries==0)
ProfessionsFrame.IsShown=function()return true end;NS.StartScanner();drain()
local c=DuckMooCaptureDB.characters['Player-test']
assert(queries==6 and c.scanStatus[2906].state=='Finished')
assert(c.scanStatus[2906].checked==2 and c.scanStatus[2906].skipped==1)
assert(c.scannedRecipes[123].totalCombinations==3)
local count=0;for _,r in pairs(c.scannedRecipes[123].outcomes)do count=count+1;assert(r.operation.bonusStats[1].ratingPct==12)end
assert(count==6)
NS.StartScanner();drain();assert(queries==6) -- finished sessions do not loop forever
NS.StartScanner(true);InCombatLockdown=function()return true end;drain();assert(queries==6)
InCombatLockdown=function()return false end
local prior=c.scannedRecipes[123]
C_TradeSkillUI.GetCraftingOperationInfo=function()return nil end
NS.StartScanner();drain();assert(c.scannedRecipes[123]==prior and prior.lastAttemptUnavailable)
-- Profession source change cancels pending work before any API query.
NS.StartScanner(true);NS.StopScanner('Paused');drain();assert(queries==6)
C_TradeSkillUI.IsTradeSkillLinked=function()return true end;NS.StartScanner(true);assert(#timers==0)
''')
print('Scanner tests passed: mixed qualities, caps, both modes, bonus stats, pause/resume, combat/source guards, no repeated scans, and unavailable-data retention')
lua.execute(r'''
C_TradeSkillUI.IsTradeSkillLinked=function()return false end
C_TradeSkillUI.GetChildProfessionInfo=function()return {professionID=0}end
NS.StartScanner(true);assert(#timers==0)
assert(DuckMooCaptureDB.characters['Player-test'].scanStatus[0]==nil)
''')
print('Transient profession-zero guard passed')
lua.execute(r'''
local schema={recipeType=1,quantityMin=1,quantityMax=1,reagentSlotSchematics={}}
for i=1,3 do schema.reagentSlotSchematics[i]={required=true,quantityRequired=20,dataSlotType=Enum.TradeskillSlotDataType.ModifiedReagent,dataSlotIndex=i,reagents={{itemID=i*10},{itemID=i*10+1}}} end
local combos,total=NS.ReagentCombinations(schema,256)
assert(#combos==256 and total==21*21*21)
local varied={{},{},{}};local seen={}
for _,allocations in ipairs(combos) do
 local valid=NS.Model.ValidateReagents(schema,allocations);assert(valid and not seen[valid.signature]);seen[valid.signature]=true
 for slot=1,3 do varied[slot][valid.items[slot*10+1] or 0]=true end
end
for slot=1,3 do local n=0;for _ in pairs(varied[slot])do n=n+1 end;assert(n>=18) end
local repeated=NS.ReagentCombinations(schema,256)
for i=1,#combos do assert(NS.Model.ValidateReagents(schema,combos[i]).signature==NS.Model.ValidateReagents(schema,repeated[i]).signature) end
''')
print('Broad-search checks passed: deterministic unique samples, conserved quantities and mixed coverage in every slot')
lua.execute(r'''
C_TradeSkillUI.GetChildProfessionInfo=function()return {professionID=2906}end
C_TradeSkillUI.GetRecipeSchematic=function()return {recipeType=1,quantityMin=1,quantityMax=1,reagentSlotSchematics={{required=true,quantityRequired=20,dataSlotType=1,dataSlotIndex=1,reagents={{itemID=11},{itemID=12}}}}}end
local skill=100
C_TradeSkillUI.GetCraftingOperationInfo=function(id,reagents,guid,apply)
 queries=queries+1
 return {recipeID=id,baseSkill=skill,bonusSkill=0,baseDifficulty=200,isQualityCraft=true,craftingQuality=apply and 2 or 1,concentrationCost=100}
end
local c=DuckMooCaptureDB.characters['Player-test']
timers={};queries=0
NS.StartScanner(true);table.remove(timers,1)()
assert(queries>1 and queries<=8) -- batched work, not one query per timer
local before=queries;local saved=c.scanStatus[2906]
assert(c.scannerCache[2906].current and next(c.scannerCache[2906].current.outcomes))
assert(not c.scannedRecipes[123].partial) -- complete prior results survive a partial replacement
ProfessionsFrame.IsShown=function()return false end
NS.ScannerEvent(nil,'TRADE_SKILL_CLOSE')
while #timers>0 do table.remove(timers,1)() end
assert(queries==before and c.scanStatus[2906]==saved)
ProfessionsFrame.IsShown=function()return true end
NS.StartScanner();table.remove(timers,1)()
assert(queries>before and c.scanStatus[2906]==saved)
NS.ScannerEvent(nil,'UNIT_AURA','player')
NS.ScannerEvent(nil,'UNIT_AURA','player')
while #timers>0 do table.remove(timers,1)() end
assert(c.scanStatus[2906]==saved and saved.state=='Finished') -- irrelevant aura retained job
assert(not c.scannedRecipes[123].partial and c.scannedRecipes[123].combinations==21)
skill=101
NS.ScannerEvent(nil,'UNIT_AURA','player')
while #timers>0 do table.remove(timers,1)() end
assert(c.scanStatus[2906]~=saved and c.scanStatus[2906].state=='Finished') -- real stat change rebuilt
for _,outcome in pairs(c.scannedRecipes[123].outcomes)do assert(outcome.operation.baseSkill==101)end
''')
print('Speed/resume checks passed: bounded batches, partial checkpoints, close/reopen continuation, aura coalescing and real-stat invalidation')
lua.execute(r'''
C_TradeSkillUI.GetProfessionInfoByRecipeID=function()return {professionID=2906,skillLevel=10,skillModifier=40}end
C_TradeSkillUI.GetRecipeSourceText=function()return 'Learn from a trainer' end
NS.RememberRecipe({recipeID=999,name='History test',relativeDifficulty=0,numSkillUps=1,canSkillUp=true},nil)
C_TradeSkillUI.GetProfessionInfoByRecipeID=function()return {professionID=2906,skillLevel=11,skillModifier=40}end
C_TradeSkillUI.GetRecipeSourceText=function()return nil end
NS.RememberRecipe({recipeID=999,name='History test',relativeDifficulty=1,numSkillUps=1,canSkillUp=true},nil)
local r=DuckMooCaptureDB.characters['Player-test'].recipes[999]
assert(r.skillHistory[10].difficulty==0 and r.skillHistory[11].difficulty==1)
assert(r.sourceText=='Learn from a trainer' and r.sourceObservedAt==1000)
GetBuildInfo=function()return '12.1','new-build','date',120100 end
NS.RememberRecipe({recipeID=999,name='History test',relativeDifficulty=1,numSkillUps=1,canSkillUp=true},nil)
assert(r.skillHistory[10]==nil and r.skillHistory[11])
''')
print('Leveling capture checks passed: per-rank history, source retention and build invalidation')
lua.execute('assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Acquisition.lua'))
lua.execute(r'''
UnitGUID=function(unit)return unit=='npc' and 'Creature-0-1-2-3-456-0001' or 'Player-test' end
ClassTrainerFrame={IsShown=function()return true end}
MerchantFrame={IsShown=function()return true end}
GetMoney=function()return 100 end
GetNumTrainerServices=function()return 1 end
GetTrainerServiceInfo=function()return 'Trainer recipe','available',999,10 end
GetTrainerServiceItemLink=function()return '|Hspell:123|h[Trainer recipe]|h' end
GetTrainerServiceCost=function()return 100,false end
GetTrainerServiceSkillReq=function()return 'Alchemy',20,false end
GetTrainerServiceNumAbilityReq=function()return 1 end
GetTrainerServiceAbilityReq=function()return 'Prerequisite',false end
GetMerchantNumItems=function()return 2 end
C_MerchantFrame={GetItemInfo=function()return {name='Vendor recipe',price=0,stackCount=1,numAvailable=-1,isPurchasable=false,hasExtendedCost=true}end}
GetMerchantItemLink=function(i)return 'item:'..i end
C_Item=C_Item or {}
C_Item.GetItemInfoInstant=function(link)return tonumber(link:match('%d+')),nil,nil,nil,nil,link=='item:1' and 9 or 7 end
GetMerchantItemCostInfo=function()return 1 end
GetMerchantItemCostItem=function()return 1,20,'|Hcurrency:7|h[Test currency]|h','Test currency' end
CanAffordMerchantItem=function()return false end
C_TooltipInfo={GetMerchantItem=function()return {lines={{leftText='Requires Renown 10'}}}end}
NS.CaptureTrainerOffers();NS.CaptureVendorOffers()
local c=NS.Character();local t=c.acquisitionOffers['trainer:456:123'];local v=c.acquisitionOffers['vendor:456:1']
assert(t.recipeID==123 and t.status=='available' and t.requiredLevel==10 and t.hasSkill==false and t.requirements[1].met==false)
assert(v.itemID==1 and v.recipeID==nil and v.canAfford==false and v.costs[1].amount==20 and v.costsComplete and v.tooltip[1]=='Requires Renown 10')
assert(c.acquisitionOffers['vendor:456:2'].itemClass==7)
GetMerchantItemCostInfo=function()return nil end
NS.CaptureVendorOffers();assert(not c.acquisitionOffers['vendor:456:1'].costsComplete)
MerchantFrame.IsShown=function()return false end
local old=c.acquisitionOffers['vendor:456:1'];NS.CaptureVendorOffers();assert(old==c.acquisitionOffers['vendor:456:1'])
timers={};NS.AcquisitionEvent();NS.AcquisitionEvent();assert(#timers==1)
ClassTrainerFrame.IsShown=function()return false end
table.remove(timers,1)();assert(old==c.acquisitionOffers['vendor:456:1'])
''')
print('Acquisition capture checks passed: Retail trainer fields, recipe-only vendors, currency costs, requirements, close guard and coalesced events')

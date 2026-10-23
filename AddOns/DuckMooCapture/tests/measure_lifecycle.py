"""Focused query-count harness for scanner lifecycle and retained checkpoints."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'Nexus/test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('NS={};assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Model.lua'))
lua.execute(r'''
local c={name='Tester',realm='Realm'}
function NS.Character()return c end
function NS.OwnProfession()return true end
function NS.Call(fn,...)if type(fn)~='function'then return nil end;local ok,value=pcall(fn,...);if ok then return value end end
function NS.RememberRecipe()end
function GetServerTime()return 1000 end
function GetBuildInfo()return 'test','12345','date',120100 end
function InCombatLockdown()return false end
Enum={TradeskillSlotDataType={ModifiedReagent=1},TradeskillRecipeType={Item=1}}
SlashCmdList={};CreateFrame=function()return {RegisterEvent=function()end,SetScript=function()end}end
ProfessionsFrame={IsShown=function()return true end,CraftingPage={IsShown=function()return true end}}
timers={};C_Timer={After=function(_,fn)table.insert(timers,fn)end}
function drain()local count=0;while #timers>0 do count=count+1;assert(count<1000);table.remove(timers,1)()end end
queries=0;skill=100;unavailable=false
C_TradeSkillUI={GetChildProfessionInfo=function()return {professionID=1,skillLevel=skill}end,
 GetAllRecipeIDs=function()return {123}end,
 GetRecipeInfo=function(id)return {recipeID=id,name='Test',learned=true}end,
 GetProfessionInfoByRecipeID=function()return {professionID=1}end,
 GetRecipeSchematic=function()return {recipeType=1,quantityMin=1,quantityMax=1,reagentSlotSchematics={{dataSlotType=1,dataSlotIndex=1,required=true,quantityRequired=1}}}end,
 GetCraftingOperationInfo=function(id,_,_,apply)queries=queries+1;if unavailable then return nil end;return {recipeID=id,baseSkill=skill,bonusSkill=0,baseDifficulty=1,bonusDifficulty=0,concentrationCost=apply and 100 or 0,bonusStats={}}end,
 GetRecipeOutputItemData=function()return {itemID=456}end}
function NS.ReagentCombinations()return {{{dataSlotType=1,dataSlotIndex=1,quantity=1,reagent={itemID=1}}},{{dataSlotType=1,dataSlotIndex=1,quantity=1,reagent={itemID=2}}},{{dataSlotType=1,dataSlotIndex=1,quantity=1,reagent={itemID=3}}}},3 end
''')
lua.execute('assert(loadfile(...))("DuckMooCapture",NS)',str(ROOT/'Scanner.lua'))
lua.execute('NS.StartScanner();drain();first=queries;NS.ScannerEvent(nil,"TRADE_SKILL_CLOSE");NS.StartScanner();drain();reopen=queries-first;before=queries;NS.ScannerEvent(nil,"SKILL_LINES_CHANGED");drain();skillEvent=queries-before')
lua.execute('before=queries;assert(loadfile(...))("DuckMooCapture",NS);NS.StartScanner();drain();reload=queries-before',str(ROOT/'Scanner.lua'))
result={key:int(lua.globals()[key]) for key in ('first','reopen','skillEvent','reload')}
print(json.dumps(result))
lua.execute(r'''
local c=NS.Character();local old=c.scannedRecipes[123];local status=c.scanStatus[1]
unavailable=true;NS.ScannerEvent(nil,'UNIT_AURA','player');drain()
assert(c.scannedRecipes[123]==old and c.scanStatus[1]==status) -- missing APIs do not restart
unavailable=false;NS.StartScanner();drain()
traitRank=1
C_ProfSpecs={GetConfigIDForSkillLine=function()return 42 end}
C_Traits={GetConfigInfo=function()return {treeIDs={7}}end,GetTreeNodes=function()return {8}end,
 GetNodeInfo=function()return {activeRank=traitRank,activeEntry={entryID=9}}end}
NS.StartScanner(true);drain();local prior=c.scanStatus[1]
traitRank=2;NS.ScannerEvent(nil,'TRAIT_CONFIG_UPDATED');drain()
assert(c.scanStatus[1]~=prior) -- changed specialization invalidates even with the same first recipe stats
perRecipeSkill=100
C_TradeSkillUI.GetAllRecipeIDs=function()return {123,124}end
C_TradeSkillUI.GetCraftingOperationInfo=function(id,_,_,apply)
 queries=queries+1
 return {recipeID=id,baseSkill=id==124 and perRecipeSkill or 100,bonusSkill=0,baseDifficulty=1,bonusDifficulty=0,concentrationCost=apply and 100 or 0,bonusStats={}}
end
NS.StartScanner(true);drain();prior=c.scanStatus[1]
perRecipeSkill=101;NS.ScannerEvent(nil,'UNIT_AURA','player');drain()
assert(c.scanStatus[1]~=prior)
for _,outcome in pairs(c.scannedRecipes[124].outcomes)do assert(outcome.operation.baseSkill==101)end
''')
print('Lifecycle safety: transient API failure retains results; specialization and second-recipe stat changes invalidate correctly.')

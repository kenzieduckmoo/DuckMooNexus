"""Focused Lua 5.1 checks. Mocks validate logic, not live-client API behavior."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parent.parent
sys.path.insert(0,str(WORKSPACE/'Nexus/test-deps'))
sys.path.insert(0,str(WORKSPACE/'Nexus/clean-install/app'))
from lupa.lua51 import LuaRuntime
from omni_adapter import omni_rows
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
NOW=1792770000;timers={};SlashCmdList={};O={};WOW_PROJECT_ID=1
function GetServerTime() return NOW end
function UnitGUID() return 'Player-104-1234ABCD' end
function UnitName() return 'CaptureFixture' end
function GetRealmName() return 'Malygos' end
function GetNumSavedInstances() return 0 end
function GetBuildInfo() return '12.1.5','70077','',120105 end
function InCombatLockdown() return false end
function issecretvalue(v) return v=='SECRET_FIXTURE' end
C_Timer={After=function(_,fn) timers[#timers+1]=fn end}
function CreateFrame() local f={};function f:RegisterEvent() end;function f:SetScript(_,fn) self.event=fn end;FRAME=f;return f end
C_CurrencyInfo={GetCurrencyListSize=function() return 1 end,GetCurrencyListInfo=function() return {currencyID=3310,isHeader=false} end,GetCurrencyInfo=function(id) return {name='Named currency fixture',quantity=12,iconFileID=123,description='SECRET_FIXTURE'} end}
Enum={WeeklyRewardChestThresholdType={Activities=1,Raid=3,World=6}}
C_WeeklyRewards={GetActivities=function() return {{id=1,type=6,index=1,progress=4,threshold=2}} end,HasAvailableRewards=function() return false end}
C_DateAndTime={GetSecondsUntilWeeklyReset=function() return 600 end}
NUM_TOTAL_EQUIPPED_BAG_SLOTS=5
C_Container={GetContainerNumSlots=function(bag) assert(bag>=0 and bag<=5);return bag==0 and 3 or 0 end,GetContainerNumFreeSlots=function(bag) return bag==0 and 2 or 0 end,GetBagName=function(bag) return 'Fixture bag '..bag end,GetContainerItemInfo=function(bag,slot) if bag==0 and slot==1 then return {itemID=123,stackCount=2,isBound=true,quality=2,hyperlink='|Hitem:123|h[Named bag fixture]|h',iconFileID=42} end end}
C_Reputation={GetNumFactions=function() return 1 end,GetFactionDataByIndex=function() return {factionID=100} end,GetFactionDataByID=function() return {name='Fixture faction',reaction=5,currentStanding=1250,currentReactionThreshold=0,nextReactionThreshold=3000,isAccountWide=true} end}
C_MajorFactions={GetMajorFactionData=function() return {renownLevel=12,renownReputationEarned=750,renownLevelThreshold=2500} end}
''')
for name in ('Model.lua','Capture.lua','Core.lua'):
    lua.execute('assert(loadstring(...))("DuckMooOmniCapture",O)',(ROOT/name).read_text(encoding='utf-8'))
lua.execute('''
O.Init();O.Scan('test')
local c=O.Character()
assert(c.sections.currencies.data[3310].name=='Named currency fixture')
assert(c.sections.currencies.data[3310].description==nil)
assert(c.sections.vault.data.tracks.world[1].progress==4)
assert(c.sections.inventory.status=='captured')
assert(c.sections.inventory.data.bags[0].items[1].name=='Named bag fixture')
assert(c.sections.inventory.data.bags[0].items[1].isBound==true)
assert(c.sections.reputations.data[100].renownLevel==12 and c.sections.reputations.data[100].accountWide==true)
local container=C_Container;C_Container=nil;O.Scan('unavailable',{inventory=true})
assert(c.sections.inventory.status=='unavailable' and c.sections.inventory.data.bags[0].items[1].quantity==2)
C_Container=container
local getItem=C_Container.GetContainerItemInfo
C_Container.GetContainerItemInfo=function() return nil end
C_Container.GetContainerNumFreeSlots=function(bag) return bag==0 and 3 or 0 end
O.Scan('empty',{inventory=true});assert(next(c.sections.inventory.data.bags[0].items)==nil and c.sections.inventory.status=='captured')
C_Container.GetContainerItemInfo=getItem;C_Container.GetContainerNumFreeSlots=function(bag) return bag==0 and 2 or 0 end
O.Scan('restore',{inventory=true})
local old=c.sections.vault.observedAt
NOW=NOW+10;C_WeeklyRewards.GetActivities=nil;O.Scan('retry',{vault=true})
assert(c.sections.vault.status=='unavailable' and c.sections.vault.observedAt==old)
assert(c.sections.vault.data.tracks.world[1].threshold==2)
local seq=c.sequence;O.db.settings.events=false;O.Event('death',{});assert(c.sequence==seq)
O.db.settings.events=true;O.Event('quest_completed',{questID=123,name='Fixture quest'})
O.db.settings.enabled=false;O.Scan('paused');assert(c.lastSeen==NOW)
O.db.settings.enabled=true
local scanned={};local original=O.Scan;O.Scan=function(_,keys) scanned=keys or {full=true} end
FRAME.event(FRAME,'PLAYER_MONEY');FRAME.event(FRAME,'CURRENCY_DISPLAY_UPDATE',3310)
assert(#timers==1);timers[1]();assert(scanned.profile and scanned.currencies and not scanned.quests)
O.Scan=original
-- Reproduce real client teardown: every handler would now erase its section.
assert(c.sections.equipment.detail==nil)
local previous=c.sections.profile.data;local at=c.sections.profile.observedAt
O.Schedule('profile');O.Profile=function() return {ilvl=0,money=0} end
FRAME.event(FRAME,'PLAYER_LOGOUT');timers[#timers]()
assert(c.sections.profile.data==previous and c.sections.profile.observedAt==at)
assert(c.events[#c.events].kind=='session_end' and c.events[#c.events].data.cached==true)
assert(c.events[#c.events].data.profileObservedAt==at)
''')

def plain(v):
    if hasattr(v,'items'):return {k:plain(x) for k,x in v.items()}
    return v
data={'DuckMooOmniCaptureDB':plain(lua.globals().DuckMooOmniCaptureDB)}
rows=list(omni_rows(data))
assert any(r[1]=='omni_event' and r[5]['kind']=='quest_completed' for r in rows)
assert any(r[2]=='inventory' and r[5]['data']['scope']=='carried_bags' for r in rows)
assert any(r[2]=='reputations' and r[5]['data'][100]['accountWide'] for r in rows)
assert any(r[2]=='currencies' and r[5]['data'][3310]['name']=='Named currency fixture' for r in rows)
# A malformed schema is rejected without interpreting it as empty coverage.
try:list(omni_rows({'DuckMooOmniCaptureDB':{'schema':999}}))
except ValueError:pass
else:raise AssertionError('Unknown schema accepted')
legacy={'schema':1,'version':'0.1.1','characters':{'Player-104-ABC':{'guid':'Player-104-ABC','name':'Fixture','realm':'Fixture','sections':{'profile':{'status':'captured','observedAt':200,'data':{'ilvl':0,'money':0}},'quests':{'status':'captured','observedAt':200,'data':{}}},'events':[{'id':1,'kind':'session_start','at':100,'data':{'ilvl':123,'money':500}},{'id':2,'kind':'session_end','at':200,'data':{'ilvl':0,'money':0}}]}}}
recovered=list(omni_rows({'DuckMooOmniCaptureDB':legacy}))
profile=next(r for r in recovered if r[2]=='profile')
assert profile[3]==100 and profile[5]['data']['ilvl']==123 and profile[5]['recoveredFromEvent']==1
assert legacy['characters']['Player-104-ABC']['sections']['profile']['data']['ilvl']==0
assert next(r for r in recovered if r[2]=='quests')[5]['data'] is None
print('Lua51 capture and import contract passed, including empty/unavailable bag reads, bank exclusion and labeled renown/warband reputation.')

if '--fixture' in sys.argv:
    import json
    target=WORKSPACE/'Nexus/omni-verification-fixture.json'
    target.write_text(json.dumps(data),encoding='utf-8')
    print('Synthetic adapter fixture:',target)

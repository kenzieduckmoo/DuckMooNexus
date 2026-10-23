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
''')
for name in ('Model.lua','Capture.lua','Core.lua'):
    lua.execute('assert(loadstring(...))("DuckMooOmniCapture",O)',(ROOT/name).read_text(encoding='utf-8'))
lua.execute('''
O.Init();O.Scan('test')
local c=O.Character()
assert(c.sections.currencies.data[3310].name=='Named currency fixture')
assert(c.sections.currencies.data[3310].description==nil)
assert(c.sections.vault.data.tracks.world[1].progress==4)
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
''')

def plain(v):
    if hasattr(v,'items'):return {k:plain(x) for k,x in v.items()}
    return v
data={'DuckMooOmniCaptureDB':plain(lua.globals().DuckMooOmniCaptureDB)}
rows=list(omni_rows(data))
assert any(r[1]=='omni_event' and r[5]['kind']=='quest_completed' for r in rows)
assert any(r[2]=='currencies' and r[5]['data'][3310]['name']=='Named currency fixture' for r in rows)
# A malformed schema is rejected without interpreting it as empty coverage.
try:list(omni_rows({'DuckMooOmniCaptureDB':{'schema':999}}))
except ValueError:pass
else:raise AssertionError('Unknown schema accepted')
print('Lua51 capture and import contract passed: named currencies, vault, retained last-known data, settings and coalesced section refresh.')

if '--fixture' in sys.argv:
    import json
    target=WORKSPACE/'Nexus/omni-verification-fixture.json'
    target.write_text(json.dumps(data),encoding='utf-8')
    print('Synthetic adapter fixture:',target)

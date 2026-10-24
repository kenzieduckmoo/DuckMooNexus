"""Focused mixed-profession UI context regression; mocked Lua 5.1, not a client."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parent.parent
sys.path.insert(0,str(WORKSPACE/'Nexus/test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
F={};P={db=true};C={professions={}};CURRENT_PARENT=171
ALCHEMY={professionID=2906,parentProfessionID=171,parentProfessionName='Alchemy',professionName='Midnight Alchemy',expansionName='Midnight',skillLevel=75,maxSkillLevel=100}
TAILORING={professionID=2918,parentProfessionID=197,parentProfessionName='Tailoring',professionName='Midnight Tailoring',expansionName='Midnight',skillLevel=80,maxSkillLevel=100}
CHILD=ALCHEMY
function S(fn,...) if fn then return fn(...) end end
safe=S
function F.Current() return C end
function F.Now() return 1000 end
function F.DrawIfShown() end
function F.RecordProfessionCatalog(parent,info) assert(parent==info.parentProfessionID) end
function F.ProfessionKnowledge() return {} end
function P.Character() return C end
function P.Snapshot() end
function P.RefreshCurrent() end
C_TradeSkillUI={GetBaseProfessionInfo=function() return {professionID=CURRENT_PARENT,professionName='Alchemy'} end,GetChildProfessionInfo=function() return CHILD end,GetChildProfessionInfos=function() return {ALCHEMY,TAILORING} end,GetConcentrationCurrencyID=function(id) return id end}
C_CurrencyInfo={GetCurrencyInfo=function() return {maxQuantity=1000} end}
''')
source=(ROOT/'Core.lua').read_text(encoding='utf-8')
lua.execute(source[source.index('function F.DiscoverProfession()'):source.index('function F.ReadTraitSelections(')])
source=(ROOT.parent/'DuckMooPlanner/Core.lua').read_text(encoding='utf-8')
lua.execute(source[source.index('function P.Discover()'):source.index('function P.RefreshCurrent()')])
lua.execute('''
F.DiscoverProfession()
assert(C.professions[171].expansions[2906].rank==75)
assert(C.professions[171].expansions[2918]==nil)
CHILD=TAILORING;F.DiscoverProfession()
assert(C.professions[171].expansions[2918]==nil)
P.Discover()
assert(C.professions[2906].name=='Alchemy')
assert(C.professions[2918].name=='Tailoring')
''')
print('Mixed child lists and stale current-profession transitions preserve Folio ownership and Planner names.')

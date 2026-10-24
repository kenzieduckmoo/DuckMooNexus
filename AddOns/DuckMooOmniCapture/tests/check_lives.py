"""Focused life journal checks in Lua 5.1; no claim of live game behavior."""
from pathlib import Path
import runpy
state=runpy.run_path(str(Path(__file__).with_name('check_capture.py')))
lua=state['lua']
lua.execute('''
O.shuttingDown=false;O.loading=false;O.db.settings.enabled=true;O.db.settings.events=true
function UnitGUID() return 'Player-104-AAAA1111' end
function UnitLevel() return 40 end
function UnitIsDeadOrGhost() return false end
local c=O.Character();local life=O.Life()
assert(life.startMeaning=='first_observed' and life.startLevel==40 and life.mode=='standard')
O.Store('profile',{zone='Observed zone',level=40},'captured')
local originalTime=c.sections.profile.observedAt
NOW=NOW+30;O.Level(41);assert(life.highestLevel==41)
assert(c.events[#c.events].context.profileObservedAt==originalTime)
O.Death();O.Death();assert(life.deaths==1 and not life.endedAt)
FRAME.event(nil,'PLAYER_ALIVE');O.LifeMode(true);O.Death()
assert(life.deaths==2 and life.endedAt==NOW and life.endReason=='observed_death')
local ended=life.endedAt;O.LifeMode(false);assert(life.endedAt==ended)
local identity=life.id;O.PrepareJournal(c.guid,c);assert(c.life.id==identity)
function GetBuildInfo() return '1.60.1','70532','',16001 end
function UnitGUID() return 'Player-104-BBBB2222' end
local other=O.Life();assert(other.client=='forever' and other.mode=='unconfirmed' and other.id~=identity)
O.Death();assert(other.deaths==1 and not other.endedAt)
''')
print('Life journal passed: first-observed bounds, context timestamps, mode changes, duplicate deaths, standard/Hardcore distinction and client separation.')

lua.execute('''
C_MountJournal={GetMountIDs=function() return {1,2} end,GetMountInfoByID=function(id) return 'Mount '..id,100+id,42,false,true,1,false,false,nil,false,id==1 end}
C_PetJournal={GetOwnedPetIDs=function() return {'Pet-1'} end,GetPetInfoTableByPetID=function() return {speciesID=12,level=25} end}
C_ToyBox={GetNumFilteredToys=function() return 1 end,GetToyFromIndex=function() return 50 end}
function PlayerHasToy() return true end
C_Item={GetItemNameByID=function() return 'Observed toy' end}
local collections,status=O.Collections();assert(status=='partial' and collections.mounts.rows[1].collected and not collections.mounts.rows[2].collected)
assert(collections.pets.rows['Pet-1'].speciesID==12 and collections.toys.rows[50].name=='Observed toy')
C_QuestLog={GetNumQuestLogEntries=function() return 1 end,GetInfo=function() return {questID=123,title='Active quest'} end,GetQuestObjectives=function() return {{text='Do the thing',numFulfilled=1,numRequired=3}} end}
local activities=O.Activities();assert(activities.quests[123].objectives[1].numFulfilled==1)
O.bankOpen=true;Enum.BagIndex={CharacterBankTab_1=100,AccountBankTab_1=200};Enum.BankType={Character=0,Account=2};C_Bank={CanViewBank=function() return true end}
C_Container={GetContainerNumSlots=function() return 2 end,GetContainerNumFreeSlots=function() return 1 end,GetContainerItemInfo=function(_,s) if s==1 then return {itemID=99,stackCount=2} end end}
local storage=O.Storage();assert(storage.characterBank.bags[100].items[1].quantity==2);assert(storage.accountBank.bags[200].items[1].itemID==99)
O.Store('storage',storage,'partial');local sample=storage.characterBank.bags[100].observedAt
C_Container.GetContainerNumFreeSlots=function() return nil end;assert(O.Storage()==nil)
O.bankOpen=false;O.mailOpen=true
function GetInboxNumItems() return 1,2 end
function GetInboxHeaderInfo() return nil,nil,'Sender','Subject',10,0,12,true end
function GetInboxItem(_,slot) if slot==1 then return 'Mail item',77,0,3,1 end end
local mail=O.Storage();assert(mail.mail.loaded==1 and mail.mail.reportedTotal==2 and mail.mail.messages[1].attachments[1].quantity==3)
assert(mail.characterBank.bags[100].observedAt==sample)
O.mailOpen=false;assert(O.Storage()==nil)
''')
print('Extended capture passed: 11th mount result, owned pets/filtered toys, quest objectives, bank separation, unavailable reads, mail attachments and independent sample times.')

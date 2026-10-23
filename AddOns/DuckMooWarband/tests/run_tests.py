"""Lua 5.1 model and UI interaction checks; requires lupa==2.8."""
from pathlib import Path
import os
import time
os.environ['TZ']='America/Chicago'
if hasattr(time,'tzset'):
    time.tzset()
else:
    import ctypes
    crt=ctypes.CDLL('ucrtbase');crt._putenv(b'TZ=CST6CDT');crt._tzset()
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
W={};date=os.date;time=os.time;SlashCmdList={};UISpecialFrames={}
NOW=time({year=2026,month=10,day=8,hour=12,min=0,sec=0})
function GetServerTime()return NOW end
function UnitGUID()return 'priest1' end
function UnitName()return 'Ember' end
function UnitClass()return 'Priest','PRIEST' end
function GetRealmName()return 'Garona' end
local nextDaily=NOW+3600;local nextWeekly=NOW+4*86400
C_DateAndTime={GetSecondsUntilDailyReset=function()return nextDaily-NOW end,GetSecondsUntilWeeklyReset=function()return nextWeekly-NOW end}
frames={};local methods={}
MOCK_METHODS=methods
function methods:SetPoint(...)self.point={...}end
function methods:GetPoint()return 'CENTER',UIParent,'CENTER',0,0 end
function methods:ClearAllPoints()self.point=nil end
function methods:SetSize(w,h)self.w=w;self.h=h end
function methods:SetWidth(w)self.w=w end
function methods:SetHeight(h)self.h=h end
function methods:GetWidth()return self.w end
function methods:GetHeight()return self.h end
function methods:SetText(s,...)assert(select('#',...)==0,'Unexpected native text argument');self.text=s;if self.scripts.OnTextChanged then self.scripts.OnTextChanged(self,false)end end
function methods:GetText()return self.text or '' end
function methods:SetScript(event,fn)self.scripts[event]=fn end
function methods:GetScript(event)return self.scripts[event]end
function methods:SetShown(v)self.shown=not not v end
function methods:Show()self.shown=true end
function methods:Hide()self.shown=false end
function methods:IsShown()return self.shown end
function methods:SetEnabled(v)self.enabled=not not v end
function methods:SetFocus()self.focus=true end
function methods:ClearFocus()self.focus=false end
setmetatable(methods,{__index=function(_,key)if key:match('^[A-Z]')then return function()end end end})
function methods:SetToplevel(value)self.topLevel=value end
function methods:SetFlattensRenderLayers(value)self.flattenLayers=value end
function CreateFrame(kind,name,parent,template)
 local f=setmetatable({uid=#frames+1,kind=kind,name=name,template=template,parent=parent,scripts={},shown=true},{__index=function(self,key)
  -- Retail only supplies backdrop methods through BackdropTemplate.
  -- A catch-all no-op previously concealed the plain EditBox startup error.
  if key=='SetBackdrop' or key=='GetBackdrop' then
   if not self.template or not self.template:find('BackdropTemplate',1,true) then return nil end
  end
  return methods[key]
 end});frames[#frames+1]=f;return f
end
function methods:CreateFontString(_,_,template)return CreateFrame('FontString',nil,self,template)end
function methods:CreateTexture()return CreateFrame('Texture',nil,self)end
UIParent=CreateFrame('Frame');GameTooltip=CreateFrame('Frame')
UIParent:SetSize(1920,1080)
function GameTooltip:SetText(text,...)
 assert(type(text)=='string' and select('#',...)==0,'Tooltip SetText received an unexpected extra argument')
 self.text=text
end
''')
for filename in ['Model.lua','Core.lua','Activity.lua','UI.lua']:
    lua.execute("assert(loadfile(...))('DuckMooWarband',W)",str(ROOT/filename))
lua.execute(r'''
local M=W.Model
W.Init();W.CaptureCharacter();local db=W.db
db.characters.priest2={name='Willow',realm='Garona',class='PRIEST',groups={weekend=true},lastSeen=NOW-86400}
db.characters.hunter={name='Mara',realm='Garona',class='HUNTER',groups={}}
local quick=W.Quick('  Continue my quest  ')
assert(quick.text=='Continue my quest' and quick.characters.priest1 and not quick.characters.priest2 and quick.progress=='character')
local draft={text='Priest project',category='Projects',scope='class',rule='PRIEST',progress='character',repeatMode='once'}
local task=W.SaveTask(draft);assert(#M.Targets(task,db)==2)
local function rowsFor(id,resets)
 local out={};for _,r in ipairs(M.Rows(db,NOW,resets or W.Resets()))do if r.task.id==id then out[#out+1]=r end end;return out
end
assert(#rowsFor(task.id)==2)
assert(M.Action(db,task,'priest1','worked',NOW,W.Resets()))
assert(#rowsFor(task.id)==2 and task.states.priest1.lastWorked==NOW)
assert(M.Action(db,task,'priest1','done',NOW,W.Resets()))
local rows=rowsFor(task.id);assert(#rows==1 and rows[1].key=='priest2','One priest completed another priest task')
assert(not M.Action(db,task,'hunter','done',NOW,W.Resets()))
assert(M.Undo(db) and #rowsFor(task.id)==2)
draft.progress='account';local shared=W.SaveTask(draft);assert(#rowsFor(shared.id)==1)
assert(M.Action(db,shared,'@account','done',NOW,W.Resets()) and #rowsFor(shared.id)==0)
assert(#rowsFor(task.id)==2,'Shared task completed a different task')
local unchanged=M.Copy(shared);unchanged.interval=4;unchanged.weekday=1;unchanged.text='A renamed shared task'
shared=W.SaveTask(unchanged,shared.id)
assert(#rowsFor(shared.id)==0 and shared.scheduleRevision==1,'Editing unrelated fields resurrected a completed task')
draft.scope='group';draft.rule='weekend';draft.progress='character';local group=W.SaveTask(draft)
assert(#rowsFor(group.id)==1 and rowsFor(group.id)[1].key=='priest2')
assert(M.Action(db,group,'priest2','done',NOW,W.Resets()))
db.characters.priest2.groups.weekend=nil;assert(#M.Targets(group,db)==0 and group.states.priest2.lastDone==NOW)
db.characters.priest2.groups.weekend=true;assert(#rowsFor(group.id)==0,'Membership change lost completion')
-- Daily/weekly reset occurrences use API epochs; unavailable API does not guess.
draft.scope='selected';draft.characters={priest1=true};draft.repeatMode='daily';local daily=W.SaveTask(draft)
local dailyAnchor=NOW+3600;local weeklyAnchor=NOW+86400
assert(M.Action(db,daily,'priest1','done',NOW,{daily=dailyAnchor}))
assert(#rowsFor(daily.id,{daily=dailyAnchor})==0)
NOW=NOW+10;assert(#rowsFor(daily.id,{daily=dailyAnchor})==0)
NOW=dailyAnchor;assert(#rowsFor(daily.id,{daily=dailyAnchor+86400})==1)
local waiting=rowsFor(daily.id,{});assert(#waiting==1 and waiting[1].occurrence.waiting)
assert(not M.Action(db,daily,'priest1','done',NOW,{}))
draft.repeatMode='weekly';local weekly=W.SaveTask(draft)
assert(M.Action(db,weekly,'priest1','skip',NOW,{weekly=weeklyAnchor}))
assert(#rowsFor(weekly.id,{weekly=weeklyAnchor})==0)
NOW=weeklyAnchor;assert(#rowsFor(weekly.id,{weekly=weeklyAnchor+7*86400})==1)
-- Fixed weekday visibility and interval-after-completion are distinct.
draft.repeatMode='weekday';draft.weekday=date('*t',NOW).wday;local weekday=W.SaveTask(draft)
assert(#rowsFor(weekday.id)==1);assert(M.Action(db,weekday,'priest1','done',NOW,{}));assert(#rowsFor(weekday.id)==0)
NOW=M.AddDays(NOW,1);assert(#rowsFor(weekday.id)==0)
NOW=M.AddDays(NOW,6);assert(#rowsFor(weekday.id)==1)
draft.repeatMode='interval';draft.interval=4;local interval=W.SaveTask(draft)
assert(M.Action(db,interval,'priest1','done',NOW,{}));local nextAt=interval.states.priest1.nextAt
assert(nextAt==M.AddDays(NOW,4) and #rowsFor(interval.id)==0)
NOW=nextAt;assert(#rowsFor(interval.id)==1)
assert(M.Action(db,interval,'priest1','postpone',NOW,{}));assert(#rowsFor(interval.id)==0)
assert(M.Undo(db) and #rowsFor(interval.id)==1)
local oldNow=NOW
local nov=time({year=2026,month=11,day=1,hour=0,min=0,sec=0})
assert(M.AddDays(nov,1)-nov==90000,'Civil postponement failed DST')
-- Save/reload preserves identity, groups, all progress and history.
local stored=M.Copy(db);DuckMooWarbandDB=stored;W.Init();W.CaptureCharacter();db=W.db
assert(db.characters.priest2.groups.weekend and db.tasks[shared.id].states['@account'].lastDone and #db.history>0)
assert(not db.undo)
draft.interval=0;assert(not W.SaveTask(draft));draft.interval=4
assert(not W.Quick('   '))
local api=C_DateAndTime;C_DateAndTime=nil;assert(not next(W.Resets()));C_DateAndTime={GetSecondsUntilDailyReset=function()error('API unavailable')end};assert(not next(W.Resets()));C_DateAndTime=api
-- Actual keyboard capture, editing scope, chooser actions, compact mode, archive.
W.CreateUI();W.frame:Show();W.Render()
W.frame.capture:SetText('Captured with Enter');W.frame.capture:GetScript('OnEnterPressed')()
assert(db.tasks[db.nextID-1].text=='Captured with Enter' and W.frame.capture:GetText()=='')
W.EditTask(db.tasks[db.nextID-1]);W.editor.draft.scope='all';W.editor.draft.progress='account';W.editor.refresh()
assert(W.editor.progress.caption:GetText():find('shared completion'))
for _,f in ipairs(frames)do if f.parent==W.editor and f.caption and f.caption:GetText()=='Save' then f:GetScript('OnClick')();break end end
assert(db.tasks[db.nextID-1].scope=='all' and db.tasks[db.nextID-1].progress=='account')
W.ManageCharacter('priest2');W.characterEditor.edit:SetText('Weekend, Crafters')
for _,f in ipairs(frames)do if f.parent==W.characterEditor and f.caption and f.caption:GetText()=='Save groups' then f:GetScript('OnClick')();break end end
assert(db.characters.priest2.groups.weekend and db.characters.priest2.groups.crafters)
W.db.settings.compact=true;W.Render();assert(W.frame:GetWidth()==450)
local height=W.frame:GetHeight();local count=#frames;for i=1,30 do W.Render()end;assert(#frames==count,'Rows leaked frames')
-- Dense roster: paged views keep all offline character assignments visible.
for i=1,400 do db.characters['alt'..i]={name=string.format('Alt %03d',i),realm='Garona',class='PRIEST',groups={}}end
draft.scope='all';draft.repeatMode='once';draft.progress='character';draft.text='All roster project';local bulk=W.SaveTask(draft)
assert(#rowsFor(bulk.id)==403)
W.Render();W.page=2;W.Render();assert(W.page==2 and W.frame.rows[1]:IsShown())
W.frame.rows[1].more:GetScript('OnClick')();W.choice.rows[1]:GetScript('OnClick')()
assert(db.history[#db.history].action=='worked')
-- Exercise the real hover callback with an API mock that rejects stray arguments.
W.frame.rows[1]:GetScript('OnEnter')(W.frame.rows[1])
assert(GameTooltip.text:find('All roster project',1,true))
local hoveredTask=W.visibleRows[(W.page-1)*12+1].task;local savedText=hoveredTask.text
hoveredTask.text='A | B';W.frame.rows[1]:GetScript('OnEnter')(W.frame.rows[1]);assert(GameTooltip.text=='A || B');hoveredTask.text=savedText
local savedHistory=M.Copy(db.history)
local first=W.visibleRows[1]
for i=1,510 do assert(M.Action(db,first.task,first.key,'worked',NOW,W.Resets()))end
assert(#db.history==500);local oldest=db.undo.dropped
assert(M.Undo(db) and #db.history==500 and db.history[1].at==oldest.at,'Undo lost history at its storage limit')
W.manage=true;W.Render();W.frame.rows[1].more:GetScript('OnClick')();W.choice.rows[2]:GetScript('OnClick')()
assert(W.visibleRows[1].task.archived);W.frame.rows[1].done:GetScript('OnClick')();assert(not W.visibleRows[1].task.archived)
-- Optional providers export copies. Import is additive and preserves own groups.
local exported={offline={name='Imported',realm='Garona',class='EVOKER',lastSeen=NOW-1000}}
DuckMooFolio={ExportRoster=function()return exported end}
W.ImportRoster();assert(db.characters.offline.class=='EVOKER' and not next(db.characters.offline.groups))
db.characters.offline.groups.mine=true;db.characters.offline.name='Edited locally'
assert(exported.offline.name=='Imported','Import retained a source table reference')
W.ImportRoster();assert(db.characters.offline.groups.mine)
C_Covenants={GetActiveCovenantID=function()return 1 end,GetCovenantData=function()return {name='Kyrian'}end}
W.CaptureCharacter();assert(db.characters.priest1.covenantID==1 and db.characters.priest1.covenantName=='Kyrian')
C_Covenants={GetActiveCovenantID=function()return nil end};W.CaptureCharacter();assert(db.characters.priest1.covenantID==1)
local armor=assert(W.SaveTask({text='Mail task',category='Collection',scope='armor',rule='Mail',progress='character',repeatMode='once'}))
assert(M.Eligible(armor,'hunter',db.characters.hunter) and M.Eligible(armor,'offline',db.characters.offline) and not M.Eligible(armor,'priest1',db.characters.priest1))
assert(not M.Eligible(armor,'missing',{groups={}}))
local covenant=assert(W.SaveTask({text='Kyrian task',category='Collection',scope='covenant',rule=1,progress='character',repeatMode='once'}))
assert(#M.Targets(covenant,db)==1 and M.Targets(covenant,db)[1]=='priest1')
db.categoryRules.Collection={days={[date('*t',NOW).wday]=true}};assert(#rowsFor(covenant.id)==1)
db.categoryRules.Collection={days={}};assert(#rowsFor(covenant.id)==0 and #M.Targets(covenant,db)==1)
assert(#M.Rows(db,NOW,W.Resets(),true)>0,'Category hiding lost task definitions')
W.CategoryEditor('Collection');W.categoryEditor.days[date('*t',NOW).wday]:GetScript('OnClick')()
for _,f in ipairs(frames)do if f.parent==W.categoryEditor and f.caption and f.caption:GetText()=='Save days' then f:GetScript('OnClick')();break end end
assert(#rowsFor(covenant.id)==1)
assert(W.AddStarterPack('weekly')==3 and W.AddStarterPack('weekly')==0)
local before=db.nextID;UnitGUID=function()return 'priest2'end;UnitName=function()return 'Willow'end;W.CaptureCharacter()
assert(W.AddStarterPack('weekly')==3 and db.nextID==before+3)
print('PASS: detached optional roster imports, retained groups, armor/covenant rules, unknown snapshot preservation, category visibility without completion, actual category callbacks and per-character starter-pack deduplication')
print('PASS: quick capture, per-priest/shared progress, group membership, unavailable resets, reset boundaries, weekdays, intervals, postpone/skip/undo, DST, reload, actual UI callbacks, 403-character paging and stable frame count')
''')
lua.execute(r'''
local M=W.Model;W.db.tasks={};W.db.nextID=1;W.db.categoryRules={};W.db.history={};W.db.undo=nil
W.current='priest1';W.db.characters.priest1.name='Ember';W.db.settings.compact=false;W.view='today';W.manage=false;W.ApplyGeometry()
for i=1,31 do assert(W.SaveTask({text='Prepare supplies '..i,category=i%2==0 and'Weekends'or'Projects',scope='selected',characters={priest1=true},progress='character',repeatMode='once'}))end
for _,size in ipairs({{940,560},{1040,740},{1320,900}})do
 W.frame:SetSize(size[1],size[2]);W.Render()
 for _,page in ipairs({'today','all','characters','categories','preferences'})do
  W.SelectPage(page);assert(W.Page()==page and W.nav[page]._active and W.sidebar:IsShown())
  assert(W.frame.topLevel and W.frame.flattenLayers,'Warband main window interleaves with other windows')
  if page~='preferences'then
   local shown=0
   for _,row in ipairs(W.frame.rows)do
    if row:IsShown()then
     shown=shown+1;assert(-row.point[3]+row:GetHeight()<W.frame:GetHeight()-30,'Row overlaps the page footer')
    end
   end
   assert(shown<=W.pageSize and W.pageSize<=12)
  end
 end
end
W.SelectPage('today');W.frame.search:SetText('Prepare supplies 17');assert(#W.visibleRows==1 and W.visibleRows[1].task.text=='Prepare supplies 17')
W.frame.rows[1].more:GetScript('OnClick')();W.choice.rows[1]:GetScript('OnClick')()
assert(#W.visibleRows==1 and W.visibleRows[1].state.lastWorked==NOW,'Worked on it completed a task')
W.frame.rows[1].done:GetScript('OnClick')();assert(#W.visibleRows==0)
W.frame.undo:GetScript('OnClick')();assert(#W.visibleRows==1)
W.SelectPage('characters');W.frame.search:SetText('Ember');assert(#W.visibleRows==1)
W.frame.rows[1].done:GetScript('OnClick')();assert(W.characterEditor.guid=='priest1')
W.SelectPage('categories');W.frame.search:SetText('Weekends');assert(#W.visibleRows==1)
W.frame.rows[1].done:GetScript('OnClick')();assert(W.categoryEditor.category=='Weekends')
W.SelectPage('preferences');W.frame.palette:GetScript('OnClick')();W.choice.callback('translight')
assert(W.db.settings.theme=='translight' and W.Themes.translight.name=='Trans pride - dusk')
W.frame.capture:SetText('Capture before organizing');W.frame.capture:GetScript('OnEnterPressed')()
local new=W.db.tasks[W.db.nextID-1]
assert(new.characters.priest1 and new.progress=='character' and new.repeatMode=='once' and W.Page()=='today' and W.filter=='')
W.frame:SetSize(1040,740);W.SaveGeometry();W.frame.search:SetText('No matches');W.SetCompact(true)
assert(#W.visibleRows>0 and not W.sidebar:IsShown(),'Full-view search hid compact tasks')
W.frame:SetSize(390,260);W.SaveGeometry();W.Render();assert(W.pageSize==2)
W.SetCompact(false);assert(W.frame:GetWidth()==1040 and W.frame:GetHeight()==740)
W.SetCompact(true);assert(W.frame:GetWidth()==390 and W.frame:GetHeight()==260)
W.SetCompact(false);W.frame.search:SetText('')
for _,page in ipairs({'today','all','characters','categories','preferences'})do W.SelectPage(page)end
local count=#frames;for i=1,10 do for _,page in ipairs({'today','all','characters','categories','preferences'})do W.SelectPage(page)end end
assert(#frames==count,'New pages allocate frames on every render')
for _,f in ipairs(frames)do if f.parent==UIParent and f._round then assert(f.topLevel and f.flattenLayers)end end
assert(#W.inputs>0)
for _,f in ipairs(W.inputs)do
 assert(f.SetBackdrop==nil,'Plain EditBox unexpectedly exposes backdrop methods')
 assert(f._round and #f._round==9 and type(f.SetBackdropColor)=='function','Input styling did not initialize')
end
W.ApplyTheme()
for _,f in ipairs(W.inputs)do assert(f._surfaceColor and f._surfaceColor[4]==1)end
print('PASS: plain EditBoxes initialize and theme without BackdropTemplate methods')
print('PASS: full-window pages/sizing, search, worked/done/undo actions, character groups/category dialogs, palette selection, frictionless capture, separate compact geometry and bounded frame reuse')
''')
print('All Warband Planner checks passed. In-game checks remain required.')

#!/usr/bin/env python3
"""Run with Python 3 and lupa (pip install lupa). No WoW client required."""
import os
import time
from pathlib import Path
from lupa.lua51 import LuaRuntime
os.environ['TZ'] = 'America/Chicago'
if hasattr(time, 'tzset'):
    time.tzset()
else:
    # Lua and Python use the Windows C runtime's US daylight-saving rules.
    import ctypes
    crt = ctypes.CDLL('ucrtbase')
    crt._putenv(b'TZ=CST6CDT')
    crt._tzset()
ROOT = Path(__file__).resolve().parents[1]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("date=os.date;time=os.time;P={};assert(loadfile(...))('DuckMooPlanner',P)",str(ROOT/'Model.lua'))
lua.execute(r'''
local M=P.Model
local function day(s) return assert(M.ParseDay(s)) end
local now=day('2026-10-01')+7*3600
local r={name='Alchemy',skillLineID=2906,amount=431,max=1000,secondsPerPoint=240,observedAt=now}
assert(M.FullAt(r)==now+569*240)
assert(M.Current(r,now+240)==432)
assert(M.Current(r,now+999999)==1000)
assert(M.Current(r,now-100)==431)
assert(M.Clock(day('2026-10-01'))=='12:00 AM')
assert(M.Clock(day('2026-10-01')+13*3600+50*60)=='1:50 PM')
assert(M.ParseDay('2026-02-30')==nil)
assert(M.ParseDay('2026-13-01')==nil)
assert(M.Key(M.AddDays(day('2026-10-31'),1))=='2026-11-01')
assert(M.Key(M.AddDays(day('2026-03-07'),4))=='2026-03-11')
assert(M.Key(M.AddDays(day('2026-10-30'),4))=='2026-11-03')
assert(M.AddDays(day('2026-11-01'),1)-day('2026-11-01')==90000)
M.SetSchedule(r,'four',day('2026-10-01'))
M.Complete(r,day('2026-10-02')+14*3600)
assert(M.Key(r.patron.due)=='2026-10-06')
M.SetSchedule(r,'weekly',day('2026-10-04'),1)
M.Complete(r,day('2026-10-04')+3600)
assert(M.Key(r.patron.due)=='2026-10-11')
M.Complete(r,day('2026-10-05')+3600)
assert(M.Key(r.patron.due)=='2026-10-11')
M.SetSchedule(r,'four',day('2026-09-20'))
local dates=M.PatronDates(r.patron,day('2026-10-01'),day('2026-10-10'),now)
assert(#dates==3 and dates[1].overdue and M.Key(dates[1].at)=='2026-10-01')
assert(dates[2].projected and M.Key(dates[2].at)=='2026-10-05')
local db={characters={a={name='Voidchicken',realm='Garona',professions={[1]=r}}}}
r.amount=1000
assert(#M.Events(db,day('2026-10-01'),day('2026-11-01'),now,false,false)==0)
assert(M.Events(db,day('2026-10-01'),day('2026-10-02'),now,true,false)[1].ready)
r.amount=431
local cap=M.FullAt(r)
assert(#M.Events(db,cap,cap+1,now,false,false)==1)
assert(#M.Events(db,cap-1,cap,now,false,false)==0)
assert(#M.Events(db,cap,cap+1,now,false,false,'void')==1)
assert(#M.Events(db,cap,cap+1,now,false,false,'malygos')==0)
r.hidden=true
assert(#M.Events(db,cap,cap+1,now,false,false)==0)
r.hidden=nil
local start,finish=M.Week(now,5*86400,0)
assert(start==now-2*86400 and finish==now+5*86400)
print('PASS: Concentration, date boundaries, DST, clock, schedules, backlog, filters and reset interval')
''')
lua.execute(r'''
NOW=time({year=2026,month=10,day=1,hour=7,min=0,sec=0})
function GetServerTime() return NOW end
function UnitGUID() return 'Player-1' end
function UnitName() return 'Voidchicken' end
function GetNormalizedRealmName() return 'Garona' end
function GetRealmName() return 'Garona' end
function UnitClass() return 'Mage','MAGE' end
SlashCmdList={};UISpecialFrames={};StaticPopupDialogs={}
RAID_CLASS_COLORS={MAGE={r=.4,g=.8,b=1}}
C_DateAndTime={GetSecondsUntilWeeklyReset=function() return 5*86400+3*3600 end,GetSecondsUntilDailyReset=function() return 3*3600 end}
C_Timer={After=function(_,fn) fn() end,NewTicker=function(_,fn) return {Cancel=function() end} end}
CURRENCY={quantity=431,maxQuantity=1000,rechargingCycleDurationMS=240000}
C_CurrencyInfo={GetCurrencyInfo=function() return CURRENCY end}
C_TradeSkillUI={
 IsTradeSkillLinked=function() return false end,IsTradeSkillGuild=function() return false end,
 GetBaseProfessionInfo=function() return {professionName='Alchemy'} end,
 GetChildProfessionInfos=function() return {{professionID=2906,professionName='Midnight Alchemy',skillLevel=100}} end,
 GetChildProfessionInfo=function() return {professionID=2906,professionName='Midnight Alchemy',skillLevel=100} end,
 GetConcentrationCurrencyID=function() return 1234 end,
}
frameCount=0;frames={}
local methods={}
function methods:SetPoint(...) self.points=self.points or {};self.points[#self.points+1]={...} end
function methods:ClearAllPoints() self.points={} end
function methods:SetScript(event,fn) self.scripts[event]=fn end
function methods:GetScript(event) return self.scripts[event] end
function methods:SetSize(w,h) self.w=w;self.h=h end
function methods:SetWidth(w) self.w=w end
function methods:SetHeight(h) self.h=h end
function methods:GetWidth() return self.w or 990 end
function methods:GetHeight() return self.h or 500 end
function methods:SetAlpha(v) self.alpha=v end
function methods:GetAlpha() return self.alpha or 1 end
function methods:SetValue(v) self.value=v;if self.scripts.OnValueChanged then self.scripts.OnValueChanged(self,v) end end
function methods:GetValue() return self.value end
function methods:SetText(t,...) assert(select('#',...)==0,'SetText received an unintended extra argument');self.text=t end
function methods:GetText() return self.text or '' end
function methods:Show() local was=self.shown;self.shown=true;if not was and self.scripts.OnShow then self.scripts.OnShow(self) end end
function methods:Hide() self.shown=false end
function methods:IsShown() return self.shown end
function methods:SetShown(v) if v then self:Show() else self:Hide() end end
function methods:SetVerticalScroll(v) self.scroll=v end
function methods:GetVerticalScroll() return self.scroll or 0 end
function methods:SetChecked(v) self.checked=v end
function methods:GetChecked() return self.checked end
function methods:GetPoint() return 'CENTER',UIParent,'CENTER',0,0 end
function methods:SetToplevel(v)assert(type(v)=='boolean');self.topLevel=v end
function methods:SetFlattensRenderLayers(v)assert(type(v)=='boolean');self.flattenLayers=v end
setmetatable(methods,{__index=function(_,key) if key:match('^[A-Z]') then return function() end end end})
function CreateFrame(kind,name,parent,template)
 frameCount=frameCount+1
 local f=setmetatable({uid=frameCount,kind=kind,name=name,parent=parent,template=template,scripts={},shown=true},{__index=methods})
 frames[#frames+1]=f
 if name then _G[name]=f end
 return f
end
function methods:CreateFontString(_,_,font) return CreateFrame('FontString',nil,self,font) end
function methods:CreateTexture() return CreateFrame('Texture',nil,self) end
function methods:GetFrameLevel() return 3 end
function methods:GetEffectiveScale() return 1 end
function methods:GetCenter() return 100,100 end
UIParent=CreateFrame('Frame');UIParent:SetSize(1920,1080)
GameTooltip=CreateFrame('Frame')
function StaticPopup_Show(name,text,_,data) lastPopup={name=name,text=text,data=data} end
''')
for filename in ['Core.lua','Minimap.lua','UI.lua']:
    lua.execute("assert(loadfile(...))('DuckMooPlanner',P)",str(ROOT/filename))
lua.execute(r'''
P.Init();P.Discover()
local c=P.db.characters['Player-1']
local r=c.professions[2906]
assert(r and r.currencyID==1234 and r.amount==431)
local original=P.Model.FullAt(r)
NOW=NOW+300;CURRENCY.quantity=432;P.RefreshCurrent()
assert(P.Model.FullAt(r)==original) -- no forecast drift on ordinary regen
CURRENCY.quantity=200;P.RefreshCurrent()
assert(r.amount==200 and P.Model.FullAt(r)>original)
P.Show('daily');P.Show('weekly');P.Show('monthly');P.Show('settings')
P.Model.SetSchedule(r,'four',P.Model.Day(NOW))
P.Show('daily');P.Show('weekly');P.Show('monthly');P.Show('settings')
local warmed=frameCount
for i=1,20 do P.Show('daily');P.Show('weekly');P.Show('monthly');P.Show('settings') end
assert(frameCount==warmed,'Render leaked frames: '..frameCount..' versus '..warmed)
P.Show('weekly');P.scroll:SetVerticalScroll(50);P.Render(true)
assert(P.scroll:GetVerticalScroll()==math.min(50,math.max(0,P.content:GetHeight()-P.scroll:GetHeight())))
P.ScheduleEditor(r,'Voidchicken-Garona');assert(P.editor:IsShown())
local editorCount=frameCount
for i=1,10 do P.ScheduleEditor(r,'Voidchicken-Garona') end
assert(frameCount==editorCount,'Schedule editor leaked frames')
P.editor.edit:SetText('2026-02-30');P.editor.save:GetScript('OnClick')()
assert(P.editor:IsShown() and P.editor.errorText:GetText()~='')
P.editor.mode='weekly';P.editor.weekday=1;P.editor.edit:SetText('2026-10-01')
P.editor.save:GetScript('OnClick')()
assert(P.Model.Key(r.patron.due)=='2026-10-04' and r.patron.mode=='weekly')
P.followToday=true;NOW=NOW+86400;P.Render(true)
assert(P.Model.Key(P.selectedDay)=='2026-10-02')
SlashCmdList.DUCKMOOPLANNER('today');assert(P.view=='daily')
P.month=P.Model.ParseDay('2026-12-01');P.view='monthly';P.Navigate(1)
assert(P.Model.Key(P.month)=='2027-01-01')
-- Linked professions must not enroll another player's data.
C_TradeSkillUI.IsTradeSkillLinked=function() return true end
C_TradeSkillUI.GetChildProfessionInfos=function() return {{professionID=9999,skillLevel=100}} end
P.Discover();assert(c.professions[9999]==nil)
print('PASS: Lua 5.1 loading, API discovery, spend updates, all UI views, stable frame pooling, scroll, editor, slash commands and linked-profession guard')
''')
lua.execute(r'''
local M=P.Model
local now=GetServerTime()
local today=M.Day(now)
local tomorrow=M.AddDays(today,1)
local c=P.db.characters['Player-1']
local r=c.professions[2906]
r.amount=1000;r.observedAt=now;r.patron=nil
local old={name='Alchemy',skillLineID=2871,expansion='The War Within Alchemy',amount=1000,max=1000,observedAt=now,secondsPerPoint=240}
c.professions[2871]=old
assert(M.IsMidnight(r,2906))
assert(M.IsMidnight({expansion='Alchimie'},2906)) -- IDs survive localized labels
assert(not M.IsMidnight(old,2871))
assert(not P.db.settings.includePrior and not P.db.settings.priorExpanded)
assert(not M.Visible(P.db,old,2871))
local _,before=M.TodayGroups(P.db,now,'')
P.db.settings.includePrior=true
assert(M.Visible(P.db,old,2871))
P.db.settings.includePrior=false
-- Custom reminder validation and occurrence boundaries.
local once=assert(P.SaveNote(nil,'Collect mailbox',M.Key(today),'once'))
assert(P.SaveNote(nil,'',M.Key(today),'once')==nil)
assert(P.SaveNote(nil,'Bad interval',M.Key(today),'days','0')==nil)
assert(P.SaveNote(nil,'Bad interval',M.Key(today),'days','1.5')==nil)
assert(P.SaveNote(nil,'Bad date','2026-02-30','once')==nil)
assert(#M.NoteDates(once,today,tomorrow,now)==1)
assert(#M.NoteDates(once,tomorrow,M.AddDays(today,2),now)==0)
assert(M.DismissNote(once,now,100,200))
assert(once.dismissedAt==now and #M.NoteDates(once,today,tomorrow,now)==0)
local edited=assert(P.SaveNote(once,'Collect mailbox and auctions',M.Key(today),'once'))
assert(edited==once and not once.dismissedAt)
local days=assert(P.SaveNote(nil,'Check auctions',M.Key(today),'days','4'))
assert(M.DismissNote(days,now,100,200))
assert(M.Key(days.due)==M.Key(M.AddDays(now,4)))
local daily=assert(P.SaveNote(nil,'Daily quest',M.Key(today),'dailyReset'))
assert(M.DismissNote(daily,now,3600,604800))
assert(daily.due==now+3600)
assert(not M.DismissNote(daily,now,nil,604800) and daily.due==now+3600)
local weekly=assert(P.SaveNote(nil,'Weekly dungeon',M.Key(today),'weeklyReset'))
assert(M.DismissNote(weekly,now,3600,123456))
assert(weekly.due==now+123456)
local missed={text='Missed',mode='once',due=M.AddDays(today,-3)}
local dates=M.NoteDates(missed,today,tomorrow,now)
assert(#dates==1 and dates[1].overdue and dates[1].at==today)
assert(M.Duration(90061)=='1d 01h 01m 01s')
assert(M.Duration(nil)=='unavailable')
-- Compact roster deduplicates characters across Concentration and patron tasks.
local second={name='Tailoring',skillLineID=2918,expansion='Midnight Tailoring',amount=1000,max=1000,observedAt=now,secondsPerPoint=240}
c.professions[2918]=second
M.SetSchedule(r,'four',today);M.SetSchedule(second,'four',today)
local groups,notes=M.TodayGroups(P.db,now,'')
assert(#groups==1 and #groups[1].events==4 and #notes>=1)
P.Show('daily');P.frame:SetSize(720,380);P.SaveGeometry()
P.SetCompact(true)
assert(P.db.settings.compact and P.frame:GetAlpha()==.65)
assert(P.frame:GetWidth()==340)
P.frame:SetSize(300,180);P.SaveGeometry()
P.SetCompact(false)
assert(P.frame:GetWidth()==940 and P.frame:GetHeight()==560 and P.frame:GetAlpha()==.85)
P.settingsTab='appearance';P.Show('settings')
P.opacitySlider:SetValue(80)
assert(P.db.settings.compactAlpha==.8)
P.SetCompact(true)
assert(P.frame:GetWidth()==300 and P.frame:GetHeight()==180 and P.frame:GetAlpha()==.8)
P.Init() -- simulated reload must retain compact mode, saved size and data
assert(P.db.settings.compact and P.db.notes[once.id]==once and c.professions[2871]==old)
P.Render();assert(P.frame:GetAlpha()==.8)
P.SetCompact(false);P.Show('daily');P.UpdateCountdown()
assert(P.countdown:GetText():find('Daily reset:',1,true))
P.Show('weekly');P.UpdateCountdown()
assert(P.countdown:GetText():find('Weekly reset:',1,true))
-- Dynamic layout and widget pools at several supported sizes.
P.db.settings.priorExpanded=true
for _,size in ipairs({{940,560},{1040,740},{1320,900}}) do
 P.frame:SetSize(size[1],size[2])
 for _,view in ipairs({'daily','weekly','monthly','settings','reminders'}) do P.Show(view) end
end
P.NoteEditor(once)
local editor=P.noteEditor;local warmed=frameCount
for i=1,10 do P.NoteEditor(once) end
assert(frameCount==warmed,'Note editor leaked frames')
editor.text:SetText('');editor.save:GetScript('OnClick')()
assert(editor:IsShown() and editor.errorText:GetText()~='')
editor.text:SetText('Edited custom note');editor.mode='days';editor.interval:SetText('3')
editor.save:GetScript('OnClick')()
assert(once.text=='Edited custom note' and once.interval==3 and once.mode=='days')
for i=1,3 do
 for _,view in ipairs({'daily','weekly','monthly','settings','reminders'}) do P.Show(view) end
 P.SetCompact(true);P.SetCompact(false)
end
warmed=frameCount
for i=1,15 do
 for _,view in ipairs({'daily','weekly','monthly','settings','reminders'}) do P.Show(view) end
 P.SetCompact(true);P.SetCompact(false)
end
assert(frameCount==warmed,'v0.2 UI leaked frames')
assert(SLASH_DUCKMOOPLANNER3=='/planner')
SlashCmdList.DUCKMOOPLANNER('compact');assert(P.db.settings.compact)
SlashCmdList.DUCKMOOPLANNER('full');assert(not P.db.settings.compact)
-- Dismissal should affect only the selected profession / reminder.
local originalSecond=second.patron.due
M.Complete(r,now);assert(second.patron.due==originalSecond)
print('PASS: prior-expansion migration/filtering, note CRUD/recurrence, reset timing, compact grouping, saved geometry/mode/opacity, resize layouts, countdowns and v0.2 frame reuse')
''')

lua.execute(r'''
local M=P.Model
local now=GetServerTime()
local c=P.db.characters['Player-1'];local r=c.professions[2906]
local second=c.professions[2918]
-- Test actual compact button callbacks, not just their model function.
r.amount=1000;second.amount=1000
M.SetSchedule(r,'four',M.Day(now));M.SetSchedule(second,'four',M.Day(now))
P.SetCompact(true)
local otherDue=second.patron.due
local clicked=false
for _,widget in ipairs(P.widgets) do
 local pool=widget._dmpPools and widget._dmpPools.ButtonBackdropTemplate
 if pool then for _,b in ipairs(pool) do
  if b:IsShown() and b:GetText()=='Checked patrons' then b:GetScript('OnClick')();clicked=true;break end
 end end
 if clicked then break end
end
assert(clicked and M.Key(r.patron.due)==M.Key(M.AddDays(now,4)))
assert(second.patron.due==otherDue)
local note=assert(P.SaveNote(nil,'Delete this only',M.Key(now),'once'))
local keep=assert(P.SaveNote(nil,'Keep this reminder',M.Key(now),'once'))
P.DeleteNote(note)
assert(lastPopup.name=='DUCKMOOPLANNER_DELETE_NOTE' and lastPopup.data==note.id)
StaticPopupDialogs.DUCKMOOPLANNER_DELETE_NOTE.OnAccept(nil,lastPopup.data)
assert(P.db.notes[note.id]==nil and P.db.notes[keep.id]==keep)
-- The unavailable daily API must never silently use the weekly reset instead.
local dailyAPI=C_DateAndTime.GetSecondsUntilDailyReset
C_DateAndTime.GetSecondsUntilDailyReset=nil
assert(P.GetResetSeconds('daily')==nil and P.GetResetSeconds('weekly')~=nil)
C_DateAndTime.GetSecondsUntilDailyReset=dailyAPI
-- Even a one-point spend must move the frozen forecast.
r.amount=1000;r.observedAt=now;r.secondsPerPoint=240;r.max=1000
CURRENCY.quantity=999;P.Snapshot(r)
assert(r.amount==999 and M.FullAt(r)==now+240)
-- Overdue weekly forecasts keep the reset weekday instead of drifting with today.
local due=M.ParseDay('2026-09-29')+10*3600
local weekly={text='Reset',mode='weeklyReset',due=due}
local dates=M.NoteDates(weekly,M.Day(now),M.AddDays(now,14),now)
assert(#dates>=2 and dates[1].overdue)
assert(date('*t',dates[2].at).wday==date('*t',due).wday)
print('PASS: actual compact Done buttons, targeted deletion, unavailable reset API, one-point spending and overdue weekly forecast weekday')
''')

lua.execute(r'''
local M=P.Model
local now=GetServerTime();local today=M.Day(now);local finish=M.AddDays(today,7)
local c=P.db.characters['Player-1'];local r=c.professions[2906]
-- A compact Done button must exist before any patron schedule has been configured.
r.patron=nil;r.amount=1000;r.observedAt=now
P.SetCompact(true)
local clicked=false
for _,widget in ipairs(P.widgets) do
 local pool=widget._dmpPools and widget._dmpPools.ButtonBackdropTemplate
 if pool then for _,b in ipairs(pool) do
  if b:IsShown() and b:GetText()=='Checked patrons' then b:GetScript('OnClick')();clicked=true;break end
 end end
 if clicked then break end
end
assert(clicked and r.patron.mode=='four' and r.patron.lastDone==now)
assert(M.Key(r.patron.due)==M.Key(M.AddDays(now,4)))
-- Full bars and overdue work are not weekly entries.
local upcoming=M.Upcoming(P.db,today,finish,now,'')
for _,e in ipairs(upcoming) do assert(not e.ready and not e.overdue) end
P.SetCompact(false);P.Show('weekly')
for _,widget in ipairs(P.widgets) do
 for _,pool in pairs(widget._dmpPools or {}) do
  for _,child in ipairs(pool) do assert(child:GetText()~='Ready / overdue') end
 end
end
-- Hundreds of characters: pinned current + at most 15 roster characters per page.
for i=1,400 do
 local guid='Alt-'..i
 P.db.characters[guid]={name=string.format('Gremlin%03d',i),realm=i%2==0 and 'Garona' or 'Malygos',class='MAGE',professions={
  [2906]={name='Alchemy',skillLineID=2906,amount=1000,max=1000,observedAt=now,secondsPerPoint=240},
  [2918]={name='Tailoring',skillLineID=2918,amount=1000,max=1000,observedAt=now,secondsPerPoint=240}
 }}
end
local s=P.db.settings
s.rosterProfession=nil;s.rosterRealm=nil;s.rosterGroup=nil;s.priorExpanded=false
local pinned,all=M.Roster(P.db,'Player-1',{})
assert(pinned.guid=='Player-1' and #all==400)
local _,filtered=M.Roster(P.db,'Player-1',{realm='Garona',profession='Alchemy',sort='realm'})
assert(#filtered==200 and #filtered[1].professions==1)
local firstGroup=assert(P.SaveGroup(nil,'Potion battalion'))
assert(P.SaveGroup(nil,'potion battalion')==nil)
M.AssignGroup(P.db,{'Alt-1','Alt-2','Player-1'},firstGroup,true)
local pin,grouped=M.Roster(P.db,'Player-1',{group=firstGroup,sort='group'})
assert(pin.guid=='Player-1' and #grouped==2)
local secondGroup=assert(P.SaveGroup(nil,'Tailor patrol'))
M.AssignGroup(P.db,{'Alt-1'},secondGroup,true)
assert(M.GroupNames(P.db,P.db.characters['Alt-1']):find('Tailor patrol',1,true))
P.SaveGroup(firstGroup,'Potion squad')
assert(M.GroupNames(P.db,P.db.characters['Alt-1']):find('Potion squad',1,true))
M.DeleteGroup(P.db,secondGroup)
assert(P.db.characters['Alt-1'].groups[secondGroup]==nil and P.db.characters['Alt-1'].professions[2906])
P.settingsTab='roster';P.Show('settings')
assert(P.currentRoster.guid=='Player-1' and #P.filteredRoster==400)
P.rosterPage=2;P.Render()
local warm=frameCount
for page=3,20 do P.rosterPage=page;P.Render() end
assert(frameCount==warm,'Roster pages allocate frames for every alt')
assert(#P.widgets<65,'Roster rendered hundreds of rows instead of one page')
s.rosterGroup=firstGroup;P.Render();assert(#P.filteredRoster==2 and P.currentRoster.guid=='Player-1')
s.rosterRealm='No such realm';P.Render();assert(#P.filteredRoster==0 and P.currentRoster.guid=='Player-1')
s.rosterRealm=nil;s.rosterGroup=nil
-- Select a filter through the real chooser callback.
P.Choose('Realm',{{label='Garona',value='Garona'}},function(value) s.rosterRealm=value end)
P.choice.buttons[1]:GetScript('OnClick')();assert(s.rosterRealm=='Garona')
s.rosterRealm=nil
P.GroupEditor({'Alt-3','Alt-4'})
P.groupEditor.edit:SetText('Weekend ducks');P.groupEditor.save:GetScript('OnClick')()
local assigned=P.db.nextGroupID-1
assert(P.db.characters['Alt-3'].groups[assigned] and P.db.characters['Alt-4'].groups[assigned])
P.settingsTab='appearance';P.Show('settings')
assert(s.fullAlpha==.85)
P.fullOpacitySlider:SetValue(90);assert(s.fullAlpha==.9 and P.frame:GetAlpha()==.9)
P.settingsTab='about';P.Render()
local about=''
for _,widget in ipairs(P.widgets) do
 for _,pool in pairs(widget._dmpPools or {}) do for _,child in ipairs(pool) do if child:IsShown() then about=about..(child:GetText() or '') end end end
end
assert(about:find('DuckMoo Services: Concentration Planner',1,true))
assert(about:find('DuckMoo Media',1,true) and about:find('amazon.com/author/kenzieduckmoo',1,true))
assert(about:find('@KenzieDuckMoo',1,true) and about:find('@kenzieduckmoo.bsky.social',1,true))
-- Minimap entry points and persisted visibility.
Minimap=CreateFrame('Frame');Minimap:SetSize(140,140)
P.CreateMinimap();assert(P.minimap:IsShown())
P.minimap:GetScript('OnClick')(P.minimap,'RightButton');assert(P.view=='settings')
P.minimap:GetScript('OnClick')(P.minimap,'LeftButton');assert(not P.frame:IsShown())
P.minimap:GetScript('OnClick')(P.minimap,'LeftButton');assert(P.frame:IsShown())
s.hideMinimap=true;P.CreateMinimap();assert(not P.minimap:IsShown())
s.hideMinimap=false;P.CreateMinimap();assert(P.minimap:IsShown())
print('PASS: unscheduled compact Done, upcoming-only weeks, 400-character paging/filtering/sorting, multiple and bulk groups, current-character pinning, full opacity, About and minimap interactions')
''')
lua.execute(r'''
P.SetCompact(true);P.db.settings.denseCompact=false;P.Render();local roomy=P.content:GetHeight()
P.db.settings.denseCompact=true;P.Render();assert(P.content:GetHeight()<roomy,'Dense setting did not reduce row height')
local shown=0;for _,row in ipairs(P.widgets)do
 if row:IsShown() and row:GetHeight()==60 then shown=shown+1 end
end
assert(shown>0)
local exported=P.ExportRoster();local guid=next(exported);local name=P.db.characters[guid].name
exported[guid].name='Altered copy';assert(P.db.characters[guid].name==name)
print('PASS: denser compact rows retain the dashboard and roster export does not alias saved characters')
''')
lua.execute(r'''
NOW=time({year=2026,month=10,day=1,hour=12,min=0,sec=0})
local M=P.Model
local function profession(name,amount)
 return {name=name,expansion='Midnight '..name,skillLineID=2906,amount=amount,max=1000,secondsPerPoint=240,observedAt=NOW}
end
local r=profession('Alchemy',1000);M.SetSchedule(r,'four',M.AddDays(M.Day(NOW),-1))
P.db.characters={['Player-1']={name='Ember',realm='Garona',class='MAGE',professions={[2906]=r,[2908]=profession('Enchanting',950)}},alt={name='Willow',realm='Garona',class='MAGE',professions={[2906]=profession('Alchemy',500)}}}
P.db.notes={};P.filter='';P.search:SetText('');P.followToday=true
P.SaveNote(nil,'Pick up crafting supplies',M.Key(NOW),'once')
P.SetCompact(false);P.Show('daily')
assert(#P.dailySections.concentration==2 and #P.dailySections.patron==1 and #P.dailySections.note==1,'Daily summary lost events')
assert(P.dailySections.concentration[1].ready,'Ready concentration no longer ranks first')
local clicked=false
for _,row in ipairs(P.widgets)do
 for _,pool in pairs(row._dmpPools or {})do for _,b in ipairs(pool)do
  if b:IsShown() and b:GetText()=='Checked patrons'then b:GetScript('OnClick')();clicked=true;break end
 end end
end
assert(clicked and M.Key(r.patron.due)==M.Key(M.AddDays(M.Day(NOW),4)),'Redesigned check-in failed to advance its schedule')
assert(#P.dailySections.patron==0,'Checked patrons stayed actionable')
for _,size in ipairs({{940,560},{1040,740},{1320,900}})do
 P.frame:SetSize(size[1],size[2])
 for _,view in ipairs({'daily','weekly','monthly','reminders','settings'})do
  P.Show(view)
  assert(P.scroll.points[1][2]==194 and P.width==size[1]-222,'Full view lost sidebar clearance')
  assert(P.scroll:GetHeight()==size[2]-178,'Full view exceeds its viewport')
  local active=0;for _,b in ipairs(P.tabs)do if b._active then active=active+1;assert(b.view==view)end end
  assert(active==1 and P.sidebar:IsShown(),'Navigation state is incorrect')
 end
end
P.filter='does not match';P.SetCompact(true)
assert(not P.sidebar:IsShown() and not P.search:IsShown() and not P.scanButton:IsShown())
assert(P.content:GetHeight()>=145,'Old full-view search hid the current-character compact dashboard')
assert(P.scroll.points[1][2]==10,'Compact view reserved sidebar space')
P.SetCompact(false);P.filter='';P.search:SetText('');P.settingsTab='appearance';P.Show('settings')
local found=false
for _,w in ipairs(P.widgets)do if w:GetText():find('Palette:',1,true)then w:GetScript('OnClick')();found=true;break end end
assert(found and P.choice:IsShown(),'Palette chooser is inaccessible')
P.choice.callback('translight');assert(P.db.settings.theme=='translight' and P.Themes.translight.name=='Trans pride - dusk')
local function lum(c)
 local function ch(v)return v<=.04045 and v/12.92 or((v+.055)/1.055)^2.4 end
 return .2126*ch(c[1])+.7152*ch(c[2])+.0722*ch(c[3])
end
for _,key in ipairs({'purple','plum','light','trans','translight'})do
 local t=P.Themes[key]
 for _,surface in ipairs({t.bg,t.sidebar or t.panel,t.panel,t.button,t.hover})do
  local a,b=lum(t.text),lum(surface);assert((math.max(a,b)+.05)/(math.min(a,b)+.05)>=4.5,'Unreadable Planner palette: '..key)
 end
 P.db.settings.theme=key;P.Show('daily');assert(P.frame._surfaceColor[1]==t.bg[1])
end
print('PASS: grouped daily summaries, real patron-check callbacks, sidebar sizing/navigation, compact current-character scope and Folio palette chooser/contrast')
''')
lua.execute(r'''
P.SetCompact(false)
for _,view in ipairs({'daily','weekly','monthly','settings','reminders'})do
 P.Show(view)
 assert(P.countdown==P.fullCountdown and P.countdown.parent==P.sidebar,'Sidebar paints over reset text')
 assert(P.fullCountdown:IsShown() and not P.compactCountdown:IsShown(),'Both timer regions are visible')
 local expected=view=='weekly' and 'Weekly reset:'or'Daily reset:'
 assert(P.countdown:GetText():find(expected,1,true),'Wrong timer selected after page change')
end
P.SetCompact(true)
assert(P.countdown==P.compactCountdown and P.countdown.parent==P.frame)
assert(P.compactCountdown:IsShown() and not P.fullCountdown:IsShown())
P.SetCompact(false);assert(P.countdown==P.fullCountdown)
print('PASS: reset timer belongs to its visible panel and switches correctly across pages and modes')
''')
lua.execute(r'''
P.SetCompact(false);for _,view in ipairs({'daily','weekly','monthly','settings','reminders'})do P.Show(view);assert(P.frame.topLevel and P.frame.flattenLayers)end
P.SetCompact(true);assert(P.frame.topLevel and P.frame.flattenLayers);P.SetCompact(false)
local count=0
for _,f in ipairs(frames)do
 if f.parent==UIParent and f._round then assert(f.topLevel and f.flattenLayers,'Standalone window lost grouped stacking');count=count+1 end
end
assert(count>=4,'Window stacking was not checked on dialogs')
print('PASS: main and dialog window render groups survive page and mode changes')
''')
print('All checks passed. WoW client integration still requires in-game verification.')

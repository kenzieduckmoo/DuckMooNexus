#!/usr/bin/env python3
"""Lua 5.1 behavior and native-UI mock tests. pip install lupa==2.8."""
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
date=os.date;time=os.time;F={};SlashCmdList={};UISpecialFrames={}
NOW=1801767600
function GetServerTime() return NOW end
function UnitGUID() return 'Player-1' end
function UnitName() return 'Voidchicken' end
function GetNormalizedRealmName() return 'Garona' end
function GetRealmName() return 'Garona' end
function UnitClass() return 'Priest','PRIEST',5 end
function UnitRace() return 'Human','Human' end
function UnitFactionGroup() return 'Alliance' end
function UnitSex() return 3 end
function UnitLevel() return 82 end
function UnitXP() return 130 end
function UnitXPMax() return 1000 end
function GetXPExhaustion() return 1500 end
function GetMaxLevelForPlayerExpansion() return 90 end
function GetCurrentRegion() return 1 end
function GetBindLocation() return 'Dornogal' end
function GetRealZoneText() return 'Isle of Dorn' end
function GetSubZoneText() return 'Dornogal' end
function GetSpecialization() return 1 end
function GetSpecializationInfo() return 256,'Discipline',nil,1234,'HEALER' end
function GetAverageItemLevel() return 604.7,602.4 end
function UnitStat(_,i) return i*10,i*20 end
function UnitArmor() return 100,200 end
function UnitHealthMax() return 123456 end
function UnitPowerMax() return 100 end
function UnitPowerType() return 0,'MANA' end
function GetProfessions() return 1,2,nil,3 end
function GetProfessionInfo(i)
 if i==1 then return 'Tailoring',1,100,100,0,0,197 end
 if i==2 then return 'Enchanting',2,75,100,0,0,333 end
 return 'Fishing',3,10,100,0,0,356
end
function InCombatLockdown() return false end
C_TradeSkillUI={GetBaseProfessionInfo=function()return {professionID=197,professionName='Tailoring'}end,
 GetChildProfessionInfo=function()return {professionID=2883,professionName='Khaz Algar Tailoring',skillLevel=100,maxSkillLevel=100}end,
 GetChildProfessionInfos=function()return {{professionID=2539,professionName='Outland Tailoring',skillLevel=75,maxSkillLevel=75},{professionID=2540,professionName='Classic Tailoring',skillLevel=0,maxSkillLevel=300}}end,
 GetAllRecipeIDs=function()return {1,2}end,GetRecipeInfo=function(id)return {learned=id==1}end,
 IsTradeSkillLinked=function()return false end,IsTradeSkillGuild=function()return false end}
local headerCollapsed=true
C_Reputation={GetNumFactions=function()return headerCollapsed and 1 or 2 end,
 GetFactionDataByIndex=function(i)
  if i==1 then return {name='Outland',factionID=1,isHeader=true,isCollapsed=headerCollapsed}end
  return {name='Honor Hold',factionID=946,reaction=6,currentStanding=9500,currentReactionThreshold=9000,nextReactionThreshold=21000,isAccountWide=false}
 end,
 ExpandFactionHeader=function()headerCollapsed=false end,CollapseFactionHeader=function()headerCollapsed=true end}
C_Map={GetBestMapForUnit=function()return 2248 end,GetMapInfo=function(id)return {mapType=3,name=id==84 and 'Stormwind' or 'Nagrand'}end}
C_MountJournal={GetMountIDs=function()return {1,2}end,GetMountInfoByID=function(id)return 'Mount',1,2,false,false,1,true,false,false,false,id==1 end}
C_PetJournal={GetNumPets=function()return 2000,30 end}
RAID_CLASS_COLORS={PRIEST={r=1,g=1,b=1}}
C_Timer={After=function(_,fn)fn()end}
C_AddOns={IsAddOnLoaded=function()return false end}
''')
lua.execute(r'''
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
function methods:SetText(t) self.text=t end
function methods:GetText() return self.text or '' end
function methods:Show() local was=self.shown;self.shown=true;if not was and self.scripts.OnShow then self.scripts.OnShow(self) end end
function methods:Hide() self.shown=false;self.focus=false;for _,f in ipairs(frames)do if f.focus then local ancestor=f.parent;while ancestor do if ancestor==self then f.focus=false;break end;ancestor=ancestor.parent end end end end
function methods:IsShown() return self.shown end
function methods:SetShown(v) if v then self:Show() else self:Hide() end end
function methods:SetVerticalScroll(v) self.scroll=v end
function methods:GetVerticalScroll() return self.scroll or 0 end
function methods:SetChecked(v) self.checked=v end
function methods:GetChecked() return self.checked end
function methods:GetPoint() return 'CENTER',UIParent,'CENTER',0,0 end
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
function methods:SetToplevel(v)assert(type(v)=='boolean');self.topLevel=v end
function methods:SetFlattensRenderLayers(v)assert(type(v)=='boolean');self.flattenLayers=v end
function methods:SetFrameLevel(v) self.level=v end
function methods:GetFrameLevel() return self.level or 3 end
function methods:GetEffectiveScale() return 1 end
function methods:GetCenter() return 100,100 end
UIParent=CreateFrame('Frame');UIParent:SetSize(1920,1080)
GameTooltip=CreateFrame('Frame')
function StaticPopup_Show(name,text,_,data) lastPopup={name=name,text=text,data=data} end

function methods:HasFocus() return self.focus==true end
function methods:SetFocus() self.focus=true end
function methods:GetLeft() return 300 end
function methods:GetTop() return 900 end
CURSOR_X=1220;CURSOR_Y=260
function GetCursorPosition() return CURSOR_X,CURSOR_Y end
function methods:ClearFocus() self.focus=false end
function methods:SetText(text,...) assert(select('#',...)==0,'SetText received an unintended extra argument');self.text=text;if self.scripts.OnTextChanged then self.scripts.OnTextChanged(self,false)end end
Minimap=CreateFrame('Frame');Minimap:SetSize(140,140)
''')
for filename in ['Model.lua','Core.lua','Coverage.lua','ATT.lua','UI.lua','Minimap.lua']:
    lua.execute("assert(loadfile(...))('DuckMooFolio',F)",str(ROOT/filename))
lua.execute(r'''
F.Init();F.Snapshot(true)
local M=F.Model;local c=F.db.characters['Player-1']
assert(c.name=='Voidchicken' and c.specName=='Discipline' and c.role=='HEALER')
assert(c.collections.mounts==1 and c.collections.pets==30)
assert(c.stats.intellect==80 and c.stats.armor==200)
assert(C_Reputation.GetNumFactions()==1,'Collapsed reputation headers were not restored')
assert(c.reputations[946].name=='Honor Hold' and c.reputations[946].value==9500)
assert(M.Level(c)=='82.13' and M.Rested(c)=='150%')
assert(M.Level({level=90,maxLevel=90})=='90' and M.Rested({level=90,maxLevel=90})=='-')
F.DiscoverProfession();c=F.db.characters['Player-1']
assert(c.professions[197].expansions[2883].rank==100)
assert(c.professions[197].expansions[2539].rank==75)
assert(not c.professions[197].expansions[2540])
assert(c.professions[197].expansions[2883].recipes==1)
C_ProfSpecs={GetConfigIDForSkillLine=function()return 42 end}
C_Traits={GetConfigInfo=function()return {treeIDs={1},name='Cloth specialist'}end,
 GetTreeNodes=function()return {1}end,
 GetNodeInfo=function()return {activeEntry={entryID=5},activeRank=10,maxRanks=30}end,
 GetEntryInfo=function()return {definitionID=9}end,
 GetDefinitionInfo=function()return {overrideName='Cloth Armor'}end}
F.DiscoverProfession()
assert(c.professions[197].expansions[2883].knowledge[1].name=='Cloth Armor')
assert(c.professions[197].expansions[2883].knowledge[1].rank==10)

local before=c.professions[197].seenAt
C_TradeSkillUI.IsTradeSkillLinked=function()return true end
F.DiscoverProfession();assert(c.professions[197].seenAt==before)
C_TradeSkillUI.IsTradeSkillLinked=function()return false end
c.tags=M.Tags(' Delves, Cloth gear, delves ');assert(c.tags.delves and c.tags['cloth gear'])
-- Hundreds of characters, combined filters, capable roles, and precise XP sorting.
for i=1,400 do
 F.db.characters['Alt'..i]={name='Alt'..i,realm=i%2==0 and 'Saurfang' or 'Garona',realmRegion='OCE',class=i%3==0 and 'WARRIOR' or 'SHAMAN',className='Shaman',race='Orc',faction='Horde',level=82,maxLevel=90,xp=i,xpMax=1000,role=i%2==0 and 'HEALER' or 'DAMAGER',specName=i%2==0 and 'Restoration' or 'Elemental',professions={},reputations={},tags={},notes={}}
end
local entries=M.Roster(F.db,{role='HEALER',faction='Horde',region='OCE'})
assert(#entries>200 and entries[1].c.role=='HEALER')
local reachedOther=false
for _,e in ipairs(entries)do if e.c.role~='HEALER' then reachedOther=true else assert(not reachedOther)end end
assert(#M.Roster(F.db,{class='PRIEST',profession='Tailoring',expansion=2539,reputation=946,tag='cloth gear'})==1)
assert(#M.Roster(F.db,{role='HEALER',class='WARRIOR'})==0)
local levels=M.Roster(F.db,{realm='Saurfang'});assert(levels[1].c.xp==400)
local grouped=M.Grouped(levels,{Saurfang=true});assert(#grouped==1 and grouped[1].count==200)
local census=M.Census(F.db);assert(census.total==401 and census.faction.Horde==400 and census.profession.Tailoring==1)
assert(#M.Options(F.db,'reputation')==1)
print('PASS: snapshots, XP, rested, expansion skills, linked-profession guard, header restoration, 400-character filters and role ordering')
-- Native UI interaction and frame reuse across all pages.
F.Show();assert(F.tab=='sheet' and F.selected=='Player-1')
assert(F.closeButton:GetFrameLevel()>F.headerDrag:GetFrameLevel(),'Close button is underneath the drag surface')
F.closeButton:GetScript('OnClick')(F.closeButton);assert(not F.frame:IsShown());F.Show()
assert(F.tabButtons.att.parent==F.sidebar and F.tabButtons.notes.points[1][3]>F.tabButtons.att.points[1][3] and F.tabButtons.reps.points[1][3]>F.tabButtons.census.points[1][3],'Character and warband sidebar groups are out of order')
local function luminance(c)
 local function channel(v)return v<=.04045 and v/12.92 or ((v+.055)/1.055)^2.4 end
 return .2126*channel(c[1])+.7152*channel(c[2])+.0722*channel(c[3])
end
for _,id in ipairs({'light','trans'})do
 local t=F.Themes[id];for _,surface in ipairs({t.bg,t.panel,t.button})do
  local a,b=luminance(surface),luminance(t.text);assert((math.max(a,b)+.05)/(math.min(a,b)+.05)>=4.5,'Bright theme has unreadable text')
 end
end
for _,tab in ipairs({'sheet','skills','reps','notes','roster','census','att','settings'})do F.tab=tab;F.Render()end
F.tab='notes';F.Render();F.notePanel.edit:SetText('Cloth gear specialist. Stormlesbian makes bolts.')
assert(F.db.characters['Player-1'].notes.general=='Cloth gear specialist. Stormlesbian makes bolts.')
F.TagPicker();F.tagPicker.input:SetText('Delves, Cloth gear');F.tagPicker.add();F.db.characters['Player-1'].tags=F.Clean(F.tagPicker.draft);F.tagPicker:Hide();assert(F.db.characters['Player-1'].tags.delves)
F.Snapshot(true);assert(F.db.characters['Player-1'].notes.general:find('Stormlesbian'))
F.selected='Alt1';F.Render();F.notePanel.edit:SetText('Legacy farming on this one')
assert(F.db.characters.Alt1.notes.general=='Legacy farming on this one')
assert(F.db.characters['Player-1'].notes.general:find('Stormlesbian'))
F.selected='Player-1'
F.filters={role='HEALER',region='OCE'};F.tab='roster';F.Render();assert(#F.filteredRoster>200)
-- Search must retain keyboard focus after every character, including rerenders.
F.filters={};F.Render();F.rosterSearch:SetFocus()
for _,query in ipairs({'V','Vo','Void'})do F.rosterSearch.text=query;F.rosterSearch:GetScript('OnTextChanged')(F.rosterSearch,true);assert(F.rosterSearch:HasFocus());assert(#F.filteredRoster==1)end
F.filters={};F.rosterSearch:ClearFocus();F.Render()
local function visible(b) while b do if not b:IsShown()then return false end;b=b.parent end;return true end
local function click(caption)
 for i=#frames,1,-1 do local b=frames[i];if b.kind=='Button' and b:GetText()==caption and visible(b) and b:GetScript('OnClick')then b:GetScript('OnClick')(b);return end end
 error('Button not found: '..caption)
end
click('>');assert(F.page==2);click('<');assert(F.page==1)
F.db.settings.collapsed.Garona=true;F.filters.realm='Garona';F.Render();click('All realms');assert(not F.filters.realm and not next(F.db.settings.collapsed))
-- Notebook category buttons and typing preserve focus and isolate each field.
F.tab='notes';F.Render();click('Adventuring');F.notePanel.edit:SetFocus();F.notePanel.edit:SetText('Delves are my mission');F.Render();assert(F.notePanel.edit:HasFocus())
assert(c.notes.adventuring=='Delves are my mission');click('Save note');assert(F.notePanel.saved:GetText():find('Saved'))
click('Purpose & plans');assert(F.notePanel.edit:GetText():find('Stormlesbian'))
F.TagPicker();local p=F.tagPicker;p.input:SetText('Special gremlin');click('Save tags');assert(c.tags['special gremlin']=='Special gremlin')
F.TagPicker();local first=p.options[1];p.rows[1]:GetScript('OnClick')();click('Save tags');assert(c.tags[first:lower()])
F.tab='skills';F.Render();click('[-] Earned titles (0)');assert(F.db.settings.sections['Player-1:titles'])
-- Theme changes affect text and surfaces without fading the whole window.
for id in pairs(F.Themes)do F.db.settings.theme=id;F.tab='settings';F.Render();F.opacitySlider:SetValue(65);assert(F.frame._surfaceColor[4]==.65 and F.frame:GetAlpha()==1)end
F.db.settings.theme='purple'
-- Resizing starts from the original dimensions; the first update never jumps.
local w,h=F.frame:GetWidth(),F.frame:GetHeight();F.resizeGrip:GetScript('OnMouseDown')(F.resizeGrip,'LeftButton');F.resizeGrip:GetScript('OnUpdate')();assert(F.frame:GetWidth()==w and F.frame:GetHeight()==h)
CURSOR_X=CURSOR_X+50;CURSOR_Y=CURSOR_Y-25;F.resizeGrip:GetScript('OnUpdate')();assert(F.frame:GetWidth()==w+50 and F.frame:GetHeight()==h+25);F.resizeGrip:GetScript('OnMouseUp')();assert(F.db.settings.size[1]==w+50)
local warm=frameCount
for j=1,3 do for _,tab in ipairs({'sheet','skills','reps','notes','roster','census','att','settings'})do F.tab=tab;F.Render()end end
warm=frameCount
for j=1,10 do for _,tab in ipairs({'sheet','skills','reps','notes','roster','census','att','settings'})do F.tab=tab;F.Render()end end
assert(frameCount==warm,'Folio browsing leaked native frames')
F.Choose('Reputation',M.Options(F.db,'reputation'),function(id)F.filters.reputation=id end)
F.choice.rows[1]:GetScript('OnClick')();assert(F.filters.reputation==946)
F.CreateMinimap();assert(F.minimap:IsShown())
F.minimap:GetScript('OnClick')(F.minimap,'LeftButton');assert(not F.frame:IsShown())
F.minimap:GetScript('OnClick')(F.minimap,'LeftButton');assert(F.frame:IsShown() and F.tab=='sheet')
SlashCmdList.DUCKMOOFOLIO('roster');assert(F.tab=='roster')
print('PASS: all folio pages, per-character note persistence, chooser, minimap, slash commands and stable frame pools')
-- ATT missing, not ready, read-only rankings, duplicate quests and capitals.
local app,message=F.ATTStatus();assert(not app and message:find('Enable All The Things'))
AllTheThings={Windows={}};app,message=F.ATTStatus();assert(not app and message:find('not ready'))
local dungeon={instanceID=10,text='Legacy dungeon',total=12,progress=2,visible=true}
local raid={instanceID=11,text='Legacy raid',total=20,progress=5,visible=true}
local root={modeString='Character mode',g={
 {tierID=2,headerID=100,g={dungeon}},
 {tierID=2,headerID=101,g={raid}},
 {tierID=2,mapID=107,g={{questID=1,collectible=true,visible=true},{questID=1,collectible=true,visible=true},{questID=2,collectible=true,collected=true},{questID=3,collectible=true,visible=false}}},
 {tierID=1,mapID=84,g={{questID=4,collectible=true,visible=true}}},
 {tierID=12,headerID=101,g={{instanceID=12,text='Current raid',total=100,progress=0,visible=true}}}
}}
AllTheThings={Windows={Prime={data=root}},HeaderConstants={DUNGEONS=100,RAIDS=101},GroupFilter=function()return true end}
F.RefreshATT();local att=F.db.characters['Player-1'].att
assert(att and #att.dungeons==1 and att.dungeons[1].missing==10)
assert(#att.raids==1 and att.raids[1].missing==15)
assert(#att.zones==1 and att.zones[1].missing==1)
assert(dungeon.total==12 and dungeon.progress==2 and not dungeon.visited,'ATT data was mutated')
F.tab='att';F.Render()
-- ATT trees can expose expansion objects with no raid/dungeon header.
local selectedTier=2
EJ_GetCurrentTier=function()return selectedTier end
EJ_GetNumTiers=function()return 2 end
EJ_SelectTier=function(t)selectedTier=t end
EJ_GetInstanceByIndex=function(index,isRaid)if index==1 then return isRaid and 11 or 10 end end
AllTheThings.HeaderConstants={}
root.g={{expansionID=2,g={dungeon,raid}}}
F.RefreshATT();att=F.db.characters['Player-1'].att
assert(selectedTier==2 and #att.dungeons==1 and #att.raids==1 and att.raids[1].expansion=='The Burning Crusade')
-- Outdoor ATT groups often lack expansion headers. Resolve map ancestry and
-- distinct versions of zones, and exclude TWW/Midnight from fresh and old lists.
local oldMap=C_Map.GetMapInfo
local mapInfo={ [101]={mapType=2,name='Outland'},[102]={mapType=3,name='Zangarmarsh',parentMapID=101},[572]={mapType=2,name='Draenor'},[550]={mapType=3,name='Nagrand',parentMapID=572},[2395]={mapType=3,name='Eversong Woods',parentMapID=2537},[2393]={mapType=3,name='Silvermoon City',parentMapID=2537} }
C_Map.GetMapInfo=function(id)return mapInfo[id] or oldMap(id)end
root.g={
 {mapID=102,g={{questID=1001,collectible=true,visible=true}}},
 {mapID=550,g={{questID=1002,collectible=true,visible=true}}},
 {mapID=2395,g={{questID=1003,collectible=true,visible=true}}},
 {mapID=2393,g={{questID=1004,collectible=true,visible=true}}},
 {tierID=10,headerID=101,g={{instanceID=20,text='Dragonflight raid',total=10,progress=0,visible=true}}},
 {tierID=11,headerID=101,g={{instanceID=21,text='War Within raid',total=10,progress=0,visible=true}}},
 {tierID=12,headerID=101,g={{instanceID=22,text='Midnight raid',total=10,progress=0,visible=true}}},
 {headerID=101,g={{instanceID=23,text='Unknown raid',total=10,progress=0,visible=true}}}
}
AllTheThings.HeaderConstants={RAIDS=101};F.RefreshATT();att=F.db.characters['Player-1'].att
assert(#att.raids==1 and att.raids[1].name=='Dragonflight raid')
local byMap={};for _,z in ipairs(att.zones)do byMap[z.mapID]=z end
assert(byMap[102].expansion=='The Burning Crusade' and byMap[550].expansion=='Warlords of Draenor' and byMap[2395].expansion=='Midnight' and not byMap[2393])
assert(F.ATTExpansionLabel({mapID=102,expansion='Expansion not supplied'},true)=='The Burning Crusade','Older zone snapshot was not repaired at display time')
assert(not F.IsLegacyATT({expansion='The War Within'}) and not F.IsLegacyATT({expansion='Midnight'}) and F.IsLegacyATT({expansion='Dragonflight'}))
local parent={expansionID=6.02};local child={parent=parent};assert(F.ATTNodeTier(child)==6);parent.parent=child;assert(F.ATTNodeTier(child)==6)
att.raids[#att.raids+1]={expansion='The War Within',name='Cached current raid',missing=99}
F.tab='att';F.Render()
for _,f in ipairs(frames)do if f.kind=='FontString' and f:IsShown() then assert(f:GetText()~='Cached current raid','Old current-expansion snapshot leaked into legacy display')end end
print('PASS: close control layering/action, tab order, bright theme contrast, headerless zone expansions, capital exclusions and legacy cutoff for new/cached snapshots')
-- Captures are deferred in combat and secret values are never persisted.
local old=F.db.characters['Player-1'].lastSeen
InCombatLockdown=function()return true end;NOW=NOW+100;F.Snapshot(true);assert(F.db.characters['Player-1'].lastSeen==old)
InCombatLockdown=function()return false end
local secret={};issecretvalue=function(v)return v==secret end
assert(F.Clean({bad=secret,good='ok'}).bad==nil)
assert(F.Safe(function()return nil,secret,'safe' end)==nil)
-- Namespaced Retail specialization API, hero talents, and movement speed.
C_SpecializationInfo={GetSpecialization=GetSpecialization,GetSpecializationInfo=GetSpecializationInfo};GetSpecialization=nil;GetSpecializationInfo=nil
C_ClassTalents={GetActiveHeroTalentSpec=function()return 99 end,GetActiveConfigID=function()return 42 end};C_Traits.GetSubTreeInfo=function()return {name="Oracle"}end
GetUnitSpeed=function()return 0,8.4,0,0 end;CR_SPEED=14;GetCombatRating=function()return 120 end;GetCombatRatingBonus=function()return 4 end
F.Snapshot(true);assert(c.specName=='Discipline' and c.heroSpec=='Oracle' and math.abs(c.stats.movement-120)<.001 and c.stats.speedRating==120)
assert(M.Spec(c)=='Oracle Discipline');assert(M.Spec({level=80,heroSpec='Oracle',specName='Discipline'})=='Discipline')
assert(M.RealmRegion("AmanThul",1)=='NA-OCE' and M.RealmRegion('Saurfang',1)=='NA-OCE' and M.RealmRegion('Garona',1)=='NA-US' and M.RealmRegion("Quel'Thalas",1)=='NA-LATAM' and M.RealmRegion('TolBarad',1)=='NA-BR')
assert(M.Census({characters={a={level=90}}}).band['90s']==1)
assert(M.Display('|cffff7d01Manaforge Omega|r')=='Manaforge Omega')
assert(M.Display('|cfffFF7D01Manaforge Omega|r')=='Manaforge Omega')
-- Serialize/reinitialize SavedVariables, switch alts, then read unavailable APIs.
local saved=F.Clean(DuckMooFolioDB);DuckMooFolioDB=saved;F.Init();c=F.db.characters['Player-1']
UnitGUID=function()return 'Alt1' end;F.Snapshot(true);assert(F.db.characters['Player-1'].ilvl==602.4 and c.stats.intellect==80 and c.notes.general:find('Stormlesbian'))
UnitGUID=function()return 'Player-1' end
GetAverageItemLevel=function()return 0,0 end;UnitStat=function()return nil end;GetProfessions=function()return nil end;C_SpecializationInfo.GetSpecialization=function()return nil end
F.Snapshot(true);assert(c.ilvl==602.4 and c.stats.intellect==80 and c.professions[197].expansions[2539].rank==75)
UnitStat=function()return 0,0 end;UnitHealthMax=function()return 0 end
F.Snapshot(true,true);assert(c.stats.intellect==80 and c.health==123456)
assert(F.db.characters['Player-1'].loggedOut)
print('PASS: ATT missing/not-ready states, instance rankings, quest deduplication, capital exclusion, read-only traversal, combat deferral and secret-value handling')
''')

lua.execute(r'''
local M=F.Model
-- Completion is compared as exact fractions, including different denominators.
local function instance(id,progress,total,tier)
 return {instanceID=id,name='Instance '..id,kind='raid',progress=progress,total=total,tier=tier or 2,expansion='The Burning Crusade',missing=total-progress}
end
local snapshot={completion={instance(1,2,10),instance(2,20,100),instance(3,21,100),instance(4,0,100,11),instance(5,0,0),instance(6,-1,10)}}
local choices=0
local target=F.SelectATDART(snapshot,function(n)choices=choices+1;assert(n==2);return 2 end)
assert(target.instanceID==2 and choices==1)
for i=1,20 do assert(F.GetATDART(snapshot).instanceID==2)end
assert(choices==1,'Rendering rerolled the tied target')
local saved=F.Clean(snapshot);assert(F.GetATDART(saved).instanceID==2,'Saved target changed on reload')
local unique={completion={instance(1,1,3),instance(2,33,100)}};assert(F.SelectATDART(unique).instanceID==2,'Rounded percentages were used to compare completion')
assert(F.SelectATDART({completion={instance(9,10,10)}}).progress==10)
assert(F.SelectATDART({completion={instance(9,0,10,12)}})==nil)
local old={raids={{name='Old raid',missing=90,tier=2}}};assert(not F.GetATDART(old) and old.targetEvaluated,'Missing totals must not fabricate a percentage')
-- Capture total/progress, complete instances, and stable target with live adapter.
AllTheThings.HeaderConstants={RAIDS=101,DUNGEONS=100}
local root=AllTheThings.Windows.Prime.data
root.g={{tierID=2,headerID=101,g={instance(40,2,10),instance(41,20,100),instance(42,10,10)}},{tierID=11,headerID=101,g={instance(43,0,10,11)}}}
for _,group in ipairs(root.g)do for _,row in ipairs(group.g)do row.visible=true end end
F.RefreshATT()
local att=F.db.characters['Player-1'].att
assert(att.schema==3 and #att.completion==3 and #att.raids==2 and att.atdart and att.atdart.total>0)
local chosen=att.atdart.instanceID;F.selected='Player-1';F.tab='att';F.Render();F.Render();assert(att.atdart.instanceID==chosen)
local sawPercent=false;for _,f in ipairs(frames)do if f.kind=='FontString' and f:IsShown() and f:GetText()=='20.00%'then sawPercent=true end end;assert(sawPercent,'Target percentage was not displayed')
-- Coverage: a trained skill, explicit zero rank, and an unscanned base profession.
local db={characters={trained={name='Crafter',realm='Garona',profSeenAt=NOW,professions={[197]={name='Tailoring',expansions={[2539]={name='Outland Tailoring',rank=75,max=75}},expansionChecks={[2539]=NOW,[2540]=NOW}}}},unscanned={name='Scan me',realm='Saurfang',profSeenAt=NOW,professions={[333]={name='Enchanting',expansions={}}}},unknown={name='Never scanned',professions={}}}}
local rows,summary=M.ProfessionCoverage(db);assert(#rows==156 and summary.unknownCharacters==1)
local function row(id)for _,r in ipairs(rows)do if r.expansionID==id then return r end end end
assert(row(2539).status=='covered' and #row(2539).owners==1 and row(2539).owners[1].rank==75)
assert(row(2540).status=='gap','Explicitly unlearned Classic Tailoring was called unknown')
assert(row(2918).status=='needs_scan','Unscanned Midnight Tailoring was called absent')
assert(row(2906).status=='gap','No-owner Alchemy was omitted from blindspots')
db.characters.trained.professions[197].expansions[2539].rank=0
rows=M.ProfessionCoverage(db);assert(row(2539).status=='gap','Zero ranks were counted as trained')
-- The API catalogue contains unlearned skills without claiming current ownership.
C_TradeSkillUI.GetProfessionInfoBySkillLineID=function(id)if id==2918 then return {professionID=id,parentProfessionID=197,parentProfessionName='Tailoring',professionName='Localized Midnight Tailoring',expansionName='Midnight',skillLevel=0}end end
F.UpdateProfessionCatalog();assert(F.db.professionCatalog[197].expansions[2918].name=='Localized Midnight Tailoring')
-- UI navigation, independent filters, paging and bounded frame reuse.
F.tab='census';F.censusMode='coverage';F.Render();assert(#F.coverageRows>100)
F.coverageFilters={professionID=197,tier=2,all=true};F.Render();assert(#F.coverageRows==1)
local found=false
for _,b in ipairs(frames)do if b.kind=='Button' and b.parent==F.content and b:IsShown() and b:GetHeight()==43 and b:GetScript('OnClick')then b:GetScript('OnClick')(b);found=true;break end end
assert(found and F.tab=='roster' and F.filters.profession=='Tailoring' and F.filters.expansion==2539)
F.coverageFilters={};F.tab='census';F.censusMode='coverage';F.coveragePage=2;F.Render();assert(F.coveragePage==2)
local count=frameCount;for i=1,10 do F.Render()end;assert(frameCount==count,'Coverage browsing leaked frames')
print('PASS: ATDART exact fractions, random ties, stable saved targets, old snapshots, complete instances, profession blindspots, scan uncertainty, localization and coverage navigation/paging')
''')

lua.execute(r'''
-- Gathering expansion ownership can be read without opening a crafting window.
local gatherer={professions={[182]={name='Herbalism',expansions={}}}}
C_TradeSkillUI.GetProfessionInfoBySkillLineID=function(id)
 if id==2912 then return {professionID=id,parentProfessionID=182,professionName='Midnight Herbalism',skillLevel=30,maxSkillLevel=100}end
 if id==2556 then return {professionID=id,parentProfessionID=182,professionName='Classic Herbalism',skillLevel=0,maxSkillLevel=300}end
 if id==2555 then return {professionID=id,parentProfessionID=182,professionName='Outland Herbalism',skillLevel=0,maxSkillLevel=0}end
end
F.ScanProfessionCoverage(gatherer)
assert(gatherer.professions[182].expansions[2912].rank==30 and gatherer.professions[182].expansionChecks[2556])
assert(not gatherer.professions[182].expansionChecks[2555],'An unavailable 0/0 API read was marked scanned')
C_TradeSkillUI.GetProfessionInfoBySkillLineID=function()return nil end
F.ScanProfessionCoverage(gatherer);assert(gatherer.professions[182].expansions[2912].rank==30)
local c=F.db.characters['Player-1'];UnitGUID=function()return 'Player-1' end
C_TradeSkillUI.GetChildProfessionInfos=function()return {}end
C_TradeSkillUI.GetChildProfessionInfo=function()return {professionID=2539,professionName='Outland Tailoring',skillLevel=0,maxSkillLevel=0}end
F.DiscoverProfession();assert(c.professions[197].expansions[2539].rank==75,'A temporary 0/0 profession window overwrote a trained rank')
print('PASS: gathering expansion ownership, explicit unlearned checks and unavailable API preservation')
''')
lua.execute(r'''
-- Resume notes survive snapshots, reloads and switching to an offline alt.
F.selected='Player-1';local c=F.db.characters[F.selected];local general=c.notes.general
assert(F.SaveResume(F.selected,'Continue the Outland recipe hunt'))
local updated=c.resumeUpdatedAt;NOW=NOW+60
F.SaveResume(F.selected,'Continue the Outland recipe hunt');assert(c.resumeUpdatedAt==updated)
F.Snapshot(true);assert(c.notes.resume=='Continue the Outland recipe hunt' and c.notes.general==general)
F.tab='sheet';F.Render()
local clicked=false
for _,b in ipairs(frames)do
 if b.kind=='Button' and b:IsShown() and b:GetText()=='Edit next step' then b:GetScript('OnClick')();clicked=true;break end
end
assert(clicked and F.tab=='notes' and F.notePanel.section=='resume')
F.notePanel.edit:SetText('One small next step');assert(c.notes.resume=='One small next step')
F.selected='Alt1';F.Render();F.notePanel.edit:SetText('Pick up supplies')
assert(F.db.characters.Alt1.notes.resume=='Pick up supplies' and c.notes.resume=='One small next step')
F.filters={class='PRIEST',profession='Tailoring',expansion=2539,sort='rested',search='Void',junk={}};F.flatRoster=true
assert(F.SaveRosterView('  Cloth crafters  ') and not F.SaveRosterView('   '))
F.filters.class='MAGE';assert(F.db.settings.rosterViews['Cloth crafters'].filters.class=='PRIEST')
DuckMooFolioDB=F.Clean(F.db);F.Init();assert(F.db.characters['Player-1'].notes.resume=='One small next step')
assert(F.ApplyRosterView('Cloth crafters') and F.filters.class=='PRIEST' and F.filters.expansion==2539 and F.flatRoster and F.page==1 and not F.filters.junk)
F.filters.search='Changed';assert(F.db.settings.rosterViews['Cloth crafters'].filters.search=='Void')
assert(not F.ApplyRosterView('Missing'))
F.tab='roster';F.Render();F.RosterViewEditor();F.viewEditor.edit:SetText('Second view');F.viewEditor.save:GetScript('OnClick')()
assert(F.db.settings.rosterViews['Second view'] and not F.viewEditor:IsShown())
F.RosterViewPicker(false);F.choice.rows[1]:GetScript('OnClick')();assert(F.filters.search=='Void')
F.RosterViewPicker(true);F.choice.rows[1]:GetScript('OnClick')();assert(not F.db.settings.rosterViews['Cloth crafters'] and F.db.settings.rosterViews['Second view'])
F.Render();local count=frameCount;for i=1,20 do F.Render()end;assert(frameCount==count,'Saved-view controls leaked frames')
print('PASS: resume editing, offline alt isolation, unchanged timestamps, snapshot/reload preservation, named filter copies, view editor/chooser/removal and frame reuse')
''')
lua.execute(r'''
local exported=F.ExportRoster();local guid=next(exported);local name=F.db.characters[guid].name
exported[guid].name='Altered copy';assert(F.db.characters[guid].name==name and not exported[guid].notes)
assert(F.Themes.plum and F.Themes.gunmetal and F.Themes.purple.bg[1]==.065)
assert(select('#',F.Model.Plain('Text|with bars'))==1 and select('#',F.Model.Display('|cffffffffText|r'))==1 and select('#',F.Model.RealmKey('Moon Guard'))==1)
local function luminance(color)
 local function channel(v)return v<=.04045 and v/12.92 or ((v+.055)/1.055)^2.4 end
 return .2126*channel(color[1])+.7152*channel(color[2])+.0722*channel(color[3])
end
local t=F.Themes.trans
for _,surface in ipairs({t.bg,t.panel,t.button,t.hover})do
 local a,b=luminance(t.text),luminance(surface);assert((math.max(a,b)+.05)/(math.min(a,b)+.05)>=4.5,'Trans Pride text contrast is insufficient')
end
print('PASS: optional read-only roster export and classic plum theme preservation')
''')
lua.execute(r'''
-- The complete redesign remains usable at supported window sizes, preserves
-- editing scope, and never strands a realm heading apart from its characters.
F.filters={};F.flatRoster=false;F.db.settings.collapsed={};F.selected='Player-1'
for _,size in ipairs({{940,560},{1040,740},{1320,900}})do
 F.frame:SetSize(size[1],size[2])
 for _,tab in ipairs({'sheet','notes','skills','reps','att','roster','census','settings'})do
  F.tab=tab;F.Render()
  assert(F.width+194<=size[1]-20 and F.viewportHeight+84<=size[2]-20,'Content exceeds the window')
  assert(F.sidebar:GetHeight()-96>423,'Character chooser overlaps navigation')
  assert(F.tabButtons[tab]._active,'Selected page lost its sidebar highlight')
 end
 F.tab='notes';F.Render()
 assert(F.notePanel.paper:GetWidth()==F.width-176 and F.notePanel.scroll:GetHeight()>=260)
 F.notePanel.edit:SetFocus();F.Render();assert(F.notePanel.edit:HasFocus(),'Rerender interrupted note entry')
 F.notePanel.edit:ClearFocus()
 for _,expanded in ipairs({false,true})do
  F.tab='roster';F.rosterFiltersOpen=expanded;F.page=1;F.Render()
  local seen={}
  for _,page in ipairs(F.rosterPages)do
   assert(#page<=F.rosterPageSize)
   for index,row in ipairs(page)do
    if row.header and not F.db.settings.collapsed[row.header]then
     assert(page[index+1] and not page[index+1].header,'Realm heading stranded on a page')
    elseif row.guid then
     assert(not seen[row.guid],'Character appeared twice in roster pagination');seen[row.guid]=true
    end
   end
  end
  local count=0;for _ in pairs(seen)do count=count+1 end
  assert(count==#F.filteredRoster,'Roster pagination omitted characters')
 end
end
F.tab='notes';F.noteSection='general';F.Render();F.PickCharacter()
local chosen=F.choice.options[1].id;F.choice.rows[1]:GetScript('OnClick')()
assert(F.tab=='notes' and F.selected==chosen and F.notePanel.guid==chosen,'Character chooser lost the notebook scope')
F.notePanel.edit:SetText('Offline editing stays with this character')
assert(F.db.characters[chosen].notes.general=='Offline editing stays with this character')
local expected={{91,206,250},{245,169,184},{255,255,255},{245,169,184},{91,206,250}}
for i,color in ipairs(expected)do for channel,value in ipairs(color)do assert(math.abs(F.TransFlag[i][channel]*255-value)<.00001,'Flag color changed')end end
F.db.settings.theme='purple';F.tab='sheet';F.Render()
local b=F.tabButtons.sheet;b:GetScript('OnEnter')(b);b:GetScript('OnLeave')(b)
assert(b._surfaceColor[1]==F.Themes.purple.hover[1],'Hover removed the active-page highlight')
for _,tab in ipairs({'sheet','notes','skills','reps','att','roster','census','settings'})do F.tab=tab;F.Render()end
local count=frameCount
for i=1,3 do for _,tab in ipairs({'sheet','notes','skills','reps','att','roster','census','settings'})do F.tab=tab;F.Render()end end
assert(frameCount==count,'Redesigned pages leaked native frames')
print('PASS: supported window sizes, all sidebar pages, uninterrupted note entry, offline character switching, complete realm pagination, exact flag colors and frame reuse')
''')
lua.execute(r'''
local function lum(c)
 local function ch(v)return v<=.04045 and v/12.92 or ((v+.055)/1.055)^2.4 end
 return .2126*ch(c[1])+.7152*ch(c[2])+.0722*ch(c[3])
end
for _,key in ipairs({'trans','translight','light','plum'})do
 local t=F.Themes[key]
 for _,surface in ipairs({t.bg,t.sidebar,t.panel,t.button,t.hover})do
  for _,foreground in ipairs({t.text,t.muted})do
   local a,b=lum(surface),lum(foreground)
   assert((math.max(a,b)+.05)/(math.min(a,b)+.05)>=4.5,key..' has unreadable text')
  end
 end
 F.db.settings.theme=key;F.tab='notes';F.Render()
 assert(F.notePanel.paper._surfaceColor[1]==t.panel[1],'Notebook ignored its selected preset')
end
assert(F.Themes.trans.bg[1]==91/255 and F.Themes.trans.panel[1]==245/255)
assert(F.Themes.translight.text[1]==1 and F.Themes.translight.name=='Trans pride - dusk')
assert(F.Themes.plum.bg[1]~=F.Themes.purple.bg[1],'Plum still duplicates Purple')
print('PASS: revised palette contrast for primary/secondary text, saved preset keys and notebook theme application')
''')
lua.execute(r'''
for _,view in ipairs({'sheet','notes','skills','reps','att','roster','census','settings'})do F.tab=view;F.Render();assert(F.frame.topLevel and F.frame.flattenLayers)end
local count=0
for _,f in ipairs(frames)do
 if f.parent==UIParent and f._round then assert(f.topLevel and f.flattenLayers,'Standalone window lost grouped stacking');count=count+1 end
end
assert(count>=4,'Window stacking was not checked on dialogs')
print('PASS: main and dialog window render groups survive page and mode changes')
''')
print('All tests passed. Actual Retail client verification is still required.')

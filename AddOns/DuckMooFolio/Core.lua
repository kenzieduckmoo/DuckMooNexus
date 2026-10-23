local addon,F=...
DuckMooFolio=F
F.name=addon;F.version='0.5.2';F.Model=F.Model or {}
local M=F.Model
function F.Safe(fn,...)
    if type(fn)~='function' then return nil end
    local function pack(...) return {n=select('#',...),...} end
    local results=pack(pcall(fn,...))
    if not results[1] then return nil end
    for i=2,results.n do if issecretvalue and issecretvalue(results[i]) then results[i]=nil end end
    return unpack(results,2,results.n)
end
local S=F.Safe
function F.Clean(value,depth)
    if issecretvalue and issecretvalue(value) then return nil end
    local kind=type(value)
    if kind=='number' or kind=='string' or kind=='boolean' then return value end
    if kind=='table' and (depth or 0)<8 then
        local out={}
        for k,v in pairs(value) do
            if not (issecretvalue and issecretvalue(k)) and (type(k)=='string' or type(k)=='number') then out[k]=F.Clean(v,(depth or 0)+1) end
        end
        return out
    end
end
function F.Now() return S(GetServerTime) or time() end
function F.ExportRoster()
    local out={}
    for guid,c in pairs(F.db and F.db.characters or {})do
        out[guid]=F.Clean({name=c.name,realm=c.realm,class=c.class,className=c.className,lastSeen=c.lastSeen})
    end
    return out
end
function F.Print(message) print('|cffbf8beaDuckMoo Folio:|r '..message) end
function F.Init()
    DuckMooFolioDB=DuckMooFolioDB or {}
    F.db=DuckMooFolioDB;local db=F.db
    db.version=1;db.characters=db.characters or {};db.settings=db.settings or {};db.settings.collapsed=db.settings.collapsed or {};db.settings.realmRegions=db.settings.realmRegions or {}
    db.settings.rosterViews=db.settings.rosterViews or {}
    db.settings.sections=db.settings.sections or {};db.settings.theme=db.settings.theme or 'purple';db.settings.backgroundAlpha=tonumber(db.settings.backgroundAlpha) or .92
    for _,c in pairs(db.characters) do
        c.notes=c.notes or {};c.tags=c.tags or {};c.reputations=c.reputations or {};c.professions=c.professions or {};c.professions[794]=nil
        local region=c.region or (c.realmRegion=='Europe' and 3 or c.realmRegion=='Korea' and 2 or c.realmRegion=='Taiwan' and 4 or 1)
        c.region=region;c.realmRegion=M.RealmRegion(c.realm,region)
    end
    F.filters={};F.tab='sheet';F.page=1
end
-- Store only supported filter values; drafts and saved views never share tables.
local viewKeys={class=true,role=true,faction=true,region=true,profession=true,expansion=true,reputation=true,tag=true,sort=true,realm=true,search=true}
local function viewFilters(source)
    local out={}
    for key in pairs(viewKeys) do
        local value=source and source[key]
        if type(value)=='string' or type(value)=='number' then out[key]=value end
    end
    return out
end
function F.SaveRosterView(name)
    if type(name)~='string' then return false end
    name=name:match('^%s*(.-)%s*$')
    if name=='' or #name>60 then return false end
    F.db.settings.rosterViews[name]={filters=viewFilters(F.filters),flat=not not F.flatRoster}
    return true
end
function F.ApplyRosterView(name)
    local view=F.db.settings.rosterViews[name]
    if type(view)~='table' then return false end
    F.filters=viewFilters(view.filters);F.flatRoster=not not view.flat;F.page=1
    if F.rosterSearch then F.rosterSearch:ClearFocus();F.rosterSearch:SetText(F.filters.search or '') end
    return true
end
function F.SaveResume(guid,text)
    local c=F.db.characters[guid]
    if not c or type(text)~='string' then return false end
    c.notes=c.notes or {}
    if c.notes.resume~=text then c.notes.resume=text;c.resumeUpdatedAt=F.Now() end
    return true
end
function F.Current()
    local guid=S(UnitGUID,'player');if not guid or not F.db then return nil end
    local c=F.db.characters[guid]
    if not c then c={professions={},reputations={},notes={},tags={}};F.db.characters[guid]=c end
    c.notes=c.notes or {};c.tags=c.tags or {};c.professions=c.professions or {};c.reputations=c.reputations or {}
    F.current=guid;return c
end
function F.Reputations(c)
    local api=C_Reputation
    if not api or not api.GetNumFactions then return end
    local collapsed={};local index=1
    while index<=(S(api.GetNumFactions) or 0) and index<2000 do
        local r=S(api.GetFactionDataByIndex,index)
        if r then
            if r.isHeader and r.isCollapsed then
                collapsed[r.factionID or r.name]=true;S(api.ExpandFactionHeader,index)
            end
            if not r.isHeader or r.isHeaderWithRep then
                if r.factionID and r.name then
                    local row={name=r.name,reaction=r.reaction,value=r.currentStanding,min=r.currentReactionThreshold,max=r.nextReactionThreshold,accountWide=r.isAccountWide}
                    local renown=S(C_MajorFactions and C_MajorFactions.GetMajorFactionData,r.factionID)
                    if renown and renown.renownLevel then row.renown=renown.renownLevel;row.value=renown.renownReputationEarned;row.max=renown.renownLevelThreshold end
                    c.reputations[r.factionID]=F.Clean(row)
                end
            end
        end
        index=index+1
    end
    -- Collapse in reverse, preserving nested header state and the user's UI.
    for i=(S(api.GetNumFactions) or 0),1,-1 do
        local r=S(api.GetFactionDataByIndex,i)
        if r and collapsed[r.factionID or r.name] then S(api.CollapseFactionHeader,i) end
    end
    c.repSeenAt=F.Now()
end
function F.Professions(c)
    if type(GetProfessions)~='function' then return end
    local slots={GetProfessions()};local active={}
    for _,index in pairs(slots) do
        local name,icon,rank,max,_,_,id=S(GetProfessionInfo,index)
        if name and id and id~=794 then
            local p=c.professions[id] or {expansions={}}
            p.name=name;p.icon=icon;p.rank=rank;p.max=max;p.id=id;p.expansions=p.expansions or {};active[id]=p
        end
    end
    if next(active) then c.professions=active;c.profSeenAt=F.Now() end
end
function F.DiscoverProfession()
    local api=C_TradeSkillUI;local c=F.Current()
    if not c or not api or S(api.IsTradeSkillLinked) or S(api.IsTradeSkillGuild) then return end
    local base=S(api.GetBaseProfessionInfo);if not base or not base.professionID or base.professionID==794 then return end
    local p=c.professions[base.professionID] or {expansions={}}
    p.id=base.professionID;p.name=base.professionName or base.name or 'Profession';p.expansions=p.expansions or {};c.professions[p.id]=p
    local current=S(api.GetChildProfessionInfo)
    local children=S(api.GetChildProfessionInfos) or {}
    p.expansionChecks=p.expansionChecks or {}
    if current then children[#children+1]=current end
    for _,info in ipairs(children) do
        local usableRank=type(info.skillLevel)=='number' and (info.skillLevel>0 or type(info.maxSkillLevel)=='number' and info.maxSkillLevel>0)
        if info.professionID then
            F.RecordProfessionCatalog(p.id,info)
            if usableRank then
                p.expansionChecks[info.professionID]=F.Now()
                if info.skillLevel==0 and p.expansions[info.professionID]then p.expansions[info.professionID].rank=0 end
            end
        end
        if info.professionID and ((info.skillLevel or 0)>0 or current and info.professionID==current.professionID) then
            local row=p.expansions[info.professionID] or {};p.expansions[info.professionID]=row
            row.id=info.professionID;row.name=info.professionName or info.name or row.name or 'Expansion skill'
            if usableRank then row.rank=info.skillLevel end
            if info.maxSkillLevel and info.maxSkillLevel>0 then row.max=info.maxSkillLevel end
            row.seenAt=F.Now()
        end
    end
    if current and current.professionID and p.expansions[current.professionID] then
        local ids=S(api.GetAllRecipeIDs);local count=0
        if ids then
            for _,id in ipairs(ids) do local r=S(api.GetRecipeInfo,id);if r and r.learned then count=count+1 end end
            p.expansions[current.professionID].recipes=count
            p.expansions[current.professionID].recipesFiltered=true -- depends on profession UI filters
        end
    end
    if current and current.professionID and p.expansions[current.professionID] then
        local list=F.ProfessionKnowledge(current.professionID)
        if list then p.expansions[current.professionID].knowledge=list end
    end
    p.seenAt=F.Now();F.DrawIfShown()
end
function F.ReadTraitSelections(config)
    local api=C_Traits;local info=S(api and api.GetConfigInfo,config)
    if not info then return nil end
    local list={}
    for _,tree in ipairs(info.treeIDs or {}) do
        for _,node in ipairs(S(api.GetTreeNodes,tree) or {}) do
            local n=S(api.GetNodeInfo,config,node)
            if n and n.activeEntry and (n.activeRank or n.currentRank or 0)>0 then
                local e=S(api.GetEntryInfo,config,n.activeEntry.entryID)
                local d=e and S(api.GetDefinitionInfo,e.definitionID)
                local spell=d and S(C_Spell and C_Spell.GetSpellInfo,d.spellID)
                local name=d and (d.overrideName or spell and spell.name)
                if name then list[#list+1]={name=name,rank=n.activeRank or n.currentRank,max=n.maxRanks,spellID=d.spellID,nodeID=node} end
            end
        end
    end
    table.sort(list,function(a,b)return a.name<b.name end)
    return list,info.name
end
function F.Talents(c)
    local config=S(C_ClassTalents and C_ClassTalents.GetActiveConfigID)
    local list,name=F.ReadTraitSelections(config)
    if list then c.talents=list;c.loadout=name end
end
function F.ProfessionKnowledge(id)
    local config=S(C_ProfSpecs and C_ProfSpecs.GetConfigIDForSkillLine,id)
    if not config or config<=0 then return nil end
    return F.ReadTraitSelections(config)
end
function F.Snapshot(full,logout)
    if not logout and S(InCombatLockdown) then return end
    local c=F.Current();if not c then return end
    if logout then
        local zone,subzone=S(GetRealZoneText),S(GetSubZoneText)
        if zone and zone~='' then c.zone=zone end
        if subzone and subzone~='' then c.subzone=subzone end
        c.lastSeen=F.Now();c.loggedOut=true;return
    end
    local ready=S(UnitLevel,'player');if not ready or ready<=0 then return end
    -- A partial login/logout API read must not erase a good saved snapshot.
    local function put(key,v,positive)
        if v~=nil and not (positive and type(v)=='number' and v<=0) then c[key]=F.Clean(v) end
    end
    put('name',S(UnitName,'player'));put('realm',S(GetNormalizedRealmName) or S(GetRealmName))
    local cn,ct,ci=S(UnitClass,'player');put('className',cn);put('class',ct);put('classID',ci)
    local rn,rt=S(UnitRace,'player');put('race',rn);put('raceToken',rt)
    put('faction',S(UnitFactionGroup,'player'));put('sex',S(UnitSex,'player'));put('level',S(UnitLevel,'player'),true)
    put('maxLevel',S(GetMaxLevelForPlayerExpansion) or S(GetMaxPlayerLevel),true)
    put('xp',S(UnitXP,'player'));put('xpMax',S(UnitXPMax,'player'),true)
    if GetXPExhaustion then put('rested',S(GetXPExhaustion) or 0) end
    local guild,rank=S(GetGuildInfo,'player');if guild then put('guild',guild);put('guildRank',rank) end
    put('region',S(GetCurrentRegion));c.realmRegion=M.RealmRegion(c.realm,c.region or 1)
    local api=C_SpecializationInfo
    local spec=S(api and api.GetSpecialization or GetSpecialization)
    if spec then
        local id,name,_,icon,role=S(api and api.GetSpecializationInfo or GetSpecializationInfo,spec)
        put('specID',id,true);put('specName',name);put('specIcon',icon);put('role',role)
    end
    if (c.level or 0)>=81 then
        local hero=S(C_ClassTalents and C_ClassTalents.GetActiveHeroTalentSpec)
        local config=S(C_ClassTalents and C_ClassTalents.GetActiveConfigID)
        local info=hero and S(C_Traits and C_Traits.GetSubTreeInfo,config,hero)
        if info and info.name then put('heroSpec',info.name) end
    else c.heroSpec=nil end
    local avg,equipped=S(GetAverageItemLevel);put('avgIlvl',avg,true);put('ilvl',equipped,true)
    put('bind',S(GetBindLocation));put('zone',S(GetRealZoneText));put('subzone',S(GetSubZoneText))
    put('mapID',S(C_Map and C_Map.GetBestMapForUnit,'player'))
    c.lastSeen=F.Now();c.loggedOut=logout==true
    local title=S(GetCurrentTitle)
    if title then c.title=title>0 and S(GetTitleName,title) or nil end
    put('health',S(UnitHealthMax,'player'),true);put('power',S(UnitPowerMax,'player'),true);put('powerType',select(2,S(UnitPowerType,'player')))
    local stats=c.stats or {}
    local function stat(key,v) if v~=nil then stats[key]=F.Clean(v) end end
    stat('strength',select(2,S(UnitStat,'player',1)));stat('agility',select(2,S(UnitStat,'player',2)))
    stat('stamina',select(2,S(UnitStat,'player',3)));stat('intellect',select(2,S(UnitStat,'player',4)))
    stat('armor',select(2,S(UnitArmor,'player')));stat('crit',S(GetCritChance));stat('haste',S(GetHaste));stat('mastery',S(GetMasteryEffect))
    local speedRating=Enum and Enum.CombatRating and Enum.CombatRating.Speed or CR_SPEED
    if speedRating then stat('speedRating',S(GetCombatRating,speedRating));stat('speedBonus',S(GetCombatRatingBonus,speedRating))end
    local current,run=S(GetUnitSpeed,'player');stat('movement',run and run>0 and run/7*100 or nil);stat('moving',current and current/7*100 or nil)
    c.stats=stats
    if full and not logout then
        F.Professions(c);F.ScanProfessionCoverage(c);F.Reputations(c);F.Talents(c)
        if type(GetNumTitles)=='function' then
            local titles={};for i=1,(S(GetNumTitles) or 0) do if S(IsTitleKnown,i) then titles[#titles+1]=S(GetTitleName,i) end end
            if #titles>0 then c.titles=titles end
        end
        c.collections=c.collections or {}
        local mounts=S(C_MountJournal and C_MountJournal.GetMountIDs)
        if mounts and #mounts>0 then
            local owned=0;for _,id in ipairs(mounts) do local _,_,_,_,_,_,_,_,_,_,collected=S(C_MountJournal.GetMountInfoByID,id);if collected then owned=owned+1 end end
            if owned>0 then c.collections.mounts=owned end
        end
        local pets=select(2,S(C_PetJournal and C_PetJournal.GetNumPets));if pets then c.collections.pets=pets end
        local points=S(GetTotalAchievementPoints);if points then c.collections.achievementPoints=points end
    end
    -- Keep the same character object so editors and profession scans stay linked.
    for k,v in pairs(c) do c[k]=F.Clean(v) end
    F.DrawIfShown()
end
function F.DrawIfShown() if F.frame and F.frame:IsShown() and not F.rendering then F.Render() end end
local events=CreateFrame('Frame')
events:RegisterEvent('ADDON_LOADED');events:RegisterEvent('PLAYER_LOGIN');events:RegisterEvent('PLAYER_LOGOUT')
for _,event in ipairs({'PLAYER_ENTERING_WORLD','PLAYER_GUILD_UPDATE','KNOWN_TITLES_UPDATE','UNIT_NAME_UPDATE','PLAYER_LEVEL_UP','PLAYER_XP_UPDATE','UPDATE_EXHAUSTION','PLAYER_EQUIPMENT_CHANGED','PLAYER_SPECIALIZATION_CHANGED','PLAYER_TALENT_UPDATE','TRAIT_CONFIG_UPDATED','UPDATE_FACTION','SKILL_LINES_CHANGED','TRADE_SKILL_SHOW','TRADE_SKILL_LIST_UPDATE','TRADE_SKILL_DATA_SOURCE_CHANGED','HEARTHSTONE_BOUND','ZONE_CHANGED_NEW_AREA','PLAYER_REGEN_ENABLED'}) do pcall(events.RegisterEvent,events,event) end
function F.Queue(full,profession)
    F.needFull=F.needFull or full;F.needProfession=F.needProfession or profession
    if F.pending then return end;F.pending=true
    C_Timer.After(.5,function()
        F.pending=false;local a,b=F.needFull,F.needProfession;F.needFull=nil;F.needProfession=nil
        F.Snapshot(a);if b then F.DiscoverProfession() end
    end)
end
events:SetScript('OnEvent',function(_,event,arg)
    if event=='ADDON_LOADED' then if arg==addon then F.Init() end;return end
    if not F.db then return end
    if event=='PLAYER_LOGOUT' then F.Snapshot(true,true);return end
    if event=='PLAYER_LOGIN' then F.UpdateProfessionCatalog();F.Snapshot(true);F.CreateMinimap();C_Timer.After(2,function()F.Snapshot(true)end);return end
    local profession=event:find('TRADE_SKILL',1,true)~=nil
    local full=event=='UPDATE_FACTION' or event=='SKILL_LINES_CHANGED' or event=='PLAYER_ENTERING_WORLD' or event=='PLAYER_TALENT_UPDATE' or event=='TRAIT_CONFIG_UPDATED' or event=='PLAYER_REGEN_ENABLED'
    F.Queue(full,profession or event=='TRAIT_CONFIG_UPDATED')
end)
F.events=events
SLASH_DUCKMOOFOLIO1='/folio';SLASH_DUCKMOOFOLIO2='/dmfolio'
SlashCmdList.DUCKMOOFOLIO=function(cmd)
    cmd=(cmd or ''):lower():match('^%s*(.-)%s*$')
    if cmd=='scan' then F.Snapshot(true);F.DiscoverProfession();F.Print('Current character refreshed. Open each profession for expansion details.')
    elseif cmd=='minimap' then F.db.settings.hideMinimap=not F.db.settings.hideMinimap;F.CreateMinimap()
    else F.Show(cmd=='roster' and 'roster' or 'sheet') end
end

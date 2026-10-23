local _,O=...
local function api(root,key) return root and root[key] end
local function read(root,key,...) return O.Call(api(root,key),...) end
function O.Profile()
    local class,classFile,classID=O.Call(UnitClass,"player")
    local race,raceFile,raceID=O.Call(UnitRace,"player")
    local spec=O.Call(GetSpecialization)
    local specID,specName=O.Call(GetSpecializationInfo,spec)
    local avg,ilvl=O.Call(GetAverageItemLevel)
    local map=read(C_Map,"GetBestMapForUnit","player")
    local _,build,_,interface=O.Call(GetBuildInfo)
    return {name=O.Call(UnitName,"player"),realm=O.Call(GetRealmName),class=classFile,className=class,classID=classID,
        race=race,raceFile=raceFile,raceID=raceID,level=O.Call(UnitLevel,"player"),faction=O.Call(UnitFactionGroup,"player"),
        specID=specID,specName=specName,ilvl=ilvl,avgIlvl=avg,money=O.Call(GetMoney),zone=O.Call(GetRealZoneText),
        subzone=O.Call(GetSubZoneText),mapID=map,bind=O.Call(GetBindLocation),guild=O.Call(GetGuildInfo,"player"),
        xp=O.Call(UnitXP,"player"),xpMax=O.Call(UnitXPMax,"player"),rested=O.Call(GetXPExhaustion),
        health=O.Call(UnitHealthMax,"player"),build=build,interface=interface,projectID=WOW_PROJECT_ID,
        locale=O.Call(GetLocale),region=O.Call(GetCurrentRegion),lastSeen=GetServerTime()}
end
function O.Currencies()
    if not api(C_CurrencyInfo,"GetCurrencyListSize") then return nil,"unavailable","Currency API unavailable" end
    local rows,ids={},{}
    local c=O.Character()
    for id in pairs(c.sections.currencies and c.sections.currencies.data or {}) do ids[id]=true end
    for id in pairs(O.currencyIDs or {}) do ids[id]=true end
    local size=read(C_CurrencyInfo,"GetCurrencyListSize")
    if not size then return nil,"unavailable","Currency list not ready" end
    for i=1,math.min(size,3000) do
        local info=read(C_CurrencyInfo,"GetCurrencyListInfo",i)
        if info and not info.isHeader and info.currencyID then ids[info.currencyID]=true end
    end
    for id in pairs(ids) do
        local info=read(C_CurrencyInfo,"GetCurrencyInfo",id)
        if info and info.name then rows[id]=info end
    end
    if not next(rows) then return nil,"unavailable","No readable currencies returned; prior observation retained" end
    return rows,"partial","Visible list, previously observed IDs and currency events; collapsed/undiscovered currencies may be absent"
end
function O.Vault()
    local activities=read(C_WeeklyRewards,"GetActivities")
    if not activities or not next(activities) then return nil,"unavailable","Vault API unavailable, ineligible or not ready" end
    local tracks={}
    local types=Enum and Enum.WeeklyRewardChestThresholdType or {}
    for _,slot in ipairs(activities) do
        local key=slot.type==types.Raid and "raids" or slot.type==types.World and "world" or slot.type==types.Activities and "mythicPlus" or "other"
        tracks[key]=tracks[key] or {}
        local link=read(C_WeeklyRewards,"GetExampleRewardItemHyperlinks",slot.id)
        if link then slot.itemLevel=read(C_Item,"GetDetailedItemLevelInfo",link) end
        tracks[key][#tracks[key]+1]=slot
    end
    local reset=read(C_DateAndTime,"GetSecondsUntilWeeklyReset")
    return {tracks=tracks,weeklyResetTime=reset and GetServerTime()+reset,hasAvailableRewards=read(C_WeeklyRewards,"HasAvailableRewards")},"captured"
end
function O.Lockouts()
    if type(GetNumSavedInstances)~="function" then return nil,"unavailable","Saved-instance API unavailable" end
    local rows={}
    for i=1,math.min(O.Call(GetNumSavedInstances) or 0,300) do
        local ok,name,id,reset,difficulty,locked,extended,_,isRaid,maxPlayers,difficultyName,numEncounters,progress=pcall(GetSavedInstanceInfo,i)
        if ok then
            local row=O.Safe({name=name,id=id,reset=reset,difficulty=difficulty,locked=locked,extended=extended,isRaid=isRaid,maxPlayers=maxPlayers,difficultyName=difficultyName,numEncounters=numEncounters,encounterProgress=progress})
            if row then
                row.resetAt=row.reset and row.reset>0 and GetServerTime()+row.reset or nil;row.encounters={}
                for boss=1,math.min(row.numEncounters or 0,100) do
                    local bossName,_,killed=O.Call(GetSavedInstanceEncounterInfo,i,boss)
                    row.encounters[#row.encounters+1]={name=bossName,killed=killed}
                end
                rows[#rows+1]=row
            end
        end
    end
    return rows,"captured"
end
function O.Keystone()
    if not api(C_MythicPlus,"GetOwnedKeystoneLevel") then return nil,"unavailable","Keystone API unavailable" end
    local level=read(C_MythicPlus,"GetOwnedKeystoneLevel")
    local id=read(C_MythicPlus,"GetOwnedKeystoneChallengeMapID")
    if level==nil then return nil,"unavailable","Owned key not returned" end
    return {level=level,mapID=id,name=id and read(C_ChallengeMode,"GetMapUIInfo",id)},"captured"
end
function O.Equipment()
    local rows={}
    for slot=1,19 do rows[slot]={itemID=O.Call(GetInventoryItemID,"player",slot),link=O.Call(GetInventoryItemLink,"player",slot),texture=O.Call(GetInventoryItemTexture,"player",slot)} end
    return rows,"captured"
end
function O.Quests()
    local ids=read(C_QuestLog,"GetAllCompletedQuestIDs")
    if not ids then return nil,"unavailable","Completed quest list not ready" end
    return ids,"captured","Completed IDs; completion names/times come from observed quest events or API profiles"
end
function O.Knowledge()
    local info=read(C_TradeSkillUI,"GetProfessionChildSkillLineID")
    if not info or info==0 then return nil,"unavailable","Open a profession naturally to capture its knowledge; last observation is retained" end
    local config=read(C_ProfSpecs,"GetConfigIDForSkillLine",info)
    local tabs=read(C_ProfSpecs,"GetSpecTabIDsForSkillLine",info)
    if not config or not tabs then return nil,"unavailable","Specialization data not available for this profession" end
    local result={skillLineID=info,profession=read(C_TradeSkillUI,"GetProfessionInfoBySkillLineID",info),tabs={}}
    for _,id in ipairs(tabs) do
        local tab=read(C_ProfSpecs,"GetTabInfo",id) or {}
        tab.tabID=id;tab.spendCurrency=tab.rootNodeID and read(C_ProfSpecs,"GetSpendCurrencyForPath",tab.rootNodeID)
        tab.currencies=read(C_Traits,"GetTreeCurrencyInfo",config,id,false);tab.nodes={}
        local nodes=read(C_Traits,"GetTreeNodes",id) or {}
        for index,node in ipairs(nodes) do
            if index>500 then result.limited=true;break end
            tab.nodes[node]=read(C_Traits,"GetNodeInfo",config,node)
        end
        result.tabs[id]=tab
    end
    local c=O.Character();local all=c.sections.knowledge and c.sections.knowledge.data or {}
    all[info]={observedAt=GetServerTime(),data=result}
    return all,"partial","Only profession specializations opened by this character; no automatic UI opening"
end
function O.Scan(reason,only)
    if not O.Character() then return end
    if O.Call(InCombatLockdown) then O.pending=true;return end
    local handlers={profile=O.Profile,currencies=O.Currencies,vault=O.Vault,lockouts=O.Lockouts,keystone=O.Keystone,equipment=O.Equipment,quests=O.Quests,knowledge=O.Knowledge}
    for key,fn in pairs(handlers) do
        if not only or only[key] then
            O.readLimited=false
            local ok,body,status,detail=pcall(fn)
            if O.readLimited then status="partial" end
            O.Store(key,ok and body or nil,ok and (status or "captured") or "unavailable",ok and detail or "API read failed; previous observation retained")
        end
    end
    O.db.lastCapture=GetServerTime();O.db.version=O.version
end

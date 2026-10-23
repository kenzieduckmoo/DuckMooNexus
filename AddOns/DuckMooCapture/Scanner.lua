local _, NS = ...
local M, call = NS.Model, NS.Call
local jobs, active, token = {}, nil, 0
local CAP, QUERY_LIMIT = 256, 24000
local BATCH, SLICE_MS = 8, 4
local CACHE_VERSION=1
local function encode(value)
    if type(value)~="table" then return tostring(value) end
    local keys={};for k in pairs(value) do keys[#keys+1]=k end
    table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
    local parts={};for _,k in ipairs(keys) do parts[#parts+1]=tostring(k).."="..encode(value[k]) end
    return "{"..table.concat(parts,";").."}"
end
local function fingerprint(operation)
    if not operation then return nil end
    return encode(M.Copy({baseSkill=operation.baseSkill,bonusSkill=operation.bonusSkill,
        baseDifficulty=operation.baseDifficulty,bonusDifficulty=operation.bonusDifficulty,
        concentrationCost=operation.concentrationCost,bonusStats=operation.bonusStats}))
end
local function contextStamp(id)
    local info=call(C_TradeSkillUI.GetChildProfessionInfo)
    if not info then return nil end
    local _,build=GetBuildInfo()
    local traits={}
    if C_ProfSpecs and C_ProfSpecs.GetConfigIDForSkillLine then
        local config=call(C_ProfSpecs.GetConfigIDForSkillLine,id)
        if config==nil then return nil end
        if config>0 then
            local api=C_Traits;local tree=api and call(api.GetConfigInfo,config)
            if not tree then return nil end
            for _,treeID in ipairs(tree.treeIDs or {}) do
                local nodes=call(api.GetTreeNodes,treeID);if not nodes then return nil end
                for _,nodeID in ipairs(nodes) do
                    local node=call(api.GetNodeInfo,config,nodeID);if not node then return nil end
                    traits[tostring(nodeID)]={rank=node.activeRank or node.currentRank or 0,entry=node.activeEntry and node.activeEntry.entryID}
                end
            end
        end
    end
    local ids=M.Copy(call(C_TradeSkillUI.GetAllRecipeIDs))
    if not ids or #ids==0 then return nil end
    table.sort(ids)
    return encode({version=CACHE_VERSION,build=build,profession=M.Copy(info),traits=traits,recipes=ids})
end
local function invalidate(c,id)
    for _,scan in pairs(c.scannedRecipes or {}) do
        if scan.profession and scan.profession.professionID==id then scan.invalidatedAt=GetServerTime() end
    end
    for _,operation in pairs(c.operations or {}) do
        if operation.skillLineID==id then operation.invalidatedAt=GetServerTime() end
    end
end
local function checkpoint(job, complete)
    local current=job.current
    if not current or not next(current.outcomes) then return end
    local c=NS.Character();if not c then return end
    c.scannedRecipes=c.scannedRecipes or {}
    -- A partial replacement stays in the persistent cursor; keep the complete
    -- prior observation until a complete replacement is ready.
    local previous=c.scannedRecipes[current.info.recipeID]
    if not complete and previous and not previous.partial then return end
    c.scannedRecipes[current.info.recipeID]={info=M.Copy(current.info),schematic=M.Copy(current.schematic),profession=M.Copy(current.profession),
        observedAt=GetServerTime(),outcomes=current.outcomes,combinations=math.min(#current.combinations,current.index-1),totalCombinations=current.total,
        partial=not complete,limited=not complete or current.total>#current.combinations,unavailable=current.unavailable}
end

local function context()
    if InCombatLockdown() or not NS.OwnProfession() or not ProfessionsFrame or not ProfessionsFrame:IsShown() then return nil end
    local page=ProfessionsFrame.CraftingPage
    if not page or not page:IsShown() then return nil end
    local profession=call(C_TradeSkillUI.GetChildProfessionInfo)
    return profession and type(profession.professionID)=="number" and profession.professionID>0 and profession.professionID or nil
end
local function status(job, state)
    job.saved.state,job.saved.observedAt=state,GetServerTime()
    if NS.ScannerLabel then
        local now=GetTime and GetTime() or GetServerTime()
        if job.labelState==state and job.labelAt and now-job.labelAt<0.2 then return end
        job.labelState,job.labelAt=state,now
        local progress=job.current and (" - "..(job.current.info.name or "Recipe").." "..math.min(job.current.index,#job.current.combinations).."/"..#job.current.combinations.." mixes") or ""
        NS.ScannerLabel:SetText("Crafting Desk: "..state.." - "..job.saved.checked.."/"..job.saved.total.." recipes; "..job.saved.outcomes.." outcomes"..progress)
    end
end
function NS.StopScanner(reason)
    token=token+1
    if active then active.checking=false;checkpoint(active,false);status(active,reason or "Paused");active=nil end
end

local function query(job)
    local current=job.current
    local allocations=current.combinations[current.index]
    local modified={}
    for _,a in ipairs(allocations) do
        if a.dataSlotType==Enum.TradeskillSlotDataType.ModifiedReagent then
            modified[#modified+1]={reagent=M.Copy(a.reagent),quantity=a.quantity,dataSlotIndex=a.dataSlotIndex}
        end
    end
    local apply=current.apply
    local operation=call(C_TradeSkillUI.GetCraftingOperationInfo,current.info.recipeID,modified,nil,apply)
    job.saved.queries=job.saved.queries+1
    if not apply and operation then
        job.probes=job.probes or {}
        local key=tostring(current.info.recipeID)
        if not job.probes[key] then job.probes[key]={recipeID=current.info.recipeID,modified=M.Copy(modified),fingerprint=fingerprint(operation)} end
        job.probe=job.probe or job.probes[key]
    end
    if operation and operation.recipeID and operation.recipeID~=current.info.recipeID then operation=nil end
    local qualityID=operation and (operation.craftingQualityID or (current.info.qualityIDs or {})[operation.craftingQuality])
    local output=operation and call(C_TradeSkillUI.GetRecipeOutputItemData,current.info.recipeID,modified,nil,qualityID)
    local zero=apply and operation and operation.concentrationCost==0
    if not zero and operation and output and output.itemID and (not operation.isQualityCraft or qualityID) and
        (not apply or type(operation.concentrationCost)=="number" and operation.concentrationCost>0) then
        local signature=M.ValidateReagents(current.schematic,allocations).signature
        current.outcomes[signature.."|"..tostring(apply)]={allocations=M.Copy(allocations),operation=M.Copy(operation),output=M.Copy(output),applyConcentration=apply,observedAt=GetServerTime()}
        job.saved.outcomes=job.saved.outcomes+1
    elseif not zero then
        current.unavailable=current.unavailable+1;job.saved.unavailable=job.saved.unavailable+1
    end
    if apply then current.index=current.index+1 end
    current.apply=not apply
    if current.index>#current.combinations then
        checkpoint(job,true)
        local c=NS.Character()
        c.scannedRecipes=c.scannedRecipes or {}
        local old=c.scannedRecipes[current.info.recipeID]
        if not next(current.outcomes) and old then old.lastAttemptAt=GetServerTime();old.lastAttemptUnavailable=true end
        job.saved.checked=job.saved.checked+1
        if current.total>#current.combinations then job.saved.limited=job.saved.limited+1 end
        job.current=nil
    end
end

function NS.StartScanner(force)
    local professionID=context()
    if not professionID then return end
    if active and active.professionID==professionID and not force then return end
    NS.StopScanner("Paused")
    local c=NS.Character();if not c then return end
    c.scannerCache=c.scannerCache or {}
    local job=jobs[professionID]
    if not job then
        local cached=c.scannerCache[professionID]
        if cached and cached.cacheVersion==CACHE_VERSION then
            job=cached;job.needsCheck=true;job.checking=false;jobs[professionID]=job
            c.scanStatus=c.scanStatus or {};c.scanStatus[professionID]=job.saved
        end
    end
    local stamp=contextStamp(professionID)
    if not stamp then if job then status(job,"Waiting: profession data");job.needsCheck=true end;return end
    local changed=job and job.stamp~=stamp
    if changed then force=true end
    if job and job.needsCheck and not force then
        local probes={};for _,probe in pairs(job.probes or {}) do probes[#probes+1]=probe end
        if #probes==0 then force=true else
            -- Validate every sampled recipe, in bounded work slices. A single
            -- recipe cannot establish specialization-dependent equivalence.
            local previousState=job.saved.state;local index=1
            active=job;job.checking=true;token=token+1;local mine=token
            local function check()
                if mine~=token then return end
                if context()~=professionID then NS.StopScanner("Paused: profession window closed");return end
                local started=debugprofilestop and debugprofilestop() or 0
                for work=1,BATCH do
                    local probe=probes[index]
                    if not probe then
                        job.needsCheck=false;job.checking=false;active=nil;job.saved.state=previousState
                        job.saved.cacheHits=(job.saved.cacheHits or 0)+1;NS.StartScanner();return
                    end
                    local op=call(C_TradeSkillUI.GetCraftingOperationInfo,probe.recipeID,probe.modified,nil,false)
                    job.saved.validationQueries=(job.saved.validationQueries or 0)+1
                    local fresh=fingerprint(op)
                    if not fresh then
                        job.checking=false;active=nil;job.needsCheck=true;status(job,"Waiting: crafting data");return
                    end
                    if fresh~=probe.fingerprint then
                        invalidate(c,professionID);job.checking=false;active=nil;NS.StartScanner(true);return
                    end
                    index=index+1
                    if debugprofilestop and debugprofilestop()-started>=SLICE_MS then break end
                end
                C_Timer.After(0.02,check)
            end
            status(job,"Checking cached results");C_Timer.After(0.02,check);return
        end
    end
    if force or not job then
        local ids=call(C_TradeSkillUI.GetAllRecipeIDs)
        if not ids or #ids==0 then return end
        if changed then invalidate(c,professionID) end
        c.scanStatus=c.scanStatus or {}
        local saved={total=#ids,checked=0,skipped=0,queries=0,outcomes=0,limited=0,unavailable=0,startedAt=GetServerTime(),combinationLimit=CAP,
            starts=((job and job.saved.starts) or 0)+1,resetReason=changed and "Profession, build, recipe list or specialization changed" or force and "Requested refresh" or "Initial capture"}
        c.scanStatus[professionID]=saved
        job={ids=ids,index=1,professionID=professionID,saved=saved,stamp=stamp,cacheVersion=CACHE_VERSION,probes={}}
        jobs[professionID]=job;c.scannerCache[professionID]=job
    end
    if job.saved.state=="Finished" or job.saved.state=="Scan limit reached" then return end
    active=job;token=token+1;local mine=token
    local function step()
        if mine~=token then return end
        if context()~=professionID then NS.StopScanner(InCombatLockdown() and "Paused: combat" or "Paused: open the Crafting tab to resume");return end
        if job.saved.queries>=QUERY_LIMIT then status(job,"Scan limit reached");active=nil;return end
        local started=debugprofilestop and debugprofilestop() or 0
        for work=1,BATCH do
        if active~=job or mine~=token then break end
        if job.saved.queries>=QUERY_LIMIT then status(job,"Scan limit reached");active=nil;break end
        local ok,err=pcall(function()
            if job.current then query(job) else
                local id=job.ids[job.index]
                if not id then status(job,"Finished");active=nil;return end
                job.index=job.index+1
                local info=call(C_TradeSkillUI.GetRecipeInfo,id)
                local profession=call(C_TradeSkillUI.GetProfessionInfoByRecipeID,id)
                local schematic=info and info.learned and profession and profession.professionID==professionID and call(C_TradeSkillUI.GetRecipeSchematic,id,false)
                if info then NS.RememberRecipe(info,schematic) end
                local combinations,total
                if schematic then combinations,total=NS.ReagentCombinations(schematic,CAP) end
                if combinations then
                    -- Finish the last recipe inside the session query budget,
                    -- storing it as limited rather than abandoning staged data.
                    local remaining=math.floor((QUERY_LIMIT-job.saved.queries)/2)
                    while #combinations>remaining do table.remove(combinations) end
                    job.current={info=info,profession=profession,schematic=schematic,combinations=combinations,total=total,index=1,apply=false,outcomes={},unavailable=0}
                else job.saved.checked=job.saved.checked+1;job.saved.skipped=job.saved.skipped+1 end
            end
        end)
        if not ok then
            checkpoint(job,false)
            job.saved.lastError=tostring(err)
            job.saved.unavailable=job.saved.unavailable+1
            job.saved.checked=job.saved.checked+1
            job.current=nil -- Skip one failed recipe, not the rest of the profession.
        end
        if debugprofilestop and debugprofilestop()-started>=SLICE_MS then break end
        end
        if active==job then checkpoint(job,false);status(job,"Scanning");C_Timer.After(0.02,step) end
    end
    status(job,"Scanning");C_Timer.After(0.02,step)
end

local frame=CreateFrame("Frame")
for _,event in ipairs({"TRADE_SKILL_SHOW","TRADE_SKILL_LIST_UPDATE","TRADE_SKILL_DATA_SOURCE_CHANGED","TRADE_SKILL_DATA_SOURCE_CHANGING","TRADE_SKILL_CLOSE","PLAYER_REGEN_DISABLED","PLAYER_REGEN_ENABLED","PLAYER_EQUIPMENT_CHANGED","UNIT_AURA","TRADE_SKILL_ITEM_CRAFTED_RESULT","NEW_RECIPE_LEARNED","SKILL_LINES_CHANGED","TRAIT_CONFIG_UPDATED"}) do frame:RegisterEvent(event) end
local refresh=0
function NS.ScannerEvent(_,event,unit)
    if event=="UNIT_AURA" and unit~="player" then return end
    if event=="TRADE_SKILL_CLOSE" or event=="TRADE_SKILL_DATA_SOURCE_CHANGING" or event=="PLAYER_REGEN_DISABLED" then NS.StopScanner(event=="PLAYER_REGEN_DISABLED" and "Paused: combat" or "Paused: profession window closed or changed");return end
    if event=="NEW_RECIPE_LEARNED" then
        NS.StopScanner("Checking newly learned recipes")
        C_Timer.After(0.5,function()NS.StartScanner(true)end);return
    end
    if event=="UNIT_AURA" or event=="PLAYER_EQUIPMENT_CHANGED" or event=="TRADE_SKILL_ITEM_CRAFTED_RESULT" or event=="SKILL_LINES_CHANGED" or event=="TRAIT_CONFIG_UPDATED" then
        for _,job in pairs(jobs) do job.needsCheck=true end
        NS.StopScanner("Checking for crafting changes")
        if refresh==1 then return end
        refresh=1
        C_Timer.After(0.5,function()refresh=0;NS.StartScanner()end)
        return
    end
    if ProfessionsFrame and not NS.ScannerLabel and ProfessionsFrame.CreateFontString then
        NS.ScannerLabel=ProfessionsFrame:CreateFontString(nil,"OVERLAY","GameFontNormalSmall")
        NS.ScannerLabel:SetPoint("BOTTOMLEFT",ProfessionsFrame,"TOPLEFT",10,4)
    end
    NS.StartScanner()
end
frame:SetScript("OnEvent",NS.ScannerEvent)
SLASH_DUCKMOOSCAN1="/dmcapscan"
SlashCmdList.DUCKMOOSCAN=function()NS.StartScanner(true)end

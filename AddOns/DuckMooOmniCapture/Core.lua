local name,O=...
local frame=CreateFrame("Frame")
local scheduled=false
local dirty,full={},false
function O.Schedule(keys)
    if not keys then full=true else for key in string.gmatch(keys,"%S+") do dirty[key]=true end end
    if scheduled then return end
    scheduled=true
    C_Timer.After(3,function() local selected=not full and dirty or nil;scheduled=false;dirty={};full=false;O.Scan("change",selected) end)
end
local refresh={CURRENCY_DISPLAY_UPDATE=true,WEEKLY_REWARDS_UPDATE=true,WEEKLY_REWARDS_ITEM_CHANGED=true,UPDATE_INSTANCE_INFO=true,CHALLENGE_MODE_COMPLETED=true,CHALLENGE_MODE_MAPS_UPDATE=true,PLAYER_EQUIPMENT_CHANGED=true,TRADE_SKILL_SHOW=true,TRAIT_CONFIG_UPDATED=true,SKILL_LINES_CHANGED=true,PLAYER_MONEY=true,ZONE_CHANGED_NEW_AREA=true,PLAYER_SPECIALIZATION_CHANGED=true,PLAYER_REGEN_ENABLED=true,PLAYER_ENTERING_WORLD=true}
frame:SetScript("OnEvent",function(_,event,...)
    if event=="ADDON_LOADED" then
        if ...==name then O.Init() end
        return
    end
    if not O.db or O.blocked then return end
    if event=="PLAYER_LOGIN" then
        O.Event("session_start",O.Profile());O.Call(RequestRaidInfo);O.Call(C_MythicPlus and C_MythicPlus.RequestMapInfo);O.Call(C_WeeklyRewards and C_WeeklyRewards.OnUIInteract);O.Schedule()
    elseif event=="PLAYER_LOGOUT" then
        O.Event("session_end",O.Profile());O.Scan("logout")
    elseif event=="PLAYER_LEVEL_UP" then
        O.Event("level",{level=O.Safe((...))});O.Schedule("profile")
    elseif event=="QUEST_TURNED_IN" then
        local questID,xp,money=O.Safe((select(1,...))),O.Safe((select(2,...))),O.Safe((select(3,...)))
        O.Event("quest_completed",{questID=questID,name=O.Call(C_QuestLog and C_QuestLog.GetTitleForQuestID,questID),xp=xp,money=money});O.Schedule("profile quests")
    elseif event=="CHAT_MSG_LOOT" then
        local text,_,_,_,_,_,_,_,_,_,_,guid=...
        if O.Safe(guid)==O.Call(UnitGUID,"player") then O.Event("loot",{message=O.Safe(text)}) end
    elseif event=="ENCOUNTER_END" then
        local id,label,difficulty,size,success=...
        O.Event("encounter",{id=O.Safe(id),name=O.Safe(label),difficulty=O.Safe(difficulty),groupSize=O.Safe(size),success=O.Safe(success)})
        O.Schedule("profile vault lockouts keystone")
    elseif event=="PLAYER_DEAD" then O.Event("death",O.Profile())
    elseif event=="ACHIEVEMENT_EARNED" then
        O.Event("achievement",{id=O.Safe((...))})
    elseif refresh[event] then
        if event=="CURRENCY_DISPLAY_UPDATE" then
            local id=O.Safe((...));if type(id)=="number" and id>0 then O.currencyIDs=O.currencyIDs or {};O.currencyIDs[id]=true end
        end
        local sections={CURRENCY_DISPLAY_UPDATE="currencies",PLAYER_MONEY="profile",ZONE_CHANGED_NEW_AREA="profile",PLAYER_EQUIPMENT_CHANGED="profile equipment",PLAYER_SPECIALIZATION_CHANGED="profile",TRADE_SKILL_SHOW="knowledge",TRAIT_CONFIG_UPDATED="knowledge",SKILL_LINES_CHANGED="knowledge",WEEKLY_REWARDS_UPDATE="vault",WEEKLY_REWARDS_ITEM_CHANGED="vault",UPDATE_INSTANCE_INFO="lockouts",CHALLENGE_MODE_COMPLETED="vault lockouts keystone",CHALLENGE_MODE_MAPS_UPDATE="keystone"}
        if event=="PLAYER_REGEN_ENABLED" and not O.pending then return end
        O.pending=false
        O.Schedule(sections[event])
    end
end)
for _,event in ipairs({"ADDON_LOADED","PLAYER_LOGIN","PLAYER_LOGOUT","PLAYER_LEVEL_UP","QUEST_TURNED_IN","CHAT_MSG_LOOT","PLAYER_DEAD","ACHIEVEMENT_EARNED","ENCOUNTER_END"}) do pcall(frame.RegisterEvent,frame,event) end
for event in pairs(refresh) do pcall(frame.RegisterEvent,frame,event) end
SLASH_DUCKMOOOMNI1="/dmomni"
SlashCmdList.DUCKMOOOMNI=function(text)
    if not O.db then return end
    if text=="off" then O.db.settings.enabled=false
    elseif text=="on" then O.db.settings.enabled=true;O.Schedule()
    elseif text=="events off" then O.db.settings.events=false
    elseif text=="events on" then O.db.settings.events=true
    elseif text=="capture" then O.Scan("manual") end
    local c=O.Character()
    print("DuckMoo Omni Capture "..O.version..": "..(O.db.settings.enabled and "enabled" or "paused")..". Events retained: "..(c and #c.events or 0).."; overflow: "..(c and c.droppedEvents or 0)..". /dmomni on | off | capture | events on | events off")
end

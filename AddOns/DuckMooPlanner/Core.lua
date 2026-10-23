local addon, P = ...
DuckMooPlanner = P
P.name = addon
P.version = '0.5.2'
P.fullName = 'DuckMoo Services: Concentration Planner'
P.publisher = 'DuckMoo Media'
P.weekOffset = 0
P.view = 'daily'
P.filter = ''
P.followToday = true
local M = P.Model
function P.Print(s) print('|cffbf8fffDuckMoo Planner:|r '..s) end
function P.ExportRoster()
    local out={}
    for guid,c in pairs(P.db and P.db.characters or {})do
        out[guid]={name=c.name,realm=c.realm,class=c.class,className=c.className,lastSeen=c.lastSeen}
    end
    return out
end
local function safe(fn,...)
    if type(fn) ~= 'function' then return nil end
    local ok, result = pcall(fn,...)
    if ok then return result end
end
function P.Init()
    DuckMooPlannerDB = DuckMooPlannerDB or {}
    P.db = DuckMooPlannerDB
    P.db.schema = 3
    P.db.characters = P.db.characters or {}
    P.db.settings = P.db.settings or {login=true}
    local s=P.db.settings
    if s.login==nil then s.login=true end
    if s.includePrior==nil then s.includePrior=false end
    if s.compactAlpha==nil then s.compactAlpha=.65 end
    if s.fullAlpha==nil then s.fullAlpha=.85 end
    s.fullAlpha=math.max(.2,math.min(1,tonumber(s.fullAlpha) or .85))
    P.db.groups=P.db.groups or {}
    P.db.nextGroupID=P.db.nextGroupID or 1
    P.rosterPage=P.rosterPage or 1
    P.selectedCharacters=P.selectedCharacters or {}
    P.settingsTab=P.settingsTab or 'roster'
    s.compactAlpha=math.max(.2,math.min(1,tonumber(s.compactAlpha) or .65))
    s.fullPosition=s.fullPosition or s.position
    P.db.notes=P.db.notes or {}
    P.db.nextNoteID=P.db.nextNoteID or 1
    P.view = s.fullView or s.view or 'daily'
    if P.view=='compact' then P.view='daily';s.compact=true end
    P.selectedDay = M.Day(GetServerTime())
    P.month = P.selectedDay
end
function P.Character()
    local guid = UnitGUID('player')
    if not guid then return nil end
    local c = P.db.characters[guid]
    if not c then c={professions={}}; P.db.characters[guid]=c end
    c.name = UnitName('player')
    c.realm = GetNormalizedRealmName() or GetRealmName()
    local _, class = UnitClass('player')
    c.class = class
    c.lastSeen = GetServerTime()
    return c
end
function P.Snapshot(r)
    local info = safe(C_CurrencyInfo.GetCurrencyInfo,r.currencyID)
    if not info or type(info.quantity) ~= 'number' or type(info.maxQuantity) ~= 'number' then return end
    if issecretvalue and (issecretvalue(info.quantity) or issecretvalue(info.maxQuantity)) then return end
    if info.maxQuantity <= 0 then return end
    local cycle = info.rechargingCycleDurationMS
    if issecretvalue and issecretvalue(cycle) then return end
    local now = GetServerTime()
    local amountPerCycle = info.rechargingAmountPerCycle
    if issecretvalue and issecretvalue(amountPerCycle) then return end
    amountPerCycle = type(amountPerCycle)=='number' and amountPerCycle>0 and amountPerCycle or 1
    local rate = cycle and cycle > 0 and cycle/1000/amountPerCycle or r.secondsPerPoint
    if not rate and info.quantity < info.maxQuantity then return end
    -- Keep the original forecast while simply re-observing normal regeneration.
    -- A spend/refund, max change or rate change creates a new snapshot.
    local predicted = M.Current(r,now)
    if predicted and r.max == info.maxQuantity and r.secondsPerPoint == rate
        and info.quantity >= math.floor(predicted+0.000001)
        and math.abs(predicted-info.quantity) < 1.01 then
        r.lastChecked = now
        return
    end
    r.amount, r.max, r.secondsPerPoint = info.quantity, info.maxQuantity, rate
    r.observedAt, r.lastChecked = now,now
end
function P.Discover()
    if not P.db then return end
    local c = P.Character()
    if not c then return end
    local api = C_TradeSkillUI
    -- Inspect the player's loaded profession, never linked / other-player recipes.
    if safe(api.IsTradeSkillLinked) or safe(api.IsTradeSkillGuild) then return end
    local base = safe(api.GetBaseProfessionInfo)
    local children = safe(api.GetChildProfessionInfos) or {}
    local child = safe(api.GetChildProfessionInfo)
    if child and child.professionID then children[#children+1]=child end
    local seen = {}
    for _,p in ipairs(children) do
        local skill = p.professionID
        if skill and not seen[skill] and p.skillLevel and p.skillLevel > 0 then
            seen[skill]=true
            local currencyID = safe(api.GetConcentrationCurrencyID,skill)
            local info = currencyID and currencyID > 0 and safe(C_CurrencyInfo.GetCurrencyInfo,currencyID)
            if info and info.maxQuantity and not (issecretvalue and issecretvalue(info.maxQuantity)) and info.maxQuantity > 0 then
                local r = c.professions[skill] or {}
                c.professions[skill]=r
                r.currencyID, r.skillLineID = currencyID,skill
                r.name = (base and base.professionName) or p.parentProfessionName or p.professionName or 'Profession'
                r.expansion = p.expansionName or p.professionName or ''
                r.expansionID=p.expansionID or r.expansionID
                r.icon = p.icon or info.iconFileID
                P.Snapshot(r)
            end
        end
    end
    P.RefreshCurrent()
end
function P.RefreshCurrent()
    local c = P.Character()
    if not c then return end
    for _,r in pairs(c.professions) do P.Snapshot(r) end
    if P.frame and P.frame:IsShown() then P.Render(true) end
end
function P.QueueScan(discover)
    P.needDiscovery = P.needDiscovery or discover
    if P.scanPending then return end
    P.scanPending=true
    C_Timer.After(0.4,function()
        P.scanPending=false
        local need=P.needDiscovery; P.needDiscovery=false
        if need then P.Discover() else P.RefreshCurrent() end
    end)
end
function P.ResetSeconds()
    local seconds = safe(C_DateAndTime.GetSecondsUntilWeeklyReset)
    if type(seconds)=='number' and seconds > 0 then return seconds,false end
    -- Explicit fallback for an unavailable reset API: NA Tuesday 10 AM local.
    local now=GetServerTime()
    local nextDay=M.NextWeekday(M.Day(now),3)
    local t=date('*t',nextDay); t.hour=10
    local nextReset=time(t)
    if nextReset<=now then nextReset=M.AddDays(nextDay,7)+10*3600 end
    return nextReset-now,true
end
function P.GetResetSeconds(kind)
    local api=C_DateAndTime
    local fn
    if api then if kind=='daily' then fn=api.GetSecondsUntilDailyReset else fn=api.GetSecondsUntilWeeklyReset end end
    local seconds=safe(fn)
    if type(seconds)=='number' and seconds>0 then return seconds end
end
function P.DismissNote(n)
    local ok,err=M.DismissNote(n,GetServerTime(),P.GetResetSeconds('daily'),P.GetResetSeconds('weekly'))
    if not ok then P.Print(err);return end
    P.Render(true)
end
function P.SaveNote(existing,text,firstDay,mode,interval)
    text=text:match('^%s*(.-)%s*$')
    if text=='' or #text>500 then return nil,'Enter a note (up to 500 characters).' end
    local due=M.ParseDay(firstDay)
    if not due then return nil,'Enter a real date as YYYY-MM-DD.' end
    if mode=='days' then
        interval=tonumber(interval)
        if not interval or interval~=math.floor(interval) or interval<1 or interval>3650 then return nil,'Repeat interval must be 1 to 3650 whole days.' end
    end
    if mode=='dailyReset' or mode=='weeklyReset' then
        local seconds=P.GetResetSeconds(mode=='dailyReset' and 'daily' or 'weekly')
        if not seconds then return nil,'Reset time is unavailable. Try again after entering the world.' end
        local clock=date('*t',GetServerTime()+seconds)
        if mode=='weeklyReset' then due=M.NextWeekday(due,clock.wday) end
        local d=date('*t',due);d.hour=clock.hour;d.min=clock.min;d.sec=clock.sec
        due=time(d)
    end
    local n=existing or {id=P.db.nextNoteID}
    if not existing then P.db.nextNoteID=n.id+1 end
    n.text,n.due,n.mode,n.interval=text,due,mode,interval
    n.dismissedAt=nil
    P.db.notes[n.id]=n
    return n
end
function P.Show(view)
    if not P.frame then P.BuildUI() end
    if view then
        P.view=view
        if P.db.settings.compact then P.SetCompact(false) end
    end
    P.frame:Show()
    P.Render()
end
local events=CreateFrame('Frame')
P.eventFrame=events
for _,e in ipairs({'ADDON_LOADED','PLAYER_LOGIN','PLAYER_ENTERING_WORLD','CURRENCY_DISPLAY_UPDATE',
    'TRADE_SKILL_SHOW','TRADE_SKILL_DATA_SOURCE_CHANGED','TRADE_SKILL_LIST_UPDATE','SKILL_LINES_CHANGED','PLAYER_LOGOUT'}) do events:RegisterEvent(e) end
events:SetScript('OnEvent',function(_,event,arg)
    if event=='ADDON_LOADED' then
        if arg==addon then P.Init() end
    elseif not P.db then return
    elseif event=='PLAYER_LOGIN' then
        P.Character()
        P.CreateMinimap()
        C_Timer.After(2,function()
            P.RefreshCurrent()
            if P.db.settings.login then P.selectedDay=M.Day(GetServerTime()); P.Show() end
        end)
        P.ticker=C_Timer.NewTicker(60,function() P.RefreshCurrent() end)
        P.clockTicker=C_Timer.NewTicker(1,function()
            if P.frame and P.frame:IsShown() then
                local day=M.Key(GetServerTime())
                if P.lastRenderedDay~=day then P.Render(true) else P.UpdateCountdown() end
            end
        end)
    elseif event=='PLAYER_LOGOUT' then
        if P.frame then P.SaveGeometry() end
        P.RefreshCurrent()
    elseif event=='CURRENCY_DISPLAY_UPDATE' then
        P.QueueScan(false)
    else
        P.QueueScan(true)
    end
end)
SLASH_DUCKMOOPLANNER1='/dmp'
SLASH_DUCKMOOPLANNER2='/duckplanner'
SLASH_DUCKMOOPLANNER3='/planner'
SlashCmdList.DUCKMOOPLANNER=function(input)
    local cmd=input:lower():match('^%s*(.-)%s*$')
    if cmd=='scan' then P.Discover(); P.Print('Scanned the open profession. Open each crafting profession once on each character.'); return end
    if cmd=='minimap' then P.db.settings.hideMinimap=not P.db.settings.hideMinimap;P.CreateMinimap();return end
    if cmd=='about' then P.settingsTab='about';P.Show('settings');return end
    if cmd=='compact' then P.Show();P.SetCompact(true);return end
    if cmd=='full' then P.Show();P.SetCompact(false);return end
    if cmd=='note' then P.Show('reminders');P.NoteEditor();return end
    if cmd=='today' then P.followToday=true;P.selectedDay=M.Day(GetServerTime()); P.Show('daily'); return end
    if cmd=='daily' or cmd=='weekly' or cmd=='monthly' or cmd=='settings' or cmd=='reminders' then P.Show(cmd); return end
    if cmd=='position' then if P.frame then P.frame:ClearAllPoints();P.frame:SetPoint('CENTER') end;P.db.settings.position=nil;P.db.settings.fullPosition=nil;P.db.settings.compactPosition=nil;return end
    if P.frame and P.frame:IsShown() then P.frame:Hide() else P.Show() end
end

function P.SaveGroup(id,name)
    name=name:match('^%s*(.-)%s*$')
    if name=='' or #name>60 then return nil,'Use a group name from 1 to 60 characters.' end
    for existing,g in pairs(P.db.groups) do if existing~=id and g.name:lower()==name:lower() then return nil,'That group name already exists.' end end
    if not id then id=P.db.nextGroupID;P.db.nextGroupID=id+1 end
    P.db.groups[id]={name=name}
    return id
end

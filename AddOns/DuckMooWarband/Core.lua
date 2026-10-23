local addon,W=...
W.name=addon;W.version='0.4.0';local M=W.Model
function W.Now()return GetServerTime()end
function W.Init()
    DuckMooWarbandDB=DuckMooWarbandDB or {}
    W.db=DuckMooWarbandDB;local db=W.db
    db.version=1;db.characters=db.characters or {};db.tasks=db.tasks or {};db.nextID=db.nextID or 1
    db.settings=db.settings or {};db.history=db.history or {};db.undo=nil;db.categoryRules=db.categoryRules or {}
end
function W.ImportRoster()
    for _,source in ipairs({{provider=DuckMooFolio,name='Character Folio'},{provider=DuckMooPlanner,name='Concentration Planner'}})do
        local provider=source.provider
        if provider and type(provider.ExportRoster)=='function' then
            local ok,rows=pcall(provider.ExportRoster)
            if ok and type(rows)=='table' then
                for guid,snapshot in pairs(rows)do
                    if type(guid)=='string' and type(snapshot)=='table' and type(snapshot.name)=='string' and type(snapshot.realm)=='string' then
                        local c=W.db.characters[guid] or {groups={}}
                        if not c.lastSeen or (tonumber(snapshot.lastSeen) or 0)>c.lastSeen then
                            for _,key in ipairs({'name','realm','class','className','lastSeen'})do
                                if type(snapshot[key])=='string' or type(snapshot[key])=='number' then c[key]=snapshot[key] end
                            end
                            c.rosterSource=source.name
                        end
                        W.db.characters[guid]=c
                    end
                end
            end
        end
    end
end
function W.CaptureCharacter()
    W.ImportRoster()
    local guid=UnitGUID('player');if not guid then return end
    local c=W.db.characters[guid] or {groups={}}
    c.name=UnitName('player');c.realm=GetRealmName();local name,token=UnitClass('player')
    c.class=token;c.className=name;c.lastSeen=W.Now();c.groups=c.groups or {};c.rosterSource='Logged in'
    local api=C_Covenants
    if api and type(api.GetActiveCovenantID)=='function' then
        local ok,id=pcall(api.GetActiveCovenantID)
        if ok and not (issecretvalue and issecretvalue(id)) and type(id)=='number' and id>=0 then
            c.covenantID=id;c.covenantName=nil;c.covenantSeenAt=c.lastSeen
            if id>0 and type(api.GetCovenantData)=='function' then
                local success,data=pcall(api.GetCovenantData,id)
                if success and type(data)=='table' and not (issecretvalue and issecretvalue(data)) and type(data.name)=='string' and not (issecretvalue and issecretvalue(data.name)) then c.covenantName=data.name end
            end
        end
    end
    W.db.characters[guid]=c;W.current=guid
end
function W.Resets()
    local out={};local api=C_DateAndTime or {};local now=W.Now()
    for kind,fn in pairs({daily=api.GetSecondsUntilDailyReset,weekly=api.GetSecondsUntilWeeklyReset})do
        if type(fn)=='function' then
            local ok,seconds=pcall(fn)
            if ok and not (issecretvalue and issecretvalue(seconds)) and type(seconds)=='number' and seconds>0 then out[kind]=now+seconds end
        end
    end
    return out
end
function W.SaveTask(draft,id)
    local ok,err=M.Validate(draft,W.db);if not ok then return nil,err end
    local old=id and W.db.tasks[id]
    if id and not old then return nil,'This task no longer exists.' end
    local task=M.Copy(draft);task.text=M.Trim(task.text);task.category=M.Trim(task.category)
    task.weekday=task.repeatMode=='weekday' and task.weekday or nil
    task.interval=task.repeatMode=='interval' and task.interval or nil
    task.id=id or W.db.nextID;task.createdAt=old and old.createdAt or W.Now()
    task.states=old and old.states or {};task.archived=old and old.archived or false
    task.scheduleRevision=old and old.scheduleRevision or 1
    if old and (old.repeatMode~=task.repeatMode or old.weekday~=task.weekday or old.interval~=task.interval)then
        task.scheduleRevision=task.scheduleRevision+1
        -- A changed cadence starts fresh; historical actions remain in history.
        for _,state in pairs(task.states)do state.nextAt=nil;state.deferUntil=nil end
    end
    W.db.tasks[task.id]=task;if not id then W.db.nextID=task.id+1 end
    W.db.undo=nil;return task
end
function W.Quick(text)
    if not W.current then return nil,'Log into a character before adding a task.' end
    return W.SaveTask({text=text,category='',scope='selected',characters={[W.current]=true},progress='character',repeatMode='once'})
end
W.StarterPacks={
    daily={title='Daily world activities',tasks={{id='world',text='Do a world quest outing',category='World activities',repeatMode='daily'}}},
    weekly={title='Weekly activities',tasks={{id='dungeon',text='Do a weekly dungeon run',category='Weekly activities',repeatMode='weekly'},{id='delve',text='Do a weekly delve',category='Weekly activities',repeatMode='weekly'},{id='vault',text='Check the Great Vault',category='Weekly activities',repeatMode='weekly'}}},
}
function W.AddStarterPack(name)
    local pack=W.StarterPacks[name];if not pack or not W.current then return nil,'Log into a character and choose a starter pack.' end
    local count=0
    for _,template in ipairs(pack.tasks)do
        local key=name..':'..template.id;local exists=false
        for _,task in pairs(W.db.tasks)do if task.sourceTemplate==key and task.sourceCharacter==W.current then exists=true end end
        if not exists then
            local draft=M.Copy(template);draft.id=nil;draft.sourceTemplate=key;draft.sourceCharacter=W.current
            draft.scope='selected';draft.characters={[W.current]=true};draft.progress='character'
            local task,err=W.SaveTask(draft);if not task then return nil,err end;count=count+1
        end
    end
    return count
end
function W.Action(row,action)
    local ok,err=M.Action(W.db,row.task,row.key,action,W.Now(),W.Resets())
    if not ok then W.Print(err)end;W.Render()
end
function W.Print(text)print('|cffb99af4Warband Planner:|r '..text)end
local events=CreateFrame('Frame')
events:RegisterEvent('ADDON_LOADED');events:RegisterEvent('PLAYER_LOGIN');events:RegisterEvent('PLAYER_LOGOUT');events:RegisterEvent('COVENANT_CHOSEN')
events:SetScript('OnEvent',function(_,event,name)
    if event=='ADDON_LOADED' and name==addon then W.Init()
    elseif event=='PLAYER_LOGIN' and W.db then W.CaptureCharacter()
    elseif event=='PLAYER_LOGOUT' and W.db then W.CaptureCharacter()
    elseif event=='COVENANT_CHOSEN' and W.db then W.CaptureCharacter();W.Render() end
end)
SLASH_DUCKMOOWARBAND1='/warplan';SLASH_DUCKMOOWARBAND2='/dmwarband'
SlashCmdList.DUCKMOOWARBAND=function(text)
    if not W.db then W.Init()end;W.CaptureCharacter()
    if M.Trim(text)~='' then local task,err=W.Quick(text);if not task then W.Print(err)end end
    W.CreateUI();W.frame:Show();W.Render()
end

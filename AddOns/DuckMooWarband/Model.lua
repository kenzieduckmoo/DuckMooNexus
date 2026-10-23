local _,W=...
local M={};W.Model=M
-- Primary armor categories, verified against Blizzard's Midnight class sets.
M.Armor={MAGE='Cloth',PRIEST='Cloth',WARLOCK='Cloth',DRUID='Leather',MONK='Leather',ROGUE='Leather',DEMONHUNTER='Leather',HUNTER='Mail',SHAMAN='Mail',EVOKER='Mail',WARRIOR='Plate',PALADIN='Plate',DEATHKNIGHT='Plate'}
function M.Copy(value)
    if type(value)~='table' then return value end
    local out={};for k,v in pairs(value)do out[k]=M.Copy(v)end;return out
end
function M.Trim(text) return type(text)=='string' and text:match('^%s*(.-)%s*$') or '' end
function M.Day(now)
    local d=date('*t',now);return time({year=d.year,month=d.month,day=d.day,hour=0,min=0,sec=0})
end
function M.AddDays(now,n)
    local d=date('*t',now);return time({year=d.year,month=d.month,day=d.day+n,hour=0,min=0,sec=0})
end
function M.Validate(d,db)
    if M.Trim(d.text)=='' or #d.text>500 then return nil,'Enter a task, up to 500 characters.' end
    if not ({selected=true,all=true,class=true,group=true,armor=true,covenant=true})[d.scope] then return nil,'Choose who this applies to.' end
    if d.scope=='selected' then
        local found=false;for guid,yes in pairs(d.characters or {})do if yes and db.characters[guid]then found=true end end
        if not found then return nil,'Choose at least one recorded character.' end
    elseif d.scope=='class' and M.Trim(d.rule)=='' then return nil,'Choose a class.'
    elseif d.scope=='group' and M.Trim(d.rule)=='' then return nil,'Choose a group.'
    elseif d.scope=='armor' and not ({Cloth=true,Leather=true,Mail=true,Plate=true})[d.rule] then return nil,'Choose an armor category.'
    elseif d.scope=='covenant' and (type(d.rule)~='number' or d.rule<=0 or d.rule%1~=0) then return nil,'Choose a recorded covenant.' end
    if d.progress~='character' and d.progress~='account' then return nil,'Choose separate or shared progress.' end
    if not ({once=true,daily=true,weekly=true,weekday=true,interval=true})[d.repeatMode] then return nil,'Choose when it appears.' end
    if d.repeatMode=='weekday' and (type(d.weekday)~='number' or d.weekday%1~=0 or d.weekday<1 or d.weekday>7) then return nil,'Choose a weekday.' end
    if d.repeatMode=='interval' and (type(d.interval)~='number' or d.interval%1~=0 or d.interval<1 or d.interval>365) then return nil,'Use a whole number of days from 1 to 365.' end
    return true
end
function M.Eligible(task,guid,c)
    if task.scope=='all' then return true end
    if task.scope=='selected' then return task.characters and task.characters[guid]==true end
    if task.scope=='class' then return c.class~=nil and c.class==task.rule end
    if task.scope=='group' then return c.groups and c.groups[task.rule]==true end
    if task.scope=='armor' then return c.class~=nil and M.Armor[c.class]==task.rule end
    if task.scope=='covenant' then return c.covenantID~=nil and c.covenantID==task.rule end
    return false
end
function M.Targets(task,db)
    local out={};for guid,c in pairs(db.characters)do if M.Eligible(task,guid,c)then out[#out+1]=guid end end
    table.sort(out);return out
end
function M.Occurrence(task,state,now,resets)
    if task.archived then return nil end
    local mode=task.repeatMode;local key='once';local untilAt
    if mode=='daily' or mode=='weekly' then
        untilAt=resets and resets[mode]
        if not untilAt or untilAt<=now then return {waiting=true,key='unknown',label='Reset data unavailable'} end
        key=mode..':'..math.floor((untilAt+30)/60)
    elseif mode=='weekday' then
        if date('*t',now).wday~=task.weekday then return nil end
        key='day:'..date('%Y-%m-%d',now);untilAt=M.AddDays(now,1)
    elseif mode=='interval' then
        if state and state.nextAt and now<state.nextAt then return nil end
        key='interval:'..tostring(state and state.nextAt or task.createdAt)
    end
    key=tostring(task.scheduleRevision or 1)..':'..key
    if state and state.deferUntil and state.deferUntil>now then return nil end
    if state and (state.doneKey==key or state.skipKey==key) then return nil end
    return {key=key,untilAt=untilAt}
end
function M.Rows(db,now,resets,allTasks)
    local rows={}
    for _,task in pairs(db.tasks)do
        local targets=M.Targets(task,db)
        if allTasks then rows[#rows+1]={task=task,key='@account',targets=targets}
        elseif #targets>0 and not task.archived and (not db.categoryRules or not db.categoryRules[task.category] or not db.categoryRules[task.category].days or db.categoryRules[task.category].days[date('*t',now).wday]) then
            local keys=task.progress=='account' and {'@account'} or targets
            for _,key in ipairs(keys)do
                local state=task.states and task.states[key]
                local occurrence=M.Occurrence(task,state,now,resets)
                if occurrence then rows[#rows+1]={task=task,key=key,targets=targets,occurrence=occurrence,state=state} end
            end
        end
    end
    return rows
end
function M.Action(db,task,key,action,now,resets)
    local valid=key=='@account' and task.progress=='account' and #M.Targets(task,db)>0
    if key~='@account' then valid=task.progress=='character' and db.characters[key] and M.Eligible(task,key,db.characters[key]) end
    if not valid then return nil,'This character is no longer eligible.' end
    local old=task.states[key];local occurrence=M.Occurrence(task,old,now,resets)
    if not occurrence or occurrence.waiting then return nil,'This occurrence is unavailable. Refresh reset data before recording progress.' end
    if not ({done=true,worked=true,postpone=true,skip=true})[action] then return nil,'Unknown action.' end
    local state=M.Copy(old or {})
    db.undo={id=task.id,key=key,before=M.Copy(old),historySize=#db.history}
    if action=='done' then
        state.doneKey=occurrence.key;state.lastDone=now
        if task.repeatMode=='interval' then state.nextAt=M.AddDays(now,task.interval);state.doneKey=nil end
    elseif action=='worked' then state.lastWorked=now
    elseif action=='postpone' then state.deferUntil=M.AddDays(now,1)
    elseif action=='skip' then
        state.skipKey=occurrence.key
        if task.repeatMode=='interval' then state.nextAt=M.AddDays(now,task.interval);state.skipKey=nil end
    end
    task.states[key]=state
    db.history[#db.history+1]={taskID=task.id,key=key,action=action,at=now,text=task.text}
    -- Keep a small activity record without letting the saved database grow forever.
    if #db.history>500 then db.undo.dropped=table.remove(db.history,1);db.undo.historySize=499 end
    return true
end
function M.Undo(db)
    local u=db.undo;if not u or not db.tasks[u.id]then return false end
    db.tasks[u.id].states[u.key]=M.Copy(u.before)
    while #db.history>u.historySize do table.remove(db.history)end
    if u.dropped then table.insert(db.history,1,u.dropped)end
    db.undo=nil;return true
end

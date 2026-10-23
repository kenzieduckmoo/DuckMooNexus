local _, P = ...
P.Model = {}
local M = P.Model
local floor, ceil = math.floor, math.ceil

-- Civil dates deliberately use the computer clock. Noon-based day arithmetic
-- avoids adding 86400 seconds across a daylight saving transition.
function M.Day(t)
    local d = date('*t', t)
    return time({year=d.year, month=d.month, day=d.day, hour=0, min=0, sec=0})
end
function M.AddDays(t, count)
    local d = date('*t', t)
    return time({year=d.year, month=d.month, day=d.day+count, hour=0, min=0, sec=0})
end
function M.Key(t) return date('%Y-%m-%d', t) end
function M.Clock(t)
    local d = date('*t', t)
    return string.format('%d:%02d %s', (d.hour+11)%12+1, d.min, d.hour < 12 and 'AM' or 'PM')
end
function M.ParseDay(s)
    local y, m, d = s:match('^(%d%d%d%d)%-(%d%d)%-(%d%d)$')
    if not y then return nil end
    y,m,d = tonumber(y),tonumber(m),tonumber(d)
    if y < 2000 or y > 2100 or m < 1 or m > 12 or d < 1 or d > 31 then return nil end
    local t = time({year=y,month=m,day=d,hour=0,min=0,sec=0})
    if M.Key(t) ~= s then return nil end
    return t
end
function M.Current(r, now)
    if not r.amount or not r.max or r.max <= 0 then return nil end
    if r.amount >= r.max then return r.max end
    if not r.secondsPerPoint or r.secondsPerPoint <= 0 then return nil end
    return math.min(r.max, r.amount + math.max(0,now-r.observedAt)/r.secondsPerPoint)
end
function M.FullAt(r)
    if not r.amount or not r.max or r.max <= 0 or not r.observedAt then return nil end
    if r.amount >= r.max then return r.observedAt end
    if not r.secondsPerPoint or r.secondsPerPoint <= 0 then return nil end
    return r.observedAt + ceil((r.max-r.amount)*r.secondsPerPoint)
end
function M.NextWeekday(day, weekday)
    return M.AddDays(day, (weekday-date('*t',day).wday)%7)
end
function M.SetSchedule(r, mode, firstDay, weekday)
    r.patron = {mode=mode, due=M.Day(firstDay), weekday=weekday}
end
function M.Complete(r, now)
    local s = r.patron
    if not s then return end
    s.lastDone = now
    if s.mode == 'four' then
        s.due = M.AddDays(now,4)
    else
        s.due = M.NextWeekday(M.AddDays(now,1),s.weekday)
    end
end
-- Use the regional reset API's epoch anchor, including local DST changes.
function M.PatronResetAt(day, now, dailySeconds)
    if type(dailySeconds)~='number' or dailySeconds<0 then return nil end
    local anchor=now+dailySeconds
    local target=M.Key(day)
    local at=anchor+floor((M.Day(day)-M.Day(anchor))/86400)*86400
    while M.Key(at)<target do at=at+86400 end
    while M.Key(at)>target do at=at-86400 end
    return at
end
function M.PatronDue(r,now,dailySeconds)
    local s=r.patron
    if not s or not s.due then return false end
    if M.Day(s.due)<M.Day(now) then return true end
    local at=M.PatronResetAt(s.due,now,dailySeconds)
    return at~=nil and at<=now
end
function M.PatronDates(s, first, last, now)
    local out = {}
    if not s or not s.due or s.due >= last then return out end
    local due = M.Day(s.due)
    local today = M.Day(now)
    -- Outstanding work is sticky. Forecasts after this date are tentative until Done.
    if due < today then due = today end
    local step = s.mode == 'four' and 4 or 7
    while due < first do due = M.AddDays(due,step) end
    while due < last do
        out[#out+1] = {at=due, overdue=s.due < today and due == today,
            projected=due ~= math.max(M.Day(s.due),today)}
        due = M.AddDays(due,step)
    end
    return out
end
function M.Events(db, first, last, now, includeReady, patrons, filter)
    local out = {}
    filter = (filter or ''):lower()
    for guid, c in pairs(db.characters) do
        for id,r in pairs(c.professions) do
            local label = c.name..'-'..c.realm
            if M.Visible(db,r,id) and (label..' '..r.name..' '..(r.expansion or '')):lower():find(filter,1,true) then
                local full = M.FullAt(r)
                local function add(kind,at,extra)
                    local e = {kind=kind,at=at,guid=guid,id=id,character=label,record=r}
                    for k,v in pairs(extra or {}) do e[k]=v end
                    out[#out+1]=e
                end
                if full then
                    if full > now and full >= first and full < last then
                        add('concentration',full)
                    elseif includeReady and full <= now then
                        add('concentration',now,{ready=true})
                    end
                end
                if patrons then
                    for _,p in ipairs(M.PatronDates(r.patron,first,last,now)) do
                        add('patron',p.at,p)
                    end
                end
            end
        end
    end
    for id,n in pairs(db.notes or {}) do
        if (n.text or ''):lower():find(filter,1,true) then
            for _,occurrence in ipairs(M.NoteDates(n,first,last,now)) do
                local e={kind='note',id=id,character='',record=n,at=occurrence.at}
                for k,v in pairs(occurrence) do e[k]=v end
                out[#out+1]=e
            end
        end
    end
    table.sort(out,function(a,b)
        if a.ready ~= b.ready then return a.ready == true end
        if a.at ~= b.at then return a.at < b.at end
        if a.character ~= b.character then return a.character < b.character end
        local an,bn=a.record.name or a.record.text or '',b.record.name or b.record.text or ''
        if an ~= bn then return an < bn end
        if a.id ~= b.id then return a.id < b.id end
        return a.kind < b.kind
    end)
    return out
end
function M.Week(now, untilReset, offset)
    -- Reset-aligned 24h intervals; unlike the daily view these start at reset hour.
    local start = now + untilReset - 604800 + (offset or 0)*604800
    return start, start+604800
end

-- IDs work across localized profession names and migrate existing snapshots.
M.MidnightSkills = {[2906]=true,[2907]=true,[2908]=true,[2909]=true,[2910]=true,
    [2911]=true,[2912]=true,[2913]=true,[2914]=true,[2915]=true,[2916]=true,
    [2917]=true,[2918]=true,[2950]=true}
function M.IsMidnight(r,id)
    return M.MidnightSkills[r.skillLineID or id] == true or r.expansionID == 11
        or (r.expansion or ''):lower():find('midnight',1,true) ~= nil
end
function M.Visible(db,r,id)
    return not r.hidden and (M.IsMidnight(r,id) or (db.settings and db.settings.includePrior == true))
end
function M.Duration(seconds)
    if type(seconds)~='number' then return 'unavailable' end
    seconds=math.max(0,math.floor(seconds))
    local days=math.floor(seconds/86400)
    local hours=math.floor(seconds%86400/3600)
    local minutes=math.floor(seconds%3600/60)
    local secs=seconds%60
    if days>0 then return string.format('%dd %02dh %02dm %02ds',days,hours,minutes,secs) end
    return string.format('%02dh %02dm %02ds',hours,minutes,secs)
end
function M.DismissNote(n,now,dailySeconds,weeklySeconds)
    if n.mode=='dailyReset' or n.mode=='weeklyReset' then
        local seconds
        if n.mode=='dailyReset' then seconds=dailySeconds else seconds=weeklySeconds end
        if type(seconds)~='number' or seconds<=0 then return false,'Reset time is unavailable. Try again after entering the world.' end
        n.due=now+seconds
    elseif n.mode=='days' then
        n.due=M.AddDays(now,n.interval)
    else
        n.dismissedAt=now
    end
    n.lastDone=now
    return true
end
function M.NoteDates(n,first,last,now)
    local out={}
    if n.dismissedAt or not n.due then return out end
    local today=M.Day(now)
    local at=math.max(n.due,today)
    local function advance(t)
        if n.mode=='days' then return M.AddDays(t,n.interval) end
        if n.mode=='dailyReset' or n.mode=='weeklyReset' then
            local clock=date('*t',n.due)
            local nextDay=n.mode=='dailyReset' and M.AddDays(t,1) or M.NextWeekday(M.AddDays(t,1),clock.wday)
            local d=date('*t',nextDay);d.hour=clock.hour;d.min=clock.min;d.sec=clock.sec
            return time(d)
        end
    end
    while at and at<first do at=advance(at) end
    while at and at<last do
        out[#out+1]={at=at,overdue=n.due<today and at==today,
            projected=at~=math.max(n.due,today),due=n.due}
        at=advance(at)
    end
    return out
end
function M.TodayGroups(db,now,filter)
    local events=M.Events(db,M.Day(now),M.AddDays(now,1),now,true,true,filter)
    local groups,byGuid,notes={},{},{}
    for _,e in ipairs(events) do
        if e.kind=='note' then notes[#notes+1]=e
        else
            local g=byGuid[e.guid]
            if not g then g={guid=e.guid,name=e.character,events={}};groups[#groups+1]=g;byGuid[e.guid]=g end
            g.events[#g.events+1]=e
        end
    end
    table.sort(groups,function(a,b) return a.name<b.name end)
    return groups,notes
end

function M.CompletePatron(r,now)
    if not r.patron then M.SetSchedule(r,'four',M.Day(now)) end
    M.Complete(r,now)
end
function M.GroupNames(db,c)
    local names={}
    for id in pairs(c.groups or {}) do if db.groups and db.groups[id] then names[#names+1]=db.groups[id].name end end
    table.sort(names);return table.concat(names,', ')
end
function M.AssignGroup(db,guids,id,enabled)
    if not db.groups[id] then return end
    for _,guid in ipairs(guids) do
        local c=db.characters[guid]
        if c then c.groups=c.groups or {};c.groups[id]=enabled and true or nil end
    end
end
function M.DeleteGroup(db,id)
    db.groups[id]=nil
    for _,c in pairs(db.characters) do if c.groups then c.groups[id]=nil end end
end
function M.Roster(db,current,filters)
    filters=filters or {}
    local entries,pinned={}
    local function entry(guid,c)
        local professions={}
        for id,r in pairs(c.professions) do
            if (M.IsMidnight(r,id) or filters.prior) and (not filters.profession or filters.profession==r.name) then
                professions[#professions+1]={id=id,r=r,guid=guid,c=c,name=c.name..'-'..c.realm}
            end
        end
        table.sort(professions,function(a,b) if a.r.name~=b.r.name then return a.r.name<b.r.name end;return a.id<b.id end)
        return {guid=guid,c=c,name=c.name,realm=c.realm,professions=professions,groups=M.GroupNames(db,c)}
    end
    for guid,c in pairs(db.characters) do
        if guid==current then
            pinned=entry(guid,c)
            pinned.professions={}
            for id,r in pairs(c.professions) do
                if M.IsMidnight(r,id) or filters.prior then pinned.professions[#pinned.professions+1]={id=id,r=r,guid=guid,c=c,name=c.name..'-'..c.realm} end
            end
            table.sort(pinned.professions,function(a,b) if a.r.name~=b.r.name then return a.r.name<b.r.name end;return a.id<b.id end)
        else
            local e=entry(guid,c)
            local groupMatch=not filters.group or (filters.group=='ungrouped' and e.groups=='') or (c.groups and c.groups[filters.group])
            local search=(e.name..' '..e.realm..' '..e.groups):lower()
            for _,p in ipairs(e.professions) do search=search..' '..p.r.name:lower()..' '..(p.r.expansion or ''):lower() end
            if #e.professions>0 and groupMatch and (not filters.realm or filters.realm==e.realm)
                and search:find((filters.search or ''):lower(),1,true) then entries[#entries+1]=e end
        end
    end
    local function sortValue(e)
        if filters.sort=='realm' then return e.realm:lower() end
        if filters.sort=='profession' then return (#e.professions>0 and e.professions[1].r.name or ''):lower() end
        if filters.sort=='group' then return e.groups:lower() end
        return e.name:lower()
    end
    table.sort(entries,function(a,b)
        local av,bv=sortValue(a),sortValue(b)
        if av~=bv then if filters.descending then return av>bv else return av<bv end end
        if a.name~=b.name then return a.name<b.name end
        if a.realm~=b.realm then return a.realm<b.realm end
        return a.guid<b.guid
    end)
    return pinned,entries
end
function M.Upcoming(db,first,last,now,filter)
    local out={}
    for _,e in ipairs(M.Events(db,first,last,now,false,true,filter)) do
        local due=e.kind=='patron' and e.record.patron.due or e.kind=='note' and e.record.due or e.at
        if not e.ready and not e.overdue and (e.projected or due>=M.Day(now)) then out[#out+1]=e end
    end
    return out
end

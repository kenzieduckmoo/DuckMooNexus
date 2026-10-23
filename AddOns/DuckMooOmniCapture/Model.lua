local _, O = ...
O.version = "0.1.0"
function O.Safe(value, depth, seen, budget)
    if issecretvalue and issecretvalue(value) then return nil end
    local kind = type(value)
    if kind == "number" then
        if value == value and value ~= math.huge and value ~= -math.huge then return value end
    elseif kind == "string" then return string.sub(value, 1, 2048)
    elseif kind == "boolean" then return value
    elseif kind == "table" then
        depth, seen, budget = depth or 0, seen or {}, budget or {remaining=50000, omitted=0}
        if depth >= 10 or seen[value] then budget.omitted=budget.omitted+1; return nil end
        seen[value] = true
        local result = {}
        for k,v in pairs(value) do
            if budget.remaining <= 0 then budget.omitted=budget.omitted+1; break end
            if not (issecretvalue and issecretvalue(k)) and (type(k)=="string" or type(k)=="number") then
                budget.remaining=budget.remaining-1
                local safe=O.Safe(v,depth+1,seen,budget)
                if safe~=nil then result[k]=safe end
            end
        end
        seen[value]=nil
        return result
    end
end
function O.Call(fn, ...)
    if type(fn)~="function" then return nil end
    local ok,a,b,c,d,e,f,g,h = pcall(fn,...)
    if ok then
        local budget={remaining=50000,omitted=0}
        a,b,c,d,e,f,g,h=O.Safe(a,0,{},budget),O.Safe(b,0,{},budget),O.Safe(c,0,{},budget),O.Safe(d,0,{},budget),O.Safe(e,0,{},budget),O.Safe(f,0,{},budget),O.Safe(g,0,{},budget),O.Safe(h,0,{},budget)
        if budget.omitted>0 then O.readLimited=true end
        return a,b,c,d,e,f,g,h
    end
end
function O.Init()
    if DuckMooOmniCaptureDB and DuckMooOmniCaptureDB.schema~=1 then
        O.blocked=true; print("DuckMoo Omni Capture: unknown saved-data schema; existing data preserved."); return
    end
    DuckMooOmniCaptureDB=DuckMooOmniCaptureDB or {schema=1,characters={},settings={enabled=true,events=true}}
    O.db=DuckMooOmniCaptureDB
    O.db.settings=O.db.settings or {enabled=true,events=true}
    O.db.characters=O.db.characters or {}
end
function O.Character()
    if not O.db or not O.db.settings.enabled then return nil end
    local guid=O.Call(UnitGUID,"player")
    if not guid then return nil end
    local c=O.db.characters[guid]
    if not c then c={guid=guid,sections={},events={},sequence=0,droppedEvents=0};O.db.characters[guid]=c end
    c.name=O.Call(UnitName,"player");c.realm=O.Call(GetRealmName)
    return c
end
function O.Store(name, body, status, detail)
    local c=O.Character();if not c then return end
    local budget={remaining=50000,omitted=0}
    local safe=O.Safe(body,0,{},budget)
    local now=GetServerTime()
    c.sections[name]=c.sections[name] or {}
    local section=c.sections[name]
    section.attemptedAt=now;section.status=budget.omitted>0 and "partial" or status
    section.detail=detail;section.omitted=budget.omitted
    -- Failed reads do not erase the last successful observation.
    if safe~=nil then section.data=safe;section.observedAt=now end
    c.lastSeen=now
end
function O.Event(kind, payload)
    local c=O.Character();if not c or not O.db.settings.events then return end
    -- Never silently overwrite unsent history. Surface the overflow count.
    if #c.events>=10000 then c.droppedEvents=c.droppedEvents+1;if c.droppedEvents==1 then print("DuckMoo Omni Capture: event journal full. New events paused; snapshots continue. Existing history has been preserved.") end;return end
    c.sequence=c.sequence+1
    c.events[#c.events+1]={id=c.sequence,kind=kind,at=GetServerTime(),data=O.Safe(payload)}
end

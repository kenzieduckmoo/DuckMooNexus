local _,F=...
local tiers={[1]='Classic',[2]='The Burning Crusade',[3]='Wrath of the Lich King',[4]='Cataclysm',[5]='Mists of Pandaria',[6]='Warlords of Draenor',[7]='Legion',[8]='Battle for Azeroth',[9]='Shadowlands',[10]='Dragonflight',[11]='The War Within',[12]='Midnight'}
local capitals={[84]=true,[85]=true,[87]=true,[88]=true,[89]=true,[90]=true,[103]=true,[110]=true,[111]=true,[125]=true,[126]=true,[627]=true,[628]=true,[1161]=true,[1165]=true,[1670]=true,[2112]=true,[2339]=true,[2393]=true}
-- ATT can group outdoor zones by geography instead of expansion. Use map
-- ancestry for these groups, after preferring explicit ATT expansion metadata.
local mapTiers={[12]=1,[13]=1,[101]=2,[113]=3,[424]=5,[572]=6,[619]=7,[875]=8,[876]=8,[1550]=9,[1978]=10,[2274]=11,
    [194]=4,[174]=4,[198]=4,[203]=4,[204]=4,[201]=4,[205]=4,[207]=4,[241]=4,[249]=4,[244]=4,[245]=4,[338]=4,
    [97]=2,[106]=2,[94]=2,[95]=2,[122]=2,[407]=4,[504]=5,[554]=5,[646]=7,[650]=7,[830]=7,[905]=7,[1355]=8,[1462]=8,[1961]=9,[2029]=10,[2133]=10,[2200]=10,[2248]=11,[2214]=11,[2215]=11,[2255]=11,[2346]=11,[2371]=11,[2369]=11,[2472]=11,[2537]=12,[2424]=12,[2432]=12,[2395]=12,[2393]=12,[2437]=12,[2405]=12,[2413]=12,[2536]=12,[2444]=12,[2512]=12,[2509]=12,[2613]=12,[107]=2}
local function numberTier(value)
    if type(value)=='number' then local tier=math.floor(value);if tiers[tier]then return tier end end
end
function F.ATTNodeTier(node,fallback)
    local seen={};local depth=0
    while type(node)=='table' and not seen[node] and depth<20 do
        seen[node]=true;depth=depth+1
        local tier=numberTier(node.tierID) or numberTier(node.expansionID)
        if tier then return tier end
        node=node.sourceParent or node.parent
    end
    return numberTier(fallback)
end
local mapCache,mapReader={},nil
function F.ATTMapInfo(mapID)
    local reader=C_Map and C_Map.GetMapInfo
    if reader~=mapReader then mapCache={};mapReader=reader end
    if mapCache[mapID]then return mapCache[mapID]end
    local map=F.Safe(reader,mapID)
    -- Retry unready map data later; only static usable metadata is cached.
    if map and map.mapType then mapCache[mapID]=map end
    return map
end
function F.ATTMapTier(mapID)
    local seen={}
    while mapID and not seen[mapID]do
        seen[mapID]=true
        if mapTiers[mapID]then return mapTiers[mapID]end
        local map=F.ATTMapInfo(mapID)
        mapID=map and map.parentMapID
    end
end
-- Build labels/paths only for retained quest rows or an actual failure.
function F.ATTPath(frame)
    local parts={};local size=0
    while frame and size<1000 do
        local n=frame.node
        local label=F.ATTLabel(n) or (F.ReadATT(n,'mapID') and 'mapID '..F.ReadATT(n,'mapID')) or (F.ReadATT(n,'headerID') and 'headerID '..F.ReadATT(n,'headerID')) or (F.ReadATT(n,'questID') and 'questID '..F.ReadATT(n,'questID')) or 'group'
        parts[#parts+1]=label;size=size+#label+3;frame=frame.parent
    end
    local ordered={};for i=#parts,1,-1 do ordered[#ordered+1]=parts[i]end
    return table.concat(ordered,' > '):sub(-900)
end
local journalCache
local function journalMetadata()
    local selected=F.Safe(EJ_GetCurrentTier);local num=F.Safe(EJ_GetNumTiers) or 0
    local now=F.Now()
    if journalCache and journalCache.reader==EJ_GetInstanceByIndex and journalCache.selector==EJ_SelectTier and journalCache.num==num and now-journalCache.at<300 then return journalCache.kinds,journalCache.tiers end
    local kinds,tiers={},{}
    if selected and num>0 then
        for tier=1,num do
            F.Safe(EJ_SelectTier,tier)
            for _,raid in ipairs({false,true})do
                for i=1,100 do
                    local id=F.Safe(EJ_GetInstanceByIndex,i,raid);if not id then break end
                    kinds[id]=raid and 'raid' or 'dungeon';tiers[id]=tier
                end
            end
        end
        F.Safe(EJ_SelectTier,selected)
        if next(kinds)then journalCache={reader=EJ_GetInstanceByIndex,selector=EJ_SelectTier,num=num,at=now,kinds=kinds,tiers=tiers}end
    end
    return kinds,tiers
end
function F.ATTExpansionLabel(row,zone)
    local tier=numberTier(row.tier)
    if row.expansion and row.expansion~='Expansion not supplied' and row.expansion~='Unknown expansion'then return row.expansion end
    if not tier and zone then tier=F.ATTMapTier(row.mapID)end
    return tiers[tier] or 'Unknown expansion'
end
function F.IsLegacyATT(row)
    local tier=numberTier(row.tier)
    if not tier then for id,name in pairs(tiers)do if row.expansion==name then tier=id;break end end end
    return tier~=nil and tier<=10
end
-- Compare exact completion fractions, rather than rounded display values.
-- Pick a tied minimum only when a snapshot is captured or first upgraded.
-- Encounter Journal ID; exclude only from ATDART, not the captured rankings.
local atdartExcluded={[1209]=true} -- Dawn of the Infinite
local function excludedATDART(row)return row and atdartExcluded[tonumber(row.instanceID)]end
function F.SelectATDART(snapshot,random)
    local candidates={};local best
    for _,row in ipairs(snapshot.completion or {})do
        if not excludedATDART(row) and F.IsLegacyATT(row) and type(row.total)=='number' and row.total>0 and type(row.progress)=='number' and row.progress>=0 and row.progress<=row.total then
            local compare=best and row.progress*best.total-best.progress*row.total or -1
            if compare<0 then best=row;candidates={row}
            elseif compare==0 then candidates[#candidates+1]=row end
        end
    end
    snapshot.targetEvaluated=true
    snapshot.atdart=nil
    if #candidates>0 then snapshot.atdart=F.Clean(candidates[(random or math.random)(#candidates)])end
    return snapshot.atdart
end
function F.GetATDART(snapshot)
    -- Old captures may contain alternate/reference instance groups. Do not
    -- present their cached percentages as if they were main-list completion.
    if (snapshot.schema or 0)<4 then return nil end
    -- Repair an already-saved Dawn target, including offline captures, once.
    -- Other saved targets keep their existing random tie selection.
    if not snapshot.targetEvaluated or excludedATDART(snapshot.atdart)then F.SelectATDART(snapshot)end
    return snapshot.atdart
end
function F.ATTStatus()
    local app=_G.AllTheThings
    if type(app)~='table' then return nil,'Enable All The Things for this character in the AddOns menu, then reload your UI. The folio works without it.' end
    local prime=app.Windows and app.Windows.Prime
    if not prime or not prime.data then return nil,'All The Things is enabled but its collection data is not ready. Open ATT, let its scan finish, then click Refresh.' end
    return app,nil,prime.data
end
function F.RefreshATT()
    if F.Safe(InCombatLockdown)then F.attMessage='Refresh after combat.';F.DrawATTIfShown();return end
    if not F.DebugReady()then return end
    local app,message,root=F.ATTStatus()
    if not app then F.attMessage=message;F.DrawATTIfShown();return end
    if F.attBusy then return end
    local guid=F.current;local c=F.db.characters[guid]
    local H=app.HeaderConstants or {}
    -- ATT repeats instance IDs in achievements, professions, seasonal shortcuts
    -- and difficulty/reference groups. Only its actual Dungeons & Raids section
    -- owns the completion shown in the main list.
    local instanceRoot,zoneRoot
    for _,node in ipairs(root.g or {})do
        if H.DUNGEONS_AND_RAIDS and node.headerID==H.DUNGEONS_AND_RAIDS then instanceRoot=node end
        if H.OUTDOOR_ZONES and node.headerID==H.OUTDOOR_ZONES and not node.sourceIgnored and not node.dynamicID and not node.dynamic_withsubgroups then zoneRoot=node end
    end
    if not instanceRoot then
        F.attBusy=false;F.attMessage='Open ATT Dungeons & Raids, then Refresh to capture instance counts.';F.DrawATTIfShown();return
    end
    F.attBusy=true;F.attMessage='Reading ATT collection opportunities...';F.DrawATTIfShown()
    local run={};F.attRun=run
    -- Prefer ATT's actual outdoor category over duplicate achievement/profession
    -- and dynamic-window references. Unknown layouts keep the broad fallback.
    local stack=zoneRoot and {{node=instanceRoot},{node=zoneRoot}} or {{node=root}};local visited={};local canonicalVisited={};local instances={};local ambiguous={};local zones={};local count=0
    local questDebug={enabled=not not F.db.settings.questDebug,used=0}
    F.activeQuestDebug=questDebug
    local context={stage='starting capture'}
    local started=F.Safe(GetTimePreciseSec) or F.Now()
    local journalKinds,journalTiers
    local intrinsicTiers={};local batches,pruned=0,0;local activeFrame
    local clock=type(debugprofilestop)=='function' and debugprofilestop or nil
    local step
    local lastDraw=started
    local function work()
            if not journalKinds then context.stage='reading Encounter Journal metadata';journalKinds,journalTiers=journalMetadata()end
            local elapsed=(F.Safe(GetTimePreciseSec) or F.Now())-started
            if elapsed>180 or count>2000000 then error('Capture exceeded its bounded work limit; previous snapshot retained. Stop ATT activity and retry.')end
            local budget=0;local slice=clock and clock();batches=batches+1
            while #stack>0 and budget<(clock and 4000 or 350) do
                local frame=table.remove(stack)
                -- Resume one child at a time, so a huge lazy g list does not
                -- allocate the entire work stack in one unbudgeted loop.
                if frame.children then
                    local cursor=frame;local child=cursor.children[cursor.index];cursor.index=cursor.index-1
                    if cursor.index>0 then stack[#stack+1]=cursor end
                    frame={node=child,parent=cursor.parent,kind=cursor.kind,tier=cursor.tier,zone=cursor.zone,inInstances=cursor.inInstances,reference=cursor.reference,instanceParent=cursor.instanceParent}
                end
                local n=frame.node
                activeFrame=frame;context={stage='reading ATT node',visited=count+1,mapID=frame.zone}
                budget=budget+1;count=count+1
                if type(n)=='table' then
                    local inInstances=frame.inInstances or n==instanceRoot
                    local reference=frame.reference or n.sourceIgnored or n.dynamicID or n.dynamic_withsubgroups
                    local seen=inInstances and not reference and not frame.instanceParent and canonicalVisited or visited
                    if not seen[n]then
                    seen[n]=true
                    local kind=frame.kind;local own=intrinsicTiers[n]
                    if own==nil then own=F.ATTNodeTier(n) or false;intrinsicTiers[n]=own end
                    local tier=own or numberTier(frame.tier)
                    context.questID=F.ReadATT(n,'questID');context.instanceID=F.ReadATT(n,'instanceID')
                    if H.RAIDS and n.headerID==H.RAIDS then kind='raid' end
                    if H.DUNGEONS and n.headerID==H.DUNGEONS then kind='dungeon' end
                    local zone=frame.zone
                    if n.instanceID then
                        if not journalKinds[n.instanceID] then journalCache=nil end
                        kind=journalKinds[n.instanceID] or kind;tier=tier or journalTiers[n.instanceID]
                        zone=nil
                        local total,progress=n.total,n.progress
                        if inInstances and not reference and not frame.instanceParent and kind and type(total)=='number' and type(progress)=='number' and total>0 and progress>=0 and progress<=total and n.visible~=false and tier and tier<=10 then
                            local key=kind..':'..n.instanceID
                            local old=instances[key];local missing=total-progress
                            if old and(old.total~=total or old.progress~=progress)then ambiguous[key]=true end
                            if not old then instances[key]={name=F.Clean(n.text) or ('Instance '..n.instanceID),missing=missing,total=total,progress=progress,kind=kind,expansion=tiers[tier],tier=tier,instanceID=n.instanceID}end
                        end
                    elseif not kind and n.mapID then
                        local map=F.ATTMapInfo(n.mapID)
                        if map and map.mapType==3 then
                            zone=not capitals[n.mapID] and n.mapID or nil
                            if zone then
                                local zoneTier=tier or F.ATTMapTier(zone)
                                if not zones[zone]then zones[zone]={name=map.name,expansion=tiers[zoneTier] or 'Unknown expansion',tier=zoneTier,quests={},missing=0,mapID=zone}
                                elseif zoneTier and not zones[zone].tier then zones[zone].tier=zoneTier;zones[zone].expansion=tiers[zoneTier]end
                            end
                        end
                    end
                    if zone and n.questID then
                        local z=zones[zone];local eligible;local status
                        if not F.IsATTQuest(n)then status='excluded: not a quest object'
                        elseif n.collected then status='excluded: collected'
                        elseif n.visible==false then status='excluded: hidden'
                        elseif not n.collectible then status='excluded: not collectible'
                        else
                            eligible=not app.GroupFilter or F.Safe(app.GroupFilter,n)
                            if not eligible then status='excluded: group filter'
                            elseif z and z.quests[n.questID]then status='duplicate'
                            else status='counted';if z then z.quests[n.questID]=true;z.missing=z.missing+1 end end
                        end
                        if z then context.stage='recording quest diagnostics';F.RecordQuestDebug(app,z,n,status,nil,reference,eligible,questDebug,frame)end
                    end
                    -- A classified instance owns aggregate totals. Its children
                    -- cannot be canonical instances or outdoor quest zones.
                    if n.instanceID and kind then pruned=pruned+1
                    elseif n.visible~=false then
                        local children=n.g or {}
                        if #children>0 then stack[#stack+1]={children=children,index=#children,kind=kind,tier=tier,zone=zone,parent=frame,inInstances=inInstances,reference=reference,instanceParent=frame.instanceParent or n.instanceID}end
                    end
                    end
                end
                if clock and budget%16==0 and clock()-slice>=4 then break end
            end
        run.nodes=count;run.pending=#stack;run.elapsed=math.max(0,(F.Safe(GetTimePreciseSec) or F.Now())-started)
        if #stack>0 then
            local now=F.Safe(GetTimePreciseSec) or F.Now()
            if now-lastDraw>=1 then lastDraw=now;F.attMessage=string.format('Reading ATT: %d nodes, %d branches queued, %.1fs elapsed. Click Stop to retain the previous snapshot.',count,#stack,run.elapsed);F.DrawATTIfShown()end
            C_Timer.After(.01,step);return
        end
        context.stage='finishing capture'
        local result={schema=6,seenAt=F.Now(),mode=F.Clean(root.modeString) or 'ATT active profile',attVersion=F.Safe(C_AddOns and C_AddOns.GetAddOnMetadata,'AllTheThings','Version'),questDebug=questDebug.enabled,dungeons={},raids={},zones={},completion={},instanceSource=instanceRoot and'main Dungeons & Raids'or'unavailable',ambiguousInstances=0}
        result.questDebug=not not questDebug.usedDetailed;result.questDebugStopped=questDebug.stopped or nil
        result.scan={scope=zoneRoot and 'main instances + outdoor zones' or 'full-tree fallback',nodes=count,batches=batches,prunedInstances=pruned,elapsedSeconds=math.max(0,(F.Safe(GetTimePreciseSec) or F.Now())-started),detailedDebug=result.questDebug}
        for key,r in pairs(instances) do
            if ambiguous[key]then result.ambiguousInstances=result.ambiguousInstances+1
            else
            result.completion[#result.completion+1]=r
            if r.missing>0 then table.insert(r.kind=='raid' and result.raids or result.dungeons,r)end
            end
        end
        table.sort(result.completion,function(a,b)return a.kind..':'..a.instanceID<b.kind..':'..b.instanceID end)
        F.SelectATDART(result)
        for _,r in pairs(zones) do if r.missing>0 then r.quests=nil;result.zones[#result.zones+1]=r end end
        for _,list in ipairs({result.dungeons,result.raids,result.zones}) do table.sort(list,function(a,b)if a.missing~=b.missing then return a.missing>b.missing end;return a.name<b.name end) end
        if F.db.characters[guid] then F.db.characters[guid].att=result end
        run.done=true;F.attBusy=false;F.attRun=nil;F.activeQuestDebug=nil;F.attMessage=nil;F.Safe(F.DrawATTIfShown)
    end
    local function fail(err)
        run.done=true
        context.path=activeFrame and F.Safe(F.ATTPath,activeFrame)
        c.captureError={seenAt=F.Now(),addonVersion=F.version,attVersion=F.Safe(C_AddOns and C_AddOns.GetAddOnMetadata,'AllTheThings','Version'),message=tostring(err):sub(1,2000),context=F.Clean(context)}
        F.attBusy=false;F.attRun=nil;F.activeQuestDebug=nil;F.attMessage='Collector capture failed; previous snapshot retained. /folio att error shows the actual error.'
        print('Folio ATT capture error: '..c.captureError.message);F.Safe(F.DrawATTIfShown)
    end
    step=function()
        if run.cancelled or run.done or F.attRun~=run then return end
        -- Final sorting, lazy mode/version reads and timer rescheduling must be
        -- protected too, or a callback error leaves Reading stuck indefinitely.
        local ok,err=pcall(work)
        if not ok then fail(err)end
    end
    local scheduled,err=pcall(C_Timer.After,.01,step)
    if not scheduled then fail(err)end
end
function F.OpenATT()
    local app=_G.AllTheThings
    if type(app)=='table' and type(app.ToggleMainList)=='function' then F.Safe(app.ToggleMainList) end
end


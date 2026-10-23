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
function F.ATTMapTier(mapID)
    local seen={}
    while mapID and not seen[mapID]do
        seen[mapID]=true
        if mapTiers[mapID]then return mapTiers[mapID]end
        local map=F.Safe(C_Map and C_Map.GetMapInfo,mapID)
        mapID=map and map.parentMapID
    end
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
function F.SelectATDART(snapshot,random)
    local candidates={};local best
    for _,row in ipairs(snapshot.completion or {})do
        if F.IsLegacyATT(row) and type(row.total)=='number' and row.total>0 and type(row.progress)=='number' and row.progress>=0 and row.progress<=row.total then
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
    if not snapshot.targetEvaluated then F.SelectATDART(snapshot)end
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
    local app,message,root=F.ATTStatus()
    if not app then F.attMessage=message;F.DrawIfShown();return end
    if F.attBusy then return end
    F.attBusy=true;F.attMessage='Reading ATT collection opportunities...';F.DrawIfShown()
    local guid=F.current;local c=F.db.characters[guid]
    local stack={{node=root}};local visited={};local instances={};local zones={};local count=0
    local H=app.HeaderConstants or {}
    local journalKinds={};local journalTiers={}
    -- Encounter Journal IDs match ATT instanceID. Restore the user's tier.
    local selected=F.Safe(EJ_GetCurrentTier)
    if selected then
        for tier=1,(F.Safe(EJ_GetNumTiers) or 0) do
            F.Safe(EJ_SelectTier,tier)
            for _,isRaid in ipairs({false,true}) do
                local i=1
                while i<=100 do
                    local id=F.Safe(EJ_GetInstanceByIndex,i,isRaid)
                    if not id then break end
                    journalKinds[id]=isRaid and 'raid' or 'dungeon';journalTiers[id]=tier;i=i+1
                end
            end
        end
        F.Safe(EJ_SelectTier,selected)
    end
    local function step()
        local ok,err=pcall(function()
            local budget=0
            while #stack>0 and budget<350 do
                local frame=table.remove(stack);local n=frame.node
                budget=budget+1;count=count+1
                if type(n)=='table' and not visited[n] then
                    visited[n]=true
                    local kind=frame.kind;local tier=F.ATTNodeTier(n,frame.tier)
                    if H.RAIDS and n.headerID==H.RAIDS then kind='raid' end
                    if H.DUNGEONS and n.headerID==H.DUNGEONS then kind='dungeon' end
                    local zone=frame.zone
                    if n.instanceID then
                        kind=journalKinds[n.instanceID] or kind;tier=tier or journalTiers[n.instanceID]
                        zone=nil
                        local total,progress=n.total,n.progress
                        if kind and type(total)=='number' and type(progress)=='number' and total>0 and progress>=0 and progress<=total and n.visible~=false and tier and tier<=10 then
                            local key=kind..':'..n.instanceID
                            local old=instances[key];local missing=total-progress
                            if not old or missing>old.missing then
                                instances[key]={name=F.Clean(n.text) or ('Instance '..n.instanceID),missing=missing,total=total,progress=progress,kind=kind,expansion=tiers[tier],tier=tier,instanceID=n.instanceID}
                            end
                        end
                    elseif not kind and n.mapID then
                        local map=F.Safe(C_Map and C_Map.GetMapInfo,n.mapID)
                        if map and map.mapType==3 then
                            zone=not capitals[n.mapID] and n.mapID or nil
                            if zone then
                                local zoneTier=tier or F.ATTMapTier(zone)
                                if not zones[zone]then zones[zone]={name=map.name,expansion=tiers[zoneTier] or 'Unknown expansion',tier=zoneTier,quests={},missing=0,mapID=zone}
                                elseif zoneTier and not zones[zone].tier then zones[zone].tier=zoneTier;zones[zone].expansion=tiers[zoneTier]end
                            end
                        end
                    end
                    if zone and n.questID and not n.collected and n.visible~=false and n.collectible then
                        local eligible=not app.GroupFilter or F.Safe(app.GroupFilter,n)
                        local z=zones[zone]
                        if eligible and z and not z.quests[n.questID] then z.quests[n.questID]=true;z.missing=z.missing+1 end
                    end
                    if n.visible~=false then
                        for _,child in ipairs(n.g or {}) do stack[#stack+1]={node=child,kind=kind,tier=tier,zone=zone} end
                    end
                end
            end
        end)
        if not ok then
            F.attBusy=false;F.attMessage='ATT data could not be read by this version of the adapter. Update ATT and try Refresh. No collection data was changed.';F.DrawIfShown();return
        end
        if #stack>0 then C_Timer.After(.01,step);return end
        local result={schema=3,seenAt=F.Now(),mode=F.Clean(root.modeString) or 'ATT active profile',dungeons={},raids={},zones={},completion={}}
        for _,r in pairs(instances) do
            result.completion[#result.completion+1]=r
            if r.missing>0 then table.insert(r.kind=='raid' and result.raids or result.dungeons,r)end
        end
        table.sort(result.completion,function(a,b)return a.kind..':'..a.instanceID<b.kind..':'..b.instanceID end)
        F.SelectATDART(result)
        for _,r in pairs(zones) do if r.missing>0 then r.quests=nil;result.zones[#result.zones+1]=r end end
        for _,list in ipairs({result.dungeons,result.raids,result.zones}) do table.sort(list,function(a,b)if a.missing~=b.missing then return a.missing>b.missing end;return a.name<b.name end) end
        if F.db.characters[guid] then F.db.characters[guid].att=result end
        F.attBusy=false;F.attMessage=nil;F.DrawIfShown()
    end
    C_Timer.After(.01,step)
end
function F.OpenATT()
    local app=F.ATTStatus()
    if app and type(app.ToggleMainList)=='function' then F.Safe(app.ToggleMainList) end
end

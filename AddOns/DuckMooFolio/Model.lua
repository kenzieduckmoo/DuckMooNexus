local _,F=...
F.Model={};local M=F.Model
M.Healers={PRIEST=true,SHAMAN=true,PALADIN=true,DRUID=true,MONK=true,EVOKER=true}
M.Tanks={WARRIOR=true,PALADIN=true,DRUID=true,DEATHKNIGHT=true,MONK=true,DEMONHUNTER=true}
function M.Level(c)
    if c.level and c.maxLevel and c.level>=c.maxLevel then return tostring(c.level) end
    local p=c.xpMax and c.xpMax>0 and math.min(.9999,math.max(0,(c.xp or 0)/c.xpMax)) or 0
    return string.format('%d.%02d',c.level or 0,math.floor(p*100))
end
function M.LevelValue(c) return (c.level or 0)+(c.xpMax and c.xpMax>0 and math.min(.9999,(c.xp or 0)/c.xpMax) or 0) end
function M.Rested(c)
    if c.maxLevel and (c.level or 0)>=c.maxLevel then return '-' end
    if not c.xpMax or c.xpMax<=0 then return '?' end
    return string.format('%.0f%%',100*(c.rested or 0)/c.xpMax)
end
function M.Tags(text)
    local out={}
    for tag in (text or ''):gmatch('[^,]+') do
        tag=tag:match('^%s*(.-)%s*$'):sub(1,60)
        if tag~='' then out[tag:lower()]=tag end
    end
    return out
end
function M.TagText(c)
    local out={};for _,tag in pairs(c.tags or {}) do out[#out+1]=tag end;table.sort(out);return table.concat(out,', ')
end
function M.ReputationText(r)
    if not r then return 'Not recorded' end
    if r.renown then return 'Renown '..r.renown end
    local standing=_G['FACTION_STANDING_LABEL'..(r.reaction or 4)] or tostring(r.reaction or '?')
    local amount=(r.value or 0)-(r.min or 0);local max=(r.max or 0)-(r.min or 0)
    return standing..(max>0 and string.format(' %d / %d',amount,max) or '')
end
function M.ReputationValue(r)
    if not r then return -math.huge end
    if r.renown then return r.renown*100000+(r.value or 0) end
    return (r.reaction or 0)*1000000+(r.value or 0)
end
function M.Options(db,kind,profession)
    local found={}
    for _,c in pairs(db.characters) do
        if kind=='class' then if c.class then found[c.class]=c.className or c.class end
        elseif kind=='realm' then found[c.realm or '?']=c.realm or '?'
        elseif kind=='tag' then for id,t in pairs(c.tags or {}) do found[id]=t end
        elseif kind=='reputation' then for id,r in pairs(c.reputations or {}) do found[id]=r.name end
        elseif kind=='profession' then for _,p in pairs(c.professions or {}) do found[p.name]=p.name end
        elseif kind=='expansion' then
            for _,p in pairs(c.professions or {}) do
                if not profession or p.name==profession then
                    for id,e in pairs(p.expansions or {}) do found[id]=e.name end
                end
            end
        end
    end
    local out={};for id,name in pairs(found) do out[#out+1]={id=id,name=name} end
    table.sort(out,function(a,b) return a.name<b.name end);return out
end
function M.Matches(c,f)
    f=f or {}
    if f.class and c.class~=f.class then return false end
    if f.faction and c.faction~=f.faction then return false end
    if f.realm and c.realm~=f.realm then return false end
    if f.region and c.realmRegion~=f.region then return false end
    if f.role=='HEALER' and not M.Healers[c.class] then return false end
    if f.role=='TANK' and not M.Tanks[c.class] then return false end
    if f.tag and not (c.tags and c.tags[f.tag]) then return false end
    if f.reputation and not (c.reputations and c.reputations[f.reputation]) then return false end
    if f.profession or f.expansion then
        local match=false
        for _,p in pairs(c.professions or {}) do
            if (not f.profession or p.name==f.profession) and (not f.expansion or p.expansions and p.expansions[f.expansion]) then match=true end
        end
        if not match then return false end
    end
    local searchable=(c.name or '')..' '..(c.realm or '')..' '..(c.specName or '')..' '..M.TagText(c)
    for _,note in pairs(c.notes or {}) do searchable=searchable..' '..note end
    return searchable:lower():find((f.search or ''):lower(),1,true)~=nil
end
function M.Roster(db,f)
    f=f or {};local out={}
    for guid,c in pairs(db.characters) do if M.Matches(c,f) then out[#out+1]={guid=guid,c=c} end end
    table.sort(out,function(a,b)
        local x,y=a.c,b.c
        if f.role and (x.role==f.role)~=(y.role==f.role) then return x.role==f.role end
        if f.reputation then
            local av,bv=M.ReputationValue(x.reputations[f.reputation]),M.ReputationValue(y.reputations[f.reputation])
            if av~=bv then return av>bv end
        end
        if f.sort=='name' then if x.name~=y.name then return x.name<y.name end
        elseif f.sort=='ilvl' then if (x.ilvl or -1)~=(y.ilvl or -1) then return (x.ilvl or -1)>(y.ilvl or -1) end
        elseif f.sort=='rested' then
            local av,bv=(x.rested or 0)/math.max(1,x.xpMax or 1),(y.rested or 0)/math.max(1,y.xpMax or 1)
            if av~=bv then return av>bv end
        else if M.LevelValue(x)~=M.LevelValue(y) then return M.LevelValue(x)>M.LevelValue(y) end end
        if x.name~=y.name then return x.name<y.name end;return a.guid<b.guid
    end)
    return out
end
function M.Grouped(entries,collapsed)
    local groups,keys={},{ }
    for _,e in ipairs(entries) do
        local key=e.c.realm or '?'
        if not groups[key] then groups[key]={};keys[#keys+1]=key end
        groups[key][#groups[key]+1]=e
    end
    table.sort(keys)
    local out={}
    for _,key in ipairs(keys) do
        out[#out+1]={header=key,count=#groups[key]}
        if not collapsed[key] then for _,e in ipairs(groups[key]) do out[#out+1]=e end end
    end
    return out
end
function M.Census(db)
    local result={total=0,faction={},race={},class={},profession={},band={},realm={},tag={}}
    local function add(t,k) t[k]=(t[k] or 0)+1 end
    for _,c in pairs(db.characters) do
        result.total=result.total+1
        add(result.faction,c.faction or 'Unknown');add(result.race,c.race or 'Unknown');add(result.class,c.className or c.class or 'Unknown')
        add(result.realm,c.realm or 'Unknown')
        local n=math.floor((c.level or 1)/10)*10
        add(result.band,n==0 and '1-9' or (n>=90 and tostring(n)..'s' or tostring(n)..'-'..tostring(n+9)))
        for id,p in pairs(c.professions or {}) do if (p.id or id)~=794 then add(result.profession,p.name) end end
        for _,tag in pairs(c.tags or {}) do add(result.tag,tag) end
    end
    return result
end
function M.Plain(s) return (tostring(s or ''):gsub('|','||')) end
M.CommonTags={'Main','Tank main','Healer main','Dual gatherer','Speed druid','Legacy farmer','Delves','Dungeon runner','Raid character','Timewalking','PvP','Leveling','Bank alt','Auction house','Crafter','Concentration alt','Recipe collector','Transmog collector','Mount farmer','Pet collector','Reputation farmer','Quest completion','Cloth gear','Bolt maker','Parked alt','Roleplay'}
local oce={"Saurfang","Aman'Thul","Khaz'goroth","Barthilas","Caelestrasz","Dath'Remar","Nagrand","Dreadmaul","Frostmourne","Gundrak","Jubei'thos","Thaurissan"}
local latam={'Drakkari',"Quel'Thalas",'Ragnaros'}
local brazil={'Gallywix','Goldrinn','Nemesis','Tol Barad','Azralon'}
function M.RealmKey(name) return ((name or ''):lower():gsub('[%s%p]','')) end
local realmGroups={}
for _,list in ipairs({{oce,'NA-OCE'},{latam,'NA-LATAM'},{brazil,'NA-BR'}}) do for _,name in ipairs(list[1]) do realmGroups[M.RealmKey(name)]=list[2] end end
function M.RealmRegion(name,region)
    if region==3 then return 'EU' elseif region==2 then return 'KR' elseif region==4 then return 'TW' elseif region==5 then return 'CN' end
    return realmGroups[M.RealmKey(name)] or 'NA-US'
end
function M.IsSecondary(p,id) return (p.id or id)==185 or (p.id or id)==356 end
function M.Spec(c) return ((c.level or 0)>=81 and c.heroSpec and c.heroSpec~='' and (c.heroSpec..' ') or '')..(c.specName or 'No spec recorded') end
function M.Display(s)
    return (tostring(s or ''):gsub('|c[fF][fF][fF][fF][fF]7[dD]01',''):gsub('|c%x%x%x%x%x%x%x%x',''):gsub('|r',''):gsub('|H.-|h(.-)|h','%1'):gsub('|T.-|t',''):gsub('|A.-|a',''))
end

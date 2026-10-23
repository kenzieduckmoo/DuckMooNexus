local _,F=...
local M=F.Model
-- Expansion profession skill IDs, checked against ATT's skill conversion data.
-- Labels are replaced by localized Blizzard profession data when available.
M.CoverageExpansions={'Classic','The Burning Crusade','Wrath of the Lich King','Cataclysm','Mists of Pandaria','Warlords of Draenor','Legion','Battle for Azeroth','Shadowlands','Dragonflight','The War Within','Midnight'}
M.CoverageProfessions={
    {id=171,name='Alchemy',skills={2485,2484,2483,2482,2481,2480,2479,2478,2750,2823,2871,2906}},
    {id=164,name='Blacksmithing',skills={2477,2476,2475,2474,2473,2472,2454,2437,2751,2822,2872,2907}},
    {id=185,name='Cooking',skills={2548,2547,2546,2545,2544,2543,2542,2541,2752,2824,2873,2908}},
    {id=333,name='Enchanting',skills={2494,2493,2492,2491,2489,2488,2487,2486,2753,2825,2874,2909}},
    {id=202,name='Engineering',skills={2506,2505,2504,2503,2502,2501,2500,2499,2755,2827,2875,2910}},
    {id=356,name='Fishing',skills={2592,2591,2590,2589,2588,2587,2586,2585,2754,2826,2876,2911}},
    {id=182,name='Herbalism',skills={2556,2555,2554,2553,2552,2551,2550,2549,2760,2832,2877,2912}},
    {id=773,name='Inscription',skills={2514,2513,2512,2511,2510,2509,2508,2507,2756,2828,2878,2913}},
    {id=755,name='Jewelcrafting',skills={2524,2523,2522,2521,2520,2519,2518,2517,2757,2829,2879,2914}},
    {id=165,name='Leatherworking',skills={2532,2531,2530,2529,2528,2527,2526,2525,2758,2830,2880,2915}},
    {id=186,name='Mining',skills={2572,2571,2570,2569,2568,2567,2566,2565,2761,2833,2881,2916}},
    {id=393,name='Skinning',skills={2564,2563,2562,2561,2560,2559,2558,2557,2762,2834,2882,2917}},
    {id=197,name='Tailoring',skills={2540,2539,2538,2537,2536,2535,2534,2533,2759,2831,2883,2918}},
}
function F.RecordProfessionCatalog(parent,info)
    if not info or not info.professionID or info.professionID==parent then return end
    local known=false;for _,p in ipairs(M.CoverageProfessions)do if p.id==parent then known=true;break end end
    if not known then return end
    F.db.professionCatalog=F.db.professionCatalog or {}
    local p=F.db.professionCatalog[parent] or {expansions={}};F.db.professionCatalog[parent]=p
    p.name=info.parentProfessionName or p.name
    p.expansions[info.professionID]={name=info.professionName,expansionName=info.expansionName}
end
function F.UpdateProfessionCatalog()
    local api=C_TradeSkillUI
    if not api or not api.GetProfessionInfoBySkillLineID then return end
    for _,p in ipairs(M.CoverageProfessions)do
        for _,id in ipairs(p.skills)do
            local info=F.Safe(api.GetProfessionInfoBySkillLineID,id)
            if info then F.RecordProfessionCatalog(info.parentProfessionID or p.id,info)end
        end
    end
end
-- Gathering has no recipe window to open. Read owned profession skill lines
-- directly when Blizzard supplies usable ranks; missing API values stay unknown.
function F.ScanProfessionCoverage(c)
    local api=C_TradeSkillUI
    if not api or not api.GetProfessionInfoBySkillLineID then return end
    for _,definition in ipairs(M.CoverageProfessions)do
        local p=c.professions[definition.id]
        if p then
            p.expansionChecks=p.expansionChecks or {};p.expansions=p.expansions or {}
            for _,id in ipairs(definition.skills)do
                local info=F.Safe(api.GetProfessionInfoBySkillLineID,id)
                if info and info.professionID==id and info.parentProfessionID==definition.id then
                    F.RecordProfessionCatalog(definition.id,info)
                    local rank,max=info.skillLevel,info.maxSkillLevel
                    if type(rank)=='number' and rank>=0 and (rank>0 or type(max)=='number' and max>0)then
                        p.expansionChecks[id]=F.Now()
                        if rank>0 or p.expansions[id]then
                            local row=p.expansions[id] or {};p.expansions[id]=row
                            row.id=id;row.name=info.professionName or row.name or 'Expansion skill';row.rank=rank;row.max=max or row.max;row.seenAt=F.Now()
                        end
                    end
                end
            end
        end
    end
end
function M.ProfessionCoverage(db)
    local rows={};local summary={covered=0,gap=0,needs_scan=0,unknownCharacters=0}
    for _,c in pairs(db.characters)do if not c.profSeenAt then summary.unknownCharacters=summary.unknownCharacters+1 end end
    for _,definition in ipairs(M.CoverageProfessions)do
        local catalog=db.professionCatalog and db.professionCatalog[definition.id]
        local profession=catalog and catalog.name or definition.name
        for _,c in pairs(db.characters)do if c.professions and c.professions[definition.id] then profession=c.professions[definition.id].name or profession;break end end
        for tier,id in ipairs(definition.skills)do
            local info=catalog and catalog.expansions[id]
            local row={professionID=definition.id,profession=profession,expansionID=id,tier=tier,expansion=M.CoverageExpansions[tier],name=info and info.name or (M.CoverageExpansions[tier]..' '..profession),owners={},pending={}}
            for guid,c in pairs(db.characters)do
                local p=c.professions and c.professions[definition.id]
                if p then
                    local skill=p.expansions and p.expansions[id]
                    if skill and (skill.rank or 0)>0 then
                        row.owners[#row.owners+1]={guid=guid,c=c,rank=skill.rank,max=skill.max}
                    elseif not (p.expansionChecks and p.expansionChecks[id]) and not (skill and type(skill.rank)=='number') then
                        row.pending[#row.pending+1]={guid=guid,c=c}
                    end
                end
            end
            table.sort(row.owners,function(a,b)if a.rank~=b.rank then return a.rank>b.rank end;return a.guid<b.guid end)
            row.status=#row.owners>0 and 'covered' or #row.pending>0 and 'needs_scan' or 'gap'
            summary[row.status]=summary[row.status]+1;rows[#rows+1]=row
        end
    end
    return rows,summary
end

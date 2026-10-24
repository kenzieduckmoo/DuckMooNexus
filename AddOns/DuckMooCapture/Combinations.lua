local _, NS = ...
local M = NS.Model

-- Use a single whole-stack quality choice per required slot; never split a slot.
-- No price or quality prediction: each returned allocation is queried in-game.
function NS.ReagentCombinations(schematic, limit)
    limit = limit or 256
    if schematic.isRecraft or schematic.recipeType ~= Enum.TradeskillRecipeType.Item then return nil, 'Unsupported recipe type' end
    if schematic.quantityMin ~= schematic.quantityMax then return nil, 'Variable output quantity' end
    local slots,total={},1
    for _,slot in ipairs(schematic.reagentSlotSchematics or {}) do
        if slot.required then
            local n,options=slot.quantityRequired,slot.reagents or {}
            if type(n)~='number' or n<1 or n>1000 or n~=math.floor(n) or #options<1 or #options>3 then return nil,'Unsupported reagent choices' end
            if #options>1 and slot.dataSlotType~=Enum.TradeskillSlotDataType.ModifiedReagent then return nil,'Unqueryable reagent alternatives' end
            for _,r in ipairs(options) do if not r.itemID or r.currencyID then return nil,'Currency or unknown reagent' end end
            local count=#options
            slots[#slots+1]={slot=slot,n=n,options=options,count=count}
            total=total*count
        end
    end
    if #slots>12 then return nil,'Too many reagent slots' end
    local results,seen={},{}
    local function emit(indices)
        if #results>=limit then return end
        local allocations={}
        for k,s in ipairs(slots) do
            local index=(indices[k] or 0)+1
            allocations[#allocations+1]={reagent=M.Copy(s.options[index]),quantity=s.n,
                dataSlotIndex=s.slot.dataSlotIndex,dataSlotType=s.slot.dataSlotType}
        end
        local valid=M.ValidateReagents(schematic,allocations)
        if valid and not seen[valid.signature] then seen[valid.signature]=true;results[#results+1]=allocations end
    end
    -- Anchor both ends before any cap can favor one end of the space.
    for _,high in ipairs({false,true}) do
        local indices={};for i,s in ipairs(slots) do indices[i]=high and #s.options-1 or 0 end;emit(indices)
    end
    if total<=limit then
        for rank=0,total-1 do
            local indices={}
            local rest=rank
            for i,s in ipairs(slots) do indices[i]=rest%s.count;rest=math.floor(rest/s.count) end
            emit(indices)
        end
    else
        -- Large recipes still use a bounded, deterministic spread across whole
        -- quality choices for every slot, with both extremes already anchored.
        local primes={2,3,5,7,11,13,17,19,23,29,31,37}
        local function radical(n,base)
            local value,factor=0,1/base
            while n>0 do value=value+(n%base)*factor;n=math.floor(n/base);factor=factor/base end
            return value
        end
        for sample=1,limit*16 do
            local indices={}
            for i,s in ipairs(slots) do indices[i]=math.min(s.count-1,math.floor(radical(sample,primes[i])*s.count)) end
            emit(indices)
            if #results>=limit then break end
        end
    end
    return results,total
end

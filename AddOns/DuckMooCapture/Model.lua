local _, NS = ...
NS.Model = {}
local M = NS.Model

function M.Copy(value, depth)
    depth = depth or 0
    if issecretvalue and issecretvalue(value) then return nil end
    if depth > 12 then return nil end
    local kind = type(value)
    if kind == "number" then
        if value ~= value or value == math.huge or value == -math.huge then return nil end
        return value
    end
    if kind == "boolean" or kind == "string" then return value end
    if kind ~= "table" then return nil end
    local result = {}
    for key, child in pairs(value) do
        if type(key) == "string" or type(key) == "number" then result[key] = M.Copy(child, depth + 1) end
    end
    return result
end

function M.ValidateReagents(schematic, allocations)
    local totals, parts, items = {}, {}, {}
    for _, allocation in ipairs(allocations) do
        local reagent = allocation.reagent
        if not reagent or not reagent.itemID or reagent.currencyID then return nil, "Currency or unknown reagent costs are not supported yet." end
        if type(allocation.quantity) ~= "number" or allocation.quantity <= 0 then return nil, "Invalid allocated quantity." end
        local index = allocation.dataSlotIndex
        if type(index) ~= "number" or type(allocation.dataSlotType) ~= "number" then return nil, "Missing reagent slot identity." end
        local slot = allocation.dataSlotType .. ":" .. index
        totals[slot] = (totals[slot] or 0) + allocation.quantity
        items[reagent.itemID] = (items[reagent.itemID] or 0) + allocation.quantity
        parts[#parts+1] = slot .. ":" .. reagent.itemID .. ":" .. allocation.quantity
    end
    for _, slot in ipairs(schematic.reagentSlotSchematics or {}) do
        local key = tostring(slot.dataSlotType) .. ":" .. tostring(slot.dataSlotIndex)
        if slot.required and (totals[key] or 0) ~= slot.quantityRequired then
            return nil, "Selected setup is incomplete (slot " .. tostring(slot.dataSlotIndex) .. "); recipe data and available background previews are retained."
        end
    end
    table.sort(parts)
    return {signature=table.concat(parts, ";"), items=items}
end

function M.Store(character, record)
    character.operations = character.operations or {}
    local key = record.recipeID .. "|" .. record.reagentSignature .. "|" .. tostring(record.applyConcentration)
    character.operations[key] = record
    local count, oldestKey, oldestTime = 0, nil, math.huge
    for id, value in pairs(character.operations) do
        count = count + 1
        if (value.observedAt or 0) < oldestTime then oldestKey, oldestTime = id, value.observedAt or 0 end
    end
    if count > 300 and oldestKey then character.operations[oldestKey] = nil end
end

local _, NS = ...
local M = NS.Model
local function message(text) print("|cffc6a0eeDuckMoo Capture:|r " .. text) end
local function call(fn, ...)
    if type(fn) ~= "function" then return nil end
    local ok, value = pcall(fn, ...)
    if ok then return value end
end
local function init()
    if not DuckMooCaptureDB then DuckMooCaptureDB = {schemaVersion=1, characters={}} end
    if DuckMooCaptureDB.schemaVersion ~= 1 then return nil end
    return DuckMooCaptureDB
end
NS.Call, NS.Init = call, init
function NS.OwnProfession()
    return C_TradeSkillUI and call(C_TradeSkillUI.IsTradeSkillLinked) == false and call(C_TradeSkillUI.IsTradeSkillGuild) == false
end
function NS.Character()
    local db, guid = init(), UnitGUID("player")
    if not db or not guid then return nil end
    db.characters[guid] = db.characters[guid] or {}
    local c = db.characters[guid]
    c.name, c.realm, c.faction = UnitName("player"), GetRealmName(), UnitFactionGroup("player")
    return c
end
function NS.RememberRecipe(info, schematic)
    local c = NS.Character()
    if not c or not info or not info.recipeID then return end
    c.recipes = c.recipes or {}
    local previous = c.recipes[info.recipeID] or {}
    previous.info, previous.observedAt = M.Copy(info), GetServerTime()
    previous.profession = M.Copy(call(C_TradeSkillUI.GetProfessionInfoByRecipeID, info.recipeID)) or previous.profession
    local _, build = GetBuildInfo()
    previous.build = build
    local source = call(C_TradeSkillUI.GetRecipeSourceText, info.recipeID)
    if type(source)=="string" and source~="" then
        previous.sourceText, previous.sourceObservedAt = source, GetServerTime()
    end
    local rank=previous.profession and previous.profession.skillLevel
    if type(rank)=="number" and rank>=1 and rank<=1000 and info.relativeDifficulty~=nil then
        if previous.skillHistoryBuild~=build then previous.skillHistory={};previous.skillHistoryBuild=build end
        previous.skillHistory=previous.skillHistory or {}
        previous.skillHistory[rank]={difficulty=info.relativeDifficulty,numSkillUps=info.numSkillUps,
            canSkillUp=info.canSkillUp,observedAt=GetServerTime(),skillModifier=previous.profession.skillModifier}
    end
    previous.cooldownCaptured = false
    if type(C_TradeSkillUI.GetRecipeCooldown) == "function" then
        local ok, seconds, isDay, charges, maximum = pcall(C_TradeSkillUI.GetRecipeCooldown, info.recipeID)
        if ok then
            previous.cooldownCaptured = true
            previous.cooldown = {seconds=seconds or 0,isDay=isDay,charges=charges,maxCharges=maximum,observedAt=GetServerTime()}
        end
    end
    if schematic then previous.schematic, previous.schematicAt = M.Copy(schematic), GetServerTime() end
    c.recipes[info.recipeID] = previous
end

function NS.Capture(quiet, preset)
    local function message(text)
        local c = NS.Character()
        if c then c.captureStatus = {text=text, observedAt=GetServerTime()} end
        if not quiet then print("|cffc6a0eeDuckMoo Capture:|r " .. text) end
    end
    local db = init()
    if not db then message("Unsupported saved schema; existing data was preserved."); return end
    if InCombatLockdown() then message("Capture after leaving combat."); return end
    if not NS.OwnProfession() then return end
    local frame = ProfessionsFrame
    local page = frame and frame.CraftingPage
    local form = page and page.SchematicForm
    if not page or not page:IsShown() or not form or not form:IsShown() then message("Open a recipe in Blizzard's normal Crafting tab first."); return end
    local transaction = call(form.GetTransaction, form)
    local info = call(form.GetRecipeInfo, form)
    if not info or not info.recipeID then message("Recipe data is not ready."); return end
    local schematic = call(C_TradeSkillUI.GetRecipeSchematic, info.recipeID, false, call(form.GetCurrentRecipeLevel, form))
    NS.RememberRecipe(info, schematic)
    if not transaction then message("Recipe catalog saved; operation data is not ready."); return end
    if not info.learned then message("Capture a learned recipe on this character."); return end
    if call(transaction.IsRecraft, transaction) then message("Recrafts are not supported in this version."); return end
    local level = call(form.GetCurrentRecipeLevel, form)
    if not schematic or schematic.recipeType ~= Enum.TradeskillRecipeType.Item then message("Only ordinary item crafts are supported in this version."); return end
    if schematic.quantityMin ~= schematic.quantityMax then message("Variable base output quantities need additional modeling; no estimate was captured."); return end
    local modified = call(transaction.CreateCraftingReagentInfoTbl, transaction)
    local regular = call(transaction.CreateReagentInfoTbl, transaction)
    if preset then
        modified, regular = {}, {}
        for _, slot in ipairs(schematic.reagentSlotSchematics or {}) do
            if slot.required then
                local options = slot.reagents or {}
                local reagent = options[preset == 2 and #options or 1]
                if not reagent or not reagent.itemID or reagent.currencyID then message("Catalog saved; this recipe needs unsupported or currency reagents."); return end
                local target = slot.dataSlotType == Enum.TradeskillSlotDataType.ModifiedReagent and modified or regular
                target[#target+1] = {reagent=M.Copy(reagent),quantity=slot.quantityRequired,dataSlotIndex=slot.dataSlotIndex}
            end
        end
    end
    if not modified or not regular then message("Recipe saved; exact reagent allocations are unavailable."); return end
    local allocations = {}
    for groupIndex, group in ipairs({modified, regular}) do
        for _, value in ipairs(group) do
            local allocation = M.Copy(value)
            allocation.dataSlotType = groupIndex == 1 and Enum.TradeskillSlotDataType.ModifiedReagent or
                (allocation.reagent and allocation.reagent.currencyID and Enum.TradeskillSlotDataType.Currency or Enum.TradeskillSlotDataType.Reagent)
            allocations[#allocations+1] = allocation
        end
    end
    local validated, reason = M.ValidateReagents(schematic, allocations)
    if not validated then message(reason); return end
    local itemNames = {}
    for itemID in pairs(validated.items) do itemNames[itemID] = call(C_Item and C_Item.GetItemNameByID, itemID) end
    local guid = UnitGUID("player")
    if not guid then message("Character identity is unavailable."); return end
    db.characters[guid] = db.characters[guid] or {}
    local character = db.characters[guid]
    character.name, character.realm = UnitName("player"), GetRealmName()
    character.faction = UnitFactionGroup("player")
    local profession = call(C_TradeSkillUI.GetProfessionInfoByRecipeID, info.recipeID)
    local allocationGUID = call(transaction.GetAllocationItemGUID, transaction)
    local version, build, _, toc = GetBuildInfo()
    local captured, missing = 0, {}
    for _, apply in ipairs({false, true}) do
        local operation = call(C_TradeSkillUI.GetCraftingOperationInfo, info.recipeID, modified, allocationGUID, apply)
        local qualityID = operation and info.qualityIDs and info.qualityIDs[operation.craftingQuality]
        local output = operation and call(C_TradeSkillUI.GetRecipeOutputItemData, info.recipeID, modified, allocationGUID, qualityID)
        if operation and output and output.itemID and (not operation.isQualityCraft or qualityID) then
            local record = M.Copy({recipeID=info.recipeID, name=info.name, observedAt=GetServerTime(),
                build=build, version=version, interface=toc, recipeLevel=level, recipeInfo=info,
                skillLineID=profession and profession.professionID, profession=profession,
                reagentSignature=validated.signature, materials=validated.items, itemNames=itemNames, allocations=allocations,
                schematic=schematic, applyConcentration=apply, operation=operation, output=output,
                quantity=schematic.quantityMin, source=preset and "schematic-preview" or "selected-crafting-operation", preset=preset})
            if record then M.Store(character, record); captured = captured + 1 end
        else missing[#missing+1] = apply and "with concentration" or "without concentration" end
    end
    if captured > 0 then
        db.lastCaptureAt = GetServerTime()
        message("Captured " .. captured .. " outcome(s) for " .. info.name .. ". Use /reload or log out to save to disk, then Import game snapshots in Crafting Desk.")
    end
    if #missing > 0 then message("Unavailable " .. table.concat(missing, ", ") .. "; prior records retained. The client may lack concentration or operation data.") end
end

function NS.SafeCapture(quiet)
    local ok = pcall(NS.Capture, quiet)
    if not ok and not quiet then message("Capture was unavailable. Existing snapshots were kept; try reopening the recipe.") end
end
SLASH_DUCKMOOCAPTURE1 = "/dmcap"
SlashCmdList.DUCKMOOCAPTURE = function() NS.SafeCapture(false) end

local _, NS = ...
local call = NS.Call
local pending, scanning, generation = false, false, 0
local hooked = setmetatable({}, {__mode="k"})
local function visible()
    return not InCombatLockdown() and NS.OwnProfession() and ProfessionsFrame and ProfessionsFrame:IsShown()
end
function NS.QueueCapture()
    if pending then return end
    pending = true
    C_Timer.After(0.4, function()
        pending = false
        if not visible() then return end
        -- Query previews separately; never allocate reagents or toggle the player's controls.
        pcall(NS.Capture, true, 1)
        pcall(NS.Capture, true, 2)
        NS.SafeCapture(true)
    end)
end
function NS.HookForm()
    local form = ProfessionsFrame and ProfessionsFrame.CraftingPage and ProfessionsFrame.CraftingPage.SchematicForm
    if not form or hooked[form] then return end
    hooked[form] = true
    for _, method in ipairs({"Init", "UpdateDetailsStats"}) do
        if type(form[method]) == "function" then hooksecurefunc(form, method, NS.QueueCapture) end
    end
    local event = ProfessionsRecipeSchematicFormMixin and ProfessionsRecipeSchematicFormMixin.Event
    if event and event.AllocationsModified and form.RegisterCallback then
        form:RegisterCallback(event.AllocationsModified, NS.QueueCapture, NS)
    end
end
function NS.ScanCatalog()
    if scanning or not visible() then return end
    local ids = call(C_TradeSkillUI.GetAllRecipeIDs)
    if type(ids) ~= "table" or #ids == 0 then return end
    scanning = true
    local token, index = generation, 1
    local function batch()
        if token ~= generation then return end
        if not visible() then scanning = false; return end
        for _ = 1, 10 do
            local id = ids[index]
            if not id then scanning = false; return end
            index = index + 1
            local info = call(C_TradeSkillUI.GetRecipeInfo, id)
            if info then pcall(NS.RememberRecipe, info, call(C_TradeSkillUI.GetRecipeSchematic, id, false)) end
        end
        C_Timer.After(0.1, batch)
    end
    batch()
end
local events = CreateFrame("Frame")
for _, event in ipairs({"ADDON_LOADED", "TRADE_SKILL_SHOW", "TRADE_SKILL_CLOSE", "TRADE_SKILL_DATA_SOURCE_CHANGING", "TRADE_SKILL_DATA_SOURCE_CHANGED", "TRADE_SKILL_LIST_UPDATE", "TRADE_SKILL_DETAILS_UPDATE", "CRAFTING_DETAILS_UPDATE", "NEW_RECIPE_LEARNED", "SKILL_LINES_CHANGED", "BAG_UPDATE_DELAYED", "PLAYER_EQUIPMENT_CHANGED", "PLAYER_REGEN_ENABLED", "UNIT_AURA", "CURRENCY_DISPLAY_UPDATE"}) do
    events:RegisterEvent(event)
end
events:SetScript("OnEvent", function(_, event, addon)
    if event == "UNIT_AURA" and addon ~= "player" then return end
    if event == "ADDON_LOADED" then
        if addon == "DuckMooCapture" then NS.Init() end
        NS.HookForm(); return
    end
    if event == "TRADE_SKILL_CLOSE" or event == "TRADE_SKILL_DATA_SOURCE_CHANGING" then
        generation = generation + 1; scanning = false; return
    end
    NS.HookForm(); NS.QueueCapture()
    if event == "SKILL_LINES_CHANGED" then generation=generation+1;scanning=false end
    if event == "TRADE_SKILL_SHOW" or event == "TRADE_SKILL_LIST_UPDATE" or event == "TRADE_SKILL_DATA_SOURCE_CHANGED" or event == "NEW_RECIPE_LEARNED" or event == "SKILL_LINES_CHANGED" then NS.ScanCatalog() end
end)

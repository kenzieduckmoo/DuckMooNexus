local _, NS = ...
local function call(fn, ...)
    if type(fn) ~= 'function' then return nil end
    local ok, a,b,c,d,e,f = pcall(fn, ...)
    if ok then return a,b,c,d,e,f end
end
local function tooltip(fn, index)
    local data=call(fn,index);local lines={}
    for _,line in ipairs(data and data.lines or {}) do
        if type(line.leftText)=='string' then lines[#lines+1]=line.leftText end
        if type(line.rightText)=='string' then lines[#lines+1]=line.rightText end
    end
    return lines
end
local function context(kind)
    local c=NS.Character();local npc=call(UnitGUID,'npc')
    if not c or not npc then return end
    c.acquisitionOffers=c.acquisitionOffers or {}
    local _,build=GetBuildInfo()
    local npcID=tonumber(npc:match('^[^-]+%-%d+%-%d+%-%d+%-%d+%-(%d+)'))
    return c,{kind=kind,npcGUID=npc,npcID=npcID,npcName=call(UnitName,'npc'),observedAt=GetServerTime(),build=build,
        mapID=call(C_Map and C_Map.GetBestMapForUnit,'player'),zone=call(GetRealZoneText),subzone=call(GetSubZoneText),money=call(GetMoney)}
end
local function save(c,base,key,record)
    for k,v in pairs(base)do record[k]=v end
    c.acquisitionOffers[base.kind..':'..tostring(base.npcID or base.npcGUID)..':'..key]=record
    -- Keep visits bounded; never replace a record merely because a filter hides it.
    local count,oldest,stamp=0,nil,math.huge
    for k,v in pairs(c.acquisitionOffers)do count=count+1;if (v.observedAt or 0)<stamp then oldest,stamp=k,v.observedAt or 0 end end
    if count>2000 then c.acquisitionOffers[oldest]=nil end
end
function NS.CaptureTrainerOffers()
    if not ClassTrainerFrame or not ClassTrainerFrame:IsShown() then return end
    local c,base=context('trainer');if not c then return end
    for i=1,math.min(call(GetNumTrainerServices) or 0,500)do
        local name,status,_,level=call(GetTrainerServiceInfo,i)
        if name and (status=='available' or status=='unavailable' or status=='used') then
            local link=call(GetTrainerServiceItemLink,i)
            local recipeID=type(link)=='string' and tonumber(link:match('spell:(%d+)')) or nil
            local price,isProfession=call(GetTrainerServiceCost,i)
            local skill,rank,hasSkill=call(GetTrainerServiceSkillReq,i)
            local requirements={}
            for j=1,math.min(call(GetTrainerServiceNumAbilityReq,i) or 0,50)do
                local ability,met=call(GetTrainerServiceAbilityReq,i,j)
                if ability then requirements[#requirements+1]={name=ability,met=met} end
            end
            save(c,base,tostring(recipeID or link or name),{name=name,recipeID=recipeID,link=link,status=status,
                price=price,isProfession=isProfession,requiredLevel=level,skill=skill,requiredSkill=rank,hasSkill=hasSkill,
                requirements=requirements,description=call(GetTrainerServiceDescription,i),
                tooltip=tooltip(C_TooltipInfo and C_TooltipInfo.GetTrainerService,i)})
        end
    end
end
function NS.CaptureVendorOffers()
    if not MerchantFrame or not MerchantFrame:IsShown() then return end
    local c,base=context('vendor');if not c then return end
    for i=1,math.min(call(GetMerchantNumItems) or 0,500)do
        local info=call(C_MerchantFrame and C_MerchantFrame.GetItemInfo,i)
        local link=call(GetMerchantItemLink,i)
        local itemID,_,_,_,_,classID=call(C_Item and C_Item.GetItemInfoInstant,link)
        -- Recipe items plus consumables/trade goods used by profession shopping lists.
        if info and info.name and itemID and (classID==9 or classID==7 or classID==0) then
            local costs={};local count=call(GetMerchantItemCostInfo,i)
            local complete=info.hasExtendedCost==false or (type(count)=='number' and count>0)
            for j=1,math.min(count or 0,20)do
                local _,amount,costLink,currencyName=call(GetMerchantItemCostItem,i,j)
                if type(amount)~='number' or not(costLink or currencyName)then complete=false end
                costs[#costs+1]={amount=amount,link=costLink,name=currencyName}
            end
            if count and count>20 then complete=false end
            save(c,base,tostring(itemID),{name=info.name,itemID=itemID,itemClass=classID,link=link,price=info.price,stackCount=info.stackCount,
                numAvailable=info.numAvailable,isPurchasable=info.isPurchasable,isUsable=info.isUsable,
                canAfford=call(CanAffordMerchantItem,i),hasExtendedCost=info.hasExtendedCost,costs=costs,costsComplete=complete,
                tooltip=tooltip(C_TooltipInfo and C_TooltipInfo.GetMerchantItem,i)})
        end
    end
end
local pending=false
local frame=CreateFrame('Frame')
for _,event in ipairs({'TRAINER_SHOW','TRAINER_UPDATE','TRAINER_SERVICE_INFO_NAME_UPDATE','MERCHANT_SHOW','MERCHANT_UPDATE','MERCHANT_FILTER_ITEM_UPDATE','GET_ITEM_INFO_RECEIVED','PLAYER_MONEY','CURRENCY_DISPLAY_UPDATE'})do frame:RegisterEvent(event)end
function NS.AcquisitionEvent()
    if pending or not ((ClassTrainerFrame and ClassTrainerFrame:IsShown()) or (MerchantFrame and MerchantFrame:IsShown()))then return end
    pending=true
    C_Timer.After(0.3,function()
        pending=false
        pcall(NS.CaptureTrainerOffers);pcall(NS.CaptureVendorOffers)
    end)
end
frame:SetScript('OnEvent',NS.AcquisitionEvent)

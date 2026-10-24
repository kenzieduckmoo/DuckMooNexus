local _,O=...
local function read(root,key,...) return O.Call(root and root[key],...) end
function O.Collections()
 local c=O.Character();local previous=c.sections.collections;if previous and previous.data and not O.collectionsDirty and GetServerTime()-(previous.observedAt or 0)<300 then return nil,"partial","Retained collection sample; collection changes trigger another read" end;O.collectionsDirty=false
 local prior=c.sections.collections and c.sections.collections.data or {};local out={};for k,v in pairs(prior) do out[k]=v end
 local changed=false;local ids=read(C_MountJournal,"GetMountIDs")
 if type(ids)=="table" and next(ids) then
  local rows={};for index,id in ipairs(ids) do if index>5000 then break end
   local name,spell,icon,_,_,source,_,_,_,_,owned=read(C_MountJournal,"GetMountInfoByID",id)
   if name and type(owned)=="boolean" then rows[id]={id=id,name=name,spellID=spell,icon=icon,collected=owned,sourceType=source} end
  end
  if next(rows) then out.mounts={observedAt=GetServerTime(),rows=rows,scope="returned_mount_ids",limited=#ids>5000};changed=true end
 end
 local pets=read(C_PetJournal,"GetOwnedPetIDs")
 if type(pets)=="table" then local rows={};for i,id in ipairs(pets) do if i>2000 then break end;local info=read(C_PetJournal,"GetPetInfoTableByPetID",id);if info then rows[id]=info end end
  if #pets==0 or next(rows) then out.pets={observedAt=GetServerTime(),rows=rows,scope="owned_pet_ids",reportedCount=#pets,limited=#pets>2000};changed=true end
 end
 -- Never change collection filters to obtain a larger list.
 local toys=read(C_ToyBox,"GetNumFilteredToys")
 if type(toys)=="number" and toys>0 then local rows={};for i=1,math.min(toys,3000) do local id=read(C_ToyBox,"GetToyFromIndex",i);if id and O.Call(PlayerHasToy,id)==true then rows[id]={itemID=id,name=read(C_Item,"GetItemNameByID",id)} end end
  out.toys={observedAt=GetServerTime(),rows=rows,scope="visible_filtered_owned_toys",limited=toys>3000};changed=true
 end
 local points=O.Call(GetTotalAchievementPoints);if type(points)=="number" then out.achievements={observedAt=GetServerTime(),points=points};changed=true end
 if not changed then return nil,"unavailable","Collection APIs not loaded or unavailable; prior observations retained" end
 return out,"partial","Account collections as exposed to this character; toy filters are respected. Each collection keeps its own observation time. Appearance completion is not inferred."
end
function O.Activities()
 local size=read(C_QuestLog,"GetNumQuestLogEntries");if type(size)~="number" then return nil,"unavailable","Quest log not ready" end
 local rows={};for i=1,math.min(size,500) do local info=read(C_QuestLog,"GetInfo",i);if info and not info.isHeader and info.questID then
  rows[info.questID]={questID=info.questID,title=info.title,level=info.level,isComplete=info.isComplete,frequency=info.frequency,isTask=info.isTask,isHidden=info.isHidden,objectives=read(C_QuestLog,"GetQuestObjectives",info.questID)}
 end end
 return {quests=rows,scope="active_quest_log",limited=size>500},"partial","Active quest log only; hidden world tasks and unaccepted weekly objectives may be absent."
end
local function bag(id)
 local slots=read(C_Container,"GetContainerNumSlots",id);if type(slots)~="number" or slots<=0 then return nil end
 local free=read(C_Container,"GetContainerNumFreeSlots",id);if type(free)~="number" then return nil end
 local row={bagID=id,slots=slots,freeSlots=free,observedAt=GetServerTime(),items={}};local found=0
 for slot=1,math.min(slots,200) do local item=read(C_Container,"GetContainerItemInfo",id,slot);if item and item.itemID then row.items[slot]={slot=slot,itemID=item.itemID,quantity=item.stackCount,link=item.hyperlink,quality=item.quality,isBound=item.isBound};found=found+1 end end
 if found~=slots-free then return nil end
 return row
end
function O.Storage()
 local c=O.Character();local prior=c.sections.storage and c.sections.storage.data or {};local out={};for k,v in pairs(prior) do out[k]=v end;local changed=false
 if O.bankOpen then
  for _,kind in ipairs({{key="characterBank",prefix="CharacterBankTab_",type="Character"},{key="accountBank",prefix="AccountBankTab_",type="Account"}}) do
   local bankType=Enum and Enum.BankType and Enum.BankType[kind.type];local allowed=bankType and read(C_Bank,"CanViewBank",bankType)
   if allowed~=false then local rows={};for id,r in pairs(out[kind.key] and out[kind.key].bags or {}) do rows[id]=r end;local sampled=false;local enums=Enum and Enum.BagIndex or {};local hasTabs=false
    for key,id in pairs(enums) do if type(key)=="string" and string.match(key,"^"..kind.prefix.."%d+$") then hasTabs=true;local r=bag(id);if r then rows[id]=r;sampled=true end end end
    if kind.key=="characterBank" and not hasTabs and enums.Bank then local r=bag(enums.Bank);if r then rows[enums.Bank]=r;sampled=true end end
    if sampled then out[kind.key]={observedAt=GetServerTime(),bags=rows,scope="readable_bank_containers",partial=true};changed=true end
   end
  end
 end
 if O.mailOpen then local count,total=O.Call(GetInboxNumItems)
  if type(count)=="number" then local messages={};local ready=true
   for i=1,math.min(count,100) do local _,_,sender,subject,money,cod,days,hasItem=O.Call(GetInboxHeaderInfo,i)
    if not sender then ready=false;break end
    local m={index=i,sender=sender,subject=subject,money=money,cod=cod,daysLeft=days,attachments={}}
    for a=1,math.min(tonumber(ATTACHMENTS_MAX_RECEIVE) or 16,16) do local name,id,_,quantity,quality=O.Call(GetInboxItem,i,a);if id then m.attachments[a]={itemID=id,name=name,quantity=quantity,quality=quality} end end
    if hasItem and not next(m.attachments) then ready=false;break end
    messages[i]=m
   end
   if ready then out.mail={observedAt=GetServerTime(),messages=messages,loaded=count,reportedTotal=total,scope="loaded_inbox_headers_and_attachments",partial=true};changed=true end
  end
 end
 if O.guildOpen then local tab=O.Call(GetCurrentGuildBankTab);local guild=O.Call(GetGuildInfo,"player")
  if tab and guild then local name,_,viewable=O.Call(GetGuildBankTabInfo,tab)
   if viewable then local rows={};local ready=true;for slot=1,98 do local _,quantity=O.Call(GetGuildBankItemInfo,tab,slot);local link=O.Call(GetGuildBankItemLink,tab,slot);if quantity==nil or quantity>0 and not link then ready=false;break end;local id=link and tonumber(string.match(link,"item:(%d+)"));if id then rows[slot]={itemID=id,quantity=quantity,link=link,slot=slot} end end
    if ready then local old=out.guildBank;local tabs=old and old.guild==guild and old.tabs or {};tabs[tab]={name=name,observedAt=GetServerTime(),items=rows};out.guildBank={guild=guild,tabs=tabs,scope="viewed_guild_tabs",partial=true};changed=true end
   end
  end
 end
 if not changed then return nil,"unavailable","Open a bank, mailbox or guild tab naturally; prior observations retained" end
 return out,"partial","Observed storage only. Locations/tabs keep their own sample times; unvisited containers and hidden mail are unknown. Mail bodies are not read. These observations do not duplicate inventory totals."
end

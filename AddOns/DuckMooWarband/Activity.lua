local _,W=...
local A={};W.Activity=A
-- Saved detail is bounded. Session totals survive trimming of individual events.
A.maxSessions=100;A.maxEvents=250;A.maxItems=300
local function secret(v)return issecretvalue and issecretvalue(v)end
local function number(v)return not secret(v) and type(v)=='number' and v==v and v>=0 and v<1e16 end
local function read(fn,...)
 if type(fn)~='function'then return nil end
 local ok,v=pcall(fn,...);if ok and number(v)then return math.floor(v)end
end
function A.Init()
 local db=W.db;db.activity=db.activity or{sessions={},nextID=1,wallets={}}
 local a=db.activity;a.sessions=a.sessions or{};a.wallets=a.wallets or{};a.nextID=a.nextID or 1
 return a
end
function A.Current()
 local a=A.Init();return a.sessions[#a.sessions]and a.sessions[#a.sessions].id==A.activeID and a.sessions[#a.sessions]or nil
end
function A.Get(id)
 if not id then return A.Current()end
 for _,s in ipairs(A.Init().sessions)do if s.id==id then return s end end
end
function A.Money(value,signed)
 if value==nil then return 'Not recorded'end
 local sign=value<0 and'-'or(signed and value>0 and'+'or'');local n=math.floor(math.abs(value))
 local gold=tostring(math.floor(n/10000));gold=gold:reverse():gsub('(%d%d%d)','%1,'):reverse():gsub('^,','')
 return sign..gold..'g '..string.format('%02ds %02dc',math.floor(n/100)%100,n%100)
end
function A.Character(guid)
 local c=W.db.characters[guid];return c and((c.name or'?')..' - '..(c.realm or'?'))or'Unknown character'
end
function A.Duration(s)
 local n=math.max(0,(s.endedAt or W.Now())-s.startedAt);return math.floor(n/3600)..'h '..math.floor(n/60)%60 ..'m'
end
local function log(s,event)
 event.at=W.Now();s.lastAt=event.at;s.events[#s.events+1]=event
 if #s.events>A.maxEvents then table.remove(s.events,1);s.trimmedEvents=(s.trimmedEvents or 0)+1 end
end
function A.BankRead()
 return read(C_Bank and C_Bank.FetchDepositedMoney,Enum and Enum.BankType and Enum.BankType.Account)
end
function A.Sample()
 local a=A.Init();local s=A.Current();local now=W.Now();local wallet=read(GetMoney);local bank=A.BankRead()
 if wallet~=nil and W.current then a.wallets[W.current]={amount=wallet,at=now}end
 if bank~=nil then a.bank={amount=bank,at=now}end
 if not s then return end
 if wallet==nil then s.walletGap=true;A.lastWallet=nil
 else
  if A.lastWallet~=nil then
   local delta=wallet-A.lastWallet
   if delta~=0 then
    s.walletDelta=s.walletDelta+delta
    if delta>0 then s.walletIn=s.walletIn+delta else s.walletOut=s.walletOut-delta end
    log(s,{kind='wallet',amount=delta,title='Wallet change'})
   end
  elseif s.walletStart==nil then s.walletStart=wallet end
  A.lastWallet=wallet;s.walletEnd=wallet
 end
 if bank==nil then s.bankGap=true;A.lastBank=nil
 else
  if A.lastBank~=nil then
   local delta=bank-A.lastBank
   if delta~=0 then s.bankDelta=s.bankDelta+delta;log(s,{kind='bank',amount=delta,title='Warbank change'})end
  elseif s.bankStart==nil then s.bankStart=bank end
  A.lastBank=bank;s.bankEnd=bank
 end
 s.lastAt=now
end
function A.Begin(label)
 local a=A.Init();local now=W.Now();local previous=A.Current()
 if previous then A.Sample();previous.endedAt=now end
 -- An interrupted client leaves a partial session, not offline earning time.
 for _,s in ipairs(a.sessions)do if not s.endedAt then s.endedAt=s.lastAt or s.startedAt;s.interrupted=true end end
 if not W.current then return end
 local s={id=a.nextID,character=W.current,label=label or'',startedAt=now,lastAt=now,walletDelta=0,bankDelta=0,walletIn=0,walletOut=0,quantity=0,items={},itemCount=0,events={}}
 a.nextID=a.nextID+1;a.sessions[#a.sessions+1]=s
 while #a.sessions>A.maxSessions do table.remove(a.sessions,1)end
 A.activeID=s.id;A.lastWallet=nil;A.lastBank=nil;A.seenLines={};A.lineQueue={}
 A.Sample();W.activitySession=nil;return s
end
function A.Finish()
 local s=A.Current();if s then A.Sample();s.endedAt=W.Now()end
 A.activeID=nil;A.lastWallet=nil;A.lastBank=nil
end
function A.Cash(s)
 if not s or s.walletStart==nil then return nil,'Wallet not recorded'end
 if s.walletGap or s.bankGap or s.bankStart==nil then return nil,'Incomplete balance coverage'end
 return s.walletDelta+s.bankDelta,'Observed wallet + warbank change'
end
-- Compile the game's localized *self* messages, preserving positional arguments.
-- Anchoring the whole format avoids mistaking another player's loot for yours.
local forms={{'LOOT_ITEM_SELF_MULTIPLE','loot'},{'LOOT_ITEM_PUSHED_SELF_MULTIPLE','received'},{'LOOT_ITEM_CREATED_SELF_MULTIPLE','crafted'},{'LOOT_ITEM_SELF','loot'},{'LOOT_ITEM_PUSHED_SELF','received'},{'LOOT_ITEM_CREATED_SELF','crafted'}}
function A.Pattern(fmt)
 local out,fields={},{};local i,implicit=1,1
 while i<=#fmt do
  local ch=fmt:sub(i,i)
  if ch=='%'then
   if fmt:sub(i+1,i+1)=='%'then out[#out+1]='%%';i=i+2
   else
    local rest=fmt:sub(i);local token,pos,kind=rest:match('^(%%(%d+)%$([sd]))')
    if not token then token,kind=rest:match('^(%%([sd]))');pos=implicit;implicit=implicit+1 end
    if not token then return nil end
    fields[#fields+1]={position=tonumber(pos),kind=kind};out[#out+1]=kind=='d'and'(%d+)'or'(.-)';i=i+#token
   end
  else
   out[#out+1]=ch:match('[%^%$%(%)%.%[%]%*%+%-%?]')and('%'..ch)or ch;i=i+1
  end
 end
 return '^'..table.concat(out)..'$',fields
end
function A.ParseLoot(message)
 if secret(message)or type(message)~='string'then return end
 for _,form in ipairs(forms)do
  local fmt=_G[form[1]]
  if type(fmt)=='string'then
   local pattern,fields=A.Pattern(fmt)
   if pattern then
    local captures={message:match(pattern)}
    if #captures>0 then
     local link,quantity=nil,1
     for i,field in ipairs(fields)do if field.kind=='s'and captures[i]:find('|Hitem:',1,true)then link=captures[i]elseif field.kind=='d'then quantity=tonumber(captures[i])end end
     local id=link and tonumber(link:match('|Hitem:(%d+)'))
     if id and quantity and quantity>0 then return link,quantity,id,form[2]end
    end
   end
  end
 end
end
function A.ItemInfo(link)
 local fn=C_Item and C_Item.GetItemInfo
 if type(fn)~='function'then return end
 local result={pcall(fn,link)}
 if result[1]and not secret(result[2])and type(result[2])=='string'then
  local price=result[12];return result[2],number(price)and price or nil
 end
end
function A.Loot(message,lineID)
 local s=A.Current();if not s then return end
 local link,quantity,id,kind=A.ParseLoot(message);if not link then return end
 if not secret(lineID)and type(lineID)=='number'and lineID>0 then
  if A.seenLines[lineID]then return end
  A.seenLines[lineID]=true;A.lineQueue[#A.lineQueue+1]=lineID
  if #A.lineQueue>500 then A.seenLines[table.remove(A.lineQueue,1)]=nil end
 end
 local name,price=A.ItemInfo(link);local key=link..':'..kind..':'..date('%Y-%m-%d',W.Now())
 s.quantity=s.quantity+quantity
 local item=s.items[key]
 if not item and s.itemCount>=A.maxItems then
  s.unlistedQuantity=(s.unlistedQuantity or 0)+quantity;s.unlistedDays=s.unlistedDays or{}
  local day=date('%Y-%m-%d',W.Now());s.unlistedDays[day]=(s.unlistedDays[day]or 0)+quantity
 else
  if not item then item={id=id,link=link,name=name or link:match('|h%[(.-)%]|h')or('Item '..id),kind=kind,quantity=0,price=price};s.items[key]=item;s.itemCount=s.itemCount+1 end
  item.quantity=item.quantity+quantity;item.at=W.Now();if price~=nil then item.price=price end
 end
 log(s,{kind=kind,title=name or link:match('|h%[(.-)%]|h')or('Item '..id),quantity=quantity,link=link})
 if C_Item and type(C_Item.RequestLoadItemDataByID)=='function'and price==nil then pcall(C_Item.RequestLoadItemDataByID,id)end
end
function A.Resolve(id)
 for _,s in ipairs(A.Init().sessions)do
  for _,item in pairs(s.items)do
   if item.id==id and item.price==nil then local name,price=A.ItemInfo(item.link);if name then item.name=name end;if price~=nil then item.price=price end end
  end
 end
end
function A.Estimate(s)
 local value,unknown=0,s and(s.unlistedQuantity or 0)or 0
 if s then for _,item in pairs(s.items)do if item.price==nil then unknown=unknown+item.quantity else value=value+item.price*item.quantity end end end
 return value,unknown
end
function A.Filtered(defaultRange)
 local list={};local range=W.activityRange or defaultRange or'session';local character=W.activityCharacter;local cutoff
 if range=='today'then local d=date('*t',W.Now());d.hour=0;d.min=0;d.sec=0;cutoff=time(d)
 elseif range=='week'then local d=date('*t',W.Now());d.day=d.day-6;d.hour=0;d.min=0;d.sec=0;cutoff=time(d)end
 local current=A.Current()
 for _,s in ipairs(A.Init().sessions)do
  if (not character or character==s.character)and(range~='session'or(current and s.id==current.id))then list[#list+1]=s end
 end
 return list,cutoff
end
function A.Notify()if W.frame and W.frame:IsShown()and W.Render then W.Render()end end
local events=CreateFrame('Frame');A.events=events
for _,event in ipairs({'PLAYER_ENTERING_WORLD','PLAYER_LOGOUT','PLAYER_MONEY','ACCOUNT_MONEY','BANKFRAME_OPENED','CHAT_MSG_LOOT','GET_ITEM_INFO_RECEIVED'})do events:RegisterEvent(event)end
events:SetScript('OnEvent',function(_,event,...)
 if not W.db then return end
 if event=='PLAYER_ENTERING_WORLD'then W.CaptureCharacter();if not A.Current()then A.Begin()else A.Sample()end
 elseif event=='PLAYER_LOGOUT'then A.Finish()
 elseif event=='PLAYER_MONEY'or event=='ACCOUNT_MONEY'or event=='BANKFRAME_OPENED'then A.Sample()
 elseif event=='CHAT_MSG_LOOT'then local message=...;local lineID=select(11,...);A.Loot(message,lineID)
 elseif event=='GET_ITEM_INFO_RECEIVED'then local id,success=...;if success and not secret(id)and type(id)=='number'then A.Resolve(id)end end
 A.Notify()
end)

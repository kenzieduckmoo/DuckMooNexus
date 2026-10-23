"""Activity event integration and migration checks, plus existing task regressions."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
ns=runpy.run_path(str(root/'tests/run_tests.py'))
lua=ns['lua']
lua.globals().ACTIVITY_SOURCE=str(root/'Activity.lua')
lua.execute(r'''
local A=W.Activity
W.db.activity=nil;W.current='priest1';W.db.settings.compact=false
UnitGUID=function()return 'priest1'end;UnitName=function()return 'Ember'end
W.activityRange=nil;W.activityCharacter=nil;W.activitySession=nil
local wallet,bank=10000000,50000000
GetMoney=function()return wallet end
Enum={BankType={Account=2}}
C_Bank={FetchDepositedMoney=function(kind)assert(kind==2);return bank end}
local function dispatch(event,...)A.events:GetScript('OnEvent')(A.events,event,...)end
LOOT_ITEM_SELF='You receive loot: %s.'
LOOT_ITEM_SELF_MULTIPLE='You receive loot: %sx%d.'
LOOT_ITEM_PUSHED_SELF='You receive item: %s.'
LOOT_ITEM_PUSHED_SELF_MULTIPLE='You receive item: %sx%d.'
LOOT_ITEM_CREATED_SELF='You create: %s.'
LOOT_ITEM_CREATED_SELF_MULTIPLE='You create: %sx%d.'
local link='|cffffffff|Hitem:2589:::::::::|h[Linen Cloth]|h|r'
local price=nil
C_Item={GetItemInfo=function(item)return 'Linen Cloth',item,1,1,1,'Trade Goods','Cloth',200,'',123,price end,RequestLoadItemDataByID=function(id)assert(type(id)=='number')end}
dispatch('PLAYER_ENTERING_WORLD');local s=A.Current();assert(s and #A.Init().sessions==1)
dispatch('PLAYER_ENTERING_WORLD');assert(A.Current()==s,'Zone transitions created sessions')
assert(s.walletStart==wallet and s.bankStart==bank and A.Cash(s)==0)
-- Deposit wallet-first, then withdrawal bank-first: final cash remains unchanged.
wallet=wallet-2500000;dispatch('PLAYER_MONEY');bank=bank+2500000;dispatch('ACCOUNT_MONEY');assert(A.Cash(s)==0)
bank=bank-1000000;dispatch('ACCOUNT_MONEY');wallet=wallet+1000000;dispatch('PLAYER_MONEY');assert(A.Cash(s)==0)
wallet=wallet+1250000;dispatch('PLAYER_MONEY');wallet=wallet-250000;dispatch('PLAYER_MONEY')
assert(A.Cash(s)==1000000 and s.walletIn==2250000 and s.walletOut==2750000)
local quantity=s.quantity
dispatch('CHAT_MSG_LOOT','Someone receives loot: '..link..'.','','','','','',0,0,'',0,10)
assert(s.quantity==quantity,'Other-player loot counted')
dispatch('CHAT_MSG_LOOT',string.format(LOOT_ITEM_SELF_MULTIPLE,link,12),'','','','','',0,0,'',0,11)
dispatch('CHAT_MSG_LOOT',string.format(LOOT_ITEM_SELF_MULTIPLE,link,12),'','','','','',0,0,'',0,11)
assert(s.quantity==12,'Duplicate line counted')
dispatch('CHAT_MSG_LOOT',string.format(LOOT_ITEM_CREATED_SELF,link),'','','','','',0,0,'',0,12)
dispatch('CHAT_MSG_LOOT',string.format(LOOT_ITEM_PUSHED_SELF_MULTIPLE,link,3),'','','','','',0,0,'',0,13)
assert(s.quantity==16 and s.itemCount==3)
local estimate,unknown=A.Estimate(s);assert(estimate==0 and unknown==16)
price=7;dispatch('GET_ITEM_INFO_RECEIVED',2589,true);estimate,unknown=A.Estimate(s)
assert(estimate==112 and unknown==0 and A.Cash(s)==1000000,'Vendor estimate counted as cash')
price=0;A.Loot(string.format(LOOT_ITEM_SELF,link),14);estimate,unknown=A.Estimate(s);assert(unknown==0,'Zero vendor price became unknown')
-- Position arguments, escaped punctuation and literal percent signs.
LOOT_ITEM_SELF_MULTIPLE='Erhalten (100%%): %2$dx %1$s!'
local l,q,id,kind=A.ParseLoot('Erhalten (100%): 24x '..link..'!')
assert(l==link and q==24 and id==2589 and kind=='loot')
LOOT_ITEM_SELF_MULTIPLE='You receive loot: %sx%d.'
-- Calendar filters correctly split one session across midnight.
W.db.activity=nil;A.activeID=nil;NOW=time({year=2026,month=10,day=8,hour=23,min=59,sec=0})
s=A.Begin('Crossing midnight');A.Loot(string.format(LOOT_ITEM_SELF_MULTIPLE,link,2),101)
NOW=NOW+120;A.Loot(string.format(LOOT_ITEM_SELF_MULTIPLE,link,3),102)
W.activityRange='today';local rows,headings,values=W.ActivityRows('loot','');assert(values[2]=='3')
W.activityRange='week';rows,headings,values=W.ActivityRows('loot','');assert(values[2]=='5')
W.activityRange='all';W.activityCharacter='hunter';rows=W.ActivityRows('loot','');assert(#rows==0)
W.activityCharacter=nil;W.activityRange=nil
-- Unavailable/secret/error balances preserve snapshots and flag coverage gaps.
local snapshot=A.Init().wallets.priest1.amount;local secretValue={}
issecretvalue=function(v)return v==secretValue end
wallet=secretValue;dispatch('PLAYER_MONEY');assert(s.walletGap and A.Init().wallets.priest1.amount==snapshot)
wallet=snapshot+500000;dispatch('PLAYER_MONEY');assert(A.Cash(s)==nil,'Unobserved wallet interval treated as complete')
local prior=A.Init().bank.amount;C_Bank.FetchDepositedMoney=function()error('Unavailable')end
dispatch('ACCOUNT_MONEY');assert(A.Init().bank.amount==prior and s.bankGap)
C_Bank.FetchDepositedMoney=function()return bank end;issecretvalue=nil
-- Reload-like module reset retains sessions but cannot count offline time or gains.
local last=s.lastAt;local idBefore=s.id;NOW=NOW+86400
assert(loadfile(ACTIVITY_SOURCE))('DuckMooWarband',W);A=W.Activity;wallet=wallet+900000
dispatch('PLAYER_ENTERING_WORLD');local nextSession=A.Current()
assert(nextSession.id>idBefore and s.endedAt==last and s.interrupted and A.Cash(nextSession)==0)
dispatch('PLAYER_LOGOUT');assert(nextSession.endedAt==NOW and A.Current()==nil)
local priestWallet=A.Init().wallets.priest1.amount
W.current='hunter';wallet=2000000;local alt=A.Begin('Alt session')
assert(alt.character=='hunter'and A.Cash(alt)==0 and A.Init().wallets.priest1.amount==priestWallet)
A.Finish();W.current='priest1';wallet=priestWallet
-- Begin a fresh observed session; labelled history opens through real UI controls.
s=A.Begin('Cloth outing');W.activityRange=nil;W.activityCharacter=nil
W.SelectPage('sessions');assert(#W.visibleRows>=2 and W.frame.rows[1].done:IsShown())
W.frame.rows[1].done:GetScript('OnClick')();assert(W.Page()=='session' and W.activitySession==s.id)
W.frame.activity.name:SetText('A small next step');W.frame.activity.save:GetScript('OnClick')();assert(s.label=='A small next step')
local older=s.id;W.frame.activity.new:GetScript('OnClick')();assert(A.Current().id>older and s.endedAt)
W.SelectPage('loot');W.frame.activity.range:GetScript('OnClick')();W.choice.callback('all');assert(W.activityRange=='all')
W.frame.activity.character:GetScript('OnClick')();W.choice.callback('priest1');assert(W.activityCharacter=='priest1')
W.SelectPage('gold');W.frame.search:SetText('Ember');assert(#W.visibleRows==1)
-- Every new page fits the smallest full view and reuses the existing row pool.
local pages={'today','all','characters','categories','session','gold','loot','sessions','preferences'}
W.frame.search:SetText('');W.frame:SetSize(940,560)
for _,page in ipairs(pages)do W.SelectPage(page)end
local frameCount=#frames
for j=1,8 do for _,page in ipairs(pages)do
 W.SelectPage(page)
 for _,row in ipairs(W.frame.rows)do if row:IsShown()then
  assert(-row.point[3]+row:GetHeight()<=W.frame:GetHeight()-40,'Rows overlap footer')
 end end
end end
assert(#frames==frameCount,'Activity pages allocate widgets each refresh')
W.SelectPage('gold');W.SelectPage('today');assert(W.frame.capture:IsShown()and W.frame.rows[1].done:IsShown(),'Task controls stayed hidden after activity')
-- Event and item limits retain totals, and the session ring is bounded.
W.db.activity=nil;A.activeID=nil;s=A.Begin();local oldItems=A.maxItems;A.maxItems=1
A.Loot(string.format(LOOT_ITEM_SELF,link),1)
local another='|cffffffff|Hitem:2592:::::::::|h[Wool Cloth]|h|r'
for i=2,302 do A.Loot(string.format(LOOT_ITEM_SELF,another),i)end
assert(s.quantity==302 and s.itemCount==1 and #s.events==A.maxEvents and s.unlistedQuantity==301)
W.activityRange='today';W.activityCharacter=nil;rows,headings,values=W.ActivityRows('loot','');assert(values[2]=='302')
A.maxItems=oldItems
for i=1,110 do A.Begin()end
assert(#A.Init().sessions==A.maxSessions)
print('PASS: real activity events, transfer neutrality, cash/estimate separation, self-loot localization/dedup, delayed/zero prices, calendar filters, secret/unavailable balances, reload/alt persistence, session controls, page geometry and bounded storage/widgets')
''')

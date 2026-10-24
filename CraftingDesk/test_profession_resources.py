"""Focused assemble boundary: fresh resources cannot establish recipe ownership."""
from copy import deepcopy
from importer import assemble

guid='Player-104-ABCD'
data={'DuckMooFolio':{'DuckMooFolioDB':{'characters':{guid:{'name':'Fixture','realm':'Realm','professions':{171:{'name':'Alchemy','expansions':{2906:{'name':'Midnight Alchemy','rank':50,'max':100,'seenAt':1000}}}}}}}},'DuckMooPlanner':{'DuckMooPlannerDB':{'characters':{guid:{'professions':{2906:{'currencyID':3161,'amount':900,'max':1000,'observedAt':1000,'secondsPerPoint':345.6}}}}}},'DuckMooOmniCapture':{'DuckMooOmniCaptureDB':{'schema':1,'characters':{guid:{'name':'Fixture','realm':'Realm','sections':{'knowledge':{'observedAt':1100,'data':{2906:{'observedAt':1100,'data':{'skillLineID':2906,'profession':{'professionID':2906,'parentProfessionName':'Alchemy','professionName':'Midnight Alchemy','skillLevel':60,'maxSkillLevel':100},'concentration':{'currencyID':3161,'amount':123,'max':1000,'observedAt':1100,'secondsPerPoint':345.6}}}}},'currencies':{'observedAt':1200,'data':{3161:{'quantity':0,'maxQuantity':1000,'rechargingCycleDurationMS':345600,'rechargingAmountPerCycle':1}}}}}}}}}
before=deepcopy(data)
def model(value):return assemble(value,[],[],market_override={'commodities':{}},inventory_override={'items':{},'names':{},'tiers':{}})
result=model(data);p=result['characters'][0]['professions'][0]
assert p['rank']==60 and p['concentration']['amount']==0 and p['concentration']['observedAt']==1200
assert p['concentration']['source']=='DuckMoo Omni Capture' and p['concentration']['secondsPerPoint']==345.6
assert result['recipes']==[] and data==before
data['DuckMooOmniCapture']['DuckMooOmniCaptureDB']['characters'][guid]['sections']['currencies']['data']={9999:{'quantity':0,'maxQuantity':1000}}
assert model(data)['characters'][0]['professions'][0]['concentration']['amount']==123
data['DuckMooOmniCapture']['DuckMooOmniCaptureDB']['characters'][guid]['sections']['knowledge']['data'][2906]['data']['concentration']['amount']=-1
assert model(data)['characters'][0]['professions'][0]['concentration']['amount']==900
data['DuckMooOmniCapture']['DuckMooOmniCaptureDB']['schema']=999
assert model(data)['characters'][0]['professions'][0]['rank']==50
print('Crafting assemble uses only newer valid resource observations, preserves real zero and rate, ignores other currency IDs, and adds no recipe ownership.')

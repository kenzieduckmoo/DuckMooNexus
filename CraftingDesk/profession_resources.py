"""Merge independently captured profession resources, never recipe ownership."""
import math


def number(value):
    return type(value) in (int,float) and math.isfinite(value)


def valid_pool(pool):
    return isinstance(pool,dict) and all(number(pool.get(k)) for k in ('amount','max','observedAt')) and 0<=pool['amount']<=pool['max'] and pool['max']>0 and 0<pool['observedAt']<4102444800


def merge_omni_resources(characters,omni):
    if omni.get('schema')!=1:return
    by_guid={c['guid']:c for c in characters}
    for guid,record in omni.get('characters',{}).items():
        sections=record.get('sections',{})
        profile=sections.get('profile',{}).get('data') or {}
        c=by_guid.get(guid)
        if c is None:
            name,realm=record.get('name',profile.get('name')),record.get('realm',profile.get('realm'))
            if not name or not realm:continue
            c={'guid':guid,'name':name,'realm':realm,'class':profile.get('class'),'faction':profile.get('faction'),'level':profile.get('level'),'professions':[]}
            characters.append(c);by_guid[guid]=c
        professions={int(p['id']):p for p in c['professions'] if p.get('id')}
        knowledge=sections.get('knowledge',{}).get('data') or {}
        for saved in knowledge.values():
            meta=saved.get('data',{}) if isinstance(saved,dict) else {}
            skill=meta.get('skillLineID');info=meta.get('profession') or {}
            if type(skill) is not int or skill<=0:continue
            if info.get('professionID') not in (None,skill):info={}
            p=professions.get(skill)
            if p is None:
                if not info.get('professionName'):continue
                p={'id':skill,'baseName':info.get('parentProfessionName'),'name':info['professionName'],'rank':None,'max':None,'seenAt':None,'knowledgeNodes':0,'concentration':None}
                c['professions'].append(p);professions[skill]=p
            if info.get('parentProfessionName'):p['baseName']=info['parentProfessionName']
            if info.get('professionName'):p['name']=info['professionName']
            at=saved.get('observedAt')
            if number(at) and at>float(p.get('seenAt') or 0):
                if number(info.get('skillLevel')):p['rank']=info['skillLevel']
                if number(info.get('maxSkillLevel')):p['max']=info['maxSkillLevel']
                p['seenAt']=at
            pool=meta.get('concentration')
            if valid_pool(pool) and (not valid_pool(p.get('concentration')) or pool['observedAt']>p['concentration']['observedAt']):p['concentration']={**pool,'source':'DuckMoo Omni Capture'}
        currency_section=sections.get('currencies',{})
        currencies=currency_section.get('data') or {};at=currency_section.get('observedAt')
        for p in c['professions']:
            pool=p.get('concentration') or {};currency=currencies.get(pool.get('currencyID')) or currencies.get(str(pool.get('currencyID')))
            if not isinstance(currency,dict) or not number(at) or at<=float(pool.get('observedAt') or 0):continue
            cycle,amount=currency.get('rechargingCycleDurationMS'),currency.get('rechargingAmountPerCycle')
            newer={'currencyID':pool['currencyID'],'amount':currency.get('quantity'),'max':currency.get('maxQuantity'),'observedAt':at,'secondsPerPoint':cycle/1000/amount if number(cycle) and cycle>0 and number(amount) and amount>0 else None,'source':'DuckMoo Omni Capture'}
            if valid_pool(newer):p['concentration']=newer

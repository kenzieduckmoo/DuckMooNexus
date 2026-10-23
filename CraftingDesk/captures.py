"""Adapt explicit in-game operations to fixed-reagent recipes."""
import hashlib
import math
import re

def positive(value):
    return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value) and value>0

def with_scanned_operations(db):
    """Expand compact scanner records into the same validated operation format."""
    result={**db,'characters':{}}
    for guid,character in db.get('characters',{}).items():
        operations=dict(character.get('operations',{}))
        for recipe_id,scan in character.get('scannedRecipes',{}).items():
            if scan.get('invalidatedAt'):continue
            info=scan.get('info',{});schematic=scan.get('schematic',{});profession=scan.get('profession',{})
            for key,outcome in scan.get('outcomes',{}).items():
                operations[f'scan:{recipe_id}:{key}']={**outcome,'recipeID':info.get('recipeID'),'name':info.get('name'),
                    'schematic':schematic,'profession':profession,'skillLineID':profession.get('professionID'),
                    'quantity':schematic.get('quantityMin'),'source':'recipe-scan','scanLimited':scan.get('limited',True)}
        result['characters'][guid]={**character,'operations':operations}
    return result

def scan_coverage(db):
    return [{'character':c.get('name'),'realm':c.get('realm'),'professionID':pid,**status}
            for c in db.get('characters',{}).values() for pid,status in c.get('scanStatus',{}).items() if positive(pid)]

def captured_recipes(db, market):
    if db.get('schemaVersion') != 1: raise ValueError('Unsupported DuckMooCapture schema')
    recipes, names, skipped = [], {}, 0
    for guid, character in db.get('characters',{}).items():
        for capture_id, record in character.get('operations',{}).items():
            if record.get('invalidatedAt'):continue
            try:
                rid, output = record['recipeID'], record['output']['itemID']
                if not positive(rid) or not positive(output) or int(rid)!=rid or int(output)!=output: raise ValueError()
                quantity=record['quantity']; schematic=record['schematic']
                if not positive(quantity) or schematic.get('quantityMin')!=quantity or schematic.get('quantityMax')!=quantity or schematic.get('isRecraft'): raise ValueError()
                if not positive(record.get('observedAt')) or not isinstance(record.get('applyConcentration'),bool): raise ValueError()
                allocations=record['allocations'].values()
                materials, totals = {}, {}
                for allocation in allocations:
                    reagent=allocation['reagent']; item=reagent.get('itemID'); amount=allocation['quantity']; slot=(allocation['dataSlotType'],allocation['dataSlotIndex'])
                    if not positive(item) or reagent.get('currencyID') or not positive(amount): raise ValueError()
                    key='i:'+str(int(item)); materials[key]=materials.get(key,0)+amount
                    totals[slot]=totals.get(slot,0)+amount
                for slot in schematic.get('reagentSlotSchematics',{}).values():
                    if slot.get('required') and totals.get((slot['dataSlotType'],slot['dataSlotIndex']),0)!=slot['quantityRequired']: raise ValueError()
                operation=record['operation']; apply=record['applyConcentration']
                cost=operation.get('concentrationCost') if apply else 0
                # The game can return an unchanged preview when concentration
                # is requested but costs zero. Ignore it only when a valid,
                # otherwise identical normal operation is present. Unknown or
                # unmatched zero-cost operations still fail validation below.
                if apply and type(cost) in (int,float) and cost==0:
                    duplicate=False
                    for other_id, other in character.get('operations',{}).items():
                        if (other.get('applyConcentration') is False
                            and all(other.get(key)==record.get(key) for key in ('recipeID','output','quantity','schematic','allocations','skillLineID'))
                            and other.get('operation',{}).get('craftingQuality')==operation.get('craftingQuality')):
                            check={'schemaVersion':1,'characters':{guid:{**character,'operations':{other_id:other}}}}
                            if captured_recipes(check,market)[0]:
                                duplicate=True;break
                    if duplicate: continue
                if apply and not positive(cost): raise ValueError()
                name=character['name']; realm=character['realm']; faction=character['faction']
                digest=hashlib.sha256((str(guid)+'|'+str(capture_id)).encode()).hexdigest()[:20]
                item='i:'+str(int(output))
                capture={'observedAt':record['observedAt'],'applyConcentration':apply,'concentration':cost,'skillLineID':record.get('skillLineID'),
                         'build':record.get('build'),'quality':operation.get('craftingQuality'),'operation':operation,
                         'manualSalePrice':item not in market.get('commodities',{}),'source':record.get('source','selected-crafting-operation'),'preset':record.get('preset'),'scanLimited':record.get('scanLimited')}
                profession=record.get('profession',{})
                recipes.append({'key':f'c:{int(rid)}:q{operation.get("craftingQuality",0)}:capture:{digest}',
                                'scope':f'{faction} - {realm}','name':record['name'],'profession':profession.get('parentProfessionName') or profession.get('professionName','Captured craft'),
                                'output':item,'quantity':quantity,'materials':materials,
                                'crafters':[{'name':name,'realm':realm,'guid':guid,'stats':{}}],'capture':capture})
                link=record['output'].get('hyperlink',''); match=re.search(r'\|h\[(.*?)\]\|h',link)
                if match: names[item]=re.sub(r'\|A:.*?\|a','',match[1]).strip()
                for item_id, label in record.get('itemNames',{}).items():
                    if isinstance(label,str) and str(item_id).isdigit(): names['i:'+str(item_id)]=re.sub(r'\|A:.*?\|a','',label).strip()
            except (KeyError,TypeError,ValueError,AttributeError): skipped+=1
    return recipes,names,skipped

def capture_catalog(db):
    result=[]
    for guid, character in db.get('characters',{}).items():
        for recipe_id, record in character.get('recipes',{}).items():
            info=record.get('info',{})
            result.append({'guid':guid,'character':character.get('name'),'realm':character.get('realm'),'recipeID':recipe_id,
                           'name':info.get('name'),'learned':info.get('learned'),'firstCraft':info.get('firstCraft') if isinstance(info.get('firstCraft'),bool) else None,'observedAt':record.get('observedAt'),
                           'profession':record.get('profession',{}),'schematic':record.get('schematic'),
                           'build':record.get('build'),'sourceText':record.get('sourceText'),'sourceObservedAt':record.get('sourceObservedAt'),
                           'skillHistory':record.get('skillHistory',{}) if record.get('skillHistoryBuild')==record.get('build') else {},
                           'relativeDifficulty':info.get('relativeDifficulty'),'disabled':info.get('disabled'),'disabledReason':info.get('disabledReason'),'cooldown':record.get('cooldown'),'cooldownCaptured':record.get('cooldownCaptured',False),'canSkillUp':info.get('canSkillUp'),'numSkillUps':info.get('numSkillUps'),'maxTrivialLevel':info.get('maxTrivialLevel')})
    return result

def acquisition_offers(db):
    """Keep visits character-specific; no name matching or inferred unlocks."""
    rows=[]
    for guid, character in db.get('characters',{}).items():
        for record in character.get('acquisitionOffers',{}).values():
            if not isinstance(record,dict) or record.get('kind') not in ('trainer','vendor') or not positive(record.get('observedAt')):
                continue
            row={**record,'guid':guid,'character':character.get('name'),'realm':character.get('realm')}
            for key in ('costs','requirements','tooltip'):
                value=row.get(key,{})
                row[key]=list(value.values()) if isinstance(value,dict) else value if isinstance(value,list) else []
            rows.append(row)
    return rows

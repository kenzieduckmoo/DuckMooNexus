"""Read WoW SavedVariables as data, without executing Lua."""
import re
from pathlib import Path
from datetime import datetime, timezone
from materials import market_data, inventory_data, item_names, item_tiers, APP_DATA
from captures import captured_recipes, capture_catalog, with_scanned_operations, scan_coverage, acquisition_offers
from profession_resources import merge_omni_resources

ROOT = Path(r'D:\World of Warcraft\_retail_\WTF\Account\SQUIRRELUDECKER\SavedVariables')

def read_lua(path, binary_strings=False):
    # WoW emits one table field per line. Preserve bytes before decoding strings.
    root, stack, indexes = {}, [], []
    stack.append(root); indexes.append(0)
    def scalar(s):
        if s.startswith('"') and s.endswith('"'):
            raw = s[1:-1]
            escapes = {'n':'\n','r':'\r','t':'\t','"':'"','\\':'\\','a':'\a','b':'\b','f':'\f','v':'\v'}
            raw = re.sub(r'\\(\d{1,3}|.)', lambda m: chr(int(m[1])) if m[1].isdigit() else escapes.get(m[1], m[1]), raw)
            return raw if binary_strings else raw.encode('latin1').decode('utf-8', errors='replace')
        if s == 'true': return True
        if s == 'false': return False
        if s == 'nil': return None
        if re.fullmatch(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', s):
            return float(s) if any(c in s for c in '.eE') else int(s)
        raise ValueError('Unsupported SavedVariables value')
    for number, line in enumerate(path.read_bytes().decode('latin1').split('\n'), 1):
        s = line.strip().removesuffix(',')
        if not s: continue
        if s == '}':
            if len(stack) == 1: raise ValueError('Unexpected table end')
            stack.pop(); indexes.pop(); continue
        match = re.fullmatch(r'\[("(?:\\.|[^"\\])*"|-?\d+)\] = (.*)', s)
        assignment = re.fullmatch(r'(\w+) = (.*)', s)
        if match: key, value = scalar(match[1]), match[2]
        elif assignment: key, value = assignment.groups()
        else: indexes[-1] += 1; key, value = indexes[-1], s
        if value == '{':
            child = {}; stack[-1][key] = child; stack.append(child); indexes.append(0)
        else:
            try: stack[-1][key] = scalar(value)
            except ValueError as e: raise ValueError(f'{path.name}:{number}: {e}') from e
    if len(stack) != 1: raise ValueError('Incomplete SavedVariables file; try again after saving finishes')
    return root

def collect():
    data, sources, errors = {}, [], []
    for name in ('DuckMooFolio', 'DuckMooPlanner', 'TradeSkillMaster', 'Syndicator', 'DuckMooCapture','DuckMooOmniCapture'):
        path = ROOT / (name + '.lua')
        if name in ('DuckMooCapture','DuckMooOmniCapture') and not path.exists(): continue
        try:
            before = path.stat()
            data[name] = read_lua(path)
            after = path.stat()
            if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
                raise ValueError('File changed during import; retry after reload finishes')
            sources.append({'name':name, 'bytes':after.st_size, 'savedAt':after.st_mtime})
        except (OSError, ValueError) as e:
            data.pop(name, None); errors.append(f'{name}: {e}')
    return assemble(data,sources,errors)


def assemble(data,sources,errors,market_override=None,inventory_override=None):
    folio = data.get('DuckMooFolio', {}).get('DuckMooFolioDB', {}).get('characters', {})
    planner = data.get('DuckMooPlanner', {}).get('DuckMooPlannerDB', {}).get('characters', {})
    synd = data.get('Syndicator', {}).get('SYNDICATOR_DATA', {})
    characters = []
    for guid in folio.keys() | planner.keys():
        f, p = folio.get(guid, {}), planner.get(guid, {})
        c = {'guid':guid, 'name':f.get('name',p.get('name')), 'realm':f.get('realm',p.get('realm')), 'class':f.get('class',p.get('class')), 'faction':f.get('faction'), 'level':f.get('level'), 'professions':[]}
        for base in f.get('professions', {}).values():
            for skill, row in base.get('expansions', {}).items():
                con = p.get('professions', {}).get(skill)
                c['professions'].append({'id':skill, 'baseName':base.get('name'), 'name':row.get('name'), 'rank':row.get('rank'), 'max':row.get('max'), 'seenAt':row.get('seenAt'), 'knowledgeNodes':len(row.get('knowledge',{})), 'concentration':con})
        professions={}
        for profession in c['professions']:
            if not profession['id'] or not profession.get('name'):continue
            previous=professions.get(profession['id'])
            if previous is None or (profession.get('seenAt') or 0)>(previous.get('seenAt') or 0):professions[profession['id']]=profession
        c['professions']=list(professions.values())
        characters.append(c)
    merge_omni_resources(characters,data.get('DuckMooOmniCapture',{}).get('DuckMooOmniCaptureDB',{}))
    recipes = []
    tsm = data.get('TradeSkillMaster',{}).get('TradeSkillMasterDB',{})
    for scope, records in tsm.items():
        if not scope.endswith('@internalData@crafts') or not isinstance(records,dict): continue
        faction_realm = scope.split('@')[1]
        faction, _, realm = faction_realm.partition(' - ')
        for key, r in records.items():
            if not isinstance(r,dict): continue
            crafters = []
            for name, stats in r.get('players',{}).items():
                matches = [c for c in characters if c['name'].casefold()==name.casefold() and c['realm'].replace(' ','').casefold()==realm.replace(' ','').casefold() and c['faction']==faction]
                crafters.append({'name':name,'realm':realm,'guid':matches[0]['guid'] if len(matches)==1 else None,'stats':stats})
            recipes.append({'key':key,'scope':faction_realm,'name':r.get('name'),'profession':r.get('profession'),'output':r.get('itemString'),'quantity':r.get('numResult'),'materials':r.get('mats',{}),'crafters':crafters})
    inventory = inventory_override if inventory_override is not None else inventory_data(synd)
    try:
        names = item_names(data.get('TradeSkillMaster', {}).get('TSMItemInfoDB', {}))
        names.update(inventory['names'])
        inventory['names'] = names
        inventory.setdefault('tiers',{}).update(item_tiers(data.get('TradeSkillMaster', {}).get('TSMItemInfoDB', {})))
    except ValueError as e:
        errors.append('TSM item names: ' + str(e))
    if market_override is not None:
        market=market_override
    else:
        market = {}
        try:
            before=APP_DATA.stat()
            market=market_data()
            after=APP_DATA.stat()
            if (before.st_mtime_ns,before.st_size)!=(after.st_mtime_ns,after.st_size):
                raise ValueError('Price file changed during import; retry')
            sources.append({'name':'TSM downloaded prices','bytes':after.st_size,'savedAt':after.st_mtime})
        except (OSError,ValueError) as e:
            market={}; errors.append('TSM prices: '+str(e))
        try:
            from auctionator import auctionator_prices
            path=ROOT/'Auctionator.lua'
            before=path.stat()
            auctionator=auctionator_prices(read_lua(path,binary_strings=True).get('AUCTIONATOR_PRICE_DATABASE',{}),market)
            after=path.stat()
            if (before.st_mtime_ns,before.st_size)!=(after.st_mtime_ns,after.st_size): raise ValueError('Price file changed during import; retry')
            market['auctionator']=auctionator
            errors.extend('Auctionator: '+warning for warning in auctionator['warnings'])
            sources.append({'name':'Auctionator prices','bytes':after.st_size,'savedAt':after.st_mtime})
        except (OSError,ValueError,TypeError) as e: errors.append('Auctionator prices: '+str(e))
    catalog=[]
    offers=[]
    coverage=[]
    diagnostics=[]
    if 'DuckMooCapture' in data:
        try:
            capture_db=data['DuckMooCapture'].get('DuckMooCaptureDB',{})
            coverage=scan_coverage(capture_db)
            offers=acquisition_offers(capture_db)
            for offer in offers:
                if offer.get("itemID") and offer.get("name"):
                    inventory["names"]["i:"+str(offer["itemID"])]=offer["name"]
            captured,names,skipped=captured_recipes(with_scanned_operations(capture_db),market)
            catalog=capture_catalog(data['DuckMooCapture'].get('DuckMooCaptureDB',{}))
            for character in data['DuckMooCapture'].get('DuckMooCaptureDB',{}).get('characters',{}).values():
                if character.get('captureStatus'):
                    diagnostics.append({'character':character.get('name'),'realm':character.get('realm'),**character['captureStatus']})
            recipes[:0]=captured
            inventory['names'].update(names)
            if skipped: errors.append(f'DuckMooCapture: {skipped} unsupported or incomplete operations skipped')
        except ValueError as e: errors.append('DuckMooCapture: '+str(e))
    return {'importedAt':datetime.now(timezone.utc).isoformat(),'characters':sorted(characters,key=lambda c:c['name'].casefold()),'recipes':recipes,'catalog':catalog,'acquisitionOffers':offers,'scanCoverage':coverage,'captureDiagnostics':diagnostics,'sources':sources,'errors':errors,'market':market,'inventory':inventory,'limitations':['TSM recipe ownership has no per-recipe capture timestamp in this import.','Material quality choices do not predict output quality.','Minimum-price estimates do not establish available quantity at that price.']}

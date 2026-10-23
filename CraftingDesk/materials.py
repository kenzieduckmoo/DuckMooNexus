"""Local market and inventory adapters. No Lua code is executed."""
import re
from pathlib import Path

APP_DATA = Path(r'D:\World of Warcraft\_retail_\Interface\AddOns\TradeSkillMaster_AppHelper\AppData.lua')

def item_tiers(cache):
    """TSM cache v19: craftedQuality is the last of 24 base64-alphabet chars."""
    if not str(cache.get('versionStr','')).startswith('19,'): return {}
    value=cache.get('itemStrings','')
    chunks=[value] if isinstance(value,str) else [value[k] for k in range(1,len(value)+1)]
    items=[item for chunk in chunks for item in (chunk.split('\x02') if chunk else [])]
    raw=cache.get('data','')
    if isinstance(raw,dict):raw=''.join(raw[k] for k in range(1,len(raw)+1))
    if len(raw)!=24*len(items): raise ValueError('TSM item quality cache length does not match items')
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    result={}
    for index,item in enumerate(items):
        tier=alphabet.find(raw[index*24+23])
        # TSM adds 10 for Midnight's quality icons (ItemInfo.GetCraftedQuality).
        if 11<=tier<=15: tier-=10
        if 1<=tier<=5:result[item]=tier
    return result

def item_names(cache):
    """Decode TSM's parallel LongString lists, preserving exact item identities."""
    def unpack(value):
        if value is None: return []
        if isinstance(value, str): return value.split('\x02') if value else []
        if not isinstance(value, dict) or set(value) != set(range(1, len(value)+1)):
            raise ValueError('Invalid TSM item-name cache chunks')
        result = []
        for i in range(1, len(value)+1):
            if not isinstance(value[i], str): raise ValueError('Invalid TSM item-name cache chunk')
            result.extend(value[i].split('\x02'))
        return result
    names, items = unpack(cache.get('names')), unpack(cache.get('itemStrings'))
    if len(names) != len(items): raise ValueError('TSM item names and IDs do not match')
    return {item: re.sub(r'\|A:.*?\|a', '', name).strip()
            for item, name in zip(items, names)
            if re.fullmatch(r'i:\d+(?::[^\s]*)?', item) and name.strip()}

def market_data(path=APP_DATA):
    text = path.read_text(encoding='utf-8')
    result = {'commodities': {}, 'realms': {}, 'datasets': [], 'sales': {}}
    pattern = r'LoadData\("(AUCTIONDB_[^"]+)","([^"]+)",\[\[return \{downloadTime=(\d+),fields=\{([^}]+)\},data=\{(.*?)\}\}\]\]'
    for m in re.finditer(pattern, text, re.S):
        tag, scope, stamp, fields, body = m.groups()
        if tag not in ('AUCTIONDB_COMMODITY_DATA', 'AUCTIONDB_NON_COMMODITY_DATA', 'AUCTIONDB_REGION_SALE'): continue
        if tag in ('AUCTIONDB_COMMODITY_DATA','AUCTIONDB_REGION_SALE') and scope != 'US': continue
        keys = re.findall(r'"([^"]+)"', fields)
        bucket = result['sales'] if tag == 'AUCTIONDB_REGION_SALE' else result['commodities'] if tag == 'AUCTIONDB_COMMODITY_DATA' else result['realms'].setdefault(scope.replace(' ', '').casefold(), {})
        count = 0
        for row in re.finditer(r'\{"?([^,"{}]+)"?,([^{}]+)\}', body):
            item, values = row.groups()
            item = 'i:' + item if item.isdigit() else item
            vals = values.split(',')
            if len(vals) != len(keys)-1: raise ValueError('TSM market field count changed')
            decoded = dict(zip(keys[1:], (int(v, 32) for v in vals)))
            if tag == 'AUCTIONDB_REGION_SALE':
                bucket[item] = {'saleRate':decoded['regionSalePercent']/1000, 'dailySold':decoded['regionSoldPerDay']/1000, 'at':int(stamp), 'scope':scope, 'source':'TSM regional sales'}
            elif decoded.get('minBuyout', 0) > 0:
                bucket[item] = {'price':decoded['minBuyout'], 'at':int(stamp), 'source':'TSM downloaded snapshot', 'scope':scope}
            count += 1
        result['datasets'].append({'scope':scope, 'at':int(stamp), 'entries':count})
    if not result['datasets']: raise ValueError('No recognized TSM price datasets found')
    return result

def inventory_data(synd):
    items, names = {}, {}
    def walk(value, owner, location):
        if not isinstance(value, dict): return
        if 'itemID' in value and 'itemCount' in value:
            item = 'i:' + str(value['itemID'])
            name = re.search(r'\|h\[(.*?)\]\|h', value.get('itemLink',''))
            if name:
                names[item] = re.sub(r'\|A:.*?\|a', '', name[1]).strip()
            items.setdefault(item, []).append({'owner':owner,'location':location,'quantity':value['itemCount'],'bound':value.get('isBound') is not False})
            return
        for child in value.values(): walk(child,owner,location)
    for key, character in synd.get('Characters',{}).items():
        for location in ('bags','bank'):
            walk(character.get(location,{}),key,location)
    for bank in synd.get('Warband',{}).values():
        walk(bank.get('bank',{}),'Warband','warband')
    return {'items':items,'names':names,'characters':len(synd.get('Characters',{})), 'warbandCaptured':bool(synd.get('Warband'))}

"""TSM v19 metadata decoder, shared format with Crafting Desk materials.py."""
import re

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

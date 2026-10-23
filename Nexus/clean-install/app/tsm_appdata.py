"""Data-only TSM AppData adapter retained from Crafting Desk."""
import re

def market_data(path):
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

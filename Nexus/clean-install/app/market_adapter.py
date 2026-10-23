"""Auctionator day buckets and TSM downloaded quotes, retaining exact identities."""
from datetime import datetime, timezone
from auctionator_codec import decode_cbor

# Auctionator's epoch is local Jan 1 2020 midnight. This account uses Chicago.
# Its day counter advances every 86400 seconds, not civil midnights across DST.
AUCTIONATOR_EPOCH = datetime(2020, 1, 1, 6, tzinfo=timezone.utc).timestamp()


def auctionator_rows(data):
    db = data[b'AUCTIONATOR_PRICE_DATABASE']
    if db.get(b'__dbversion') != 8:
        raise ValueError('Unsupported Auctionator database version')
    for realm, blob in db.items():
        if realm == b'__dbversion':
            continue
        records = decode_cbor(blob)
        if records.get('version')!=2:
            raise ValueError('Unsupported Auctionator realm record version')
        for key, row in records.items():
            if key=='version':continue
            if isinstance(row, str):
                row = decode_cbor(row)
            if not isinstance(row, dict):
                raise ValueError('Invalid Auctionator item record')
            # Preserve variants and realm labels exactly, no guessed commodity scope.
            scope = realm.decode('utf-8')
            def mapping(key):
                value=row.get(key,{})
                if value==[]:return {}
                if not isinstance(value,dict):raise ValueError('Invalid Auctionator price history')
                return value
            for day, high in mapping('h').items():
                day = int(day)
                metrics = dict(lowest_low=mapping('l').get(str(day), high),
                               highest_low=high, highest_quantity=mapping('a').get(str(day)))
                yield scope, str(key), AUCTIONATOR_EPOCH + day*86400, 'day_bucket', day, metrics, 'observed_price_extrema_not_sales'
            yield scope, str(key), None, 'unknown', None, {'last_minimum': row.get('m')}, 'cached_quote_without_source_timestamp'


def tsm_rows(market):
    for item, quote in market.get('commodities', {}).items():
        yield 'US commodities', item, quote['at'], 'second', None, {'min_buyout': quote['price']}, 'TSM_downloaded_quote'
    for scope, items in market.get('realms', {}).items():
        for item, quote in items.items():
            yield scope, item, quote['at'], 'second', None, {'min_buyout': quote['price']}, 'TSM_downloaded_quote'
    for item, quote in market.get('sales', {}).items():
        yield quote['scope'], item, quote['at'], 'second', None, {'region_sale_rate': quote['saleRate'], 'region_sold_per_day': quote['dailySold']}, 'TSM_regional_estimate_not_personal_sales'

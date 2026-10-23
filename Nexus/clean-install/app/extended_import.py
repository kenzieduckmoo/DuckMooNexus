"""Normalized market/crafting adapters using the existing archived snapshot ID."""
import hashlib
from datetime import datetime, timezone
from financials import canonical
from capture_adapter import crafting_rows
from market_adapter import auctionator_rows, tsm_rows
from savedvariables import read_lua
from tsm_appdata import market_data
from character_adapter import CHARACTER_SOURCES,normalize_characters

EXTENDED = ('Auctionator.lua', 'DuckMooCapture.lua', 'TSM_AppData.lua', *CHARACTER_SOURCES)


def utc(stamp):
    return datetime.fromtimestamp(stamp, timezone.utc) if stamp is not None else None


def normalize_extended(conn, path, source, namespace, snapshot_id):
    data = None if source == 'TSM_AppData.lua' else read_lua(path, binary=source=='Auctionator.lua')
    if source in CHARACTER_SOURCES:
        return normalize_characters(conn,data,source,namespace,snapshot_id)
    inserted = records = 0
    with conn.cursor() as cur:
        if source == 'DuckMooCapture.lua':
            cur.execute('CREATE TEMP TABLE source_stage (LIKE nexus.crafting_observations) ON COMMIT DROP')
            with cur.copy('COPY source_stage FROM STDIN') as copy:
                for guid, recipe, kind, key, stamp, payload in crafting_rows(data):
                    oid = hashlib.sha256(canonical([namespace,guid,recipe,kind,key,stamp,payload]).encode()).hexdigest()
                    copy.write_row((oid, namespace, guid, recipe, kind, key, utc(stamp), canonical(payload)))
                    records += 1
            cur.execute('INSERT INTO nexus.crafting_observations SELECT DISTINCT ON(id) * FROM source_stage ON CONFLICT DO NOTHING')
            inserted=cur.rowcount
            cur.execute('INSERT INTO nexus.snapshot_crafting SELECT %s,id FROM source_stage GROUP BY id ON CONFLICT DO NOTHING',(snapshot_id,))
        else:
            rows = auctionator_rows(data) if source=='Auctionator.lua' else tsm_rows(market_data(path))
            cur.execute('CREATE TEMP TABLE source_stage (LIKE nexus.market_observations) ON COMMIT DROP')
            with cur.copy('COPY source_stage FROM STDIN') as copy:
                for scope,item,stamp,precision,day,metrics,quality in rows:
                    oid = hashlib.sha256(canonical([namespace,source,scope,item,stamp,precision,day,metrics,quality]).encode()).hexdigest()
                    copy.write_row((oid, namespace, source, scope, item, utc(stamp), precision, day, canonical(metrics), quality))
                    records += 1
            cur.execute('INSERT INTO nexus.market_observations SELECT DISTINCT ON(id) * FROM source_stage ON CONFLICT DO NOTHING')
            inserted=cur.rowcount
            cur.execute('INSERT INTO nexus.snapshot_market SELECT %s,id FROM source_stage GROUP BY id ON CONFLICT DO NOTHING',(snapshot_id,))
    return inserted, records

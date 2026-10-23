"""Normalize retained TSM item names/quality using Crafting Desk's validated decoder."""
import re
from item_cache import item_names,item_tiers

ITEM_SOURCE='TradeSkillMaster.lua'
ITEM_VERSION='0.5.0-item-metadata1'

def normalize_items(conn,data,namespace,snapshot_id):
    cache=data.get('TSMItemInfoDB',{})
    if not str(cache.get('versionStr','')).startswith('19,'):raise ValueError('Unsupported TSM item metadata version')
    names=item_names(cache);tiers=item_tiers(cache)
    rows=[(namespace,int(key[2:]),name,'TradeSkillMaster item cache') for key,name in names.items() if re.fullmatch(r'i:\d+',key)]
    with conn.cursor() as cur:
        cur.execute('CREATE TEMP TABLE tsm_names(namespace text,item_id bigint,name text,source text) ON COMMIT DROP')
        with cur.copy('COPY tsm_names FROM STDIN') as copy:
            for row in rows:copy.write_row(row)
        cur.execute('INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source) SELECT DISTINCT * FROM tsm_names ON CONFLICT DO NOTHING')
        cur.execute('CREATE TEMP TABLE tsm_quality(namespace text,item_id bigint,crafting_quality integer,snapshot_id bigint,source text) ON COMMIT DROP')
        with cur.copy('COPY tsm_quality FROM STDIN') as copy:
            for key,tier in tiers.items():
                if re.fullmatch(r'i:\d+',key):copy.write_row((namespace,int(key[2:]),tier,snapshot_id,ITEM_SOURCE))
        cur.execute('INSERT INTO nexus.item_quality_evidence SELECT DISTINCT * FROM tsm_quality ON CONFLICT DO NOTHING')
    return len(rows)

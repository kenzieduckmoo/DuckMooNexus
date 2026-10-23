"""Syndicator cached locations. File saves do not date individual items."""
import hashlib
import re
from financials import canonical
from psycopg.types.json import Jsonb

INVENTORY_SOURCE='Syndicator.lua'
INVENTORY_VERSION='0.5.0-inventory1'


def items(data):
    db=data['SYNDICATOR_DATA']
    if db.get('Version')!=2:raise ValueError('Unsupported Syndicator schema')
    def walk(value,path=()):
        if not isinstance(value,dict):return
        if value.get('itemID'):
            if type(value['itemID']) is not int or type(value.get('itemCount')) is not int or value['itemCount']<=0:
                raise ValueError('Invalid inventory item identity or quantity')
            yield '/'.join(path),value
        else:
            for k,v in value.items():
                if isinstance(v,dict):yield from walk(v,(*path,str(k)))
    for group,kind in (('Characters','character'),('Warband','warband'),('Guilds','guild')):
        for owner,entity in db.get(group,{}).items():
            locations=('bags','bank','bankTabs','equipped','mail','auctions','void') if kind=='character' else ('bank',)
            for location in locations:
                # Modern tabs supersede the retained legacy bank container.
                if location=='bank' and kind=='character' and entity.get('bankTabs'):continue
                for slot,row in walk(entity.get(location,{})):
                    link=row.get('itemLink') or ''
                    label=re.search(r'\|h\[([^]]+)\]',link)
                    raw_name=label.group(1) if label else None
                    name=re.sub(r'\|A:.*?\|a','',raw_name).strip() if raw_name else None
                    tier=re.search(r'Professions-ChatIcon-Quality-[^:|]*?Tier(\d+)',link)
                    body=dict(owner_kind=kind,owner_key=str(owner),location=location,slot_key=slot,
                        item_id=row['itemID'],quantity=row['itemCount'],name=name,item_link=link,
                        rarity=row.get('quality'),crafting_quality=int(tier.group(1)) if tier else None,
                        is_bound=row.get('isBound'),payload=row)
                    yield body


def normalize_inventory(conn,data,namespace,snapshot_id):
    rows=list(items(data));inserted=0
    conn.execute('''CREATE TEMP TABLE inventory_stage(LIKE nexus.inventory_records INCLUDING DEFAULTS) ON COMMIT DROP''')
    with conn.cursor().copy('COPY inventory_stage FROM STDIN') as copy:
        for row in rows:
            identity=hashlib.sha256(canonical([namespace,row]).encode()).hexdigest()
            copy.write_row((identity,namespace,row['owner_kind'],row['owner_key'],row['location'],row['slot_key'],
                row['item_id'],row['quantity'],row['name'],row['item_link'],row['rarity'],row['crafting_quality'],row['is_bound'],Jsonb(row['payload'])))
    inserted=conn.execute('INSERT INTO nexus.inventory_records SELECT * FROM inventory_stage ON CONFLICT DO NOTHING').rowcount
    conn.execute('''INSERT INTO nexus.snapshot_inventory SELECT %s,id FROM inventory_stage ON CONFLICT DO NOTHING''',(snapshot_id,))
    conn.execute('''INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source)
        SELECT DISTINCT namespace,item_id,name,'Syndicator' FROM inventory_stage WHERE nullif(name,'') IS NOT NULL ON CONFLICT DO NOTHING''')
    conn.execute('''INSERT INTO nexus.inventory_snapshot_coverage(snapshot_id,characters,guilds,warbanks,stacks)
        VALUES(%s,%s,%s,%s,%s) ON CONFLICT(snapshot_id) DO UPDATE SET stacks=excluded.stacks''',
        (snapshot_id,len(data['SYNDICATOR_DATA'].get('Characters',{})),len(data['SYNDICATOR_DATA'].get('Guilds',{})),len(data['SYNDICATOR_DATA'].get('Warband',{})),len(rows)))
    return inserted,len(rows)

"""Build the Crafting Desk model from preserved PostgreSQL sources and views."""
import gzip
import json
import os
from pathlib import Path
import tempfile
import psycopg
from psycopg.rows import dict_row
from importer import assemble

ACCOUNT=os.environ.get('NEXUS_ACCOUNT','retail-main-account')
REALMS={11:['Tichondrius'],57:['Illidan'],61:["Zul'jin"],63:['Ysera'],76:['Sargeras'],99:['Llane'],
 104:['Garona','Malygos'],162:['EmeraldDream'],1426:['AeriePeak'],3675:['MoonGuard'],3685:['Turalyon'],
 3721:['Saurfang'],3726:["Aman'Thul","Khaz'goroth"]}


def lua_keys(value):
    if isinstance(value,dict):return {int(k) if isinstance(k,str) and k.isdigit() else k:lua_keys(v) for k,v in value.items()}
    if isinstance(value,list):return [lua_keys(v) for v in value]
    return value


def build(conn):
    data={'DuckMooFolio':{'DuckMooFolioDB':{'characters':{}}},'DuckMooPlanner':{'DuckMooPlannerDB':{'characters':{}}}}
    sources=[]
    latest=conn.execute('''SELECT DISTINCT ON(source) id,source,source_saved_at,captured_at
      FROM nexus.source_snapshots WHERE namespace=%s
      AND (source='TradeSkillMaster.lua' OR normalized_version IS NOT NULL)
      ORDER BY source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''',(ACCOUNT,)).fetchall()
    for row in latest:
        if row['source'] in ('DuckMooCapture.lua','DuckMooFolio.lua','DuckMooPlanner.lua','DuckMooOmniCapture.lua','Syndicator.lua','TSM_AppData.lua','Auctionator.lua'):
            sources.append({'name':row['source'].removesuffix('.lua'),'snapshotId':row['id'],
                'savedAt':row['source_saved_at'].timestamp() if row['source_saved_at'] else None})
    for row in conn.execute("SELECT source,character_guid,payload FROM nexus.current_character_records WHERE namespace=%s AND record_kind='profile'",(ACCOUNT,)):
        key=row['source'].removesuffix('.lua');data[key][key+'DB']['characters'][row['character_guid']]=lua_keys(row['payload'])
    omni={'schema':1,'characters':{}}
    for row in conn.execute("SELECT character_guid,record_kind,record_key,payload FROM nexus.current_omni_records WHERE namespace=%s AND (record_kind='omni_identity' OR record_kind='omni_section' AND record_key IN('profile','knowledge','currencies'))",(ACCOUNT,)):
        c=omni['characters'].setdefault(row['character_guid'],{'guid':row['character_guid'],'sections':{}})
        if row['record_kind']=='omni_identity':c.update(lua_keys(row['payload']))
        else:c['sections'][row['record_key']]=lua_keys(row['payload'])
    data['DuckMooOmniCapture']={'DuckMooOmniCaptureDB':omni}
    # TSM craft ownership/name metadata is still a raw-only source; read its
    # preserved DB archive, never a Windows path or the user's old JSON snapshot.
    tsm=next((r for r in latest if r['source']=='TradeSkillMaster.lua'),None)
    if tsm:
        from savedvariables import read_lua
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'tsm.gz';raw=Path(folder)/'TradeSkillMaster.lua'
            with archive.open('wb') as out:
                for row in conn.execute('SELECT compressed_bytes FROM nexus.snapshot_chunks WHERE snapshot_id=%s ORDER BY ordinal',(tsm['id'],)):out.write(row['compressed_bytes'])
            with gzip.open(archive,'rb') as inp,raw.open('wb') as out:
                while block:=inp.read(1024**2):out.write(block)
            data['TradeSkillMaster']=read_lua(raw)
    capture={'schemaVersion':1,'characters':{}}
    query='''WITH latest AS (SELECT id FROM nexus.source_snapshots WHERE namespace=%s AND source='DuckMooCapture.lua'
      AND normalized_version IS NOT NULL ORDER BY source_saved_at DESC NULLS LAST,captured_at DESC,id DESC LIMIT 1)
      SELECT o.character_guid,o.recipe_id,o.kind,o.operation_key,o.payload FROM latest s
      JOIN nexus.snapshot_crafting l ON l.snapshot_id=s.id JOIN nexus.crafting_observations o ON o.id=l.observation_id
      ORDER BY CASE o.kind WHEN 'character' THEN 0 WHEN 'scan_definition' THEN 1 ELSE 2 END'''
    for row in conn.execute(query,(ACCOUNT,)):
        c=capture['characters'].setdefault(row['character_guid'],{})
        kind,key,payload=row['kind'],row['operation_key'],row['payload']
        if kind=='character':c.update(payload)
        elif kind=='catalog':c.setdefault('recipes',{})[row['recipe_id']]=payload
        elif kind=='scan_definition':c.setdefault('scannedRecipes',{})[row['recipe_id']]={**payload,'outcomes':{}}
        elif kind=='scan_outcome':c.setdefault('scannedRecipes',{}).setdefault(row['recipe_id'],{'outcomes':{}})['outcomes'][key]=payload
        elif kind=='selected_operation':c.setdefault('operations',{})[key]=payload
        elif kind=='acquisition_offer':c.setdefault('acquisitionOffers',{})[key]=payload
        elif kind=='scan_status':c.setdefault('scanStatus',{})[int(key)]=payload
        elif kind=='capture_status':c['captureStatus']=payload
    data['DuckMooCapture']={'DuckMooCaptureDB':capture}
    inventory={'items':{},'names':{},'tiers':{},'characters':0,'warbandCaptured':False}
    owners=set()
    for row in conn.execute('SELECT * FROM nexus.current_inventory WHERE namespace=%s',(ACCOUNT,)):
        item='i:'+str(row['item_id'])
        if row['name']:inventory['names'][item]=row['name']
        if row['crafting_quality']:inventory['tiers'][item]=row['crafting_quality']
        if row['owner_kind']=='character':owners.add(row['owner_key'])
        if row['owner_kind']=='warband':inventory['warbandCaptured']=True
        if row['owner_kind']=='guild' or row['location'] not in ('bags','bank','bankTabs'):continue
        location='warband' if row['owner_kind']=='warband' else 'bank' if row['location']=='bankTabs' else row['location']
        inventory['items'].setdefault(item,[]).append({'owner':'Warband' if location=='warband' else row['owner_key'],
            'location':location,'quantity':row['quantity'],'bound':row['is_bound'] is not False})
    inventory['characters']=len(owners)
    for row in conn.execute('SELECT item_id,name FROM nexus.item_catalog WHERE namespace=%s',(ACCOUNT,)):
        inventory['names'].setdefault('i:'+str(row['item_id']),row['name'])
    market={'commodities':{},'realms':{},'datasets':[],'sales':{},'auctionator':{'commodities':{},'realms':{},'warnings':[]}}
    # TSM downloaded observations retain sale-rate semantics. Historical daily
    # extrema are not promoted into fresh executable AH quotes.
    q='''WITH latest AS (SELECT id FROM nexus.source_snapshots WHERE namespace=%s AND source='TSM_AppData.lua'
      AND normalized_version IS NOT NULL ORDER BY source_saved_at DESC NULLS LAST,captured_at DESC,id DESC LIMIT 1)
      SELECT o.scope,o.item_key,o.observed_at,o.metrics FROM latest s JOIN nexus.snapshot_market l ON l.snapshot_id=s.id
      JOIN nexus.market_observations o ON o.id=l.observation_id'''
    for row in conn.execute(q,(ACCOUNT,)):
        at=row['observed_at'].timestamp() if row['observed_at'] else None
        if at is None:continue
        item=row['item_key'];item='i:'+item if item.isdigit() else item;metrics=row['metrics']
        if 'region_sale_rate' in metrics:
            market['sales'][item]={'saleRate':metrics['region_sale_rate'],'dailySold':metrics.get('region_sold_per_day'),'at':at,'scope':row['scope'],'source':'TSM regional sales'}
        elif metrics.get('min_buyout',0)>0:
            quote={'price':metrics['min_buyout'],'at':at,'scope':row['scope'],'source':'TSM downloaded snapshot'}
            bucket=market['commodities'] if row['scope']=='US commodities' else market['realms'].setdefault(row['scope'].replace(' ','').casefold(),{})
            bucket[item]=quote
    for row in conn.execute("SELECT scope,item_id,min(lowest_unit_copper) AS price,max(source_modified_at) AS at FROM nexus.latest_auction_prices WHERE region='us' GROUP BY scope,item_id"):
        if row['price'] is None or row['at'] is None:continue
        item='i:'+str(row['item_id']);scope=row['scope']
        quote={'price':float(row['price']),'at':row['at'].timestamp(),'scope':'US commodities' if scope=='commodities' else scope,'source':'Blizzard AH snapshot'}
        buckets=[market['commodities']] if scope=='commodities' else [market['realms'].setdefault(r.replace(' ','').casefold(),{}) for r in REALMS.get(int(scope.split(':')[1]),[])]
        for bucket in buckets:
            if item not in bucket or quote['at']>=bucket[item]['at']:bucket[item]=quote
    result=assemble(data,sources,[],market_override=market,inventory_override=inventory)
    result['dataHost']='Nexus';return result


def _refresh(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row) as conn:
        conn.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        # Archiving commits before normalization. Track each usable source,
        # rather than a global raw max(id), so a finishing import cannot be
        # hidden behind a newer archive or unrelated source. TSM ownership is
        # intentionally raw-only and its committed archive is immediately usable.
        signature=conn.execute('''WITH latest AS (
          SELECT DISTINCT ON(source) source,id,normalized_version
          FROM nexus.source_snapshots WHERE namespace=%s
          AND source IN('TradeSkillMaster.lua','DuckMooCapture.lua','DuckMooFolio.lua','DuckMooPlanner.lua',
            'DuckMooOmniCapture.lua','Syndicator.lua','TSM_AppData.lua','Auctionator.lua')
          AND (source='TradeSkillMaster.lua' OR normalized_version IS NOT NULL)
          ORDER BY source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC)
          SELECT json_build_array('crafting-0.9.3',
            (SELECT json_agg(json_build_array(source,id,normalized_version) ORDER BY source) FROM latest),
            (SELECT max(id) FROM nexus.api_snapshots WHERE region='us')) AS signature''',(ACCOUNT,)).fetchone()['signature']
        checkpoint=folder/'source-signature.json'
        if checkpoint.exists() and json.loads(checkpoint.read_text())==signature and (folder/'local-data.json.gz').exists():return False
        model=build(conn)
    temporary=folder/'local-data.json.gz.tmp'
    with gzip.open(temporary,'wt',encoding='utf-8',compresslevel=3) as out:
        json.dump(model,out,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    temporary.replace(folder/'local-data.json.gz')
    pending=checkpoint.with_suffix('.tmp');pending.write_text(json.dumps(signature));pending.replace(checkpoint)
    status=folder/'status.json';pending=status.with_suffix('.tmp')
    pending.write_text(json.dumps({'importedAt':model['importedAt'],'recipes':len(model['recipes']),'characters':len(model['characters'])}));pending.replace(status)
    return True


def refresh(folder):
    import fcntl
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'.refresh.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _refresh(folder)


if __name__=='__main__':print('Snapshot updated:',refresh(os.environ.get('CRAFTING_STATE','/crafting-state')))

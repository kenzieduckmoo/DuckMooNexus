"""Inventory lookup backed by shared normalized stock views."""
import json
from pathlib import Path
from build_dashboards import dashboard,panel,DS,NS
from table_display import format_table


def build_inventory():
    m=dashboard('duckmoo-warband-inventory','DuckMoo Nexus | Warband Inventory',
        'Search cached item names across characters, the Warbank and guild banks. Individual item observation times are unavailable.')
    m['templating']['list'].extend([
        dict(name='item_search',label='Item name or ID',type='textbox',query='',current={'text':'','value':''}),
        dict(name='owner',label='Owner',type='query',datasource=DS,
            query="SELECT DISTINCT owner_kind||': '||owner_key AS __text,owner_kind||':'||owner_key AS __value FROM nexus.current_inventory WHERE namespace=${account:sqlstring} ORDER BY 1",
            multi=True,includeAll=True,refresh=1,current={'text':'All','value':'$__all'}),
        dict(name='location',label='Location',type='query',datasource=DS,
            query='SELECT DISTINCT location FROM nexus.current_inventory WHERE namespace=${account:sqlstring} ORDER BY 1',
            multi=True,includeAll=True,refresh=1,current={'text':'All','value':'$__all'})])
    base="""FROM nexus.inventory_totals WHERE namespace=${account:sqlstring}
      AND (strpos(lower(coalesce(name,'')),lower(${item_search:sqlstring}))>0 OR item_id::text=${item_search:sqlstring})
      AND owner_kind||':'||owner_key IN (${owner:sqlstring}) AND location IN (${location:sqlstring})"""
    panel(m,'Matching stock by owner and location',f'''SELECT name AS item,crafting_quality AS crafting_rank,
       owner_kind,owner_key AS owner,location,quantity,is_bound,rarity,item_id,snapshot_file_saved_at {base}
       ORDER BY name,crafting_quality NULLS LAST,owner_kind,owner_key,location LIMIT 1000''',width=24,height=13,
       description='Partial names work. Crafting rank stays separate from item rarity. Guild stock, equipped items, mail and auctions are shown with their own location; they are not automatically usable crafting supplies. Timestamp is the source file save, not a fresh inspection of each item.')
    panel(m,'Matching totals by item and storage',f'''SELECT name AS item,crafting_quality AS crafting_rank,
       owner_kind,location,is_bound,sum(quantity) AS quantity,item_id {base}
       GROUP BY name,crafting_quality,owner_kind,location,is_bound,item_id ORDER BY name,crafting_quality,owner_kind,location LIMIT 500''',width=24,height=10)
    panel(m,'Inventory capture coverage',"""SELECT c.characters,c.guilds,c.warbanks,c.stacks,s.source_saved_at AS file_saved_at,
        s.captured_at,s.normalized_version FROM nexus.inventory_snapshot_coverage c
        JOIN nexus.source_snapshots s ON s.id=c.snapshot_id WHERE s.namespace=${account:sqlstring}
        ORDER BY s.source_saved_at DESC NULLS LAST,s.captured_at DESC LIMIT 1""",width=24,
        description='A newer file can still contain old offline-character caches. No per-item observation date is supplied by this source.')
    m['links']=[{'title':t,'type':'link','url':u,'targetBlank':False} for t,u in (
        ('Character Observatory','/d/duckmoo-character-observatory'),('Auction Analysis','/d/duckmoo-azeroth-stock-exchange'),
        ('Warband Financials','/d/duckmoo-warband-financials'))]
    for obj in m['panels']:format_table(obj)
    return m


if __name__=='__main__':
    out=Path(__file__).parent/'dashboard-seeds';out.mkdir(exist_ok=True)
    (out/'warband-inventory.json').write_text(json.dumps(build_inventory(),indent=2))

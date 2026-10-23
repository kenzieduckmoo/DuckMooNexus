"""Name-searchable market reporting over shared PostgreSQL views."""
import json
from pathlib import Path
from build_dashboards import dashboard,panel,DS,NS
from table_display import format_table


def build_market():
    m=dashboard('duckmoo-azeroth-stock-exchange','DuckMoo Nexus | Azeroth Stock Exchange',
        'Search by item name. Blizzard listings, cached observations and confirmed personal transactions stay distinct.')
    variables=m['templating']['list']
    variables.append(dict(name='item_search',label='Find item by name',type='textbox',query='Bismuth',
        current={'text':'Bismuth','value':'Bismuth'}))
    query="""SELECT name||' ['||item_id::text||']' AS __text,item_id::text AS __value
        FROM nexus.item_catalog WHERE namespace=${account:sqlstring}
        AND (EXISTS(SELECT 1 FROM unnest(aliases) n WHERE strpos(lower(n),lower(${item_search:sqlstring}))>0)
          OR item_id::text=${item_search:sqlstring}) ORDER BY name,item_id LIMIT 500"""
    variables.append(dict(name='item',label='Matching item',type='query',datasource=DS,query=query,
        refresh=1,sort=0,multi=False,includeAll=False,current={}))
    variables.append(dict(name='market_scope',label='Addon market',type='query',datasource=DS,
        query='SELECT DISTINCT scope FROM nexus.market_observations WHERE namespace=${account:sqlstring} ORDER BY 1',
        refresh=1,multi=True,includeAll=True,current={'text':'All','value':'$__all'}))
    item="item_key IN (${item:sqlstring},'i:'||${item:sqlstring})"
    base=f"FROM nexus.market_observations WHERE {NS} AND {item} AND scope IN (${{market_scope:sqlstring}})"
    panel(m,'Current Blizzard asking prices',"""SELECT p.scope,p.item_id,c.name,p.quantity,p.listings,
        p.lowest_unit_copper/10000.0 AS lowest_unit_gold,p.item_variant,
        p.source_modified_at,p.fetched_at FROM nexus.latest_auction_prices p
        LEFT JOIN nexus.item_catalog c ON c.namespace=${account:sqlstring} AND c.item_id=p.item_id
        WHERE p.region='us' AND p.item_id=substring(${item:sqlstring} FROM '^[0-9]{1,18}$')::bigint ORDER BY p.scope,p.lowest_unit_copper""",
        width=24,description='Latest preserved snapshot per market. Asking prices are not completed sales. Variant details remain separate. Source update and fetch time are shown separately.')
    panel(m,'Blizzard asking price over time',"""SELECT coalesce(s.source_modified_at,s.fetched_at) AS time,s.scope AS metric,
        min(coalesce(a.unit_price_copper,a.buyout_copper::numeric/nullif(a.quantity,0)))/10000.0 AS value
        FROM nexus.api_snapshots s JOIN nexus.auction_listings a ON a.snapshot_id=s.id
        WHERE s.region='us' AND a.item_id=substring(${item:sqlstring} FROM '^[0-9]{1,18}$')::bigint AND $__timeFilter(s.fetched_at)
        GROUP BY 1,2 ORDER BY 1""",'timeseries','suffix:g',width=24,
        description='Lowest asking price across variants in each market; consult the current listing table for exact variants.')
    panel(m,'Blizzard observed listing supply',"""SELECT coalesce(s.source_modified_at,s.fetched_at) AS time,s.scope AS metric,sum(a.quantity) AS value
        FROM nexus.api_snapshots s JOIN nexus.auction_listings a ON a.snapshot_id=s.id
        WHERE s.region='us' AND a.item_id=substring(${item:sqlstring} FROM '^[0-9]{1,18}$')::bigint AND $__timeFilter(s.fetched_at)
        GROUP BY 1,2 ORDER BY 1""",'timeseries',description='Listing disappearance can reflect cancellation, expiry or relisting; it is not sales volume.')
    panel(m,'Auctionator daily price range for selected item',f"SELECT observed_at AS time,scope||' low' AS metric,(metrics->>'lowest_low')::numeric/10000.0 AS value {base} AND time_precision='day_bucket' AND $__timeFilter(observed_at) ORDER BY 1",'timeseries','suffix:g')
    panel(m,'Auctionator observed daily peak availability',f"SELECT observed_at AS time,scope AS metric,(metrics->>'highest_quantity')::numeric AS value {base} AND time_precision='day_bucket' AND $__timeFilter(observed_at) ORDER BY 1",'timeseries')
    panel(m,'TSM downloaded prices',f"SELECT observed_at AS time,scope AS metric,(metrics->>'min_buyout')::numeric/10000.0 AS value {base} AND metrics ? 'min_buyout' AND $__timeFilter(observed_at) ORDER BY 1",'timeseries','suffix:g')
    panel(m,'Selected item: observations across markets',f'SELECT scope,source,observed_at,time_precision,metrics,quality {base} ORDER BY observed_at DESC NULLS LAST LIMIT 200',description='Daily extrema, cached quotes and regional estimates retain their source meaning.')
    panel(m,'Confirmed personal transactions for selected item',f"SELECT occurred_at,character,realm,category,subtype,item_name,quantity,invoice_value_copper/10000.0 AS invoice_g FROM nexus.transactions WHERE {NS} AND item_id::text=${{item:sqlstring}} AND $__timeFilter(occurred_at) ORDER BY occurred_at DESC LIMIT 200")
    panel(m,'API collection status','SELECT region,scope,status,last_attempt,last_success,next_attempt FROM nexus.api_worker_status ORDER BY region,scope',width=24)
    panel(m,'Source refresh and API poll health','SELECT p.region,p.scope,p.fetched_at,p.status,s.source_modified_at,s.auction_count FROM nexus.api_polls p LEFT JOIN nexus.api_snapshots s ON s.id=p.snapshot_id ORDER BY p.fetched_at DESC LIMIT 100',width=24)
    panel(m,'Item-name coverage',"SELECT count(*) AS named_item_ids FROM nexus.item_catalog WHERE namespace=${account:sqlstring}",'stat',description='Names come from preserved item hyperlinks and transactions. Items with no known name will be enriched separately.')
    panel(m,'Crafting observation coverage',f'SELECT kind,count(*) AS observations,max(observed_at) AS newest FROM nexus.crafting_observations WHERE {NS} GROUP BY kind',description='Operation previews and outcomes are not completed crafts or realized profits.')
    m['links']=[{'title':title,'type':'link','url':url,'targetBlank':False} for title,url in (
        ('Warband Financials','/d/duckmoo-warband-financials'),('Character Observatory','/d/duckmoo-character-observatory'),
        ('Warband Inventory','/d/duckmoo-warband-inventory'))]
    for obj in m['panels']:format_table(obj)
    return m


if __name__=='__main__':
    out=Path(__file__).parent/'dashboard-seeds';out.mkdir(exist_ok=True)
    (out/'azeroth-stock-exchange.json').write_text(json.dumps(build_market(),indent=2))

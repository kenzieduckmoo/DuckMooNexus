"""Generate importable Grafana dashboards using PostgreSQL source tables/views."""
import json
from pathlib import Path

DS={'type':'grafana-postgresql-datasource','uid':'duckmoo-postgres'}
NS='namespace=${account:sqlstring}'
FIN='FROM nexus.cash_financial_components WHERE '+NS+' AND $__timeFilter(occurred_at)'


def dashboard(uid,title,description):
    return dict(uid=uid,title=title,description=description,schemaVersion=39,version=1,timezone='browser',editable=True,
                time={'from':'now-90d','to':'now'},refresh='5m',tags=['DuckMoo Nexus'],
                templating={'list':[dict(name='account',label='Account',type='query',datasource=DS,
                query='SELECT DISTINCT namespace FROM nexus.imports UNION SELECT DISTINCT namespace FROM nexus.source_snapshots',
                current={'text':'retail-main-account','value':'retail-main-account'},refresh=1)]},panels=[])


def panel(db,title,query,kind='table',unit='none',description='',width=12,height=8):
    i=len(db['panels']); y=max((p['gridPos']['y']+p['gridPos']['h'] for p in db['panels']),default=0)
    # Two-column rows except deliberately full-width text/history panels.
    x=0
    if i and width==12:
        prev=db['panels'][-1]
        if prev['gridPos']['w']==12 and prev['gridPos']['x']==0 and prev['gridPos']['h']==height:
            x=12;y=prev['gridPos']['y']
    obj=dict(id=i+1,title=title,type=kind,description=description,datasource=DS,
             gridPos=dict(x=x,y=y,w=width,h=height),
             fieldConfig={'defaults':{'unit':unit,'decimals':2 if unit=='suffix:g' else 0,'noValue':'No recorded data'},'overrides':[]},
             targets=[dict(refId='A',datasource=DS,rawSql=query,format='time_series' if kind=='timeseries' else 'table',rawQuery=True)],
             options={})
    if kind=='stat':obj['options']={'reduceOptions':{'calcs':['lastNotNull'],'fields':'','values':False},'colorMode':'value','graphMode':'none'}
    db['panels'].append(obj)
    return obj


def fixed_color(obj, color):
    obj['fieldConfig']['defaults']['color']={'mode':'fixed','fixedColor':color}


def net_colors(obj):
    obj['fieldConfig']['defaults'].update(color={'mode':'thresholds'},thresholds={
        'mode':'absolute','steps':[{'color':'red','value':None},
                                 {'color':'text','value':0},{'color':'green','value':0.0001}]})


def patron_panels(db):
    base="FROM nexus.crafting_order_financials WHERE "+NS+" AND order_kind='Patron'"
    variables=db['templating']['list']
    for name,label,column,extra in (
        ('patron_character','Patron character','character_key',''),
        ('patron_profession','Patron profession','profession',
         ' AND character_key IN (${patron_character:sqlstring})')):
        variables.append(dict(name=name,label=label,type='query',datasource=DS,
            query=f'SELECT DISTINCT {column} {base}{extra} ORDER BY 1',
            multi=True,includeAll=True,refresh=1,sort=1,
            current={'text':'All','value':'$__all','selected':True}))
    filters=" AND character_key IN (${patron_character:sqlstring}) AND profession IN (${patron_profession:sqlstring})"
    selected=base+filters+' AND $__timeFilter(occurred_at)'
    total=panel(db,'Patron-order gold received',f'SELECT sum(net_copper)/10000.0 AS gold {selected}',
        'stat','suffix:g','Selected period. Recorded patron commissions minus order cuts; supplied materials are not deducted.',height=5)
    fixed_color(total,'green')
    fixed_color(panel(db,'Patron orders completed',f'SELECT count(*) AS orders {selected}',
          'stat',description='Completed NPC patron orders, excluding public, guild and personal orders.',height=5),'text')
    # Opening and closing points keep the full recorded running total visible even
    # when no orders occurred within the selected period. Same-time orders aggregate.
    cumulative=f'''WITH amounts AS (
 SELECT occurred_at,net_copper {base}{filters} AND gold_complete
 AND occurred_at <= $__timeTo()
), points AS (
 SELECT $__timeFrom() AS time,coalesce(sum(net_copper),0) AS copper
 FROM amounts WHERE occurred_at < $__timeFrom()
 UNION ALL SELECT occurred_at,sum(net_copper) FROM amounts
 WHERE occurred_at >= $__timeFrom() GROUP BY occurred_at
 UNION ALL SELECT $__timeTo(),0
), totals AS (
 SELECT time,sum(sum(copper)) OVER (ORDER BY time)/10000.0 AS gold FROM points GROUP BY time
)
SELECT time,gold AS "Patron-order gold" FROM totals ORDER BY time'''
    history=panel(db,'Patron-order gold over time',cumulative,'timeseries','suffix:g',
        'Cumulative across all captured history for the selected characters/professions. Opening balance includes earlier orders. Raw gold after cuts, before supplied-material costs.',width=24,height=10)
    fixed_color(history,'green')
    history['fieldConfig']['defaults']['custom']={'drawStyle':'line','lineInterpolation':'stepAfter','fillOpacity':12,'spanNulls':False}
    daily=panel(db,'Daily patron-order gold',
        f"SELECT date_trunc('day',occurred_at,'America/Chicago') AS time,sum(net_copper)/10000.0 AS gold {selected} GROUP BY 1 ORDER BY 1",
        'timeseries','suffix:g','Recorded gold after order cuts, before supplied-material costs.',width=24)
    fixed_color(daily,'green')
    panel(db,'Patron gold by character and profession',
        f'''SELECT character,realm,profession,count(*) AS orders,
 sum(gross_copper)/10000.0 AS commission_g,sum(cut_copper)/10000.0 AS cuts_g,
 sum(net_copper)/10000.0 AS received_g,
 count(*) FILTER(WHERE NOT gold_complete) AS incomplete_gold_records
 {selected} GROUP BY 1,2,3 ORDER BY received_g DESC NULLS LAST''',width=24,
        description='Profession comes from a matching captured recipe. Unknown professions remain included.')
    panel(db,'Patron-order history',
        f'''SELECT occurred_at AS completed_at,character,realm,profession,item_name,
 gross_copper/10000.0 AS commission_g,cut_copper/10000.0 AS cut_g,
 net_copper/10000.0 AS received_g,supplied_materials {selected}
 ORDER BY occurred_at DESC,id LIMIT 250''',width=24,
        description='Latest 250 orders in the selected period. Completion time is recorded by Journalator; it is not a mailbox-collection timestamp.')
    panel(db,'Patron data coverage',
        f'''SELECT count(*) AS orders,count(*) FILTER(WHERE profession='Unknown profession') AS unknown_profession,
 count(*) FILTER(WHERE NOT gold_complete) AS incomplete_gold_records,
 min(occurred_at) AS first_order,max(occurred_at) AS latest_order {selected}''',width=24,
        description='Missing payment fields are excluded from gold totals. Item/currency rewards are not assigned a gold value.')
    for obj in db['panels']:
        if obj['id']<17 or obj['type']!='table':continue
        names={'character':'Character','realm':'Realm','profession':'Profession','orders':'Orders',
               'commission_g':'Commission','cuts_g':'Order cuts','cut_g':'Order cut','received_g':'Gold received',
               'incomplete_gold_records':'Missing payment fields','completed_at':'Completed',
               'item_name':'Item','supplied_materials':'Supplied materials',
               'unknown_profession':'Unknown profession','first_order':'First order','latest_order':'Latest order'}
        for name,label in names.items():
            props=[{'id':'displayName','value':label}]
            if name.endswith('_g'):props.extend([{'id':'unit','value':'suffix:g'},{'id':'decimals','value':2}])
            obj['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':name},'properties':props})
        for name,color in [('received_g','green'),('cut_g','red'),('cuts_g','red')]:
            obj['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':name},
                'properties':[{'id':'color','value':{'mode':'fixed','fixedColor':color}}]})


def cashflow_panels(db):
    cash='FROM nexus.recorded_cash_events WHERE '+NS+' AND $__timeFilter(occurred_at)'
    auction='FROM nexus.auction_deposit_events WHERE '+NS+' AND $__timeFilter(occurred_at)'
    net_colors(panel(db,'Net recorded gold after deposits',
        f'SELECT sum(net_copper)/10000.0 AS gold {cash}', 'stat','suffix:g',
        'Selected period: recorded income minus spending and fees, minus posting deposits plus returned deposits. Internal transfers and unresolved mail/trades are excluded. This is cash flow, not profit on sold inventory.',height=5))
    outflow=panel(db,'Net auction-deposit outflow',
        f"SELECT -sum(deposit_movement_copper)/10000.0 AS gold {cash}",
        'stat','suffix:g','Posting deposits minus refunds received during the selected period. Includes lost deposits, still-held deposits and unmatched history. A negative value means more deposits were returned than posted in this period.',height=5)
    outflow['fieldConfig']['defaults'].update(color={'mode':'thresholds'},thresholds={
        'mode':'absolute','steps':[{'color':'green','value':None},
                                 {'color':'text','value':0},{'color':'red','value':0.0001}]})
    cumulative=f'''WITH events AS MATERIALIZED (
 SELECT occurred_at,net_copper {cash} AND net_copper IS NOT NULL
), points AS (
 SELECT $__timeFrom() AS time,0::numeric AS copper
 UNION ALL SELECT occurred_at,sum(net_copper) FROM events GROUP BY occurred_at
 UNION ALL SELECT $__timeTo(),0
)
SELECT time,sum(sum(copper)) OVER (ORDER BY time)/10000.0 AS "Net recorded gold"
FROM points GROUP BY time ORDER BY time'''
    graph=panel(db,'Net recorded gold over time',cumulative,'timeseries','suffix:g',
        'Starts at zero at the beginning of the selected period. Includes recorded listing deposits and refunds, alongside income and spending. Inventory purchases count when recorded; this is not a sale-by-sale profit calculation.',width=24,height=10)
    fixed_color(graph,'blue')
    graph['fieldConfig']['defaults']['custom']={'drawStyle':'line','lineInterpolation':'stepAfter','fillOpacity':10,'spanNulls':False}
    table=panel(db,'Auction deposits and outcomes by character',
        f'''SELECT character,realm,
 count(*) FILTER(WHERE event_kind='posting') AS posted,
 count(*) FILTER(WHERE event_kind='refund') AS sale_refunds,
 count(*) FILTER(WHERE event_kind='expired') AS expired,
 count(*) FILTER(WHERE event_kind='cancelled') AS cancelled,
 coalesce(sum(deposit_copper) FILTER(WHERE event_kind='posting'),0)/10000.0 AS posted_g,
 coalesce(sum(deposit_copper) FILTER(WHERE event_kind='refund'),0)/10000.0 AS refunded_g,
 (coalesce(sum(deposit_copper) FILTER(WHERE event_kind='posting'),0)
  -coalesce(sum(deposit_copper) FILTER(WHERE event_kind='refund'),0))/10000.0 AS outflow_g,
 count(*) FILTER(WHERE event_kind IN ('posting','refund') AND deposit_copper IS NULL) AS missing_amounts
 {auction} GROUP BY character,realm ORDER BY outflow_g DESC''',width=24,
        description='Failure records do not contain deposit amounts or auction IDs, so failed auctions cannot be assigned an exact gold loss. Posting records are captured from posting requests; refunds are recorded when sale mail is collected.')
    names={'character':'Character','realm':'Realm','posted':'Postings','sale_refunds':'Sale refunds',
           'expired':'Expired','cancelled':'Cancelled','posted_g':'Deposits recorded',
           'refunded_g':'Deposits returned','outflow_g':'Net deposit outflow','missing_amounts':'Missing amounts'}
    for name,label in names.items():
        properties=[{'id':'displayName','value':label}]
        if name.endswith('_g'):properties.extend([{'id':'unit','value':'suffix:g'},{'id':'decimals','value':2}])
        table['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':name},'properties':properties})
    transfers=panel(db,'Transfers and external payments',
        f'''SELECT occurred_at AS "Recorded",character AS "Sender",realm AS "Realm",counterparty AS "Counterparty",
 cash_copper/10000.0 AS "Gold movement",CASE ownership WHEN 'external' THEN 'External payment'
 WHEN 'own_account' THEN 'Same account' WHEN 'own_other_account' THEN 'Another owned account'
 ELSE 'Unresolved' END AS "Classification",ownership_evidence AS "Evidence"
 FROM nexus.cash_transfer_classification WHERE {NS} AND $__timeFilter(occurred_at) ORDER BY occurred_at DESC''',
        width=24,height=7,description='Money to a character proven to belong to you is a transfer. External payments affect recorded cash flow. Unmatched names remain unresolved until there is evidence.')
    transfers['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':'Gold movement'},
        'properties':[{'id':'unit','value':'suffix:g'},{'id':'decimals','value':2}]})


def build():
    f=dashboard('duckmoo-warband-financials','DuckMoo Nexus | Warband Financials',
                'Physical Warbank gold from timestamped transfer ledger balances. Income/expenses exclude bank transfers, deposits held as principal, unresolved mail/trades and unpriced materials. Net flow is not crafting profit.')
    panel(f,'Warbank gold: latest recorded balance',f'SELECT copper/10000.0 AS gold FROM nexus.warbank_history WHERE {NS} AND observed_at<=to_timestamp(${{__to}}/1000.0) ORDER BY observed_at DESC,source_saved_at DESC,source_ordinal ASC LIMIT 1',
          'stat','suffix:g','Actual bank balance, never combined wallets. Recorded ledger state as of selected end time. See source timestamp below.',height=5)
    panel(f,'Bank observation timestamp',f'SELECT observed_at,source,copper/10000.0 AS gold FROM nexus.warbank_history WHERE {NS} AND observed_at<=to_timestamp(${{__to}}/1000.0) ORDER BY observed_at DESC,source_saved_at DESC,source_ordinal ASC LIMIT 1',height=5)
    panel(f,'Warbank balance over time',f'SELECT observed_at AS time,copper/10000.0 AS "Warbank gold" FROM nexus.warbank_history WHERE {NS} AND $__timeFilter(observed_at) ORDER BY observed_at',
          'timeseries','suffix:g','Recorded balances after deposits/withdrawals. Missing intervals stay missing. Same-second records may have uncertain order.',width=24,height=10)
    fixed_color(f['panels'][0],'yellow')
    fixed_color(f['panels'][2],'yellow')
    fixed_color(panel(f,'Recorded income',f'SELECT sum(income_copper)/10000.0 AS gold {FIN}','stat','suffix:g',height=5),'green')
    fixed_color(panel(f,'Recorded expenses',f'SELECT sum(expense_copper)/10000.0 AS gold {FIN}','stat','suffix:g','Does not include unmatched lost auction deposits or unpriced crafting materials.',height=5),'red')
    net_colors(panel(f,'Net recorded flow',f'SELECT sum(income_copper-expense_copper)/10000.0 AS gold {FIN}','stat','suffix:g',height=5))
    fixed_color(panel(f,'Auction commission fees',f"SELECT sum(expense_copper)/10000.0 AS gold {FIN} AND component='auction sale'",'stat','suffix:g',height=5),'red')
    daily=panel(f,'Daily income and expenses',f"SELECT date_trunc('day',occurred_at,'America/Chicago') AS time,sum(income_copper)/10000.0 AS income,-sum(expense_copper)/10000.0 AS expenses {FIN} GROUP BY 1 ORDER BY 1",'timeseries','suffix:g',width=24)
    daily['fieldConfig']['overrides']=[{'matcher':{'id':'byName','options':name},'properties':[
        {'id':'color','value':{'mode':'fixed','fixedColor':color}}]} for name,color in [('income','green'),('expenses','red')]]
    panel(f,'Income and expenses by source',f'SELECT component,sum(income_copper)/10000.0 AS income_g,sum(expense_copper)/10000.0 AS expense_g,sum(income_copper-expense_copper)/10000.0 AS net_g {FIN} GROUP BY 1 ORDER BY net_g DESC')
    panel(f,'All tracked characters: financial activity',f'SELECT character,realm,sum(income_copper)/10000.0 AS income_g,sum(expense_copper)/10000.0 AS expense_g {FIN} GROUP BY 1,2 ORDER BY income_g DESC')
    panel(f,'Crafting orders, including patron orders',f"SELECT character,realm,order_type,count(*) AS orders,sum(income_copper)/10000.0 AS tips_g,sum(expense_copper)/10000.0 AS cuts_g,count(*) FILTER(WHERE has_crafter_materials) AS orders_with_own_materials {FIN} AND category='Fulfilling' GROUP BY 1,2,3",description='Order type retained as source enum. Commission net excludes own reagent costs, so it is not profit.')
    panel(f,'Auction deposit principal and unresolved money',f'SELECT component,sum(internal_transfer_copper)/10000.0 AS deposit_cash_g,sum(uncertain_copper)/10000.0 AS unresolved_g {FIN} GROUP BY 1 HAVING sum(internal_transfer_copper)<>0 OR sum(uncertain_copper)<>0',description='Principal returned is not new income. Failed/cancelled deposits are not matched to invoices yet.')
    panel(f,'Category coverage and incomplete attribution',f'SELECT * FROM nexus.financial_coverage WHERE {NS} ORDER BY records DESC',description='Coverage spans all imported history. Unclassified records are never silently converted into income.')
    panel(f,'Cached character balances, separately',f"SELECT DISTINCT ON(o.source,o.entity) o.source,o.entity,o.copper/10000.0 AS gold,o.observed_at,o.time_precision,o.quality,s.source_saved_at AS snapshot_file_saved_at FROM nexus.source_observations o JOIN nexus.snapshot_observations l ON l.observation_id=o.id JOIN nexus.source_snapshots s ON s.id=l.snapshot_id WHERE o.namespace=${{account:sqlstring}} AND o.kind='character_balance' ORDER BY o.source,o.entity,s.source_saved_at DESC NULLS LAST,s.captured_at DESC,s.id DESC",description='Latest preserved file for each source and character. File save time is shown separately from source observation time. Cached balances are not added to Warbank gold.')
    panel(f,'Other bank observations and source quality',f"SELECT source,observed_at,copper/10000.0 AS gold,quality FROM nexus.source_observations WHERE {NS} AND kind='warbank_balance' AND quality<>'recorded_after_transfer' ORDER BY observed_at DESC NULLS LAST",description='Includes timestamp-free Syndicator cache and legacy samples; excluded from primary balance history.')
    panel(f,'Snapshot preservation and normalization',f'SELECT source,count(*) AS snapshots,max(source_saved_at) AS latest_file_save,max(imported_at) AS latest_archive,max(normalized_version) AS normalized_version FROM nexus.source_snapshots WHERE {NS} GROUP BY 1 ORDER BY 1')
    patron_panels(f)
    cashflow_panels(f)
    # Preserve existing panel IDs/links, but put patron earnings immediately after
    # the bank history instead of hiding the new section below diagnostic tables.
    panels=f['panels']; f['panels']=panels[:3]+panels[16:20]+panels[23:]+panels[20:23]+panels[3:16]
    y=0; previous=None
    for obj in f['panels']:
        width,height=obj['gridPos']['w'],obj['gridPos']['h']
        if previous and width==12 and previous['gridPos']['w']==12 and previous['gridPos']['x']==0 and previous['gridPos']['h']==height:
            obj['gridPos'].update(x=12,y=previous['gridPos']['y'])
        else:
            obj['gridPos'].update(x=0,y=y)
        y=max(y,obj['gridPos']['y']+height); previous=obj

    from build_market_dashboard import build_market
    m=build_market()
    out=Path(__file__).parent/'grafana';out.mkdir(exist_ok=True)
    for name,db in [('warband-financials',f),('azeroth-stock-exchange',m)]:
        (out/(name+'.json')).write_text(json.dumps(db,indent=2),encoding='utf-8')


if __name__=='__main__':
    build()

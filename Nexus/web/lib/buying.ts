import 'server-only';
import {rows,account} from './db';
import {buyingPlan} from './buying-model';
export async function buyingAdvisor(days:number,horizon:number){
 const purchases=await rows(`WITH coverage AS (
   SELECT greatest(1,least($2::int,ceil(extract(epoch FROM now()-min(occurred_at))/86400))) AS days
   FROM nexus.transactions WHERE namespace=$1 AND category='Invoices' AND subtype='buyer'),
 bought AS (SELECT item_id,max(item_name) AS name,count(*) AS orders,count(DISTINCT (occurred_at AT TIME ZONE 'America/Chicago')::date) AS purchase_days,
   sum(quantity) AS units,sum(invoice_value_copper) AS spent,max(occurred_at) AS last_purchase,
   count(*) FILTER(WHERE invoice_value_copper IS NULL) AS incomplete
   FROM nexus.transactions WHERE namespace=$1 AND category='Invoices' AND subtype='buyer' AND item_id IS NOT NULL AND quantity>0
   AND occurred_at>=now()-($2::int*interval '1 day') AND occurred_at<=now() GROUP BY item_id HAVING count(*)>=2),
 snapshot AS (SELECT id,fetched_at,source_modified_at FROM nexus.latest_api_snapshots WHERE region='us' AND scope='commodities')
 SELECT b.*,coverage.days AS coverage_days,m.payload->>'_nexus_icon' AS icon,m.payload#>>'{quality,type}' AS quality,
   q.crafting_quality,p.price,p.quantity AS listed,s.fetched_at,s.source_modified_at,
   inv.stock,inv.saved_at,inv.excluded,inv.bound
 FROM bought b CROSS JOIN coverage CROSS JOIN snapshot s
 JOIN nexus.api_item_metadata m ON m.region='us' AND m.item_id=b.item_id AND m.payload#>>'{item_class,id}'='7'
 LEFT JOIN nexus.item_qualities q ON q.namespace=$1 AND q.item_id=b.item_id
 JOIN LATERAL (SELECT min(unit_price_copper) AS price,sum(quantity) AS quantity,count(DISTINCT item_variant) AS variants
   FROM nexus.auction_listings WHERE snapshot_id=s.id AND item_id=b.item_id) p ON p.price>0 AND p.variants=1
 LEFT JOIN LATERAL (SELECT sum(quantity) FILTER(WHERE owner_kind IN('character','warband') AND location IN('bags','bank','bankTabs') AND is_bound=false) AS stock,
   max(snapshot_file_saved_at) AS saved_at,
   sum(quantity) FILTER(WHERE owner_kind='guild' OR location='auctions') AS excluded,
   sum(quantity) FILTER(WHERE is_bound=true) AS bound
   FROM nexus.current_inventory WHERE namespace=$1 AND item_id=b.item_id) inv ON true
 ORDER BY b.purchase_days DESC,b.orders DESC,b.units DESC LIMIT 60`,[account,days]);
 const ids=purchases.map(r=>Number(r.item_id));
 const history=ids.length?await rows(`WITH snapshots AS (
   SELECT id,coalesce(source_modified_at,fetched_at) AS at FROM nexus.api_snapshots
   WHERE region='us' AND scope='commodities' AND fetched_at>=now()-interval '56 days' AND fetched_at<=now()),
 points AS (SELECT a.item_id,s.at,min(a.unit_price_copper)::numeric AS price
   FROM snapshots s JOIN nexus.auction_listings a ON a.snapshot_id=s.id AND a.item_id=ANY($1::bigint[]) AND a.unit_price_copper>0
   GROUP BY a.item_id,s.at HAVING count(DISTINCT a.item_variant)=1),
 daily AS (SELECT item_id,(at AT TIME ZONE 'America/Chicago')::date AS day,
   percentile_cont(.5) WITHIN GROUP(ORDER BY price) AS price,count(*)::int AS samples
   FROM points GROUP BY 1,2)
 SELECT item_id,day::text,extract(dow FROM day)::int AS weekday,price,samples FROM daily ORDER BY day`,[ids]):[];
 return {items:purchases.map(p=>buyingPlan(p,history.filter(h=>h.item_id===p.item_id),horizon,days)),days,horizon,timezone:'America/Chicago',asOf:new Date().toISOString()};
}

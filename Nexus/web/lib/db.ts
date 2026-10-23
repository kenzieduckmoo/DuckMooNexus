import 'server-only';
import { Pool } from 'pg';
const globalDb = globalThis as unknown as { nexusPool?: Pool };
export const db = globalDb.nexusPool ?? new Pool({ connectionString: process.env.DATABASE_URL, max: 5, connectionTimeoutMillis: 4000, options: '-c default_transaction_read_only=on -c statement_timeout=15000' });
globalDb.nexusPool = db;
export const account = 'retail-main-account';
export async function rows(sql: string, values: unknown[] = []) { return (await db.query(sql, values)).rows; }

const realms: Record<string,string> = {'11':'Tichondrius','57':'Illidan','61':"Zul’jin",'63':'Ysera','76':'Sargeras','99':'Llane','104':'Malygos / Garona','162':'Emerald Dream','1426':'Aerie Peak','3675':'Moon Guard','3685':'Turalyon','3721':'Saurfang','3726':"Aman’Thul / Khaz’goroth"};
export function scopeName(scope: string) { return scope === 'commodities' ? 'US commodities' : (realms[scope.split(':')[1]] ?? scope.replace('connected-realm:', 'Connected realm ')); }
export async function scopes() { return (await rows('SELECT scope,fetched_at,source_modified_at,auction_count FROM nexus.latest_api_snapshots WHERE region=\'us\' ORDER BY scope')).map(r=>({...r,label:scopeName(r.scope)})); }

export async function search(q: string, scope: string, sort = 'name') {
  // Match names first; the item/snapshot index then reads only their auction rows.
  const found = await rows(`WITH matches AS MATERIALIZED (
    SELECT item_id,name FROM nexus.item_catalog WHERE namespace=$1
    AND ($2='' OR EXISTS(SELECT 1 FROM unnest(aliases) n WHERE strpos(lower(n),lower($2))>0) OR item_id::text=$2)
    ORDER BY CASE WHEN lower(name)=lower($2) THEN 0 ELSE 1 END,name LIMIT 500),
    snapshot AS (SELECT id,fetched_at,source_modified_at FROM nexus.latest_api_snapshots WHERE region='us' AND scope=$3)
    SELECT m.item_id,m.name,p.price,p.quantity,p.listings,p.variants,s.fetched_at,s.source_modified_at,
      meta.payload->>'_nexus_icon' AS icon,meta.payload#>>'{quality,type}' AS quality,coalesce(tiers.crafting_quality,stock.crafting_quality) AS crafting_quality
    FROM matches m CROSS JOIN snapshot s JOIN LATERAL (
      SELECT min(coalesce(unit_price_copper,buyout_copper::numeric/nullif(quantity,0))) AS price,
      sum(quantity) AS quantity,count(*) AS listings,count(DISTINCT item_variant) AS variants
      FROM nexus.auction_listings WHERE snapshot_id=s.id AND item_id=m.item_id
    ) p ON p.listings>0 LEFT JOIN nexus.api_item_metadata meta ON meta.item_id=m.item_id AND meta.region='us'
    LEFT JOIN nexus.item_qualities tiers ON tiers.namespace=$1 AND tiers.item_id=m.item_id
    LEFT JOIN LATERAL (SELECT CASE WHEN count(DISTINCT crafting_quality)=1 THEN max(crafting_quality) END AS crafting_quality
      FROM nexus.current_inventory WHERE namespace=$1 AND item_id=m.item_id) stock ON true`,[account,q,scope]);
  found.sort((a,b)=>sort==='price'?Number(a.price??Infinity)-Number(b.price??Infinity):sort==='quantity'?Number(b.quantity)-Number(a.quantity):a.name.localeCompare(b.name));
  return { rows: found.slice(0,80), matched: found.length, limited: true, scope, label:scopeName(scope) };
}

export async function overview() {
  const [stats,bank,sources,markets,characters] = await Promise.all([
    rows(`SELECT (SELECT count(*) FROM nexus.character_roster WHERE namespace=$1) AS characters,
    (SELECT count(DISTINCT character_guid) FROM nexus.character_professions WHERE namespace=$1) AS crafters,
    (SELECT count(*) FROM nexus.item_catalog WHERE namespace=$1) AS items,
    (SELECT sum(auction_count) FROM nexus.latest_api_snapshots WHERE region='us') AS listings`,[account]),
    rows(`SELECT DISTINCT ON(date_trunc('hour',observed_at)) observed_at AS time,copper::numeric/10000 AS value
      FROM nexus.warbank_history WHERE namespace=$1 AND observed_at>now()-interval '90 days'
      ORDER BY date_trunc('hour',observed_at) DESC,observed_at DESC,source_ordinal DESC`,[account]),
    rows(`SELECT DISTINCT ON(source) source,source_saved_at,captured_at,normalized_version FROM nexus.source_snapshots WHERE namespace=$1 ORDER BY source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC`,[account]),
    scopes(),
    rows(`SELECT name,realm,class,class_name,level,item_level FROM nexus.character_roster WHERE namespace=$1 ORDER BY last_seen DESC NULLS LAST LIMIT 5`,[account])
  ]);
  return {stats:stats[0],bank:bank.reverse(),sources,markets,characters};
}

export async function item(id: number, scope: string, days: number, variant: string) {
  if(variant){ const v=JSON.parse(variant);if(typeof v!=='object'||v===null||Array.isArray(v))throw Error('variant'); }
  const [info,offers,history,owned,sales] = await Promise.all([
    rows(`SELECT c.*,m.payload->>'_nexus_icon' AS icon,m.payload#>>'{quality,type}' AS quality,m.payload#>>'{item_class,name}' AS category,m.payload#>>'{item_subclass,name}' AS subcategory,
      coalesce((SELECT crafting_quality FROM nexus.item_qualities WHERE namespace=$1 AND item_id=$2),
      (SELECT CASE WHEN count(DISTINCT crafting_quality)=1 THEN max(crafting_quality) END FROM nexus.current_inventory WHERE namespace=$1 AND item_id=$2)) AS crafting_quality
      FROM nexus.item_catalog c LEFT JOIN nexus.api_item_metadata m ON m.item_id=c.item_id AND m.region='us' WHERE c.namespace=$1 AND c.item_id=$2`,[account,id]),
    rows(`SELECT a.item_variant::text AS variant,min(coalesce(a.unit_price_copper,a.buyout_copper::numeric/nullif(a.quantity,0))) AS price,sum(a.quantity) AS quantity,count(*) AS listings,max(s.fetched_at) AS fetched_at,max(s.source_modified_at) AS source_modified_at FROM nexus.latest_api_snapshots s JOIN nexus.auction_listings a ON a.snapshot_id=s.id WHERE s.region='us' AND s.scope=$1 AND a.item_id=$2 GROUP BY a.item_variant ORDER BY price NULLS LAST LIMIT 100`,[scope,id]),
    rows(`SELECT s.fetched_at AS time,s.source_modified_at,min(coalesce(a.unit_price_copper,a.buyout_copper::numeric/nullif(a.quantity,0)))::numeric/10000 AS value,sum(a.quantity) AS quantity FROM nexus.api_snapshots s JOIN nexus.auction_listings a ON a.snapshot_id=s.id AND a.item_id=$1 WHERE s.region='us' AND s.scope=$2 AND s.fetched_at>now()-($3::integer*interval '1 day') AND ($4='' OR a.item_variant= nullif($4,'')::jsonb) GROUP BY s.id ORDER BY s.fetched_at LIMIT 1000`,[id,scope,days,variant]),
    rows(`SELECT owner_kind,owner_key,location,crafting_quality,is_bound,sum(quantity) AS quantity,max(snapshot_file_saved_at) AS saved_at FROM nexus.current_inventory WHERE namespace=$1 AND item_id=$2 GROUP BY owner_kind,owner_key,location,crafting_quality,is_bound ORDER BY quantity DESC LIMIT 40`,[account,id]),
    rows(`SELECT metrics,observed_at,scope FROM nexus.market_observations WHERE namespace=$1 AND item_key IN($2,$3) AND metrics ? 'region_sale_rate' ORDER BY observed_at DESC LIMIT 1`,[account,'i:'+id,String(id)])
  ]);
  return {item:info[0]??{item_id:id,name:'Item '+id},offers,history,owned,sales:sales[0]??null,scope,label:scopeName(scope),days,variant};
}

CREATE TABLE IF NOT EXISTS nexus.item_name_evidence (
 namespace text NOT NULL, item_id bigint NOT NULL, name text NOT NULL,
 source text NOT NULL, locale text NOT NULL DEFAULT 'en_US',
 PRIMARY KEY(namespace,item_id,name,source,locale)
);
CREATE INDEX IF NOT EXISTS item_name_lookup ON nexus.item_name_evidence(namespace,item_id);
CREATE OR REPLACE FUNCTION nexus.record_transaction_item_name() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.item_id IS NOT NULL AND nullif(NEW.item_name,'') IS NOT NULL THEN
  INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source)
  VALUES(NEW.namespace,NEW.item_id,NEW.item_name,'Journalator') ON CONFLICT DO NOTHING;
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS transaction_item_name ON nexus.transactions;
CREATE TRIGGER transaction_item_name AFTER INSERT ON nexus.transactions
 FOR EACH ROW EXECUTE FUNCTION nexus.record_transaction_item_name();
INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source)
 SELECT DISTINCT namespace,item_id,item_name,'Journalator' FROM nexus.transactions
 WHERE item_id IS NOT NULL AND nullif(item_name,'') IS NOT NULL ON CONFLICT DO NOTHING;
-- Use actual item hyperlinks, never assume a recipe name is its output name.
INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source)
 SELECT DISTINCT namespace,(regexp_match(payload#>>'{info,hyperlink}','item:([0-9]+)'))[1]::bigint,
 (regexp_match(payload#>>'{info,hyperlink}','\|h\[([^]]+)\]'))[1],'DuckMooCapture'
 FROM nexus.crafting_observations WHERE kind='catalog'
 AND payload#>>'{info,hyperlink}' ~ 'item:[0-9]+'
 AND payload#>>'{info,hyperlink}' ~ '\|h\[[^]]+\]' ON CONFLICT DO NOTHING;
CREATE OR REPLACE VIEW nexus.item_catalog AS
 SELECT namespace,item_id,min(name) AS name,array_agg(DISTINCT name ORDER BY name) AS aliases,
 array_agg(DISTINCT source ORDER BY source) AS name_sources
 FROM nexus.item_name_evidence WHERE locale='en_US' GROUP BY namespace,item_id;
CREATE OR REPLACE FUNCTION nexus.record_capture_item_name() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE link text; item text; label text;
BEGIN
 IF NEW.kind='catalog' THEN
  link:=NEW.payload#>>'{info,hyperlink}';
  item:=(regexp_match(link,'item:([0-9]+)'))[1];
  label:=(regexp_match(link,'\|h\[([^]]+)\]'))[1];
  IF item IS NOT NULL AND label IS NOT NULL THEN
   INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source)
   VALUES(NEW.namespace,item::bigint,label,'DuckMooCapture') ON CONFLICT DO NOTHING;
  END IF;
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS capture_item_name ON nexus.crafting_observations;
CREATE TRIGGER capture_item_name AFTER INSERT ON nexus.crafting_observations
 FOR EACH ROW EXECUTE FUNCTION nexus.record_capture_item_name();
CREATE INDEX IF NOT EXISTS market_namespace_item_time ON nexus.market_observations(namespace,item_key,observed_at);
CREATE INDEX IF NOT EXISTS api_scope_time ON nexus.api_snapshots(region,scope,fetched_at DESC,id DESC);
CREATE OR REPLACE VIEW nexus.latest_api_snapshots AS
 SELECT DISTINCT ON(region,scope) * FROM nexus.api_snapshots ORDER BY region,scope,fetched_at DESC,id DESC;
CREATE OR REPLACE VIEW nexus.latest_auction_prices AS
 SELECT s.region,s.scope,s.id AS snapshot_id,s.fetched_at,s.source_modified_at,
 a.item_id,a.item_variant,sum(a.quantity) AS quantity,count(*) AS listings,
 min(coalesce(a.unit_price_copper,a.buyout_copper::numeric/nullif(a.quantity,0))) AS lowest_unit_copper
 FROM nexus.latest_api_snapshots s JOIN nexus.auction_listings a ON a.snapshot_id=s.id
 GROUP BY s.region,s.scope,s.id,s.fetched_at,s.source_modified_at,a.item_id,a.item_variant;
CREATE TABLE IF NOT EXISTS nexus.api_worker_status (
 region text NOT NULL,scope text NOT NULL,last_attempt timestamptz NOT NULL,
 last_success timestamptz,next_attempt timestamptz NOT NULL,status text NOT NULL,
 PRIMARY KEY(region,scope)
);
CREATE TABLE IF NOT EXISTS nexus.api_item_metadata (
 region text NOT NULL,item_id bigint NOT NULL,payload jsonb NOT NULL,checked_at timestamptz NOT NULL,
 PRIMARY KEY(region,item_id)
);
INSERT INTO nexus.schema_migrations(version) VALUES(9) ON CONFLICT DO NOTHING;

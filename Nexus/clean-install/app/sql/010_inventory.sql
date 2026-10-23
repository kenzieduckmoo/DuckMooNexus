CREATE TABLE IF NOT EXISTS nexus.inventory_records (
 id text PRIMARY KEY,namespace text NOT NULL,owner_kind text NOT NULL,owner_key text NOT NULL,
 location text NOT NULL,slot_key text NOT NULL,item_id bigint NOT NULL,quantity bigint NOT NULL CHECK(quantity>0),
 name text,item_link text,rarity integer,crafting_quality integer,is_bound boolean,payload jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS inventory_item ON nexus.inventory_records(namespace,item_id);
CREATE TABLE IF NOT EXISTS nexus.snapshot_inventory (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 observation_id text NOT NULL REFERENCES nexus.inventory_records,PRIMARY KEY(snapshot_id,observation_id)
);
CREATE TABLE IF NOT EXISTS nexus.inventory_snapshot_coverage (
 snapshot_id bigint PRIMARY KEY REFERENCES nexus.source_snapshots,
 characters integer NOT NULL,guilds integer NOT NULL,warbanks integer NOT NULL,stacks integer NOT NULL
);
CREATE OR REPLACE VIEW nexus.current_inventory AS
 WITH latest AS (
 SELECT DISTINCT ON(namespace) id,namespace,source_saved_at,captured_at
 FROM nexus.source_snapshots WHERE source='Syndicator.lua' AND normalized_version='0.5.0-inventory1'
 ORDER BY namespace,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC
 )
 SELECT r.*,s.id AS snapshot_id,s.source_saved_at AS snapshot_file_saved_at,s.captured_at,
 NULL::timestamptz AS item_observed_at,'cached_without_observation_time'::text AS freshness
 FROM latest s JOIN nexus.snapshot_inventory l ON l.snapshot_id=s.id
 JOIN nexus.inventory_records r ON r.id=l.observation_id;
-- Location and access restrictions remain visible; guild stock is never personal stock.
CREATE OR REPLACE VIEW nexus.inventory_totals AS
 SELECT namespace,item_id,name,crafting_quality,rarity,owner_kind,owner_key,location,is_bound,
 sum(quantity) AS quantity,max(snapshot_file_saved_at) AS snapshot_file_saved_at
 FROM nexus.current_inventory GROUP BY namespace,item_id,name,crafting_quality,rarity,owner_kind,owner_key,location,is_bound;
INSERT INTO nexus.schema_migrations(version) VALUES(10) ON CONFLICT DO NOTHING;

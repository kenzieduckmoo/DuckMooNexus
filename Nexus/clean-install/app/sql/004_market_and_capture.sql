CREATE TABLE IF NOT EXISTS nexus.market_observations (
 id text PRIMARY KEY,namespace text NOT NULL,source text NOT NULL,scope text NOT NULL,
 item_key text NOT NULL,observed_at timestamptz,time_precision text NOT NULL,
 source_day integer,metrics jsonb NOT NULL,quality text NOT NULL
);
CREATE TABLE IF NOT EXISTS nexus.snapshot_market (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 observation_id text NOT NULL REFERENCES nexus.market_observations,
 PRIMARY KEY(snapshot_id,observation_id)
);
CREATE INDEX IF NOT EXISTS market_item_time ON nexus.market_observations(scope,item_key,observed_at);
CREATE TABLE IF NOT EXISTS nexus.crafting_observations (
 id text PRIMARY KEY,namespace text NOT NULL,character_guid text NOT NULL,
 recipe_id bigint,kind text NOT NULL,operation_key text NOT NULL,
 observed_at timestamptz,payload jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS nexus.snapshot_crafting (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 observation_id text NOT NULL REFERENCES nexus.crafting_observations,
 PRIMARY KEY(snapshot_id,observation_id)
);
CREATE INDEX IF NOT EXISTS crafting_recipe_time ON nexus.crafting_observations(recipe_id,observed_at);
CREATE TABLE IF NOT EXISTS nexus.api_snapshots (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 region text NOT NULL,scope text NOT NULL,endpoint text NOT NULL,
 fetched_at timestamptz NOT NULL,source_modified_at timestamptz,
 last_modified_header text,etag text,sha256 text NOT NULL,
 raw_gzip bytea NOT NULL,auction_count integer NOT NULL,
 UNIQUE(region,scope,sha256,source_modified_at)
);
CREATE TABLE IF NOT EXISTS nexus.api_polls (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,region text NOT NULL,scope text NOT NULL,
 fetched_at timestamptz NOT NULL,status integer NOT NULL,
 snapshot_id bigint REFERENCES nexus.api_snapshots,retry_after text
);
CREATE TABLE IF NOT EXISTS nexus.auction_listings (
 snapshot_id bigint NOT NULL REFERENCES nexus.api_snapshots,auction_id bigint NOT NULL,
 item_id bigint NOT NULL,item_variant jsonb NOT NULL,quantity bigint NOT NULL CHECK(quantity>0),
 unit_price_copper bigint,buyout_copper bigint,bid_copper bigint,time_left text,
 PRIMARY KEY(snapshot_id,auction_id)
);
CREATE INDEX IF NOT EXISTS auction_items ON nexus.auction_listings(item_id,snapshot_id);
-- No sale field: a disappearing listing is not a confirmed sale.
INSERT INTO nexus.schema_migrations(version) VALUES(4) ON CONFLICT DO NOTHING;

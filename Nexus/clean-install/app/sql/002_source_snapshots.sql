-- Additive: does not change the operational Journalator tables or importer.
CREATE TABLE IF NOT EXISTS nexus.source_snapshots (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 namespace text NOT NULL, source text NOT NULL, sha256 text NOT NULL,
 raw_bytes bigint NOT NULL CHECK(raw_bytes>0), source_saved_at timestamptz,
 captured_at timestamptz NOT NULL, imported_at timestamptz NOT NULL DEFAULT now(),
 normalized_version text, UNIQUE(namespace,source,sha256)
);
CREATE TABLE IF NOT EXISTS nexus.snapshot_chunks (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 ordinal integer NOT NULL, compressed_bytes bytea NOT NULL,
 PRIMARY KEY(snapshot_id,ordinal)
);
CREATE TABLE IF NOT EXISTS nexus.snapshot_sightings (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 source_saved_at timestamptz NOT NULL,captured_at timestamptz NOT NULL,
 original_name text NOT NULL,PRIMARY KEY(snapshot_id,source_saved_at,original_name)
);
CREATE TABLE IF NOT EXISTS nexus.source_observations (
 id text PRIMARY KEY, namespace text NOT NULL, source text NOT NULL,
 kind text NOT NULL, entity text NOT NULL, source_key text NOT NULL,
 observed_at timestamptz, time_precision text NOT NULL,
 copper bigint CHECK(copper>=0), quality text NOT NULL, payload jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS nexus.snapshot_observations (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 observation_id text NOT NULL REFERENCES nexus.source_observations,
 source_ordinal integer NOT NULL,
 PRIMARY KEY(snapshot_id,observation_id)
);
CREATE INDEX IF NOT EXISTS source_obs_time ON nexus.source_observations(namespace,kind,observed_at);
-- Recorded bank ledger points only. Unknown-time caches and unvalidated legacy
-- samples remain inspectable but cannot silently replace these balances.
CREATE OR REPLACE VIEW nexus.warbank_history AS
 SELECT DISTINCT ON (o.id) o.id,o.namespace,o.source,o.observed_at,o.copper,o.payload,o.source_key,
  s.source_saved_at,link.source_ordinal
 FROM nexus.source_observations o
 JOIN nexus.snapshot_observations link ON link.observation_id=o.id
 JOIN nexus.source_snapshots s ON s.id=link.snapshot_id
 WHERE o.kind='warbank_balance' AND o.quality='recorded_after_transfer'
 ORDER BY o.id,s.source_saved_at DESC,link.source_ordinal;
INSERT INTO nexus.schema_migrations(version) VALUES(2) ON CONFLICT DO NOTHING;

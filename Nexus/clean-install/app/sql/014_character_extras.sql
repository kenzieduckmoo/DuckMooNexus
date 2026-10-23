CREATE TABLE IF NOT EXISTS nexus.character_extras (
 id text PRIMARY KEY,namespace text NOT NULL,source text NOT NULL,character_guid text NOT NULL,
 observed_at timestamptz,payload jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS character_extras_lookup ON nexus.character_extras(namespace,character_guid,source);
CREATE TABLE IF NOT EXISTS nexus.snapshot_character_extras (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,observation_id text NOT NULL REFERENCES nexus.character_extras,
 PRIMARY KEY(snapshot_id,observation_id)
);
CREATE OR REPLACE VIEW nexus.current_character_extras AS
 WITH latest AS(SELECT DISTINCT ON(namespace,source) id,namespace,source,source_saved_at,captured_at
 FROM nexus.source_snapshots WHERE source IN('WarbandNexus.lua','WoWthing_Collector.lua','DuckMooWarband.lua') AND normalized_version='0.5.0-character-extras1'
 ORDER BY namespace,source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC)
 SELECT e.*,s.source_saved_at,s.captured_at FROM latest s JOIN nexus.snapshot_character_extras l ON l.snapshot_id=s.id JOIN nexus.character_extras e ON e.id=l.observation_id;
INSERT INTO nexus.schema_migrations(version) VALUES(14) ON CONFLICT DO NOTHING;

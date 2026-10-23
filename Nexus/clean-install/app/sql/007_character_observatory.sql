CREATE TABLE IF NOT EXISTS nexus.character_records (
 id text PRIMARY KEY,namespace text NOT NULL,source text NOT NULL,character_guid text NOT NULL,
 record_kind text NOT NULL,record_key text NOT NULL,observed_at timestamptz,
 time_precision text NOT NULL,payload jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS character_record_lookup ON nexus.character_records(namespace,source,character_guid,record_kind,observed_at);
CREATE TABLE IF NOT EXISTS nexus.snapshot_characters (
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,
 observation_id text NOT NULL REFERENCES nexus.character_records,
 PRIMARY KEY(snapshot_id,observation_id)
);
CREATE INDEX IF NOT EXISTS snapshot_character_observation ON nexus.snapshot_characters(observation_id);

-- Latest successfully normalized full source, not a union of stale records from
-- professions which a character may have since dropped. History stays intact.
CREATE OR REPLACE VIEW nexus.current_character_records AS
 WITH latest AS (
  SELECT DISTINCT ON(namespace,source) id,namespace,source,source_saved_at,captured_at
  FROM nexus.source_snapshots
  WHERE source IN ('DuckMooFolio.lua','DuckMooPlanner.lua')
   AND normalized_version='0.5.0-characters1'
  ORDER BY namespace,source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC
 )
 SELECT r.*,s.id AS snapshot_id,s.source_saved_at,s.captured_at
 FROM latest s JOIN nexus.snapshot_characters l ON l.snapshot_id=s.id
 JOIN nexus.character_records r ON r.id=l.observation_id;

CREATE OR REPLACE VIEW nexus.character_roster AS
 SELECT namespace,character_guid,payload->>'name' AS name,payload->>'realm' AS realm,
 payload->>'class' AS class,payload->>'className' AS class_name,payload->>'race' AS race,
 payload->>'faction' AS faction,(payload->>'level')::integer AS level,
 (payload->>'ilvl')::numeric AS item_level,payload->>'specName' AS specialization,
 payload->>'heroSpec' AS hero_specialization,payload->>'role' AS role,
 payload->>'zone' AS zone,payload->>'subzone' AS subzone,payload->>'guild' AS guild,
 observed_at AS last_seen,source_saved_at,payload
 FROM nexus.current_character_records WHERE source='DuckMooFolio.lua' AND record_kind='profile';

CREATE OR REPLACE VIEW nexus.character_professions AS
 SELECT r.namespace,r.character_guid,c.name,c.realm,r.record_key AS skill_line_id,
 r.payload->>'profession' AS profession,r.payload->>'name' AS expansion_skill,
 (r.payload->>'rank')::integer AS skill,(r.payload->>'max')::integer AS maximum,
 (r.payload->>'recipes')::integer AS recorded_recipes,
 (r.payload->>'recipesFiltered')::boolean AS recipe_list_filtered,
 r.observed_at,r.payload
 FROM nexus.current_character_records r JOIN nexus.character_roster c
 ON c.namespace=r.namespace AND c.character_guid=r.character_guid
 WHERE r.record_kind='profession';

CREATE OR REPLACE VIEW nexus.character_concentration AS
 SELECT r.namespace,r.character_guid,c.name,c.realm,r.record_key AS skill_line_id,
 r.payload->>'name' AS profession,r.payload->>'expansion' AS expansion,
 (r.payload->>'amount')::numeric AS sampled_amount,(r.payload->>'max')::numeric AS maximum,
 CASE WHEN r.observed_at<=now() AND (r.payload->>'secondsPerPoint')::numeric>0
      AND (r.payload->>'amount')::numeric>=0 AND (r.payload->>'max')::numeric>0
 THEN least((r.payload->>'max')::numeric,(r.payload->>'amount')::numeric+
      floor(greatest(0,extract(epoch FROM now()-r.observed_at))/(r.payload->>'secondsPerPoint')::numeric)) END AS projected_amount,
 r.observed_at,coalesce((r.payload->>'hidden')::boolean,false) AS hidden,r.payload
 FROM nexus.current_character_records r LEFT JOIN nexus.character_roster c
 ON c.namespace=r.namespace AND c.character_guid=r.character_guid
 WHERE r.record_kind='concentration';

INSERT INTO nexus.schema_migrations(version) VALUES(7) ON CONFLICT DO NOTHING;

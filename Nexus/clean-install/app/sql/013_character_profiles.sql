CREATE TABLE IF NOT EXISTS nexus.character_api_documents (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,namespace text NOT NULL,character_guid text NOT NULL,
 region text NOT NULL,endpoint text NOT NULL,first_fetched_at timestamptz NOT NULL,last_checked_at timestamptz NOT NULL,
 response_modified_at timestamptz,status integer NOT NULL,payload_sha256 text NOT NULL,payload jsonb NOT NULL,
 UNIQUE(namespace,character_guid,endpoint,status,payload_sha256)
);
CREATE INDEX IF NOT EXISTS character_api_latest ON nexus.character_api_documents(namespace,character_guid,endpoint,last_checked_at DESC,id DESC);
ALTER TABLE nexus.character_api_documents ADD COLUMN IF NOT EXISTS profile_observed_at timestamptz;
CREATE OR REPLACE VIEW nexus.latest_character_api AS
 SELECT DISTINCT ON(namespace,character_guid,endpoint) * FROM nexus.character_api_documents
 ORDER BY namespace,character_guid,endpoint,last_checked_at DESC,id DESC;
CREATE TABLE IF NOT EXISTS nexus.character_api_refresh (
 namespace text NOT NULL,character_guid text NOT NULL,last_attempt timestamptz NOT NULL,next_attempt timestamptz NOT NULL,
 last_addon_seen timestamptz,status integer NOT NULL,PRIMARY KEY(namespace,character_guid)
);
INSERT INTO nexus.schema_migrations(version) VALUES(13) ON CONFLICT DO NOTHING;

-- Personal writing is separate from immutable captured game observations.
CREATE TABLE IF NOT EXISTS nexus.character_stories (
 namespace text NOT NULL CHECK(namespace IN ('retail-main-account','forever-main-account')),
 character_guid text NOT NULL CHECK(character_guid ~ '^Player-[0-9]+-[A-Fa-f0-9]+$'),
 document jsonb NOT NULL DEFAULT '{}'::jsonb CHECK(jsonb_typeof(document)='object'),
 revision integer NOT NULL DEFAULT 1 CHECK(revision>0),
 updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(namespace,character_guid)
);
DO $$ BEGIN IF EXISTS(SELECT FROM pg_roles WHERE rolname='nexus_web') THEN GRANT SELECT ON nexus.character_stories TO nexus_web; END IF; END $$;
INSERT INTO nexus.schema_migrations(version) VALUES(22) ON CONFLICT DO NOTHING;

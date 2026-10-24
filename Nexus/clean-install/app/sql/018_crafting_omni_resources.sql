-- Existing crafting service already reads archived source data. Permit the
-- current normalized Omni view for identity/profession/resource model refresh.
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='nexus_crafting') THEN
  GRANT SELECT ON nexus.current_omni_records TO nexus_crafting;
 END IF;
END $$;
INSERT INTO nexus.schema_migrations(version) VALUES(18) ON CONFLICT DO NOTHING;

ALTER TABLE nexus.crafting_documents DROP CONSTRAINT IF EXISTS crafting_documents_key_check;
ALTER TABLE nexus.crafting_documents ADD CONSTRAINT crafting_documents_key_check CHECK(key IN('plan','setups','guides'));
INSERT INTO nexus.schema_migrations(version) VALUES(20) ON CONFLICT DO NOTHING;

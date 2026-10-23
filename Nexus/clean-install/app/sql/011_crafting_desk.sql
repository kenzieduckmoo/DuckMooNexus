CREATE TABLE IF NOT EXISTS nexus.crafting_documents (
 namespace text NOT NULL,key text NOT NULL CHECK(key IN ('plan','setups')),
 payload jsonb NOT NULL,updated_at timestamptz NOT NULL DEFAULT now(),PRIMARY KEY(namespace,key)
);
CREATE TABLE IF NOT EXISTS nexus.crafting_document_history (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,namespace text NOT NULL,key text NOT NULL,
 payload jsonb NOT NULL,saved_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO nexus.schema_migrations(version) VALUES(11) ON CONFLICT DO NOTHING;

-- The advisor needs only purchase fields, never the raw transaction payload.
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='nexus_web') THEN
  GRANT SELECT(namespace,category,subtype,item_id,item_name,quantity,invoice_value_copper,occurred_at)
   ON nexus.transactions TO nexus_web;
 END IF;
END $$;
INSERT INTO nexus.schema_migrations(version) VALUES(19) ON CONFLICT DO NOTHING;

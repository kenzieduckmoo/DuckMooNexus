CREATE SCHEMA IF NOT EXISTS nexus;
CREATE TABLE IF NOT EXISTS nexus.schema_migrations(version integer PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS nexus.imports (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 namespace text NOT NULL, sha256 text NOT NULL, filename text NOT NULL,
 raw_file bytea NOT NULL, imported_at timestamptz NOT NULL DEFAULT now(),
 importer_version text NOT NULL, UNIQUE(namespace,sha256)
);
CREATE TABLE IF NOT EXISTS nexus.archives (
 import_id bigint NOT NULL REFERENCES nexus.imports, store_id text NOT NULL,
 encoded text NOT NULL, decoded jsonb NOT NULL, PRIMARY KEY(import_id,store_id)
);
CREATE TABLE IF NOT EXISTS nexus.transactions (
 id text PRIMARY KEY, namespace text NOT NULL, store_id text NOT NULL,
 category text NOT NULL, ordinal integer NOT NULL CHECK(ordinal>0),
 occurred_at timestamptz NOT NULL, character text, realm text, faction text,
 item_id bigint, item_name text, quantity numeric, subtype text,
 invoice_value_copper bigint, auction_fee_copper bigint, deposit_copper bigint,
 payload_sha256 text NOT NULL, payload jsonb NOT NULL,
 UNIQUE(namespace,store_id,category,ordinal)
);
CREATE TABLE IF NOT EXISTS nexus.observations (
 import_id bigint NOT NULL REFERENCES nexus.imports,
 transaction_id text NOT NULL REFERENCES nexus.transactions,
 PRIMARY KEY(import_id,transaction_id)
);
CREATE INDEX IF NOT EXISTS transactions_time ON nexus.transactions(occurred_at);
CREATE OR REPLACE VIEW nexus.auction_invoices AS
 SELECT id, namespace, occurred_at, character, realm, item_name, quantity, subtype,
 CASE WHEN subtype='seller' THEN invoice_value_copper-auction_fee_copper
      WHEN subtype='buyer' THEN -invoice_value_copper END AS trade_net_copper
 FROM nexus.transactions WHERE category='Invoices';
INSERT INTO nexus.schema_migrations(version) VALUES(1) ON CONFLICT DO NOTHING;

# Project M.O.O. / DuckMoo Nexus — Journalator MVP

Imports Journalator SavedVariables into your existing PostgreSQL database. No SSH access or changes to your existing Docker services are assumed. Includes an importable Grafana dashboard. Python 3.13+ and PostgreSQL 17 are the deployment targets.

## Deploy on Ubuntu

1. Copy this folder to `~/duckmoo-nexus` on the Linux host. Exit WoW or `/reload`, then copy the account-level `WTF/Account/<account>/SavedVariables/Journalator.lua` to a private `~/journalator-inbox` folder. Use a stable completed copy; do not read while WoW is writing. Do not commit or publish these files: they contain character names, mail, counterparties and other personal activity.
2. Build the importer (does not create or replace PostgreSQL or Grafana):

```sh
cd ~/duckmoo-nexus
docker build -t duckmoo-nexus:0.1.0 .
mkdir -p ~/journalator-inbox
chmod 700 ~/journalator-inbox
```

3. Create a private environment file, using your existing database details. Choose ONE networking approach:
   - If PostgreSQL publishes a port on the Linux host, use `--network host` below and `127.0.0.1:<published-port>` in the URL.
   - If it is only on a Docker network, replace `--network host` with `--network YOUR_EXISTING_NETWORK` and use its container/service DNS name and port 5432. Inspect your existing Compose configuration to identify that network. Do not create a replacement database.

```sh
umask 077
cat > .env <<'EOF'
DATABASE_URL=postgresql://IMPORT_USER:URL_ENCODED_PASSWORD@127.0.0.1:5432/DATABASE_NAME
EOF
# Edit .env to substitute your real values before continuing.
```

Use a database owner/migration role to run migration 001, then an importer role with schema USAGE, SELECT/INSERT on the four data tables and USAGE/SELECT on identity sequences. Migration changes are confined to the `nexus` schema. Back up the existing database first. The migration is transactional and repeatable; subsequent schema changes should receive new numbered migrations. Do not grant Grafana the migration/import credentials.

```sh
docker run --rm --network host --env-file .env duckmoo-nexus:0.1.0 migrate
# Run imports as your host UID so the private inbox can stay private.
chmod 600 ~/journalator-inbox/Journalator.lua
docker run --rm --user "$(id -u):$(id -g)" --mount type=bind,src="$HOME/journalator-inbox",dst=/input,readonly \
  duckmoo-nexus:0.1.0 inspect /input/Journalator.lua
docker run --rm --user "$(id -u):$(id -g)" --network host --env-file .env \
  --mount type=bind,src="$HOME/journalator-inbox",dst=/input,readonly \
  duckmoo-nexus:0.1.0 import /input/Journalator.lua --namespace retail-main-account
# Repeat the same import command: expected status already_imported, inserted 0.
```

Keep `--namespace` stable for this WoW account and game flavor. Give another account or Classic a different namespace. Different namespaces intentionally have independent records. Keep dated input copies outside the container; the database also stores the exact bytes of successful imports. A rejected file remains in your inbox, but is not inserted into the database.

## Grafana

With your database administrator, grant the existing Grafana login read access (replace `grafana_reader` with its actual role):

```sql
GRANT USAGE ON SCHEMA nexus TO grafana_reader;
GRANT SELECT ON nexus.transactions, nexus.auction_invoices TO grafana_reader;
GRANT SELECT (namespace, imported_at, filename, sha256, importer_version)
  ON nexus.imports TO grafana_reader;
```

In Grafana, import `grafana-dashboard.json` and select your working PostgreSQL data source. Choose the account namespace. Default window is 90 days; widen it for older data. The dashboard displays UTC dates, auction trade net, event counts, character totals, category coverage, and import timestamps/hashes. It deliberately excludes full raw mail and archive payloads from dashboard queries.

Auction trade net = seller value minus recorded consignment, minus buyer value. Returned deposits are excluded, as are posting deposits and all non-invoice categories. This is neither cash balance nor profit: no inventory cost matching, crafting material costs, or full wallet reconciliation is performed. Missing fees remain unknown (NULL), not guessed as zero. All categories are retained as normalized events with the original payload.

## Preservation and identity

- `imports`: exact source bytes, SHA-256, namespace, original basename, import time and importer version.
- `archives`: original print-encoded strings and decoded JSON for every store, including empty stores.
- `transactions`: UTC event time, character/realm/faction, category/subtype, item ID/name/count where present, invoice copper fields, original JSON and its hash.
- `observations`: ties each transaction to every successful distinct snapshot containing it.

Identity hashes `[namespace, store_id, category, ordinal]`; this follows Journalator's append-only store arrays. It preserves two otherwise identical events at different positions. Reimporting the same bytes returns immediately after validation. Overlapping snapshots add observations but no duplicate transactions. Imports for a namespace are serialized using a database advisory lock. Any conflicting payload at an existing position rolls back the whole import: never silently overwrite history. Archive rebuilding/reordering or moving records between stores is outside this identity model and needs explicit reconciliation; do not change namespace just to bypass a conflict.

The parser accepts data-only SavedVariables assignments and never executes the input Lua. The bundled Lua libraries decode Archivist internalVersion 1 / SometimesLocked version 1. Store versions 1–15 are retained without invoking Journalator migrations; empty stores are supported. Legacy `JOURNALATOR_LOGS`, unknown versions, malformed data, and executable expressions fail closed. Nested arrays remain JSON objects with numeric keys represented as strings. Input size is capped at 64 MiB in the CLI; Lua allocation is capped at 256 MiB. This is a local trusted-file MVP, not a public upload service.

## Verification on your Linux host

The integration test requires a disposable test database, NOT the production database. It creates its schema, tests real-file import/reimport/overlap/conflict handling, and removes only its random verification namespace. It requires database create-schema privileges.

```sh
# .env.test must point to a separate disposable database.
docker run --rm --user "$(id -u):$(id -g)" --network host --env-file .env.test \
 --mount type=bind,src="$HOME/journalator-inbox",dst=/input,readonly \
 --entrypoint python duckmoo-nexus:0.1.0 tests/verify.py /input/Journalator.lua
```

See `VERIFICATION.md` for observed local results and unverified deployment steps. Backup/restore the database using your existing PostgreSQL process; the raw byte archive lives in the same database and must be included in backups. No timer, sync service, public endpoint, pricing optimizer, or addon modification is included.

## Codec provenance

The vendored LibDeflate and LibSerialize files are copied unmodified from the user's installed Journalator/Embeds/Archivist libraries. Their licenses accompany them. `vendor-manifest.json` records their SHA-256 values. The format was confirmed from the installed Archivist.lua Archive/DeArchive methods and Journalator Source/Archiving and Source/Monitor/AuctionMail.lua.

Upstream references: [Archivist](https://github.com/emptyrivers/Archivist), [LibSerialize](https://github.com/rossnichols/LibSerialize), [LibDeflate](https://github.com/SafeteeWoW/LibDeflate).

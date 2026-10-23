# DuckMoo Nexus v0.3.0 audit revision 1: deployment and verification

This release is prepared locally. It has **not** been deployed to Nexus. Local parser/transport checks and actual-data inspection are documented in `verification/real-data-verification.json`. PostgreSQL integration and Grafana rendering still require the LAN host.

The existing importer, image tag, migration 001, Windows Journalator script, restricted SSH identity and Docker network are retained. No public SSH access is needed.

Read `AUDIT-2026-10-20.md` for the changes and current verification limits. The original release ZIP is preserved; use the audited revision package for the commands below.

## 1. Inspect the existing server on its LAN

Copy the extracted release to a new directory under `~/nexus/releases/v0.3.0/`. Keep the old release. From that new directory:

```bash
docker ps --format '{{.Names}} {{.Image}}'
sudo bash preflight.sh YOUR_POSTGRES_CONTAINER
sudo diff -u sync-reference/duckmoo-nexus-sync-0.2.0/server/worker.py /opt/duckmoo-sync/worker.py
sudo diff -u sync-reference/duckmoo-nexus-sync-0.2.0/server/receiver.py /opt/duckmoo-sync/receiver.py
sudo diff -u sync-reference/duckmoo-nexus-sync-0.2.0/server/sync_core.py /opt/duckmoo-sync/sync_core.py
```

`preflight.sh` reads the existing migration and transaction counts without revealing environment values. The upgrader refuses to overwrite sync files that differ from the inspected v0.2.0 reference. Reconcile actual changes first if differences exist. Existing Windows code has local fixes, so its deployed Journalator script is preserved as-is.

## 2. Run the isolated PostgreSQL check before production changes

Extract the separate source snapshot archive into a private directory, owned by the user running this command. It contains genuine SavedVariables, not test fixtures. Do not put it in a web directory.

```bash
bash verify-stack.sh /absolute/path/to/private-snapshots
```

This builds `duckmoo-nexus:0.3.0`, starts a disposable PostgreSQL 17 container on a new internal-only Docker network, applies all migrations twice, imports real source snapshots, repeats imports, compares reconstructed original bytes, exercises the original Journalator importer, executes every dashboard query and checks Grafana view access. Its containers/network are removed on exit. All source normalization runs under the importer role; all 24 panel queries and both account-selector queries run under the Grafana role. A successful run writes `.verified-release.json`, binding the source fingerprint and built image ID. The upgrader refuses a missing or stale receipt. Do not copy a receipt from another release. Production database and containers are not used. It may need to pull `postgres:17` on first use. This check has not run in Work because no local Docker/PostgreSQL runtime is available.

If any check fails, keep the current production pipeline and fix the failure before proceeding. The API response/304/rate-limit logic is unit-tested using controlled responses; live Blizzard credentials have not been supplied.

## 3. Apply additive migrations and the compatible receiver upgrade

Identify the existing importer and Grafana login **role names** from the existing server configuration. Do not paste passwords into commands or this document.

```bash
sudo bash upgrade-server.sh YOUR_POSTGRES_CONTAINER YOUR_IMPORTER_ROLE YOUR_GRAFANA_ROLE
```

The script saves a PostgreSQL custom-format dump and copies existing sync code/config before applying migrations 002Ã¢â‚¬â€œ004 and explicit grants. The dump table of contents is checked before migration. Migrations 002â€“004 and grants run in one transaction with a 10-second lock timeout. New modules are staged separately; launchers pin imports to that directory. The timer is paused only for activation, and an active worker is allowed to finish. Activation failures restore the original launchers and resume the timer. It preserves the old 64 MiB Journalator upload path and `duckmoo-nexus:0.1.0`. New `put2` packets use the same restricted SSH receiver/inbox/worker; raw source bytes are gzip-compressed and chunked in PostgreSQL. Large sources are bounded at 2 GiB raw and 512 MiB compressed per packet. Unknown normalized sources are archived without waiting for an adapter. Failed normalization retains the committed raw archive and retries through the existing worker.

After upgrade, check the original Journalator sync from the normal desktop shortcut and inspect its receipt/log before enabling additional sources. No replacement credentials or SSH exposure changes are needed.

## 4. Enable separate additional-source jobs

After confirming a fresh original Journalator receipt on Nexus, enable the separate server worker:

```bash
sudo systemctl enable --now duckmoo-sources.timer
```

Then, from the extracted release on Windows:

```powershell
powershell.exe -NoProfile -File .\sync-0.3.0\windows\Upgrade-Sources.ps1
```

This backs up the existing task/config/scripts and registers a separate **DuckMoo Nexus Additional Sources** task using the existing task's triggers, principal, and settings. The original Journalator task, scripts, helper, credentials, and shortcut remain unchanged. Python 3.13+ and required collector files are checked first. The server's source worker uses a separate lock and container name, so large imports cannot hold the Journalator worker queue. Resource use is still shared and must be observed during the first full import. No installed task was changed during this audit.

Changed files are double-hash checked and gzip-compressed. Unchanged sources reuse their compressed snapshot and deterministic transport packet, then query receipts. Pending packets survive disconnects. Archives stay private under the existing installation.

The collector also archives TSM's actual `Interface/AddOns/TradeSkillMaster_AppHelper/AppData.lua`. The AppHelper SavedVariables alone do not contain the downloaded market datasets.

## 5. Import Grafana dashboards and verify against real rows

Import `duckmoo-nexus/grafana/warband-financials.json` and `azeroth-stock-exchange.json` through Grafana's existing dashboard import UI, selecting the existing PostgreSQL datasource. New UIDs preserve the current MVP dashboard. No public web service is added. The JSON is importable configuration, not a screenshot or fabricated mockup.

The original verification report includes 982 distinct historical Warbank observations and latest **15,440,018,739 copper** at Unix time **1792481621**. An earlier snapshot has 981 ledger points and **15,437,420,159 copper**. Use the actual selected fixture manifests when reconciling counts; those earlier reports are not live balances. Later snapshots may legitimately increase counts and change balances. Syndicator's cached money matches that latest balance but has no exact source timestamp, so it appears separately. All character wallets remain separate from Warbank gold. Date/time displays use the browser timezone.

```sql
SELECT count(*) FROM nexus.warbank_history WHERE namespace='retail-main-account';
SELECT observed_at,copper,source FROM nexus.warbank_history
WHERE namespace='retail-main-account'
ORDER BY observed_at DESC,source_saved_at DESC,source_ordinal ASC LIMIT 1;
SELECT source,count(*),max(imported_at) FROM nexus.source_snapshots GROUP BY source;
SELECT * FROM nexus.financial_coverage WHERE namespace='retail-main-account';
```

Recorded income/expenses include invoices/commission, vendoring, quest/cache money, crafting-order commissions/cuts, personal repairs, training, taxis and postage. Bank transfers are separate observations. Auction deposit principal is shown separately; unmatched lost deposits remain incomplete. Mail/trade money with unresolved ownership is excluded from income and expenses. Recipe previews and reagent offers are not realized material costs or crafting profit. Order types remain source enums rather than guessed labels.

Auctionator stores daily lowest-low, highest-low and peak quantity, plus a current quote with unknown exact observation time. TSM quotes retain `downloadTime`; region sale rates remain estimates. Recipe, gear and pet variant keys are preserved. These are not synchronized arbitrage opportunities or inferred confirmed sales.

## 6. Blizzard API foundation

`api_collect.py` supports US/EU/KR/TW Retail regional commodities and an explicitly selected connected-realm ID. It uses client-credentials OAuth from `BLIZZARD_CLIENT_ID` and `BLIZZARD_CLIENT_SECRET`, passed through private server environment files, never dashboard JSON. It stores raw gzip responses before database import, source `Last-Modified`, fetch times, ETags, HTTP poll results and listing variants. 304 responses do not create new market snapshots; 429/503 record Retry-After without pretending collection succeeded.

Run inside the existing private Docker network, with a persistent writable archive mounted at `/archive` and the appropriate database/API environment file:

```bash
docker run --rm --network duckmoo-nexus_nexus_internal \
 --env-file /private/path/nexus-api.env --mount type=bind,src=/private/archive,dst=/archive \
 --entrypoint python duckmoo-nexus:0.3.0 \
 api_collect.py --region us --archive /archive --import-db
```

Add `--connected-realm ID` for non-commodity listings. Resolve IDs through Blizzard's connected-realm API rather than guessing from character realm names. No API timer is enabled by this release. The scheduler should honor recorded Retry-After and fetch only as often as upstream refresh timestamps justify; do not interpret a 15-minute poll as a 15-minute upstream update. A previous collection whose database import failed must be replayed before advancing conditional-fetch state. Automatic archived-response replay and scheduler installation are pending.

Authoritative endpoint reference: https://us.forums.blizzard.com/en/blizzard/t/immediate-change-to-auction-apis-for-commodities-with-927/31522 . Official developer portal: https://develop.battle.net/documentation/world-of-warcraft/game-data-apis . The portal is client-rendered and its full current content was not retrievable in Work.

## Rollback

Before server rollback, remove the separate additional-source Windows task if enabled, after its active run finishes:

```powershell
powershell.exe -NoProfile -File .\sync-0.3.0\windows\Rollback-Sources.ps1 -BackupPath "C:\Users\YOUR_USER\AppData\Local\DuckMooNexusSync\before-sources-TIMESTAMP"
```

Then use the exact backup directory printed by the upgrader:

```bash
sudo bash rollback-server.sh /home/kenzieduckmoo/nexus/backups/pre-0.3.0-TIMESTAMP-PID
```

Rollback disables the additional-source timer, waits for active source and Journalator workers, and restores the original entrypoints. The existing Windows Journalator task needs no restoration for this audited revision. It keeps additive tables, raw archives, receipts, and queued packets. Old code ignores `.bundle` packets until a corrected upgrade is deployed. It does not restore a stale database dump over newer Journalator imports. Inspect a fresh Journalator receipt and confirm the timer is active after rollback. The dump is a disaster-recovery artifact; an actual restore drill remains part of server verification.

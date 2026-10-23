# Nexus execution ledger

## Current continuation — October 22, 2026

This section supersedes the historical deployment instructions below. Live admin
access was established with the existing SSH identity. The installed stack is
`/opt/duckmoo-nexus-clean`, Compose project `duckmoo-nexus-clean`.

Delivered and verified live: patron-order financial view and automatic captured
recipe/profession lookup, cumulative and daily earnings, character/profession
filters, breakdown/history, deliberate earnings/expense colors, and independently
editable Financials dashboard. Existing Warbank history remains. No reinstall,
database reset, source-history changes or Windows task changes.

Live reconciliation: 1,723 patron orders, 1,163,786,373 copper after recorded cuts;
zero missing payment fields or unknown professions. Alchemy: 444 orders,
299,700,013 copper. Seven new panel queries executed as `grafana`; final combined
check took 1.428 seconds. UI save succeeded; version 5 survived a provisioning
reload unchanged. Details and update files: `financial-update-2026-10-22/README.md`.

Follow-up delivered live: net recorded cash flow including auction deposit
payments/refunds, cumulative graph and per-character deposit/outcome breakdown.
Fixed vendor purchases recorded as `purchase` being excluded by the old `buy`
filter: 281 purchases, 151,341,675 copper restored to expenses. Net recorded gold
after deposits is 13,103,792,728 copper. Net deposit outflow is 62,721,381 copper;
it is not all confirmed loss. Four panel queries reconcile as `grafana` in about
one second. See `cashflow-update-2026-10-22/README.md`.

Character batch delivered live October 22: Folio/Planner adapters and 16-panel
Character Observatory (`duckmoo-character-observatory`). Latest state includes
58 profiles, 298 expansion-skill records, 4,373 reputations and 55 concentration
pools. All 72 Folio and 57 Planner archives normalized; zero pending. Per-source
adapter version `0.5.0-characters1`; other adapters remain on their existing marker.
Automatic ingestion image rebuilt; original files, snapshots and runtime volumes
preserved. Sixteen new SQL queries executed as Grafana in 2.579 seconds, with two
focused adapter checks and browser verification across two characters.

User-confirmed Beärkoda-Illidan is external; the 50,000g mail payment is now an
expense with separate ownership evidence. Financial queries use
`nexus.cash_financial_components`. New recorded net at the live check:
12,633,399,041 copper (also includes newly imported activity since the prior batch).
Details: `character-update-2026-10-22/README.md`. Character reminders display plain
calendar dates; concentration is explicitly projected, not live or reservation-aware.

AH/inventory batch delivered live October 22 (server UTC October 23): Blizzard
OAuth, 14 markets (US commodities plus 13 connected-realm markets covering the
captured roster), scheduled conditional hourly collection with durable retry/replay,
and partial item-name search on Auction Analysis. First collection stored 836,166
listings; all response counts reconcile. Market dashboard is now UI-owned/editable.
Shared item catalog had 9,722 named IDs at verification; bounded API enrichment continues.

All 72 Syndicator archives normalized without changing wallet observations:
4,099 current stacks / 39,402 units. New searchable Warband Inventory and selected
character stock table show location, rank, rarity and binding. Cached stock has no
invented observation timestamp. Shared views support future crafting consumers.

Read-only Nexus data service on private LAN port 8080 exposes item search,
inventory, markets, character profiles and source normalization status, using the
existing Grafana login and read-only DB role. Anonymous requests reject with 401.
Crafting Desk proxy routes are added locally; existing screens and calculations
have NOT yet been switched from local imports to Nexus. No saved plans changed.
Sixteen affected panel queries ran as Grafana in 2.337 seconds. Five HTTP data
routes verified; four focused local checks plus a proxy check, no broad suite/hash
audit. Details: `market-update-2026-10-22/README.md` and inventory update README.

Next implementation focus: wire Crafting Desk's owned/needed and price consumers
to the shared service, then website character sheets and remaining raw-only adapters.
Do not claim all sources normalized: ATT, CraftSim, WarbandNexus, WoWthing and other
archived-only inputs remain visible as pending in the source-status endpoint.
Folio/Planner normalization is completed, not part of the remaining raw-only backlog.
Exact failed-auction attribution cannot be
established from Journalator failures alone (no deposit amounts or auction IDs).
Future collection needs richer evidence. Unresolved mail/trades and inventory
cost attribution remain before claiming complete realized profit. The existing
50,000g external-mail ambiguity is resolved; future unmatched identities stay open.
Patron raw gold
does not deduct supplied-material costs. Broader source adapters, website, Capture
redesign and Crafting Desk requirements remain incomplete. Do not rerun the
destructive clean installer to continue dashboard work.

## Historical ledger — October 20, 2026

## Verified existing state

- Local v0.1.0 ZIP inspected and extracted without changing the existing importer.
- v0.2.0 sync ZIP found in Downloads. Installed Windows configuration and logs inspected.
- Journalator log reports successful imports through 07:22 UTC; newer snapshot queued at 07:27 UTC. This is log evidence, not an independent database check.
- SSH from this execution environment to 10.20.30.239:22 fails before authentication with Permission denied. No server source, schema, dashboard, or Docker state verified this session.
- Relevant SavedVariables and installed addon source are readable. No live game files modified.
- WarbandAccountantDB.ledger: 981 records. Each stores timestamp and balanceAfter. Latest balance 15,437,420,159 copper matches SYNDICATOR_DATA.Warband[1].money.
- accountTotalHistory is combined wealth, not bank history. Excluded from bank adapter.
- Syndicator bank money has no source observation timestamp; file write time must not be presented as that timestamp.
- DuckMooWarband legacy session samples and WarbandNexus caches include zero values. Preserve and label; do not substitute for recorded ledger history.

## Implemented and verified locally

- Streaming, data-only SavedVariables parser, including binary strings for Auctionator CBOR; rejects executable expressions, truncation, duplicate keys and unsupported syntax.
- Gzip snapshots and SHA256 verification for all 15 requested SavedVariables sources, backups and TSM's actual AppData.lua. 56 capture manifests preserved across two collection passes. Snapshots include complete 324,313,598-byte Capture files.
- Warband Accountant historical bank balances, separate character wallets, timestamp-free Syndicator cache and explicitly labeled legacy samples. Archive history proves accumulation from 981 to 982 distinct ledger points with one new bank observation, without counting transfers as income.
- Most recently captured bank balance: 15,440,018,739 copper at Unix timestamp 1792481621. The earlier matching balance of 15,437,420,159 copper remains preserved. See CSV/report for exact timestamps.
- Complete Capture normalization validates 24 character identities, 12,427 catalog records, 1,180 scan definitions, 112,409 outcomes, 508 selected operations and 792 acquisition offers. No arbitrary truncation or discarded large file.
- Auctionator adapter reads 1,147,669 daily history records and 412,761 timestamp-free cached quotes. Daily fields mean lowest-low/highest-low/peak availability, verified in installed addon source. Exact realm and variant identities preserved.
- TSM downloaded AppData parser produces 195,087 market/sales-estimate rows across 11 datasets, preserving explicit download timestamps. AppHelper SavedVariables are also archived.
- Additive migrations 002â€“004 and explicit grants; existing importer.py, decode.py, migration 001, Dockerfile and requirements match the original v0.1.0 ZIP byte-for-byte.
- PostgreSQL bulk COPY staging implemented for market/crafting volume. SQL execution is pending, not claimed verified.
- Generated 16-panel Warband Financials dashboard and 8-panel Azeroth Stock Exchange dashboard. Primary metric is actual recorded bank balance. Same-second bank points retain ledger order per snapshot. Character balances, legacy zero samples and timestamp-free caches are separate.
- Financial SQL covers invoices/fees, vendor cash, quest/cache money, crafting-order commission/cuts, personal repairs, training, taxis and postage. Deposit principal and unresolved mail/trade money are separate. No fabricated crafting profits.
- Same restricted sync protocol extended with bounded compressed put2 packets; original put/status and v0.1.0 Journalator import path retained. New worker archives first and preserves failed packets for retry. Windows wrapper extends the existing scheduled task without replacing deployed Journalator/helper/config/credentials.
- API foundation: client-credentials OAuth, regional commodities/connected-realm endpoint selection, raw compressed response preservation, separate fetch/Last-Modified timestamps, ETags, 304/429/503 handling, listing normalization and poll history. Unit-tested controlled responses; no live credentialed fetch performed.
- 27 tests pass: 12 original sync regression checks, 3 new bundle-worker checks, 12 parser/archive/identity/API checks. Python compile checks and Windows PowerShell syntax checks pass.
- Full real-data verification completed against immutable captured snapshots: all original SHA256/lengths checked, all Capture identities serialized without collisions, market parsers read full data, original Journalator decoder produces 19,897 records.
- Prepared server preflight, disposable PostgreSQL integration check, backup/upgrade procedure, Windows task upgrade and rollback instructions. None applied to installed services.

## Blocking deployment

- Verbose SSH stops at `connect`, before any server banner or key exchange. Independent socket.connect fails with WinError 10013 (locally forbidden socket access). This is not an SSH credential/authentication failure and does not establish that the LAN server is down or port 22 closed. Do not retry credentials or expose SSH publicly.
- Existing server code/config must be inspected before installing an upgrade.
- Windows installed sync is outside permitted writable directories; leave it intact and deliver an upgrade package.

## Pending / limitations

- PostgreSQL 17 integration and dashboard SQL execution: no local Docker/PostgreSQL runtime is available. `verify-stack.sh` is ready to run in an isolated disposable database on Nexus. SQL must pass there before production changes.
- Linux shell scripts have been inspected, but not executed or Bash syntax-checked in this Windows runtime, which has no Bash binary. PowerShell scripts were syntax-checked but have not altered the installed task.
- Live server configuration must be inspected; upgrade refuses to overwrite deployed sync source that differs from the v0.2.0 reference.
- Grafana datasource selection, actual dashboard rendering and new end-to-end sync require LAN deployment. Dashboard JSON is prepared, not deployed.
- Live Blizzard OAuth needs a client ID/secret and selected connected-realm IDs. No secrets requested or read. API scheduling, automatic archived-response replay and inferred listing deltas remain pending; no disappearing listing is classified as a sale.
- WarbandNexus, Folio, Planner, TSM SavedVariables, CraftSim, ATT, WoWthing and Journalator Statistics are fully preserved raw; dedicated normalization is not yet implemented for each. Their existing source bytes remain available.
- Own-reagent crafting cost attribution, realized crafting profit, explicit patron enum labels, unresolved counterparties and unmatched lost deposits require further evidence/joins. Coverage is visible rather than guessed.
- TSM parser retains min-buyout and regional estimate fields interpreted by existing Crafting Desk code. Other AppData metrics remain in preserved originals pending expanded parsing.

## Exact next implementation action

From the LAN host, run the read-only preflight and compare deployed sync code, then run `bash verify-stack.sh /absolute/path/to/private-snapshots`. Fix any PostgreSQL integration or dashboard query failures before applying `upgrade-server.sh`. After that check succeeds, deploy and verify the original Journalator path, enable the same Windows task's multi-source wrapper, import both Grafana dashboards, and verify bank points against the preserved snapshot report. This is the first dependency requiring access that Work cannot provide. Independent later work can add API replay/scheduling and the remaining normalized source adapters.


## Audit revision 1 — current continuation

The preceding entries describe the original v0.3.0 handoff. This section supersedes its deployment/wrapper procedure.

- Verified uploaded DuckMoo-Nexus-0.3.0(1).zip matches the preserved original release byte-for-byte.
- Audited migrations, source archival/normalization, packet transport, deployment, tests and all generated dashboard queries against bundled v0.2.0 and the readable installed Windows helper/log.
- Fixed deterministic packet identity and arbitrary latest-character snapshot selection.
- Added explicit dashboard grants and expanded isolated integration verification to both actual restricted roles, including variable queries and source COPY operations.
- Isolated additional imports into separate server and Windows jobs; original Journalator scheduling is preserved.
- Added source/image verification gate, one-transaction additive migration/grants, immutable staged modules, activation recovery, and executable server/Windows rollback scripts.
- Original importer.py, decode.py, migration 001, Dockerfile and requirements remain byte-identical to the uploaded release.
- 30 unit/regression tests pass (13 source tests, 16 sync tests, 1 release gate test). Python compilation and Windows PowerShell syntax checks pass.
- Installed sync log contains successful original import receipt at 2026-10-20 07:57:51 UTC. This is local log evidence, not a live database check.
- No installed task, server service, database, credentials, or sync configuration modified. No LAN reachability assumed.
- PostgreSQL execution, Linux/systemd activation and rollback, dump restore drill, Grafana rendering and full additional-source end-to-end operation remain unverified because this runtime has no PostgreSQL, Docker or Bash/WSL installation. The gate blocks production upgrade until the isolated database verification succeeds on the host.
- Deliverable: DuckMoo-Nexus-0.3.0-audit1.zip; start with AUDIT-2026-10-20.md and revised DEPLOYMENT.md.

## October 23 sync performance follow-up

Verified the installed Windows task reads the Retail account SavedVariables folder
and includes DuckMooCapture.lua plus its backup. It runs every five minutes.
The old pass resent all retained packets and took roughly 14–15 minutes between
successful completions. Receiver now supports a bounded bulk receipt query; the
client uploads only packets without a valid current-generation server receipt.
Historical packets and archives are retained, with reinstall/recovery replay.
The real updated pass succeeded: 1 packet uploaded, 1,164 already committed.
Focused receipt recovery/input cases and the real Windows scheduled run passed.
Installed scripts were backed up before update. Crafting Desk continues rebuilding
from PostgreSQL on its five-minute refresh timer; reload its page to read the new
model. WoW must first save on reload/logout. No exact end-to-end latency guarantee:
large new captures still require processing.

## October 23 — actual Nexus website delivered

Home and Auction House pages now run at http://10.20.30.239, built with Next.js,
React, shadcn components, Tailwind, Motion and Recharts. Read-only PostgreSQL data
feeds real bank history, item search, market/variant/quality selection, price
history, stock context and TSM estimates. Browser-local watchlists and CSV export
are available. Crafting Desk remains linked at :8765; character-sheet pages have
not been built. See WEB-IMPLEMENTATION.md and web/README.md for precise scope and
live evidence. Migration 12 normalizes retained TSM item names/quality; official
item icons enrich incrementally. Original sources, plans and existing services
are preserved. No framework/logo-only prototype is represented as a full site.

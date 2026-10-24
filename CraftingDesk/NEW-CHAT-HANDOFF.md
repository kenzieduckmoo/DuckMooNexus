# October 24 update

The native Nexus guides are deployed. The user explicitly resumed their development; the old optimization pause is superseded. See ../Nexus/PROFESSION-GUIDES-2026-10-24.md and EXECUTION-LEDGER.md for the current scope and evidence. Capture is now 0.9.0; the older notes below are historical.

# Crafting Desk — current handoff

Updated October 23, 2026. Read EXECUTION-LEDGER.md first for R1–R13 reconciliation.
The approved implementation is deployed at http://10.20.30.239:8765 on Nexus;
there is no desktop hosting requirement or separate login on the private LAN.
User confirmed laptop page loading. Saved plan/choice storage is PostgreSQL with
write history. No original desktop JSON or game SavedVariables were overwritten.

Shared batch/product/concentration UI, exact shopping exports, acquisition exports,
and scanner cache/resume fixes are implemented. DuckMooCapture 0.8.0 is installed
in the existing Retail addon folder and packaged in downloads/. The previous
installed addon is backed up under Nexus/crafting-update-2026-10-23.

Remaining external gates: actual laptop save and refresh, and real WoW profession
open/close/reload/context-change behavior. Mocked scanner results are recorded in
the ledger; they do not prove the live game lifecycle. No RTM claim yet.

Relevant implementation: hosted_server.py (LAN Host/Origin restrictions, optional
Grafana auth mode), nexus_snapshot.py (repeatable-read PostgreSQL model assembly,
atomic gzip cache and locking), nexus_storage.py (documents/history),
Nexus/clean-install/compose.crafting.yaml (service and refresh job),
Nexus/clean-install/app/sql/011_crafting_desk.sql,
batch-evaluation.js, product-ui.js, batch-ui.js, concentration-ready.js,
and AddOns/DuckMooCapture/Scanner.lua. The main app lives on the server under
/opt/duckmoo-nexus-clean/app/craftingdesk; refresh timer is duckmoo-crafting-refresh.

Keep execution focused. Deeper guide optimization stays paused, no new secondary
profession scope, no repeated broad test/hash audits. Preserve all original
sources and user choices. Full consumed material cost determines estimated net
profit; missing purchases are a separate cash figure. Preserve mode/quality and
character identity, honor shared stock/reservations, and never invent learner
performance or unavailable cooldown ETAs. Character order remains the explicit
CHARACTER_ORDER list in batch-evaluation.js. Existing game data must sync before
Nexus can refresh it. See README.md for operation and optional desktop fallback.

Prior handoff retained at ../Nexus/crafting-update-2026-10-23/HANDOFF-before-hosting.md;
BUILD-PLAN.md and the original Crafting Desk chat update.txt retain historical
scope. Credentials are intentionally excluded; do not reset working services.

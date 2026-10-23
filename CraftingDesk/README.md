# DuckMoo Crafting Desk on Nexus

Open **http://10.20.30.239/crafting** from the desktop or laptop on the home network.
`Start.cmd` and `Start.ps1` open that address. No desktop command window is needed.
The private-network service has no separate login; Grafana keeps its existing login.

## Current workflows

- Search by product name, choose an exact number of crafts and independent concentration mode/quality, and compare feasible crafters by total net batch profit.
- Materials show full consumption, stock allocated once across the plan, missing purchases and estimated cash cost. Owned materials still count toward profit cost. Shopping exports contain only missing AH purchases, with quality and market separation.
- Concentration Ready uses current projected concentration minus reservations, including characters below cap, in the supplied character order. Economic/data failures have reasons; availability times appear only when the recorded concentration/cooldown evidence supports them.
- Daily plans and saved crafts live in PostgreSQL, with previous versions retained on writes. Browser guide checkpoints and display preferences remain browser-local.
- Recipe investments retain strict margin >20% and regional sale rate >0.1, learner ownership checks, recorded acquisition offers and purchase exports. Primary guides remain available; deeper guide optimization is paused. Secondary professions are excluded from the new workflows.

## Data and operation

Nexus builds its crafting model from PostgreSQL profiles, captured operations/catalog/status, inventory and market quotes. TSM ownership/name archives are preserved in PostgreSQL and decoded during assembly. The refresh timer checks every five minutes and rebuilds when source/API versions change. The native website checks for changed data every 30 seconds while visible and on focus/reconnect. WoW must first write SavedVariables on reload/logout, then the existing sync uploads them. No manual update button is required.

The large recipe model and calculations run in an internal worker on Nexus. The browser requests the filtered results it needs. Saved plans/setups use revision checks and Undo to preserve changes made on another device. The original hosted interface at **http://10.20.30.239:8765** and the `--local` desktop fallback remain available.

Profits are estimates after the configured selling fee and full material value. They exclude random bonus yields/refunds and are not actual earnings. Unsupported gear output variants need a manual sale price. Missing or invalidated captures are not treated as verified current operations. Unknown cooldowns do not receive invented ETAs.

The original desktop `local-data.json`, `daily-plan.json` and `saved-setups.json` are preserved. `Start.cmd --local` or `Start.ps1 -Local` runs the optional original desktop server; that is a separate fallback and does not synchronize saved choices back from Nexus automatically.

## Capture addon

`downloads/DuckMooCapture-0.8.0.zip` contains persistent scanner cursors/context and bounded validation. Known changed contexts invalidate estimates while retaining the source records; temporarily unavailable APIs pause safely. The focused harness measured six initial queries, zero ordinary reopen queries, and one validation query for unchanged skill/reload instead of six repeated outcome queries. Real game reopen/reload/change confirmation remains a release gate.

## Deployment and evidence

See `../Nexus/clean-install/compose.crafting.yaml`, `hosted_server.py`, `nexus_snapshot.py`, and `nexus_storage.py`. The service binds the Nexus private address, permits explicitly configured Host/write Origin values, and runs as an unprivileged container user with a separate database role. Keep this home-network app private; authentication mode can be restored with `CRAFTING_ACCESS=grafana` and the Grafana auth URL.

Implementation status and remaining real-device/game checks are in `EXECUTION-LEDGER.md`. Older chronological README notes are preserved in `../Nexus/crafting-update-2026-10-23/README-before-hosting.md`. This is not yet an RTM claim.

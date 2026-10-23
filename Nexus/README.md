> **Audit revision 1:** Use `AUDIT-2026-10-20.md` and the revised `DEPLOYMENT.md`. Additional sources now use separate jobs; the original Journalator task is preserved. This package is prepared for host verification, not deployed.

# DuckMoo Nexus v0.3.0, prepared October 20, 2026

Local implementation of expanded ingestion and two Grafana dashboards. The production Journalator importer is preserved byte-for-byte. This package has not been deployed.

Start with `DEPLOYMENT.md`. Run `verify-stack.sh` against the separately preserved source snapshots on the Linux host before production migration. `EXECUTION-LEDGER.md` records verified work, limitations and the exact continuation action. `verification/real-data-verification.json` contains actual source counts and bank observations, not fixture metrics.

Contents:

- `duckmoo-nexus/`: original importer plus source archival/normalization, bulk market/crafting loading, additive SQL 002â€“004, role grants, API collector and Grafana dashboards.
- `sync-0.3.0/`: compatible compressed packet extension to the existing receiver/worker and an upgrade for the existing Windows task. It preserves the locally fixed Journalator script and credentials.
- `sync-reference/`: original v0.2.0 reference for inspecting deployed differences.
- `verification/`: real-data report and bank history CSV.
- `preflight.sh`, `verify-stack.sh`, `upgrade-server.sh`: inspection, disposable database verification, backup and additive deployment.

Local checks: 27 unit/regression tests pass, Python source compilation passes, PowerShell files pass syntax parsing, and complete source archive SHA256/length checks pass. Full Capture parses to 112,409 outcomes with no discarded observations. PostgreSQL SQL execution, Linux shell execution, actual SSH synchronization of v0.3.0, Grafana rendering and live Blizzard API collection remain unverified here.

No full Nexus website or Crafting Desk UI migration is included. The original Crafting Desk continuity files have not been modified.

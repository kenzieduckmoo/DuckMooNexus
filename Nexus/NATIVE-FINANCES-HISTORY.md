# Native financial workspace and character history — October 23, 2026

User authorized continuing implementation through the remaining usage window.

## Delivered implementation

- `/finances`: matching native Nexus workspace, navigation and home card. Grafana remains available as an original dashboard link.
- Actual warbank observations and selected-period growth; recorded income, spending, net cash after deposits; daily income/spending and cumulative cash-flow graphs; category and character breakdowns.
- Patron-order daily/cumulative graphs, character/profession filters, commissions/cuts, reagent-supplied counts and searchable paginated order records. Cumulative history includes earlier recorded earnings. Raw patron gold is not profit after reagent cost.
- Searchable financial component ledger with evidence, pagination and page CSV exports (amount columns explicitly in copper). Preset and custom date ranges use America/Chicago; custom end date is inclusive.
- Auction posting/refund/outcome section. Net deposit outflow is not mislabeled as exact expired/cancelled loss; records lack exact matching identifiers.
- Uses existing PostgreSQL views and resolved ownership decisions, including the user's external 50,000g payment decision. Unresolved transfers stay excluded. Missing monetary fields are flagged rather than invented.
- New character History tab: source-separated retained Folio/API profile observations, level/ilvl graphs and observed changes to level, equipped ilvl, specialization, guild and location. Actual observation timestamps are used; older raw archives may not yet be normalized. This is an initial historical view, not complete omni-capture.
- General omni-capture remains separate from crafting capture, per AddOns/AGENTS.md. No additional game-side collector was created in this pass.

## Verification

- TypeScript and production builds passed for financial workspace and character history. Initial live API returned in 0.25 seconds.
- Cash totals reconcile across daily closing totals, categories and characters; deposit movement reconciles to posting/refund totals. Patron totals reconcile against original Journalator transaction payment/cut fields. Live profession filter verified in API and browser; daily/cumulative chart controls verified. Deposit and activity tabs also checked in the browser. Nightchicken history rendered 24 Folio observations and 7 changes; graph and sample timestamps were checked.
- Public page and source package: `Nexus/nexus-native-finances.tar.gz`; deployment helper: `Nexus/deploy-native-finances.py`.
- Website remains read-only in PostgreSQL; added SELECT grants for existing financial views and retained character records. No data reset, reimport, saved-choice mutation or game-file changes.
- Deployment backups: `/opt/duckmoo-nexus-clean/web-update-backups/`, timestamped native-finances folders.

## Next window

1. Richer progress, vault, currencies, encounters, quest, PvP and profession-knowledge displays are now live; see `CHARACTER-PROGRESS-2026-10-23.md`. Named currency capture remains pending.
2. Plan a bounded historical backfill from retained Folio archives to enrich history without replaying unrelated financial/Capture imports.
3. Build Retail omni-capture as a separate addon and source adapter. Forever in-game integration waits until November 4; character-life capture must be ready before the expected January/February Hardcore window.
4. Real-game crafting scanner lifecycle and actual laptop save/refresh are still external verification gates. Deeper profession-guide optimization stays paused.

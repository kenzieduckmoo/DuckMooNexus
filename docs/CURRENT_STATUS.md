# Current status â€” October 23, 2026

## Delivered

- Native Nexus website on the private server: overview, item-name auction search, dedicated character sheets, warband profession board, Crafting Desk and financial workspace. Grafana remains available separately.
- PostgreSQL source archival and source-specific adapters; scheduled auction/public-character API imports and Windows SavedVariables sync.
- Character pages: equipment/artwork, inventory, professions, history, visual vault/weekly progress, completed quest chronicle with API/Omni source choice, title search and recorded turn-ins, searchable encounters, currencies, PvP and source evidence.
- Financials: actual warbank observations and growth, recorded cash movement, raw patron-order gold with profession filters and graphs, financial activity and auction-deposit movement.
- Nexus-hosted Crafting Desk and internal calculation worker, with automatic source refresh and preserved saved choices.
- Independent `DuckMooOmniCapture` 0.1.4 Retail preview installed; source adapter, automatic sync allowlist and website integration deployed. It captures named currencies, vault, lockouts, owned keys, equipment, basic character details, completed quest IDs, naturally opened knowledge and lightweight adventure events. It does not depend on the crafting scanner or third-party collectors.

## Important remaining work

1. Real Omni captures and the corrected logout lifecycle have been observed. Acknowledged journal rotation has now completed in the actual client, with historical event records and recovered current profiles retained. Broader capture/scanner coverage remains partial.
2. Warband profession board is deployed with source-aware skill, knowledge, concentration forecasts and recorded patron earnings. Character/profession shortcuts connect Crafting Desk and financials. Folio/Planner 0.5.3 context corrections are installed; their next real client load remains to be verified.
3. Verify the crafting scanner's real in-game open/close/reload/context-change lifecycle. Confirm actual laptop save/page-refresh persistence.
4. Expand retained character history with a bounded backfill; preserve original archives and source timestamps.
5. Forever in-game work waits until November 4. Hardcore character-life capture must be ready before the expected January/February start; the exact date has not been announced. Deeper profession-guide optimization remains paused.

Latest detail: `Nexus/OMNI-CAPTURE-2026-10-23.md`, `Nexus/CHARACTER-PROGRESS-2026-10-23.md`, `Nexus/NATIVE-FINANCES-HISTORY.md` and `CraftingDesk/EXECUTION-LEDGER.md`. Earlier deployment/audit notes describe their own dated state, which may have been superseded.

Deferred feature requests: see [Nexus backlog](../Nexus/BACKLOG.md), including reagent buying-day and quantity recommendations.

Latest profession delivery: `Nexus/PROFESSION-BOARD-2026-10-23.md`. The reagent buying-day/quantity advisor remains deferred in the backlog.

Profession concentration freshness now feeds the shared Crafting Desk model from valid newer Omni observations, with matched currency IDs and original resource timestamps. The new 0.1.4 discovery path awaits an actual client save; existing current Omni resources were verified through the live board and crafting API. See `Nexus/PROFESSION-RESOURCE-FRESHNESS-2026-10-23.md`.

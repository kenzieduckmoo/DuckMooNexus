# Current status â€” October 23, 2026

## Delivered

- Native Nexus website on the private server: overview, item-name auction search, dedicated character sheets, Crafting Desk and financial workspace. Grafana remains available separately.
- PostgreSQL source archival and source-specific adapters; scheduled auction/public-character API imports and Windows SavedVariables sync.
- Character pages: equipment/artwork, inventory, professions, history, visual vault/weekly progress, searchable completed quests and encounters, currencies, PvP and source evidence.
- Financials: actual warbank observations and growth, recorded cash movement, raw patron-order gold with profession filters and graphs, financial activity and auction-deposit movement.
- Nexus-hosted Crafting Desk and internal calculation worker, with automatic source refresh and preserved saved choices.
- Independent `DuckMooOmniCapture` 0.1.3 Retail preview installed; source adapter, automatic sync allowlist and website integration deployed. It captures named currencies, vault, lockouts, owned keys, equipment, basic character details, completed quest IDs, naturally opened knowledge and lightweight adventure events. It does not depend on the crafting scanner or third-party collectors.

## Important remaining work

1. Seven real characters have reached PostgreSQL. Real data exposed and led to a logout lifecycle correction and sparse-bag null handling. Legacy profiles were recovered from earlier retained session events, with their original timestamps. The 0.1.2 logout correction has since been observed in real client saves. Installed 0.1.3 adds acknowledged journal rotation; its load/save/sync/load cycle remains to be verified. See `Nexus/OMNI-LIVE-DATA-2026-10-23.md`.
2. Verify acknowledged event-journal rotation in the actual client. Version 0.1.3 implements the confirmed-archive receipt bridge and retains newer unsent events. The preview retains 10,000 unconfirmed events per character and pauses/counts overflow; it is not yet a complete long-term life recorder. Direct carried bags and partial reputations are implemented in 0.1.1. Add bank storage and broader character progress coverage.
3. Verify the crafting scanner's real in-game open/close/reload/context-change lifecycle. Confirm actual laptop save/page-refresh persistence.
4. Expand retained character history with a bounded backfill; preserve original archives and source timestamps.
5. Forever in-game work waits until November 4. Hardcore character-life capture must be ready before the expected January/February start; the exact date has not been announced. Deeper profession-guide optimization remains paused.

Latest detail: `Nexus/OMNI-CAPTURE-2026-10-23.md`, `Nexus/CHARACTER-PROGRESS-2026-10-23.md`, `Nexus/NATIVE-FINANCES-HISTORY.md` and `CraftingDesk/EXECUTION-LEDGER.md`. Earlier deployment/audit notes describe their own dated state, which may have been superseded.

# Direct carried bags and reputations — October 23, 2026

Follow-up to the GitHub source import. Omni Capture Retail preview is now 0.1.1.

- Direct carried-bag/reagent-bag capture: bag/slot identity, quantity, captured item names/links, binding, quality and texture metadata. Uses equipped bag indices only; does not guess bank/warbank container IDs or open a bank UI.
- A known empty bag clears old contents. Missing APIs retain the previous observation with unavailable status. Free-slot versus observed-stack mismatch marks the sample partial rather than proving emptiness.
- Direct reputations: visible factions and previously observed faction IDs, standing, renown level/progress when returned, and account-wide flags. Collapsed/undiscovered rows remain partial coverage. No faction UI expansion is automated.
- Bag/faction events join the existing three-second section-specific refresh batching. Capture remains independent of DuckMooCapture and other collectors.
- The existing Omni adapter accepts both new source sections and retains them in PostgreSQL. No migration or historical-data replay is required for these additive sections.
- Native Inventory displays a separate own-capture bag panel with item-name search and bag selection. Existing cached storage remains a separate observation. Counts are not added across sources. These direct bag observations are not yet substituted into Crafting Desk's shared inventory budget.
- Native Reputations defaults to the newest explicitly dated source and allows switching among available Omni, Folio and Blizzard observations; renown and warband labels are explicit.

Focused Lua 5.1 checks cover unavailable/empty bags, carried-only boundaries and renown/account labels. TypeScript checks passed. Real in-game capture, saved-file upload and observed item/faction coverage remain unverified until the user next logs in and reloads/logs out.

The 10,000-event preview journal limit and acknowledged-rotation requirement remain. Currency icon IDs remain captured but not fully resolved to website image URLs. Bank storage, deeper collection coverage and Forever client work remain pending. Keep the original SavedVariables and raw source archives intact.

Deployment completed with production build/TypeScript success. Final source backup: `/opt/duckmoo-nexus-clean/web-update-backups/20261023T194243Z-omni-capture`. Installed Retail version: 0.1.1. Browser confirmed the direct-bag waiting state and available reputation source choices without replacing existing cached observations. Source changes are published in GitHub commit `ff4ef56df542c2a4afef0b0a3af61dea4916c616`.

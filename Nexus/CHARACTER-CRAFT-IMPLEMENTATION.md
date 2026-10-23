# Character sheets and native Crafting Desk

## Website polish, October 23

- Directory order: any tag containing the word Main (case insensitive), then descending level, then descending equipped item level; names/realms break remaining ties. Crafting Desk's separate preferred character order remains intact.
- Character crafting link has its own style; overview AH button has explicit contrasting colors, resolving their shared-style collision.
- Overview chooses one of five Midnight scenes on each page load: Silvermoon, Eversong, Zul'Aman, Harandar, Voidstorm. Official artwork source: https://worldofwarcraft.blizzard.com/en-us/midnight. Four new images are served as preoptimized local WebP assets; original downloaded artwork is retained in Nexus/hero-original-art.
- Warbank change is the difference between the earliest and latest valid sample in the selected 7D/30D/90D window, matching the graph. Tooltip gives exact sample timestamps; unavailable periods remain unknown.
- Financial dashboards now use the same icon/title/description workspace-card layout as the other three workspaces.
- Focused comparator/window checks and production build passed; live browser confirmed main-first ordering, both text colors, different range deltas, a new banner after reload, and successful image loading. Deployed to Nexus; source bundle Nexus/nexus-overview-polish.tar.gz; before-change code retained under server web-update-backups.

Authorized 2026-10-23: native character sheets using public Blizzard profiles and SavedVariables; native Crafting Desk matching Nexus; automatic freshness detection. Preserve original source files and saved documents. Reuse existing crafting calculations. Profession-guide algorithm expansion remains paused.

## Delivered to Nexus

- Public character API worker deployed: all 58 roster identities matched successfully. Scheduled every five minutes, successful profiles refreshed after four hours or a new addon character observation. Only public endpoints; unavailable sections remain explicit.
- Native directory and character sheets: paper doll, public artwork, gear inspection, attributes, talents, professions, inventory, progress, collections, notes and full expandable source evidence. Newer known observations take precedence; API download time is not an in-game sample time.
- Additional character-associated Warband Nexus, WoWthing Collector and DuckMoo Warband records normalized from retained PostgreSQL archives. Account-wide tables are not assigned to individual characters. Mixed Lua keys preserved in JSON-compatible form.
- Native Crafting Desk: product-name search, exact batches, costs/profit, concentration projections, persistent plan, shopping/imports, saved scenarios and existing profession guides. Heavy model parsing/calculation runs in the internal Node worker, not in the browser. Guides reuse existing algorithms; deeper optimization remains paused.
- Saved documents retain revision history and use conditional writes; stale revisions return a conflict. Successful changes provide Undo, which also refuses to overwrite intervening changes.
- Automatic browser version checks (30 seconds while visible; focus/reconnect) update data without resetting current controls. SavedVariables still require the game to save, then the existing five-minute sync/snapshot pipeline.

## Verification and limits

- Production Next build and TypeScript check passed. Services run on Nexus; craft-engine has no published port. Website retains its read-only database role; saved changes use the existing dedicated crafting service.
- Live browser: rendered character, equipment inspection, professions and exact three-craft Phoenix Oil result; three crafts produce 15 output with matching reagent requirements. Older captures honestly show recipe-availability warnings.
- Live document save, fresh read and Undo passed through the website and HTTP API; original choices restored. Stale revision rejection verified. Invalid recipes return a prompt 404.
- Focused source identity/mixed-key/account-wide separation and vendor-only purchase export checks passed.
- Original SavedVariables, desktop model and JSON choices were not overwritten. Deployment code backups are under /opt/duckmoo-nexus-clean/web-update-backups; final source package is Nexus/nexus-character-craft.tar.gz.
- Public API omissions and addon-specific encoded fields remain inspectable source data, not invented completion. In-game addon lifecycle checks and actual laptop save/refresh remain external verification gates.

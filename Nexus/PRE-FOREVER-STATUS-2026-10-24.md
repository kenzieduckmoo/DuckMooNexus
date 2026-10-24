# Pre-Forever checkpoint — October 24, 2026

## Implemented and deployed

The native Nexus website has Overview, Auction House, dedicated character sheets, Crafting Desk, Financials, Professions and the reagent buying advisor. Sources flow through PostgreSQL, with original source archives retained separately from normalized observations and derived forecasts. Scheduled game-file sync and API imports remain the data suppliers. Grafana remains available as a separate dashboard interface.

Latest delivery: the buying advisor identifies repeatedly purchased commodity reagents, shows prices and recorded stock, provides conditional planning quantities and accumulates weekday evidence automatically. Details and limits are in `BUYING-ADVISOR-2026-10-24.md`.

## Addon documentation and packages

Six separate addon ZIPs have comprehensive USER-GUIDE.txt files, roughly 1,000 words each, covering workflows, commands, collected data, storage, retention, integration and limitations. All owned TOCs use `## Category: DuckMoo Media`. Player databases, credentials, personal acknowledgement receipts and development files are excluded from the release ZIPs. The existing licenses are retained; no new open-source license is assigned to collectors that did not declare one.

| Addon | Version | Individual source repository |
| --- | --- | --- |
| DuckMooCapture | 0.9.0 | https://github.com/kenzieduckmoo/DuckMooCapture |
| DuckMooFolio | 0.5.3 | https://github.com/kenzieduckmoo/CharacterFolio |
| DuckMooPlanner | 0.5.3 | https://github.com/kenzieduckmoo/ConcentrationPlanner |
| DuckMooWarband | 0.4.0 | https://github.com/kenzieduckmoo/DuckMooWarband |
| DuckMooOmniCapture | 0.2.0 | https://github.com/kenzieduckmoo/DuckMooOmniCapture |
| FiammaCollector / Fia's ATDART | 0.1.2 | https://github.com/kenzieduckmoo/FiasATDART |

The three newly created repositories are private. Existing repository visibility is preserved. Existing remote source was reconciled before updates; Fia's newer repository version 0.1.2 was retained over the older installed 0.1.1 copy. Planner's repository-required pull-request workflow was followed and merged. The Nexus aggregate source is supplementary, not a replacement for individual repositories.

Prepared ZIPs are under `releases/curseforge-ready-2026-10-24/`. They are upload packages for the user, not a claim of publication on CurseForge or completion of every preview feature. Source and package checks do not establish unobserved client compatibility.

## Current live verification and remaining external checks

- Actual Crafting Capture 0.9.0 whole-quality scans have completed and reached PostgreSQL, including a recorded cache reuse. Captured whole-quality outcomes contain no within-slot split stacks. Exhaustive close/reopen/reload/combat/context-change behavior and actual timing remain separate client observations.
- Actual Omni 0.1.4 concentration discovery/save has now been observed, with matching pools in Professions and Crafting Desk. Earlier logout preservation and acknowledged journal rotation were also observed. Folio/Planner context-transition edge cases remain separate from ordinary successful captures.
- Fixed the remaining crafting refresh race: a pending raw archive cannot mask the later completion of its normalized import. Source labels now identify usable data. See `CRAFTING-FRESHNESS-2026-10-24.md`.
- Actual laptop save/page-refresh confirmation. Hosted saved-choice persistence and the page loading were checked, but those are separate evidence.
- Weekday advice needs more automatically accumulated history. A waiting evidence gate is not unfinished implementation.
- Forever-specific client access and capture validation wait until November 4. Hardcore character-life coverage must be ready before the expected January/February start; its exact date remains unannounced in the project brief.
- Profession guides resumed at the user’s request and the native workflow is deployed; see `PROFESSION-GUIDES-2026-10-24.md`. Unknown game observations and larger future collector coverage remain explicit evidence gates.

This is a usable pre-Forever checkpoint with explicit remaining checks, not an RTM declaration for every addon or a claim that the entire long-term Nexus vision is finished.

Crafting Capture 0.9.0 now scans one quality per whole reagent slot rather than mixed-stack permutations. The cache revision prevents resuming older mixed jobs; actual timing remains a client measurement.

## Later October 24 preparation

Omni 0.2.0 and the native Adventure Journal are delivered, with independent Forever sync, character sheets and expanded storage/collection/activity/life observations. The earlier 0.1.4 actual-client results above do not establish live validation of the new 0.2.0 paths. See FOREVER-READY-2026-10-24.md.

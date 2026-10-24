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
| DuckMooOmniCapture | 0.1.4 | https://github.com/kenzieduckmoo/DuckMooOmniCapture |
| FiammaCollector / Fia's ATDART | 0.1.2 | https://github.com/kenzieduckmoo/FiasATDART |

The three newly created repositories are private. Existing repository visibility is preserved. Existing remote source was reconciled before updates; Fia's newer repository version 0.1.2 was retained over the older installed 0.1.1 copy. Planner's repository-required pull-request workflow was followed and merged. The Nexus aggregate source is supplementary, not a replacement for individual repositories.

Prepared ZIPs are under `releases/curseforge-ready-2026-10-24/`. They are upload packages for the user, not a claim of publication on CurseForge or completion of every preview feature. Source and package checks do not establish unobserved client compatibility.

## Remaining external checks and deliberately deferred work

- Normal-client validation of Crafting Capture 0.9.0 close/reopen/reload/context-change behavior.
- Actual client capture/save of Omni 0.1.4's new concentration discovery and Folio/Planner 0.5.3 context guards. Earlier actual capture, logout preservation and acknowledged journal rotation were observed; newer path coverage must remain distinct.
- Actual laptop save/page-refresh confirmation. Hosted saved-choice persistence and the page loading were checked, but those are separate evidence.
- Weekday advice needs more automatically accumulated history. A waiting evidence gate is not unfinished implementation.
- Forever-specific client access and capture validation wait until November 4. Hardcore character-life coverage must be ready before the expected January/February start; its exact date remains unannounced in the project brief.
- Deeper profession-guide optimization remains paused. Larger collector coverage and other future ideas are not silently claimed complete by this checkpoint.

This is a usable pre-Forever checkpoint with explicit remaining checks, not an RTM declaration for every addon or a claim that the entire long-term Nexus vision is finished.

Crafting Capture 0.9.0 now scans one quality per whole reagent slot rather than mixed-stack permutations. The cache revision prevents resuming older mixed jobs; actual timing remains a client measurement.

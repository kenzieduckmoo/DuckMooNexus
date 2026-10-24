# Crafting Desk execution ledger

Updated October 23, 2026. Approved implementation is deployed to Nexus at
http://10.20.30.239/crafting, rebuilt as a native Nexus workspace. The original
hosted interface remains at :8765 as a fallback. The user confirmed that fallback
loads correctly on the laptop.
The extra Grafana login was then removed for this private-network application.
**Not yet RTM: real WoW scanner lifecycle validation remains outstanding.**

## Requirement reconciliation

| ID | Requirement | Delivered evidence / remaining gate |
|---|---|---|
| R1 | Shared batch evaluation; one product row; best feasible crafter | Implemented in batch-evaluation.js/product-ui.js. Name search deduplicates variants while preserving quality/mode candidates; full requested count, highest feasible net profit and shared inventory. Focused batch tests passed. Browser verified Phoenix Oil name search and exact three-craft quantities/profit. |
| R2 | Remove workshop and clean terminology | Workshop removed; character control retained in product flow. Main saved-choice UI uses saved crafts. Existing saved choices preserved. Browser reviewed. |
| R3 | Craft details, shortlist, exact shopping | Exact quality/needed/reserved/missing amounts, purchase cost and full material value; per-market missing-only Auctionator exports. Shared plan accounting regression passed. Browser verified three-craft detail and successful clipboard copy over LAN HTTP. |
| R4 | Current concentration rather than cap-only | Shared budget projection minus reservations, sub-cap pools, known charges/cooldowns and full feasible batch. Focused current-budget tests passed; hosted browser displayed sub-cap characters. |
| R5 | Character grouping/order, profession details and exports | Supplied character order used; profession pools grouped by character; skill/current concentration/reservations and exact shopping available. Unknown characters retained. Duplicate profile professions deduplicated during model assembly. |
| R6 | Actual ineligibility reasons; known-only ETA | Capture age, missing price, loss, margin, sale rate/daily volume, missing learned availability, budget and cooldown explanations. ETA only from known budget/cooldown evidence. Focused missing-availability tests passed. |
| R7 | Scanner cache/resume | DuckMooCapture 0.8.0 installed with old addon backed up. Persistent profession/build/trait context, cursors, per-recipe probe validation and safe pause. Measured fixture: 6 initial / 0 reopen / 1 unchanged-event / 1 reload queries; previously 6 repeated on event/reload. Full existing Lua harness plus trait/second-recipe/unknown-API fixtures passed. **Real WoW open/close/reload/context-change check remains.** |
| R8 | Nexus hosting and laptop access; local fallback | Hosted unprivileged service, restart policy and five-minute data refresh timer active. LAN host/origin restrictions verified. User confirmed laptop page loads. Existing plan/saved crafts survived identical save and fresh read via HTTP; **actual laptop save/page-refresh confirmation remains requested**. Desktop fallback retained; launchers default to Nexus. |
| R9 | Recipe investment acquisition | Existing strict >20% margin and >0.1 regional sale-rate/learner checks retained; missing recipe AH export and separate recorded vendor instructions added, capture records vendor zone/subzone. Investment and acquisition tests passed; no invented learner stats. |
| R10 | Native guides delivered; user resumed work October 24 | Server-saved alternatives/progress, stable steps, bounded next batches, vendor exclusions, checkpoints and exports verified. See the October 24 delivery note. |
| R11 | Ignore secondary professions | New product/concentration flows and primary guide selector exclude secondary professions; historical raw data preserved. |
| R12 | Continuity | Current README, ledger and new-chat handoff updated. Prior README/ledger/handoff preserved under Nexus/crafting-update-2026-10-23. |
| R13 | Release reconciliation | Implementation packaged/deployed, original user files preserved, addon archive/install completed, focused model and primary-guide regressions passed. **No RTM claim until external checks above pass.** |

## Deployment and data

- October 23 native website: Craft & profit, Concentration, Your plan, Profession guides, Saved crafts. Matching Nexus components, responsive cards, exact-count economics, reagent tables, name search, shared shopping and exports. Existing calculation modules reused.
- Heavy recipe parsing and calculations now run in an internal Node worker on Nexus. The browser requests filtered results rather than downloading the entire model.
- Document revision checks reject stale writes; successful mutations offer Undo and retain PostgreSQL history. Live saved-setup write/read/Undo and stale-revision rejection verified; original documents restored afterward.
- Browser version checks run every 30 seconds while visible, with checks on focus/reconnect. The five-minute source/snapshot pipeline and scheduled public API collector supply new data. No manual update button required.
- Character sheets are native pages at /characters, with public API equipment/artwork and timestamped addon records. This does not replace the outstanding real-game scanner gate.

- Host app: /opt/duckmoo-nexus-clean/app/craftingdesk; compose.crafting.yaml.
- PostgreSQL plans/saved crafts: crafting_documents; prior writes: crafting_document_history.
- Initial desktop choices seeded only when absent. Original local-data.json, daily-plan.json and saved-setups.json untouched.
- Canonical profiles, Capture, Syndicator inventory and market quotes come through PostgreSQL; TSM ownership archives are decoded from preserved PostgreSQL chunks.
- Latest Capture metadata backfill added 58 status observations from snapshot 820, without replaying older archives; future snapshots use the updated adapter.
- Model 0.9.1 forces corrected numeric profile keys, deduplicated professions and scan-status refresh. Initial hosted model: 58 characters, 119,557 recipe variants, 2,201 product groups; counts change with new data.
- Private cache /var/lib/duckmoo-crafting; separate database role; no credentials in documentation.
- Old installed addon preserved under Nexus/crafting-update-2026-10-23/installed-addon-backup-20261023-005753. Original SavedVariables untouched.

## Validation scope

One final regression pass: 17 Python tests; Node shared batch, concentration-ready,
daily-plan, guide and investment suites passed. Earlier targeted Lua lifecycle and
existing addon harness passed. Syntax checks passed for changed browser/backend
modules. Live checks: unauthenticated page/status return 200 without a login
challenge; unrelated Host and write Origin return 403; unchanged plan/setups save
and reread compare equal. Browser confirmed product search, three-craft accounting,
clipboard export, character order and current sub-cap concentration.

## Next concrete action

Obtain the user's real game reopen/reload/context-change result and laptop
save/refresh result. Investigate any reported mismatch against fresh saved Capture
and profile data; do not restart broad audits or guide optimization. Reconcile
these two remaining external gates, then assess RTM. Prior planning/history is in
the preserved ledger and VERIFIED-BASELINE-2026-10-19.md.

October 23 follow-up: verified the desktop sync includes DuckMooCapture current
and backup SavedVariables. Fixed full historical packet retransmission: one bulk
receipt query skips known committed packets while retaining source history and
recovery replay. Real scheduled pass succeeded with 1 new upload / 1,164 already
committed. The pipeline is game save -> scheduled upload -> PostgreSQL import ->
Crafting Desk model refresh -> page reload. No desktop Crafting Desk process is
required.

## Profession resource freshness follow-up — October 23, 2026

R4/R5 now accept newer valid Omni concentration and opened-profession skill observations in the hosted model, matched by character GUID, child skill-line ID and concentration currency ID. Missing/older/invalid resources do not erase a valid earlier pool. New resources do not establish learned recipes or captured outcomes, and saved plans/setups are unchanged. Model refresh signature advanced to crafting-0.9.2. The first Omni journal rotation was observed in the actual client; the separate crafting scanner's live lifecycle gate remains outstanding. Profession-guide optimization remains paused.

## Pre-Forever closeout — October 24, 2026

Actual 0.9.0 whole-quality scans have completed and reached Nexus with unsplit reagent allocations and a recorded cache reuse. Omni 0.1.4's discovered concentration pools now agree between Professions and the hosted Crafting Desk. These are real source observations, distinct from a full controlled game-transition test or physical laptop confirmation.

Fixed a model freshness race where raw archival could advance a global checkpoint before normalization finished. Signature crafting-0.9.3 tracks each relevant usable source/version; source labels exclude pending normalized imports while keeping committed raw-only TSM ownership usable. The actual refresh SQL passed a synthetic temporary-row PostgreSQL check, then the production image/model/service were updated. Saved plans/setups and source archives were preserved. Deeper guide optimization remains paused; no blanket RTM declaration replaces the documented external checks.

## 2026-10-24: Profession guides resumed
The user explicitly resumed guide development after the native Nexus migration, whole-quality collector changes, and API auction imports. Work in progress: server-saved route choices/progress and bounded next-batch shopping; keep uncertain skill gains, random yields and unlocks explicit. This supersedes the previous guide optimization pause.

Completed and deployed: native guide alternatives, PostgreSQL guide documents with revisions/history/Undo, progress migration from browser storage, stable step identities after skill updates, up-to-ten-craft next-batch material lists, separate checkpoint inputs, vellum and vendor exclusions. Focused workflow/route checks, TypeScript/build and all eight live route endpoints passed. Browser save/independent-page persistence and Undo verified. Remaining unknown vendor prices and random-yield/unlock/skill-up evidence are explicit, not fabricated. See Nexus/PROFESSION-GUIDES-2026-10-24.md.


## October 24 — cross-character crafting continuity repair

Live diagnosis found a stale Munsell Ink plan entry was propagating its missing-recipe warning into unrelated characters’ batch eligibility. The native engine also globally blocked additions after any completion until both inventory and planner saves advanced. Neither condition establishes corrupted SavedVariables. The latest Capture had replacement Munsell Ink scan outcomes; the old mixed-reagent plan identity was no longer present.

The native workspace now provisionally deducts completed concentration per character/profession and selected materials from older accessible stock. New item observation timestamps let fresh inventory replace those deductions. A stale saved line keeps its warning, known material reservations and concentration demand, while unrelated crafts remain eligible. Matching recaptures with unchanged output, quantity, materials, profession and concentration cost remain usable; changed results still require review. Saved plan/setup documents and raw sources are not rewritten by deployment.

Focused continuity and shared-batch checks passed; existing daily-plan and concentration checks passed for the initial fix. Next.js production build passed. Live native API recovered 19 eligible profession entries out of 32 at the time checked. A read-only worker prepare accepted Hammeredchic’s Refulgent Copper Ingot alongside an injected stale line and retained it, without saving a document. Pending completion accounting is conservative and remains an estimate until newer observations arrive; this is not an additional in-game validation claim.

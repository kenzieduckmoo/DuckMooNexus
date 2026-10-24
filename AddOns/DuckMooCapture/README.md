# Current release: 0.9.0 — whole-slot quality scanning

The background scanner uses one quality for each required reagent slot's entire
quantity. Ten ore with two qualities has two choices, not eleven split-stack
allocations. Different slots still combine independently and every available
quality is included. Both concentration modes and existing scan safety limits
remain. Older persisted scan jobs cannot resume under the new allocation policy;
normal rescanning replaces prior recipe results. Manual capture can still record
an actual mixed-quality craft. Mixed-stack cost optimization is deliberately
outside this scanner's scope. No live speed measurement is claimed.

See USER-GUIDE.txt for the current behavior. Earlier version notes follow.

Current release documentation: see **USER-GUIDE.txt** for installation, commands, captured data, storage, Nexus integration and current verification limits. Earlier version notes below are historical.

# DuckMoo Capture 0.8.0

Passive, read-only collection for Crafting Desk. Replace the existing DuckMooCapture folder in Retail Interface/AddOns with this version, then reload or restart WoW. Existing SavedVariables remain compatible.

## Cache and resume in 0.8.0

Profession jobs and partial cursors now survive a normal SavedVariables save and reload. Unchanged skill/specialization events validate cached results instead of clearing every profession. Build, profession, recipe list and trait selections are compared; gear/buff checks validate each sampled recipe in bounded slices. An unavailable operation pauses validation and preserves previous observations rather than forcing a new scan.

Completed prior outcomes stay stored while a replacement is collected. Known-invalid contexts are marked so Crafting Desk excludes them until refreshed. Explicit `/dmcapscan` still requests a scan. `scanStatus` records reset reasons, validation query counts and cache hits. The first scan under this cache format establishes its checkpoints; old observations are retained.

Focused harness: six initial outcome queries, zero ordinary reopen queries, one validation query for an unchanged skill event and one after reload. Specialization and second-recipe stat changes invalidate; transient failures retain data. These are mocked checks; the real Retail lifecycle remains a separate release gate.

## Normal use

Open your professions and browse recipes normally. No capture button, slash command, or ready-to-craft inventory is required.

Opening a profession collects the recipe catalog exposed by the client in small batches: learned status, reagent schematics, profession information, and available skill-up fields. Unavailable fields remain unknown. No filters or selections are changed.

Browsing a recipe and changing reagents triggers a quiet background refresh. Complete selected setups are recorded. The addon also queries two schematic reagent presets, with and without concentration, using the first/last offered required reagent alternatives and no optional additions. These are sampled previews, not exhaustive optimization. They do not consume or require ownership of materials; the API may still refuse an operation because of client restrictions or insufficient concentration.

Gear, player buff, and currency changes refresh the visible recipe. The addon never crafts, buys items, allocates reagents, switches recipes, or toggles concentration controls.

WoW writes SavedVariables on reload/logout. After that, use Import game snapshots in the app. Previews appear in Captured crafting opportunities, with the searchable recipe catalog below. /dmcap remains an optional diagnostic refresh, not the normal workflow.

## Scope and freshness

Catalog records are separate from complete profit inputs. Operation previews initially support learned ordinary item crafts with fixed output and item-only costs. Orders, recrafts, salvage, enchants, currency costs, and incomplete selected allocations do not become priced operations. Mixed-quality selected allocations are retained. Unavailable API results preserve previous valid observations.

Collection pauses in combat or when professions are hidden and excludes linked/guild profession views. Catalog work is canceled on source changes. Event bursts share one delayed capture; catalog batches process ten recipes at a time. Up to 300 distinct operation configurations are retained per character. Recapturing the same recipe/reagents/mode replaces its previous observation. Observation time does not prove current equipment or buffs.

The app automatically prices commodity outputs; other output variants require a manual sale price. Bonus procs/refunds and sale speed remain excluded. Skill-up fields are observations at the recorded rank, not a full 1-100 leveling model.

## Validation

Version 0.1.0 worked for the user's live Phoenix Oil capture. Version 0.2.0 passive hooks and empty-bag previews pass Lua 5.1 mocks but still need live testing: open a profession without materials, browse recipes, reload, and verify catalog and available previews in the app. Repeat with other reagents and a second character.

Run python AddOns/DuckMooCapture/tests/run_tests.py from the project root. Tests use the project-local Lua runtime in CraftingDesk/.test-deps. They do not modify installed addons or live SavedVariables.

Implementation references: Blizzard UI source mirrored at https://github.com/Gethe/wow-ui-source/tree/live/Interface/AddOns/Blizzard_ProfessionsTemplates and API declarations at https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/TradeSkillUIDocumentation.lua .


## Background recipe scanner (0.3.0)

Opening the normal Crafting tab starts a read-only scan for the active profession expansion. It checks learned ordinary item recipes with fixed output and item-only required reagents. It never selects recipes, edits transactions, toggles concentration, crafts, buys, or requires owned materials. A small status line above the profession window reports progress. Switch expansions to cover those recipes too.

For each supported recipe it enumerates up to 64 required-reagent combinations, including integer mixtures within a quality slot. Whole-quality combinations are visited first, followed by mixed allocations. Both concentration modes are queried; zero-cost concentration requests are omitted. Recipes with more combinations are explicitly marked limited. This is bounded comparison, not exhaustive optimization. Optional/finishing reagents, currency costs, orders, recrafts, salvage, enchanting actions and variable output counts remain unsupported. Default recipe levels are queried. Bonus stats are captured but the desktop app does not yet price their expected effects.

One operation query runs per 0.05-second timer step; a profession session is capped at 12,000 operation queries. Closing the window, entering combat, linked views and profession source changes stop pending work. Reopening resumes the session. Equipment/buff, skill, knowledge and learned-recipe changes and successful crafts invalidate the session and queue a fresh scan after two quiet seconds. Frequent buff changes can delay scanning. Completed sessions do not loop; /dmcapscan is an optional explicit fresh scan, not required for normal collection. Reloading starts a new in-memory session. No timer runs while paused.

Completed recipe results are stored compactly in scannedRecipes separately from the existing 300 selected/preview operations. Closing midway retains the current recipe in memory for resume; reload/logout saves completed recipes only. If every outcome query fails, prior successful results remain with their original timestamps. Partial availability is recorded, and unsupported/out-of-expansion entries count as skipped. The scanned catalog total is what GetAllRecipeIDs exposes, so it may include other expansions or unlearned entries. Scan statistics describe the current pass, not the entire retained history.

After /reload or logout, click Import game snapshots. Recipe scan coverage appears above the passive catalog, and scanned outcomes enter the daily shortlist with your existing market filters. Coverage is a snapshot at the last save, not a live connection. Limited recipes are labeled on shortlist entries.

Validation: Lua 5.1 mocks and Python importer tests pass. Live WoW verification is still needed for 0.3.0: let a profession scan, save/import, and compare a familiar recipe's exact reagent quantities, output quality and concentration with CraftSim. Test a second profession and closing/reopening while scanning. No claim of CraftSim-equivalent expected profit is made yet.


0.3.1 rejects transient profession ID zero while the profession UI initializes. This prevents empty phantom scan sessions; 0.3.0 real scan results remain compatible. The updated local app hides previously recorded ID-zero statuses. Live 0.3.0 results now demonstrate multi-profession collection; numerical agreement with CraftSim still needs comparison.


## 0.4.0: broader reagent coverage and leveling observations

The current scanner uses up to 256 allocations per recipe. Small spaces are exhaustive. Larger spaces begin at both quality extremes, devote at most one quarter of the budget to pure-quality corners, and distribute the remaining samples across every required reagent slot. Deterministic samples avoid repeating allocations. This removes the earlier nested-loop bias toward the last slot; it is not a proof of the global optimum and does not use prices to prune mixes. Both modes still receive independent live queries.

The current budget is 24,000 operation queries per profession session, with one query per 0.02-second scheduled step. Timing is a scheduling target, not a live performance guarantee. Large professions can still reach the cap; coverage reports remain explicit. These settings supersede the 0.3.0 values above. Passive safety and pause/resume behavior are unchanged.

Recipe catalog capture now records cooldown status when available and refreshes after skill changes. The app imports the already-captured relative difficulty, disabled state and skill-up count. The leveling guide recommends one supported craft at the observed skill, then recalculates after another save/import. It does not invent future orange/yellow/green transitions or exact skill-up probabilities.


## 0.4.1: faster batches and interruption handling

The scanner now runs up to eight work units per 0.02-second timer callback, yielding after approximately 4 ms when the client's profiling clock is available. A single API call or combination-generation step can exceed that budget; it is a cooperative limit, not a frame-time guarantee. Scan-label updates are limited to five per second and show the current recipe/mix progress.

Aura, equipment and crafting-result events compare a stable operation probe before resetting. Unchanged stats retain the job; actual or unqueryable changes rebuild it. Skill, recipe and specialization events still invalidate scans conservatively. The probe checks one recipe's operation stats, not every possible recipe-specific effect.

Closing the profession window or entering combat pauses the current in-memory job; reopening the normal Crafting tab resumes it. Partial recipe outcomes are checkpointed after batches and on pause and are flagged limited in the app. Reload/logout writes these checkpoints but starts a new scan session next time; it does not persist the timer/job cursor. Already captured outcomes survive. A failed recipe is skipped with lastError recorded instead of leaving the entire scan paused indefinitely. The 24,000-query session cap is unchanged.

Mock tests cover batching, partial checkpoints, close/reopen, unchanged aura events and changed-stat invalidation. Live frame impact and speedup still need in-game validation.


## 0.5.0: recipe sources and skill-range history

Catalog capture attempts GetRecipeSourceText when that function exists and retains returned text with its observation time. Missing/unavailable text is not converted into invented trainer, reputation or specialization requirements. Each recipe now retains difficulty and skill-up observations keyed by base profession rank, with the skill modifier and game build. History clears when the build changes; it is a set of observations, not a complete threshold table. Existing 0.4.1 batching and pause/resume behavior is retained.

The app can use same-build, same-profession and same-modifier orange observations across your characters to bound a planning range. It labels the reference character/rank and stops at unsupported gaps. This is an inference for planning, not proof that every character has identical profession behavior. Unlock costs, yellow/green odds and exact transitions remain unavailable. Installation and live-game field availability still need verification; mocks exercise history/source capture and build changes.
## 0.6.0 — passive acquisition visits
Opening trainers and recipe vendors now records character-specific offers, NPC/map, observation time, gold prices, alternative currency/item costs, stock, and available requirement text. Trainer status is recorded using Retail's second return value. Vendor recipe-class items are kept as items, not guessed crafting recipe IDs. No purchases, training, filter changes, or automatic travel are performed.

Only exposed offers are captured; filters and uncached item data can limit coverage. Events are coalesced and hidden windows are skipped. Keep playing normally, then /reload or log out and import. Older visit records remain historical evidence, not current availability. Up to 2,000 offers are retained per character.

API implementation references: Blizzard's exported [trainer UI](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_TrainerUI/Mainline/Blizzard_TrainerUI.lua) and [merchant UI](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/MerchantFrame.lua). Mock tests pass; live trainer/vendor capture still needs verification in Retail.

## 0.7.0 — profession shopping supplies
Merchant visits now capture recipe items, trade goods and consumables, including price per vendor stack. This lets the profession guide select a recorded cheaper vendor purchase instead of the AH. Offers retain character, NPC, stock and time; extended-currency prices are never treated as plain gold prices. Reload/logout and import after a visit. Automated capture tests cover trade goods as well as recipe items.

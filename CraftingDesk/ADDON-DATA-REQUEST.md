# Data needed for automatic crafting recommendations

This is a development request for the DuckMoo addons, prepared from the current app and inspected local addon sources. It does not change either addon. Confirm the current Retail API signatures and availability in the live client before implementation; the fields below describe the data contract, not guaranteed API return values.

Update: DuckMoo Capture 0.1.0 now implements a separate, explicit capture of ordinary crafting operations and their reagent allocations, querying both concentration modes when available. Crafting Desk imports those snapshots and automatically ranks captured setups. The package is mock-tested and awaits live-client validation. Equipment/buff fingerprints, bulk catalog capture, actual craft-result logging, and leveling thresholds remain future work below.

## First priority: capture the selected crafting operation

The app already has recipe materials and recorded ownership from TSM, concentration pools from Planner, profession progress from Folio, inventory from Syndicator, and TSM price snapshots. The key missing input is what a specific character can produce using specific reagents.

Capture a snapshot while the player has a recipe open and the relevant data is available. Store character GUID, profession expansion skill-line ID, recipe ID, capture time, game build, and a schema version. Identify the operation by all selected reagent slots: item ID, quantity, quality, optional and finishing choices. Include whether concentration was enabled and whether this is an ordinary craft or recraft/order.

Record the output item ID/link, output quality and base quantity, effective recipe skill, recipe difficulty and quality thresholds when exposed, concentration cost when exposed, and operation-specific crafting bonuses. Keep multicraft, resourcefulness, ingenuity and their rating/percentage/effect data separate; preserve units rather than converting fields using guessed formulas. Track unavailable fields explicitly. A profession-wide stat is not a substitute for a recipe-specific operation value.

Capture without and with concentration only when the client exposes both results or the player actually selects those configurations. Do not invent the unobserved result, automatically alter their reagent choices, or automate crafting. Include profession tools/accessories, relevant buffs and specialization snapshot/fingerprint so older results can be identified as potentially outdated. Preserve previous valid observations if the API temporarily returns nothing.

Prefer a small optional capture module in Folio or a shared capture addon; Planner can remain focused on concentration tracking. Give the player a clear capture status, missing-data reason and observation time. Do not continuously scan every recipe on every frame.

## Second priority: full recipe and leveling records

Folio currently records learned recipe counts, not a full per-character recipe catalog. Add recipe IDs, learned/unlearned status, expansion skill line, unlock/training source and cost when available, reagent schematics, output IDs and quantities, minimum skill, cooldown/charges and capture timestamp. Preserve unavailable unlock data as unknown rather than treating a recipe as freely learnable.

For leveling, capture the displayed difficulty/skill-up behavior at the observed profession rank. If the client exposes skill-up thresholds or guaranteed skill gains, preserve them with provenance. A color at one rank is not enough to infer an entire 1–100 route. The optimizer will need validated threshold/probability data, or observations at the relevant ranks, and must report uncovered ranges.

Log actual craft results where feasible: starting/ending profession rank, recipe, reagents consumed, output quantity and quality, concentration before/after, and bonus/refund events. Keep these observations distinct from predictions. This permits calibration without declaring every craft profitable merely because its auction listing price exceeds its material price.

## Snapshot and import behavior

Use a versioned SavedVariables structure. Every record needs its own observedAt timestamp; a file save time does not refresh all records. The desktop app reads the file after WoW writes it to disk, so capture and disk-save status should be explained separately. Keep character GUIDs and numeric IDs authoritative; names are display metadata. Include item names/links for captured reagents and outputs as a fallback to TSM's cache.

Accept an initial implementation that captures one selected recipe reliably. Test two characters with different crafting skill, both concentration modes, mixed reagent qualities, optional reagents, capped concentration, unavailable API data, and a reload/import round trip before expanding to bulk capture.

## Current app bridge

Saved setups let the player enter the observed output and concentration cost, choose the correct concentration pool, and save the exact reagent selection. The app reprices these against imported prices and inventory. This is a temporary manual bridge. Automatic quality simulation, optimal reagent search, and the cheapest feasible leveling route remain pending the above data.

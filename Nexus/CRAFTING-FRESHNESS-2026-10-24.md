# Crafting source freshness — October 24, 2026

The crafting model previously tracked the maximum raw archive ID. Source archival commits before normalization; a model build during that gap could use earlier normalized records, label its checkpoint with the newer archive ID, and fail to refresh when normalization finished under the same ID.

The model now tracks each relevant source's latest usable snapshot and normalization version. Pending normalized sources stay excluded from source labels and refresh checkpoints. TradeSkillMaster ownership remains an explicitly raw-only source: its fully committed archive is usable without a normalization marker. The repeatable-read build observes a consistent set of source records, and an import that completes later changes the next refresh signature. Signature revision is crafting-0.9.3. Existing atomic model writes and the refresh lock remain in place.

A focused PostgreSQL check exercises the actual refresh query against temporary synthetic rows. A pending Capture snapshot stays excluded, then completing it changes the signature even with an unchanged higher raw maximum ID. Temporary rows are rolled back. The rebuilt production image, model refresh and crafting service recreation succeeded. Source/cache backup: `20261024T092952Z-crafting-freshness` in the server's website update backups.

Actual game captures now demonstrate completed Crafting Capture 0.9.0 whole-slot-quality scans, cached scan reuse and unsplit reagent allocations. Actual Omni 0.1.4 concentration discovery reaches both Professions and Crafting Desk with matching observed amounts, currency IDs and timestamps. These observations verify the real capture/import/display path; they do not measure in-game frame time or prove every combat/interruption/context-transition case.

Plan, saved-craft and buying-advisor endpoints remained available after deployment. Source normalization, raw archives and saved crafting documents were not rewritten by the model refresh. More extensive game transition checks and a physical laptop save/refresh remain user-side confirmations rather than unfinished implementation in this fix.

# Midnight leveling benchmarks

Reviewed 2026-10-16 from the user-selected [WoW-Professions hub](https://www.wow-professions.com/midnight). These are brief research notes and implementation requirements, not copied guides or executable routes. Follow the linked guides for their full steps. This pass covers the eight primary crafting professions and Cooking; gathering routes are outside the current crafting optimizer.

Guide advice is external reference evidence, not confirmation of a character's unlocks, skill thresholds, currency balances, or current prices. Recheck it when encoding a route and retain the source URL and review date. No guide route is priced or integrated into the solver yet.

## Guide-specific comparison cases

| Profession / source | Baseline characteristics to preserve | Planner work needed for a fair comparison |
| --- | --- | --- |
| [Alchemy](https://www.wow-professions.com/guides/wow-alchemy-leveling-guide) | Early potion recycling, cauldron research, and first crafts; later potion/flask/transmute alternatives depend on unlocks and market conditions. Some quantities are approximate. | Model consumed crafted outputs, research prerequisites and currency, random skill-ups, and separate late-stage branches. |
| [Blacksmithing](https://www.wow-professions.com/guides/wow-blacksmithing-leveling-guide) | Early trainer first crafts; intermediate alloy production; later specialization equipment or orders. Ingot purchase versus production is an explicit choice. | Compare buying intermediates with crafting them; retain first-craft rewards and distinguish time-gated materials from repeatable crafts. |
| [Enchanting](https://www.wow-professions.com/guides/wow-enchanting-leveling-guide) | Disenchanting can contribute early progress and materials. Later options depend on learned recipes and sale prospects. | Support enchants and disenchanting separately from ordinary item recipes; keep uncertain recovered materials and sales separate from guaranteed cost. |
| [Engineering](https://www.wow-professions.com/guides/wow-engineering-leveling-guide) | Recycling specialization and random discovery are central. Discovered gear supports intermediate progress; decor or orders extend the route. | Treat discovery and specialization as prerequisites, not guaranteed recipes or fixed-cost actions. Respect an existing character build. |
| [Inscription](https://www.wow-professions.com/guides/wow-inscription-leveling-guide) | Milling feeds ink production, with ink saved for later crafts. First crafts and a Calm Hands treatise unlock shape the early route. | Track intermediate inventory and Knowledge allocation; do not count raw herbs and purchased inks as simultaneous full costs. |
| [Jewelcrafting](https://www.wow-professions.com/guides/wow-jewelcrafting-leveling-guide) | Prospecting and trainer first crafts lead into a cheap intermediate recipe. Later choices include purchased recipes, equipment, and orders. | Separate prospecting yield uncertainty from purchases; include recipe acquisition costs and allow a deliberate pause before 100. |
| [Leatherworking](https://www.wow-professions.com/guides/wow-leatherworking-leveling-guide) | Trainer first crafts establish the early path. Later options span quest, drop, vendor and specialization unlocks; patron orders provide a slower alternative. | Preserve acquisition requirements and first-craft benefits; compare feasible unlock branches rather than assuming every recipe is available. |
| [Tailoring](https://www.wow-professions.com/guides/wow-tailoring-leveling-guide) | Bolts feed subsequent crafts. First crafts can be worthwhile even when grey. Later routes distinguish cooldown/order progress from faster purchased-recipe options. | Carry crafted bolts forward, track first-craft rewards independently of skill, and compare time and gold as separate objectives. |
| [Cooking](https://www.wow-professions.com/guides/wow-cooking-leveling-guide) | Vendor supplies and conversion of cooked food into Hearty Food drive much of the path. Output servings change with skill. | Capture vendor reagent prices, support output-to-input conversions, and distinguish craft actions from servings. Validate quantities against game schematics. |

## Benchmark contract for implementation

These are project decisions informed by the review, not claims made by the guides.

1. Compare the same starting character, base skill, target skill, recipe access and specialization constraints. A one-step estimate cannot beat a complete 1–100 guide by comparison alone.
2. Offer two explicit objectives: lowest material value for the chosen skill target, and profession setup that preserves selected first-craft Knowledge benefits. Do not silently sacrifice the latter for a cheaper number.
3. Price both paths from the same local import and market scope. Report full material value and additional gold needed separately; owned materials are not free economically.
4. Include training, purchased recipe costs, vendor supplies, and intermediate crafting. Charge each unlock once. Allocate starting stock once and carry intermediate outputs forward without double counting.
5. Display currencies and Knowledge commitments in their own units. Do not invent a gold conversion for Moxie, reputation, or specialization points.
6. Label guide batch counts as estimates when they depend on yellow/green skill-ups. Keep observed game difficulty separate from guide-described ranges. A reliable cost range requires a supported probability model or actual progress observations.
7. Keep fast completion and gradual cooldown/patron-order progress as separate comparisons. Random order availability cannot be guaranteed on a timetable.
8. Show first-craft benefits, unresolved unlocks, time gates and leftover outputs alongside the gold difference. Sales value is an estimate, not guaranteed reimbursement.
9. Only display a percentage saving when both routes cover the same target and all required costs are priced. Otherwise show a partial comparison and name the missing components.

## Next implementation priorities

- Capture/import first-craft status and make it an explicit planning objective.
- Extend passive merchant capture beyond recipe items to needed vendor reagents; avoid substituting AH prices for known cheaper vendor purchases.
- Extend routes to include training steps and intermediate production while retaining character-specific unlock checks.
- Encode a small, traceable guide baseline and reprice it alongside the personal route. Start with a supported deterministic segment; expand to recycling, milling, prospecting, and chance-based progress as those models become available.
- Keep recipe-source references linked to the guide; no automatic specialization spending or inferred learning.

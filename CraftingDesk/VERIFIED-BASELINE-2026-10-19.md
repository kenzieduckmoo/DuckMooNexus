# Build plan and verified state

Updated October 19, 2026.

## Implemented

- **All nine profession guides:** one ordered route with combined purchases, owned stock deducted once, exact-quality Auctionator import, separate vendor quantities, unlock notes, skill overrides and saved place markers. Tailoring combines its remaining 1–100 purchases; other professions combine purchases through the next conversion or unlock checkpoint. Fixed-count batches are estimates, not guaranteed skill gains.
- **Current-price alternatives:** fresh, learned recipes can join repeat-stage comparisons when their current skill-up color, points, grey cutoff, build and skill modifier match a baseline recipe. Unknown unlock/vendor prices cannot establish cheapest cost. The comparison includes known recipe gold. Mid-stage repeat quantities scale down from the guide estimate. Manual choices remain available by stage.
- **Learned finishing recipes:** Engineering 80–100 and Leatherworking 91–100 use a priced, fresh, available learned recipe when captured. Prefer orange, then cost per potential point; use small batches and reimport after crafting. Missing evidence leaves a concrete unlock/capture checkpoint instead of invented order availability.
- **Recipe investments:** strict >20% margin after a 5% fee and >0.1 sale rate; selected learner's realm for AH recipe prices; exclude recipes already learned by that character. Payback is individual output items sold, conditional on the named reference crafter's results. Complete current vendor offers retain currencies separately; no invented unlearned-character crafting performance.
- **Concentration ready:** third top-level tab; capped Midnight professions, observed/projected distinction, remaining pool after reservations, best repeated-single-recipe batch by total profit, alternatives, material purchases, owned-stock-only option and add-to-plan action. Cooldown charges and existing same-recipe reservations are respected. No random refunds or multicraft assumed. Mixed-recipe optimization is separate in Crafting & profit.
- **Capture import:** the addon already saves `firstCraft`; the importer now preserves it for trainer-step annotations. No addon update required for this field.
- **Local previews:** write endpoints accept only the running port's loopback origins, so preview-port plan saving works without allowing arbitrary origins.

## Evidence

- User's concentration example passes: 5 x 250g at 200 concentration beats 1 x 1,000g at 600 concentration with a 1,000-point budget.
- Browser add/undo check saved Kaissiriah's three-craft batch, reserved 999 concentration, and restored the original empty plan afterwards. Subsequent user changes are not overwritten.
- Live catalog examples: Darayeda selects learned Snakeskin Lining; Pandaquack can select Devouring Banding; Zaraevelina can use a cheaper Quel'dorei variant. Prices and selections can change after import.
- Eight generic profession catalogs checked at skill 1, the baseline late stage and 100. Tailoring accounting/quality tests retained. Regression tests cover substitutions, stale/incompatible evidence, cooldowns, shared stock, conversion targets, recipe investment thresholds and local-origin enforcement.

## Limits requiring in-game evidence, not placeholder controls

- Milling, prospecting, disenchanting and recycling produce variable results. Their targets are not fully represented by ordinary reagent slots. Follow the explicit target instructions and import after the checkpoint; later purchases use actual resulting stock.
- Hearty Food consumes food targets. Cooking shows vendor batches and the conversion loop, not a fabricated exact 1–100 quantity.
- Unavailable discoveries and customer/patron orders cannot be treated as acquired recipes or free reagents. Open learned recipes and import to replace those checkpoints with priced finishing batches.
- Vendor prices and access are character-specific snapshots. Visit the vendor, save in WoW and import when a price is missing.
- Matched recipe colors/points/cutoffs support a comparison, not proof that future skill-up odds are identical. Sparse skill history cannot prove a globally cheapest path through every possible recipe. No guessed yellow/green probabilities are used.
- Recipe investments cannot predict the resulting quality/stat performance of an unlearned character. Capture that character's actual craft after learning before treating the reference profit as their own.

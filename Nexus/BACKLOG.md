# Nexus backlog

## Reagent buying recommendations

Status: implemented October 24, 2026 at `/auctions/buying` for repeatedly purchased US commodity trade goods. Weekday advice is gated on sufficient retained history. Additional market types or measured consumption can be expanded later.

- Identify reagents frequently purchased from the auction house using recorded purchases, quantities and purchase frequency.
- Compare retained auction-price history by weekday to find when each reagent has typically been cheapest. Respect the item's market scope and available quality distinctions.
- Suggest an item, buying day and quantity based on usual consumption/purchases and known current stock. Avoid counting transfers as consumption or assuming missing inventory is zero.
- Show the suggestion on a suitable Nexus page, likely Crafting Desk or Auction House; final placement remains open.
- Include recent price context, sample coverage and confidence. With insufficient history, show that there is not enough evidence for a weekday recommendation.
- Seasonal/patch changes and unusual prices should not become confident recurring recommendations. Suggestions only; no automated buying.

## Pre-Forever addon documentation and release handoff

Status: prepared and uploaded October 24, 2026 for the current pre-Forever checkpoint. See `PRE-FOREVER-STATUS-2026-10-24.md`. Client checks and Forever access remain explicit external gates; the packages preserve current preview functionality.

- Inventory all DuckMoo-owned addons and their individual GitHub repositories. Start with DuckMooCapture, DuckMooFolio, DuckMooPlanner, DuckMooWarband and DuckMooOmniCapture; reconcile any other owned addons before calling the inventory complete. Exclude third-party addons.
- Write a comprehensive plain-text user guide inside each addon's folder (for example, USER-GUIDE.txt). Explain purpose, installation/update steps, supported clients, dependencies and optional integrations, commands/settings, normal workflows, what triggers capture, exactly what data is collected, SavedVariables names and locations, account/character scope, retention, Nexus sync behavior where applicable, troubleshooting, limitations and known unfinished features. Derive claims from the current implementation and distinguish observed client behavior from unverified paths.
- Include exactly `## Category: DuckMoo Media` in every owned addon TOC variant. Preserve valid client/interface metadata and each collector's independent lifecycle.
- Package each addon separately as it exists at that milestone, with a correctly named top-level addon folder, the TXT guide, required runtime files and applicable licenses. Exclude credentials, personal SavedVariables, generated personal acknowledgement receipts, caches, tests and development-only files. Preserve an empty runtime acknowledgement stub where required.
- Produce individual versioned ZIP files ready for the user to upload to CurseForge. Do not claim unfinished functionality is complete or preview compatibility is live-verified. Uploading the packages to CurseForge itself is not requested by this milestone.
- Update each addon's own GitHub repository with the current source, new TXT guide and TOC category change; the Nexus aggregate repository alone does not satisfy this requirement. Preserve unrelated remote changes and existing repository visibility. Verify repository identities rather than guessing or creating duplicate repositories.
- Deliver the ZIP links, repository links and version/status of each addon. Use focused packaging/version checks and record any actual blocker without an excessive test campaign.

## Profession guides

Resumed and delivered October 24: native route choices/progress saved on Nexus, next-batch shopping, stable checkmarks, vendor exclusions and observed recipe alternatives. See PROFESSION-GUIDES-2026-10-24.md. Unknown acquisition prices, random yields and additional expansion/client evidence remain explicit data gates; no claim of globally optimal routing.

## Forever and expanded Omni preparation

Delivered October 24: client-specific Omni TOC/install, independent first-save-gated Forever sync/receipts/namespace, separate character sheets, Adventure Journal with archived-history paging, explicit life-mode/death summaries, partial visited storage, collection and active-quest capture. See FOREVER-READY-2026-10-24.md. Remaining evidence gates are actual updated-client observations, Forever access and actual Hardcore rules/events. Exhaustive appearances/achievement criteria, hidden/unaccepted weekly tasks and verified killer attribution are not represented as captured.

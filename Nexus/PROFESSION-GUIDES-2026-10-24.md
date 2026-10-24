# Native Nexus profession guides — October 24, 2026

The user resumed this work after the native website migration, whole-quality crafting scans and official auction imports. The older optimization pause is superseded for this implementation.

## Using the guides

Open http://10.20.30.239/crafting?tab=guides and choose a character and primary profession. Blank starting skill uses the latest imported profession rank. An entered skill is a preview; it never changes game data. All eight primary crafting professions have routes. Secondary professions remain outside this scope.

Recipe alternatives show recorded material/unlock costs where available. Choose the recipe that fits your unlocks and materials. Choices and checkmarks are saved per character/profession in PostgreSQL and follow you across computers. The existing Undo action can reverse a recent change while preserving newer changes from another page. Older browser checkmarks can be copied into the current route without deleting browser data.

The next-batch panel buys for at most ten ordinary crafts. Conversion and discovery checkpoints can instead specify the inputs for that operation. Owned stock reduces purchases. Copy its Auctionator import for the missing auction materials, then craft in game. Vendor supplies are separate and are excluded from the auction import even when their vendor price has not been observed. Enchant operations include vellum.

After crafting or recycling, save the game data through the normal reload/logout workflow. Nexus automatically imports the changed observations and refreshes the route. Checkmarks record your actions; they do not consume stock, increment skill, or establish skill 100. Stable step identifiers preserve progress when earlier stages disappear after a skill update.

Expand full-route shopping for the shopping plan through the next evidence checkpoint, recipe acquisition items, trainer reference and unlock details. Recipe investment estimates remain available when the captured outcomes and market observations qualify; those are estimates from the reference crafter, not guaranteed sales or identical results for your selected character.

## Data and limits

Recipe schematics, ownership, current skill, skill-up metadata and observed vendor offers come from the saved character/crafting observations. Omni supplies independently captured profession resources. Auction quotes come from Nexus's normalized market model, including official API imports and applicable saved market observations. The guide uses the same PostgreSQL-backed pipeline as the rest of the native Crafting Desk; it does not read a desktop file directly.

The route sequence is a baseline informed by captured recipes and selected alternatives. It is not a proof of a globally cheapest path. Fully priced compatible learned alternatives and bounded finishing batches are supported where their current-rank evidence qualifies. Missing schematics, unavailable unlocks, random recycling/prospecting/milling yields, customer orders and uncertain yellow/green skill gains remain checkpoints or explicit limitations. A missing price is not treated as zero. Full-route totals can remain unavailable while an individual next batch is usable.

The current guide workflow required no additional addon fields: the collectors already retain the necessary recipe and resource observations. A website/API cannot replace a character observation that has not been saved yet. Additional expansion-specific data collection can be added when an actual gap is identified.

## Storage and deployment

Migration `020_guide_progress.sql` permits a separate `guides` document; existing plans and saved craft setups are preserved. Profile keys combine character GUID and primary profession. Documents have input validation, write history, optimistic revision checks and conflict-aware Undo. The site detects document changes through its existing automatic freshness polling.

Implementation: CraftingDesk/guide-workspace.js, guide_workspace.py, profession-route.js, hosted_server.py and nexus_storage.py; Nexus/craft-engine/worker.cjs and server.cjs; Nexus/web/components/crafting-desk.tsx. The deployment helper backs up source before replacing it and applies the migration in a transaction.

## Verification

Focused workflow checks covered bounded batches, validated selections, preservation of other character profiles, stable step IDs, checkmarks, vellum, vendor exclusions and completed primary routes. Existing profession-route checks and TypeScript validation passed. The production web build succeeded.

Live checks exercised all eight primary professions at completed skill and active/preview stages. Browser verification saved a checkmark, observed it from an independently opened page, and restored it with Undo. Recipe choice persistence and restoration were also checked through the live endpoint. Existing plan and saved-craft endpoints remained available. These checks do not claim an actual laptop round-trip or additional live game crafting occurred during deployment.

Source backup: `/opt/duckmoo-nexus-clean/web-update-backups/20261024T100120Z-profession-guides`. Build log: `/home/kenzieduckmoo/profession-guides-deploy.log`.

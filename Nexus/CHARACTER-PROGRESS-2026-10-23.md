# Character progress workspace — October 23, 2026

## Delivered live

The existing character sheet at `/characters/[guid]` now has dedicated Progress categories:

- Weekly adventures: Great Vault slot progress, recorded reward item levels and availability, owned keystone, total played time, and expandable lockout/boss records.
- Currencies: source selector, balances, maximum/weekly counters where known, zero-balance toggle, ID search and currency reference links. Existing files omit currency names and icons; these are explicitly unavailable rather than guessed.
- Dungeons and raids: searchable API lifetime encounter history, expansion filter, separate difficulties, boss kills and last kill dates. These are not treated as current-week lockouts.
- Completed quests: name/ID search, completion list and quest reference links. The API list does not supply completion timestamps.
- PvP: API honor and battleground records, plus separately dated addon rated-bracket samples.
- Reputations: searchable faction progress retained from the prior page.

Professions also has dedicated knowledge cards with spent/unspent points and specialization branch rank bars, Midnight first. Older source details remain available.

Source adapters use structured WarbandNexus data and the installed WoWthing Collector format. WoWthing currency field order was checked in `Modules/Currencies.lua`; lockout fields and boss encoding were checked in actual retained data and installed addon source. Unsupported formats are excluded rather than interpreted speculatively.

Weekly data defaults to the newest explicitly dated vault sample. Selecting an older source displays that source's own values and reset date. Weeks whose recorded reset passed are clearly historical. False `locked` flags and missing reset times do not become active lockout claims. Source identity, dates and unknown values remain visible.

## Verification and deployment

TypeScript and the server production build passed. A focused adapter check against a retained Nightchicken sample verifies source ordering, two unlocked world-vault choices, currency total-earned cap fields, unknown coverage and source separation. Browser checks verified the deployed vault, older-reset notice, quest-name search, encounter-name search, zero-balance currency cap and profession knowledge panels.

Nightchicken example: newer WoWthing snapshot has two world-activity choices at item level 305 and an owned +10 key. The older WarbandNexus sample is not used as this week's current progress. Four stored boss records explicitly have `locked=false` and remain labeled accordingly.

Only the website was rebuilt/restarted. No database migration, data reimport, credential change or game-addon installation was performed.

- Source: `Nexus/web/lib/character-progress.ts`, `Nexus/web/components/character-progress.tsx`, `Nexus/web/app/progress.css`, plus character-sheet/layout integration.
- Deployment bundle: `Nexus/nexus-character-progress.tar.gz`.
- Deployment helper: `Nexus/deploy-character-progress.py`.
- Live backup: `/opt/duckmoo-nexus-clean/web-update-backups/20261023T175434Z-character-progress`.
- Live deployment log: `/home/kenzieduckmoo/character-progress-deploy.log`.
- Browser evidence: `Nexus/web-verification/character-weekly-progress.png`.
- Adapter verification: `Nexus/progress-verification/check.cjs` and reduced source fixture. Compiled JS there is verification output; TypeScript under web/lib is the maintained source.

## Next meaningful work

Build the separate Retail omni-capture collector and its Nexus ingestion adapter, including named currencies, quest/loot/session observations and independent capture settings. Keep it separate from DuckMooCapture, use its own SavedVariables and include `## Category: DuckMoo Media` in every DuckMoo TOC. Existing retained archives remain preserved.

Forever in-game integration waits until November 4. Hardcore life-history capture must be ready before the expected January/February start; that exact date remains unannounced. Profession-guide optimization remains paused. Older Folio archive backfill and actual game/laptop verification remain separate pending work.

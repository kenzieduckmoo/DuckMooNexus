# Independent Omni Capture — October 23, 2026

## User direction

Collect useful character progress directly instead of requiring WarbandNexus or WoWthing Collector. Keep this separate from DuckMooCapture. Every DuckMoo TOC uses `## Category: DuckMoo Media`.

## Implemented

`AddOns/DuckMooOmniCapture`, version 0.1.0 Retail preview, own SavedVariables/settings and no addon dependencies. Installed in `D:/World of Warcraft/_retail_/Interface/AddOns/DuckMooOmniCapture`. Installable preview ZIP is at `releases/DuckMooOmniCapture-0.1.0-preview.zip`.

Collects character identity/client provenance/basic status, named currencies and icon IDs/caps/account flags, vault tracks/rewards/reset, lockouts/bosses, owned keystone, equipment, completed quest IDs, naturally opened profession knowledge, and lightweight session/quest/loot/level/death/achievement/encounter events. It coalesces refreshes and only rescans affected sections after normal events. It waits out combat. It requests readable cached data but does not open game windows or automate gameplay.

Sections retain coverage, observation and attempted-read timestamps. Failed reads keep the previous observation. Currency coverage is partial for hidden/undiscovered rows. Knowledge retains individual profession observation times. Secret values are omitted.

The initial event journal retains 10,000 events per character and explicitly pauses/counts overflow afterward. It needs an acknowledged rotation/export workflow before it can be called a complete long-term life recorder. Bags/bank, deeper collections/reputations/activities, fuller gameplay timelines and currency icon image resolution remain future work. Do not describe this preview as complete omni-capture or live-game validated.

## Nexus integration

- Added the source to both development and installed Windows collector allowlists. Installed sync source: `C:/Users/Kenzie DuckMoo/AppData/Local/DuckMooNexusClean/app/snapshots.py`. Pre-change backup is `Nexus/snapshots-before-omni.py`.
- Complete raw archives are retained first; `omni_adapter.py` normalizes identity, per-section observations and events into existing `character_records`/`snapshot_characters`.
- Migration 015 adds `current_omni_records`, selecting the latest successfully normalized source snapshot per namespace. Website role has SELECT on that view; it remains read-only.
- Website roster/sheets can use Omni identity/profile data. Known newer fields compete by observation time. Folio notes/tags remain intact.
- New Omni-only identities can enter the public-profile API queue without a Folio record.
- Financial views remain sourced separately. Omni wallet observations are not double-counted as income.
- Progress uses Omni weekly/currency/knowledge data alongside earlier collectors. Currency search accepts captured names/IDs. History adds Omni profile observations and captured adventure events.

Source package `Nexus/nexus-omni-capture.tar.gz`, deployment helper `Nexus/deploy-omni-capture.py`, live log `/home/kenzieduckmoo/omni-capture-deploy.log`. Timestamped backups under `/opt/duckmoo-nexus-clean/web-update-backups/` end in `-omni-capture`.

## Verification boundary

Focused Lua 5.1 mock checks passed for named currencies, vault capture, retaining last-known values on unavailable API reads, settings and coalesced section refresh. TypeScript/server production builds passed. Server normalization against a synthetic fixture produced 10 records, a retry inserted zero, and named currency/event payloads remained intact. That entire synthetic database transaction was rolled back; no synthetic snapshots were retained or presented as real character observations.

Actual game API behavior has not been verified. On next Retail login: ensure DuckMoo Omni Capture is enabled, allow the initial capture, open a profession normally if knowledge is wanted, and reload or log out. WoW only writes SavedVariables to disk on reload/logout; the existing sync then uploads it and the website notices the new source revision. Verify real named currencies, vault and timestamps after that first upload.

Forever client integration still waits until November 4. This preview was installed only in Retail.

API design references: Blizzard-generated CurrencyInfoDocumentation.lua and WeeklyRewardsDocumentation.lua in the live WoW UI source mirror, plus the currently installed collectors as source-format evidence. Those references are not proof of behavior in the user's live client.

Final deployment backup: `/opt/duckmoo-nexus-clean/web-update-backups/20261023T182357Z-omni-capture`. The new API identity queue SQL resolves successfully against the live database. At completion, real Omni observations received: 0; the character History panel explicitly waits for the first game save/upload. Browser evidence: `Nexus/web-verification/omni-capture-awaiting-first-login.png`.

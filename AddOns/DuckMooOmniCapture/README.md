# DuckMoo Omni Capture 0.2.0

Current behavior is documented in USER-GUIDE.txt. Includes life summaries and a prepared Forever/Camelot interface-16001 TOC. Actual Forever login and Hardcore verification remain pending game access.

Earlier notes below are historical and superseded where the current guide differs.

Current release documentation: see **USER-GUIDE.txt** for installation, commands, captured data, storage, Nexus integration and current verification limits. Earlier version notes below are historical.

# DuckMoo Omni Capture 0.1.1 â€” Retail preview

Independent from DuckMooCapture, DuckMooFolio, WarbandNexus and WoWthing Collector. No addon dependency. Uses its own `DuckMooOmniCaptureDB`, settings and capture lifecycle. Category: DuckMoo Media.

## First capture

Installed under Retail Interface/AddOns/DuckMooOmniCapture. Enable it in the AddOns screen and log in. A full capture runs after login/entering-world; later events refresh only affected sections in three-second batches. Data reads wait until combat ends. Opening a profession naturally captures the available knowledge data. No profession/bank/vault window is automatically opened and no gameplay is automated.

WoW writes SavedVariables on reload/logout. Nexus's existing sync task then uploads the saved file to PostgreSQL. The website notices incoming source revisions automatically. An on-screen capture does not mean the disk file has been saved yet.

Commands: `/dmomni`, `/dmomni capture`, `/dmomni on`, `/dmomni off`, `/dmomni events on`, `/dmomni events off`.

## Initial coverage

- Character identity and client/build/project/locale, level/XP/rested XP, observed gold, equipment ilvl, specialization, guild, location/hearthstone and health maximum.
- Named currencies: quantity, icon file ID, caps, weekly/total-earned counters, account-wide/transfer flags where the client returns them. It reads visible rows, previously observed IDs and currency events without changing your currency list. Collapsed/undiscovered rows may be absent, so coverage is explicitly partial.
- Great Vault: activity tracks, thresholds/progress, available reward state, reset timestamp, and example reward item level when item data is available. Empty/not-ready APIs do not erase prior observations.
- Saved instances: names, difficulty, reset timestamp, locked/extended flags and individual boss observations.
- Carried bags and equipped reagent bag: named items, slots/counts, binding, quality and cache-available texture/link metadata. Empty captures replace old contents; unavailable reads retain prior observations. Banks are not scanned through guessed container IDs.
- Visible/previously observed reputations: names, standing, account-wide labels and renown level/progress where available. Hidden rows remain partial coverage.
- Owned keystone level/map/name; equipment IDs, links and texture IDs; completed quest IDs.
- Profession knowledge: naturally opened profession's specialization tabs, currency pool and available node ranks; retained independently by skill line.
- Timestamped events: sessions, levels, quest turn-ins, own loot chat, deaths, achievements and encounter endings.

These are observations, not exhaustive coverage. API restrictions, hidden data and caches can leave fields unavailable. Secret values are omitted. Each section has its own observation/attempt time and coverage status; failed reads retain earlier data. Event journal preserves its first 10,000 entries per character, then explicitly pauses new event recording and counts overflow; it does not silently discard older events. A Nexus-acknowledged rotation workflow is still needed before calling the event journal a complete long-term life recorder. Snapshots continue at that limit. No player-to-player chat or combat-log stream is collected.

## Integration and limits

Server source adapter archives the complete saved file first, then normalizes identity, sections and journal into PostgreSQL. Website progress/history consumes that source alongside older collectors. New Omni identities can create character pages and join the public-profile enrichment queue.

Currency icon IDs are preserved; resolving every icon into a website image is a separate enrichment step. Other future coverage includes bank storage, deeper collections/weekly activities, richer session/dungeon details and reliable journal rotation. Existing collectors remain useful sources for those areas.

Retail only in this preview. Forever compatibility and its in-game verification wait until November 4. This release has Lua 5.1 mock and server adapter checks; actual in-game capture/reload/upload behavior has not yet been verified.

### 0.1.2 logout correction
Real October 23 captures showed that PLAYER_LOGOUT APIs can return zero wallet/item level and empty equipment/quests. Logout now journals the end time with the last cached profile and its own observation timestamp, and stops scans during shutdown/loading. Successful scans no longer receive an erroneous API-failure detail. Nexus normalization recovers affected legacy profiles from earlier retained session events, retaining their original observation time and labeling the recovery. Raw files and events are preserved. Empty legacy logout equipment/quests are unknown rather than proof of owning/completing nothing. The correction was subsequently observed in real 0.1.2 client saves.

### 0.1.3 acknowledged event rotation

The independent Windows sync writes `Acknowledgements.lua` in the installed addon only after Nexus confirms the exact archived source packet. At the next addon load, a matching journal identity and event ID/time permit removal of just that confirmed prefix from the in-memory queue. Event IDs keep increasing; newer events stay queued. A missing, old or mismatched receipt retains the queue. No tool edits SavedVariables, and local/server raw archives and PostgreSQL event history remain retained.

Fully close and reopen the client once to load the added receipt file. The first load of this version assigns journal identities. Save normally, allow sync, then the following load can rotate confirmed events. `/dmomni` reports queued, archived and overflow totals. The 10,000-event limit still protects an unacknowledged queue; recording pauses/counts overflow until space is available. Rotation is not a claim of complete gameplay coverage or proof that no events were missed before installation. The source/release acknowledgement file is empty; generated installed receipts are private runtime data and must not be copied into source control.

### 0.1.4 profession concentration resources

A naturally opened specialization-capable profession records its concentration currency ID, amount, cap, rate when available, and its own observation time. Known pools are subsequently refreshed with normal currency reads, including after the profession closes; this does not rescan trait trees or change the older knowledge observation time. Unknown or unavailable reads preserve the earlier pool and its timestamp. Nexus's profession board and Crafting Desk can use the newer valid observation. This is resource data, not recipe ownership or a crafting outcome. The new capture path was subsequently observed in actual client saves, with matching concentration observations in Nexus Professions and Crafting Desk. Existing acknowledgement files and SavedVariables remain intact.

# DuckMoo Omni Capture 0.1.0 — Retail preview

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
- Owned keystone level/map/name; equipment IDs, links and texture IDs; completed quest IDs.
- Profession knowledge: naturally opened profession's specialization tabs, currency pool and available node ranks; retained independently by skill line.
- Timestamped events: sessions, levels, quest turn-ins, own loot chat, deaths, achievements and encounter endings.

These are observations, not exhaustive coverage. API restrictions, hidden data and caches can leave fields unavailable. Secret values are omitted. Each section has its own observation/attempt time and coverage status; failed reads retain earlier data. Event journal preserves its first 10,000 entries per character, then explicitly pauses new event recording and counts overflow; it does not silently discard older events. A Nexus-acknowledged rotation workflow is still needed before calling the event journal a complete long-term life recorder. Snapshots continue at that limit. No player-to-player chat or combat-log stream is collected.

## Integration and limits

Server source adapter archives the complete saved file first, then normalizes identity, sections and journal into PostgreSQL. Website progress/history consumes that source alongside older collectors. New Omni identities can create character pages and join the public-profile enrichment queue.

Currency icon IDs are preserved; resolving every icon into a website image is a separate enrichment step. Other future coverage includes bags/bank, deeper reputations/collections/weekly activities, richer session/dungeon details and reliable journal rotation. Existing collectors remain useful sources for those areas.

Retail only in this preview. Forever compatibility and its in-game verification wait until November 4. This release has Lua 5.1 mock and server adapter checks; actual in-game capture/reload/upload behavior has not yet been verified.

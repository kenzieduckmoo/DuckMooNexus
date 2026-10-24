Current release documentation: see **USER-GUIDE.txt** for installation, commands, captured data, storage, Nexus integration and current verification limits. Earlier version notes below are historical.

# DuckMoo Services: Warband Planner

**0.4.0 preview — by DuckMoo Media**

A separate general-activity planner. Leave a small next step, see remaining tasks across your recorded characters, and return to them when you are ready. No dependency on Folio, Concentration Planner or Fia's addon.

## Open and capture

Extract the `DuckMooWarband` folder into WoW Retail's `Interface/AddOns` folder while the game is closed. Enable it and use `/warplan` or `/dmwarband`.

Type a task in the entry box and press Enter. It defaults to the logged-in character, separate progress, and a one-time task that stays visible until handled. `/warplan Your task here` also captures a task. Organization can wait.

## Task details

Use **Details** for a new task, or a task's **… → Edit task** action to change one.

- **Applies to:** selected characters, all recorded characters, a recorded class, or a custom group. Class/group membership is evaluated whenever the list is refreshed.
- **Progress:** separately for every eligible character, or once for the account. Shared tasks appear once. Character progress survives changes in eligibility.
- **Appears:** one time, daily game reset, weekly game reset, a chosen weekday, or an interval of 1–365 local calendar days after completion. A weekday task appears only on that weekday. An unfinished one-time task remains available on later days.
- **Category:** an optional label. Optional category weekdays control Today visibility without changing progress.

Choose **Characters** to assign comma-separated group names to a recorded character, including offline characters. Groups are case-insensitive. This addon records characters when you log into them and imports identity snapshots through the optional roster-export APIs in Folio 0.4.1 / Planner 0.4.2. Imports preserve the original observation time and your own groups; they never write into either source addon. It does not automatically discover unrecorded account characters. Class choices come from recorded characters. Missing details are not inferred.

Armor rules use the primary class categories in [Blizzard's class-set guide](https://news.blizzard.com/en-us/article/24244458/gear-up-with-new-pve-and-pvp-class-sets-in-midnight). Covenant rules match the recorded active covenant. The covenant API is read on login and when the active covenant changes; unavailable reads preserve the prior snapshot, while a reported zero records no active covenant. Characters without a covenant observation remain unknown and do not match a covenant rule.

**Categories** lets you choose multiple weekdays for a category. This only changes Today visibility; it never completes or skips the underlying tasks. **Every day** removes the restriction. All tasks still shows hidden definitions. Task weekday rules and category weekday rules combine.

**Starter tasks** in full view offers optional daily/weekly manual reminders for the current character. The weekly set includes a dungeon run, a delve and a Great Vault check, consistent with [Blizzard's weekly Vault guidance](https://worldofwarcraft.blizzard.com/en-us/news/24272606/wow-semanal-atualiza%C3%A7%C3%A3o-de-conte%C3%BAdo-1205-raides-de-midnight-e-modo-hist%C3%B3ria-e-mais). Packs do not detect completion, impose activity requirements or encode seasonal quest IDs. Re-adding a pack does not duplicate that character's previously added reminders, including archived ones. Edit their scope/category/cadence afterward.

Changing cadence starts a new occurrence and clears old interval/postponement timing; historical actions remain recorded. Changing assignment or progress scope preserves existing progress records.

## Today and compact view

Today includes remaining tasks across eligible recorded characters, regardless of which character is logged in. `*` marks the current character. By character / By activity changes the sorting; it does not change task eligibility or progress. Full view has sidebar pages for Today, All tasks, Characters, Categories, Session, Gold, Loot, Session history and Preferences. Search filters the current page. Today summary cards count remaining occurrences, character owners and shared tasks before search. Up to twelve rows per page keep the window bounded; smaller windows show fewer rows.

Compact mode uses single-line rows and initially fits their contents. Hover a row for the full task and scope. Full view adds a second line for character, recurrence and category. Drag the window to move it or use the bottom-right grip to resize it. Full and compact size/position are saved separately. Full view starts at 1040 × 740 with a 940 × 560 minimum, scaled down when the screen needs it. All main windows and dialogs use grouped stacking so their components stay together when windows overlap. Preferences offers the approved Folio palettes, including warm Light Mode and Trans Pride Dusk. The Characters and Categories pages open the existing group and weekday editors.

**Done** records manual completion. **Worked on it** records attention without finishing the task. **Postpone** hides it until tomorrow's local midnight, then its normal visibility rules apply. **Skip** hides the current occurrence; for intervals it starts the next interval. One-time tasks have one occurrence. **Undo** reverses the most recent action in the current login session, including completion and postponement. It does not undo editing, group changes or archiving.

**All tasks** lists task definitions, including completed, postponed and archived ones. Edit there, or archive/restore through the task controls. Archiving preserves progress and history. There is no destructive delete control.

Reset-based tasks use the game's regional reset APIs. When reset data is unavailable they remain visible with `?` and cannot record progress; the addon does not guess a reset time. Offline character information is a snapshot. Nothing in this version automatically detects activity completion or performs gameplay.

## Gold, loot and sessions

Recording starts automatically on entering the world while the addon is enabled. Every login or UI reload begins a new session; zone transitions keep the existing one. Logging out closes it. An interrupted client session stops at its last observation instead of counting offline time. **New session** closes the current session and starts another without discarding history. You can give live or saved sessions a short name, such as “Old recipes and a dungeon.”

- **Session:** recent activity, wallet and warbank changes, item quantity and a separate vendor estimate. The combined cash-change card adds observed wallet and warbank changes, so moving money between them cancels once both balance updates arrive. It is an observed balance change, not profit or a source-attributed income figure. Wallet increases/decreases include trading, mail, purchases and transfers. Unknown/restricted reads mark cash coverage incomplete; missed intervals are not guessed.
- **Gold:** timestamped warbank and character-wallet snapshots, plus a sum of recorded wallets. This excludes unknown characters and does not claim to be your complete account wealth. Offline snapshots can become stale. Refresh balances reads the currently available data. The addon never deposits or withdraws money.
- **Loot:** grouped item variants and quantities from the game's localized self-loot messages. Crafted, received and looted items have distinct labels; other players' loot is ignored. Vendor estimates are separate from gold, use available item information, and show `?` when prices are missing. Zero vendor value is valid. This is received-item history, not a current inventory or sales-profit report. No auction prices are inferred.
- **Session history:** saved sessions across recorded characters. View opens the original session summary. Character and date filters apply to the selected activity page; the history page defaults to all saved sessions, while Loot defaults to the current session. Today uses the local calendar day; Last 7 days includes today and the previous six calendar days. History date filtering uses session start times; loot uses receipt days, including sessions crossing midnight.

Saved history retains the newest 100 sessions. Each session retains 250 recent event details and up to 300 item/day/source groups. Total received quantity survives detail limits; omitted item prices stay unknown. Older sessions eventually age out. No data is imported from Journalator, My Loot History or Warband Accountant, and existing planner tasks and other addon databases remain intact.

## Development status

This combines a manual-task planner with observed gold, item and session history. It now includes armor/covenant rules, category weekday visibility, small optional starter packs and read-only roster imports. A comprehensive seasonal task catalog, automatic activity completion, a comprehensive transaction-source breakdown, auction market valuations and reminder migration remain pending. Gold, loot and session history are available in this version.

Existing Folio notes and crafting Planner reminders remain in their own addons. No migration is performed.

## Verification

The Lua 5.1 checks in `tests/run_tests.py` cover quick capture, independent/shared completion, group changes, unavailable reset data, reset transitions, weekday/interval recurrence, postponement, skipping, undo, DST, reload persistence, actual UI callbacks and a 403-character roster with bounded frame reuse, all full-window pages at three sizes, search, task action buttons, group/category dialogs, palette selection, Enter capture and separate compact geometry. Requires Python and `lupa==2.8`.

Still required in the WoW client: text/font fitting at your UI scale, long names, row tooltips, keyboard focus, dragging, actual reset APIs, login/alt/reload persistence, and behavior in combat. No in-game validation has been claimed.

Activity checks: run `tests/run_activity_tests.py` (also runs the existing task suite). Covers native event callbacks, bank transfers in either event order, separate cash/vendor estimates, localized/positional self-loot formats, duplicate chat lines, delayed and zero prices, midnight filters, secret/unavailable reads, reload and alt session boundaries, bounded storage and UI reuse. Game-client checks still required: real bank event timing, loot messages in your locale, cached item-price updates, tooltip fitting and login/reload behavior.

API implementation references: [Blizzard-generated item APIs](https://raw.githubusercontent.com/Gethe/wow-ui-source/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/ItemDocumentation.lua), [chat/loot events](https://raw.githubusercontent.com/Gethe/wow-ui-source/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/ChatInfoDocumentation.lua). Existing installed reference addons were inspected for bank snapshots, localized self-loot parsing and distinctions between received items and financial transactions. The new recorder is independent.

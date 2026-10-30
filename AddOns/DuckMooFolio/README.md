# DuckMoo Services: Character Folio

**v0.5.4, by DuckMoo Media**

An adventurer's binder for your alt army: character sheets, searchable warband information, personal plans, and collector field notes. A persistent sidebar, compact character cards, searchable roster, and an autosaving notebook. The original purple palette remains available; Trans Pride uses the exact blue, pink, and white of the supplied flag.

## Install and open

1. Close WoW, or return to character selection.
2. Extract the `DuckMooFolio` folder into `_retail_/Interface/AddOns/`.
3. Enable **DuckMoo Services: Character Folio** in your AddOns list.
4. Log in and type `/folio`, `/dmfolio`, or click the book minimap button.

Opening the folio shows your **current character**. The Roster sidebar page opens the roster, and selecting a character opens that character's sheet. `/folio roster` goes straight to the roster. `/folio scan` refreshes your current character; `/folio minimap` toggles the minimap button. The window moves and resizes, retaining its position and size. The default is 1040 by 740; the supported minimum is 940 by 560. Older smaller saved windows are expanded to fit the sidebar. Escape closes it.

Log into each character once with the addon enabled. Open each crafting profession and allow its recipe data to load to capture expansion skills. No protected API is used to open professions for you. Linked/guild professions are ignored.

## Pages

- **Character:** Name, chosen title, race, faction, guild, realm, specialization, role, exact level/XP display, equipped item level, rested XP, attributes, health, armor, crit/haste/mastery, speed rating/bonus and movement percentage, hearthstone destination, location, update time, account collection milestones, and your general plans.
- **Skills & trades:** Known professions and secondary skills, recorded expansion ranks and spent specialization nodes, last filtered known-recipe count, a compact hero-talent and specialization summary, and known titles. Expansion data is collected when a profession is opened; absence of a snapshot is explicitly shown as not scanned.
- **Reputations:** Reputations encountered by that character, progress/renown, and whether the game marks the reputation account-wide. Collapsed reputation headers are expanded for scanning and restored afterward.
- **Notebook:** Separate Where I left off, Purpose & plans, Adventuring, Professions, and Backstory sections, with a category rail and an editor that grows with the window. Notes save as you type. Assign tags opens a picker of common character purposes, with selected tags highlighted and custom tag creation. Tags are case-insensitive and filterable; Save tags applies your choices. The notebook also has an explicit Save note button and saved feedback. You can edit notes for offline characters.
- **Roster:** Collapsible realm groups ordered by level/XP. Rows show name, realm, region, level, equipped item level, rested XP, faction, and last recorded spec. Combine class, faction, role, region, realm, profession, expansion skill, reputation and tag filters. Search also includes notes. Select a reputation to show progress directly in each row. Reputation and role searches use a flat ranking so the best match is not buried in another realm group. Role filters include capable classes and put characters last recorded in that role first. Other sorting controls include level/XP, item level, name, and rested XP. Filters expand when needed; search, sorting, and saved views remain accessible above the rows. Page capacity adapts to window height up to 20 entries/headers. Realm headings stay with their characters and repeat when a realm continues on the next page.
- **Census:** Open **Profession blindspots** to inspect all 156 standard profession expansion skills from Classic through Midnight, including Cooking, Fishing, and gathering. Filter by profession/expansion, show gaps or all coverage, inspect owner counts and highest recorded ranks, and click a row to find its owners or base-profession characters in Roster. **No owner recorded** means no owner in saved snapshots, not proof that your entire account lacks it. **Needs scanning** means a character has the base profession but their expansion ownership is unknown. Gathering skills are captured directly when Blizzard supplies usable rank data.

  Character counts by faction, class, race, profession, level band, realm and tag, plus characters closest to their next level.
- **Collection leads:** Optional read-only collection opportunities from All The Things, including instance rankings and zone quest counts. **ATDART % Target** appears above Legacy Dungeons and shows the legacy dungeon or raid with the lowest exact completion fraction. Ties are selected randomly once per ATT capture, then saved with that snapshot; tab changes, resizing, and reloads retain the target. This is the only percentage ranking in ATT. The other lists remain ranked by missing counts. After upgrading, click **Refresh opportunities** for each character to capture the totals needed for percentages. A fully complete snapshot can still show a 100% target; no eligible data shows a message instead.
- **Preferences:** Eleven themes (purple, bright light mode, Azeroth, trans pride, lesbian pride, teal, crimson, blue), background opacity, minimap visibility, usage guidance, and the extremely official DuckMoo Media binder manifesto.

Level **82.13** means level 82 and 13% toward 83. Sorting uses the unrounded XP fraction. Rested XP is expressed as a percentage of one level's XP requirement, so 150% is meaningful; max-level characters show a dash. All timestamps use your computer's local time.

## Oceanic realms

Americas realm labels are automatic: **NA-OCE**, **NA-LATAM**, **NA-BR**, and **NA-US**. Oceanic, Latin American, and Brazilian realm lists follow the supplied realm groupings. Normalized realm names, spaces, and apostrophes are handled. Other regions retain EU/KR/TW/CN labels. Combine NA-OCE + Horde + Healer to find your Sydney-server healers. Older manual realm assignments are migrated to automatic labels.

## All The Things

ATT is optional. If missing or disabled for the current character, the Collection leads page tells you to enable it and reload. If enabled but not ready, the tab asks you to open ATT and let it prepare its collection data.

With your current character selected, open ATT's main list, let it update, then click **Refresh opportunities** in the folio. The adapter reads `AllTheThings.Windows.Prime.data`, using ATT's already-prepared progress, visibility and collection flags. It does not change ATT's collection records, filters, or groups. Dungeon/raid classification uses the Encounter Journal with header fallbacks; the Journal's selected tier is restored afterward. Work is spread across small timer batches.

- Legacy dungeon and raid lists rank remaining ATT opportunities, not drop probabilities or runs required. Legacy instances stop at Dragonflight: The War Within and Midnight are excluded. Instances without a known expansion are omitted from legacy rankings. This also applies to older saved snapshots.
- Zone lists count distinct visible, collectible, uncollected quest IDs and exclude known capital map IDs. Zone expansion labels use ATT metadata, with map ancestry as a fallback when zones are grouped geographically. The expansion chooser narrows results. The first 15 matches in each category are displayed.
- Counts follow the ATT profile at capture. An account-wide/all-character profile can include things that this particular character cannot obtain. For useful per-character rankings, configure ATT's character/availability filters before capture.
- Offline characters show their saved ATT snapshot and its timestamp. Only the logged-in character can refresh that data.
- Unprepared, filtered, hidden, or unsupported ATT groups may not appear. ATT's internal structure can change. An adapter failure produces a message rather than inventing counts. This adapter has been source-inspected and mock-tested; it still needs a live ATT/Blizzard client field test.

## Concentration Planner

This addon is separate from DuckMoo Services: Concentration Planner and has its own SavedVariables, `DuckMooFolioDB`. When the planner is loaded, a shortcut on the character sheet opens it. No concentration schedule or planner data is changed by the folio.

## Snapshot limits

Offline characters cannot be queried live. A sheet represents its last observed state, with an update timestamp. Logout capture records the last location when possible; a client crash can leave an earlier snapshot. Collection milestones such as mounts and pets are shared account totals, not counts earned by that individual character.

This release covers the sheet/roster/notebook foundation. It is not a complete replacement for every WoWThing feature. It does not track inventory, mail, auctions, sell items, modify talents, equip gear, or automate gameplay. A graphical profession knowledge-tree view, exhaustive quest history, friendship/paragon-specific reputation presentation, and live-client refinement are further development areas. Standard reputation/renown information is captured now. Missing or restricted API data appears as unknown, rather than being fabricated.

## Development and validation

Install `lupa==2.8` and run:

```sh
python3 DuckMooFolio/tests/run_tests.py
```

Tests run actual addon code under Lua 5.1 with mocked Blizzard frames/APIs. Coverage includes snapshots, concentration-independent note storage, exact XP sorting, rested display, expansion skills, linked profession rejection, collapsed reputation restoration, combined filters over 400 alts, healer-role prioritization, all UI pages, note isolation/persistence, frame reuse, chooser actions, minimap/slash behavior, ATT absent/not-ready states, read-only instance/quest ranking, deduplication, capital exclusion, combat deferral, and secret-value sanitization. Regression checks also cover continuous keyboard focus, roster paging, realm expansion, tag selection/custom tags, notebook category switching, theme opacity, resize cursor deltas, namespaced specialization APIs, hero talents, realm mapping, ATT color-code cleanup, and persisted snapshots through reload/alt switches and unavailable/logout APIs. Real Retail client verification is still required.

API/source references checked while building:

- Blizzard-generated API documentation in [wow-ui-source](https://github.com/Gethe/wow-ui-source/tree/live/Interface/AddOns/Blizzard_APIDocumentationGenerated).
- Blizzard's [Encounter Journal](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_EncounterJournal/Mainline/Blizzard_EncounterJournal.lua).
- ATT's [Prime window](https://github.com/ATTWoWAddon/AllTheThings/blob/master/src/UI/Windows/Prime.lua), [map/instance classes](https://github.com/ATTWoWAddon/AllTheThings/blob/master/src/Classes/Maps.lua), and filter module.

## License

Copyright 2026 DuckMoo Media. GNU GPL v3. See `LICENSE`.

## Profession coverage catalogue

The catalogue uses standard expansion profession skill IDs checked against ATT's [skill conversion data](https://github.com/ATTWoWAddon/AllTheThings/blob/master/.contrib/.db/shared/constants/Parser%20Setup%20Data/SKILL_ID_CONVERSION_TABLE.lua). Labels use Blizzard's localized profession information when available. Special crafting systems and retired Archaeology/First Aid are outside the standard profession matrix. Learned expansion skill coverage does not imply complete recipe collections or specialization investment. Coverage uses only the characters recorded by this addon.

## Returning to a character

Use **Edit next step** on the character sheet to leave a reminder in **Where I left off**. It saves as you type, stays with that character, and remains separate from Purpose & plans. Offline notes can be edited too. The card shows when the reminder last changed; opening it does not refresh that date.

The card sits between Travel & whereabouts and Collection milestones. Purple retains its original palette. Gunmetal is a separately named choice. Trans Pride uses exact #5BCEFA blue, #F5A9B8 pink, and #FFFFFF white in the flag order, with dark readable text. Trans pride - dusk replaces the former pastel option with deeper blue and pink surfaces, white text, and white accents. Its saved preset key is retained so existing preferences continue working. Light mode uses warm peach, butter-yellow, coral, and rosy pastel surfaces. Classic plum now uses distinct wine/plum shades rather than duplicating DuckMoo Purple. All other theme choices remain available. Warband Planner can optionally read a detached identity roster through this addon's export API; notes and tags are not exported.

## Saved roster views

Set the roster filters, search, sort and flat/grouped preference, then choose **Save view** and give it a name. **Saved views** recalls it. Saving the same name replaces that view. **Remove view** removes only that saved filter preset. Character data and your current filters remain available. Realm collapse state stays independent of saved views.


## 0.5.0 visual milestone

This release replaces the horizontal navigation and main character, roster, and notebook layouts. Character and warband pages share a sidebar and stable header. Attributes use one compact grid; travel, next step, collection milestones, and plans retain their saved data and order. Character selection works from any page. The collection, reputation, skills, census, and preferences pages retain their existing behavior inside the new frame.

The package passes Lua 5.1 behavioral and strict native-text mock checks, including 400-character combined searches, resizing, note focus, offline edits, and paged realm groups. The accompanying PNGs are source-based layout previews with fictional data and approximate fonts/icons, not screenshots from WoW. Actual game rendering, game interactions, and live ATT compatibility still require client testing. This delivery does not install into the game or touch SavedVariables.


## 0.5.1 preset refinement

Trans Pride uses flag blue as the main background, pink panels, blue buttons, and white accents. White is reserved for the flag stripe and accents rather than large surfaces. Dusk uses darker blue/pink with white text. Warm Light Mode and Classic Plum have distinct palettes. The 0.5.0 layout and data behavior are unchanged.


## 0.5.2 window stacking

Main windows and standalone dialogs enable native top-level window behavior and render-layer flattening so their child panels stack as a single window when overlapping other DuckMoo windows. Clicking a window brings it forward. Layouts, colors, reset logic, data and chosen opacity remain unchanged. Actual overlapping-window rendering requires a Retail client check.


## Bundled user guide

See USER-GUIDE.txt for current installation, commands, collected data, storage, Nexus integration, troubleshooting and limitations. All TOCs use the DuckMoo Media category.


## Roster race, level bands and open profession slots (0.5.4)

Open Roster, then Filters. Race and Level band combine with existing class, realm, tag and profession filters. Level bands include decade ranges plus 80+ and 90+. Profession slots offers Level 80+ / open slot, any open primary slot, full, and unknown. These options persist in named saved views. Roster rows and tooltips show recorded open-slot counts and profession observation time.

Only the two primary professions use these slots; Cooking, Fishing and Archaeology do not. New snapshots explicitly capture primary slots, including a genuinely empty list. Partial reads preserve prior observations; completely empty reads are confirmed on a subsequent capture rather than clearing a prior snapshot during login. Legacy snapshots use their recorded profession list/time; characters with no profession observation remain unknown. Offline entries represent the last capture, not live state. Notes and tags are preserved.

# DuckMoo Services: Concentration Planner 0.5.2

By DuckMoo Media. Another suspiciously useful thing by DuckMoo Media.

A standalone WoW Retail calendar, crafting planner and reminder addon for Kenzie DuckMoo. No CraftSim or other addon dependency.

The full window now follows Folio's sidebar design, with persistent search, Refresh and quick note controls. Daily planning separates concentration, patron checks and custom reminders beneath summary cards. Weekly and monthly views preserve their date/reset behavior inside the new frame. Preferences > Appearance offers the approved Folio palettes, including original Purple, distinct Classic Plum, warm pastel Light Mode, Trans Pride and Trans Pride Dusk.

The compact current-character dashboard retains its layout, dense/standard row options, Checked patrons actions, auto-fit behavior and separately saved position/size. The new full window defaults to 1040 by 740 with a supported minimum of 940 by 560; older smaller full-window sizes are expanded to fit the sidebar. Concentration snapshots, patron schedules, reminders, groups and visibility choices are preserved.

## Upgrade from 0.1.0 or 0.2.0

Exit WoW and replace the old `Interface/AddOns/DuckMooPlanner` folder with the folder from this ZIP. Keep your SavedVariables. Existing characters, Concentration snapshots, patron schedules and manual Hide choices are preserved. Prior expansion entries are now excluded by default, without deleting their data.

## First installation

1. Exit WoW.
2. Extract so `World of Warcraft/_retail_/Interface/AddOns/DuckMooPlanner/DuckMooPlanner.toc` exists. Avoid a duplicate nested folder.
3. Enable DuckMoo Planner in the character-selection AddOns menu. For a newer interface build, enable Load out of date AddOns for this beta.
4. Visit each crafter and open each crafting profession window once to register it. Use `/planner scan` if necessary.
5. Open `/planner` or `/dmp`.

Interface versions: 120005, 120007 and 120100. This update has offline Lua 5.1 tests and a 400-character roster test. Its new native styling, minimap interaction and live-client behavior still require in-game verification.

## Midnight and prior expansions

Midnight entries are shown by default. Recognition uses verified skill-line IDs, so English profession names are not required.

Preferences contains a collapsed **Prior expansions** section. Expand it and enable **Include prior expansions in planner views** to include older currencies. Individual Hide/Unhide choices remain available within each section. An entry you manually hid stays hidden even when its expansion is enabled. Forget asks for confirmation before deleting one profession snapshot and its patron schedule.

Older data continues to be collected when accessible. Disabling its display does not erase it.

## Compact mode and resizing

Click **Compact** in the full window, or use `/planner compact`.

- Always shows only the logged-in character, even when no work is due.
- Each visible profession shows its concentration cap date and local AM/PM time, or **Full now**. Unknown snapshots prompt you to open the profession.
- Shows the next patron check date and regional daily-reset time, with Due/Overdue status only once actionable.
- **Checked patrons** buttons remain available for every visible profession. Clicking records your check-in and starts the default four-day reminder if none exists. You may check early; this does not verify whether orders were completed.
- Custom notes stay in the full Daily/Weekly planner and Reminders page.
- Defaults to 65% opacity. Preferences has a 20–100% slider. Full view has its own opacity slider, defaulting to 85%.
- **Expand** or `/planner full` restores the full window.

Drag the lower-right corner to resize either mode. Full and compact sizes and positions are stored separately. The initial compact window fits its current content up to a bounded height; once a size is saved, it respects that size and scrolls longer lists. The last mode and full-view tab are remembered across reloads/logins. The login checkbox opens the last view/mode automatically.

The full layout is denser than 0.1.0: responsive row widths, less padding, shorter rows, calendar cells that follow the available width, and only the number of calendar rows needed for that month. Long names and notes can be read in tooltips.

## Views and reset countdowns

All dates and AM/PM times use the computer's local clock.

**Daily:** Selected civil date, midnight to midnight. Today includes already full professions, caps later today, patron orders and custom notes. Already full Concentration stays on the list until spent. Today follows midnight rollover; browsing another date stops following until Today is clicked. A live daily-reset countdown updates once per second.

**Weekly:** Seven reset-day sections based on the regional game API. Concentration sections start at the local weekly-reset hour; an early Wednesday cap can belong to Tuesday's reset-day section. Patron reminders and dated notes use civil dates. Only upcoming work is shown. Already full bars and the Ready / overdue section are reserved for Daily and Compact. Missed recurring tasks may have tentative future occurrences marked as forecasts; their actual overdue entry stays in Daily. A live weekly-reset countdown updates once per second, including when browsing another week. If the reset API is unavailable, week grouping falls back explicitly to Tuesday 10 AM computer-local time; the countdown says unavailable.

**Monthly:** Upcoming Concentration caps and dated custom notes. Already full bars are excluded; patron reminders remain in the daily/weekly views. Up to two entries are visible per cell, with a `+N more` count. Hover for the full contents; click a date for the daily planner.

**Reminders:** Editable list of active and dismissed custom reminders.

**Preferences:** Separate Roster, Appearance and About sections. Roster pins the logged-in character, then offers a paginated, sortable alt list. Appearance has login behavior, minimap visibility, and separate full/compact opacity sliders. About explains the addon and lists DuckMoo Media and creator information.

The full-window search filters characters, realms, professions, expansions and note text. Compact mode always shows the logged-in character, regardless of an old search term.

## Roster at scale

Preferences > Roster pins the logged-in character and all its displayed professions above the alt controls. That pinned character is not hidden by a realm, profession, group or search filter. The alt list excludes the pinned character to avoid duplicate rows.

- Filter alts by profession, realm or custom group. Each chooser has text search and a scrollable list.
- Sort by character name, realm, profession or group, ascending or descending.
- Text search matches names, realms, displayed professions and assigned groups.
- Browse 15 characters per page. The UI reuses one page of row widgets instead of creating every roster row at once.
- A profession filter narrows the alt profession rows as well as the character results. The current-character block remains complete.
- Check character boxes across pages, then choose **Group selected** for bulk assignment. **Clear selection** clears the selected set.
- Each character's **Groups** button manages its own assignments. Characters may belong to multiple groups.
- Create, rename or delete groups in the group editor. New groups are assigned to the editor's selected characters. Checkbox changes assign/remove all selected characters. Deleting a group requires confirmation and preserves the characters and their schedules.
- **Reset** clears roster filters, sorting direction and search.

Prior expansion rows remain folded away by default. Expand **Prior expansions** to reveal those rows within the roster and access the option to include them in planner views. Manual profession Hide choices still take precedence.

## Minimap button

A duck-calendar button sits around the minimap. Left-click opens/closes the planner; right-click opens Preferences; Shift-click changes compact mode. Drag it around the minimap to reposition it. Its angle and visibility are saved. Hide/show it through Preferences > Appearance or `/planner minimap`. It has no external library dependency and supports the native round minimap and square layout.

## Appearance and About

Rounded purple surfaces, custom buttons with hover/press feedback, active-tab markers and slim status accents replace the stock boxed button layout. Existing resize and mode-specific geometry behavior remains.

Preferences > Appearance has independent opacity controls: **Full window 85%** and **Compact window 65%** by default, adjustable from 20% to 100%. The Daily onboarding text again explains character registration, slash commands and the local clock.

Preferences > About lists **DuckMoo Services: Concentration Planner**, **DuckMoo Media**, the addon purpose, registration and planner workflow, and the following user-provided creator information:

- Amazon: `amazon.com/author/kenzieduckmoo`
- Twitch, AO3, Threads, Instagram, TikTok and YouTube: `@KenzieDuckMoo`
- BlueSky: `@kenzieduckmoo.bsky.social`

Copy buttons select the page/handle text for Ctrl+C. The addon does not open a browser or send messages.

## Patron reminders

Each profession has its own schedule in Preferences. Click **Patron schedule**, choose four days or a fixed weekday, enter the first due date, and save. The weekday button cycles through Sunday–Saturday.

Four-day schedules restart from the civil day you click Checked patrons. Thursday completion schedules Monday; late Friday completion schedules Tuesday. Weekly schedules keep the selected weekday. Completing Sunday schedules next Sunday; finishing late Monday schedules the coming Sunday.

Missed work stays visible. Later dates are marked forecasts until completion determines the next actual due date. Reminder completion is manual, not automatic detection of patron order availability or completion of an individual in-game order.

## Custom reminders

Click **+ Note** in either mode, or use `/planner note`.

Enter text and a date as `YYYY-MM-DD`. Click the Repeat button to cycle between:

| Repeat | Behavior after Dismiss |
| --- | --- |
| Once | Removes the note from planner views; retains it in Notes for editing/restoring |
| After daily reset | Next occurrence is scheduled at the next actual regional daily reset |
| After weekly reset | Next occurrence is scheduled at the next actual regional weekly reset |
| Every X days | Next occurrence is X civil days after dismissal, from 1 to 3650 days |

For first occurrences, ordinary dates and X-day reminders start at local midnight. Reset reminders start at the reset hour on the selected date. Weekly first dates align to the reset weekday on or after that date.

Overdue reminders remain visible until dismissed. Future repeats are forecasts, not separate copies of the note. Forecasts use the stored reset weekday/hour and are recalculated from the game API on dismissal. A reset-based reminder cannot be dismissed or saved while its required reset API is unavailable; it never silently substitutes the other reset type.

In Notes, **Edit** opens the editor, **Delete** asks for confirmation, and **Restore** reactivates a dismissed one-off reminder. Saving an edit schedules the reminder again on its chosen date. Reset reminders and X-day reminders can be dismissed early from Notes; the next occurrence is based on the dismissal time.

Notes are account-wide, not bound to a character. You can include a character name in the text. Up to 500 characters are accepted. They are plain reminders and do not execute macros, commands or game actions.

## Commands

`/planner`, `/dmp` and `/duckplanner` accept the same commands:

| Command | Action |
| --- | --- |
| `/planner` | Toggle the window in its last mode |
| `/planner compact` | Open compact character dashboard |
| `/planner full` | Open full window |
| `/planner today` | Open full daily view at today |
| `/planner daily` | Open full daily view |
| `/planner weekly` | Open full weekly view |
| `/planner monthly` | Open full calendar |
| `/planner reminders` | Open Notes |
| `/planner note` | Open Notes and the new reminder editor |
| `/planner settings` | Open Preferences |
| `/planner about` | Open the About section |
| `/planner minimap` | Hide/show the minimap button |
| `/planner scan` | Scan the open profession |
| `/planner position` | Center the window and clear both saved positions |

## Concentration data

`DuckMooPlannerDB` stores account-wide data on this WoW installation. Characters use GUIDs internally and Name-Realm in the UI. Expansion skill lines remain separate.

The addon observes game-provided amounts, caps, recharge rates and timestamps. It projects offline regeneration, updates on currency/profession events, and refreshes once per minute. Normal regeneration preserves the forecast; spending/refunds replace it, including one-point spends. Rows show the last observation and current projected amount in tooltips.

You must visit characters to register them. Changes made with the addon disabled or on another installation are unknown until revisited. It does not automatically remove unlearned professions; use Hide or Forget. Data is written on normal logout/reload; a crash can lose recent observations. Fractional Concentration not exposed in the initial quantity can cause a small forecast difference.

No crafting, order submission or character switching is automated.

## Testing and reporting

Run offline tests with Python 3 and `lupa`: `python tests/run_tests.py`.

Coverage includes date boundaries and DST, Concentration forecasts and spends, patron schedules, prior-expansion filtering/migration, custom reminder validation and recurrence, targeted deletion, reset API failure, compact grouping and actual check-in button callbacks, saved sizes/modes/opacity, responsive layouts at multiple sizes, countdown text and frame/editor reuse. The 0.3.0 checks add 400 characters with 800 professions, pinned-current behavior, realm/profession/group filters, multi-group and bulk assignment, group rename/delete, actual chooser callbacks, page frame reuse, unscheduled compact check-in, upcoming-only weeks, full opacity, About text and minimap clicks/visibility.

These tests mock native frames and APIs. They do not establish pixel-perfect layout or event behavior inside the live client. For this update, also verify minimap placement/dragging, the new native rounded styling, roster filters/pagination and bulk group assignment on your actual client. Existing checks:

1. Existing characters/patron schedules remain, with only Midnight visible initially.
2. Prior expansions can be expanded and enabled in Preferences.
3. Resize both modes, change opacity, and reload to check persistence.
4. Confirm compact shows only the logged-in character, future cap/check times, and Checked patrons affects only that profession.
5. Confirm today's patron tasks appear after regional daily reset; earlier unfinished tasks remain overdue.
5. Check daily/weekly countdowns against the game clock.
6. Add, dismiss, edit and delete a custom note; try each repeat option.

For Lua errors, enable `/console scriptErrors 1` and provide the first error and build number from `/dump select(4, GetBuildInfo())`.

Source references: [Blizzard API source mirror](https://github.com/Gethe/wow-ui-source), [CraftSim profession skill-line constants](https://github.com/derfloh205/CraftSim/blob/main/Util/Const.lua) and [CraftSim concentration model](https://github.com/derfloh205/CraftSim/blob/main/Classes/ConcentrationData.lua). DuckMoo Planner is an independent implementation.

Patron reminder dates start at that date's regional daily reset, rather than local midnight. Before reset, today's patron work stays out of the Daily task list. Compact displays its scheduled time without calling it due. If the reset API is unavailable, today's new reminder waits until the API recovers; earlier overdue work remains visible.


## 0.5.0 verification and delivery

Automated Lua 5.1 checks pass for reset handling, DST, forecasts, note recurrence, real patron-check button callbacks, current-character compact scope, prior-expansion visibility, 400-character roster filtering/paging/groups, saved geometry/opacity, frame reuse, sidebar layouts and the palette chooser. Source-based PNG previews use fictional data and approximate fonts/icons; they are not WoW screenshots. Actual Retail rendering and live interaction still require in-game verification. This release is delivered as a ZIP and does not automatically install into WoW.


## 0.5.1 reset timer visibility

The full-window reset timer is now drawn inside the sidebar instead of underneath its background. Compact and full views have separate timer text elements, using each palette's main text color. The approved layout and reset calculations are unchanged.


## 0.5.2 window stacking

Main windows and standalone dialogs enable native top-level window behavior and render-layer flattening so their child panels stack as a single window when overlapping other DuckMoo windows. Clicking a window brings it forward. Layouts, colors, reset logic, data and chosen opacity remain unchanged. Actual overlapping-window rendering requires a Retail client check.

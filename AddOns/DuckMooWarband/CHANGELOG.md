# 0.4.0 gold, loot and session milestone

- Add Session, Gold, Loot and Session history pages in the approved full-window design.
- Automatically record sessions while enabled, across login/reload/alt changes. Add optional names, manual new-session boundaries and history drill-down.
- Record actual wallet and warbank snapshots, observed balance changes and timestamps. Internal bank transfers cancel in combined cash change; missing/restricted data stays explicitly incomplete.
- Record localized self-loot/received/crafted item messages, deduplicate chat lines and resolve delayed item information. Keep vendor estimates separate from real gold, with unknown-price indicators.
- Add date/character filters, search, native item tooltips and bounded history. Preserve manual task behavior, compact layout, palettes and prior startup/stacking fixes.
- Extend Lua 5.1 event integration, accounting, localization, persistence and UI checks. Include fictional source-based visual previews; actual client validation remains required.

# 0.3.1 startup repair

- Fix UI.lua:51 when opening /warplan: plain EditBoxes do not provide SetBackdrop. Rounded styling now clears a native backdrop only when that method exists; custom textures still draw normally.
- Tighten the UI mock to expose backdrop methods only with BackdropTemplate. It reproduces the original failure and passes after the repair; all input boxes and their theme initialization are checked.
- Preserve the 0.3.0 layout and all task data. No SavedVariables migration.

# 0.3.0 visual milestone

- Rebuild full view with Folio-style sidebar navigation, Today summary cards, persistent search and quick entry.
- Add dedicated Characters, Categories and Preferences pages using the existing roster, group and weekday behavior.
- Include all approved Folio palettes, rounded input surfaces and gentle quick-entry guidance.
- Preserve current-character capture defaults, cross-character visibility, independent/shared progress, Worked on it, recurrence, archive/restore and Undo.
- Save full and compact geometry separately; add resizing, viewport-aware pagination and bounded widget reuse.
- Keep compact mode as a dense cross-character list. Include grouped main/dialog stacking to prevent components interleaving with the other addons.
- Extend offline Lua 5.1 checks and provide fictional source-based previews. Live WoW rendering still requires client verification.

# 0.2.1 repair

- Fix task hover errors caused by a replacement count reaching GameTooltip:SetText. Add a real hover regression with strict argument checks, including escaped pipe characters.
- Regression mocks now reject unintended extra native text arguments.

# 0.2.0 preview

- Add armor and observed active-covenant eligibility rules with explicit unknown-data handling.
- Add independent category weekday visibility.
- Add optional current-character daily/weekly starter packs with duplicate prevention.
- Import detached roster snapshots through new optional Folio/Planner provider APIs, preserving timestamps and own group assignments.
- Extend regression checks for rules, category callbacks, imports and pack deduplication.

# 0.1.0 preview

- Add independent character snapshots and frictionless current-character capture.
- Separate character/class/group eligibility from individual/account completion.
- Add remaining-work views across the roster, a compact auto-height window and task editing.
- Support manual Done, Worked on it, Postpone, Skip, Undo and archive/restore.
- Add reset, weekday and completion-relative intervals, with explicit unavailable-reset handling.
- Preserve per-character state and bounded action history; validate Lua 5.1 behavior and UI callbacks offline.

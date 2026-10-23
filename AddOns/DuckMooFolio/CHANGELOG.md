# v0.5.2

- Enable top-level window behavior and render-layer flattening on main windows and standalone dialogs. This keeps child panels in their window's stacking group instead of interleaving with another DuckMoo window.
- Preserve internal control layering, approved layouts, palettes, data, calculations and saved opacity.
- Add regression checks for main/dialog window configuration across page changes and mode switching. Actual overlap behavior requires a client check.

# v0.5.1

- Replace white Trans Pride surfaces with flag blue/pink, keeping exact flag stripes and white accents.
- Replace Trans pride - pastel with Trans pride - dusk: deeper blue/pink, white text and accents. Preserve the existing saved preset key.
- Give Light Mode warm peach, butter-yellow, coral and rose pastels; distinguish Classic Plum with wine/plum tones.
- Preserve the approved 0.5.0 layout and all existing behavior. Check main and secondary text contrast across every revised surface.

# v0.5.0

- Replace horizontal tabs with grouped sidebar navigation and a persistent character chooser/header.
- Rebuild the character sheet with a compact attribute grid and clearer identity, travel, next-step, collection, and plans cards. Preserve the approved next-step placement.
- Rebuild the notebook with a category rail, responsive editor, autosaving, and offline character editing.
- Rebuild the roster toolbar with expandable filters and saved views. Adapt page capacity to window height; keep realm headings with their rows and repeat them on continued pages.
- Use the supplied Trans Pride flag colors exactly: #5BCEFA, #F5A9B8, #FFFFFF, pink, blue. Preserve the original purple and separately named Gunmetal palettes.
- Preserve existing snapshots, tags, notes, profession coverage, reputation, ATT integrations, and minimap/slash access.
- Add behavioral regression checks for supported window sizes, focused note entry, character switching, realm pagination, exact flag colors, and frame reuse. All Lua 5.1 checks pass; live Retail verification remains outstanding.

# 0.4.2 repair

- Restore the original purple preset, name gunmetal explicitly, and use dark blue/pink Trans Pride surfaces with light text. Retain the earlier pastel variant as a separate choice. Normalize string helpers to return text only.
- Regression mocks now reject unintended extra native text arguments.

# v0.4.1

- Refine the default purple theme with charcoal surfaces and restrained accent colors; retain the earlier palette as Classic plum and preserve other themes.
- Keep the accepted Where I left off placement between Travel and Collection milestones.
- Expose a detached identity-only roster snapshot for optional read-only integration with Warband Planner.

# v0.4.0

- Add a prominent Where I left off card and autosaving notebook entry for each character.
- Preserve resume notes across snapshots, reloads and offline character browsing; timestamp actual edits.
- Add named roster views for filters, search, sort and flat/grouped preference, with save, recall and removal controls.
- Keep existing notes, tags, profession coverage and ATT integration.
- Add Lua 5.1 regression checks for the new persistence and UI callbacks.

# v0.3.0

- Added ATDART % Target above Legacy Dungeons: lowest completion fraction across legacy raids/dungeons, with random tie selection once per captured snapshot. Targets persist across browsing and reloads.
- ATT captures now retain total/progress, including complete instances for the target. Existing opportunity lists continue to use missing counts and show unfinished content only. Older snapshots ask for a refresh rather than inventing percentages.
- Added Census → Profession blindspots, covering all 156 standard expansion profession skills from Classic through Midnight. Profession/expansion filters, gap/all views, owner counts, best ranks, paging, and roster shortcuts are included.
- Coverage distinguishes recorded owners, unscanned base-profession owners, and no owner recorded. It flags characters missing profession snapshots and does not claim definitive account-wide absence.
- Added direct gathering/expansion rank capture where supported by Blizzard APIs and zero-rank scan checks. Preserved recipe/knowledge details when refreshing expansion ranks.
- Extended Lua 5.1 regression checks for percentages, ties, persistence, old snapshots, coverage states, localization, gathering, navigation, and frame reuse.

# v0.2.1

- Raised header buttons above the draggable header so X receives clicks.
- Swapped ATT and Reputations tabs.
- Reworked trans pride into pastel pink/light blue surfaces and light mode into bright blue/pink/lavender colors with dark text.
- Resolved outdoor zone expansions from ATT source ancestry and Blizzard map ancestry, including distinct Outland/Draenor and Midnight versions of zones.
- Legacy dungeon/raid lists now stop at Dragonflight. The War Within, Midnight, and unclassified instances are excluded, including from older saved snapshots.
- Added regression checks for closing, control layering, tab order, bright theme text contrast, headerless zone groups, legacy cutoff, and cached snapshot display.

# v0.2.0

- Tightened stat cards, profession rows, census spacing, and settings paragraphs; removed the background footer line.
- Added eight themes and a background opacity slider that leaves text fully opaque.
- Added common/custom tag picker with selection indicators and Save tags; tags appear beside identity information.
- Fixed notebook mouse/keyboard input, category switching, saved feedback, and explicit Save note.
- Fixed roster search focus, paging/realm controls, and resize anchoring with cursor delta tracking.
- Switched to Retail namespaced specialization APIs and added hero specialization summaries.
- Added movement percentage, speed rating, and speed bonus to character stats.
- Preserved existing snapshots when APIs return unavailable values; logout updates whereabouts without overwriting stats.
- Added automatic NA-US/OCE/LATAM/BR realm classification and migration.
- Excluded Archaeology; moved Cooking/Fishing below primary professions. Profession, specialization, and title headers collapse.
- Changed the highest census band to 90s and removed ATT color markup from displayed names/profile labels.
- Extended Lua 5.1 regression checks; actual Retail client validation remains required.

# 0.1.0

- First character-folio release with a purple fantasy dossier presentation.
- Collect identity, level/XP, spec/role, attributes, item level, rested XP, guild, location, hearthstone, talents, titles, professions/expansion skills, reputation/renown, and account collection milestone snapshots.
- Add searchable/paginated warband roster, realm collapse controls, combined filters, exact XP sorting, and role-capability prioritization.
- Add persistent per-character notes and tags.
- Add Warband Census and nearest-to-next-level list.
- Add optional read-only ATT adapter, active-profile opportunities, zone quest deduplication, capital exclusions, and missing/disabled/not-ready messages.
- Add minimap button, slash commands, resizable saved window, and Concentration Planner shortcut.
- Add Lua 5.1 behavior/UI tests with 400 simulated alts.

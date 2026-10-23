# v0.5.2

- Enable top-level window behavior and render-layer flattening on main windows and standalone dialogs. This keeps child panels in their window's stacking group instead of interleaving with another DuckMoo window.
- Preserve internal control layering, approved layouts, palettes, data, calculations and saved opacity.
- Add regression checks for main/dialog window configuration across page changes and mode switching. Actual overlap behavior requires a client check.

# v0.5.1

- Fix full-window reset text being drawn beneath the sidebar background. Use separate sidebar/full and main-window/compact timer elements with the theme's main text color.
- Add regression checks for timer parentage, visibility, daily/weekly selection and switching modes. Preserve the approved layout and all reset calculations.

# v0.5.0

- Rebuild the full window with Folio-style sidebar navigation, persistent search, profession Refresh and quick-note controls.
- Add daily summary cards and separate concentration, patron-check and reminder sections. Preserve reset gating, ready bars and forecast semantics.
- Retain weekly/monthly views, reminders and roster/group/settings tools within the redesigned full window.
- Add the approved Folio palettes under Preferences > Appearance; preserve independent addon data and settings.
- Keep the compact current-character layout, dense/standard rows, Checked patrons, auto-fit and separate geometry. Migrate small full windows to the new 940 by 560 minimum.
- Extend actual Lua 5.1 UI checks for daily grouping, patron actions, sidebar sizing, compact scope and palette selection. Live Retail verification remains outstanding.

# 0.4.3 repair

- Normalize the text sanitizer to return one value to native UI methods. Preserve the approved Checked patrons behavior and existing layout.
- Regression mocks now reject unintended extra native text arguments.

# v0.4.2

- Align the fixed window palette with Folio and Warband Planner's charcoal/purple styling.
- Add an optional denser compact dashboard with 60-pixel profession rows; retain both forecasts, check-in controls and the standard layout.
- Expose a detached identity-only roster snapshot for optional read-only integration with Warband Planner.
- Preserve current-character scope, saved geometry/opacity, schedules and existing reminders.

# v0.4.1

- Rename patron check-in buttons to Checked patrons and clarify that they record a check, not verified order completion.
- Preserve patron recurrence behavior and the current-character compact dashboard.
- Align the displayed version, manifest and README.
- Reserve enough row space for the new labels.
- Make the test runner work with the Windows C runtime timezone rules; retain daylight-saving transition checks.

# 0.4.0

- Replace compact's alt roster with the logged-in character and every visible profession, regardless of whether work is due.
- Show each profession's concentration cap time (or Full now), next patron check date and local AM/PM reset time, plus its Done button.
- Wait until the regional daily reset before showing today's patron tasks in Daily; keep unfinished earlier tasks overdue.
- Preserve early Done, automatic four-day schedules, prior-expansion visibility, opacity, and saved window geometry.
- Keep custom notes in the full planner instead of the character-focused compact dashboard.

# 0.3.0

- Rename display title to DuckMoo Services: Concentration Planner by DuckMoo Media.
- Remove Ready / overdue and already-full bars from weekly view; retain upcoming tasks and forecasts.
- Show compact Done for unscheduled professions; create the default four-day patron schedule and mark it done on click.
- Add a draggable minimap duck-calendar button, settings visibility and slash toggle.
- Pin the logged-in character above a paginated 15-character alt roster.
- Add profession, realm and custom-group filters, search, ascending/descending sorting, and reusable row widgets.
- Add character group creation, rename, confirmed deletion, multiple memberships and bulk assignment across selected pages.
- Separate Settings into Roster, Appearance and About.
- Add full-window opacity, default 85%; retain independent compact opacity, default 65%.
- Restore Daily onboarding/local-time text.
- Add a playful branded About section with user-provided Amazon/social information and copy controls.
- Replace stock buttons/hard outlines with rounded purple surfaces, hover/press feedback, active tabs and status accents.
- Add 400-character/800-profession roster tests and new interaction tests.

# 0.2.0

- Default planner visibility to Midnight; put older entries in a collapsed Prior expansions section with an inclusion toggle. Preserve saved data and explicit Hide choices.
- Add remembered compact Today roster, character grouping and per-profession patron Done buttons.
- Add compact opacity slider, default 65%.
- Add native window resizing, independent sizes/positions by mode, responsive widths, denser rows and shorter headers.
- Add live daily/weekly reset countdowns.
- Add `/planner`, `/planner compact`, `/planner full` and note commands.
- Add dated custom notes, daily-reset/weekly-reset/X-day recurrence, Dismiss, Restore, Edit and confirmed Delete.
- Add custom reminders to calendar, daily/weekly planners and compact view.
- Preserve last view/mode at login.
- Catch one-point Concentration spends when preserving recharge forecasts.
- Expand Lua 5.1 integration/model tests for upgrade behavior and new features.

# 0.1.0

Initial monthly calendar, daily/weekly planners, Concentration snapshots, per-profession patron schedules and crafting roster settings.

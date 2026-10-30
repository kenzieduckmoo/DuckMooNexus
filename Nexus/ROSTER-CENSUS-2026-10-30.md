# Character Sheets: roster and census

The Character Sheets section now contains a dedicated `/characters/roster` subpage. Its Roster, Census and Profession Openings tabs share combined filters: class, race, level band, role capability, faction, realm, realm region, profession, expansion skill, reputation, tag, primary profession slots, and text search including captured notebook text.

Roster columns show level and XP, equipped item level, rested XP, last specialization and role, professions and last seen. Sorting supports level plus unrounded XP, equipped item level, rested XP and name. Optional realm grouping and browser-local named views are included. Healer and tank filters include capable classes, with the last observed matching role sorted first.

Census counts faction, class, race, profession, level band, realm, tags and region within the filtered roster. Click a category to drill into the roster. Uncapped characters with recorded XP appear in a nearest-next-level list.

Profession Openings contains the existing level-80+ open-primary-slot list, with links to individual sheets. Cooking, Fishing and Archaeology do not consume primary slots. Unknown profession observations remain distinct from confirmed openings. The former `/characters?professionSlots=open` link redirects to this view.

Folio supplies recorded XP, rested XP, notes, tags, realm region, expansion skills and reputations; existing API/addon identity and profession observations remain in use. Data refresh follows Nexus source revisions. The roster query projects only needed fields rather than transferring recipe/knowledge catalogs. Saved views use local browser storage, separately for Retail and Forever, and do not edit addon notes, game data or plans. Missing captured fields remain unknown. Existing addon files need no update for this page.

Validation: focused roster-model checks cover combined filters (including 80+/90+ bands), class capability and recorded-role priority, unrounded XP ordering, notebook search and census memberships. Production web build includes TypeScript checking. Deployment backs up replaced web source files before rebuilding only the web service.

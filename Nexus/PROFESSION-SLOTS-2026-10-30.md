# Level 80+ profession opportunities

The Characters page now displays characters at level 80 or above with one or two observed open primary profession slots, with source timestamps, current profession names and character-sheet links. A toggle filters the roster to these characters, and the Professions page links directly to `/characters?professionSlots=open`. The view works within the selected client namespace. Missing profession observations are separate from recorded empty slots.

Slot observations use the newest usable Folio profile profession capture or successful Blizzard professions profile. Count only the primary base professions; expansion tiers, secondary professions and missing API payloads do not create extra slots. Folio 0.5.4 adds race and level-band roster filters, saved-view support and explicit primary capture. Existing legacy profession timestamps/lists remain usable. No notes, tags, saved plans, database history or game SavedVariables are reset.

Validation: primary/secondary separation, unknown/empty distinction, source freshness, level boundaries, Folio combined filters and named view persistence. Production build and live verification are recorded in the deployment log on Nexus. Native in-game verification requires the updated addon to load in WoW.

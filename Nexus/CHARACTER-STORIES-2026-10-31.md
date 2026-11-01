# Character biographies, memorials and launch readiness

## Delivered on October 31, 2026

Every captured Omni character can open a native biography and memorial from its character sheet or Adventure Journal. Routes are `/characters/<guid>/story?client=retail|forever` and `/characters/<guid>/memorial?client=retail|forever`. The independent client channels stay separate. A missing Omni character displays a waiting state instead of a fabricated story.

### Biography and memorial

The factual biography is assembled deterministically from retained observations, not generated fictional adventures. It includes identity, first-observed life date and level, elapsed calendar span between observations (not played time), highest recorded level, retained event counts and an explicit terminal-death status. Early observations are not presented as a character creation date. UTC dates in narrative exports are labelled; the website also presents local timestamps.

The memorial only presents a recorded terminal Hardcore death when the life summary has endedAt, which the existing addon sets when Hardcore mode was explicitly enabled. Ordinary deaths and being offline never declare a character deceased. An epitaph can be drafted beforehand and is labelled as personal writing. Killer attribution and death cause remain unknown.

Recorded highlights select up to eight recent events in each of five milestone categories (levels, quests, achievements, encounters and deaths), at most 40 total. Expand an event to inspect captured evidence. Full event history remains in the paginated Adventure Journal. Counts use the full deduplicated retained event archive, including events rotated out of the addon; counts are events, not unique quest/achievement completion totals.

### Writing and highlights

Open **Write & choose highlights** to edit backstory, journey notes and an epitaph. Keep a recorded milestone as a highlight, add your own commentary, or add a dated personal recollection. Personal writing is labelled separately from captured facts. Up to 100 selected or personal highlights are supported. Press Save to persist changes to Nexus across devices.

Writing is stored in PostgreSQL in character_stories, keyed by namespace and GUID, separately from captured game data and Folio notes. A dedicated writer role has only SELECT/INSERT/UPDATE access to that table. The existing source-data connection remains read-only. Same-origin JSON requests, size/field limits and server-side evidence ownership checks protect writes. A captured event reference is checked against the same client and character and keeps its original observed time.

Revision checks reject an older browser/device overwrite. The editor retains unsaved changes through background source refreshes, and edits made while a save is in flight remain drafts. The browser attempts to retain a recovery draft, with explicit restore/download controls. A revision mismatch requires downloading/merging the draft rather than silently overwriting server writing. Use Download current draft before leaving when saving is unavailable. Local browser storage may be unavailable or cleared, so it is not a replacement for saving to Nexus or downloading a draft.

### Exports

- Biography TXT: factual summary, personal writing, selected highlights and source references.
- Documentary outline: the same evidence plus a suggested chapter structure for making a video.
- Evidence JSON: summary, personal document, selected highlights, current journal page, coverage and cursor for earlier history. It is explicitly not a complete raw archive export.
- Print / PDF: use the browser print dialog to print the biography or save a PDF. This is browser printing, not an automatic video/PDF production service.

Exports include current unsaved edits when downloaded from the editor page. No gameplay footage, music or narrated video is generated.

### Capture health and launch checklist

`/adventures/health?client=forever` displays the latest received Omni file save, receipt time, normalization format, character observations, section statuses and journal-overflow warnings. Old captures are labelled older, not declared broken just because the player is offline. Individual sections retain their own timestamps and may be partial, unavailable or unobserved. Internal event-sequence gaps are shown in each character story's Evidence & coverage view as possible missing records, without guessing their contents.

The page includes the first-login acceptance checklist and troubleshooting steps: verify addon loading, play normally, save with reload/logout, allow the separate hidden sync up to five minutes, confirm normalized data and actual character milestones. It does not claim to inspect the Windows task or live game session from the website. Source revision notifications now watch both allowed client namespaces so Forever arrivals refresh the website automatically.

## Verified

Focused story-model checks cover terminal-death attribution, factual/personal separation in exports, documentary boundaries and invalid/oversized/conflicting highlight input. TypeScript checks and production builds pass. Live Retail biography reads used Nightchicken's existing 763 retained events, eight quest turn-ins, 32 successful encounters and 20 achievement events. A blank personal document was saved through the editor and its saved revision survived reload; no fictional backstory or events were written. The Forever health page correctly waits for its first saved capture. Live TXT, outline and JSON downloads return successfully. Missing-origin writes return 403 and stale-revision writes return 409. PostgreSQL confirms the story writer can update stories but cannot update captured character records or delete source snapshots.

## Remaining external checks

On November 4: actual Forever addon loading, event/API compatibility, performance and first real save through sync/import to these pages. Later, when Hardcore opens: actual mode/death behavior. No real Forever or Hardcore observations have been invented as substitutes. The existing OmniCapture 0.2.0 runtime remains installed; this delivery changes Nexus features, not addon capture behavior.

Deployment is through deploy-character-stories.py. Replaced sources and private web configuration are backed up under the server web-update-backups folder. Migration 022 is additive. No captured history, SavedVariables, crafting plans or source archives are deleted or edited. Keep the new story table when rolling back web source so personal writing is preserved.

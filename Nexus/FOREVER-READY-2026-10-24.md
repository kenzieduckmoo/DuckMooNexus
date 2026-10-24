# Forever preparation and expanded Omni coverage — October 24, 2026

## Delivered

DuckMooOmniCapture 0.2.0 is installed in both `_retail_/Interface/AddOns` and `_forever_/Interface/AddOns`. The Forever installation includes `DuckMooOmniCapture_Camelot.toc`, interface 16001 and `## Category: DuckMoo Media`. Installed client metadata identifies product wowf and executable 1.60.1.70532. This establishes the prepared target, not live addon compatibility. Other installed addons and all player SavedVariables remain intact; installed acknowledgement receipts are preserved.

The general collector stays independent of DuckMooCapture's crafting scanner. Retail-specific crafting/concentration addons are not silently relabeled as Forever-compatible.

## Independent data channels

The original Retail sync/task/config remains in place. The separate `DuckMoo Nexus Forever Sync` task runs invisibly every five minutes while the user is signed in. Its helper directory is `%LOCALAPPDATA%/DuckMooNexusForever`; it references the existing restricted transfer key and known-host configuration without generating credentials or exposing a public service.

Retail packets retain namespace `retail-main-account`; Forever uses `forever-main-account`. A state directory is bound to one namespace and refuses cross-client reuse. The server only accepts the two explicit namespaces. Receipt publication checks the expected namespace and infers the corresponding client's addon path from that client's SavedVariables folder.

Forever enrollment has a persistent minimum source-save time. Existing older/copied files are skipped; the collector waits for a newer stable game save. No Retail databases were copied into Forever. The first run returned success with status `awaiting_first_save`, zero packets and the Forever namespace. Its actual scheduled run was verified with LastTaskResult 0 and a fresh `awaiting_first_save` result. A packaged-app AppData redirection issue was resolved by running preparation in the normal Windows user context; the task uses Windows Script Host to launch PowerShell invisibly from the start, matching Retail and avoiding a flashing console. The launcher preserves the sync exit status for Task Scheduler. The Retail task's latest observed result remained 0.

The existing API workers use Retail API namespaces. Their candidate queries now explicitly restrict character, item-name and icon enrichment to Retail. Forever does not inherit Retail API profile lookups, item icons, character history or crafting links. Forever API imports require supported endpoints/client evidence later; no unsupported API connectivity is claimed.

## Website

- `/adventures`: Adventure Journal, with independent Retail/Forever and character selectors, event-kind filters, first-observed life summaries and loading of earlier archived events. Historical session, quest, loot and other Omni events are read from PostgreSQL after local journal rotation; earlier events are not limited to the addon's current queue.
- `/adventures?client=forever`: honest first-save waiting state, ready to populate automatically.
- `/characters?client=forever`: a separate Forever directory and automatic character-sheet routes. A new normalized Omni profile supplies a sheet without requiring a Retail API profile or Folio entry.
- Character sheets use newer available Omni equipment when an API equipment observation is absent or older. Item identity/links and readable item level are shown; absent detailed stats stay unknown. Artwork remains separately attributed to the API.
- Character Collections includes Omni mounts, owned pets, filtered toys and achievement points. Active quests and Storage observations appear under Progress. Every location/collection retains its own sample time and coverage limits.

## Expanded collection

Omni retains the earlier profile, currencies, vault, lockouts, keystone, equipment, carried bags, reputations, completed quest IDs and profession knowledge/resource observations.

New sections:

- **Life:** stable life ID, first observed time/level, highest observed level, configured mode, death count, last death and a terminal Hardcore death only when Hardcore mode was explicitly enabled. Events include life ID and cached level/location context with the context's original observation time.
- **Storage:** readable bank/warbank containers from exposed client enums, loaded mailbox headers/attachments, and naturally viewed readable guild-bank tabs. The addon does not open windows, switch tabs, send/collect mail or read mail bodies. Unready reads retain older observations; omitted/unvisited locations remain unknown. Legacy bank fallback is partial and does not invent container IDs.
- **Collections:** returned mount IDs/ownership, owned pet IDs/details where supported, visible filtered owned toys, and reported achievement points. Filters are not changed. Read loops are bounded, collection changes trigger refresh, and ordinary full collection reads are throttled for five minutes. This is not exhaustive appearance collection or achievement criteria coverage.
- **Activities:** readable active quest-log IDs/titles/frequency flags and objectives. Unaccepted daily/weekly activities and hidden world tasks are outside that partial snapshot.

These storage views are separate source observations. They are not added on top of Syndicator inventory or financial totals, so items and mail money are not double-counted.

## Hardcore use

On the appropriate character, `/dmomni hardcore on` explicitly enables Hardcore life recording; `/dmomni hardcore off` marks standard play. The change is journaled. Forever defaults to unconfirmed mode; Retail defaults to standard. No realm-name guess declares Hardcore eligibility. A normal death never closes a Hardcore life without the explicit setting. Duplicate death signals before resurrection are suppressed. A terminal observation is retained even if the setting changes later. A new character GUID receives a separate record.

Recording starts at first observation, not at an invented character creation time. Killer attribution/combat cause remain unknown; there is no unrestricted combat-log stream. This prepares the life recorder, but actual Hardcore rule/API behavior must still be observed when that mode becomes accessible.

## Verification and launch checks

Focused Lua 5.1 checks covered the existing capture contract, life modes, duplicate deaths, context timestamps, client detection, mount ownership beyond the eighth return value, pets/toys, quest objectives, bank separation, unreadable containers, mail attachments and independent sample times. Transfer checks covered first-save enrollment, strict/default namespace validation, explicit Forever acceptance and refusal to reuse another client's state. Existing acknowledgement checks passed. TypeScript checks and production builds passed.

Live checks cover separate client endpoints, real archived Retail events, the empty Forever state, existing character pages and PostgreSQL planning of the Retail-only worker queries. `verify-forever-ready.py` is read-only and makes no API calls or synthetic database writes. No synthetic character is presented as a real game observation.

Pending external evidence: activate the installed update with a normal Retail reload/login; save new observations, visit storage/collection views naturally and verify their real data. Forever login/save and final interface compatibility wait for access. Actual Hardcore events wait for that mode. Missing game evidence is not silently replaced with a mocked result.

## Release and recovery

Latest source is maintained in the Nexus aggregate and Omni's individual repository. The upload-ready addon is `releases/curseforge-ready-2026-10-24/DuckMooOmniCapture-0.2.0.zip`, with USER-GUIDE.txt and both client TOCs. Release archives contain an empty receipt stub and no player data or credentials. This is preparation for the user's CurseForge upload, not a publication claim.

Run `Prepare-Forever.ps1` in a normal Windows PowerShell user session, outside packaged-app AppData virtualization. It installs the relevant runtime, preserves installed receipts, backs up changed addon files and configures the separate task. Its backup directory is under `Nexus/forever-preparation/backups/`. Server source backups end in `-forever-ready`; the build log is `/home/kenzieduckmoo/forever-ready-deploy.log`. To disable only the new sync, disable `DuckMoo Nexus Forever Sync` in Task Scheduler; the original Retail task continues independently. Existing source archives and database history are retained.

API design references, separate from actual client verification: Blizzard-generated [bank documentation](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/BankDocumentation.lua) and [mount journal documentation](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/MountJournalDocumentation.lua). Installed client addon metadata and existing local collector implementations informed compatibility preparation; they do not substitute for a Forever login.

Final actual Windows task evidence: October 24, 2026, 11:34:29 UTC; task result 0, sync success, namespace `forever-main-account`, status `awaiting_first_save`, zero packets, and installed Forever runtime visible from the normal user context. Source backup for the final server update: `/opt/duckmoo-nexus-clean/web-update-backups/20261024T112015Z-forever-ready`.

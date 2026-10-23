# Omni Capture real-data follow-up — October 23, 2026

Seven real characters reached PostgreSQL through the existing secure SavedVariables sync: Nightchicken, Kenziemoo, Demonchick, Hammeredchic, Darayeda, Pandaquack and Stabbiechick. The latest archive includes carried bags/reputations for four; the remaining three were captured with the earlier loaded addon version. Profession knowledge, named currencies, vault tracks and activity events are present. This is partial roster coverage, not a full account census.

## Corrected after observing real data

WoW shutdown cleared several APIs before PLAYER_LOGOUT. Version 0.1.1 then overwrote profiles with zero equipped item level/money, and equipment/completed quests with empty values. Version 0.1.2 retains the last in-world sections, suspends scans during loading/shutdown and records a cached session-end profile with its own earlier observation timestamp. Successful scans no longer receive an erroneous API failure detail.

Normalizer 0.1.2-omni2 narrowly recognizes legacy zero profiles matching their retained session-end event. It recovers an earlier valid session profile, retains that earlier timestamp, marks partial/recovered coverage and records the source event ID. Matching logout equipment/quests become unavailable, not evidence of an empty character. Original archives/events and previous normalized observations remain retained; snapshot links are reconciled transactionally. The history endpoint excludes the identified terminal zero observations. No raw SavedVariables or archives are edited. The separate financial pipeline is unaffected; Omni wallet values are not added to financial totals.

Real sparse bag tables include null placeholders for empty slots. The website now ignores those placeholders instead of failing the entire character request. Session history understands the new cached session-end envelope.

## Verification and remaining boundary

Focused Lua 5.1 lifecycle/adapter checks reproduce teardown and verify retained section timestamps, cached end events, error detail handling and provenance-preserving legacy recovery. Read-only parsing of the real local capture recovered all seven nonzero item levels. All eight archived Omni snapshots were re-normalized on Nexus; PostgreSQL current profiles show seven recovered item levels and their original event references. The production website build succeeded. Addon 0.1.2 was installed into Retail without changing SavedVariables, and a preview ZIP was built. A later in-game load and save is still required to prove the corrected lifecycle with the actual client. Profession panels remain naturally observed; unvisited characters and unopened data are unknown.

# Omni Capture lifecycle correction — October 23, 2026

Real client observations exposed API teardown at PLAYER_LOGOUT and sparse bag placeholders. Version 0.1.2 retains the last in-world sections, suspends scans during loading/shutdown, and records session-end timestamps separately from cached profile observation timestamps. Successful reads no longer receive an erroneous API-failure detail.

Normalizer 0.1.2-omni2 recognizes legacy terminal zero profiles matching a retained session-end event. It recovers an earlier valid profile with the original observation timestamp and labels the recovery. Unknown shutdown equipment/quests remain unavailable. Raw archives, source events and earlier normalized records are preserved. Reprocessing reconciles snapshot links in a transaction; the financial pipeline is unchanged.

The website ignores empty bag-slot placeholders and excludes identified shutdown-zero observations from character history. Focused mocked lifecycle/adapter checks, the production build, and live website checks passed. The corrected addon is installed; a later client load and save is still required to verify its corrected lifecycle in game. Detailed gameplay observations and screenshots remain local and are excluded from this source report.

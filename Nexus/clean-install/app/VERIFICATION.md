# Verification — 2026-10-19 (America/Chicago)

## Actual source evidence

Read-only copies of the user's Retail account SavedVariables were tested locally. Personal input files are intentionally excluded from the deliverable ZIP.

| File | Bytes | SHA-256 | Records |
|---|---:|---|---:|
| Journalator.lua | 867861 | 2b126d44f2b6f99120d3939ded1db94839a434429e1fc635fb8ff075edd1b5f0 | 19581 |
| Journalator.lua.bak | 866040 | fa82fbdc27f953e001120fc919796477d3e655695e3e58e6efdb639e5337c4a7 | 19555 |

Both files decoded with the installed Journalator LibDeflate and LibSerialize libraries: 27 stores each, 13 empty and 14 at Journalator Version 15. Every backup record has an identical location and payload in the current snapshot; the current file adds 26 records (9 invoices, 17 crafting-order fulfillment events).

Current coverage: 6,113 invoices; 4,052 postings; 2,918 loot-container events; 2,109 vendor events; 1,968 failed auctions; 1,681 fulfillments; 464 training costs; 225 quest events; 26 repairs; 19 sent mails; 4 taxis; 2 trades. Event timestamps span 2026-09-09 17:05:27 UTC through 2026-10-19 14:55:48 UTC. This describes the file, not complete live account activity.

## Verified locally

Python 3.14, Lupa 2.8 (Lua 5.1), psycopg 3.3.6, and a temporary PostgreSQL 17.6 instance on Windows were used. No SSH connection or remote deployment was performed.

- Migration 001 executes successfully on PostgreSQL 17.
- First import inserted 19,581 normalized records and 27 archives.
- Second import of identical bytes under a different filename returned `already_imported`, inserted zero records.
- A byte-different copy with an added newline inserted zero transactions and retained a second import with 19,581 provenance observations.
- Raw bytes read back from PostgreSQL exactly matched the input.
- Deliberately conflicting an existing payload hash caused the whole next import to roll back, including its import row.
- Executable input and truncated input were rejected.
- Two identical payloads at separate positions produced distinct record IDs.
- Actual backup-to-current PostgreSQL test: 19,555 inserted from backup, exactly 26 added from current, then zero on repeat.
- All six dashboard SQL queries executed successfully against PostgreSQL after replacing Grafana macros with equivalent test literals.
- Python compilation and Grafana JSON parsing passed.

## Remaining deployment checks

The Docker image build, Linux runtime, existing host credentials/network/permissions, and Grafana's actual import/rendering have not been verified. No claim is made that the supplied dashboard has been installed. No live WoW capture or reconciliation with the game's wallet was performed. Historical Journalator versions 1–14 are structurally accepted but were not present in these fixtures. Reordered/rebuilt archives require manual reconciliation. Concurrency is protected by an advisory lock but a concurrent stress test was not performed.

Use the reproducible scripts in `tests/` against a disposable PostgreSQL database and the supplied deployment instructions to finish host validation.

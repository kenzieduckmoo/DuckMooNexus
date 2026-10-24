# DuckMoo Nexus

A personal World of Warcraft data platform: independent addon capture → archived source files → PostgreSQL → the Nexus website, Crafting Desk and Grafana.

This repository contains the maintained source as of October 23, 2026. The native website, financial workspace, character sheets and crafting services are deployed on the existing private Nexus server. Omni Capture has real Retail observations and acknowledged journal rotation; coverage remains partial and it is not a completed life-history recorder.

## Source map

| Folder | Purpose |
|---|---|
| `Nexus/web/` | Next.js/React website: overview, auction search, character sheets, professions, crafting and financials |
| `Nexus/clean-install/app/` | SavedVariables adapters, source archival, PostgreSQL migrations, Blizzard API workers and Grafana dashboards |
| `Nexus/clean-install/` | Server/Windows setup, restricted SSH receiver and Compose service definitions |
| `Nexus/craft-engine/` | Internal Node crafting calculation worker |
| `CraftingDesk/` | Shared crafting models, profession guides, persistence and hosted/fallback interface |
| `AddOns/` | DuckMooCapture, DuckMooOmniCapture, Folio, Planner and Warband source |
| `Nexus/sync-0.3.0/` | Historical sync/upgrade implementation retained for continuity |
| `docs/` | Current status, source handling and historical project direction |

General character/activity collection stays separate from the crafting scanner. Each DuckMoo addon uses `## Category: DuckMoo Media`. Financial pages distinguish actual balances and recorded cash movement from crafting estimates. Listing disappearance is not proof of a sale, and a recorded boss kill is not proof of an active weekly lockout.

## Working with the source

For the website, install the pinned dependencies with `pnpm install --frozen-lockfile` in `Nexus/web`, then run `pnpm dev` or `pnpm build`. Database-backed pages need a private `DATABASE_URL`; browser code must never receive credentials. Use the read-only website database role.

The deployed server combines files that are maintained in separate folders here. Run `python tools/prepare-stack.py` to assemble an ignored `.build/stack/` directory containing the application, website and crafting engine in the expected server layout. This creates a source bundle only; it does not deploy, reset a database, generate credentials or copy personal game data.

**Do not run the historical clean-install script against the existing server as a routine update.** Its documented behavior includes replacing Nexus database/Grafana volumes. Current updates must preserve source archives, database history, saved plans and private environment files. See [current status](docs/CURRENT_STATUS.md) and the dated implementation notes before deploying.

## Private runtime data

Credentials, private keys, `.env` files, SavedVariables, source archives, database dumps, saved crafting plans, generated `local-data.json`, logs and installed dependencies are deliberately excluded. They remain in their existing private locations. Required vendored decoder libraries are included with their licenses; game-art attribution is in `Nexus/web/ASSETS.md`.

The dated notes include historical claims and planned work. They are context, not current deployment instructions or proof that every item is complete. Real game capture/scanner checks remain distinct from automated source checks and server/browser verification.

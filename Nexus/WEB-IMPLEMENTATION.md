# Nexus website implementation — October 23, 2026

User authorized a real Nexus website using Next.js/React, shadcn, Motion and a
polished custom design. This pass builds home and Auction House first. Grafana
dashboards are separate; no character-sheet pages existed before this pass and
none are claimed delivered by this release.

## Delivered source and services

- Nexus/web: application, navigation, design system, home, AH, charts and watchlist.
- Nexus/clean-install/compose.web.yaml: private-address web service, default HTTP
  port, dedicated read-only database role, automatic restart, no separate login.
- item_media.py / api_worker.py: bounded official icon enrichment in PostgreSQL.
- Migration 12, item_cache.py, tsm_item_adapter.py, source_importer.py: normalize
  TSM item name/quality evidence without changing financial adapter versions.
- backfill_tsm_items.py: latest preserved TSM only; normalized 20,801 item-name
  rows from snapshot 1165. Historical packets/SavedVariables/plans untouched.

## Live evidence

Initial production website was built/deployed successfully on Nexus. Live reads
returned 58 characters, 32 characters with profession records, 14 market scopes,
798,045 listings and 23,753 named catalog items before the TSM name backfill.
Counts naturally change with imports. Initial HTTP request times were 0.18s
(overview), 0.08s (Eversinging Dust search), 0.03s (market scopes).

Browser confirmed official Eversinging Dust icons, two distinct item IDs/prices,
nine real collected price-history points, stock context, TSM estimates and
working navigation. Watchlist survived page reload; temporary verification watch
was then removed. Source/image credits are in web/ASSETS.md.

The quality follow-up also replaces the old 400-point bank limit with hourly
latest actual records over 90 days. A final component build caught a Windows
text-encoding issue; corrected the edited file to UTF-8. Existing preview stayed
live during the correction. Final production build and API/browser checks must
be recorded below before release handoff.

## Scope boundaries and next work

Home and AH are the delivered foundation. Crafting Desk is linked and still
runs at :8765. Full visual integration and actual character-sheet pages remain
next work, followed by deeper item/crafting workflows. No extra scope was moved
into Grafana. The game scanner lifecycle and laptop plan-save confirmation from
the prior Crafting Desk release remain external gates for that release.

## Final verification

Final production build and TypeScript succeeded after the encoding correction.
Live quality-aware search returned Eversinging Dust 243599/quality 1 and
243600/quality 2 at distinct recorded prices. Item detail returned quality 2 and
nine actual history points. Overview returned 299 hourly recorded bank points
and 30,141 named items after the TSM backfill (counts are snapshot-specific).
Request times were 0.22s search, 0.16s overview and 0.03s item history. Invalid
variant input returns 400; unrelated Host returns 403. Dedicated web role has no
write grants; neither credentials nor arbitrary SQL are exposed to the browser.

The final UTF-8 source package is nexus-web-current.tar.gz; deploy-web.py is the
consolidated update helper for the existing configured Nexus stack. Earlier
release/polish archives and finish-web.py are intermediate historical artifacts,
not the current deployment input. Runtime private environment files stay on Nexus.

Browser final review confirmed explicit Quality 1 / Quality 2 search labels,
selected item prices/history and final home counts. Export history action was
invoked without a browser error. Final previews are saved in web-verification/
(home.png and auction-house.png). The website is available without desktop
hosting or a separate login at http://10.20.30.239/.

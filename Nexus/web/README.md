# DuckMoo Nexus web — first release

Live home: http://10.20.30.239/
Auction House: http://10.20.30.239/auctions

This is the actual Nexus website. Crafting Desk remains a separately hosted
workspace linked from its navigation. Character-sheet pages are not built yet.

## Delivered

- Next.js 16 / React 19 application, official shadcn button/input/badge components,
  Tailwind 4, Motion with reduced-motion support, Recharts and Lucide.
- Custom dark/gold Nexus identity, Silvermoon hero, responsive navigation and
  layouts, real loading/error states, accessible labels and keyboard focus.
- Home: recorded warbank balance, up to 90 days of hourly latest recorded bank
  samples, real roster/item/listing counts, source timestamps and workspace links.
  Bank balance movement is not presented as profit.
- AH: name or exact item-ID search, 14 imported market scopes, result sorting,
  quality labels when evidenced, exact item selection, listing-variant selection,
  24h/7d/30d price history, CSV export, inventory context and TSM regional activity.
- Watchlist persists in this browser only. Shareable item URLs preserve the
  selected item/search/market. No fabricated listings, history, stock or sales.

## Data and boundaries

The server reads PostgreSQL through a separate read-only role. No database/API
credentials reach the browser. The service binds only the private Nexus address;
Host checks reject unrelated hostnames. Existing Grafana, data API, sync and
Crafting Desk services retain their roles and addresses.

AH responses distinguish fetched and source-modified times. A disappearing listing
is not proof of a sale. All-variant quotes are explicit; choose a listing variant
for a matching history. Unknown prices remain unknown. Search returns up to 80
listed results from the first 500 matching names; narrow broad searches.

Blizzard item media is cached incrementally by the API worker; unavailable icons
use a generic item symbol. TSM v19 item names and quality evidence are normalized
from the preserved source into PostgreSQL (migration 12); only the latest TSM
snapshot was backfilled. Raw source history remains intact. Conflicting quality
evidence yields an unknown quality instead of an invented rank.

## Runtime and updates

Source is deployed under /opt/duckmoo-nexus-clean/web. The service uses
compose.web.yaml, image duckmoo-nexus-web and private root-owned web.env. Never
commit or include that environment file in a handoff. The Docker build uses the
committed pnpm lockfile; the runtime is unprivileged and restarts automatically.

The initial deployment and quality update preserve backups under
/opt/duckmoo-nexus-clean/web-update-backups. Stop or roll back only the web service
when needed; do not run the clean installer or remove database volumes.

Local source is Nexus/web. `pnpm build` builds/checks the app. `pnpm dev` is for
local development and requires a suitable read-only DATABASE_URL to load real
data. The deployed app needs no desktop process. See ASSETS.md for asset credits.

## Verification

Production builds and TypeScript passed. Real endpoints were checked against the
live PostgreSQL data. Browser review covered home navigation, item-name search,
quality-specific item selection, chart rendering and watchlist save/refresh.
The final verification record is in ../WEB-IMPLEMENTATION.md.

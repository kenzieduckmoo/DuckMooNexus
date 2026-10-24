# Current status — October 24, 2026

The native Nexus website is deployed on the private server with Overview, named-item Auction House, dedicated character sheets, hosted Crafting Desk, Financials, Professions and the reagent buying advisor. Game-file sync, source archives, PostgreSQL normalization and scheduled official API imports supply the views. Grafana remains available separately.

## Latest completed work

- Reagent buying advisor at `/auctions/buying`: recurring commodity purchases, current price, separate quality cards, recorded stock, conditional 7/14-day top-ups and evidence-gated weekday patterns. Item API enrichment now fills classifications even for items already named by addon data and preserves cached icons.
- Character history retains the newest bounded API observations before chronological display; fixed history text encoding. All retained Folio/Planner/Omni source archives inspected at this checkpoint were normalized already, so no replay was needed.
- Comprehensive USER-GUIDE.txt documents bundled with six individual CurseForge upload ZIPs. Every owned TOC uses DuckMoo Media. Current source, guides and category are uploaded to each addon's individual GitHub repository, with older remote history and unrelated files retained. The three new collector/planner repositories are private; existing visibility remains unchanged.
- Existing installed addons have the guides/category updates. Fia's current repository version 0.1.2 replaces the older installed copy. Original files were backed up; player SavedVariables and Omni receipts were not rewritten.

The final crafting freshness race is fixed: the model tracks completed usable source imports instead of the largest raw archive ID. Deployment and actual observation agreement are recorded in Nexus/CRAFTING-FRESHNESS-2026-10-24.md.

## Remaining checks and future work

Actual Capture 0.9.0 completed whole-quality scans and cached reuse have now been observed, along with Omni 0.1.4 concentration discovery and matching hosted resource observations. Full controlled game transitions and Folio/Planner context edge cases remain separate client checks. Actual-client earlier Omni capture, logout preservation and acknowledged journal rotation have been observed. Laptop page loading and hosted persistence were checked; the user's actual laptop save/refresh remains a separate gate.

Weekday buying patterns await enough automatically accumulated history. Forever-specific game access and verification wait until November 4. Hardcore life capture must be ready before the expected January/February start; exact date remains unannounced in the project brief. Deeper profession-guide optimization remains paused. The entire long-term Nexus vision is not declared complete by this checkpoint.

Details: [pre-Forever checkpoint](../Nexus/PRE-FOREVER-STATUS-2026-10-24.md), [buying advisor](../Nexus/BUYING-ADVISOR-2026-10-24.md), [backlog](../Nexus/BACKLOG.md), and CraftingDesk/EXECUTION-LEDGER.md. Earlier dated documents retain their historical evidence and may be superseded by this status.

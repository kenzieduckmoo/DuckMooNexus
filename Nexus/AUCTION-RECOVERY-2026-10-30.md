# Auction import recovery - October 30, 2026

The collector stopped progressing after an Illidan API response fetched October 25 at 01:00 UTC contained two identical repeated auction IDs. Direct COPY violated the listing primary key. The failed response was correctly retained, but pending replay ran outside per-response error handling and aborted every subsequent worker run before fresh markets could be fetched. Other scopes last succeeded at approximately 01:00 UTC on October 25.

The importer now collapses exactly identical listings by auction ID before insertion, and snapshot auction_count reflects the unique listings. Different IDs remain separate. Conflicting duplicate contents reject the response instead of guessing a price. Raw compressed responses are retained unchanged. Transactions still roll back failed imports.

Pending response replay isolates individual failures. Invalid saved data is renamed rejected for inspection, while transient failures remain pending for retry. Fresh scheduled collection continues independently. No auction history or source archives are deleted.

Three targeted regression checks cover duplicate handling and conflicting prices, continuation after an invalid pending response, and retention of transient failures. The worker image was rebuilt on Nexus and the scheduled service restarted. Live PostgreSQL verification confirmed all 14 scopes imported successfully between 15:47:56 and 15:48:47 UTC on October 30. Every latest snapshot was refreshed; the oldest Blizzard source update was 15:32:26 UTC. The website displayed Fetched Just now.

Existing schedule: the timer checks every five minutes; each successful market is eligible again after one hour. HTTP throttling and other failures retain their existing retry handling.

-- Cash movement follows the recorded event, without matching ambiguous auctions
-- or mistaking a deposit refund for new earnings. Unresolved mail/trades stay out.
CREATE OR REPLACE VIEW nexus.recorded_cash_events AS
 SELECT id,namespace,occurred_at,character,realm,component,
  income_copper,expense_copper,internal_transfer_copper AS deposit_movement_copper,
  CASE WHEN income_copper IS NOT NULL AND expense_copper IS NOT NULL
         AND internal_transfer_copper IS NOT NULL
       THEN income_copper-expense_copper+internal_transfer_copper END AS net_copper,
  uncertain_copper,evidence
 FROM nexus.financial_components;

CREATE OR REPLACE VIEW nexus.auction_deposit_events AS
 SELECT id,namespace,occurred_at,character,realm,item_name,quantity,
  CASE WHEN category='Posting' THEN 'posting'
       WHEN category='Invoices' THEN 'refund' ELSE subtype END AS event_kind,
  CASE WHEN category='Posting' AND payload->>'deposit' ~ '^[0-9]+$'
       THEN (payload->>'deposit')::numeric
       WHEN category='Invoices' THEN deposit_copper::numeric END AS deposit_copper
 FROM nexus.transactions
 WHERE category='Posting' OR (category='Invoices' AND subtype='seller')
    OR (category='Failures' AND subtype IN ('expired','cancelled'));

INSERT INTO nexus.schema_migrations(version) VALUES(6) ON CONFLICT DO NOTHING;

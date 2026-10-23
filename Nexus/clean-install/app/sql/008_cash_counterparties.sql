-- Explicit ownership decisions are kept apart from immutable transaction records.
CREATE TABLE IF NOT EXISTS nexus.cash_counterparty_decisions (
 namespace text NOT NULL,character_name text NOT NULL,realm text NOT NULL,
 ownership text NOT NULL CHECK(ownership IN ('own_account','own_other_account','external')),
 evidence text NOT NULL,recorded_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(namespace,character_name,realm)
);
CREATE UNIQUE INDEX IF NOT EXISTS cash_counterparty_identity ON nexus.cash_counterparty_decisions
 (namespace,lower(character_name),regexp_replace(lower(realm),'[[:space:][:punct:]]','','g'));

CREATE OR REPLACE VIEW nexus.cash_transfer_classification AS
 WITH transfers AS MATERIALIZED (
  SELECT id,namespace,occurred_at,character,realm,category,
   CASE WHEN category='BasicMailSent' THEN payload->>'recipient'
        ELSE coalesce(payload->>'playerName',payload->>'target',payload->>'recipient') END AS counterparty,
   CASE WHEN category='BasicMailSent' THEN -(payload->>'money')::numeric
        ELSE (payload->>'moneyIn')::numeric-(payload->>'moneyOut')::numeric END AS cash_copper
  FROM nexus.transactions WHERE category IN ('BasicMailSent','Trades')
 ), named AS (
  SELECT *,split_part(counterparty,'-',1) AS counterparty_name,
   CASE WHEN position('-' IN counterparty)>0 THEN substring(counterparty FROM position('-' IN counterparty)+1)
        ELSE realm END AS counterparty_realm
  FROM transfers WHERE cash_copper<>0
 )
 SELECT n.*,coalesce(d.ownership,CASE WHEN EXISTS(
  SELECT 1 FROM nexus.character_roster r WHERE r.namespace=n.namespace
   AND lower(r.name)=lower(n.counterparty_name)
   AND regexp_replace(lower(r.realm),'[[:space:][:punct:]]','','g')=
       regexp_replace(lower(n.counterparty_realm),'[[:space:][:punct:]]','','g')
 ) THEN 'own_account' ELSE 'unresolved' END) AS ownership,
 coalesce(d.evidence,'Captured character roster; unmatched names remain unresolved') AS ownership_evidence
 FROM named n LEFT JOIN nexus.cash_counterparty_decisions d
 ON d.namespace=n.namespace AND lower(d.character_name)=lower(n.counterparty_name)
 AND regexp_replace(lower(d.realm),'[[:space:][:punct:]]','','g')=
     regexp_replace(lower(n.counterparty_realm),'[[:space:][:punct:]]','','g');

-- A resolved external payment now contributes to cash flow. Internal movements
-- remain excluded. Neither absence from the roster nor a name guess means external.
CREATE OR REPLACE VIEW nexus.cash_financial_components AS
 WITH transfers AS MATERIALIZED(SELECT * FROM nexus.cash_transfer_classification)
 SELECT f.id,f.namespace,f.occurred_at,f.character,f.realm,f.category,f.subtype,f.item_name,
 CASE WHEN t.ownership='external' THEN 'external '||CASE WHEN f.category='BasicMailSent' THEN 'mail payment' ELSE 'trade payment' END
      WHEN t.ownership IN ('own_account','own_other_account') THEN 'own character transfer'
      ELSE f.component END AS component,
 CASE WHEN t.ownership='external' THEN greatest(t.cash_copper,0) ELSE f.income_copper END AS income_copper,
 CASE WHEN t.ownership='external' THEN greatest(-t.cash_copper,0) ELSE f.expense_copper END AS expense_copper,
 f.internal_transfer_copper,
 CASE WHEN t.ownership IN ('external','own_account','own_other_account') THEN 0 ELSE f.uncertain_copper END AS uncertain_copper,
 coalesce(t.ownership_evidence,f.evidence) AS evidence,f.order_type,f.has_crafter_materials
 FROM nexus.financial_components f LEFT JOIN transfers t
 ON t.id=f.id AND f.component IN ('mail money, ownership unresolved','trade money, ownership unresolved');

CREATE OR REPLACE VIEW nexus.recorded_cash_events AS
 SELECT id,namespace,occurred_at,character,realm,component,income_copper,expense_copper,
 internal_transfer_copper AS deposit_movement_copper,
 CASE WHEN income_copper IS NOT NULL AND expense_copper IS NOT NULL AND internal_transfer_copper IS NOT NULL
      THEN income_copper-expense_copper+internal_transfer_copper END AS net_copper,
 uncertain_copper,evidence FROM nexus.cash_financial_components;

INSERT INTO nexus.schema_migrations(version) VALUES(8) ON CONFLICT DO NOTHING;

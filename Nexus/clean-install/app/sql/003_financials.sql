-- Recorded cash components, never item value, listing value, or crafted profit.
CREATE OR REPLACE VIEW nexus.financial_components AS
 WITH base AS (
  SELECT id,namespace,occurred_at,character,realm,category,subtype,item_name,payload,
   invoice_value_copper AS invoice,auction_fee_copper AS commission,deposit_copper AS refund,
   (payload->>'money')::numeric AS money,
   (payload->>'unitPrice')::numeric AS unit_price,quantity,
   (payload->>'tipAmount')::numeric AS tip,(payload->>'consortiumCut')::numeric AS cut
  FROM nexus.transactions
 )
 SELECT b.id,b.namespace,b.occurred_at,b.character,b.realm,b.category,b.subtype,b.item_name,
  c.component,c.income_copper,c.expense_copper,c.internal_transfer_copper,c.uncertain_copper,c.evidence,
  b.payload->>'orderType' AS order_type,
  (b.payload->>'crafterReagents' IS NOT NULL AND b.payload->'crafterReagents' <> '{}'::jsonb) AS has_crafter_materials
 FROM base b CROSS JOIN LATERAL (
  SELECT 'auction sale'::text,invoice,commission,0::numeric,0::numeric,'recorded invoice'::text
   WHERE category='Invoices' AND subtype='seller'
  UNION ALL SELECT 'auction purchase',0,invoice,0,0,'recorded invoice' WHERE category='Invoices' AND subtype='buyer'
  UNION ALL SELECT 'auction deposit refund',0,0,refund,0,'deposit principal returned; not new income'
   WHERE category='Invoices' AND subtype='seller' AND refund IS NOT NULL
  UNION ALL SELECT 'auction deposit paid',0,0,-(payload->>'deposit')::numeric,0,'deposit principal committed; losses not matched'
   WHERE category='Posting' AND payload ? 'deposit'
  UNION ALL SELECT 'vendor sale',unit_price*quantity,0,0,0,'recorded unit price times quantity'
   WHERE category='Vendoring' AND subtype='sell'
  UNION ALL SELECT 'vendor purchase',0,unit_price*quantity,0,0,'recorded unit price times quantity'
   WHERE category='Vendoring' AND subtype IN ('buy','purchase')
  UNION ALL SELECT 'quest reward',(payload->>'rewardMoney')::numeric,0,0,0,'recorded quest reward'
   WHERE category='Questing' AND payload->>'state'='turned in'
  UNION ALL SELECT 'cache or loot container',money,0,0,0,'recorded container money'
   WHERE category='LootContainers'
  UNION ALL SELECT 'crafting order commission',tip,cut,0,0,'recorded commission less consortium cut; material cost excluded'
   WHERE category='Fulfilling'
  UNION ALL SELECT 'repairs',0,money,0,0,'recorded personal repair bill' WHERE category='VendorRepairs'
  UNION ALL SELECT 'training',0,money,0,0,'recorded training cost' WHERE category='TrainingCosts'
  UNION ALL SELECT 'taxi',0,money,0,0,'recorded taxi cost' WHERE category='Taxis'
  UNION ALL SELECT 'mail postage',0,(payload->>'sendCost')::numeric,0,0,'recorded postage'
   WHERE category='BasicMailSent'
  UNION ALL SELECT 'mail money, ownership unresolved',0,0,0,-money,'excluded from income and expenses until recipient ownership resolved'
   WHERE category='BasicMailSent' AND money<>0
  UNION ALL SELECT 'trade money, ownership unresolved',0,0,0,
   (payload->>'moneyIn')::numeric-(payload->>'moneyOut')::numeric,'excluded until counterparty ownership resolved'
   WHERE category='Trades'
 ) AS c(component,income_copper,expense_copper,internal_transfer_copper,uncertain_copper,evidence);

CREATE OR REPLACE VIEW nexus.financial_coverage AS
 SELECT namespace,category,count(*) AS records,min(occurred_at) AS first_record,max(occurred_at) AS last_record,
 count(*) FILTER (WHERE NOT EXISTS (SELECT 1 FROM nexus.financial_components f WHERE f.id=t.id)) AS unclassified_records
 FROM nexus.transactions t GROUP BY namespace,category;
INSERT INTO nexus.schema_migrations(version) VALUES(3) ON CONFLICT DO NOTHING;

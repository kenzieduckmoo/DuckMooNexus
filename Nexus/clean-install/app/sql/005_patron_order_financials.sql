-- Completed orders only. Capture provides recipe -> profession evidence, not earnings.
-- Extract the tiny lookup once. Re-reading large toasted Capture JSON for every
-- panel made a single dashboard aggregate take tens of seconds on the live host.
CREATE TABLE IF NOT EXISTS nexus.recipe_profession_evidence (
 observation_id text PRIMARY KEY REFERENCES nexus.crafting_observations(id) ON DELETE CASCADE,
 namespace text NOT NULL,recipe_id bigint NOT NULL,profession text NOT NULL
);
CREATE TABLE IF NOT EXISTS nexus.recipe_profession_labels (
 namespace text NOT NULL,recipe_id bigint NOT NULL,profession text,
 PRIMARY KEY(namespace,recipe_id)
);
CREATE OR REPLACE FUNCTION nexus.capture_profession_name(payload jsonb)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$
 SELECT coalesce(nullif(payload #>> '{profession,parentProfessionName}',''),
                 nullif(payload #>> '{profession,baseName}',''),
                 nullif(payload #>> '{profession,professionName}',''))
$$;
CREATE OR REPLACE FUNCTION nexus.record_recipe_profession()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE name text;
BEGIN
 name := nexus.capture_profession_name(NEW.payload);
 IF name IS NOT NULL THEN
  INSERT INTO nexus.recipe_profession_evidence VALUES(NEW.id,NEW.namespace,NEW.recipe_id,name)
  ON CONFLICT DO NOTHING;
  INSERT INTO nexus.recipe_profession_labels VALUES(NEW.namespace,NEW.recipe_id,name)
  ON CONFLICT(namespace,recipe_id) DO UPDATE SET profession=
   CASE WHEN nexus.recipe_profession_labels.profession=excluded.profession
        THEN excluded.profession ELSE NULL END;
 END IF;
 RETURN NEW;
END
$$;
CREATE OR REPLACE TRIGGER record_recipe_profession
 AFTER INSERT ON nexus.crafting_observations
 FOR EACH ROW WHEN (NEW.kind='catalog' AND NEW.recipe_id IS NOT NULL)
 EXECUTE FUNCTION nexus.record_recipe_profession();
INSERT INTO nexus.recipe_profession_evidence
 SELECT o.id,o.namespace,o.recipe_id,nexus.capture_profession_name(o.payload)
 FROM nexus.crafting_observations o
 WHERE o.kind='catalog' AND o.recipe_id IS NOT NULL
 AND NOT EXISTS(SELECT 1 FROM nexus.recipe_profession_evidence e WHERE e.observation_id=o.id)
 AND nexus.capture_profession_name(o.payload) IS NOT NULL
 ON CONFLICT DO NOTHING;
INSERT INTO nexus.recipe_profession_labels
 SELECT namespace,recipe_id,CASE WHEN count(DISTINCT profession)=1 THEN min(profession) END
 FROM nexus.recipe_profession_evidence GROUP BY namespace,recipe_id
 ON CONFLICT(namespace,recipe_id) DO UPDATE SET profession=excluded.profession;

CREATE OR REPLACE VIEW nexus.recipe_professions AS
 SELECT namespace,recipe_id,profession FROM nexus.recipe_profession_labels WHERE profession IS NOT NULL;

CREATE OR REPLACE VIEW nexus.crafting_order_financials AS
 WITH orders AS MATERIALIZED (
  SELECT id,namespace,occurred_at,character,realm,item_name,payload,
   CASE WHEN payload->>'recipeID' ~ '^[0-9]+$' THEN (payload->>'recipeID')::bigint END AS recipe_id,
   payload->>'orderType' AS order_type,
   CASE WHEN payload->>'tipAmount' ~ '^[0-9]+$' THEN (payload->>'tipAmount')::numeric END AS gross_copper,
   CASE WHEN payload->>'consortiumCut' ~ '^[0-9]+$' THEN (payload->>'consortiumCut')::numeric END AS cut_copper
  FROM nexus.transactions WHERE category='Fulfilling'
 )
 SELECT o.id,o.namespace,o.occurred_at,o.character,o.realm,o.item_name,o.recipe_id,o.order_type,
  CASE o.order_type WHEN '0' THEN 'Public' WHEN '1' THEN 'Guild'
   WHEN '2' THEN 'Personal' WHEN '3' THEN 'Patron' ELSE 'Unknown' END AS order_kind,
  coalesce(p.profession,'Unknown profession') AS profession,
  coalesce(o.character,'Unknown character') || ' - ' || coalesce(o.realm,'Unknown realm') AS character_key,
  o.gross_copper,o.cut_copper,o.gross_copper-o.cut_copper AS net_copper,
  o.gross_copper IS NOT NULL AND o.cut_copper IS NOT NULL AS gold_complete,
  coalesce(o.payload->'crafterReagents','{}'::jsonb) NOT IN ('{}'::jsonb,'[]'::jsonb,'null'::jsonb) AS supplied_materials
 FROM orders o LEFT JOIN nexus.recipe_professions p
 ON p.namespace=o.namespace AND p.recipe_id=o.recipe_id;

INSERT INTO nexus.schema_migrations(version) VALUES(5) ON CONFLICT DO NOTHING;

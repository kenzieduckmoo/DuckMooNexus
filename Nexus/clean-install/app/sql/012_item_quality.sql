CREATE TABLE IF NOT EXISTS nexus.item_quality_evidence (
 namespace text NOT NULL,item_id bigint NOT NULL,crafting_quality integer NOT NULL CHECK(crafting_quality BETWEEN 1 AND 5),
 snapshot_id bigint NOT NULL REFERENCES nexus.source_snapshots,source text NOT NULL,
 PRIMARY KEY(namespace,item_id,snapshot_id)
);
CREATE OR REPLACE VIEW nexus.item_qualities AS
 SELECT namespace,item_id,CASE WHEN count(DISTINCT crafting_quality)=1 THEN max(crafting_quality) END AS crafting_quality
 FROM nexus.item_quality_evidence GROUP BY namespace,item_id;
INSERT INTO nexus.schema_migrations(version) VALUES(12) ON CONFLICT DO NOTHING;

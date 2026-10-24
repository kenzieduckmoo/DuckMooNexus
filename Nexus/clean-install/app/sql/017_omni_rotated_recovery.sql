-- The raw archive and historical normalized events survive queue rotation.
CREATE OR REPLACE VIEW nexus.current_omni_records AS
 WITH latest AS (
  SELECT DISTINCT ON(namespace) id,namespace,source_saved_at,captured_at
  FROM nexus.source_snapshots WHERE source='DuckMooOmniCapture.lua'
   AND normalized_version IN('0.1.0-omni1','0.1.2-omni2','0.1.3-omni3')
  ORDER BY namespace,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC
 ) SELECT r.*,s.source_saved_at,s.captured_at FROM latest s
 JOIN nexus.snapshot_characters l ON l.snapshot_id=s.id
 JOIN nexus.character_records r ON r.id=l.observation_id;
INSERT INTO nexus.schema_migrations(version) VALUES(17) ON CONFLICT DO NOTHING;

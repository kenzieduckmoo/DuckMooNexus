"""Read-only live checks; report counts, never character identities or balances."""
import json,urllib.request,subprocess
get=lambda path:json.load(urllib.request.urlopen('http://10.20.30.239'+path,timeout=45))
board=get('/api/professions?days=30');craft=get('/api/crafting?view=init')
index={(c['guid'],str(p['id'])):p.get('concentration') for c in craft['characters'] for p in c['professions']}
pools=[r for r in board['rows'] if (r.get('concentration') or {}).get('source')=='DuckMoo Omni Capture']
matches=0;pending=0
for r in pools:
    pool=r['concentration'];other=index.get((r['guid'],str(r['id'])))
    if other and all(pool.get(k)==other.get(k) for k in ('amount','max','observedAt','currencyID')):matches+=1
    else:pending+=1
print(json.dumps({'board_omni_pools':len(pools),'matching_crafting_observations':matches,'pending_or_different_observation':pending}))
for path in ('/api/crafting?view=plan','/api/crafting?view=saved','/api/buying?days=30&horizon=7'):
    get(path);print(path.split('?')[0],path.split('view=')[-1] if 'view=' in path else 'advisor','OK')
sql="""WITH latest AS(SELECT id FROM nexus.source_snapshots WHERE source='DuckMooCapture.lua' AND normalized_version IS NOT NULL ORDER BY source_saved_at DESC NULLS LAST,id DESC LIMIT 1),
 records AS MATERIALIZED(SELECT o.* FROM latest s JOIN nexus.snapshot_crafting l ON l.snapshot_id=s.id JOIN nexus.crafting_observations o ON o.id=l.observation_id),
 outcomes AS MATERIALIZED(SELECT o.* FROM records o JOIN records d ON d.kind='scan_definition' AND d.character_guid=o.character_guid AND d.recipe_id=o.recipe_id AND d.payload->>'allocationMode'='whole-slot-quality' WHERE o.kind='scan_outcome'),
 split AS(SELECT o.id,a.value->>'dataSlotType',a.value->>'dataSlotIndex' FROM outcomes o CROSS JOIN LATERAL jsonb_each(o.payload->'allocations') a GROUP BY o.id,a.value->>'dataSlotType',a.value->>'dataSlotIndex' HAVING count(*)>1)
 SELECT json_build_object('whole_quality_outcomes',(SELECT count(*) FROM outcomes),'split_slots',(SELECT count(*) FROM split),
 'finished_whole_quality_scans',(SELECT count(*) FROM records WHERE kind='scan_status' AND payload->>'allocationMode'='whole-slot-quality' AND payload->>'state'='Finished'),
 'whole_quality_cache_hits',(SELECT coalesce(sum((payload->>'cacheHits')::int),0) FROM records WHERE kind='scan_status' AND payload->>'allocationMode'='whole-slot-quality'));"""
r=subprocess.run(['docker','compose','exec','-T','postgres','psql','-A','-t','-U','nexus','-d','nexus','-c',sql],text=True,capture_output=True,check=True)
summary=json.loads(r.stdout);print(json.dumps(summary));assert summary['split_slots']==0,'A split allocation appeared in a whole-quality scan'
assert summary['whole_quality_outcomes']>0 and summary['finished_whole_quality_scans']>0,'Awaiting actual whole-quality scans'

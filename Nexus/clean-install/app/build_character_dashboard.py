"""A useful view of the character data already captured by Folio and Planner."""
import json
from pathlib import Path
from build_dashboards import dashboard,panel,fixed_color,DS

db=dashboard('duckmoo-character-observatory','DuckMoo Nexus | Character Observatory',
 'Latest saved character details from Folio and Planner. History graphs use the date range; roster and details show the latest normalized source. Concentration is projected, not live.')
ns='namespace=${account:sqlstring}'
selected=ns+' AND character_guid=${character:sqlstring}'
character_order=('Rolla','Stormlesbian','Hammeredchic','Stabbiechick','Kenziemoo','Pandaquack',
 'Fearfulchick','Pandachicken','Kaidiellicia','Meepkin','Bloodchicken','Voidchicken','Kaissiriah',
 'Zaraevelina','Trunktix','Darayeda','Kyootchick','Risharika','Duckmoochick')
order='CASE name '+ ' '.join("WHEN '"+name+"' THEN "+str(i) for i,name in enumerate(character_order,1))+' ELSE 100 END,name,realm'
db['templating']['list'][0]['query']='SELECT DISTINCT namespace FROM nexus.character_roster ORDER BY 1'
db['templating']['list'].append(dict(name='character',label='Character',type='query',datasource=DS,
 query="SELECT name||' - '||realm AS __text,character_guid AS __value FROM nexus.character_roster WHERE "+ns+" ORDER BY "+order,
 refresh=1,current={'text':'Rolla - Malygos','value':'Player-104-0021EA6C'}))


def table(title,query,description='',height=8):
    return panel(db,title,query,description=description,width=24,height=height)


fixed_color(panel(db,'Captured characters','SELECT count(*) AS characters FROM nexus.character_roster WHERE '+ns,'stat',height=4),'text')
fixed_color(panel(db,'Recorded character level','SELECT level FROM nexus.character_roster WHERE '+selected,'stat',height=4),'blue')
table('Character overview',f'''SELECT name AS "Character",realm AS "Realm",class_name AS "Class",race AS "Race",faction AS "Faction",
 level AS "Level",round(item_level,2) AS "Item level",specialization AS "Specialization",hero_specialization AS "Hero specialization",
 role AS "Role"
 FROM nexus.character_roster WHERE {selected}''',height=4)
table('Where you left off',f'''SELECT zone AS "Zone",subzone AS "Location",guild AS "Guild",last_seen AS "Last seen",source_saved_at AS "File saved"
 FROM nexus.character_roster WHERE {selected}''',height=4)
table('Professions and expansion skills',f'''SELECT profession AS "Profession",expansion_skill AS "Expansion skill",
 skill AS "Skill",maximum AS "Maximum",recorded_recipes AS "Recipes shown",recipe_list_filtered AS "Recipe list filtered",
 observed_at AS "Observed" FROM nexus.character_professions WHERE {selected}
 ORDER BY CASE WHEN profession IN ('Cooking','Fishing','Archaeology') THEN 1 ELSE 0 END,
 CASE WHEN skill_line_id IN (SELECT skill_line_id FROM nexus.character_concentration WHERE {selected} AND NOT hidden) THEN 0 ELSE 1 END,
 profession,CASE WHEN recorded_recipes IS NOT NULL THEN 0 ELSE 1 END,observed_at DESC NULLS LAST,expansion_skill''',
 'Recipe counts reflect the filters active when captured; they are not guaranteed complete recipe ownership counts.')
table('Projected concentration',f'''SELECT profession AS "Profession",expansion AS "Expansion",
 sampled_amount AS "Recorded amount",projected_amount AS "Projected now",maximum AS "Maximum",observed_at AS "Sample time"
 FROM nexus.character_concentration WHERE {selected} AND NOT hidden ORDER BY profession,expansion''',
 'Projected from saved amount and recharge rate, capped at the recorded maximum. Assumes no unrecorded spending. Planned crafts/reservations are not deducted. Hidden Planner pools are omitted.',height=6)
table('Your patron reminders',f'''SELECT profession AS "Profession",expansion AS "Expansion",
 to_char(to_timestamp((payload #>> '{{patron,due}}')::double precision) AT TIME ZONE 'America/Chicago','YYYY-MM-DD') AS "Reminder day",
 to_timestamp((payload #>> '{{patron,lastDone}}')::double precision) AS "Last marked done",
 CASE payload #>> '{{patron,mode}}' WHEN 'four' THEN 'Every four days' ELSE 'Weekly' END AS "Schedule"
 FROM nexus.character_concentration WHERE {selected} AND NOT hidden AND payload ? 'patron' ORDER BY 3,profession''',
 'Your saved Planner reminders. A reminder day is not confirmation that new orders are currently available.',height=6)
table('Reputations',f'''SELECT payload->>'name' AS "Faction",(payload->>'renown')::integer AS "Renown",
 CASE WHEN payload ? 'renown' THEN 'Renown' ELSE CASE payload->>'reaction'
 WHEN '1' THEN 'Hated' WHEN '2' THEN 'Hostile' WHEN '3' THEN 'Unfriendly' WHEN '4' THEN 'Neutral'
 WHEN '5' THEN 'Friendly' WHEN '6' THEN 'Honored' WHEN '7' THEN 'Revered' WHEN '8' THEN 'Exalted' ELSE 'Unknown' END END AS "Standing",
 (payload->>'value')::numeric AS "Recorded progress",
 (payload->>'max')::numeric AS "Recorded maximum",(payload->>'accountWide')::boolean AS "Account-wide",
 observed_at AS "Captured" FROM nexus.current_character_records
 WHERE {selected} AND record_kind='reputation' ORDER BY "Renown" DESC NULLS LAST,"Faction"''',height=10)
table('Recorded specialization nodes',f'''SELECT p.profession AS "Profession",p.expansion_skill AS "Expansion skill",
 node.value->>'name' AS "Node",(node.value->>'rank')::integer AS "Rank",(node.value->>'max')::integer AS "Maximum",p.observed_at AS "Captured"
 FROM nexus.character_professions p CROSS JOIN LATERAL jsonb_each(coalesce(p.payload->'knowledge','{{}}'::jsonb)) node
 WHERE p.namespace=${{account:sqlstring}} AND p.character_guid=${{character:sqlstring}} ORDER BY 1,2,3''',height=10)
for field,title,label in [('level','Observed level history','Level'),('ilvl','Observed item-level history','Item level')]:
    query=f'''SELECT DISTINCT ON(r.observed_at) r.observed_at AS time,(r.payload->>'{field}')::numeric AS "{label}"
 FROM nexus.character_records r JOIN nexus.snapshot_characters l ON l.observation_id=r.id
 JOIN nexus.source_snapshots s ON s.id=l.snapshot_id
 WHERE r.namespace=${{account:sqlstring}} AND r.character_guid=${{character:sqlstring}}
 AND r.source='DuckMooFolio.lua' AND r.record_kind='profile' AND r.payload ? '{field}' AND $__timeFilter(r.observed_at)
 ORDER BY r.observed_at,s.source_saved_at DESC NULLS LAST,s.captured_at DESC,s.id DESC'''
    chart=panel(db,title,query,'timeseries',description='Recorded samples only. Archives cannot reconstruct character changes that were never captured.',height=8)
    fixed_color(chart,'blue')
table('Collection totals reported by Folio',f'''SELECT
 (payload #>> '{{collections,mounts}}')::integer AS "Mounts reported",
 (payload #>> '{{collections,pets}}')::integer AS "Pets reported",
 (payload #>> '{{collections,toys}}')::integer AS "Toys reported",
 (payload #>> '{{collections,achievementPoints}}')::integer AS "Achievement points reported",
 last_seen AS "Character last seen" FROM nexus.character_roster WHERE {selected}''',
 'Cached addon-reported totals, which may be incomplete. Account collection totals are not summed across characters.',height=5)
table('Recorded combat stats',f'''SELECT (payload #>> '{{stats,strength}}')::numeric AS "Strength",
 (payload #>> '{{stats,agility}}')::numeric AS "Agility",(payload #>> '{{stats,intellect}}')::numeric AS "Intellect",
 (payload #>> '{{stats,stamina}}')::numeric AS "Stamina",(payload #>> '{{stats,crit}}')::numeric AS "Critical strike %",
 (payload #>> '{{stats,haste}}')::numeric AS "Haste %",(payload #>> '{{stats,mastery}}')::numeric AS "Mastery %",
 (payload #>> '{{stats,movement}}')::numeric AS "Movement %",last_seen AS "Character last seen"
 FROM nexus.character_roster WHERE {selected}''',height=5)
table('Recorded talents',f'''SELECT talent.value->>'name' AS "Talent",(talent.value->>'rank')::integer AS "Rank",
 (talent.value->>'max')::integer AS "Maximum",talent.value->>'spellID' AS "Spell ID"
 FROM nexus.character_roster c CROSS JOIN LATERAL jsonb_each(coalesce(c.payload->'talents','{{}}'::jsonb)) talent
 WHERE c.namespace=${{account:sqlstring}} AND c.character_guid=${{character:sqlstring}} ORDER BY 1''',height=10)
table('Warband roster',f'''SELECT name AS "Character",realm AS "Realm",class_name AS "Class",level AS "Level",
 round(item_level,2) AS "Item level",specialization AS "Specialization",zone AS "Zone",last_seen AS "Last seen"
 FROM nexus.character_roster WHERE {ns} ORDER BY {order}''',height=12)
table('Cached inventory',f'''SELECT i.name AS item,i.crafting_quality AS crafting_rank,i.location,i.quantity,i.is_bound,i.item_id,
 i.snapshot_file_saved_at FROM nexus.inventory_totals i
 JOIN nexus.character_roster c ON c.namespace=i.namespace
 AND lower(regexp_replace(i.owner_key,'[^[:alnum:]]','','g'))=lower(regexp_replace(c.name||c.realm,'[^[:alnum:]]','','g'))
 WHERE i.namespace=${{account:sqlstring}} AND i.owner_kind='character' AND c.character_guid=${{character:sqlstring}}
 ORDER BY i.location,i.name,i.crafting_quality LIMIT 500''',
 'Cached character locations. File-save time is not an item observation time; search all owners in Warband Inventory.',height=10)

table('Data freshness',f'''WITH latest AS (
 SELECT DISTINCT ON(source) source,source_saved_at,normalized_version FROM nexus.source_snapshots
 WHERE {ns} AND source IN ('DuckMooFolio.lua','DuckMooPlanner.lua')
 ORDER BY source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC
), counts AS (
 SELECT source,count(*) AS records,count(DISTINCT character_guid) AS characters,max(observed_at) AS newest
 FROM nexus.current_character_records WHERE {ns} GROUP BY source
)
SELECT replace(l.source,'.lua','') AS "Source",c.records AS "Observations",c.characters AS "Characters",
 l.source_saved_at AS "Latest source file",c.newest AS "Newest observation",
 CASE WHEN l.normalized_version='0.5.0-characters1' THEN 'Imported' ELSE 'Awaiting normalization' END AS "Import status"
 FROM latest l LEFT JOIN counts c ON c.source=l.source ORDER BY l.source''',
 'File-save times and source observation times are separate. These counts describe normalized data, not live game access.',height=5)

for obj in db['panels']:
    if obj['title']=='Cached inventory':
        from table_display import format_table
        format_table(obj)
    if obj['type']=='table':
        obj['fieldConfig']['overrides'].append({'matcher':{'id':'byRegexp','options':'.*(%|Item level)$'},
            'properties':[{'id':'decimals','value':2}]})

out=Path(__file__).parent/'dashboard-seeds'
out.mkdir(exist_ok=True)
(out/'character-observatory.json').write_text(json.dumps(db,indent=2),encoding='utf-8')

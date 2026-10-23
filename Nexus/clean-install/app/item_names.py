"""Enrich a bounded number of missing market item names per collection tick."""
import json
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from psycopg.types.json import Jsonb


def enrich(conn,region,bearer,limit=200):
    # API items are global per region; duplicate account evidence is intentional.
    namespaces=[r[0] for r in conn.execute('SELECT DISTINCT namespace FROM nexus.source_snapshots')]
    ids=conn.execute('''SELECT DISTINCT a.item_id FROM nexus.latest_api_snapshots s
       JOIN nexus.auction_listings a ON a.snapshot_id=s.id
       WHERE s.region=%s AND NOT EXISTS(SELECT 1 FROM nexus.item_name_evidence n WHERE n.item_id=a.item_id)
       AND NOT EXISTS(SELECT 1 FROM nexus.api_item_metadata m WHERE m.region=%s AND m.item_id=a.item_id AND m.checked_at>now()-interval '7 days')
       ORDER BY a.item_id LIMIT %s''',(region,region,limit)).fetchall()
    count=0
    for (item_id,) in ids:
        url=f'https://{region}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{region}&locale=en_US'
        try:
            with urlopen(Request(url,headers={'Authorization':'Bearer '+bearer}),timeout=20) as response:
                payload=json.load(response)
        except HTTPError as exc:
            if exc.code!=404: raise
            exc.close();payload={'id':item_id,'not_found':True}
        with conn.transaction():
            conn.execute('''INSERT INTO nexus.api_item_metadata(region,item_id,payload,checked_at)
                VALUES(%s,%s,%s,now()) ON CONFLICT(region,item_id) DO UPDATE SET payload=excluded.payload,checked_at=excluded.checked_at''',
                (region,item_id,Jsonb(payload)))
            if payload.get('name'):
                for namespace in namespaces:
                    conn.execute('''INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source)
                        VALUES(%s,%s,%s,'Blizzard item API') ON CONFLICT DO NOTHING''',(namespace,item_id,payload['name']))
                count+=1
    return count

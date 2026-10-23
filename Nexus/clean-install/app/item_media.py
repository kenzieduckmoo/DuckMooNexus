"""Cache bounded, official item media for Nexus without exposing API credentials."""
from datetime import datetime,timezone
import json
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from psycopg.types.json import Jsonb

def enrich_media(conn,region,bearer,limit=40):
    ids=conn.execute('''SELECT DISTINCT c.item_id,
      CASE WHEN c.name ILIKE ANY(ARRAY['%%Eversinging%%','%%Mote of Light%%','%%Phoenix Oil%%']) THEN 0 ELSE 1 END AS priority
      FROM nexus.item_catalog c LEFT JOIN nexus.api_item_metadata m ON m.region=%s AND m.item_id=c.item_id
      WHERE NOT coalesce(m.payload ? '_nexus_media_checked',false)
      ORDER BY priority,c.item_id DESC LIMIT %s''',(region,limit)).fetchall()
    count=0
    for item_id,_ in ids:
        url=f'https://{region}.api.blizzard.com/data/wow/media/item/{item_id}?namespace=static-{region}&locale=en_US'
        try:
            with urlopen(Request(url,headers={'Authorization':'Bearer '+bearer}),timeout=12) as response:media=json.load(response)
        except HTTPError as exc:
            if exc.code!=404:raise
            exc.close();media={}
        icon=next((a['value'] for a in media.get('assets',[]) if a.get('key')=='icon'),None)
        payload={'id':item_id,'_nexus_icon':icon,'_nexus_media_checked':datetime.now(timezone.utc).isoformat()}
        conn.execute('''INSERT INTO nexus.api_item_metadata(region,item_id,payload,checked_at) VALUES(%s,%s,%s,now())
          ON CONFLICT(region,item_id) DO UPDATE SET payload=nexus.api_item_metadata.payload||excluded.payload''',(region,item_id,Jsonb(payload)))
        count+=bool(icon)
    return count

if __name__=='__main__':
    import os,psycopg
    from api_collect import token
    with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:print('Item icons cached:',enrich_media(conn,'us',token(),100))

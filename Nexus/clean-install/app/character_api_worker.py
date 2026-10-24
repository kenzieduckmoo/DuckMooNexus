"""Public character profile collection, matched to the captured character GUID.

Follows character links supplied by Blizzard; never requests protected account
access. Keeps changed responses and unavailable-status evidence in PostgreSQL.
"""
import argparse,hashlib,json,os,re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode,quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import psycopg
from psycopg.types.json import Jsonb
from api_collect import token

SECTIONS=('media','equipment','statistics','specializations','professions','reputations','titles','achievements','achievements_statistics','pvp_summary','mythic_keystone_profile','encounters','appearance','quests','collections')
def norm(value):return re.sub('[^a-z0-9]','',value.casefold())
def now():return datetime.now(timezone.utc)
def get(url,bearer,region):
    parts=urlsplit(url)
    if parts.scheme!='https' or parts.netloc!=region+'.api.blizzard.com':raise ValueError('Untrusted profile link')
    query=dict(parse_qsl(parts.query));query['locale']='en_US'
    url=urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(query),''))
    try:
        with urlopen(Request(url,headers={'Authorization':'Bearer '+bearer}),timeout=15) as r:
            raw=r.read(16*1024**2+1)
            if len(raw)>16*1024**2:raise ValueError('Oversized character response')
            payload=json.loads(raw);modified=r.headers.get('Last-Modified')
            return 200,payload,parsedate_to_datetime(modified) if modified else None
    except HTTPError as exc:
        status=exc.code;exc.close();return status,{},None
    except (URLError,TimeoutError):return 599,{},None

def persist(conn,namespace,guid,region,section,response,profile_at=None):
    status,payload,modified=response;stamp=now()
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    conn.execute('''INSERT INTO nexus.character_api_documents(namespace,character_guid,region,endpoint,
       first_fetched_at,last_checked_at,response_modified_at,status,payload_sha256,payload,profile_observed_at)
       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(namespace,character_guid,endpoint,status,payload_sha256)
       DO UPDATE SET last_checked_at=excluded.last_checked_at,response_modified_at=excluded.response_modified_at,profile_observed_at=excluded.profile_observed_at''',
       (namespace,guid,region,section,stamp,stamp,modified,status,digest,Jsonb(payload),profile_at))

def run(region='us',limit=8):
    with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
        if not conn.execute("SELECT pg_try_advisory_lock(hashtextextended('nexus-character-api',0))").fetchone()[0]:return
        jobs=conn.execute('''WITH identities AS (
          SELECT namespace,character_guid,name,realm,last_seen FROM nexus.character_roster
          UNION ALL SELECT namespace,character_guid,payload#>>'{data,name}',payload#>>'{data,realm}',observed_at FROM nexus.current_omni_records
          WHERE record_kind='omni_section' AND record_key='profile' AND payload#>>'{data,name}' IS NOT NULL AND payload#>>'{data,realm}' IS NOT NULL
          ), candidates AS(SELECT DISTINCT ON(namespace,character_guid) * FROM identities ORDER BY namespace,character_guid,last_seen DESC NULLS LAST)
          SELECT c.namespace,c.character_guid,c.name,c.realm,c.last_seen FROM candidates c
          LEFT JOIN nexus.character_api_refresh r ON r.namespace=c.namespace AND r.character_guid=c.character_guid
          WHERE c.namespace='retail-main-account' AND (r.next_attempt IS NULL OR r.next_attempt<=now() OR c.last_seen>r.last_addon_seen)
          ORDER BY (r.next_attempt IS NULL) DESC,c.last_seen DESC NULLS LAST,c.name LIMIT %s''',(limit,)).fetchall()
        if not jobs:return
        bearer=token()
        code,realm_index,_=get(f'https://{region}.api.blizzard.com/data/wow/realm/index?namespace=dynamic-{region}',bearer,region)
        if code!=200:raise RuntimeError('Realm index unavailable')
        realms={norm(r['name']):r['slug'] for r in realm_index.get('realms',[])}
        known_icons={r[0] for r in conn.execute("SELECT item_id FROM nexus.api_item_metadata WHERE region=%s AND payload ? '_nexus_media_checked'",(region,))}
        for namespace,guid,name,realm,seen in jobs:
            slug=realms.get(norm(realm))
            if not slug:response=(404,{},None)
            else:response=get(f'https://{region}.api.blizzard.com/profile/wow/character/{quote(slug)}/{quote(name.casefold())}?namespace=profile-{region}',bearer,region)
            if response[0]==200 and response[1].get('id')!=int(guid.rsplit('-',1)[1],16):response=(409,{},None)
            profile_at=datetime.fromtimestamp(response[1]['last_login_timestamp']/1000,timezone.utc) if response[0]==200 and response[1].get('last_login_timestamp') else None
            persist(conn,namespace,guid,region,'summary',response,profile_at)
            results={}
            if response[0]==200:
                profile=response[1];requests=[(k,profile[k]['href']) for k in SECTIONS if isinstance(profile.get(k),dict) and profile[k].get('href')]
                with ThreadPoolExecutor(max_workers=4) as pool:
                    fetched=pool.map(lambda pair:(pair[0],get(pair[1],bearer,region)),requests)
                    for section,result in fetched:persist(conn,namespace,guid,region,section,result,profile_at);results[section]=result
                # Follow only links actually advertised by the public summary.
                extra=[]
                for section in ('quests','collections','encounters'):
                    payload=results.get(section,(0,{},None))[1]
                    for key,value in payload.items():
                        if key=='_links' or not isinstance(value,dict) or not value.get('href'):continue
                        href=value['href']
                        if urlsplit(href).path.startswith('/profile/wow/character/'):
                            extra.append((section+'/'+key,href))
                with ThreadPoolExecutor(max_workers=4) as pool:
                    for section,result in pool.map(lambda pair:(pair[0],get(pair[1],bearer,region)),extra[:12]):persist(conn,namespace,guid,region,section,result,profile_at)
                equipment=results.get('equipment',(0,{},None))[1].get('equipped_items',[])
                with conn.transaction():
                    for item in equipment:
                        item_id=item.get('item',{}).get('id');label=item.get('name')
                        if item_id and label:conn.execute("INSERT INTO nexus.item_name_evidence(namespace,item_id,name,source) VALUES(%s,%s,%s,'Blizzard character equipment') ON CONFLICT DO NOTHING",(namespace,item_id,label))
                missing=[i.get('item',{}).get('id') for i in equipment if i.get('item',{}).get('id') not in known_icons]
                with ThreadPoolExecutor(max_workers=4) as pool:
                    for item_id,result in pool.map(lambda i:(i,get(f'https://{region}.api.blizzard.com/data/wow/media/item/{i}?namespace=static-{region}',bearer,region)),set(missing)-{None}):
                        if result[0]!=200:continue
                        icon=next((a.get('value') for a in result[1].get('assets',[]) if a.get('key')=='icon'),None)
                        conn.execute('''INSERT INTO nexus.api_item_metadata(region,item_id,payload,checked_at) VALUES(%s,%s,%s,now()) ON CONFLICT(region,item_id) DO UPDATE SET payload=nexus.api_item_metadata.payload||excluded.payload''',(region,item_id,Jsonb({'id':item_id,'_nexus_icon':icon,'_nexus_media_checked':now().isoformat()})))
                        known_icons.add(item_id)
            status=response[0];delay=timedelta(hours=4 if status==200 else 24 if status in (403,404,409) else 1)
            conn.execute('''INSERT INTO nexus.character_api_refresh VALUES(%s,%s,%s,%s,%s,%s)
              ON CONFLICT(namespace,character_guid) DO UPDATE SET last_attempt=excluded.last_attempt,next_attempt=excluded.next_attempt,last_addon_seen=excluded.last_addon_seen,status=excluded.status''',
              (namespace,guid,now(),now()+delay,seen,status))
            print(json.dumps({'character':name,'realm':realm,'profile_status':status,'sections':len(results)}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=8);a=p.parse_args();run(limit=max(1,min(100,a.limit)))

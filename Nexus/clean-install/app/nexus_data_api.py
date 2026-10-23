"""Read-only PostgreSQL access for Nexus pages and local clients.

Reuses existing Grafana login/session authorization; holds no admin credential.
No browser CORS access is enabled. Local clients use their own server-side proxy.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from urllib.parse import urlsplit,parse_qs
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import psycopg
from psycopg.rows import dict_row


def get_query(path,params):
    namespace=params.get('account',['retail-main-account'])[0]
    q=params.get('q',[''])[0]
    if len(q)>200 or len(namespace)>200:raise ValueError('Search is too long')
    limit=max(1,min(500,int(params.get('limit',['100'])[0])))
    if path=='/api/v1/items':
        return '''SELECT * FROM nexus.item_catalog WHERE namespace=%s
          AND (EXISTS(SELECT 1 FROM unnest(aliases) n WHERE strpos(lower(n),lower(%s))>0)
          OR item_id::text=%s) ORDER BY name,item_id LIMIT %s''',(namespace,q,q,limit)
    if path=='/api/v1/inventory':
        owner=params.get('owner',[''])[0]
        return ('''SELECT * FROM nexus.current_inventory WHERE namespace=%s
          AND (strpos(lower(coalesce(name,'')),lower(%s))>0 OR item_id::text=%s)
          AND (%s='' OR owner_key=%s) ORDER BY name,crafting_quality,owner_kind,owner_key,location,slot_key LIMIT %s''',
          (namespace,q,q,owner,owner,limit))
    if path=='/api/v1/market':
        item=int(params.get('item_id',['0'])[0])
        if not 0<item<10**18:raise ValueError('Choose an item first')
        region=params.get('region',['us'])[0]
        return '''SELECT p.*,c.name FROM nexus.latest_auction_prices p
          LEFT JOIN nexus.item_catalog c ON c.namespace=%s AND c.item_id=p.item_id
          WHERE p.region=%s AND p.item_id=%s ORDER BY scope,lowest_unit_copper LIMIT %s''',(namespace,region,item,limit)
    if path=='/api/v1/characters':
        return '''SELECT * FROM nexus.character_roster WHERE namespace=%s
          AND (strpos(lower(coalesce(name,'')),lower(%s))>0 OR character_guid=%s)
          ORDER BY name,realm LIMIT %s''',(namespace,q,q,limit)
    if path=='/api/v1/sources':
        return '''SELECT DISTINCT ON(source) source,source_saved_at,captured_at,normalized_version,
          CASE WHEN normalized_version IS NOT NULL THEN 'normalized'
               WHEN EXISTS(SELECT 1 FROM nexus.imports i WHERE i.namespace=s.namespace AND i.sha256=s.sha256)
               THEN 'Journalator specialized import' ELSE 'archived; adapter pending' END AS state
          FROM nexus.source_snapshots s WHERE namespace=%s
          ORDER BY source,source_saved_at DESC NULLS LAST,captured_at DESC,id DESC''',(namespace,)
    raise LookupError('Unknown endpoint')


class Handler(BaseHTTPRequestHandler):
    def send(self,status,body):
        raw=json.dumps(body,default=str,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(raw)))
        if status==401:self.send_header('WWW-Authenticate','Basic realm="DuckMoo Nexus"')
        self.end_headers();self.wfile.write(raw)
    def authorized(self):
        headers={name:self.headers[name] for name in ('Authorization','Cookie') if self.headers.get(name)}
        if not headers:return False
        request=Request(os.environ.get('GRAFANA_AUTH_URL','http://grafana:3000/api/user'),headers=headers)
        try:
            with urlopen(request,timeout=5) as response:
                user=json.load(response)
                return bool(user.get('id')) and not user.get('isAnonymous',False)
        except (HTTPError,URLError,ValueError):return False
    def do_GET(self):
        if not self.authorized():return self.send(401,{'error':'Sign in with your existing Nexus Grafana account.'})
        try:
            split=urlsplit(self.path);query,values=get_query(split.path,parse_qs(split.query,keep_blank_values=True))
            with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row,
                    options='-c default_transaction_read_only=on -c statement_timeout=10000') as conn:
                rows=conn.execute(query,values).fetchall()
            requested_limit=max(1,min(500,int(parse_qs(split.query).get('limit',['100'])[0])))
            self.send(200,{'version':1,'rows':rows,'returned':len(rows),'limit_max':500,
                'possibly_truncated':len(rows)>=requested_limit,
                'freshness_note':'File-save and API-fetch timestamps are distinct from source observation times.'})
        except LookupError:self.send(404,{'error':'Unknown endpoint'})
        except (ValueError,OverflowError):self.send(400,{'error':'Invalid query parameters'})
        except Exception:self.send(503,{'error':'Data query unavailable. Retry shortly.'})


if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',8080),Handler).serve_forever()

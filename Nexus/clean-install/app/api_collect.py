"""Blizzard Retail AH collection foundation. Listing changes never mean sales.

Keeps Last-Modified separate from fetch time; persists raw gzip before DB work.
Credentials remain in environment. Does not require or request player OAuth.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LIMIT = 512*1024**2


def now():
    return datetime.now(timezone.utc)


def source_time(headers):
    raw = headers.get('Last-Modified')
    if not raw:
        return None
    value = parsedate_to_datetime(raw)
    if value.tzinfo is None:
        raise ValueError('Last-Modified lacks timezone')
    return value.isoformat()


def endpoint(region, realm):
    if region not in ('us','eu','kr','tw'):
        raise ValueError('Unsupported region')
    if realm is not None and (type(realm) is not int or realm <= 0):
        raise ValueError('Connected-realm ID must be positive')
    path = f'connected-realm/{realm}/auctions' if realm else 'auctions/commodities'
    return f'https://{region}.api.blizzard.com/data/wow/{path}?' + urlencode({'namespace':'dynamic-'+region})


def token():
    pair = (os.environ['BLIZZARD_CLIENT_ID']+':'+os.environ['BLIZZARD_CLIENT_SECRET']).encode()
    request = Request('https://oauth.battle.net/token', data=b'grant_type=client_credentials',
                      headers={'Authorization':'Basic '+base64.b64encode(pair).decode(),
                               'Content-Type':'application/x-www-form-urlencoded'})
    with urlopen(request, timeout=30) as response:
        data = json.load(response)
    return data['access_token']


def collect(region, realm, archive, bearer, previous=None, opener=urlopen):
    url = endpoint(region, realm)
    scope = f'connected-realm:{realm}' if realm else 'commodities'
    headers = {'Authorization':'Bearer '+bearer, 'Accept':'application/json', 'Accept-Encoding':'identity'}
    if previous:
        if previous.get('etag'):
            headers['If-None-Match'] = previous['etag']
        elif previous.get('last_modified_header'):
            headers['If-Modified-Since'] = previous['last_modified_header']
    fetched = now().isoformat()
    archive = Path(archive); archive.mkdir(parents=True, exist_ok=True)
    metadata = dict(region=region,scope=scope,endpoint=url,fetched_at=fetched)
    try:
        response = opener(Request(url, headers=headers), timeout=90)
    except HTTPError as exc:
        if exc.code not in (304,429,503):
            raise
        metadata.update(status=exc.code,retry_after=exc.headers.get('Retry-After'))
        if previous and exc.code==304:
            metadata['previous_sha256'] = previous.get('sha256')
        exc.close()
        return metadata
    with response:
        if response.status != 200:
            raise ValueError('Unexpected AH response')
        metadata.update(status=200,source_modified_at=source_time(response.headers),
                        last_modified_header=response.headers.get('Last-Modified'),etag=response.headers.get('ETag'))
        fd,name = tempfile.mkstemp(prefix='.api-',dir=archive)
        try:
            h = hashlib.sha256(); size = 0
            with os.fdopen(fd,'wb') as out:
                with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0) as zipped:
                    while block := response.read(1024**2):
                        size += len(block)
                        if size > LIMIT:
                            raise ValueError('AH payload exceeds bound')
                        h.update(block); zipped.write(block)
                out.flush(); os.fsync(out.fileno())
            metadata.update(sha256=h.hexdigest(),raw_bytes=size)
            os.replace(name,archive/(h.hexdigest()+'.json.gz'))
        finally:
            if os.path.exists(name):
                os.unlink(name)
    return metadata


def ingest_api(conn, archive, meta):
    with conn.transaction():
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(meta['region']+':'+meta['scope'],))
        snapshot = None
        if meta['status']==200:
            raw = gzip.decompress((Path(archive)/(meta['sha256']+'.json.gz')).read_bytes())
            if hashlib.sha256(raw).hexdigest()!=meta['sha256']:
                raise ValueError('API archive checksum mismatch')
            body = json.loads(raw)
            auctions = body['auctions']
            if not isinstance(auctions,list):
                raise ValueError('Invalid auction array')
            snapshot = conn.execute('SELECT id FROM nexus.api_snapshots WHERE region=%s AND scope=%s AND sha256=%s AND source_modified_at IS NOT DISTINCT FROM %s::timestamptz',
                                    (meta['region'],meta['scope'],meta['sha256'],meta['source_modified_at'])).fetchone()
            if snapshot:
                snapshot=snapshot[0]
            else:
                snapshot = conn.execute('''INSERT INTO nexus.api_snapshots
                 (region,scope,endpoint,fetched_at,source_modified_at,last_modified_header,etag,sha256,raw_gzip,auction_count)
                 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id''',
                 (meta['region'],meta['scope'],meta['endpoint'],meta['fetched_at'],meta['source_modified_at'],
                  meta['last_modified_header'],meta['etag'],meta['sha256'],gzip.compress(raw,mtime=0),len(auctions))).fetchone()[0]
                with conn.cursor() as cur:
                    with cur.copy('COPY nexus.auction_listings FROM STDIN') as copy:
                        for auction in auctions:
                            item = auction['item']
                            copy.write_row((snapshot,auction['id'],item['id'],json.dumps(item),auction['quantity'],
                                            auction.get('unit_price'),auction.get('buyout'),auction.get('bid'),auction.get('time_left')))
        elif meta['status']==304:
            result=conn.execute('SELECT id FROM nexus.api_snapshots WHERE region=%s AND scope=%s AND sha256=%s ORDER BY fetched_at DESC LIMIT 1',
                                (meta['region'],meta['scope'],meta.get('previous_sha256'))).fetchone()
            snapshot=result[0] if result else None
        conn.execute('INSERT INTO nexus.api_polls(region,scope,fetched_at,status,snapshot_id,retry_after) VALUES(%s,%s,%s,%s,%s,%s)',
                     (meta['region'],meta['scope'],meta['fetched_at'],meta['status'],snapshot,meta.get('retry_after')))
    return snapshot


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--region',default='us');p.add_argument('--connected-realm',type=int)
    p.add_argument('--archive',type=Path,required=True);p.add_argument('--import-db',action='store_true')
    a=p.parse_args();a.archive.mkdir(parents=True,exist_ok=True)
    # Credentials are needed only when fetching. No credential values are logged.
    scope=str(a.connected_realm or 'commodities');state=a.archive/(a.region+'-'+scope+'-state.json')
    previous=json.loads(state.read_text()) if state.exists() else None
    meta=collect(a.region,a.connected_realm,a.archive,token(),previous)
    stamp=now().strftime('%Y%m%dT%H%M%S%fZ')
    (a.archive/(a.region+'-'+scope+'-'+stamp+'.json')).write_text(json.dumps(meta,indent=2))
    if a.import_db:
        import psycopg
        with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
            ingest_api(conn,a.archive,meta)
    # Update conditional-fetch checkpoint only after successful persistence/import.
    if meta['status']==200:
        temporary=state.with_suffix('.tmp');temporary.write_text(json.dumps(meta));os.replace(temporary,state)
    print(json.dumps(meta))


if __name__=='__main__':
    main()

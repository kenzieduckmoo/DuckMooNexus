"""Bounded scheduled AH imports with durable scope-specific retry state.

Run once per timer tick. Credentials are environment-only; never print HTTP
exceptions whose request headers might contain authorization information.
"""
import argparse
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import json
import os
from pathlib import Path
from urllib.error import HTTPError
import psycopg
from api_collect import collect, token, ingest_api
from item_names import enrich
from item_media import enrich_media


def retry_seconds(value, at):
    try:
        return max(60, int(value))
    except (ValueError, TypeError):
        try:
            return max(60, int((parsedate_to_datetime(value)-at).total_seconds()))
        except (ValueError, TypeError, OverflowError):
            return 900


def run(region, realms, archive):
    scopes = [('commodities', None)] + [(f'connected-realm:{r}', r) for r in sorted(set(realms))]
    with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True) as conn:
        locked = conn.execute("SELECT pg_try_advisory_lock(hashtextextended('nexus-api-worker',0))").fetchone()[0]
        if not locked:
            print('Another API worker is active.'); return
        # Retry metadata files whose raw responses were saved before a DB failure.
        archive.mkdir(parents=True, exist_ok=True)
        for pending in sorted(archive.glob('pending-*.json')):
            meta = json.loads(pending.read_text())
            ingest_api(conn, archive, meta)
            pending.rename(pending.with_name(pending.name.replace('pending-', 'imported-', 1)))
        bearer = None
        for scope, realm in scopes:
            at = datetime.now(timezone.utc)
            row = conn.execute('SELECT next_attempt FROM nexus.api_worker_status WHERE region=%s AND scope=%s', (region,scope)).fetchone()
            if row and row[0] > at: continue
            last = conn.execute('''SELECT sha256,etag,last_modified_header FROM nexus.api_snapshots
                WHERE region=%s AND scope=%s ORDER BY fetched_at DESC,id DESC LIMIT 1''', (region,scope)).fetchone()
            previous = dict(zip(('sha256','etag','last_modified_header'),last)) if last else None
            success = False; delay = 3600
            try:
                if bearer is None: bearer = token()
                meta = collect(region,realm,archive,bearer,previous)
                pending = archive/('pending-'+region+'-'+str(realm or 'commodities')+'-'+at.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
                temporary = pending.with_suffix('.tmp')
                temporary.write_text(json.dumps(meta)); temporary.replace(pending)
                ingest_api(conn,archive,meta)
                pending.rename(pending.with_name(pending.name.replace('pending-', 'imported-', 1)))
                status = str(meta['status']); success = meta['status'] in (200,304)
                if not success: delay = retry_seconds(meta.get('retry_after'),at)
                print(json.dumps({'scope':scope,'status':status,'snapshot_imported':success}),flush=True)
            except HTTPError as exc:
                status = 'http_'+str(exc.code)
                if exc.code in (401,403): delay = 3600; bearer = None
                else: delay = retry_seconds(exc.headers.get('Retry-After'),at)
                exc.close()
                print(json.dumps({'scope':scope,'status':status}),flush=True)
            except Exception as exc:
                status = 'error_'+type(exc).__name__
                print(json.dumps({'scope':scope,'status':status}),flush=True)
            conn.execute('''INSERT INTO nexus.api_worker_status(region,scope,last_attempt,last_success,next_attempt,status)
                VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(region,scope) DO UPDATE SET
                last_attempt=excluded.last_attempt,last_success=coalesce(excluded.last_success,nexus.api_worker_status.last_success),
                next_attempt=excluded.next_attempt,status=excluded.status''',
                (region,scope,at,at if success else None,at+timedelta(seconds=delay),status))
        try:
            if bearer is None: bearer=token()
            print(json.dumps({'names_enriched':enrich(conn,region,bearer)}),flush=True)
            print(json.dumps({'icons_enriched':enrich_media(conn,region,bearer)}),flush=True)
        except Exception as exc:
            print(json.dumps({'name_enrichment':'error_'+type(exc).__name__}),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--region',default='us')
    parser.add_argument('--connected-realms',default='')
    parser.add_argument('--archive',type=Path,required=True)
    args=parser.parse_args()
    run(args.region,[int(r) for r in args.connected_realms.split(',') if r.strip()],args.archive)

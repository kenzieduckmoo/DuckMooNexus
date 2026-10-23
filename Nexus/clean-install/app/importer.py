import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from decode import decode

VERSION = '0.1.0'
def canonical(x): return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(x): return hashlib.sha256(x).hexdigest()

def records(stores, namespace):
    for sid, encoded, data in stores:
        for category, entries in sorted(data.items()):
            if category == 'Version': continue
            if not isinstance(entries,dict): raise ValueError(f'Unexpected category {category}')
            if set(entries) != set(range(1,len(entries)+1)): raise ValueError('Non-contiguous record array')
            for ordinal,p in sorted(entries.items()):
                if not isinstance(p,dict): raise ValueError('Record must be a table')
                stamp=p.get('time')
                if type(stamp) is not int: raise ValueError('Missing/inexact timestamp')
                occurred=datetime.fromtimestamp(stamp,timezone.utc)
                source=p.get('source',{})
                link=p.get('itemLink','')
                match=re.search(r'(?:\|H|^)item:(\d+)',link)
                identity=[namespace,sid,category,ordinal]
                money=[]
                for key in ('value','consignment','deposit'):
                    v=p.get(key) if category=='Invoices' else None
                    if v is not None and (type(v) is not int or v<0): raise ValueError('Invalid invoice copper')
                    money.append(v)
                yield (digest(canonical(identity).encode()),namespace,sid,category,ordinal,
                    occurred,source.get('character'),source.get('realm'),source.get('faction'),
                    int(match[1]) if match else None,p.get('itemName'),p.get('count'),
                    p.get('invoiceType') or p.get('vendorType') or p.get('failedType'),
                    *money,digest(canonical(p).encode()),canonical(p))

def ingest(conn, raw, filename, namespace):
    # Decode and validate completely before any database writes.
    stores=list(decode(raw)); rows=list(records(stores,namespace))
    with conn.transaction():
        with conn.cursor() as cur:
            # Serializes imports for this namespace, including simultaneous uploads.
            cur.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace,))
            cur.execute('SELECT id FROM nexus.imports WHERE namespace=%s AND sha256=%s',(namespace,digest(raw)))
            existing=cur.fetchone()
            if existing: return dict(status='already_imported',import_id=existing[0],inserted=0,records=len(rows))
            cur.execute('INSERT INTO nexus.imports(namespace,sha256,filename,raw_file,importer_version) VALUES(%s,%s,%s,%s,%s) RETURNING id',
                        (namespace,digest(raw),filename,raw,VERSION))
            import_id=cur.fetchone()[0]
            for sid,encoded,data in stores:
                cur.execute('INSERT INTO nexus.archives VALUES(%s,%s,%s,%s::jsonb)',(import_id,sid,encoded,canonical(data)))
            inserted=0
            for row in rows:
                cur.execute('SELECT payload_sha256 FROM nexus.transactions WHERE id=%s',(row[0],))
                old=cur.fetchone()
                if old and old[0]!=row[-2]:
                    raise ValueError(f'Record changed at {row[2:5]}; entire import rolled back. Preserve the input for investigation.')
                if not old:
                    cur.execute('INSERT INTO nexus.transactions VALUES('+','.join(['%s']*17+['%s::jsonb'])+')',row)
                    inserted+=1
                cur.execute('INSERT INTO nexus.observations VALUES(%s,%s)',(import_id,row[0]))
    return dict(status='imported',import_id=import_id,inserted=inserted,records=len(rows),stores=len(stores))

def main():
    p=argparse.ArgumentParser(description='DuckMoo Nexus Journalator importer')
    p.add_argument('command',choices=['inspect','import','migrate'])
    p.add_argument('file',nargs='?')
    p.add_argument('--namespace',default='retail-main-account')
    args=p.parse_args()
    if args.command=='migrate':
        import psycopg
        with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=10) as conn:
            conn.execute((Path(__file__).parent/'sql/001_initial.sql').read_text())
        print('Migration 001 applied'); return
    if not args.file: p.error('file is required')
    path=Path(args.file)
    if path.stat().st_size>64*1024*1024: raise ValueError('64 MiB input limit exceeded')
    raw=path.read_bytes()
    if args.command=='inspect':
        stores=list(decode(raw)); rows=list(records(stores,args.namespace))
        print(json.dumps(dict(sha256=digest(raw),bytes=len(raw),stores=len(stores),
            empty_stores=sum(not d for _,_,d in stores),records=len(rows),
            categories=dict(Counter(r[3] for r in rows)),
            first=min(r[5] for r in rows).isoformat() if rows else None,
            last=max(r[5] for r in rows).isoformat() if rows else None),indent=2))
    else:
        import psycopg
        with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=10) as conn:
            print(json.dumps(ingest(conn,raw,path.name,args.namespace)))

if __name__=='__main__': main()


"""Archive first; normalize source-specific observations atomically on retry."""
import argparse
import gzip
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from financials import canonical, observations, ADAPTERS
from savedvariables import read_lua
from snapshots import MAX_BYTES, SOURCES
from extended_import import EXTENDED, normalize_extended
from character_adapter import CHARACTER_SOURCES,CHARACTER_VERSION
from inventory_adapter import INVENTORY_SOURCE,INVENTORY_VERSION,normalize_inventory
from tsm_item_adapter import ITEM_SOURCE,ITEM_VERSION,normalize_items
from character_extras import EXTRA_SOURCES,EXTRA_VERSION,normalize_extras
from omni_adapter import OMNI_SOURCE,OMNI_VERSION,normalize_omni

VERSION = '0.3.0'


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc) if value is not None else None


def verify_archive(archive, manifest):
    h = hashlib.sha256(); size = 0
    with gzip.open(archive, 'rb') as stream:
        while block := stream.read(1024**2):
            size += len(block)
            if size > MAX_BYTES:
                raise ValueError('Decompressed source exceeds limit')
            h.update(block)
    if size != manifest['raw_bytes'] or h.hexdigest() != manifest['sha256']:
        raise ValueError('Archive checksum/length mismatch')


def ingest_source(conn, archive, manifest, normalize=True):
    source, namespace = manifest['source'], manifest['namespace']
    version=CHARACTER_VERSION if source in CHARACTER_SOURCES else VERSION
    if source==INVENTORY_SOURCE:version=INVENTORY_VERSION
    if source==ITEM_SOURCE:version=ITEM_VERSION
    if source in EXTRA_SOURCES:version=EXTRA_VERSION
    if source==OMNI_SOURCE:version=OMNI_VERSION
    if source.removesuffix('.lua') not in SOURCES:
        raise ValueError('Unsupported source identity')
    verify_archive(archive, manifest)
    # Raw archival commits separately: parser failure must not lose source data.
    with conn.transaction():
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (namespace + ':' + source,))
        row = conn.execute('SELECT id,normalized_version FROM nexus.source_snapshots WHERE namespace=%s AND source=%s AND sha256=%s',
                           (namespace, source, manifest['sha256'])).fetchone()
        if row:
            snapshot_id, normalized = row
        else:
            snapshot_id = conn.execute('''INSERT INTO nexus.source_snapshots
                (namespace,source,sha256,raw_bytes,source_saved_at,captured_at)
                VALUES(%s,%s,%s,%s,%s,%s) RETURNING id''',
                (namespace, source, manifest['sha256'], manifest['raw_bytes'], manifest['saved_at'], manifest['captured_at'])).fetchone()[0]
            normalized = None
            with open(archive, 'rb') as stream:
                ordinal = 0
                while block := stream.read(1024**2):
                    conn.execute('INSERT INTO nexus.snapshot_chunks VALUES(%s,%s,%s)', (snapshot_id, ordinal, block))
                    ordinal += 1
        conn.execute('INSERT INTO nexus.snapshot_sightings VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING',
                     (snapshot_id, manifest['saved_at'], manifest['captured_at'], manifest.get('original_name',source)))
    if not normalize or source not in (*ADAPTERS, *EXTENDED,ITEM_SOURCE,*EXTRA_SOURCES,OMNI_SOURCE):
        return dict(status='archived', snapshot_id=snapshot_id, source=source, inserted=0)
    if normalized == version:
        return dict(status='already_imported', snapshot_id=snapshot_id, source=source, inserted=0)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / source
        with gzip.open(archive, 'rb') as inp, path.open('wb') as out:
            while block := inp.read(1024**2):
                out.write(block)
        if source in EXTENDED:
            with conn.transaction():
                conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (namespace + ':' + source,))
                inserted, count = normalize_extended(conn, path, source, namespace, snapshot_id)
                conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s', (version, snapshot_id))
            return dict(status='imported',snapshot_id=snapshot_id,source=source,inserted=inserted,records=count)
        data = read_lua(path)
    if source==OMNI_SOURCE:
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+source,))
            inserted,count=normalize_omni(conn,data,namespace,snapshot_id)
            conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(version,snapshot_id))
        return dict(status='imported',snapshot_id=snapshot_id,source=source,inserted=inserted,records=count)
    if source==ITEM_SOURCE:
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+source,))
            count=normalize_items(conn,data,namespace,snapshot_id)
            conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(version,snapshot_id))
        return dict(status='imported',snapshot_id=snapshot_id,source=source,records=count,inserted=count)
    if source in EXTRA_SOURCES and source not in ADAPTERS:
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(namespace+':'+source,))
            count=normalize_extras(conn,data,source,namespace,snapshot_id)
            conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s',(version,snapshot_id))
        return dict(status='imported',snapshot_id=snapshot_id,source=source,records=count,inserted=count)
    rows = list(observations(source, data))
    inserted = 0
    with conn.transaction():
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (namespace + ':' + source,))
        for source_ordinal,row in enumerate(rows):
            identity = canonical([namespace, source, row])
            oid = hashlib.sha256(identity.encode()).hexdigest()
            result = conn.execute('''INSERT INTO nexus.source_observations
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT(id) DO NOTHING''',
                (oid, namespace, source, row['kind'], row['entity'], row['source_key'],
                 utc(row['observed_at']), row['precision'], row['copper'], row['quality'], canonical(row['payload'])))
            inserted += result.rowcount
            conn.execute('INSERT INTO nexus.snapshot_observations VALUES(%s,%s,%s) ON CONFLICT DO NOTHING', (snapshot_id, oid, source_ordinal))
        if source==INVENTORY_SOURCE:
            inventory_inserted,inventory_count=normalize_inventory(conn,data,namespace,snapshot_id)
            inserted+=inventory_inserted
        if source in EXTRA_SOURCES:inserted+=normalize_extras(conn,data,source,namespace,snapshot_id)
        conn.execute('UPDATE nexus.source_snapshots SET normalized_version=%s WHERE id=%s', (version, snapshot_id))
    return dict(status='imported', snapshot_id=snapshot_id, source=source, inserted=inserted, records=len(rows))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('manifest', type=Path)
    p.add_argument('--archive-only', action='store_true')
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    archive = args.manifest.parent / (manifest['sha256'] + '.lua.gz')
    import psycopg
    with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True) as conn:
        print(json.dumps(ingest_source(conn, archive, manifest, not args.archive_only)))


if __name__ == '__main__':
    main()

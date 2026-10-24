"""Single synchronous ingestion endpoint. An ACK means committed PostgreSQL data."""
import gzip
import json
import os
import sys
import tempfile
from pathlib import Path
import psycopg
from bundle import unpack_bundle
from source_importer import ingest_source
from importer import ingest


def import_packet(conn, packet):
    with tempfile.TemporaryDirectory() as tmp:
        _, manifest = unpack_bundle(packet, tmp, namespace=None)
        archive = Path(tmp) / (manifest['sha256'] + '.lua.gz')
        result = ingest_source(conn, archive, manifest)
        if manifest['source'] == 'Journalator.lua':
            with gzip.open(archive, 'rb') as stream:
                result['journalator'] = ingest(conn, stream.read(), manifest['source'], manifest['namespace'])
        return result


def main():
    with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True) as conn:
        if sys.argv[1] == 'init':
            for path in sorted(Path('/app/sql').glob('0*.sql')):
                with conn.transaction():
                    conn.execute(path.read_text())
            from psycopg import sql
            conn.execute(sql.SQL("CREATE ROLE grafana LOGIN PASSWORD {}").format(sql.Literal(os.environ['GF_DB_PASSWORD'])))
            conn.execute('GRANT USAGE ON SCHEMA nexus TO grafana')
            conn.execute('GRANT SELECT ON ALL TABLES IN SCHEMA nexus TO grafana')
        elif sys.argv[1] == 'ingest':
            print(json.dumps(import_packet(conn, Path(sys.argv[2]))))
        elif sys.argv[1] == 'restore':
            for packet in sorted(Path('/sources').glob('*.bundle'), key=lambda p: p.stat().st_mtime):
                print(json.dumps(import_packet(conn, packet)), flush=True)
        elif sys.argv[1] == 'verify':
            tables = ('source_snapshots', 'transactions', 'source_observations', 'market_observations', 'crafting_observations')
            counts = {name: conn.execute('SELECT count(*) FROM nexus.' + name).fetchone()[0] for name in tables}
            print(json.dumps(counts))
            if not counts['source_snapshots'] or not sum(counts[t] for t in tables[1:]):
                raise RuntimeError('No real normalized source records in PostgreSQL')
        else:
            raise ValueError('Unknown command')


if __name__ == '__main__':
    main()

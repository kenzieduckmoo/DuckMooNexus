"""Apply additive v0.3 migrations using the existing migration-owner connection."""
import os
from pathlib import Path
import psycopg
with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True) as conn:
    if not conn.execute('SELECT 1 FROM nexus.schema_migrations WHERE version=1').fetchone():
        raise RuntimeError('Existing migration 001 not found; inspect the existing database first')
    for path in sorted((Path(__file__).parent/'sql').glob('*.sql')):
        if path.name.startswith('001_'):continue
        with conn.transaction():
            conn.execute(path.read_text())
        print(path.name+' applied')

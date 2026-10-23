"""Hosted saved choices with retained revisions, separate from derived data."""
import os
import psycopg
from psycopg.types.json import Jsonb

ACCOUNT=os.environ.get('NEXUS_ACCOUNT','retail-main-account')


class DocumentConflict(ValueError):pass

def read_document_versioned(key):
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        row=conn.execute('SELECT payload,updated_at FROM nexus.crafting_documents WHERE namespace=%s AND key=%s',(ACCOUNT,key)).fetchone()
    return (row[0],row[1].isoformat()) if row else ({'version':1,'setups':[],**({'completed':[]} if key=='plan' else {})},'missing')

def read_document(key):return read_document_versioned(key)[0]


def save_document(key,value,expected_revision=None,include_revision=False):
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',('crafting:'+ACCOUNT+':'+key,))
        current=conn.execute('SELECT updated_at FROM nexus.crafting_documents WHERE namespace=%s AND key=%s',(ACCOUNT,key)).fetchone()
        revision=current[0].isoformat() if current else 'missing'
        if expected_revision is not None and expected_revision!=revision:
            raise DocumentConflict('This plan changed on another page. The latest version has been preserved; review it and try again.')
        conn.execute('''INSERT INTO nexus.crafting_document_history(namespace,key,payload)
          SELECT namespace,key,payload FROM nexus.crafting_documents WHERE namespace=%s AND key=%s''',(ACCOUNT,key))
        updated=conn.execute('''INSERT INTO nexus.crafting_documents(namespace,key,payload) VALUES(%s,%s,%s)
          ON CONFLICT(namespace,key) DO UPDATE SET payload=excluded.payload,updated_at=now() RETURNING updated_at''',(ACCOUNT,key,Jsonb(value))).fetchone()[0].isoformat()
    return (value,updated) if include_revision else value

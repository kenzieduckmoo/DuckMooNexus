"""Read-only live checks for client separation, journal reads and API query validity."""
import ast,json,urllib.request,urllib.error
from pathlib import Path
import os,psycopg
base='http://10.20.30.239'
def get(path):
 with urllib.request.urlopen(base+path,timeout=60) as r:return json.load(r)
for client in ('retail','forever'):
 roster=get('/api/characters?client='+client);journal=get('/api/adventures?client='+client)
 assert isinstance(roster,list) and journal['client']==client
 assert all(e.get('payload',{}).get('kind') for e in journal['events'])
 if roster:
  sheet=get('/api/characters?client='+client+'&guid='+roster[0]['character_guid']);assert sheet['gameClient']==client
 print(client,':',len(roster),'character sheets,',len(journal['events']),'journal events in first page')
 if journal.get('next'):
  from urllib.parse import urlencode
  cursor=journal['next'];older=get('/api/adventures?'+urlencode({'client':client,'character':journal['selected']['character_guid'],'beforeAt':cursor['at'],'beforeId':cursor['id']}))
  assert not ({e['id'] for e in journal['events']}&{e['id'] for e in older['events']})
  print(client,': older page contains',len(older['events']),'non-overlapping events')
try:get('/api/adventures?client=invalid')
except urllib.error.HTTPError as e:assert e.code==400
else:raise AssertionError('Invalid client accepted')
with psycopg.connect(os.environ['DATABASE_URL']) as conn:
 conn.execute('SET TRANSACTION READ ONLY')
 for file,marker,args in [('character_api_worker.py','WITH identities', (8,)),('item_names.py','WITH bought',('us','us',1)),('item_media.py','SELECT DISTINCT c.item_id',('us',1))]:
  code=ast.parse((Path('/app')/file).read_text())
  query=next(n.value for n in ast.walk(code) if isinstance(n,ast.Constant) and isinstance(n.value,str) and marker in n.value)
  conn.execute('EXPLAIN '+query,args).fetchall()
 print('Retail-only API worker queries passed PostgreSQL planning; no API calls or database writes performed.')
print('Client reads and query checks passed.')

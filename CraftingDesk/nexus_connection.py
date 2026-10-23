"""Optional read-only Nexus proxy; preserves the existing local capture workflow."""
import os
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ENDPOINTS={'items','inventory','market','characters','sources'}


def fetch(path,authorization=None):
    split=urlsplit(path);endpoint=split.path.removeprefix('/api/nexus/')
    if endpoint not in ENDPOINTS:return 404,b'{"error":"Unknown Nexus endpoint"}'
    base=os.environ.get('NEXUS_DATA_URL','http://10.20.30.239:8080').rstrip('/')
    headers={}
    auth=authorization or os.environ.get('NEXUS_AUTHORIZATION')
    if auth:headers['Authorization']=auth
    request=Request(base+'/api/v1/'+endpoint+('?' + split.query if split.query else ''),headers=headers)
    try:
        with urlopen(request,timeout=20) as response:return response.status,response.read(8*1024**2)
    except HTTPError as exc:
        with exc:return exc.code,exc.read(8192)
    except (URLError,TimeoutError):return 503,b'{"error":"Nexus data service is unavailable"}'

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from services.local_api.app import create_app

@pytest.fixture
def client(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'workspace.db'),base_url='http://127.0.0.1:8765',client=('127.0.0.1',51234)) as app:
        yield app

HEADERS={'Content-Type':'application/json','X-EAW-Request':'local-template-editor'}

def payload(template_id='general-meeting'):
    return {'template_id':template_id,'title':'Synthetic Test Note','values':{'agenda':'Mock agenda'}}

def test_catalog_and_filters(client):
    data=client.get('/api/v1/templates').json()
    assert data['total']>=15
    assert all(t['fields'] and t['department'] and t['job_family'] and t['job_role'] for t in data['items'])
    assert all(t['department']=='R&D' for t in client.get('/api/v1/templates?department=R%26D').json()['items'])

def test_create_read_update_and_restart(tmp_path):
    path=tmp_path/'local.db'
    client=TestClient(create_app(db_path=path),base_url='http://127.0.0.1:8765',client=('127.0.0.1',51234))
    res=client.post('/api/v1/documents',headers=HEADERS,json=payload())
    assert res.status_code==201, res.text
    doc=res.json();assert doc['scope']=='local_private' and doc['revision']==1
    assert client.get('/api/v1/documents/'+doc['id']).json()['values']['agenda']=='Mock agenda'
    upd=client.put('/api/v1/documents/'+doc['id'],headers=HEADERS,json={'expected_revision':1,'title':'Updated','values':{'agenda':'Synthetic second draft'}})
    assert upd.status_code==200 and upd.json()['revision']==2
    assert client.put('/api/v1/documents/'+doc['id'],headers=HEADERS,json={'expected_revision':1,'title':'Stale','values':{'agenda':'No write'}}).status_code==409
    reopened=TestClient(create_app(db_path=path),base_url='http://127.0.0.1:8765',client=('127.0.0.1',51234))
    assert reopened.get('/api/v1/documents/'+doc['id']).json()['title']=='Updated'

def test_reject_unknown_fields_and_media(client):
    req=payload();req['values']['video_url']='https://example.invalid/recording.mp4'
    assert client.post('/api/v1/documents',headers=HEADERS,json=req).status_code==422
    for path in ['/api/v1/upload','/api/v1/ai/chat','/api/v1/publish','/api/v1/record','/api/v1/export']:
        assert client.post(path,headers=HEADERS,json={}).status_code==404
    assert client.post('/api/v1/documents',headers={'Content-Type':'application/json'},json=payload()).status_code==403
    assert client.post('/api/v1/documents',headers={'X-EAW-Request':'local-template-editor','Content-Type':'text/plain'},content='hi').status_code==415

def test_origin_host_and_security_headers(client):
    assert client.get('/api/v1/templates',headers={'Host':'untrusted.internal'}).status_code==403
    assert client.post('/api/v1/documents',headers={**HEADERS,'Origin':'https://external.example'},json=payload()).status_code==403
    res=client.get('/')
    assert res.status_code==200
    assert "media-src 'none'" in res.headers['Content-Security-Policy']
    assert 'microphone=()' in res.headers['Permissions-Policy']
    assert 'cdn.' not in res.text.lower()

def test_remote_peer_is_rejected(tmp_path):
    with TestClient(create_app(db_path=tmp_path/'blocked.db'),base_url='http://127.0.0.1:8765',client=('192.0.2.42',5555)) as remote:
        assert remote.get('/api/v1/templates').status_code==403

def test_content_size_limit(client):
    req=payload();req['values']['agenda']='x'*70000
    assert client.post('/api/v1/documents',headers=HEADERS,json=req).status_code==413

def test_required_field_enforced(client):
    req=payload();req['values']={}
    assert client.post('/api/v1/documents',headers=HEADERS,json=req).status_code==422

def test_no_extraneous_fields(client):
    req=payload();req['file']='/etc/passwd'
    assert client.post('/api/v1/documents',headers=HEADERS,json=req).status_code==422

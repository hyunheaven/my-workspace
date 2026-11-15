"""Data-loss, concurrency and security checks for synthetic page blocks."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from services.local_api.app import create_app
from services.local_api.storage import LocalStore

URL='http://127.0.0.1:8765'
HEADERS={'Content-Type':'application/json','X-EAW-Request':'local-template-editor'}

@pytest.fixture
def client(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'v10.db'),base_url=URL,client=('127.0.0.1',9000)) as c:yield c

def test_page_creation_and_blocks_persist(client):
    created=client.post('/api/v1/pages',headers=HEADERS,json={'title':'Synthetic page'}).json()
    assert created['template_id']=='__blank_page__' and created['revision']==1
    blocks=[{'id':'00000000-0000-4000-8000-000000000001','type':'heading_1','content':'Experiment','checked':False},
            {'id':'00000000-0000-4000-8000-000000000002','type':'todo','content':'Review','checked':True}]
    saved=client.put('/api/v1/pages/'+created['id']+'/content',headers=HEADERS,
                     json={'title':'Revision 2','expected_revision':1,'blocks':blocks})
    assert saved.status_code==200,saved.text
    assert saved.json()['revision']==2 and saved.json()['blocks']==blocks
    assert client.get('/api/v1/pages/'+created['id']+'/content').json()['blocks']==blocks
    assert len(client.get('/api/v1/pages/tree').json()['items'])==1
    assert client.get('/api/v1/templates').json()['total']>=152
    assert client.get('/api/v1/health').json()['version']=='1.0.0'

def test_revision_validation_and_max_size(client):
    page=client.post('/api/v1/pages',headers=HEADERS,json={'title':'Safe'}).json()
    url='/api/v1/pages/'+page['id']+'/content'
    b={'id':'00000000-0000-4000-8000-000000000004','type':'paragraph','content':'<script>alert(1)</script>','checked':False}
    assert client.put(url,headers=HEADERS,json={'expected_revision':1,'title':'Safe','blocks':[b]}).status_code==200
    # Text is stored literally, never rendered with innerHTML.
    assert client.get(url).json()['blocks'][0]['content']==b['content']
    assert client.put(url,headers=HEADERS,json={'expected_revision':1,'title':'Stale','blocks':[]}).status_code==409
    assert client.put(url,headers=HEADERS,json={'expected_revision':2,'title':'Safe','blocks':[b,b]}).status_code==422
    assert client.put(url,headers=HEADERS,json={'expected_revision':2,'title':'Safe','blocks':[
        dict(b,type='video')]}).status_code==422
    assert client.put(url,headers=HEADERS,json={'expected_revision':2,'title':'Safe','blocks':[
        dict(b,content='X'*4001)]}).status_code==422
    assert client.get(url).json()['title']=='Safe'

def test_template_document_preserved_when_adding_blocks(client):
    old=client.post('/api/v1/documents',headers=HEADERS,json={
        'template_id':'general-meeting','title':'Synthetic Review','values':{'agenda':'Private placeholder'}}).json()
    url='/api/v1/pages/'+old['id']+'/content'
    assert client.put(url,headers=HEADERS,json={'expected_revision':1,'title':'Synthetic Review',
        'blocks':[{'id':'00000000-0000-4000-8000-000000000005','type':'paragraph','content':'Additional block'}]}).status_code==200
    body=client.get('/api/v1/documents/'+old['id']).json()
    assert body['values']['agenda']=='Private placeholder' and body['revision']==2
    assert client.get(url).json()['blocks'][0]['content']=='Additional block'

def test_legacy_sqlite_is_migrated_without_data_loss(tmp_path:Path):
    dbpath=tmp_path/'legacy.db'
    old=LocalStore(dbpath).create_doc('00000000-0000-4000-8000-000000000008','general-meeting',1,'Old content',{'agenda':'Preserved'})
    with TestClient(create_app(db_path=dbpath),base_url=URL,client=('127.0.0.1',9000)) as c:
        assert c.get('/api/v1/pages/'+old['id']+'/content').json()['blocks']==[]
        assert c.get('/api/v1/documents/'+old['id']).json()['values']['agenda']=='Preserved'

def test_local_security_still_applies(client):
    assert client.post('/api/v1/pages',json={'title':'No marker'},headers={'Content-Type':'application/json'}).status_code==403
    assert client.post('/api/v1/pages',json={'title':'Remote'},headers={**HEADERS,'Origin':'https://example.net'}).status_code==403
    assert client.get('/assets/pagecanvas.js').status_code==200
    assert client.get('/api/v1/pages/not-found/content').status_code==404
    assert client.get('/api/v1/share').status_code==404

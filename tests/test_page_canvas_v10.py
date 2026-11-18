"""Data-loss, concurrency and security checks for synthetic page blocks."""
from pathlib import Path
from uuid import uuid4
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
    assert client.get('/api/v1/health').json()['version']=='1.3.0'

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


def test_long_korean_canvas_round_trip_and_local_link_validation(client):
    source=client.post('/api/v1/pages',headers=HEADERS,json={'title':'합성 회의 기록'}).json()
    target=client.post('/api/v1/pages',headers=HEADERS,json={'title':'합성 후속 조치'}).json()
    path=f"/api/v1/pages/{source['id']}/content"
    long_text='합성 한글 문서 ' * 400
    blocks=[{'id':str(uuid4()),'type':'ordered_list','content':long_text,'checked':False} for _ in range(12)]
    link={'id':str(uuid4()),'type':'page_link','content':target['id'],'checked':False}
    blocks.append(link)
    assert sum(len(block['content'].encode('utf-8')) for block in blocks)>64 * 1024
    payload={'title':source['title'],'expected_revision':source['revision'],'blocks':blocks}
    saved=client.put(path,headers=HEADERS,json=payload)
    assert saved.status_code==200,saved.text
    assert client.get(path).json()['blocks']==blocks
    payload['expected_revision']=saved.json()['revision']
    payload['blocks']=[dict(link,content='https://example.invalid/')]
    assert client.put(path,headers=HEADERS,json=payload).status_code==422
    assert client.get(path).json()['blocks']==blocks


def test_nested_blocks_are_preserved_and_invalid_depth_is_rejected(client):
    created=client.post('/api/v1/pages',headers=HEADERS,json={'title':'합성 계층'}).json()
    path=f"/api/v1/pages/{created['id']}"
    root={'id':str(uuid4()),'type':'toggle','content':'분류','checked':False}
    child={'id':str(uuid4()),'type':'paragraph','content':'하위 문단','checked':False,'depth':1}
    grandchild={'id':str(uuid4()),'type':'todo','content':'상세 작업','checked':True,'depth':2}
    payload={'title':created['title'],'expected_revision':created['revision']}
    blocks=[root,child,grandchild]
    saved=client.put(path+'/content',headers=HEADERS,json={**payload,'blocks':blocks})
    assert saved.status_code==200,saved.text
    assert saved.json()['blocks']==blocks
    payload['expected_revision']=saved.json()['revision']
    for invalid in ([child], [root,grandchild], [root,dict(child,depth=True)], [root,dict(child,depth=7)]):
        response=client.put(path+'/content',headers=HEADERS,json={**payload,'blocks':invalid})
        assert response.status_code==422,response.text
    assert client.get(path+'/content').json()['blocks']==blocks
    snapshot=client.get(path+f"/history/{saved.json()['revision']}")
    assert snapshot.json()['blocks']==blocks
    duplicate=client.post(path+'/duplicate',headers=HEADERS,
        json={'expected_revision':saved.json()['revision'],'request_id':str(uuid4())})
    assert duplicate.status_code==201,duplicate.text
    copied=duplicate.json()['blocks']
    assert [block.get('depth',0) for block in copied]==[0,1,2]
    assert {block['id'] for block in copied}.isdisjoint(block['id'] for block in blocks)

"""Synthetic-only local integration tests for v0.9."""
from datetime import date, timedelta
from pathlib import Path
import sqlite3
import pytest
from fastapi.testclient import TestClient
from services.local_api.app import create_app

HEADERS={'Content-Type':'application/json','X-EAW-Request':'local-template-editor'}
URL='http://127.0.0.1:8765'

@pytest.fixture
def client(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'data.db'),base_url=URL,client=('127.0.0.1',9000)) as x:
        yield x

def post(client,path,payload):
    return client.post(path,headers=HEADERS,json=payload)

def put(client,path,payload):
    return client.put(path,headers=HEADERS,json=payload)

def doc(client,title,parent_id=None):
    r=post(client,'/api/v1/documents',{'template_id':'general-meeting','title':title,'values':{'agenda':'Synthetic only'},'parent_id':parent_id})
    assert r.status_code==201,r.text
    return r.json()

def test_existing_templates_and_getting_started_remain(client):
    assert client.get('/api/v1/templates').json()['total']>=152
    html=client.get('/').text
    for text in ['id="nav-pages"','id="nav-database"','id="nav-calendar"','id="nav-projects"','시작하기','id="cal-view"','id="page-tree"']:
        assert text in html
    assert 'https://' not in html
    js=client.get('/assets/app.js').text
    for marker in ['renderPageTree','loadCalendar','renderTasks','event-chip','task-board']:
        assert marker in js
    assert '<iframe' not in html.lower()

def test_page_tree_create_move_cycle_and_stale_revision(client):
    root=doc(client,'Root page');child=doc(client,'Child page',root['id']);grand=doc(client,'Grandchild',child['id'])
    tree=client.get('/api/v1/pages/tree').json()['items'];assert len(tree)==3
    assert next(d for d in tree if d['id']==child['id'])['parent_id']==root['id']
    assert post(client,'/api/v1/documents',{'template_id':'general-meeting','title':'Orphan','values':{'agenda':'Synthetic'},'parent_id':'missing'}).status_code==422
    assert put(client,f'/api/v1/pages/{root["id"]}/move',{'expected_revision':1,'parent_id':grand['id']}).status_code==422
    assert put(client,f'/api/v1/pages/{child["id"]}/move',{'expected_revision':1,'parent_id':child['id']}).status_code==422
    moved=put(client,f'/api/v1/pages/{child["id"]}/move',{'expected_revision':1,'parent_id':None})
    assert moved.status_code==200 and moved.json()['revision']==2 and moved.json()['parent_id'] is None
    assert put(client,f'/api/v1/pages/{child["id"]}/move',{'expected_revision':1,'parent_id':root['id']}).status_code==409

def test_project_task_database_revision_and_document_link(client):
    page=doc(client,'Technical Review')
    project=post(client,'/api/v1/projects',{'title':'Synthetic Milestone','description':'Test only','status':'active'})
    assert project.status_code==201
    p=project.json()
    task=post(client,'/api/v1/tasks',{'title':'Complete review','project_id':p['id'],'document_id':page['id'],'status':'todo','priority':'high','due_on':'2026-11-26'})
    assert task.status_code==201,task.text;t=task.json()
    assert t['document_id']==page['id']
    assert client.get('/api/v1/tasks?project_id='+p['id']).json()['items'][0]['id']==t['id']
    assert post(client,'/api/v1/tasks',{'title':'Bad','project_id':'not-a-project'}).status_code==422
    assert post(client,'/api/v1/tasks',{'title':'Bad','due_on':'2026-13-31'}).status_code==422
    updated=put(client,'/api/v1/tasks/'+t['id'],{**{k:t[k] for k in ['title','project_id','document_id','status','priority','due_on']},'status':'done','expected_revision':1})
    assert updated.status_code==200 and updated.json()['revision']==2
    assert put(client,'/api/v1/tasks/'+t['id'],{**{k:t[k] for k in ['title','project_id','document_id','status','priority','due_on']},'expected_revision':1}).status_code==409
    assert put(client,'/api/v1/projects/'+p['id'],{'title':'Updated','description':'Test','status':'completed','expected_revision':1}).status_code==200
    assert put(client,'/api/v1/projects/'+p['id'],{'title':'Again','description':'Test','status':'active','expected_revision':1}).status_code==409

def test_calendar_event_crud_feed_and_task_projection(client):
    task=post(client,'/api/v1/tasks',{'title':'Documentation due','due_on':'2026-11-20'}).json()
    all_day={'title':'Design review','start_at':'2026-11-19','end_at':'2026-11-21','all_day':True,'timezone':'Asia/Seoul','task_id':task['id']}
    ev=post(client,'/api/v1/calendar/events',all_day)
    assert ev.status_code==201,ev.text
    event=ev.json();assert event['end_date']=='2026-11-21' and event['revision']==1
    feed=client.get('/api/v1/calendar/feed?start=2026-11-20&end=2026-11-21').json()['items']
    assert {e['kind'] for e in feed}=={'event','task'}
    assert len(client.get('/api/v1/calendar/events?start=2026-11-21&end=2026-11-22').json()['items'])==0
    upd=put(client,'/api/v1/calendar/events/'+event['id'],{**all_day,'title':'Review updated','expected_revision':1})
    assert upd.status_code==200 and upd.json()['revision']==2
    assert put(client,'/api/v1/calendar/events/'+event['id'],{**all_day,'expected_revision':1}).status_code==409
    assert client.get('/api/v1/calendar/events/'+event['id']).json()['title']=='Review updated'

def test_timezone_and_calendar_input_errors(client):
    payload={'title':'Standup','start_at':'2026-11-15T09:00:00+09:00','end_at':'2026-11-15T10:00:00+09:00','all_day':False,'timezone':'Asia/Seoul'}
    ev=post(client,'/api/v1/calendar/events',payload)
    assert ev.status_code==201,ev.text
    assert ev.json()['start_at']=='2026-11-15T00:00:00+00:00'
    assert ev.json()['start_date']=='2026-11-15'
    assert post(client,'/api/v1/calendar/events',{**payload,'start_at':'2026-11-15T09:00:00'}).status_code==422
    assert post(client,'/api/v1/calendar/events',{**payload,'end_at':'2026-11-15T08:00:00+09:00'}).status_code==422
    assert post(client,'/api/v1/calendar/events',{**payload,'timezone':'Not/Real'}).status_code==422
    assert post(client,'/api/v1/calendar/events',{**payload,'document_id':'missing'}).status_code==422
    assert post(client,'/api/v1/calendar/events',{'title':'bad day','start_at':'2026-11-20','end_at':'2026-11-20','all_day':True}).status_code==422
    assert client.get('/api/v1/calendar/feed?start=2026-11-22&end=2026-11-21').status_code==422
    assert client.get('/api/v1/calendar/feed?start=2026-01-01&end=2030-01-01').status_code==422

def test_local_no_remote_side_effects(client):
    assert client.get('/api/v1/health').json()['sharing_enabled'] is False
    response=client.get('/api/v1/calendar/feed?start=2026-11-15&end=2026-11-16')
    assert response.headers['Cache-Control']=='no-store'
    assert "connect-src 'self'" in response.headers['Content-Security-Policy']
    for endpoint in ['/api/v1/upload','/api/v1/share','/api/v1/ai/chat','/api/v1/calendar/export','/api/v1/calendar/sync','/api/v1/webhook']:
        assert post(client,endpoint,{}).status_code==404
    assert client.post('/api/v1/tasks',headers={'Content-Type':'application/json'},json={'title':'Forbidden'}).status_code==403
    assert client.post('/api/v1/tasks',headers={**HEADERS,'Origin':'https://external.example'},json={'title':'Blocked'}).status_code==403

def test_migrate_v08_database_without_losing_documents(tmp_path):
    path=tmp_path/'prior.db'
    from services.local_api.storage import LocalStore
    old=LocalStore(path)
    original=old.create_doc('00000000-0000-0000-0000-000000000001','general-meeting',1,'Old version doc',{'agenda':'Kept'})
    with TestClient(create_app(db_path=path),base_url=URL,client=('127.0.0.1',1234)) as client:
        doc=client.get('/api/v1/documents/'+original['id']).json()
        assert doc['title']=='Old version doc' and doc['parent_id'] is None
        assert client.get('/api/v1/projects').json()['items']==[]
        assert len(client.get('/api/v1/pages/tree').json()['items'])==1

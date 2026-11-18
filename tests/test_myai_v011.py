"""v0.11 branding, discovery, and backward-compatibility checks."""
from pathlib import Path
from fastapi.testclient import TestClient
from services.local_api.app import create_app
from services.local_api.storage import LocalStore
URL='http://127.0.0.1:8765'
HEADERS={'Content-Type':'application/json','X-EAW-Request':'local-template-editor'}

def test_brand_and_catalog_and_local_security(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'test.db'),base_url=URL,client=('127.0.0.1',1234)) as c:
        assert c.get('/api/v1/health').json()['version']=='1.3.0'
        html=c.get('/').text
        assert 'My Workspace' in html and 'id="sidebar-quick-search"' in html
        assert 'data-discovery="recommended"' in html
        assert 'data-discovery="popular_category"' in html
        assert '<iframe' not in html.lower() and 'https://' not in html.lower()
        t=[item for item in c.get('/api/v1/templates').json()['items'] if not item['id'].startswith('library-')]
        assert len(t)==152 and len({x['id'] for x in t})==152
        assert len([x for x in t if x['id'].startswith('myai-original-')])==72
        assert len([x for x in t if not x['id'].startswith('myai-original-')])==80
        assert sum(x.get('discovery')=='recommended' for x in t)==36
        assert sum(x.get('discovery')=='popular_category' for x in t)==36
        assert all(x['source_type']=='original' and x['redistribution']=='internal_review_required' for x in t)
        for x in t:
            assert len({f['id'] for f in x['fields']})==len(x['fields'])
            assert all(f['type'] in ('text','multiline','date','select') for f in x['fields'])
        for asset in ('app.css','app.js','pagecanvas.js','themes.css','themes.js'):
            resp=c.get('/assets/'+asset)
            assert resp.status_code==200 and 'http://' not in resp.text and 'https://' not in resp.text
        assert c.post('/api/v1/upload',headers=HEADERS,json={}).status_code==404

def test_new_template_saves_and_existing_db_remains_readable(tmp_path:Path):
    db=tmp_path/'legacy.db'
    legacy=LocalStore(db).create_doc('00000000-0000-4000-8000-000000000008','general-meeting',1,'Synthetic legacy',{'agenda':'Test only'})
    with TestClient(create_app(db_path=db),base_url=URL,client=('127.0.0.1',1234)) as c:
        assert c.get('/api/v1/documents/'+legacy['id']).json()['values']['agenda']=='Test only'
        new=c.post('/api/v1/documents',headers=HEADERS,json={'template_id':'myai-original-001','title':'Synthetic plan','values':{'purpose':'Non-confidential synthetic test'}})
        assert new.status_code==201,new.text
        assert c.get('/api/v1/documents/'+new.json()['id']).json()['title']=='Synthetic plan'

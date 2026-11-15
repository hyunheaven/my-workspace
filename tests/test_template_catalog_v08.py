"""v0.8 original templates and frontend onboarding regressions."""
from pathlib import Path
import json
from collections import Counter
from fastapi.testclient import TestClient
from services.local_api.app import create_app

HEADERS={'Content-Type':'application/json','X-EAW-Request':'local-template-editor'}

def test_catalog_is_152_unique_originals(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'test.db'),base_url='http://127.0.0.1:8765',client=('127.0.0.1',12345)) as client:
        catalog=[item for item in client.get('/api/v1/templates').json()['items'] if not item['id'].startswith('library-')]
        assert len(catalog)==152
        assert len({t['id'] for t in catalog})==152
        assert len({t['department'] for t in catalog})==15
        assert Counter(t['section'] for t in catalog)=={'업무':130,'개인':11,'학습':11}
        assert all(t['source_type']=='original' and t['redistribution']=='internal_review_required' for t in catalog)
        assert all(len(t['fields'])>=4 and len(set(f['id'] for f in t['fields']))==len(t['fields']) for t in catalog)
        assert all(f['type'] in ('multiline','text','date','select') for t in catalog for f in t['fields'])
        assert all(not any(keyword in f['id'].lower() for keyword in ('audio','video','embed','upload','file')) for t in catalog for f in t['fields'])

def test_search_and_statistics(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'test.db'),base_url='http://127.0.0.1:8765',client=('127.0.0.1',12345)) as client:
        stats=client.get('/api/v1/template-catalog/stats').json()
        assert stats['total']>=152 and stats['third_party_imported']==0
        assert stats['by_department']['R&D']>=20
        assert client.get('/api/v1/templates?section=%ED%95%99%EC%8A%B5').json()['total']>=11
        assert client.get('/api/v1/templates?q=%EA%B0%80%EC%84%A4').json()['total']>=1
        assert client.get('/api/v1/templates?q='+('x'*121)).status_code==422
        assert client.get('/api/v1/templates?department=R%26D').json()['total']>=20

def test_create_new_original_template_and_validate_types(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'test.db'),base_url='http://127.0.0.1:8765',client=('127.0.0.1',12345)) as client:
        t=next(t for t in client.get('/api/v1/templates').json()['items'] if t['id']=='eaw-original-001')
        values={t['fields'][0]['id']:'합성 실험 목표'}
        res=client.post('/api/v1/documents',headers=HEADERS,json={'template_id':t['id'],'title':'합성 데이터', 'values':values})
        assert res.status_code==201, res.text
        assert client.get('/api/v1/documents/'+res.json()['id']).json()['template_id']==t['id']
        date_field=next(f for f in t['fields'] if f['type']=='date')
        values[date_field['id']]='2026-99-44'
        invalid=client.post('/api/v1/documents',headers=HEADERS,json={'template_id':t['id'],'title':'유효성 테스트','values':values})
        assert invalid.status_code==422

def test_getting_started_is_local_no_external_assets(tmp_path:Path):
    with TestClient(create_app(db_path=tmp_path/'test.db'),base_url='http://127.0.0.1:8765',client=('127.0.0.1',12345)) as client:
        html=client.get('/').text
        assert '시작하기' in html and 'id="template-search"' in html and 'id="section-filter"' in html
        assert '<iframe' not in html.lower()
        assert 'https://' not in html.lower()
        js=client.get('/assets/app.js')
        assert js.status_code==200
        assert 'template-search' in js.text and 'section-filter' in js.text
        for endpoint in ['/api/v1/template-import','/api/v1/marketplace/sync','/api/v1/ai/chat','/api/v1/upload']:
            assert client.post(endpoint,headers=HEADERS,json={}).status_code==404

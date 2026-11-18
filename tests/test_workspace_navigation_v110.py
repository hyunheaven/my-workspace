"""Keep stable page IDs, tree membership and search in sync across trash and restore."""
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from services.local_api.app import create_app

HEADERS = {'X-EAW-Request': 'local-template-editor'}


@pytest.fixture
def workspace(tmp_path):
    with TestClient(create_app(tmp_path / 'workspace.db'),
                    base_url='http://127.0.0.1:8765', client=('127.0.0.1', 1234),
                    headers=HEADERS) as client:
        yield client


def test_subtree_trash_hides_search_and_rejects_stale_write(workspace):
    def blank(title, parent_id=None):
        response = workspace.post('/api/v1/pages', json={'title': title, 'parent_id': parent_id})
        assert response.status_code == 201
        return response.json()

    def page_path(page):
        return '/api/v1/pages/' + page['id']

    def change_trash(page, action, revision=None):
        return workspace.post(page_path(page) + '/' + action,
                              json={'expected_revision': revision or page['revision']})

    parent = blank('검토 문서')
    child = blank('검토 항목', parent['id'])
    hidden_child = blank('별도 보관', parent['id'])
    assert change_trash(hidden_child, 'trash').status_code == 200
    assert change_trash(parent, 'trash', parent['revision'] + 1).status_code == 409
    assert change_trash(parent, 'trash').status_code == 200
    assert workspace.get('/api/v1/pages/tree').json()['items'] == []
    assert workspace.get('/api/v1/search', params={'q': '검토'}).json()['pages'] == []
    assert workspace.get(page_path(child) + '/content').status_code == 404
    assert workspace.get(page_path(child) + '/history/1').status_code == 404
    assert workspace.get('/api/v1/documents/' + child['id']).status_code == 404
    assert workspace.put(page_path(child) + '/content', json={
        'expected_revision': child['revision'], 'title': '예전 편집기', 'blocks': [],
    }).status_code == 404
    assert workspace.post('/api/v1/pages', json={
        'title': '새 항목', 'parent_id': parent['id'],
    }).status_code == 422

    trash = {page['id']: page for page in workspace.get('/api/v1/pages/trash').json()['items']}
    assert trash[parent['id']]['page_count'] == 2
    assert trash[hidden_child['id']]['page_count'] == 1
    assert change_trash(hidden_child, 'restore', trash[hidden_child['id']]['revision']).status_code == 409
    assert change_trash(parent, 'restore', trash[parent['id']]['revision']).status_code == 200
    restored = workspace.get(page_path(child) + '/content').json()
    assert (restored['id'], restored['parent_id'], restored['title']) == (child['id'], parent['id'], child['title'])
    assert workspace.put(page_path(child) + '/content', json={
        'expected_revision': child['revision'], 'title': '예전 편집기', 'blocks': [],
    }).status_code == 409
    assert workspace.get(page_path(hidden_child) + '/content').status_code == 404
    assert change_trash(hidden_child, 'restore', trash[hidden_child['id']]['revision']).status_code == 200
    assert workspace.get('/api/v1/pages/trash').json()['items'] == []


def test_template_tag_defaults_are_independent_and_tasks_share_search(workspace):
    template = next(item for item in workspace.get('/api/v1/templates').json()['items'] if item.get('tags'))

    def create_template_page():
        response = workspace.post('/api/v1/pages/from-template', json={
            'template_id': template['id'], 'request_id': str(uuid4()),
        })
        assert response.status_code == 201, response.text
        return response.json()

    first = create_template_page()
    default_tags = first['properties']['tags']
    assert default_tags and first['blocks']
    response = workspace.patch('/api/v1/pages/' + first['id'] + '/properties', json={
        'expected_revision': first['properties']['revision'], 'tags': ['검토 자료'],
    })
    assert response.status_code == 200
    second = create_template_page()
    assert second['properties']['tags'] == default_tags
    assert {block['id'] for block in first['blocks']}.isdisjoint(block['id'] for block in second['blocks'])

    task_response = workspace.post('/api/v1/tasks', json={'title': '검토 업무', 'notes': '실험 메모'})
    assert task_response.status_code == 201, task_response.text
    task = task_response.json()
    search = workspace.get('/api/v1/search', params={'q': '검토'}).json()
    assert {page['id'] for page in search['pages']} == {first['id']}
    assert [match['id'] for match in search['tasks']] == [task['id']]
    note_search = workspace.get('/api/v1/search', params={'q': '실험 메모'}).json()
    assert [match['id'] for match in note_search['tasks']] == [task['id']]

"""Behavioral tests for local schemas, typed records, views and relations."""
from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient
import pytest

from services.local_api.app import create_app

BASE = '/api/v1/databases'
ORIGIN = 'http://127.0.0.1:8765'
HEADERS = {'X-EAW-Request': 'local-template-editor'}


def client_for(path):
    return TestClient(create_app(path), base_url=ORIGIN,
                      client=('127.0.0.1', 1234), headers=HEADERS)


@pytest.fixture
def database_client(tmp_path):
    with client_for(tmp_path / 'workspace.db') as client:
        yield client


def checked(response, status=200):
    assert response.status_code == status, response.text
    return response.json()


def create_database(client, name):
    return checked(client.post(BASE, json={'name': name}), 201)


def path_of(db):
    return BASE + '/' + db['id']


def property_of(client, db, name, kind, **config):
    updated = checked(client.post(path_of(db) + '/properties', json={
        'name': name, 'type': kind, 'config': config, 'expected_revision': db['revision'],
    }), 201)
    return updated, updated['properties'][-1]['id']


def record_of(client, db, title, values=None, notes=''):
    return checked(client.post(path_of(db) + '/records', json={
        'title': title, 'notes': notes, 'values': values or {},
    }), 201)


def revise_record(client, db, record, values):
    return client.put(path_of(db) + '/records/' + record['id'], json={
        'title': record['title'], 'notes': record['notes'], 'values': values,
        'expected_revision': record['revision'],
    })


def test_schema_and_views_are_durable(tmp_path):
    db_path = tmp_path / 'workspace.db'
    with client_for(db_path) as client:
        projects = create_database(client, '실험 목록')
        assert projects['views'][0]['kind'] == 'table'
        projects, phase = property_of(client, projects, '진행', 'select', options=['준비', '완료'])
        projects, start = property_of(client, projects, '시작', 'date')
        projects, end = property_of(client, projects, '종료', 'date')
        projects, flag = property_of(client, projects, '표시', 'checkbox')
        projects, url = property_of(client, projects, '참고 링크', 'url')
        projects, milestones = property_of(client, projects, '항목', 'multi_select',
                                           options=['설계', '검토'])
        sample = record_of(client, projects, '검증 A', {
            phase: '준비', start: '2026-11-17', end: '2026-11-18', flag: False,
            url: 'https://example.com/reference', milestones: ['설계', '검토'],
        }, '한국어 시험 메모\n새 줄')
        for name, kind, config in (
            ('상태 보드', 'board', {'group_by': phase}),
            ('시작 캘린더', 'calendar', {'date_property': start}),
            ('실험 타임라인', 'timeline', {'date_property': start, 'end_date_property': end}),
            ('완료 갤러리', 'gallery',
             {'filter_property': phase, 'filter_value': '완료', 'sort_by': start, 'sort_direction': 'desc'}),
        ):
            projects = checked(client.post(path_of(projects) + '/views', json={
                'name': name, 'kind': kind, 'config': config, 'expected_revision': projects['revision'],
            }), 201)
        assert len(projects['views']) == 5
        assert projects['records'] == [sample]
        roles = checked(client.get('/api/v1/search', params={'q': '시험 메모'}))['databases']
        assert roles[0]['kind'] == 'record' and roles[0]['id'] == sample['id']
        results = checked(client.get('/api/v1/search', params={'q': '검토'}))['databases']
        assert results[0]['id'] == sample['id']
        assert checked(client.get('/api/v1/search', params={'q': '시험 메모', 'tag': '없음'}))['databases'] == []

    with client_for(db_path) as client:
        assert checked(client.get(path_of(projects))) == projects
        with sqlite3.connect(db_path) as db:
            assert db.execute('PRAGMA foreign_key_check').fetchall() == []
            assert db.execute('PRAGMA integrity_check').fetchone() == ('ok',)


def test_relations_rollups_and_formula_follow_source_edits(database_client):
    client = database_client
    source = create_database(client, '측정 결과')
    source, result = property_of(client, source, '측정값', 'number')
    first = record_of(client, source, '첫 측정', {result: 12})
    second = record_of(client, source, '두 번째 측정', {result: 18})

    target = create_database(client, '결과 요약')
    target, link = property_of(client, target, '측정 연결', 'relation', database_id=source['id'])
    target, mean = property_of(client, target, '평균', 'rollup', operation='average',
                              relation_id=link, property_id=result)
    target, count = property_of(client, target, '샘플 수', 'rollup', operation='count', relation_id=link)
    target, scale = property_of(client, target, '환산 계수', 'number')
    target, formula = property_of(client, target, '환산 결과', 'formula',
                                 operation='multiply', left_id=mean, right_id=scale)
    row = record_of(client, target, '샘플 그룹', {link: [first['id'], second['id']], scale: 2})
    assert row['values'][mean] == 15
    assert row['values'][count] == 2
    assert row['values'][formula] == 30

    assert revise_record(client, source, first, {result: 30}).status_code == 200
    updated = checked(client.get(path_of(target)))['records'][0]
    assert updated['values'][mean] == 24
    assert updated['values'][formula] == 48
    assert updated['revision'] == row['revision']

    delete_path = path_of(source) + '/records/' + second['id']
    deleted = client.request('DELETE', delete_path, json={'expected_revision': second['revision']})
    assert deleted.status_code == 409
    unlinked = checked(revise_record(client, target, row, {link: [first['id']], scale: 2}))
    assert unlinked['values'][formula] == 60
    deleted = client.request('DELETE', delete_path, json={'expected_revision': second['revision']})
    assert deleted.status_code == 204


def test_invalid_batch_rolls_back_and_stale_mutations_are_rejected(database_client):
    client = database_client
    db = create_database(client, '기록')
    db, phase = property_of(client, db, '진행', 'select', options=['준비', '완료'])
    db, date = property_of(client, db, '시작', 'date')
    db, url = property_of(client, db, '참고 링크', 'url')
    db, number = property_of(client, db, '값', 'number')
    db, computed = property_of(client, db, '두 배', 'formula', operation='add',
                               left_id=number, right_id=number)
    row = record_of(client, db, '기존', {phase: '준비'})
    path = path_of(db)
    bad_batch = client.post(path + '/records/batch', json={'records': [
        {'title': '첫 행', 'values': {phase: '준비'}},
        {'title': '두 번째 행', 'values': {date: '2026-02-31'}},
    ]})
    assert bad_batch.status_code == 422
    assert checked(client.get(path))['records'] == [row]
    for invalid in ({computed: 9}, {number: True}, {url: 'file:///tmp/reference'}, {date: '20261117'}):
        assert client.post(path + '/records', json={'title': '잘못된 값', 'values': invalid}).status_code == 422
    saved = checked(revise_record(client, db, row, {phase: '완료'}))
    assert saved['values'][phase] == '완료'
    assert revise_record(client, db, row, {phase: '준비'}).status_code == 409

    property_path = path + '/properties/' + phase
    settings = {'name': '단계', 'type': 'select', 'config': {'options': ['준비']}}
    assert client.put(property_path, json={**settings, 'expected_revision': db['revision']}).status_code == 422
    settings['config']['options'].append('완료')
    assert client.put(property_path, json={**settings, 'expected_revision': db['revision'] - 1}).status_code == 409
    updated = checked(client.put(property_path, json={**settings, 'expected_revision': db['revision']}))
    assert updated['properties'][0]['name'] == '단계'
    assert updated['records'][0]['values'][phase] == '완료'
    batch = checked(client.post(path + '/records/batch', json={
        'records': [{'title': '첫 행'}, {'title': '두 번째 행'}],
    }), 201)
    assert len(batch['items']) == 2


def test_record_history_paginates_and_restores_as_new_revision(database_client):
    client = database_client
    database = create_database(client, '레코드 이력')
    database, effort = property_of(client, database, '공수', 'number')
    first = record_of(client, database, '합성 원본', {effort: 5}, '초기 합성 메모')
    history = path_of(database) + '/records/' + first['id'] + '/history'
    record = first
    for value in range(6, 32):
        record = checked(revise_record(client, database, record, {effort: value}))
    recent = checked(client.get(history))['items']
    earlier = checked(client.get(history, params={'before_revision': recent[-1]['revision']}))['items']
    assert [item['revision'] for item in recent] == list(range(27, 2, -1))
    assert [item['revision'] for item in earlier] == [2, 1]
    assert earlier[-1]['snapshot'] == {'title': first['title'], 'notes': first['notes'], 'values': {effort: 5}}

    restore = history + '/1/restore'
    assert client.post(restore, json={'expected_revision': first['revision']}).status_code == 409
    assert client.post(history + '/999/restore', json={'expected_revision': record['revision']}).status_code == 404
    other = create_database(client, '다른 데이터베이스')
    assert client.get(path_of(other) + '/records/' + first['id'] + '/history').status_code == 404
    assert client.post(path_of(other) + '/records/' + first['id'] + '/history/1/restore',
                       json={'expected_revision': record['revision']}).status_code == 404

    restored = checked(client.post(restore, json={'expected_revision': record['revision']}))
    assert (restored['id'], restored['revision'], restored['values']) == (first['id'], 28, {effort: 5})
    assert checked(client.get(history))['items'][0]['revision'] == 28


def test_restore_rejects_a_historical_relation_to_a_deleted_record(database_client):
    client = database_client
    target_database = create_database(client, '관계 대상')
    target = record_of(client, target_database, '이전 관계')
    source_database = create_database(client, '관계 원본')
    source_database, relation = property_of(client, source_database, '관계', 'relation',
                                            database_id=target_database['id'])
    old = record_of(client, source_database, '원본 레코드', {relation: [target['id']]})
    current = checked(revise_record(client, source_database, old, {}))
    assert client.request('DELETE', path_of(target_database) + '/records/' + target['id'],
                          json={'expected_revision': target['revision']}).status_code == 204
    history = path_of(source_database) + '/records/' + old['id'] + '/history'
    entries = checked(client.get(history))
    assert client.post(history + '/1/restore', json={'expected_revision': current['revision']}).status_code == 422
    assert checked(client.get(history)) == entries
    assert checked(client.get(path_of(source_database)))['records'] == [current]


def test_view_history_tracks_settings_and_preserves_the_view_identity(database_client):
    client = database_client
    database = create_database(client, '보기 이력')
    view_id = database['views'][0]['id']
    path = path_of(database) + '/views/' + view_id
    database, number = property_of(client, database, '합성 수치', 'number')
    original_revision = database['revision']
    config = {'sort_by': number, 'sort_direction': 'desc'}
    database = checked(client.put(path, json={
        'name': '수치 갤러리', 'kind': 'gallery', 'config': config,
        'expected_revision': database['revision'],
    }))
    entries = checked(client.get(path + '/history'))['items']
    assert [item['revision'] for item in entries] == [database['revision'], 1]
    assert entries[0]['snapshot'] == {'name': '수치 갤러리', 'kind': 'gallery', 'config': config}

    restore = path + '/history/1/restore'
    assert client.post(restore, json={'expected_revision': original_revision}).status_code == 409
    restored = checked(client.post(restore, json={'expected_revision': database['revision']}))
    assert restored['views'][0] == {'id': view_id, 'name': '표', 'kind': 'table', 'config': {}}
    assert [item['revision'] for item in checked(client.get(path + '/history'))['items']] == [
        restored['revision'], database['revision'], 1,
    ]

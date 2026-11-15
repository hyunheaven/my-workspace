"""SQLite page properties, tag normalization, filtering and history independence."""
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest import TestCase
from uuid import uuid4

from fastapi.testclient import TestClient

from services.local_api.app import create_app

URL = 'http://127.0.0.1:8765'
HEADERS = {'X-EAW-Request': 'local-template-editor'}


class PagePropertiesTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = Path(directory.name) / 'workspace.db'

    def client(self):
        return TestClient(create_app(self.db), base_url=URL, client=('127.0.0.1', 1234))

    def test_properties_are_durable_and_content_revision_is_independent(self):
        with self.client() as client:
            page = client.post('/api/v1/pages', headers=HEADERS, json={'title': 'Local sample'}).json()
            path = '/api/v1/pages/' + page['id']
            self.assertEqual(page['properties']['revision'], 0)
            updated = client.patch(path + '/properties', headers=HEADERS, json={
                'expected_revision': 0, 'tags': [' #Review ', 'ＲＥＶＩＥＷ', '공정 검토'],
                'theme': 'contrast', 'background': 'ruled', 'tab_color': 'gold',
            })
            self.assertEqual(updated.status_code, 200, updated.text)
            self.assertEqual(updated.json()['tags'], ['Review', '공정 검토'])
            self.assertEqual(client.patch(path + '/properties', headers=HEADERS, json={
                'expected_revision': 0, 'theme': 'ocean'
            }).status_code, 409)
            revision = client.patch(path + '/properties', headers=HEADERS, json={
                'expected_revision': 1, 'theme': 'ocean'
            }).json()
            self.assertEqual(revision['tags'], ['Review', '공정 검토'])
            saved = client.put(path + '/content', headers=HEADERS,
                               json={'title': 'Updated sample', 'expected_revision': 1, 'blocks': []})
            self.assertEqual(saved.status_code, 200, saved.text)
            self.assertEqual(saved.json()['properties'], revision)
            duplicate = client.post(path + '/duplicate', headers=HEADERS, json={
                'expected_revision': 2, 'request_id': str(uuid4()),
            }).json()
            self.assertEqual(duplicate['properties']['tab_color'], 'gold')
            self.assertEqual(duplicate['properties']['tags'], revision['tags'])
            self.assertEqual(len(client.get('/api/v1/search/pages?tag=review').json()['items']), 2)
            self.assertEqual(len(client.get('/api/v1/search/pages?q=review').json()['items']), 2)
            self.assertEqual(client.get('/api/v1/search/pages?tag=rev').json()['items'], [])
            self.assertEqual(client.get('/api/v1/page-tags').json()['items'][0], {'label': 'Review', 'count': 2})
            restored = client.post(path + '/history/1/restore', headers=HEADERS, json={'expected_revision': 2})
            self.assertEqual(restored.json()['properties'], revision)
        with self.client() as client:
            self.assertEqual(client.get(path + '/content').json()['properties'], revision)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone(), ('ok',))
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_rejects_unapproved_palettes_and_malformed_tags(self):
        with self.client() as client:
            page = client.post('/api/v1/pages', headers=HEADERS, json={'title': 'Local sample'}).json()
            path = '/api/v1/pages/' + page['id'] + '/properties'
            for invalid in ({'theme': 'other'}, {'tab_color': None}, {'tags': ['a\x00b']}, {'tags': ['a' * 33]},
                            {'tags': [str(i) for i in range(17)]}, {'external': True}):
                with self.subTest(invalid=invalid):
                    self.assertEqual(client.patch(path, headers=HEADERS, json={
                        'expected_revision': 0, **invalid,
                    }).status_code, 422)
            self.assertEqual(client.patch(path, json={'expected_revision': 0, 'theme': 'dark'}).status_code, 403)

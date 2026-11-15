"""Synthetic integration coverage for the v0.12 template-to-page flow."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Barrier
from unittest import TestCase
from uuid import uuid4

from fastapi.testclient import TestClient

from services.local_api.app import create_app


BASE_URL = "http://127.0.0.1:8765"
HEADERS = {"X-EAW-Request": "local-template-editor"}
TEMPLATE_PAGE_URL = "/api/v1/pages/from-template"
LEGACY_FIXTURE = Path(__file__).parent / "spec" / "v011_synthetic.sql"
LEGACY_PARENT_ID = "00000000-0000-4000-8000-000000000011"
LEGACY_CHILD_ID = "00000000-0000-4000-8000-000000000012"


class TemplatePagesV012Tests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db_path = Path(self.temp.name) / "workspace.db"

    def client(self, app=None, **kwargs):
        return TestClient(
            app if app is not None else create_app(db_path=self.db_path),
            base_url=BASE_URL,
            client=("127.0.0.1", 9000),
            **kwargs,
        )

    def create_page(self, client, template_id="pm-plan", request_id=None, **extra):
        return client.post(
            TEMPLATE_PAGE_URL,
            headers=HEADERS,
            json={"template_id": template_id, "request_id": request_id or str(uuid4()), **extra},
        )

    def assert_integrity(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchall(), [("ok",)])
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_all_152_templates_create_independent_structured_pages(self):
        with self.client() as client:
            catalog = client.get("/api/v1/templates").json()
            legacy = [item for item in catalog["items"] if not item["id"].startswith("library-")]
            self.assertEqual(len(legacy), 152)
            page_ids, block_ids = set(), set()
            for template in legacy:
                with self.subTest(template_id=template["id"]):
                    response = self.create_page(client, template["id"])
                    self.assertEqual(response.status_code, 201, response.text)
                    page = response.json()
                    self.assertEqual(page["title"], template["name"])
                    self.assertEqual(page["template_id"], template["id"])
                    self.assertEqual(page["template_version"], template["version"])
                    self.assertEqual(page["revision"], 1)
                    self.assertEqual(page["scope"], "local_private")
                    self.assertTrue(page["from_template"])
                    self.assertTrue(page["blocks"])
                    self.assertNotIn(page["id"], page_ids)
                    page_ids.add(page["id"])
                    headings = {
                        block["content"] for block in page["blocks"]
                        if block["type"] == "heading_2"
                    }
                    if template["id"] != "pm-plan":
                        self.assertTrue({field["label"] for field in template["fields"]} <= headings)
                    else:
                        self.assertTrue({"프로젝트 개요", "주요 목표", "추진 일정", "리스크 및 Action Items"} <= headings)
                    for block in page["blocks"]:
                        self.assertNotIn(block["id"], block_ids)
                        block_ids.add(block["id"])
                        if block["type"] == "table":
                            rows = json.loads(block["content"])
                            self.assertTrue(rows and rows[0])
                            self.assertTrue(all(len(row) == len(rows[0]) for row in rows))
                            self.assertTrue(all(isinstance(cell, str) for row in rows for cell in row))
                    self.assertEqual(
                        client.get(f"/api/v1/pages/{page['id']}/content").json(), page
                    )
            tree = client.get("/api/v1/pages/tree").json()
            self.assertEqual({item["id"] for item in tree["items"]}, page_ids)
            self.assertEqual(client.get("/api/v1/templates").json(), catalog)
        self.assert_integrity()

    def test_editor_history_and_snapshot_survive_reopen(self):
        request_id = str(uuid4())
        with self.client() as client:
            baseline_catalog = client.get("/api/v1/templates").json()
            response = self.create_page(client, request_id=request_id)
            self.assertEqual(response.status_code, 201, response.text)
            initial = response.json()
            page_url = f"/api/v1/pages/{initial['id']}"
            table = next(block for block in initial["blocks"] if block["type"] == "table")
            todo = next(block for block in initial["blocks"] if block["type"] == "todo")
            rows = json.loads(table["content"])
            rows[1][0] = "Editable milestone"
            edited = [
                ({**block, "content": json.dumps(rows)} if block == table else
                 {**block, "content": "Editable action", "checked": True} if block == todo else
                 block)
                for block in initial["blocks"]
            ]
            response = client.put(
                f"{page_url}/content", headers=HEADERS,
                json={"expected_revision": 1, "title": "Synthetic launch", "blocks": edited},
            )
            self.assertEqual(response.status_code, 200, response.text)
            saved = response.json()
            self.assertEqual(saved["revision"], 2)
            self.assertEqual(saved["title"], "Synthetic launch")
            no_change = client.put(
                f"{page_url}/content", headers=HEADERS,
                json={"expected_revision": 2, "title": saved["title"], "blocks": saved["blocks"]},
            )
            self.assertEqual(no_change.status_code, 200, no_change.text)
            self.assertEqual(no_change.json(), saved)
            stale = client.put(
                f"{page_url}/content", headers=HEADERS,
                json={"expected_revision": 1, "title": "Stale", "blocks": []},
            )
            self.assertEqual(stale.status_code, 409, stale.text)
            fresh = self.create_page(client).json()
            self.assertNotEqual(fresh["id"], initial["id"])
            self.assertEqual(fresh["title"], initial["title"])
            self.assertEqual(
                [(item["type"], item["content"], item["checked"]) for item in fresh["blocks"]],
                [(item["type"], item["content"], item["checked"]) for item in initial["blocks"]],
            )
            self.assertTrue({b["id"] for b in fresh["blocks"]}.isdisjoint(b["id"] for b in initial["blocks"]))
            self.assertEqual(client.get("/api/v1/templates").json(), baseline_catalog)

        with self.client() as restarted:
            self.assertEqual(restarted.get(f"{page_url}/content").json(), saved)
            retry = self.create_page(restarted, request_id=request_id)
            self.assertEqual(retry.status_code, 200, retry.text)
            self.assertEqual(retry.json()["id"], initial["id"])
            self.assertEqual(restarted.get(f"{page_url}/content").json(), saved)
            history = restarted.get(f"{page_url}/history")
            self.assertEqual(history.status_code, 200, history.text)
            self.assertEqual(
                {item["revision"]: item["title"] for item in history.json()["items"]},
                {1: initial["title"], 2: "Synthetic launch"},
            )
            old = restarted.get(f"{page_url}/history/1")
            self.assertEqual(old.status_code, 200, old.text)
            self.assertEqual(old.json()["blocks"], initial["blocks"])
            self.assertEqual(old.json()["title"], initial["title"])
            latest = restarted.get(f"{page_url}/history/2")
            self.assertEqual(latest.status_code, 200, latest.text)
            self.assertEqual(latest.json()["blocks"], saved["blocks"])
            self.assertEqual(restarted.get(f"{page_url}/history/999").status_code, 404)
        self.assert_integrity()

    def test_same_request_is_idempotent_across_simultaneous_clients(self):
        app = create_app(db_path=self.db_path)
        request_id = str(uuid4())
        synchronize = Barrier(2)

        def submit():
            with self.client(app) as client:
                synchronize.wait(timeout=5)
                return self.create_page(client, request_id=request_id)

        with ThreadPoolExecutor(max_workers=2) as threads:
            first = threads.submit(submit)
            second = threads.submit(submit)
            results = [first.result(timeout=15), second.result(timeout=15)]
        self.assertEqual(sorted(res.status_code for res in results), [200, 201])
        self.assertEqual(len({res.json()["id"] for res in results}), 1)

        with self.client(app) as client:
            tree = client.get("/api/v1/pages/tree").json()["items"]
            self.assertEqual(len(tree), 1)
            reused = self.create_page(client, "general-meeting", request_id)
            self.assertEqual(reused.status_code, 409, reused.text)
            parent = client.post("/api/v1/pages", headers=HEADERS, json={"title": "Parent"}).json()
            reused = self.create_page(client, request_id=request_id, parent_id=parent["id"])
            self.assertEqual(reused.status_code, 409, reused.text)
            child = self.create_page(client, parent_id=parent["id"])
            self.assertEqual(child.status_code, 201, child.text)
            self.assertEqual(child.json()["parent_id"], parent["id"])
            # Block IDs belong to individual pages and cannot be reused on a save.
            first_page = results[0].json()
            collision = client.put(
                f"/api/v1/pages/{child.json()['id']}/content", headers=HEADERS,
                json={"expected_revision": 1, "title": "Collision", "blocks": first_page["blocks"]},
            )
            self.assertEqual(collision.status_code, 409, collision.text)
        self.assert_integrity()

    def test_failed_template_block_insert_rolls_back_and_retry_succeeds(self):
        request_id = str(uuid4())
        with self.client(raise_server_exceptions=False) as client:
            with closing(sqlite3.connect(self.db_path)) as db:
                db.executescript(
                    """
                    CREATE TRIGGER qa_fail_second_template_block
                    BEFORE INSERT ON page_blocks WHEN NEW.position = 1
                    BEGIN SELECT RAISE(ABORT, 'Synthetic write failure'); END;
                    """
                )
            failed = self.create_page(client, request_id=request_id)
            self.assertGreaterEqual(failed.status_code, 400, failed.text)
            with closing(sqlite3.connect(self.db_path)) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM documents").fetchone()[0], 0)
                self.assertEqual(db.execute("SELECT count(*) FROM page_blocks").fetchone()[0], 0)
                db.execute("DROP TRIGGER qa_fail_second_template_block")
                db.commit()
            retry = self.create_page(client, request_id=request_id)
            self.assertEqual(retry.status_code, 201, retry.text)
            page_id = retry.json()["id"]
            history = client.get(f"/api/v1/pages/{page_id}/history").json()
            self.assertEqual([item["revision"] for item in history["items"]], [1])
        self.assert_integrity()

    def test_failed_content_save_keeps_current_page_and_history(self):
        with self.client(raise_server_exceptions=False) as client:
            response = self.create_page(client)
            self.assertEqual(response.status_code, 201, response.text)
            original = response.json()
            content_url = f"/api/v1/pages/{original['id']}/content"
            history_url = f"/api/v1/pages/{original['id']}/history"
            update = {
                "expected_revision": original["revision"],
                "title": "New editor title",
                "blocks": original["blocks"],
            }
            with closing(sqlite3.connect(self.db_path)) as db:
                db.executescript(
                    """
                    CREATE TRIGGER qa_fail_content_replacement
                    BEFORE INSERT ON page_blocks WHEN NEW.position = 1
                    BEGIN SELECT RAISE(ABORT, 'Synthetic save failure'); END;
                    """
                )
            failed = client.put(content_url, headers=HEADERS, json=update)
            self.assertGreaterEqual(failed.status_code, 400, failed.text)
            self.assertEqual(client.get(content_url).json(), original)
            history = client.get(history_url).json()
            self.assertEqual([item["revision"] for item in history["items"]], [1])
            with closing(sqlite3.connect(self.db_path)) as db:
                db.execute("DROP TRIGGER qa_fail_content_replacement")
                db.commit()
            saved = client.put(content_url, headers=HEADERS, json=update)
            self.assertEqual(saved.status_code, 200, saved.text)
            self.assertEqual(saved.json()["revision"], 2)
        self.assert_integrity()

    def test_create_and_editor_reject_unsupported_requests_without_mutation(self):
        with self.client() as client:
            unknown = self.create_page(client, "nonexistent-template")
            invalid_key = self.create_page(client, request_id="invalid request id")
            missing_parent = self.create_page(client, parent_id=str(uuid4()))
            extra_field = self.create_page(client, scope="shared")
            self.assertEqual(unknown.status_code, 404, unknown.text)
            self.assertEqual(invalid_key.status_code, 422, invalid_key.text)
            self.assertIn(missing_parent.status_code, (404, 422), missing_parent.text)
            self.assertEqual(extra_field.status_code, 422, extra_field.text)
            payload = {"template_id": "pm-plan", "request_id": str(uuid4())}
            remote = client.post(
                TEMPLATE_PAGE_URL, headers={**HEADERS, "Origin": "https://example.invalid"},
                json=payload,
            )
            self.assertEqual(remote.status_code, 403, remote.text)
            no_marker = client.post(TEMPLATE_PAGE_URL, json=payload)
            self.assertEqual(no_marker.status_code, 403, no_marker.text)
            self.assertEqual(client.get("/api/v1/pages/tree").json()["items"], [])

            created = self.create_page(client)
            self.assertEqual(created.status_code, 201, created.text)
            page = created.json()
            url = f"/api/v1/pages/{page['id']}/content"
            for block_type, content in (
                ("video", "Blocked"),
                ("embed", "Blocked"),
                ("table", "Not JSON"),
                ("table", json.dumps([["Title", "Owner"], ["Missing owner"]])),
                ("table", json.dumps([[1, 2]])),
                ("table", json.dumps([["", "\u0000"]])),
                ("table", json.dumps([[""] * 50])),
            ):
                with self.subTest(block_type=block_type, content=content):
                    invalid = client.put(
                        url, headers=HEADERS,
                        json={
                            "expected_revision": 1, "title": "Do not save",
                            "blocks": [{"id": str(uuid4()), "type": block_type, "content": content}],
                        },
                    )
                    self.assertEqual(invalid.status_code, 422, invalid.text)
            legacy_api_edit = client.put(
                f"/api/v1/documents/{page['id']}", headers=HEADERS,
                json={"expected_revision": 1, "title": "Use Canvas", "values": {"goal": "Synthetic"}},
            )
            self.assertEqual(legacy_api_edit.status_code, 409, legacy_api_edit.text)
            noncanonical = client.put(
                url, headers=HEADERS,
                json={
                    "expected_revision": 1, "title": "Do not save",
                    "blocks": [{"id": "a" * 36, "type": "paragraph", "content": "New noncanonical ID"}],
                },
            )
            self.assertEqual(noncanonical.status_code, 422, noncanonical.text)
            self.assertEqual(client.get(url).json(), page)
            self.assertEqual(
                [item["revision"] for item in client.get(url.removesuffix("/content") + "/history").json()["items"]],
                [1],
            )
        self.assert_integrity()

    def test_pre_v012_sqlite_keeps_pages_tasks_events_and_links(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            db.executescript(LEGACY_FIXTURE.read_text(encoding="utf-8"))
        expected_child_url = f"/api/v1/pages/{LEGACY_CHILD_ID}/content"

        with self.client() as client:
            document = client.get(f"/api/v1/documents/{LEGACY_PARENT_ID}").json()
            self.assertEqual(document["values"], {"agenda": "Legacy template values"})
            child = client.get(expected_child_url).json()
            self.assertEqual(child["parent_id"], LEGACY_PARENT_ID)
            self.assertEqual(child["revision"], 2)
            self.assertEqual(child["blocks"][0]["content"], "Preserve this checked item")
            self.assertTrue(child["blocks"][0]["checked"])
            self.assertEqual(child["blocks"][1]["id"], "a" * 36)
            self.assertFalse(child["from_template"])
            child_history_url = f"/api/v1/pages/{LEGACY_CHILD_ID}/history"
            before_edit = client.get(f"{child_history_url}/2")
            self.assertEqual(before_edit.status_code, 200, before_edit.text)
            self.assertEqual(before_edit.json()["blocks"], child["blocks"])
            renamed = client.put(
                expected_child_url, headers=HEADERS,
                json={"expected_revision": 2, "title": "Renamed after migration", "blocks": child["blocks"]},
            )
            self.assertEqual(renamed.status_code, 200, renamed.text)
            self.assertEqual(renamed.json()["revision"], 3)
            self.assertEqual(client.get(f"{child_history_url}/2").json(), before_edit.json())
            projects = client.get("/api/v1/projects").json()["items"]
            tasks = client.get("/api/v1/tasks").json()["items"]
            self.assertEqual(tasks[0]["project_id"], projects[0]["id"])
            self.assertEqual(tasks[0]["document_id"], LEGACY_PARENT_ID)
            feed = client.get("/api/v1/calendar/feed?start=2026-12-14&end=2026-12-17")
            self.assertEqual(feed.status_code, 200, feed.text)
            items = feed.json()["items"]
            self.assertEqual({item["kind"] for item in items}, {"task", "event"})
            self.assertEqual(next(item for item in items if item["kind"] == "event")["document_id"], LEGACY_CHILD_ID)
            created = self.create_page(client, parent_id=LEGACY_CHILD_ID)
            self.assertEqual(created.status_code, 201, created.text)
            self.assertEqual(created.json()["parent_id"], LEGACY_CHILD_ID)
            created_url = f"/api/v1/pages/{created.json()['id']}/content"

        with self.client() as restarted:
            self.assertEqual(restarted.get(expected_child_url).json(), renamed.json())
            self.assertEqual(restarted.get(f"{child_history_url}/2").json(), before_edit.json())
            self.assertEqual(restarted.get(created_url).json(), created.json())
            self.assertEqual(restarted.get(f"/api/v1/documents/{LEGACY_PARENT_ID}").json(), document)
        self.assert_integrity()

    def test_new_page_is_visible_after_existing_page_tree_reaches_500(self):
        with self.client() as client:
            with closing(sqlite3.connect(self.db_path)) as db:
                db.executemany(
                    """INSERT INTO documents (
                           id, template_id, template_version, title, field_values, created_at, updated_at
                       ) VALUES (?, '__blank_page__', 1, 'Existing synthetic page', '{}',
                                 '2020-01-01T00:00:00+00:00', '2020-01-01T00:00:00+00:00')""",
                    ((str(uuid4()),) for _ in range(500)),
                )
                db.commit()
            created = self.create_page(client)
            self.assertEqual(created.status_code, 201, created.text)
            tree = client.get("/api/v1/pages/tree").json()["items"]
            self.assertEqual(len(tree), 501)
            self.assertIn(created.json()["id"], {item["id"] for item in tree})
        self.assert_integrity()

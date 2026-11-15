"""Read-only previews and their equivalence to created v0.13 pages."""
from contextlib import closing
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from uuid import uuid4

from fastapi.testclient import TestClient

from services.local_api.app import create_app


BASE = "http://127.0.0.1:8765"
HEADERS = {"X-EAW-Request": "local-template-editor"}
TEMPLATES = "/api/v1/templates"
CREATE_PAGE = "/api/v1/pages/from-template"


def block_structure(page):
    return [{key: value for key, value in block.items() if key != "id"} for block in page["blocks"]]


class TemplateLibraryV013Tests(TestCase):
    def setUp(self):
        temp = self.enterContext(TemporaryDirectory())
        self.db_path = Path(temp) / "workspace.db"
        self.app = create_app(self.db_path)
        self.client = self.enterContext(TestClient(self.app, base_url=BASE, client=("127.0.0.1", 9000)))

    def test_preview_is_read_only_and_matches_every_created_page(self):
        original = self.client.get(TEMPLATES).json()
        self.assertEqual(original["total"], 272)
        self.assertEqual(original["total"], len({item["id"] for item in original["items"]}))
        previews = {}
        for template in original["items"]:
            with self.subTest(preview=template["id"]):
                response = self.client.get(f"{TEMPLATES}/{template['id']}/preview")
                self.assertEqual(response.status_code, 200, response.text)
                preview = response.json()
                self.assertEqual(preview["id"], template["id"])
                self.assertEqual(preview["title"], template["name"])
                self.assertTrue(preview["blocks"])
                self.assertEqual(template["source_type"], "original")
                previews[template["id"]] = block_structure(preview)

        with closing(sqlite3.connect(self.db_path)) as db:
            for table in ("documents", "page_blocks", "page_history", "page_template_requests"):
                self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone(), (0,))

        all_ids = set()
        all_block_ids = set()
        for template in original["items"]:
            with self.subTest(creation=template["id"]):
                response = self.client.post(
                    CREATE_PAGE, headers=HEADERS,
                    json={"template_id": template["id"], "request_id": str(uuid4())},
                )
                self.assertEqual(response.status_code, 201, response.text)
                page = response.json()
                self.assertEqual(page["title"], template["name"])
                self.assertEqual(page["revision"], 1)
                self.assertEqual(page["template_id"], template["id"])
                self.assertEqual(page["template_version"], template["version"])
                self.assertEqual(page["scope"], "local_private")
                self.assertTrue(page["from_template"])
                self.assertEqual(block_structure(page), previews[template["id"]])
                self.assertNotIn(page["id"], all_ids)
                all_ids.add(page["id"])
                for block in page["blocks"]:
                    self.assertNotIn(block["id"], all_block_ids)
                    all_block_ids.add(block["id"])
                self.assertEqual(self.save_page(page, page["title"], page["blocks"]), page)
                self.assertEqual(self.client.get(f"/api/v1/pages/{page['id']}/content").json(), page)

        tree = self.client.get("/api/v1/pages/tree").json()
        self.assertEqual({item["id"] for item in tree["items"]}, all_ids)
        self.assertEqual(self.client.get(TEMPLATES).json(), original)
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_preview_preserves_csp_and_loopback_boundary(self):
        path = f"{TEMPLATES}/pm-plan/preview"
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        policy = response.headers["Content-Security-Policy"]
        for directive in ("connect-src 'self'", "frame-src 'none'", "media-src 'none'"):
            self.assertIn(directive, policy)
        self.assertEqual(self.client.get(path, headers={"Origin": "https://example.invalid"}).status_code, 403)
        self.assertEqual(self.client.get(path, headers={"Host": "example.invalid"}).status_code, 403)
        self.assertEqual(self.client.get(f"{TEMPLATES}/not-a-bundled-template/preview").status_code, 404)
        self.assertEqual(self.client.post(path, json={}, headers=HEADERS).status_code, 405)
        with TestClient(self.app, base_url=BASE, client=("192.0.2.11", 9000)) as remote:
            self.assertEqual(remote.get(path).status_code, 403)

    def blank_page(self, title):
        response = self.client.post("/api/v1/pages", json={"title": title}, headers=HEADERS)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def project_plan(self, title=None, parent_id=None):
        response = self.client.post(CREATE_PAGE, headers=HEADERS, json={
            "template_id": "pm-plan", "request_id": str(uuid4()), "parent_id": parent_id,
        })
        self.assertEqual(response.status_code, 201, response.text)
        page = response.json()
        return self.save_page(page, title, page["blocks"]) if title else page

    def save_page(self, page, title, blocks):
        response = self.client.put(f"/api/v1/pages/{page['id']}/content", headers=HEADERS, json={
            "title": title, "expected_revision": page["revision"], "blocks": blocks,
        })
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_duplicate_uses_independent_blocks_and_has_persistent_request_identity(self):
        parent = self.blank_page("Duplicate test parent")
        source = self.project_plan("Duplicate test source", parent["id"])
        base = f"/api/v1/pages/{source['id']}"
        url = base + "/duplicate"
        payload = {"expected_revision": source["revision"], "request_id": str(uuid4())}
        first = self.client.post(url, headers=HEADERS, json=payload)
        self.assertEqual(first.status_code, 201, first.text)
        duplicate = first.json()
        self.assertNotEqual(duplicate["id"], source["id"])
        self.assertEqual(duplicate["parent_id"], parent["id"])
        self.assertEqual(duplicate["title"], source["title"] + " (복제본)")
        self.assertEqual(duplicate["revision"], 1)
        self.assertEqual(duplicate["template_id"], source["template_id"])
        self.assertTrue(duplicate["from_template"])
        self.assertEqual(block_structure(duplicate), block_structure(source))
        self.assertTrue({b["id"] for b in duplicate["blocks"]}.isdisjoint(b["id"] for b in source["blocks"]))
        updated_copy = self.save_page(duplicate, "Independent copy", duplicate["blocks"])
        self.assertEqual(self.client.get(base + "/content").json(), source)

        self.assertEqual(self.client.post(url, headers=HEADERS, json={
            "expected_revision": 1, "request_id": str(uuid4()),
        }).status_code, 409)
        self.assertEqual(self.client.post(url, headers=HEADERS, json={
            **payload, "expected_revision": 1,
        }).status_code, 409)
        with TestClient(create_app(self.db_path), base_url=BASE, client=("127.0.0.1", 9000)) as restarted:
            replay = restarted.post(url, headers=HEADERS, json=payload)
            self.assertEqual(replay.status_code, 200, replay.text)
            self.assertEqual(replay.json()["id"], updated_copy["id"])
            self.assertEqual(restarted.get(f"/api/v1/pages/{duplicate['id']}/content").json(), updated_copy)
            self.assertEqual(len(restarted.get("/api/v1/pages/tree").json()["items"]), 3)

    def test_restore_adds_new_revision_without_reparenting_or_discarding_edits_from_history(self):
        old_parent = self.blank_page("Old parent")
        new_parent = self.blank_page("New parent")
        initial = self.project_plan(parent_id=old_parent["id"])
        base = f"/api/v1/pages/{initial['id']}"
        edited = self.save_page(initial, "Later edit", [
            {"id": str(uuid4()), "type": "paragraph", "content": "A later synthetic change", "checked": False},
        ])
        moved = self.client.put(base + "/move", headers=HEADERS, json={
            "expected_revision": edited["revision"], "parent_id": new_parent["id"],
        })
        self.assertEqual(moved.status_code, 200, moved.text)
        url = base + "/history/1/restore"
        live = moved.json()["revision"]
        stale = self.client.post(url, headers=HEADERS, json={"expected_revision": edited["revision"]})
        self.assertEqual(stale.status_code, 409, stale.text)
        unknown = self.client.post(base + "/history/999/restore", headers=HEADERS, json={"expected_revision": live})
        self.assertEqual(unknown.status_code, 404, unknown.text)
        blocked = self.client.post(url, json={"expected_revision": live})
        self.assertEqual(blocked.status_code, 403, blocked.text)
        restore = self.client.post(url, headers=HEADERS, json={"expected_revision": live})
        self.assertEqual(restore.status_code, 200, restore.text)
        restored = restore.json()
        self.assertEqual(restored["id"], initial["id"])
        self.assertEqual(restored["title"], initial["title"])
        self.assertEqual(restored["blocks"], initial["blocks"])
        self.assertEqual(restored["parent_id"], new_parent["id"])
        self.assertEqual(restored["revision"], live + 1)
        self.assertEqual(self.client.get(base + "/history/2").json()["blocks"], edited["blocks"])
        self.assertEqual(self.client.get(base + "/content").json(), restored)

    def test_page_search_distinguishes_live_text_table_cells_and_legacy_values(self):
        folder = self.blank_page("Casefold ① Filter")
        source = self.project_plan()
        legacy_response = self.client.post("/api/v1/documents", headers=HEADERS, json={
            "title": "Legacy form", "template_id": "general-meeting",
            "values": {"agenda": "연계된 legacy private value"},
        })
        self.assertEqual(legacy_response.status_code, 201, legacy_response.text)
        legacy = legacy_response.json()
        blocks = [
            {"id": str(uuid4()), "type": "paragraph", "content": "Bracket %_ and ＡＢＣ", "checked": False},
            {"id": str(uuid4()), "type": "table",
             "content": json.dumps([["Owner", "Due"], ["업무 담당자", "2027년 1월"]]), "checked": False},
        ]
        edited = self.save_page(source, "First edited title", blocks)
        for query, expected_ids in (
            ("ＣＡＳＥＦＯＬＤ 1", {folder["id"]}),
            ("abc", {source["id"]}),
            ("%_", {source["id"]}),
            ("업무 담당자", {source["id"]}),
            ("legacy PRIVATE value", {legacy["id"]}),
            (" ", set()),
            ("not present", set()),
        ):
            with self.subTest(query=query):
                response = self.client.get("/api/v1/search/pages", params={"q": query})
                self.assertEqual(response.status_code, 200, response.text)
                items = response.json()["items"]
                self.assertEqual({item["id"] for item in items}, expected_ids)
                self.assertTrue(all("blocks" not in item and "values" not in item for item in items))
        self.save_page(edited, "Replaced text", [])
        live = self.client.get("/api/v1/search/pages", params={"q": "업무 담당자"})
        self.assertEqual(live.json()["items"], [])
        self.assertEqual(self.client.get("/api/v1/search/pages", params={"q": "x" * 121}).status_code, 422)

"""Headless Chromium validation for the v0.13 gallery against an isolated local server."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from playwright.sync_api import expect, sync_playwright


import workspace_v012 as previous

ROOT = Path(__file__).resolve().parents[2]
OLD_CATALOG = ROOT / "services/local_api/catalog.json"


def stripped_blocks(data):
    return [{key: value for key, value in block.items() if key != "id"} for block in data["blocks"]]


def gallery(page):
    page.locator("#nav-library").click()
    expect(page.locator("#library-panel")).to_be_visible()


def tile(page, ident):
    return page.locator(".template-card-shell").filter(
        has=page.locator(f'.template-card[data-template-id="{ident}"]')
    )

def choose_appearance(page, *, theme=None, default=None, current=None):
    page.locator("#workspace-theme-button").click()
    expect(page.locator("#workspace-theme-dialog")).to_be_visible()
    if theme is not None:
        page.locator("#workspace-color-theme").select_option(theme)
    if default is not None:
        page.locator("#workspace-default-background").select_option(default)
    if current is not None:
        page.locator("#workspace-page-background").select_option(current)
    page.locator("#workspace-theme-close").click()

def workspace_actions(page, url, page_id, name, record, evidence):
    expect(page.locator("html")).to_have_attribute("data-workspace-theme", "dark")
    expect(page.locator("#canvas-panel")).to_have_attribute("data-page-background", "grid")
    expect(page.locator("#canvas-favorite")).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#canvas-shortcuts-favorites")).to_contain_text("v0.13 browser QA plan")
    expect(page.locator("#canvas-shortcuts-recent")).to_contain_text("v0.13 browser QA plan")
    page.locator("#nav-documents").click()
    documents = page.locator("#document-list")
    page.locator("#doc-search").fill("not a workspace QA match")
    expect(documents).to_contain_text("일치하는 문서가 없습니다")
    page.locator("#doc-search").fill("Editable local QA content")
    match = documents.locator(".doc-row")
    expect(match).to_have_count(1)
    expect(match).to_contain_text("v0.13 browser QA plan")
    match.click()
    expect(page.locator("#canvas-title")).to_have_value("v0.13 browser QA plan")
    with page.expect_response(lambda response: response.url.endswith(f"/pages/{page_id}/duplicate")) as duplication:
        page.locator("#canvas-duplicate").evaluate("(button) => { button.click(); button.click(); }")
    assert duplication.value.status == 201, duplication.value.text()
    copy = duplication.value.json()
    expect(page.locator("#canvas-title")).to_have_value("v0.13 browser QA plan (복제본)")
    expect(page.locator("#canvas-panel")).to_have_attribute("data-page-background", "grid")
    assert stripped_blocks(copy) == stripped_blocks(record)
    assert {b["id"] for b in copy["blocks"]}.isdisjoint(b["id"] for b in record["blocks"])
    assert len(previous.api_items(url, "/api/v1/pages/tree")) == 3
    page.locator(f'#sidebar-page-tree .sidebar-page[data-page-id="{page_id}"]').click()
    expect(page.locator("#canvas-panel")).to_have_attribute("data-page-background", "grid")
    page.locator("#canvas-history").click()
    history = page.locator("#canvas-history-dialog")
    expect(history).to_be_visible()
    history.locator('[data-revision="1"]').click()
    expect(history.locator("#canvas-history-preview")).to_contain_text(name)
    previous.screenshot(page, evidence, "05-history-restore.png")
    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_response(
        lambda response: response.url.endswith(f"/pages/{page_id}/history/1/restore")
    ) as result:
        history.locator("#canvas-history-restore").click()
    assert result.value.status == 200, result.value.text()
    restored = result.value.json()
    expect(page.locator("#canvas-title")).to_have_value(name)
    assert restored["revision"] == record["revision"] + 1
    assert previous.api_json(url, f"/api/v1/pages/{page_id}/history/{record['revision']}")["blocks"] == record["blocks"]
    print("PASS persisted themes and shortcuts, body search, duplicate and history restore", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', type=Path)
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    evidence = args.screenshots
    with TemporaryDirectory() as temp, sync_playwright() as playwright:
        temp = Path(temp)
        os.environ["EAW_DATA_DIR"] = str(temp / "module-db")
        path = temp / "workspace.db"
        port = previous.free_port()
        browser = playwright.chromium.launch(executable_path=args.chromium)
        context = browser.new_context(viewport={"width": 1440, "height": 1050}, locale="ko-KR")
        page = context.new_page()
        page.set_default_timeout(10_000)
        requests, errors = [], []
        page.on("request", lambda request: requests.append((request.method, request.url)))
        page.on("pageerror", lambda error: errors.append(str(error)))
        url = f"http://127.0.0.1:{port}"

        def only_loopback(route):
            if not route.request.url.startswith(url + "/"):
                route.abort()
            else:
                route.continue_()

        page.route("**/*", only_loopback)
        with previous.local_server(path, port):
            assert previous.api_json(url, "/api/v1/health")["version"] == "0.14.0"
            catalog = previous.api_json(url, "/api/v1/templates")
            old = {template["id"] for template in json.loads(OLD_CATALOG.read_text(encoding="utf-8"))}
            new = [item for item in catalog["items"] if item["id"] not in old]
            assert len(new) > 0 and old <= {item["id"] for item in catalog["items"]}
            template = next(item for item in new if item.get("collection") and item.get("tags"))
            ident, name = template["id"], template["name"]
            preview_url = f"/api/v1/templates/{ident}/preview"
            catalog_total = str(catalog["total"])

            page.goto(url, wait_until="networkidle")
            gallery(page)
            expect(page.locator("#result-count")).to_contain_text(catalog_total)
            expect(page.locator(".template-card")).to_have_count(24)
            previous.screenshot(page, evidence, "01-gallery.png")
            page.locator("#template-more").click()
            expect(page.locator(".template-card")).to_have_count(48)
            recommended = page.locator('[data-discovery="recommended"]')
            recommended.click()
            expect(recommended).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#library-results-title")).to_contain_text("추천")
            popular = page.locator('[data-discovery="popular_category"]')
            popular.click()
            expect(popular).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#library-results-title")).to_contain_text("인기")
            page.locator('[data-discovery="all"]').click()

            collection = page.locator(".collection-filter").filter(has_text=template["collection"])
            assert collection.count() == 1, template["collection"]
            collection.click()
            expect(collection).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#library-results-title")).to_have_text(template["collection"])
            search = page.locator("#template-search")
            search.fill("this-query-has-no-match-89245")
            expect(page.locator(".library-empty")).to_be_visible()
            search.fill(name)
            selected = tile(page, ident)
            expect(selected).to_have_count(1)

            star = selected.locator(".template-save-button")
            star.click()
            expect(star).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#template-saved-count")).to_have_text("1")
            assert previous.api_items(url, "/api/v1/pages/tree") == []
            page.reload(wait_until="networkidle")
            gallery(page)
            page.locator('[data-discovery="saved"]').click()
            expect(page.locator("#template-saved-count")).to_have_text("1")
            expect(tile(page, ident)).to_have_count(1)

            with page.expect_response(lambda response: response.url.endswith(preview_url)) as result:
                tile(page, ident).locator(".template-preview-button").click()
            assert result.value.ok, result.value.text()
            expected_preview = result.value.json()
            modal = page.locator("#template-preview-dialog")
            expect(modal).to_be_visible()
            expect(modal.locator("#template-preview-title")).to_have_text(name)
            content = modal.locator("#template-preview-content")
            expect(content).to_have_attribute("aria-busy", "false")
            assert content.locator("input, textarea, [contenteditable]").count() == 0
            assert previous.api_items(url, "/api/v1/pages/tree") == []
            previous.screenshot(page, evidence, "02-template-preview.png")
            page.keyboard.press("Escape")
            expect(modal).to_be_hidden()
            assert previous.api_items(url, "/api/v1/pages/tree") == []
            choose_appearance(page, default="paper")
            tile(page, ident).locator(".template-preview-button").click()
            expect(modal).to_be_visible()
            expect(content).to_have_attribute("aria-busy", "false")

            with page.expect_response(
                lambda response: response.url.endswith("/pages/from-template") and response.request.method == "POST"
            ) as creation:
                modal.locator("#template-preview-create").evaluate("(button) => { button.click(); button.click(); }")
            assert creation.value.status == 201, creation.value.text()
            created = creation.value.json()
            assert stripped_blocks(created) == stripped_blocks(expected_preview), ident
            page_id = created["id"]
            expect(page.locator("#canvas-title")).to_have_value(name)
            expect(page.locator("#canvas-panel")).to_have_attribute("data-page-background", "paper")
            expect(page.locator("#sidebar-page-tree .sidebar-page.selected")).to_contain_text(name)
            assert [value["id"] for value in previous.api_items(url, "/api/v1/pages/tree")] == [page_id]
            assert sum(method == "POST" and link.endswith("/pages/from-template") for method, link in requests) == 1
            page.locator("#canvas-title").fill("v0.13 browser QA plan")
            target = page.locator(".block-paragraph textarea").first
            expect(target).to_be_visible()
            target.fill("Editable local QA content")
            previous.saved(page)
            content_after_save = previous.api_json(url, f"/api/v1/pages/{page_id}/content")
            assert content_after_save["title"] == "v0.13 browser QA plan"
            assert any(block["content"] == "Editable local QA content" for block in content_after_save["blocks"])
            previous.screenshot(page, evidence, "03-editor-after-apply.png")
            page.locator("#canvas-favorite").click()
            expect(page.locator("#canvas-favorite")).to_have_attribute("aria-pressed", "true")
            choose_appearance(page, theme="dark", current="grid")
            expect(page.locator("html")).to_have_attribute("data-workspace-theme", "dark")
            expect(page.locator("#canvas-panel")).to_have_attribute("data-page-background", "grid")
            previous.screenshot(page, evidence, "04-dark-theme.png")

            # Preserve the v0.12 single-click entry point on a catalog card.
            gallery(page)
            page.locator('[data-discovery="all"]').click()
            page.locator("#template-search").fill("Project Plan")
            direct = tile(page, "pm-plan").locator(".template-card")
            expect(direct).to_have_count(1)
            direct.click()
            expect(page.locator("#canvas-title")).to_have_value("Project Plan")
            assert len(previous.api_items(url, "/api/v1/pages/tree")) == 2
            print(f"PASS {catalog_total} cards; tabs, collection, search, paging, local bookmarks, read-only preview, exactly-once apply, inline autosave, direct card", flush=True)

        with previous.local_server(path, port):
            page.goto(url, wait_until="networkidle")
            page.locator("#sidebar-page-tree .sidebar-page").filter(has_text="v0.13 browser QA plan").click()
            expect(page.locator("#canvas-title")).to_have_value("v0.13 browser QA plan")
            assert previous.api_json(url, f"/api/v1/pages/{page_id}/content")["blocks"] == content_after_save["blocks"]
            workspace_actions(page, url, page_id, name, content_after_save, evidence)
            assert not errors, errors
            assert requests and all(target.startswith(url + "/") for _, target in requests), requests
            with sqlite3.connect(path) as db:
                assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
                assert db.execute("PRAGMA foreign_key_check").fetchall() == []
            print(f"PASS SQLite/server restart; {len(set(link for _, link in requests))} unique loopback URLs; no browser errors", flush=True)
        browser.close()


if __name__ == "__main__":
    main()

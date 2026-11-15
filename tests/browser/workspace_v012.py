"""Synthetic end-to-end checks against the actual local app in Chromium.

Run from the repository root with an approved Playwright install and Chromium:
python tests/browser/workspace_v012.py --chromium /usr/bin/chromium --screenshots /tmp/evidence

The test starts its own loopback server on a free port and uses a temporary DB.
"""
from __future__ import annotations

import argparse
import json
import os
from contextlib import contextmanager
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from urllib.request import ProxyHandler, build_opener

from playwright.sync_api import Page, expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
TITLE = '프로젝트 계획서 · 합성 검증'
CELL = '1차 설계 검토'
NEW_HEADING = '브라우저에서 추가한 검토 항목'
TEMPLATE = 'pm-plan'
TEMPLATE_NAME = 'Project Plan'
# The test only connects to its own loopback process.
LOOPBACK_HTTP = build_opener(ProxyHandler({}))


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


@contextmanager
def local_server(database: Path, port: int):
    url = f'http://127.0.0.1:{port}'
    # Override the development port for isolation. Keep the production entry
    # point and its fixed loopback address unchanged.
    script = (
        'from pathlib import Path; import sys, uvicorn; '
        'from services.local_api.app import create_app; '
        'uvicorn.run(create_app(Path(sys.argv[1])), host="127.0.0.1", '
        'port=int(sys.argv[2]), access_log=False, server_header=False, log_level="error")'
    )
    env = {**os.environ, 'PYTHONUTF8': '1', 'NO_PROXY': '127.0.0.1,localhost'}
    with tempfile.TemporaryFile(mode='w+b') as log:
        server = subprocess.Popen(
            [sys.executable, '-c', script, str(database), str(port)],
            cwd=ROOT, env=env, stdout=log, stderr=log,
        )
        try:
            for _ in range(100):
                if server.poll() is not None:
                    break
                try:
                    with LOOPBACK_HTTP.open(url + '/api/v1/health', timeout=0.4) as response:
                        if json.load(response).get('status') == 'ok':
                            break
                except OSError:
                    time.sleep(0.1)
            else:
                log.seek(0)
                raise RuntimeError(f'Timed out waiting for app. {log.read().decode()}')
            if server.poll() is not None:
                log.seek(0)
                raise RuntimeError(f'App startup failed. {log.read().decode()}')
            yield url
        finally:
            server.terminate()
            server.wait(timeout=10)


def saved(page: Page) -> None:
    expect(page.locator('#canvas-dirty-flag')).to_contain_text('저장됨', timeout=8_000)


def api_json(url: str, endpoint: str) -> dict:
    with LOOPBACK_HTTP.open(url + endpoint, timeout=5) as response:
        return json.load(response)


def api_items(url: str, endpoint: str) -> list[dict]:
    return api_json(url, endpoint)['items']


def screenshot(page: Page, folder: Path | None, name: str) -> None:
    if folder:
        folder.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(folder / name), animations='disabled')


def create_and_edit(page: Page, url: str, folder: Path | None) -> str:
    response = page.goto(url)
    assert response and response.ok, (response.status, response.text()[:400]) if response else url
    if not page.locator('#nav-library').count():
        raise AssertionError({'url': page.url, 'headers': response.all_headers(), 'html': page.content()[:550]})
    page.locator('#nav-library').click()
    expect(page.locator('#result-count')).to_contain_text(str(api_json(url, '/api/v1/templates')['total']))
    screenshot(page, folder, '01-template-gallery.png')
    page.locator('#template-search').fill(TEMPLATE_NAME)
    card = page.locator(f'.template-card[data-template-id="{TEMPLATE}"]')
    expect(card).to_have_count(1)

    # Send two click events in one browser call while the first write is pending.
    with page.expect_response(lambda r: r.url.endswith('/pages/from-template') and r.request.method == 'POST') as result:
        card.evaluate('(card) => { card.click(); card.click(); }')
    assert result.value.status == 201, result.value.text()
    page_id = result.value.json()['id']
    expect(page.locator('#canvas-title')).to_have_value(TEMPLATE_NAME)
    expect(page.locator('#sidebar-page-tree .sidebar-page.selected')).to_contain_text(TEMPLATE_NAME)
    expect(page.locator('#editor-panel')).to_be_hidden()
    expect(page.locator('#canvas-template-edit')).to_be_hidden()
    assert [x['id'] for x in api_items(url, '/api/v1/pages/tree')] == [page_id]
    assert len(api_items(url, f'/api/v1/pages/{page_id}/history')) == 1

    page.locator('#canvas-title').fill(TITLE)
    page.locator('.block-todo input[type=checkbox]').first.check()
    table_cell = page.locator('.block-table textarea').nth(3)
    table_cell.fill(CELL)
    target = page.locator('.block-paragraph textarea').first
    target.press('End')
    target.press('Enter')
    page.keyboard.press('/')
    expect(page.locator('.canvas-slash-menu')).to_be_visible()
    screenshot(page, folder, '02-slash-command.png')
    page.keyboard.type('h2')
    page.keyboard.press('Enter')
    expect(page.locator('.block-heading_2 textarea:focus')).to_have_count(1)
    page.keyboard.insert_text(NEW_HEADING)
    saved(page)
    expect(page.locator('#sidebar-page-tree .sidebar-page.selected')).to_contain_text(TITLE)
    screenshot(page, folder, '03-edited-page.png')
    record = api_json(url, f'/api/v1/pages/{page_id}/content')
    assert record['title'] == TITLE
    assert any(b['type'] == 'todo' and b['checked'] for b in record['blocks'])
    assert any(b['type'] == 'table' and CELL in b['content'] for b in record['blocks'])
    assert any(b['type'] == 'heading_2' and b['content'] == NEW_HEADING for b in record['blocks'])
    assert len(api_items(url, f'/api/v1/pages/{page_id}/history')) >= 2

    page.locator('#canvas-history').click()
    history = page.locator('#canvas-history-dialog')
    expect(history).to_be_visible()
    history.locator('[data-revision="1"]').click()
    expect(history.locator('#canvas-history-preview')).to_contain_text(TEMPLATE_NAME)
    screenshot(page, folder, '04-page-history.png')
    history.locator('#canvas-history-close').click()
    return page_id


def reopen_and_verify(page: Page, url: str, page_id: str) -> None:
    response = page.goto(url)
    assert response and response.ok, (response.status, response.text()[:400]) if response else url
    page.locator('#sidebar-page-tree .sidebar-page').filter(has_text=TITLE).click()
    expect(page.locator('#canvas-title')).to_have_value(TITLE)
    expect(page.locator('.block-todo input[type=checkbox]').first).to_be_checked()
    expect(page.locator('.block-table textarea').nth(3)).to_have_value(CELL)
    assert [x['id'] for x in api_items(url, '/api/v1/pages/tree')] == [page_id]

    # Navigating before the debounce expires must flush the pending edit.
    last_edit = '이동 직전 편집한 합성 메모'
    page.locator('.block-paragraph textarea').first.fill(last_edit)
    page.locator('#nav-documents').click()
    expect(page.locator('#document-list')).to_contain_text(TITLE)
    current = api_json(url, f'/api/v1/pages/{page_id}/content')
    assert any(block['content'] == last_edit for block in current['blocks'])
    page.locator('#nav-projects').click()
    page.locator('#project-title').fill('Synthetic project')
    page.locator('#project-save').click()
    expect(page.locator('#project-list')).to_contain_text('Synthetic project')
    page.locator('#nav-database').click()
    page.locator('#task-title').fill('Synthetic task')
    page.locator('#task-project').select_option(label='Synthetic project')
    task_day = page.evaluate("""() => new Intl.DateTimeFormat('sv-SE', {
        timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit'
    }).format(new Date())""")
    page.locator('#task-due').fill(task_day)
    page.locator('#task-form button[type=submit]').click()
    expect(page.locator('#task-list')).to_contain_text('Synthetic task')
    page.locator('#task-view').select_option('board')
    expect(page.locator('#task-list .task-board')).to_contain_text('Synthetic task')
    page.locator('#nav-calendar').click()
    expect(page.locator('#calendar-grid')).to_contain_text('Synthetic task')
    page.locator('#cal-title').fill('Synthetic event')
    page.locator('#cal-start-date').fill(task_day)
    page.locator('#cal-end-date').fill(task_day)
    page.locator('#calendar-form button[type=submit]').click()
    expect(page.locator('#calendar-grid')).to_contain_text('Synthetic event')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', type=Path, help='Path to an installed Chromium binary')
    parser.add_argument('--screenshots', type=Path)
    parser.add_argument('--port', type=int, help='Reserve a specific free loopback port')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as temp, sync_playwright() as playwright:
        db = Path(temp) / 'workspace.db'
        port = args.port or free_port()
        browser = playwright.chromium.launch(executable_path=args.chromium)
        print(f'Chromium {browser.version}', flush=True)
        urls: set[str] = set()
        errors: list[str] = []

        def new_page() -> Page:
            page = browser.new_page(viewport={'width': 1440, 'height': 1050}, locale='ko-KR')
            page.set_default_timeout(8_000)
            page.on('request', lambda request: urls.add(request.url))
            page.on('pageerror', lambda error: errors.append(str(error)))
            return page

        with local_server(db, port) as url:
            first = new_page()
            page_id = create_and_edit(first, url, args.screenshots)
            first.close()
            print('PASS gallery → one page → sidebar → inline text/checklist/table → slash → autosave → history', flush=True)
        with local_server(db, port) as url:
            second = new_page()
            reopen_and_verify(second, url, page_id)
            second.close()
            print('PASS server restart → SQLite readback → flush before navigation → Documents/Projects/Task Table and Board/Calendar', flush=True)
        browser.close()

        with sqlite3.connect(db) as connection:
            assert connection.execute('PRAGMA integrity_check').fetchone() == ('ok',)
            assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
        assert not errors, errors
        assert urls and all(target.startswith(url + '/') for target in urls), urls
        print(f'PASS DB integrity and browser network stayed on loopback ({len(urls)} unique URLs), no page errors', flush=True)


if __name__ == '__main__':
    main()

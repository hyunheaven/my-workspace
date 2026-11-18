"""Browser regressions for template persistence, shared task views, and page links."""
import argparse
from datetime import date
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from playwright.sync_api import Page, expect, sync_playwright

from workspace_v012 import api_items, api_json, free_port, local_server, saved


PAGE_TITLE = '검증 회의 · 합성 예시'
PAGE_TEXT = '자동 저장 후 찾아볼 한국어 합성 문장'
TASK_TITLE = '표에서 만든 합성 업무'
TASK_NOTE = '업무 상세에서 남긴 합성 메모'
UNDATED_TASK_TITLE = '마감일 없는 완료 업무 · 합성 예시'


def page_record(page: Page, url: str) -> str:
    page.goto(url)
    page.locator('#nav-library').click()
    page.locator('#template-search').fill('Project Plan')
    with page.expect_response(lambda response: response.url.endswith('/pages/from-template')) as result:
        page.locator('.template-card[data-template-id="pm-plan"]').click()
    assert result.value.status == 201, result.value.text()
    record = result.value.json()
    page_id = record['id']
    assert record['blocks'], record
    expect(page.locator('#sidebar-page-tree .sidebar-page.selected')).to_contain_text('Project Plan')
    page.locator('#canvas-title').fill(PAGE_TITLE)
    page.locator('.block-paragraph textarea').first.fill(PAGE_TEXT)
    saved(page)
    expect(page).to_have_url(url + '/#page=' + page_id)
    assert any(block['content'] == PAGE_TEXT for block in api_json(url, f'/api/v1/pages/{page_id}/content')['blocks'])
    return page_id


def restore_after_restart(page: Page, url: str, page_id: str) -> None:
    link = url + '/#page=' + page_id
    expect(page).to_have_url(link)
    response = page.reload()
    assert response and response.ok
    expect(page.locator('#canvas-title')).to_have_value(PAGE_TITLE)
    expect(page.locator('.block-paragraph textarea').first).to_have_value(PAGE_TEXT)


def shared_task_views(page: Page, url: str) -> None:
    page.locator('#nav-database').click()
    view = page.locator('#task-view')
    view.select_option('table')
    month = page.evaluate('''() => new Intl.DateTimeFormat('sv-SE', {
      timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit'
    }).format(new Date())''')
    first_sunday = 1 + (6 - date.fromisoformat(month + '-01').weekday()) % 7
    day_one, day_two = [f'{month}-{first_sunday + offset:02}' for offset in (1, 3)]
    page.locator('#task-title').fill(TASK_TITLE)
    page.locator('#task-notes').fill(TASK_NOTE)
    page.locator('#task-due').fill(day_one)
    with page.expect_response(lambda response: response.url.endswith('/tasks') and response.request.method == 'POST') as result:
        page.locator('#task-form button[type=submit]').click()
    assert result.value.status == 201, result.value.text()
    task_id = result.value.json()['id']
    card = f'[data-task-id="{task_id}"]'
    expect(page.locator('#task-list').locator(card)).to_be_visible()

    view.select_option('board')
    page.locator('#task-group').select_option('status')
    lane = page.locator('.task-lane[aria-label="진행 중"]')
    page.locator('.board-card' + card).drag_to(lane)
    expect(lane.locator(card)).to_be_visible()

    view.select_option('calendar')
    source = page.locator(f'[data-task-date="{day_one}"]').locator(card)
    destination = page.locator(f'[data-task-date="{day_two}"]')
    destination.scroll_into_view_if_needed()
    source.drag_to(destination)
    expect(destination.locator(card)).to_be_visible()
    page.locator('#task-title').fill(UNDATED_TASK_TITLE)
    page.locator('#task-status').select_option('done')
    page.locator('#task-form button[type=submit]').click()
    undated = page.locator('[aria-label="마감일 없는 업무"]')
    expect(undated.locator('.task-complete')).to_have_text(UNDATED_TASK_TITLE)
    view.select_option('table')
    task_row = page.locator('tr').filter(has=page.locator(card))
    expect(task_row).to_contain_text('진행 중')
    expect(task_row).to_contain_text(day_two)

    page.locator('#sidebar-quick-search').click()
    page.locator('#doc-search').fill(TASK_NOTE)
    page.locator(f'[data-task-result-id="{task_id}"]').click()
    expect(page.locator('#task-form-heading')).to_have_text('업무 상세')
    expect(page.locator('#task-notes')).to_have_value(TASK_NOTE)
    task = api_json(url, f'/api/v1/tasks/{task_id}')
    assert (task['title'], task['status'], task['due_on']) == (TASK_TITLE, 'in_progress', day_two), task


def link_move_and_restore(page: Page, url: str, page_id: str) -> None:
    link = url + '/#page=' + page_id
    page.goto(link)
    expect(page.locator('#canvas-title')).to_have_value(PAGE_TITLE)
    with page.expect_response(lambda response: response.url.endswith('/pages') and response.request.method == 'POST') as result:
        page.locator('#topbar-new-page').click()
    assert result.value.status == 201, result.value.text()
    parent = result.value.json()['id']
    expect(page.locator('#canvas-title')).to_have_value('제목 없음')
    page.locator('#canvas-title').fill('상위 페이지 · 합성 예시')
    saved(page)

    page.goto(link)
    expect(page.locator('#canvas-title')).to_have_value(PAGE_TITLE)
    renamed = '이름을 바꾼 회의 · 합성 예시'
    page.locator('#canvas-title').fill(renamed)
    saved(page)
    page.locator('#canvas-organize').click()
    expect(page.locator('#page-move-source')).to_have_value(page_id)
    page.locator('#page-move-target').select_option(parent)
    with page.expect_response(lambda response: response.url.endswith(f'/pages/{page_id}/move')) as result:
        page.locator('#page-move-btn').click()
    assert result.value.ok, result.value.text()
    assert next(record for record in api_items(url, '/api/v1/pages/tree') if record['id'] == page_id)['parent_id'] == parent

    page.goto(link)
    expect(page.locator('#canvas-title')).to_have_value(renamed)
    expect(page.locator('#canvas-breadcrumb')).to_contain_text('상위 페이지 · 합성 예시')
    page.keyboard.press('Control+k')
    search = page.locator('#doc-search')
    expect(search).to_be_focused()
    search.fill(PAGE_TEXT)
    page.locator('#document-list .doc-row').get_by_text(renamed, exact=True).click()
    expect(page.locator('#canvas-editing')).to_be_visible()
    page.once('dialog', lambda dialog: dialog.accept())
    with page.expect_response(lambda response: response.url.endswith(f'/pages/{page_id}/trash')) as result:
        page.locator('#canvas-trash').click()
    assert result.value.ok, result.value.text()
    expect(page.locator('#document-list')).to_contain_text('일치하는 문서나 업무가 없습니다')
    expect(page.locator(f'#sidebar-page-tree [data-page-id="{page_id}"]')).to_have_count(0)

    page.locator('#page-trash-open').click()
    with page.expect_response(lambda response: response.url.endswith(f'/pages/{page_id}/restore')) as result:
        page.locator(f'[data-restore-page-id="{page_id}"]').click()
    assert result.value.ok, result.value.text()
    expect(page.locator('#page-trash-status')).to_contain_text('복원했습니다')
    page.locator('#page-trash-close').click()
    expect(page.locator('#document-list')).to_contain_text(renamed)
    page.goto(link)
    expect(page.locator('#canvas-title')).to_have_value(renamed)
    expect(page.locator('.block-paragraph textarea').first).to_have_value(PAGE_TEXT)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', type=Path, help='Path to an installed Chromium binary')
    args = parser.parse_args()
    with TemporaryDirectory() as temp, sync_playwright() as playwright:
        db = Path(temp) / 'workspace.db'
        port = free_port()
        browser = playwright.chromium.launch(executable_path=args.chromium)
        page = browser.new_page(locale='ko-KR', viewport={'width': 1440, 'height': 1050})
        requests, errors = [], []
        page.on('request', lambda request: requests.append(request.url))
        page.on('pageerror', lambda error: errors.append(str(error)))
        with local_server(db, port) as url:
            page_id = page_record(page, url)
        with local_server(db, port) as url:
            restore_after_restart(page, url, page_id)
            print('PASS template → Korean text → autosave → local server restart', flush=True)
            shared_task_views(page, url)
            print('PASS one task ID across table → board status drag → calendar date drag → table and search', flush=True)
            link_move_and_restore(page, url, page_id)
            print('PASS page rename/move → existing URL → Korean body search → trash/restore', flush=True)
        browser.close()
        with sqlite3.connect(db) as connection:
            assert connection.execute('PRAGMA integrity_check').fetchone() == ('ok',)
            assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
        assert requests and all(request.startswith(url + '/') for request in requests), requests
        assert not errors, errors


if __name__ == '__main__':
    main()

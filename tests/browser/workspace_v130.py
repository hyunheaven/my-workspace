"""Browser acceptance for database record and view history restoration."""
import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from playwright.sync_api import Page, expect, sync_playwright

from workspace_v012 import api_items, api_json, free_port, local_server
from workspace_v120 import add_markdown, create_database, create_property, create_view, record_dialog, save_database_dialog


DATABASE = '변경 이력 검증 · 합성 예시'
RECORD = '원본 레코드 · 합성 예시'
EDITED_RECORD = '수정 레코드 · 합성 예시'
ORIGINAL_NOTE = '복원하려는 합성 메모'
VIEW = '원본 갤러리 보기'
FILTERED_VIEW = '필터를 적용한 갤러리 보기'


def open_linked_page(page: Page, url: str, page_id: str) -> None:
    page.goto(f'{url}/#page={page_id}')
    expect(page.locator('#canvas-editing')).to_be_visible()


def setup(page: Page, url: str) -> tuple[str, str, dict, dict]:
    page.goto(url)
    document = add_markdown(page, text='# 데이터베이스 이력 시험\n\n변경 이력을 연결해 복원합니다.')
    expect(page.locator('#canvas-title')).to_have_value(document['title'])
    page.locator('#nav-custom-db').click()
    database = create_database(page, DATABASE)
    create_property(page, database, '공수', 'number')
    dialog = record_dialog(page)
    dialog.get_by_label('레코드 제목').fill(RECORD)
    dialog.get_by_label('메모').fill(ORIGINAL_NOTE)
    dialog.get_by_label('공수').fill('5')
    record = save_database_dialog(page, f'/databases/{database}/records')
    create_view(page, database, VIEW, 'gallery')
    view = next(view for view in api_json(url, f'/api/v1/databases/{database}')['views'] if view['name'] == VIEW)

    open_linked_page(page, url, document['id'])
    page.locator('#page-linked-configure').click()
    page.locator('#page-linked-database').select_option(database)
    page.locator('#page-linked-view').select_option(view['id'])
    page.locator('#page-linked-add').click()
    expect(page.locator('#page-linked-results').get_by_role('button', name=RECORD, exact=True)).to_be_visible()
    return document['id'], database, record, view


def restore_previous(page: Page, path: str, revision: int, preview_text: str) -> None:
    edit = page.locator('#custom-db-dialog')
    history = page.locator('#custom-db-history-dialog')
    edit.get_by_role('button', name='변경 이력', exact=True).click()
    expect(history).to_be_visible()
    history.locator(f'[data-cdb-history-revision="{revision}"]').click()
    expect(history).to_contain_text(preview_text)
    page.once('dialog', lambda dialog: dialog.accept())
    with page.expect_response(lambda response: response.url.endswith(f'{path}/history/{revision}/restore')) as result:
        history.locator('#custom-db-history-restore').click()
    assert result.value.ok, result.value.text()
    expect(history).to_be_hidden()
    expect(edit).to_be_hidden()


def record_history(page: Page, url: str, page_id: str, database: str, original: dict) -> None:
    record_id = original['id']
    base = f'/api/v1/databases/{database}'
    path = f'{base}/records/{record_id}'
    linked_record = page.locator(f'#page-linked-results [data-cdb-record="{record_id}"]')
    dialog = page.locator('#custom-db-dialog')
    linked_record.click()
    expect(dialog.get_by_label('레코드 제목')).to_have_value(RECORD)
    dialog.get_by_label('레코드 제목').fill(EDITED_RECORD)
    dialog.get_by_label('메모').fill('수정한 합성 메모')
    dialog.get_by_label('공수').fill('8')
    edited = save_database_dialog(page, path, 'PUT')
    assert edited['revision'] > original['revision']

    open_linked_page(page, url, page_id)
    expect(linked_record).to_have_text(EDITED_RECORD)
    linked_record.click()
    expect(dialog.get_by_label('공수')).to_have_value('8')
    restore_previous(page, path, original['revision'], ORIGINAL_NOTE)
    open_linked_page(page, url, page_id)
    expect(linked_record).to_have_text(RECORD)
    current = next(record for record in api_json(url, base)['records'] if record['id'] == record_id)
    assert current['revision'] > edited['revision'], current
    assert (current['title'], current['notes'], current['values']) == (RECORD, ORIGINAL_NOTE, original['values']), current
    assert {item['revision'] for item in api_items(url, path + '/history')} == {
        original['revision'], edited['revision'], current['revision'],
    }


def view_history(page: Page, url: str, page_id: str, database: str, original: dict) -> None:
    view_id = original['id']
    base = f'/api/v1/databases/{database}'
    path = f'{base}/views/{view_id}'
    initial_revision = api_items(url, path + '/history')[0]['revision']
    gallery = page.locator('[data-cdb-view="gallery"]')
    linked = page.locator('#page-linked-results')
    page.locator('#nav-custom-db').click()
    gallery.click()
    page.locator('#custom-db-view-settings').click()
    dialog = page.locator('#custom-db-dialog')
    dialog.get_by_label('보기 이름').fill(FILTERED_VIEW)
    dialog.get_by_label('필터 속성').select_option('title')
    dialog.get_by_label('필터 값').fill('일치하는 레코드 없음')
    save_database_dialog(page, path, 'PUT')
    expect(gallery).to_have_text(FILTERED_VIEW)
    open_linked_page(page, url, page_id)
    expect(linked).to_contain_text(FILTERED_VIEW)
    expect(linked.get_by_role('button', name=RECORD, exact=True)).to_have_count(0)

    page.locator('#nav-custom-db').click()
    gallery.click()
    page.locator('#custom-db-view-settings').click()
    restore_previous(page, path, initial_revision, VIEW)
    expect(gallery).to_have_text(VIEW)
    open_linked_page(page, url, page_id)
    expect(linked).to_contain_text(VIEW)
    expect(linked.get_by_role('button', name=RECORD, exact=True)).to_be_visible()
    restored = next(view for view in api_json(url, base)['views'] if view['id'] == view_id)
    assert (restored['name'], restored['kind'], restored['config']) == (VIEW, original['kind'], original['config']), restored
    snapshots = api_items(url, path + '/history')
    assert len(snapshots) == 3 and max(item['revision'] for item in snapshots) > initial_revision, snapshots


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
            page_id, database, record, view = setup(page, url)
            record_history(page, url, page_id, database, record)
            print('PASS record edit → previous title, notes and properties restored → linked page updated', flush=True)
            view_history(page, url, page_id, database, view)
            print('PASS saved-view filter and name restored → same linked view displays same record ID', flush=True)
        with local_server(db, port) as url:
            page.reload()
            expect(page.locator('#page-linked-results').get_by_role('button', name=RECORD, exact=True)).to_be_visible()
            for route in [f'records/{record["id"]}', f'views/{view["id"]}']:
                assert len(api_items(url, f'/api/v1/databases/{database}/{route}/history')) == 3
            print('PASS both histories and linked view persist after server restart', flush=True)
        browser.close()
        with closing(sqlite3.connect(db)) as connection:
            assert connection.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
            assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
        assert requests and all(request.startswith(url + '/') for request in requests), requests
        assert not errors, errors


if __name__ == '__main__':
    main()

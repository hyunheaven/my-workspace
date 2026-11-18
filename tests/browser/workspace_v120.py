"""Browser acceptance for local text transfers and custom databases."""
import argparse
from contextlib import closing
import csv
import io
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from playwright.sync_api import Locator, Page, expect, sync_playwright

from workspace_v012 import api_json, free_port, local_server, saved


MARKDOWN = '''# 합성 Markdown 문서

검토 계획의 합성 본문입니다.

- 첫 작업
  - 하위 작업
- [x] 확인 완료

> 화면에는 문자로 표시할 <예시>

```text
합성 코드 블록
```
'''
CATALOG = '합성 프로젝트 목록'
DATA = '합성 실험 기록'
RECORD = '합성 실험 A'


def add_markdown(page: Page, *, text: str | None = None, file: Path | None = None) -> dict:
    page.locator('#workspace-markdown-import').click()
    if file is not None:
        page.locator('#workspace-transfer-file').set_input_files(file)
        expect(page.locator('#workspace-transfer-status')).to_have_text(file.name)
    else:
        assert text is not None
        page.locator('#workspace-transfer-text').fill(text)
    with page.expect_response(lambda response: response.url.endswith('/pages/import')) as result:
        page.locator('#workspace-transfer-submit').click()
    assert result.value.status == 201, result.value.text()
    return result.value.json()


def block_values(record: dict) -> list[tuple]:
    return [(block['type'], block['content'], block['checked'], block.get('depth', 0)) for block in record['blocks']]


def markdown_roundtrip(page: Page, url: str, folder: Path) -> str:
    page.goto(url)
    original = add_markdown(page, text=MARKDOWN)
    title = original['title']
    expect(page.locator('#canvas-editing')).to_be_visible()
    expect(page.locator('#canvas-title')).to_have_value(title)
    assert title == '합성 Markdown 문서'
    blocks = block_values(original)
    assert ('todo', '확인 완료', True, 0) in blocks, blocks
    assert ('bullet', '하위 작업', False, 1) in blocks, blocks
    assert ('code', '합성 코드 블록', False, 0) in blocks, blocks

    with page.expect_download() as result:
        page.locator('#workspace-markdown-export').click()
    download = result.value
    assert download.suggested_filename.endswith('.md'), download.suggested_filename
    file = folder / 'roundtrip.md'
    download.save_as(file)
    assert '  - 하위 작업' in file.read_text(encoding='utf-8-sig')
    restored = add_markdown(page, file=file)
    assert restored['id'] != original['id']
    assert restored['title'] == title
    assert block_values(restored) == blocks, restored

    expect(page).to_have_url(url + '/#page=' + restored['id'])
    expect(page.locator('#canvas-editing')).to_be_visible()
    page.locator('#canvas-title').fill('이름을 수정한 합성 Markdown 문서')
    saved(page)
    page.locator('#canvas-history').click()
    history = page.locator('#canvas-history-dialog')
    history.locator(f'[data-revision="{restored["revision"]}"]').click()
    expect(history.locator('#canvas-history-preview')).to_contain_text(title)
    page.once('dialog', lambda dialog: dialog.accept())
    page.locator('#canvas-history-restore').click()
    expect(history).to_be_hidden()
    expect(page.locator('#canvas-title')).to_have_value(title)
    current = api_json(url, f'/api/v1/pages/{restored["id"]}/content')
    assert block_values(current) == blocks and current['revision'] > restored['revision'], current
    return restored['id']


def save_database_dialog(page: Page, endpoint: str, method: str = 'POST') -> dict:
    dialog = page.locator('#custom-db-dialog')
    with page.expect_response(lambda response: response.url.endswith(endpoint) and response.request.method == method) as result:
        dialog.get_by_role('button', name='저장', exact=True).click()
    assert result.value.ok, result.value.text()
    expect(dialog).to_be_hidden()
    return result.value.json()


def create_database(page: Page, name: str) -> str:
    page.locator('#custom-db-create').click()
    page.locator('#custom-db-dialog').get_by_label('데이터베이스 이름').fill(name)
    database = save_database_dialog(page, '/databases')
    expect(page.locator('[data-cdb-name]')).to_have_text(name)
    return database['id']


def property_dialog(page: Page, name: str, kind: str) -> Locator:
    page.locator('#custom-db-properties').click()
    page.locator('#custom-db-add-property').click()
    dialog = page.locator('#custom-db-dialog')
    dialog.get_by_label('속성 이름').fill(name)
    dialog.get_by_label('속성 유형').select_option(kind)
    return dialog


def create_property(page: Page, database: str, name: str, kind: str) -> None:
    property_dialog(page, name, kind)
    save_property(page, database, name)


def save_property(page: Page, database: str, name: str) -> None:
    save_database_dialog(page, f'/databases/{database}/properties')
    # The main table is repainted only after it has fetched the new schema.
    expect(page.locator('#custom-db-content').get_by_role('columnheader', name=name, exact=True)).to_be_visible()


def create_schema(page: Page) -> tuple[str, str]:
    page.locator('#nav-custom-db').click()
    catalog = create_database(page, CATALOG)
    create_property(page, catalog, '공수', 'number')
    data = create_database(page, DATA)
    create_property(page, data, '추가 공수', 'number')
    create_property(page, data, '실시 날짜', 'date')
    dialog = property_dialog(page, '관련 프로젝트', 'relation')
    dialog.get_by_label('연결할 데이터베이스').select_option(catalog)
    save_property(page, data, '관련 프로젝트')
    dialog = property_dialog(page, '프로젝트 합계', 'rollup')
    dialog.get_by_label('관계 속성').select_option(label='관련 프로젝트')
    dialog.get_by_label('집계 방식').select_option('sum')
    dialog.get_by_label('집계할 숫자 속성').select_option(label='공수')
    save_property(page, data, '프로젝트 합계')
    dialog = property_dialog(page, '총 공수', 'formula')
    dialog.get_by_label('계산 방식').select_option('add')
    dialog.get_by_label('왼쪽 숫자 속성').select_option(label='프로젝트 합계')
    dialog.get_by_label('오른쪽 숫자 속성').select_option(label='추가 공수')
    save_property(page, data, '총 공수')
    create_property(page, data, '완료', 'checkbox')
    return catalog, data


def choose_database(page: Page, database: str, name: str) -> None:
    page.locator('#custom-db-picker').select_option(database)
    expect(page.locator('[data-cdb-name]')).to_have_text(name)


def record_dialog(page: Page, record_id: str | None = None) -> Locator:
    if record_id is None:
        page.locator('#custom-db-add-record').click()
    else:
        page.locator('#custom-db-content').locator(f'[data-cdb-record="{record_id}"]').click()
    dialog = page.locator('#custom-db-dialog')
    expect(dialog.get_by_label('레코드 제목')).to_be_visible()
    return dialog


def create_view(page: Page, database: str, name: str, kind: str) -> None:
    page.locator('#custom-db-add-view').click()
    dialog = page.locator('#custom-db-dialog')
    dialog.get_by_label('보기 이름').fill(name)
    dialog.get_by_label('보기 유형').select_option(kind)
    if kind in ('timeline', 'calendar'):
        dialog.get_by_label('날짜 속성', exact=True).select_option(label='실시 날짜')
    if kind == 'board':
        dialog.get_by_label('그룹 속성', exact=True).select_option(label='완료')
    save_database_dialog(page, f'/databases/{database}/views')
    expect(page.locator(f'[data-cdb-view="{kind}"]')).to_be_visible()


def fill_records_and_views(page: Page, catalog: str, database: str) -> tuple[str, str]:
    choose_database(page, catalog, CATALOG)
    dialog = record_dialog(page)
    dialog.get_by_label('레코드 제목').fill('합성 과제 A')
    dialog.get_by_label('공수').fill('20')
    target = save_database_dialog(page, f'/databases/{catalog}/records')['id']

    choose_database(page, database, DATA)
    dialog = record_dialog(page)
    dialog.get_by_label('레코드 제목').fill(RECORD)
    dialog.get_by_label('메모').fill('합성 첫 줄\n합성 둘째 줄, 쉼표 확인')
    dialog.get_by_label('추가 공수').fill('3')
    dialog.get_by_label('관련 프로젝트').select_option(target)
    date_value = page.evaluate('''() => new Intl.DateTimeFormat('sv-SE', {
      timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit'
    }).format(new Date())''')
    dialog.get_by_label('실시 날짜').fill(date_value)
    record = save_database_dialog(page, f'/databases/{database}/records')['id']
    row = page.locator(f'[data-cdb-row="{record}"]')
    expect(row.get_by_role('cell', name='합성 과제 A', exact=True)).to_be_visible()
    expect(row.get_by_role('cell', name='20', exact=True)).to_be_visible()
    expect(row.get_by_role('cell', name='23', exact=True)).to_be_visible()

    for name, kind in [('합성 보드', 'board'), ('합성 달력', 'calendar'),
                       ('합성 카드', 'gallery'), ('합성 일정', 'timeline')]:
        create_view(page, database, name, kind)
        page.locator(f'[data-cdb-view="{kind}"]').click()
        expect(page.locator(f'[data-cdb-kind="{kind}"] [data-cdb-record="{record}"]')).to_be_visible()
    return target, record


def linked_view_roundtrip(page: Page, url: str, page_id: str, catalog: str, target: str, database: str, record: str) -> None:
    path = url + '/#page=' + page_id
    page.goto(path)
    expect(page.locator('#canvas-editing')).to_be_visible()
    page.locator('#page-linked-configure').click()
    page.locator('#page-linked-database').select_option(database)
    page.locator('#page-linked-view').select_option(label='합성 카드')
    with page.expect_response(lambda response: response.url.endswith('/linked-views') and response.request.method == 'POST') as result:
        page.locator('#page-linked-add').click()
    assert result.value.status == 201, result.value.text()
    linked = page.locator('#page-linked-results')
    expect(linked.get_by_role('button', name=RECORD, exact=True)).to_be_visible()
    expect(linked).to_contain_text('23')

    page.locator('#nav-custom-db').click()
    choose_database(page, catalog, CATALOG)
    record_dialog(page, target).get_by_label('공수').fill('25')
    save_database_dialog(page, f'/databases/{catalog}/records/{target}', 'PUT')
    page.goto(path)
    expect(linked).to_contain_text('28')
    linked.get_by_role('button', name=RECORD, exact=True).click()
    dialog = page.locator('#custom-db-dialog')
    expect(dialog.get_by_label('레코드 제목')).to_have_value(RECORD)
    expect(dialog.get_by_label('총 공수')).to_have_text('28')
    dialog.get_by_role('button', name='닫기', exact=True).click()
    assert any(item['id'] == record for item in api_json(url, f'/api/v1/databases/{database}')['records'])


def csv_roundtrip(page: Page, url: str, folder: Path, database: str) -> None:
    with page.expect_download() as result:
        page.locator('#workspace-csv-export').click()
    download = result.value
    assert download.suggested_filename.endswith('.csv'), download.suggested_filename
    file = folder / 'roundtrip.csv'
    download.save_as(file)
    text = file.read_text(encoding='utf-8-sig')
    rows = list(csv.DictReader(io.StringIO(text)))
    assert len(rows) == 1 and rows[0]['제목'] == RECORD, rows
    assert rows[0]['메모'].splitlines() == ['합성 첫 줄', '합성 둘째 줄, 쉼표 확인'], rows
    assert set(rows[0]) == {'제목', '메모', '추가 공수', '실시 날짜', '완료'}, rows

    page.locator('#workspace-csv-import').click()
    page.locator('#workspace-transfer-file').set_input_files(file)
    expect(page.locator('#workspace-transfer-status')).to_have_text(file.name)
    with page.expect_response(lambda response: response.url.endswith(f'/databases/{database}/records/batch')) as result:
        page.locator('#workspace-transfer-submit').click()
    assert result.value.ok, result.value.text()
    copied = result.value.json()['items']
    assert len(copied) == 1 and copied[0]['title'] == RECORD, copied
    assert copied[0]['notes'].splitlines() == rows[0]['메모'].splitlines(), copied
    records = api_json(url, f'/api/v1/databases/{database}')['records']
    assert len(records) == 2 and records[0]['id'] != records[1]['id'], records


def search_and_reopen(page: Page, url: str, page_id: str, database: str, record: str) -> None:
    page.goto(url + '/#page=' + page_id)
    linked = page.locator('#page-linked-results')
    expect(linked).to_contain_text('28')
    page.keyboard.press('Control+k')
    page.locator('#doc-search').fill(RECORD)
    page.locator(f'[data-database-result-id="{record}"]').click()
    dialog = page.locator('#custom-db-dialog')
    expect(dialog.get_by_label('레코드 제목')).to_have_value(RECORD)
    dialog.get_by_role('button', name='닫기', exact=True).click()
    page.goto(url + '/#page=' + page_id)
    linked.get_by_role('button', name='합성 카드 연결 해제').click()
    expect(linked.get_by_role('button', name=RECORD, exact=True)).to_have_count(0)
    assert len(api_json(url, f'/api/v1/databases/{database}')['records']) == 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', type=Path, help='Path to an installed Chromium binary')
    args = parser.parse_args()
    with TemporaryDirectory() as temp, sync_playwright() as playwright:
        folder = Path(temp)
        db = folder / 'workspace.db'
        port = free_port()
        browser = playwright.chromium.launch(executable_path=args.chromium)
        page = browser.new_page(locale='ko-KR', viewport={'width': 1440, 'height': 1050})
        requests, errors = [], []
        page.on('request', lambda request: requests.append(request.url))
        page.on('pageerror', lambda error: errors.append(str(error)))
        with local_server(db, port) as url:
            page_id = markdown_roundtrip(page, url, folder)
            print('PASS Markdown import → download → file re-import → nested blocks and history restore', flush=True)
            catalog, database = create_schema(page)
            target, record = fill_records_and_views(page, catalog, database)
            linked_view_roundtrip(page, url, page_id, catalog, target, database, record)
            print('PASS custom fields, relations, formula/rollup, gallery/timeline and live linked view', flush=True)
            csv_roundtrip(page, url, folder, database)
            print('PASS CSV download and file import with Korean, commas, newlines, and unique IDs', flush=True)
        with local_server(db, port) as url:
            search_and_reopen(page, url, page_id, database, record)
            print('PASS server restart, record search, and unlink without deleting records', flush=True)
        browser.close()
        with closing(sqlite3.connect(db)) as connection:
            assert connection.execute('PRAGMA integrity_check').fetchone() == ('ok',)
            assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
        assert requests and all(request.startswith(url + '/') for request in requests), requests
        assert not errors, errors


if __name__ == '__main__':
    main()

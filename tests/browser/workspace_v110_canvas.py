"""Verify editor draft recovery, IME composition and block commands in Chromium."""
import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

from workspace_v012 import api_items, api_json, free_port, local_server, saved


def create_page(page, url, title):
    page.locator('#topbar-new-page').click()
    expect(page.locator('#canvas-title')).to_have_value('제목 없음')
    page.locator('#canvas-title').fill(title)
    saved(page)
    return next(row['id'] for row in api_items(url, '/api/v1/pages/tree') if row['title']==title)


def check_draft_recovery(page, url, source):
    path=f'/api/v1/pages/{source}/content'
    title='다시 저장할 합성 회의 메모'

    def reject_save(route):
        if route.request.method=='PUT':
            route.fulfill(status=503, json={'detail':'Synthetic unavailable'})
        else:
            route.continue_()

    page.route('**'+path, reject_save)
    page.locator('#canvas-title').fill(title)
    expect(page.locator('#canvas-save')).to_have_text('저장 다시 시도', timeout=8_000)
    assert api_json(url, path)['title']!=title
    page.reload()
    expect(page.locator('#canvas-title')).to_have_value(title)
    expect(page.locator('#canvas-dirty-flag')).to_contain_text('초안을 복구했습니다')
    assert api_json(url, path)['title']!=title
    page.unroute('**'+path, reject_save)
    page.locator('#canvas-save').click()
    saved(page)
    assert api_json(url, path)['title']==title
    page.reload()
    expect(page.locator('#canvas-title')).to_have_value(title)
    saved(page)


def check_conflicting_save(page, url, source):
    path=f'/api/v1/pages/{source}/content'
    other=page.context.new_page()
    other.goto(f'{url}/#page={source}')
    saved(other)
    other.locator('#canvas-title').fill('다른 탭의 합성 저장본')
    saved(other)
    other.close()
    page.locator('#canvas-title').fill('현재 탭의 별도 초안')
    expect(page.locator('#canvas-save')).to_have_text('저장 다시 시도', timeout=8_000)
    assert api_json(url, path)['title']=='다른 탭의 합성 저장본'
    page.reload()
    expect(page.locator('#canvas-title')).to_have_value('현재 탭의 별도 초안')
    expect(page.locator('#canvas-dirty-flag')).to_contain_text('다른 창의 저장본')
    page.once('dialog', lambda dialog: dialog.dismiss())
    page.locator('#canvas-save').click()
    expect(page.locator('#canvas-save')).to_have_text('저장 다시 시도')
    assert api_json(url, path)['title']=='다른 탭의 합성 저장본'
    page.once('dialog', lambda dialog: dialog.accept())
    page.locator('#canvas-save').click()
    saved(page)
    assert api_json(url, path)['title']=='현재 탭의 별도 초안'


def check_blocks(page, url, source, target):
    def add(kind):
        page.locator('#canvas-new-type').select_option(kind)
        page.locator('#canvas-add-block').click()

    add('ordered_list')
    first=page.locator('.block-ordered_list textarea').first
    first.fill('첫 작업')
    first.press('End')
    first.press('Enter')
    second=page.locator('.block-ordered_list textarea').nth(1)
    second.fill('다음 작업')
    second.press('Alt+ArrowUp')
    expect(first).to_have_value('다음 작업')
    first.press('Control+z')
    expect(first).to_have_value('첫 작업')
    page.locator('#canvas-redo').click()
    expect(first).to_have_value('다음 작업')
    add('paragraph')
    composing=page.locator('.block-paragraph textarea')
    composing.focus()
    saved(page)
    session=page.context.new_cdp_session(page)
    session.send('Input.imeSetComposition', {'text':'한ㄱ','selectionStart':2,'selectionEnd':2})
    expect(composing).to_have_value('한ㄱ')
    assert api_json(url, f'/api/v1/pages/{source}/content')['blocks'][-1]['content']==''
    session.send('Input.insertText', {'text':'한글 조합'})
    expect(composing).to_have_value('한글 조합')
    expect(composing).to_be_focused()
    assert composing.evaluate('(input) => input.selectionStart')==len('한글 조합')
    add('page_link')
    page.locator('.canvas-page-link-target').select_option(target)
    saved(page)
    page.locator('.canvas-page-link').click()
    expect(page.locator('#canvas-title')).to_have_value('합성 연결 대상')


def check_long_document(page, url, target):
    path=f'/api/v1/pages/{target}/content'
    document=api_json(url, path)
    text='합성 한글 문서 ' * 400
    blocks=[{'id':str(uuid4()),'type':'paragraph','content':text,'checked':False} for _ in range(12)]
    response=page.request.put(url+path, headers={'X-EAW-Request':'local-template-editor'},
        data={'title':document['title'],'expected_revision':document['revision'],'blocks':blocks})
    assert response.ok,response.text()
    page.reload()
    expect(page.locator('.canvas-block-text')).to_have_count(12)
    last=page.locator('.canvas-block-text').last
    last.evaluate('(input) => { input.focus(); input.setSelectionRange(0, 0); }')
    page.keyboard.insert_text('추가 ')  # Paste-like plain-text insertion through the normal editor.
    expect(last).to_be_focused()
    assert last.evaluate('(input) => input.selectionStart')==len('추가 ')
    saved(page)
    assert api_json(url, path)['blocks'][-1]['content']=='추가 '+text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp, sync_playwright() as playwright:
        db=Path(tmp)/'workspace.db'
        backup=Path(tmp)/'copy'/'workspace.db'
        backup.parent.mkdir()
        port=free_port()
        browser=playwright.chromium.launch(executable_path=args.chromium)
        context=browser.new_context(locale='ko-KR')
        page=context.new_page()
        errors=[]
        page.on('pageerror', lambda error: errors.append(str(error)))
        with local_server(db, port) as url:
            page.goto(url)
            target=create_page(page, url, '합성 연결 대상')
            source=create_page(page, url, '합성 편집기 문서')
            check_draft_recovery(page, url, source)
            check_conflicting_save(page, url, source)
            check_blocks(page, url, source, target)
            check_long_document(page, url, target)
            page.route(f'**/api/v1/pages/{target}/content',
                lambda route: route.abort() if route.request.method=='PUT' else route.continue_())
            page.locator('#canvas-title').fill('원본 작업 공간 탭의 미저장 초안')
            with closing(sqlite3.connect(db)) as source_db, closing(sqlite3.connect(backup)) as destination_db:
                source_db.backup(destination_db)
        with local_server(backup, port):
            page.reload()
            expect(page.locator('#canvas-title')).to_have_value('합성 연결 대상')
            saved(page)
        with local_server(db, port):
            page.reload()
            expect(page.locator('#canvas-title')).to_have_value('원본 작업 공간 탭의 미저장 초안')
            expect(page.locator('#canvas-dirty-flag')).to_contain_text('초안을 복구했습니다')
        browser.close()
        assert not errors, errors
    print('PASS editor recovery, conflicts, undo/redo, IME, links, long Korean document, and backup isolation')


if __name__=='__main__':
    main()

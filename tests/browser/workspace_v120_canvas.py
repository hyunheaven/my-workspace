"""Exercise nested block editing and structured clipboard in Chromium."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

from workspace_v012 import api_json, free_port, local_server, saved
from workspace_v110_canvas import create_page


def test_nested_editor(page, url):
    page.goto(url)
    ident=create_page(page,url,'합성 하위 블록 편집')
    path=f'/api/v1/pages/{ident}/content'
    original=api_json(url,path)
    blocks=[]
    for kind,content,depth in [('toggle','묶음',0),('paragraph','메모',1),('todo','확인',2),
                              ('paragraph','점검',1),('paragraph','별도 메모',0)]:
        block={'id':str(uuid4()),'type':kind,'content':content,'checked':kind=='todo'}
        if depth:block['depth']=depth
        blocks.append(block)
    response=page.request.put(url+path, headers={'X-EAW-Request':'local-template-editor'},
        data={'title':original['title'],'expected_revision':original['revision'],'blocks':blocks})
    assert response.ok,response.text()
    page.reload()
    rows=page.locator('#canvas-blocks .canvas-block')
    expect(rows).to_have_count(5)
    toggle=rows.first.locator('.toggle-caret')
    toggle.click()
    expect(rows.nth(1)).to_be_hidden()
    expect(rows.nth(3)).to_be_hidden()
    expect(rows.last).to_be_visible()
    toggle.click()
    expect(rows.nth(2)).to_be_visible()
    rows.first.locator('textarea').press('Alt+ArrowDown')
    expect(rows.first.locator('textarea')).to_have_value('별도 메모')
    expect(rows.last).to_have_attribute('data-block-depth','1')
    page.locator('#canvas-undo').click()
    expect(rows.first.locator('textarea')).to_have_value('묶음')
    rows.nth(3).locator('textarea').press('Alt+ArrowLeft')
    expect(rows.nth(3)).to_have_attribute('data-block-depth','0')
    rows.nth(3).locator('textarea').press('Alt+ArrowRight')
    expect(rows.nth(3)).to_have_attribute('data-block-depth','1')

    rows.first.locator('.block-tool-select').click()
    page.keyboard.press('Shift+ArrowDown')
    expect(page.locator('.canvas-block-selected')).to_have_count(4)
    page.keyboard.press('Control+c')
    rows.last.locator('textarea').focus()
    page.keyboard.press('Control+v')
    expect(rows).to_have_count(9)
    expect(rows.nth(7).locator('input[type=checkbox]')).to_be_checked()
    assert rows.evaluate_all('(rows) => rows.slice(5).map(row => Number(row.dataset.blockDepth))')==[0,1,2,1]
    saved(page)
    record=api_json(url,path)['blocks']
    assert len({block['id'] for block in record})==9
    page.keyboard.press('Delete')
    expect(rows).to_have_count(5)
    page.locator('#canvas-undo').click()
    expect(rows).to_have_count(9)
    saved(page)
    page.reload()
    expect(rows).to_have_count(9)
    assert api_json(url,path)['blocks']==record
    rows.first.locator('.block-tool-select').drag_to(rows.nth(4),target_position={'x':65,'y':30})
    expect(rows.first.locator('textarea')).to_have_value('별도 메모')
    saved(page)
    assert [block['id'] for block in api_json(url,path)['blocks'][:5]]==[blocks[4]['id'],*(block['id'] for block in blocks[:4])]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium',type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp, sync_playwright() as playwright:
        with local_server(Path(tmp)/'workspace.db',free_port()) as url:
            browser=playwright.chromium.launch(executable_path=args.chromium)
            context=browser.new_context(locale='ko-KR',permissions=['clipboard-read','clipboard-write'])
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            test_nested_editor(page,url)
            browser.close()
            assert not errors,errors
    print('PASS nested blocks, collapse, subtree moves, native clipboard, deletion, undo and persisted IDs')


if __name__=='__main__':
    main()

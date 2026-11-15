"""Chromium validation for per-page look, colored tabs and tags."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode

from playwright.sync_api import expect, sync_playwright

from workspace_v012 import api_items, free_port, local_server, saved, screenshot


def edit_appearance(page, options):
    page.locator('#workspace-theme-button').click()
    for field, value in options.items():
        select = page.locator('#workspace-' + field)
        if field.startswith('page-'):
            with page.expect_response(lambda response: response.request.method == 'PATCH'
                                      and response.url.endswith('/properties')) as result:
                select.select_option(value)
            assert result.value.ok, result.value.text()
        else:
            select.select_option(value)
    page.locator('#workspace-theme-close').click()


def add_tag(page, tag):
    page.locator('#page-tag-input').fill(tag)
    page.locator('#page-tag-editor [type=submit]').click()
    expect(page.locator('#page-tags')).to_contain_text('#' + tag)


def add_page(page, title):
    page.locator('#topbar-new-page').click()
    expect(page.locator('#canvas-title')).to_have_value('제목 없음')
    page.locator('#canvas-title').fill(title)
    saved(page)


def tab_for(page, title):
    return page.locator('#workspace-page-tabs .workspace-tab-link').get_by_text(title, exact=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', type=Path)
    parser.add_argument('--screenshots', type=Path)
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
            page.goto(url)
            expect(page.locator('#canvas-empty')).to_be_visible()
            add_page(page, '실험 노트 · 합성 예시')
            edit_appearance(page, {
                'color-theme':'contrast', 'page-theme':'contrast', 'page-background':'ruled',
                'page-tab-color':'gold', 'menu-tab':'documents', 'menu-tab-color':'rose',
            })
            expect(page.locator('html')).to_have_attribute('data-workspace-theme', 'contrast')
            expect(page.locator('#canvas-title')).to_have_css('color', 'rgb(255, 255, 255)')
            expect(page.locator('#canvas-save')).to_have_css('background-color', 'rgb(255, 223, 82)')
            add_tag(page, '소자 분석')
            add_tag(page, '실험 기록')
            expect(page.locator('#canvas-panel')).to_have_attribute('data-page-background', 'ruled')
            expect(page.locator('#canvas-panel')).to_have_attribute('data-page-theme', 'contrast')
            expect(page.locator('#nav-documents')).to_have_attribute('data-tab-color', 'rose')
            add_page(page, '검토 페이지 · 합성 예시')
            edit_appearance(page, {'page-theme':'lavender','page-background':'graph','page-tab-color':'indigo'})
            add_tag(page, '설계 검토')
            expect(page.locator('#canvas-panel')).to_have_attribute('data-page-background', 'graph')
            expect(tab_for(page, '검토 페이지 · 합성 예시').locator('..')).to_have_attribute('data-tab-color','indigo')
            tab_for(page, '실험 노트 · 합성 예시').click()
            expect(page.locator('#canvas-panel')).to_have_attribute('data-page-background', 'ruled')
            expect(tab_for(page, '실험 노트 · 합성 예시').locator('..')).to_have_attribute('data-tab-color','gold')
            page.locator('#canvas-add-block').click()
            page.locator('.canvas-block-text').last.fill('합성 실험 노트 · 진행 상황과 다음 확인 항목')
            saved(page)
            screenshot(page, args.screenshots, '01-ruled-page-and-tabs.png')
            page.locator('#workspace-theme-button').click()
            screenshot(page, args.screenshots, '02-page-appearance-settings.png')
            page.locator('#workspace-theme-close').click()
            page.locator('#page-tags').get_by_role('button',name='#실험 기록').click()
            expect(page.locator('#doc-tag-filter')).to_have_value('실험 기록')
            expect(page.locator('#document-list .doc-row')).to_have_count(1)
            expect(page.locator('#document-list')).to_contain_text('실험 노트 · 합성 예시')
            screenshot(page, args.screenshots, '03-tag-filter.png')
            page.locator('#doc-search').fill('일치하지 않는 본문 검색')
            expect(page.locator('#document-list')).to_contain_text('일치하는 문서가 없습니다')
            page.locator('#workspace-page-tabs').get_by_role('button',name='검토 페이지 · 합성 예시 탭 닫기').click()
            expect(tab_for(page, '검토 페이지 · 합성 예시')).to_have_count(0)
            assert len(api_items(url, '/api/v1/pages/tree')) == 2
        with local_server(db, port) as url:
            clean = browser.new_page(locale='ko-KR')
            clean.goto(url)
            expect(clean.locator('#canvas-title')).to_have_value('실험 노트 · 합성 예시')
            expect(clean.locator('#canvas-panel')).to_have_attribute('data-page-theme','contrast')
            expect(clean.locator('#canvas-panel')).to_have_attribute('data-page-background','ruled')
            expect(clean.locator('#page-tags')).to_contain_text('#실험 기록')
            expect(tab_for(clean, '실험 노트 · 합성 예시').locator('..')).to_have_attribute('data-tab-color','gold')
            clean.get_by_role('button',name='실험 기록 태그 삭제').click()
            expect(clean.locator('#page-tags')).not_to_contain_text('#실험 기록')
            assert api_items(url, '/api/v1/search/pages?' + urlencode({'tag': '실험 기록'})) == []
            browser.close()
        assert not errors, errors
        assert requests and all(request.startswith(url + '/') for request in requests), requests
        print('PASS independent page looks, tabs, menu color, tags, search and fresh browser after restart')


if __name__ == '__main__':
    main()

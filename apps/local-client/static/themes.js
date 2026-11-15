'use strict';

(() => {
  const header = document.querySelector('.topbar-right');
  const canvas = document.querySelector('#canvas-panel');
  if (!header || !canvas) return;

  const colors = [
    ['warm', '웜 뉴트럴'],
    ['sage', '세이지 그린'],
    ['indigo', '인디고'],
    ['clay', '테라코타'],
    ['dark', '다크'],
    ['ocean', '오션 블루'],
    ['lavender', '라벤더'],
    ['rose', '더스티 로즈'],
    ['slate', '슬레이트'],
    ['contrast', '고대비'],
  ];
  const backgrounds = [
    ['plain', '기본'],
    ['paper', '아이보리 종이'],
    ['mint', '민트'],
    ['mist', '블루 미스트'],
    ['grid', '도트 그리드'],
    ['ruled', '줄눈 노트'],
    ['graph', '모눈 종이'],
    ['margin', '여백 줄노트'],
    ['cream', '크림색 메모'],
    ['rosepaper', '로즈 페이퍼'],
  ];
  const tabColors = [
    ['none', '기본'], ['sage', '세이지'], ['ocean', '오션'], ['indigo', '인디고'],
    ['lavender', '라벤더'], ['rose', '로즈'], ['clay', '테라코타'], ['gold', '골드'], ['slate', '슬레이트'],
  ];
  const pageColors = [['inherit', '워크스페이스 색상 따르기'], ...colors];
  const menus = [
    ['home','홈'], ['start','시작하기'], ['canvas','페이지 편집'], ['documents','모든 문서'],
    ['library','템플릿 라이브러리'], ['database','업무 데이터베이스'], ['projects','프로젝트'],
    ['calendar','캘린더'], ['pages','페이지 구조 관리'],
  ];
  const prefix = 'my-ai-workspace.theme.';
  const session = new Map();
  let pageId = null;
  let properties = null;

  function read(key, palette, fallback = palette[0][0]) {
    let value = session.get(key);
    try {
      value ??= localStorage.getItem(prefix + key);
    } catch {
      // Private browsing or managed browser settings may disable storage.
    }
    return palette.some(([id]) => id === value) ? value : fallback;
  }

  function write(key, value) {
    try {
      localStorage.setItem(prefix + key, value);
      session.delete(key);
      status.textContent = '이 브라우저에 테마를 저장했습니다.';
    } catch {
      session.set(key, value);
      status.textContent = '브라우저 저장이 제한되어 현재 탭에만 적용했습니다.';
    }
  }

  function element(tag, text) {
    const result = document.createElement(tag);
    if (text !== undefined) result.textContent = text;
    return result;
  }

  function selectRow(id, title, palette) {
    const row = element('label');
    row.className = 'workspace-theme-option';
    const swatch = element('span');
    swatch.className = 'workspace-theme-swatch';
    swatch.setAttribute('aria-hidden', 'true');
    const select = element('select');
    select.id = id;
    for (const [value, label] of palette) {
      const option = element('option', label);
      option.value = value;
      select.append(option);
    }
    const label = element('span', title);
    row.append(swatch, label, select);
    return {row, select, swatch};
  }

  function reflect(row, value) {
    row.select.value = value;
    row.swatch.dataset.option = value;
  }

  function sync() {
    const color = read('color', colors);
    const defaultBackground = read('default-background', backgrounds);
    const pageBackground = properties?.background || (pageId ? read('page.' + pageId, backgrounds) : 'plain');
    const pageTheme = properties?.theme || 'inherit';
    const tabColor = properties?.tab_color || 'none';
    document.documentElement.dataset.workspaceTheme = color;
    canvas.dataset.pageBackground = pageBackground;
    canvas.dataset.pageTheme = pageTheme;
    reflect(colorRow, color);
    reflect(defaultRow, defaultBackground);
    reflect(pageRow, pageBackground);
    reflect(pageColorRow, pageTheme);
    reflect(pageTabRow, tabColor);
    for (const [id] of menus) el('nav-' + id).dataset.tabColor = read('nav.' + id, tabColors);
    reflect(menuColorRow, read('nav.' + menuRow.select.value, tabColors));
  }

  function settingsLabel() {
    const editorVisible = !document.querySelector('#canvas-editing')?.classList.contains('hidden');
    pageSettings.hidden = !pageId || canvas.classList.contains('hidden') || !editorVisible;
  }

  const button = element('button', '테마');
  button.type = 'button';
  button.id = 'workspace-theme-button';
  button.className = 'topbar-icon workspace-theme-button';
  button.setAttribute('aria-haspopup', 'dialog');
  button.setAttribute('aria-controls', 'workspace-theme-dialog');

  const dialog = element('dialog');
  dialog.id = 'workspace-theme-dialog';
  dialog.setAttribute('aria-labelledby', 'workspace-theme-title');
  const heading = element('h2', '테마 설정');
  heading.id = 'workspace-theme-title';
  const close = element('button', '닫기');
  close.id = 'workspace-theme-close';
  close.className = 'secondary-button';
  close.type = 'button';
  const top = element('div');
  top.className = 'workspace-theme-top';
  top.append(heading, close);
  const hint = element('p', '현재 페이지 설정은 문서에 저장됩니다. 워크스페이스와 메뉴 색상은 이 브라우저에 저장됩니다.');
  hint.className = 'workspace-theme-hint';

  const colorRow = selectRow('workspace-color-theme', '워크스페이스 색상', colors);
  const defaultRow = selectRow('workspace-default-background', '새 페이지 기본 배경', backgrounds);
  const pageRow = selectRow('workspace-page-background', '현재 페이지 배경', backgrounds);
  const pageColorRow = selectRow('workspace-page-theme', '현재 페이지 색상', pageColors);
  const pageTabRow = selectRow('workspace-page-tab-color', '현재 페이지 탭 색상', tabColors);
  const menuRow = selectRow('workspace-menu-tab', '메뉴 선택', menus);
  const menuColorRow = selectRow('workspace-menu-tab-color', '선택한 메뉴 색상', tabColors);
  const pageSettings = element('fieldset');
  pageSettings.append(element('legend','현재 페이지'), pageColorRow.row, pageRow.row, pageTabRow.row);
  const menuSettings = element('fieldset');
  menuSettings.append(element('legend','사이드바 메뉴'), menuRow.row, menuColorRow.row);
  const status = element('p');
  status.className = 'workspace-theme-status';
  status.setAttribute('role', 'status');
  dialog.append(top, hint, colorRow.row, defaultRow.row, pageSettings, menuSettings, status);
  header.insertBefore(button, header.querySelector('#topbar-new-page'));
  document.body.append(dialog);

  button.addEventListener('click', () => {
    settingsLabel();
    sync();
    status.textContent = '';
    dialog.showModal();
    colorRow.select.focus();
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => button.focus());

  function applySelection(select, key) {
    select.addEventListener('change', () => {
      const setting = key();
      if (setting) write(setting, select.value);
      sync();
    });
  }

  applySelection(colorRow.select, () => 'color');
  applySelection(defaultRow.select, () => 'default-background');
  applySelection(menuColorRow.select, () => 'nav.' + menuRow.select.value);
  menuRow.select.addEventListener('change', sync);

  for (const [row, field] of [[pageRow, 'background'], [pageColorRow, 'theme'], [pageTabRow, 'tab_color']]) {
    row.select.addEventListener('change', async () => {
      const id = pageId;
      const selection = row.select.value;
      row.select.disabled = true;
      status.textContent = '페이지 설정 저장 중…';
      try {
        await changeCanvasProperties({[field]:selection});
        if (id === pageId) status.textContent = '페이지 설정을 저장했습니다.';
      } catch (error) {
        if (id === pageId) status.textContent = error.message;
      } finally {
        row.select.disabled = false;
        sync();
      }
    });
  }

  document.addEventListener('workspace-page-opened', event => {
    const {id, created, properties:openedProperties} = event.detail ?? {};
    if (typeof id !== 'string' || !id) return;
    pageId = id;
    properties = openedProperties;
    const key = 'page.' + id;
    if (created && !properties?.background && !read(key, backgrounds, null)) {
      const background = read('default-background', backgrounds);
      write(key, background);
      if (background !== 'plain') changeCanvasProperties({background}).catch(error=>toast(error.message));
    }
    sync();
  });

  document.addEventListener('workspace-page-properties', event => {
    if (event.detail.id !== pageId) return;
    properties = event.detail.properties;
    sync();
  });

  window.addEventListener('storage', event => {
    if (!event.key || event.key.startsWith(prefix)) sync();
  });
  sync();
})();

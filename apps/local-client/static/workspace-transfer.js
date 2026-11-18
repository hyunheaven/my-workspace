'use strict';

const workspaceTransferLimit = 256 * 1024;
const markdownTicks = String.fromCharCode(96);
const markdownUuid = '[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}';
const transferDialog = el('workspace-transfer-dialog');
let transferTarget = null;

function markdownCharacters(value) {
  return value.replace(/([\\*_\x60~[\]<>#|+.!>\-])/g, '\\$1');
}

function markdownReadCharacters(value) {
  return value.replace(/\\([\\*_\x60~[\]<>#|+.!>\-])/g, '$1');
}

function markdownTableCells(line) {
  const text = line.trim();
  if (!text.startsWith('|') || !text.endsWith('|')) return null;
  const result = [];
  let cell = '';
  let escaped = false;
  for (const char of text.slice(1,-1)) {
    if (escaped) {
      cell += '\\' + char;
      escaped = false;
    } else if (char === '\\') escaped = true;
    else if (char === '|') {
      result.push(cell.trim());
      cell = '';
    } else cell += char;
  }
  if (escaped) cell += '\\';
  result.push(cell.trim());
  return result;
}

function markdownTableCellText(cell) {
  return markdownReadCharacters(cell).replace(/<br>/gi, '\n').replace(/&lt;/g, '<').replace(/&amp;/g, '&');
}

function markdownBlockType(text) {
  const localLink = new RegExp('^\\[[^\\]]+\\]\\(#page=(' + markdownUuid + ')\\)$').exec(text);
  if (localLink) return ['page_link', localLink[1]];
  const task = /^\s*(?:[-+*]|\d+[.)])\s+\[([ xX])\](?:\s+(.*))?$/.exec(text);
  if (task) return ['todo', markdownReadCharacters(task[2] || ''), task[1] !== ' '];
  const toggle = /^>\s*\[!TOGGLE\](?:\s+(.*))?$/.exec(text);
  if (toggle) return ['toggle', markdownReadCharacters(toggle[1] || '')];
  const heading = /^(#{1,6})\s+(.*)$/.exec(text);
  if (heading) return [heading[1].length === 1 ? 'heading_1' : 'heading_2', markdownReadCharacters(heading[2])];
  if (/^(?:-{3,}|\*{3,}|_{3,})$/.test(text.trim())) return ['divider', ''];
  const ordered = /^\d+[.)]\s+(.*)$/.exec(text);
  if (ordered) return ['ordered_list', markdownReadCharacters(ordered[1])];
  const bullet = /^[-*+]\s+(.*)$/.exec(text);
  if (bullet) return ['bullet', markdownReadCharacters(bullet[1])];
  const quote = /^>\s?(.*)$/.exec(text);
  if (quote) return ['quote', markdownReadCharacters(quote[1])];
  return ['paragraph', markdownReadCharacters(text)];
}

function parseWorkspaceMarkdown(source, filename) {
  const lines = source.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n').split('\n');
  while (lines.length && !lines[0].trim()) lines.shift();
  const first = /^# (.+)$/.exec(lines[0] || '');
  const title = first ? markdownReadCharacters(first[1]).trim() :
    (filename || '가져온 페이지').replace(/\.(md|markdown|txt)$/i, '').trim();
  if (first) lines.shift();
  if (!title || [...title].length > 120) throw Error('페이지 제목은 1~120자여야 합니다.');
  const blocks = [];
  const add = (type, content, checked, indent) => {
    const maxDepth = blocks.length ? (blocks.at(-1).depth ?? 0) + 1 : 0;
    const depth = Math.min(Math.floor(indent / 2), maxDepth, 6);
    if ([...content].length > 4000) throw Error('가져올 블록이 4,000자를 초과합니다.');
    const block = {id: crypto.randomUUID(), type, content, checked: !!checked};
    if (depth) block.depth = depth;
    blocks.push(block);
  };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line.trim()) continue;
    const indent = line.match(/^ */)[0].length;
    const text = line.slice(indent);
    const fence = /^([\x60]{3,}|~{3,})/.exec(text);
    if (fence) {
      const content = [];
      const matching = new RegExp('^' + fence[1][0] + '{' + fence[1].length + ',}\\s*$');
      while (++i < lines.length && !matching.test(lines[i].trim())) {
        content.push(lines[i].startsWith(' '.repeat(indent)) ? lines[i].slice(indent) : lines[i]);
      }
      if (i === lines.length) throw Error('Markdown 코드 블록이 닫히지 않았습니다.');
      add('code', content.join('\n'), false, indent);
      continue;
    }
    const header = markdownTableCells(text);
    const separator = markdownTableCells(lines[i + 1] || '');
    if (header && separator?.length === header.length && separator.every(cell => /^:?-{3,}:?$/.test(cell))) {
      if (header.length < 2 || header.length > 8) throw Error('표에는 2~8개의 열이 필요합니다.');
      i += 1;
      const table = [header.map(markdownTableCellText)];
      while (i + 1 < lines.length && /^ */.exec(lines[i + 1])[0].length === indent) {
        const row = markdownTableCells(lines[i + 1]);
        if (!row) break;
        if (row.length !== header.length) throw Error('표의 열 개수가 일정해야 합니다.');
        table.push(row.map(markdownTableCellText));
        i += 1;
      }
      if (table.length === 1) table.push(header.map(() => ''));
      if (table.length > 20 || table.flat().some(cell => [...cell].length > 256)) {
        throw Error('표는 최대 20행이며 셀은 256자까지 가능합니다.');
      }
      add('table', JSON.stringify(table), false, indent);
      continue;
    }
    const [type, content, check] = markdownBlockType(text);
    const parts = [content];
    if (type === 'paragraph' || type === 'quote' || type === 'toggle') {
      while (i + 1 < lines.length && lines[i + 1].trim() &&
             /^ */.exec(lines[i + 1])[0].length === indent) {
        const next = lines[i + 1].slice(indent);
        const [nextType, nextText] = markdownBlockType(next);
        const expected = type === 'toggle' ? 'quote' : type;
        if (nextType !== expected || /^[\x60~]{3,}/.test(next) || markdownTableCells(next)) break;
        parts.push(nextText);
        i += 1;
      }
    }
    add(type, parts.join('\n'), check, indent);
  }
  if (blocks.length > 120 || blocks.reduce((length, block) => length + [...block.content].length, 0) > 45000) {
    throw Error('페이지당 최대 120개 블록과 45,000자를 가져올 수 있습니다.');
  }
  return {title, blocks};
}

function exportWorkspaceMarkdown(title, blocks) {
  const prefixes = {heading_1:'# ', heading_2:'## ', bullet:'- ', ordered_list:'1. ', quote:'> ', toggle:'> [!TOGGLE] '};
  return ['# ' + markdownCharacters(title), ...blocks.map(block => {
    const indent = '  '.repeat(block.depth || 0);
    const value = block.content;
    let lines;
    if (block.type === 'table') {
      const rows = JSON.parse(value);
      const text = cell => markdownCharacters(cell.replace(/&/g, '&amp;').replace(/</g, '&lt;')).replace(/\r?\n/g, '<br>');
      lines = rows.map(row => '| ' + row.map(text).join(' | ') + ' |');
      lines.splice(1, 0, '| ' + rows[0].map(() => '---').join(' | ') + ' |');
    } else if (block.type === 'code') {
      const longest = Math.max(2, ...(value.match(/[\x60]+/g) || []).map(match => match.length));
      const fence = markdownTicks.repeat(longest + 1);
      lines = [fence, ...value.split('\n'), fence];
    } else if (block.type === 'page_link' && value) {
      lines = ['[페이지 링크](#page=' + value + ')'];
    } else if (block.type === 'divider') {
      lines = ['---'];
    } else {
      const prefix = block.type === 'todo' ? '- [' + (block.checked ? 'x' : ' ') + '] ' : prefixes[block.type] || '';
      const escaped = value.split('\n').map(markdownCharacters);
      lines = escaped.map((line, index) => (index === 0 ? prefix :
        ['quote','toggle'].includes(block.type) ? '> ' : '') + line);
    }
    return lines.map(line => indent + line).join('\n');
  })].join('\n\n') + '\n';
}

function parseWorkspaceCsv(source) {
  const text = source.replace(/^\uFEFF/, '');
  const rows = [];
  let row = [];
  let cell = '';
  let state = 'start';
  const nextCell = () => {
    row.push(cell);
    cell = '';
    state = 'start';
  };
  const nextRow = () => {
    nextCell();
    if (row.length > 1 || row[0] !== '') rows.push(row);
    row = [];
  };
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (state === 'quoted') {
      if (char !== '"') cell += char;
      else if (text[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else state = 'closed';
    } else if (char === ',') nextCell();
    else if (char === '\r' || char === '\n') {
      if (char === '\r' && text[i + 1] === '\n') i += 1;
      nextRow();
    } else if (state === 'start' && char === '"') state = 'quoted';
    else if (state === 'closed' || char === '"') throw Error('CSV 따옴표 형식이 올바르지 않습니다.');
    else {
      cell += char;
      state = 'plain';
    }
  }
  if (state === 'quoted') throw Error('CSV 따옴표가 닫히지 않았습니다.');
  if (row.length || cell || state === 'closed') nextRow();
  return rows;
}

function csvProperties(database) {
  return database.properties.filter(property => !['formula','rollup','relation'].includes(property.type));
}

function csvFieldHeader(name) {
  return /^(?:제목|메모|title|notes|속성:.*)$/iu.test(name) ? '속성:' + name : name;
}

function workspaceCsvRecords(source, database) {
  const rows = parseWorkspaceCsv(source);
  if (rows.length < 2 || rows.length > 101) throw Error('CSV에 헤더와 1~100개 레코드가 필요합니다.');
  const fields = new Map(csvProperties(database).map(property => [csvFieldHeader(property.name), property]));
  const headers = rows.shift().map(header => header.trim());
  const targets = headers.map(header => {
    if (/^(제목|title)$/iu.test(header)) return 'title';
    if (/^(메모|notes)$/iu.test(header)) return 'notes';
    if (!fields.has(header)) throw Error('CSV 열에 해당하는 속성이 없습니다. ' + header);
    return fields.get(header);
  });
  if (!targets.includes('title') || new Set(targets).size !== targets.length) {
    throw Error('제목 열 하나와 중복 없는 속성 열이 필요합니다.');
  }
  return rows.map((row, index) => {
    if (row.length !== targets.length) throw Error('CSV ' + (index + 2) + '번째 행의 열 개수를 확인해 주세요.');
    const record = {title:'', notes:'', values:{}};
    for (const [i, field] of targets.entries()) {
      const value = row[i];
      if (typeof field === 'string') record[field] = value;
      else if (!value) continue;
      else if (field.type === 'number') {
        if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(value.trim()) || !Number.isFinite(Number(value))) {
          throw Error('숫자를 확인해 주세요. ' + field.name);
        }
        record.values[field.id] = Number(value);
      } else if (field.type === 'checkbox') {
        if (!/^(true|false|1|0)$/i.test(value.trim())) throw Error('체크박스는 true 또는 false를 입력합니다. ' + field.name);
        record.values[field.id] = /^(true|1)$/i.test(value.trim());
      } else if (field.type === 'multi_select') {
        let choices = null;
        if (value.trim().startsWith('[')) {
          try { choices = JSON.parse(value); } catch { throw Error('다중 선택 배열 형식이 올바르지 않습니다. ' + field.name); }
        }
        record.values[field.id] = Array.isArray(choices) ? choices : value.split(';').map(option => option.trim()).filter(Boolean);
      } else record.values[field.id] = value;
    }
    if (!record.title.trim()) throw Error('CSV ' + (index + 2) + '번째 행의 제목이 비어 있습니다.');
    return record;
  });
}

function csvWorkspaceCell(value) {
  let text = Array.isArray(value) ? JSON.stringify(value) : String(value ?? '');
  // Spreadsheet formulas must remain literal text when the user opens the CSV.
  if (typeof value === 'string' && /^[\s\uFEFF]*[=+\-@\uFF1D\uFF0B\uFF0D\uFF20]|^[\t\r\n]/u.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"','""') + '"';
}

function exportWorkspaceCsv(database) {
  const properties = csvProperties(database);
  const rows = [['제목','메모',...properties.map(property => csvFieldHeader(property.name))],
    ...database.records.map(record => [record.title,record.notes,...properties.map(property => record.values[property.id])])];
  return '\uFEFF' + rows.map(row => row.map(csvWorkspaceCell).join(',')).join('\r\n') + '\r\n';
}

function saveWorkspaceText(text, name, extension, type) {
  const basename = name.replace(/[\\/:*?"<>|\x00-\x1F]/g, '_').replace(/[. ]+$/, '') || 'My Workspace';
  const url = URL.createObjectURL(new Blob([text], {type}));
  const link = node('a', {href:url, download:basename + extension});
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function openWorkspaceTransfer(mode, database = null) {
  transferTarget = {mode, database};
  const isCsv = mode === 'csv';
  el('workspace-transfer-heading').textContent = isCsv ? 'CSV 가져오기' : 'Markdown 가져오기';
  el('workspace-transfer-help').textContent = isCsv ?
    '선택한 데이터베이스에 레코드를 추가합니다. 열 이름 예시 ' +
      ['제목','메모',...csvProperties(database).map(property => csvFieldHeader(property.name))].join(', ') :
    'UTF-8 Markdown 파일 또는 텍스트로 새 페이지를 만듭니다.';
  el('workspace-transfer-file').accept = isCsv ? '.csv,text/csv' : '.md,.markdown,.txt,text/plain,text/markdown';
  el('workspace-transfer-form').reset();
  el('workspace-transfer-status').textContent = '';
  transferDialog.showModal();
}

el('workspace-markdown-import').addEventListener('click', () => openWorkspaceTransfer('markdown'));
el('workspace-markdown-export').addEventListener('click', () => {
  if (canvasPage && !canvasComposing) {
    saveWorkspaceText(exportWorkspaceMarkdown(canvasTitle,canvasBlocks), canvasTitle,'.md','text/markdown;charset=utf-8');
  }
});
el('workspace-transfer-close').addEventListener('click', () => transferDialog.close());
el('workspace-transfer-file').addEventListener('change', async event => {
  const target = transferTarget;
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (file.size > workspaceTransferLimit) throw Error('파일은 256 KiB 이하만 가져올 수 있습니다.');
    const text = new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
    if (transferTarget !== target || event.target.files[0] !== file || !transferDialog.open) return;
    target.filename = file.name;
    el('workspace-transfer-text').value = text;
    el('workspace-transfer-status').textContent = file.name;
  } catch (error) {
    if (transferTarget === target) el('workspace-transfer-status').textContent = error.message;
  }
});
el('workspace-transfer-form').addEventListener('submit', async event => {
  event.preventDefault();
  const target = transferTarget;
  const submit = el('workspace-transfer-submit');
  const status = el('workspace-transfer-status');
  const close = el('workspace-transfer-close');
  const source = el('workspace-transfer-text').value;
  if (!target || submit.disabled) return;
  submit.disabled = true;
  close.disabled = true;
  try {
    if (!source.trim()) throw Error('파일을 선택하거나 텍스트를 입력해 주세요.');
    if (new TextEncoder().encode(source).length > workspaceTransferLimit) throw Error('텍스트가 256 KiB를 초과합니다.');
    const isCsv = target.mode === 'csv';
    if (!isCsv && currentView === 'canvas' && !await canvasMayNavigate()) return;
    const data = isCsv ? {records:workspaceCsvRecords(source,target.database)} : parseWorkspaceMarkdown(source,target.filename);
    const body = JSON.stringify(data);
    if (new TextEncoder().encode(body).length > workspaceTransferLimit) throw Error('가져올 데이터가 256 KiB를 초과합니다.');
    const path = isCsv ? '/api/v1/databases/' + target.database.id + '/records/batch' : '/api/v1/pages/import';
    const result = await api(path, {method:'POST',headers:requestHeaders,body});
    transferDialog.close();
    if (isCsv) {
      await refreshCustomDatabase();
      toast(result.items.length + '개 레코드를 가져왔습니다.');
    } else {
      await openCanvas(result.id,result);
      toast('Markdown에서 새 페이지를 만들었습니다.');
    }
  } catch (error) {
    if (transferDialog.open) status.textContent = error.message;
    else toast(error.message);
  } finally {
    submit.disabled = false;
    close.disabled = false;
  }
});
transferDialog.addEventListener('cancel', event => {
  if (el('workspace-transfer-submit').disabled) event.preventDefault();
});

const csvTools = el('custom-db-transfer');
const csvImport = node('button',{id:'workspace-csv-import',className:'secondary-button',type:'button'},'CSV 가져오기');
const csvExport = node('button',{id:'workspace-csv-export',className:'secondary-button',type:'button'},'CSV 저장');
csvImport.addEventListener('click', () => {
  const database = getActiveCustomDatabase();
  if (database) openWorkspaceTransfer('csv',database);
  else toast('데이터베이스를 먼저 선택해 주세요.');
});
csvExport.addEventListener('click', () => {
  const database = getActiveCustomDatabase();
  if (database) saveWorkspaceText(exportWorkspaceCsv(database),database.name,'.csv','text/csv;charset=utf-8');
  else toast('데이터베이스를 먼저 선택해 주세요.');
});
csvTools.append(csvImport,csvExport);

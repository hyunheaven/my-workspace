'use strict';

let linkedPage = null;
let linkedOptions = [];
let linkedRequest = 0;

function linkedPagePath(pageId) {
  return '/api/v1/pages/' + encodeURIComponent(pageId) + '/linked-views';
}

async function showPageLinkedViews(pageId) {
  const request = ++linkedRequest;
  const status = el('page-linked-status');
  const results = el('page-linked-results');
  results.replaceChildren();
  status.textContent = '';
  try {
    const {items} = await api(linkedPagePath(pageId));
    if (request !== linkedRequest || linkedPage !== pageId) return;
    for (const item of items) {
      const section = node('article',{className:'workspace-linked-view'});
      const header = node('div',{className:'workspace-tools-row'});
      const title = node('strong',{},item.database_name + ' · ' + item.view_name);
      const remove = node('button',{type:'button',className:'secondary-button','aria-label':item.view_name + ' 연결 해제'},'연결 해제');
      remove.addEventListener('click', async () => {
        remove.disabled = true;
        try {
          await api(linkedPagePath(pageId) + '/' + item.id,{
            method:'DELETE',headers:requestHeaders,body:'{}'
          });
          if (linkedPage === pageId) await showPageLinkedViews(pageId);
        } catch (error) {
          if (linkedPage === pageId) status.textContent = error.message;
        } finally {
          remove.disabled = false;
        }
      });
      header.append(title,remove);
      const view = node('div');
      section.append(header,view);
      results.append(section);
      Promise.resolve().then(() => renderLinkedDatabase(view,item.database_id,item.view_id)).catch(error => {
        if (section.isConnected) view.textContent = error.message;
      });
    }
  } catch (error) {
    if (request === linkedRequest) status.textContent = error.message;
  }
}

function populateLinkedViews() {
  const database = linkedOptions.find(item => item.id === el('page-linked-database').value);
  const view = el('page-linked-view');
  view.replaceChildren(node('option',{value:''},'보기 선택'));
  for (const item of database?.views || []) view.append(node('option',{value:item.id},item.title));
}

document.addEventListener('workspace-page-opened', event => {
  linkedPage = event.detail.id;
  linkedOptions = [];
  el('page-linked-form').classList.add('hidden');
  showPageLinkedViews(linkedPage);
});
el('page-linked-database').addEventListener('change',populateLinkedViews);
el('page-linked-configure').addEventListener('click', async () => {
  const pageId = linkedPage;
  const form = el('page-linked-form');
  const status = el('page-linked-status');
  if (!pageId) return;
  if (!form.classList.contains('hidden')) {
    form.classList.add('hidden');
    return;
  }
  const button = el('page-linked-configure');
  button.disabled = true;
  try {
    const options = await linkedDatabaseOptions();
    if (pageId !== linkedPage || currentView !== 'canvas') return;
    if (!options.length) {
      status.textContent = '내 데이터베이스에서 먼저 보기를 만들어 주세요.';
      return;
    }
    linkedOptions = options;
    const input = el('page-linked-database');
    input.replaceChildren(node('option',{value:''},'데이터베이스 선택'));
    for (const item of options) input.append(node('option',{value:item.id},item.title));
    populateLinkedViews();
    status.textContent = '';
    form.classList.remove('hidden');
    input.focus();
  } catch (error) {
    if (pageId === linkedPage) status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
el('page-linked-form').addEventListener('submit',async event => {
  event.preventDefault();
  const pageId = linkedPage;
  if (!pageId) return;
  const button = el('page-linked-add');
  const body = JSON.stringify({
    database_id:el('page-linked-database').value,
    view_id:el('page-linked-view').value
  });
  button.disabled = true;
  try {
    await api(linkedPagePath(pageId),{method:'POST',headers:requestHeaders,body});
    if (linkedPage === pageId) {
      el('page-linked-form').classList.add('hidden');
      await showPageLinkedViews(pageId);
    }
  } catch (error) {
    if (linkedPage === pageId) el('page-linked-status').textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

'use strict';
// Page Canvas accepts only plain text and structured text tables.
let canvasPageId=null;
let canvasPage=null;
let canvasBlocks=[];
let canvasDirty=false;
let canvasAutoSaveTimer=null;
let canvasSavePromise=null;
let canvasLoadVersion=0;
let canvasHistoryVersion=0;
let canvasCreating=false;
let pageCopyInProgress=false;
let pendingPageCopy=null;
const workspaceOpenTabs=canvasShortcutIDs('tabs');
const canvasPropertyCache=new Map();
let canvasPropertyQueue=Promise.resolve();
const canvasBlockTypes=['paragraph','heading_1','heading_2','bullet','todo','toggle','quote','code','divider','table'];
const canvasTypeLabels={paragraph:'텍스트',heading_1:'큰 제목',heading_2:'소제목',bullet:'글머리 기호',todo:'체크리스트',toggle:'토글',quote:'인용',code:'코드 텍스트',divider:'구분선',table:'표'};
const canvasDefaultTable=[['항목','내용'],['','']];
const canvasMaxBlocks=120;
const canvasAutoSaveDelay=900;

function canvasShortcutIDs(key){
  try{
    const list=JSON.parse(localStorage.getItem('myai-page-'+key)||'[]');
    return Array.isArray(list)?list.filter(id=>typeof id==='string'):[];
  }catch{return [];}
}
function canvasSetShortcutIDs(key,ids){
  try{localStorage.setItem('myai-page-'+key,JSON.stringify(ids));}
  catch{toast('이 브라우저에 페이지 바로가기를 저장할 수 없습니다.');}
}
function pageTabColor(page){
  return page?.properties?.tab_color||page?.tab_color||'none';
}
function renderWorkspaceTabs(docs=pageDocuments){
  const strip=el('workspace-page-tabs');
  const byId=new Map(docs.map(doc=>[doc.id,doc]));
  const selected=currentView==='canvas'?canvasPageId:null;
  strip.replaceChildren();
  for(const id of workspaceOpenTabs){
    const page=byId.get(id);
    if(!page)continue;
    const tab=node('div',{className:'workspace-page-tab','data-tab-color':pageTabColor(page)});
    const open=node('button',{type:'button',className:'workspace-tab-link','data-open-page-id':id},page.title);
    if(id===selected)open.setAttribute('aria-current','page');
    open.addEventListener('click',()=>openCanvas(id).catch(error=>toast(error.message)));
    const close=node('button',{type:'button',className:'workspace-tab-close','aria-label':page.title+' 탭 닫기'},'×');
    close.addEventListener('click',async()=>{
      const index=workspaceOpenTabs.indexOf(id);
      if(index<0)return;
      if(currentView==='canvas'&&canvasPageId===id){
        const next=workspaceOpenTabs[index+1]||workspaceOpenTabs[index-1];
        const moved=next?await openCanvas(next):await selectView('documents');
        if(!moved)return;
      }
      const remaining=workspaceOpenTabs.indexOf(id);
      if(remaining>=0)workspaceOpenTabs.splice(remaining,1);
      canvasSetShortcutIDs('tabs',workspaceOpenTabs);
      renderWorkspaceTabs();
    });
    tab.append(open,close);
    strip.append(tab);
  }
  strip.classList.toggle('hidden',!strip.childElementCount);
}
function showPageTags(tags){
  const list=el('page-tags');
  list.replaceChildren();
  for(const tag of tags){
    const chip=node('span',{className:'page-tag'});
    const link=node('button',{type:'button',className:'page-tag-label'},'#'+tag);
    link.addEventListener('click',()=>showDocumentsWithTag(tag));
    const remove=node('button',{type:'button',className:'page-tag-remove','aria-label':tag+' 태그 삭제'},'×');
    remove.addEventListener('click',()=>changeCanvasProperties(current=>({
      tags:current.tags.filter(value=>value!==tag)
    })).catch(error=>{el('page-tag-status').textContent=error.message;}));
    chip.append(link,remove);
    list.append(chip);
  }
}
function applyCanvasProperties(pageId,properties){
  const previous=canvasPropertyCache.get(pageId);
  if(previous&&previous.revision>properties.revision)return;
  canvasPropertyCache.set(pageId,properties);
  if(canvasPage?.id===pageId){
    canvasPage.properties=properties;
    showPageTags(properties.tags);
    document.dispatchEvent(new CustomEvent('workspace-page-properties',{detail:{id:pageId,properties}}));
  }
  pageDocuments=pageDocuments.map(page=>page.id===pageId?{...page,tab_color:properties.tab_color,properties}:page);
  canvasSidebarTree(pageDocuments);
}
function changeCanvasProperties(changes){
  const page=canvasPage;
  if(!page)return Promise.reject(Error('페이지를 먼저 열어 주세요.'));
  const path='/api/v1/pages/'+page.id;
  const operation=canvasPropertyQueue.then(async()=>{
    const previous=canvasPropertyCache.get(page.id)||page.properties;
    const patch=typeof changes==='function'?changes(previous):changes;
    try{
      const properties=await api(path+'/properties',{
        method:'PATCH',headers:requestHeaders,
        body:JSON.stringify({expected_revision:previous.revision,...patch})
      });
      applyCanvasProperties(page.id,properties);
      return properties;
    }catch(error){
      if(error.status===409){
        const latest=await api(path+'/content');
        applyCanvasProperties(page.id,latest.properties);
      }
      throw error;
    }
  });
  canvasPropertyQueue=operation.catch(()=>{});
  return operation;
}
function canvasShortcuts(docs){
  const byID=new Map(docs.map(doc=>[doc.id,doc]));
  for(const key of ['favorites','recent']){
    const shortcut=el('canvas-shortcuts-'+key);
    const entries=canvasShortcutIDs(key).map(id=>byID.get(id)).filter(Boolean);
    const list=shortcut.querySelector('div');
    list.replaceChildren();
    shortcut.classList.toggle('hidden',!entries.length);
    for(const page of entries){
      const button=node('button',{type:'button',className:'sidebar-shortcut'},page.title);
      button.addEventListener('click',()=>openCanvas(page.id));
      list.append(button);
    }
  }
  const favorite=canvasShortcutIDs('favorites').includes(canvasPage?.id);
  el('canvas-favorite').textContent=favorite?'★':'☆';
  el('canvas-favorite').setAttribute('aria-pressed',String(favorite));
}
function canvasPageMasthead(page){
  const template=catalog.find(item=>item.id===page.template_id);
  const cover=el('canvas-template-cover');
  const collection=template?.collection;
  cover.classList.toggle('hidden',!collection||!page.from_template);
  if(!collection)return;
  cover.dataset.section=template.section;
  cover.textContent=collection;
}
function canvasClearTimer(){
  clearTimeout(canvasAutoSaveTimer);
  canvasAutoSaveTimer=null;
}
function canvasStatus(status,failed=false){
  el('canvas-dirty-flag').textContent=status;
  el('canvas-dirty-flag').classList.toggle('save-error',failed);
}
function canvasScheduleSave(){
  canvasClearTimer();
  canvasAutoSaveTimer=setTimeout(()=>{
    canvasAutoSaveTimer=null;
    saveCanvas(true).catch(()=>{});
  },canvasAutoSaveDelay);
}
function canvasMarkDirty(){
  canvasDirty=true;
  canvasStatus('저장 대기 중');
  canvasScheduleSave();
}
function canvasResetDirty(){
  canvasDirty=false;
  canvasClearTimer();
  canvasStatus('변경사항 저장됨');
}
async function canvasMayNavigate(){
  if(!canvasDirty)return true;
  try{
    while(canvasDirty)await saveCanvas(true);
    return true;
  }catch(e){
    if(!window.confirm('페이지를 저장하지 못했습니다. 변경사항을 버리고 이동하시겠습니까?'))return false;
    canvasResetDirty();
    return true;
  }
}
function canvasNewBlock(type='paragraph',content='',checked=false){
  return {id:crypto.randomUUID(),type,content:type==='table'?JSON.stringify(canvasDefaultTable):content,checked};
}
function canvasInsertBlock(index,type='paragraph',content=''){
  if(canvasBlocks.length>=canvasMaxBlocks){
    toast('페이지당 최대 '+canvasMaxBlocks+'개 블록을 사용할 수 있습니다.');
    return null;
  }
  const block=canvasNewBlock(type,content);
  canvasBlocks.splice(index,0,block);
  return block;
}
function canvasFocusBlock(index,position=0){
  const row=el('canvas-blocks').children[index];
  const input=row?.querySelector('.canvas-block-text, .canvas-table-cell')||row?.querySelector('.block-tool-add');
  if(!input)return;
  input.focus({preventScroll:true});
  input.setSelectionRange?.(position,position);
  input.scrollIntoView({block:'nearest'});
}
function canvasAddBlock(type='paragraph',index=canvasBlocks.length){
  if(!canvasInsertBlock(index,type))return;
  canvasMarkDirty();
  canvasRenderBlocks();
  canvasFocusBlock(index);
}
function canvasMoveBlock(index,step){
  const next=index+step;
  if(next<0||next>=canvasBlocks.length)return;
  [canvasBlocks[index],canvasBlocks[next]]=[canvasBlocks[next],canvasBlocks[index]];
  canvasMarkDirty();
  canvasRenderBlocks();
  canvasFocusBlock(next);
}
function canvasChangeBlockType(block,index,type){
  if(type!==block.type){
    if(type==='table'){
      const rows=canvasDefaultTable.map(row=>[...row]);
      rows[1][0]=Array.from(block.content).slice(0,256).join('');
      if(rows[1][0]!==block.content){
        toast('표로 변환하려면 텍스트를 256자 이하로 줄여 주세요.');
        canvasRenderBlocks();
        canvasFocusBlock(index);
        return;
      }
      block.content=JSON.stringify(rows);
    }else if(block.type==='table'){
      block.content=canvasReadTable(block).map(row=>row.join('\t')).join('\n');
    }
    if(type!=='todo')block.checked=false;
    block.type=type;
    canvasMarkDirty();
  }
  canvasRenderBlocks();
  canvasFocusBlock(index);
}
function canvasSlashMenu(row,block,index,input){
  document.querySelectorAll('.canvas-slash-menu').forEach(menu=>menu.remove());
  const menu=node('div',{className:'canvas-slash-menu',role:'group','aria-label':'블록 명령'});
  const query=node('input',{type:'search',className:'canvas-slash-search','aria-label':'블록 유형 검색',placeholder:'블록 유형 검색','aria-controls':'canvas-slash-options',autocomplete:'off'});
  const options=node('div',{id:'canvas-slash-options',className:'canvas-slash-options',role:'listbox','aria-label':'블록 유형'});
  const glyph={paragraph:'T',heading_1:'H₁',heading_2:'H₂',bullet:'•',todo:'☑',toggle:'▸',quote:'❝',code:'{ }',divider:'─',table:'▦'};
  const aliases={paragraph:'text',heading_1:'h1 heading',heading_2:'h2 heading',bullet:'list bullet',todo:'task check checklist'};
  let choices=[],selected=0;
  const activate=type=>canvasChangeBlockType(block,index,type);
  const highlight=()=>{
    choices.forEach((option,i)=>{
      option.classList.toggle('highlight',i===selected);
      option.setAttribute('aria-selected',String(i===selected));
    });
    if(choices[selected]){
      query.setAttribute('aria-activedescendant',choices[selected].id);
      choices[selected].scrollIntoView({block:'nearest'});
    }else query.removeAttribute('aria-activedescendant');
  };
  const render=()=>{
    const filter=query.value.trim().toLowerCase();
    choices=[];
    selected=0;
    options.replaceChildren();
    canvasBlockTypes.filter(type=>[canvasTypeLabels[type],type,aliases[type]||''].join(' ').includes(filter)).forEach(type=>{
      const choice=node('button',{type:'button',id:'canvas-command-'+type,className:'canvas-slash-item',role:'option'});
      choice.append(node('span',{className:'canvas-slash-glyph','aria-hidden':'true'},glyph[type]),node('span',{},canvasTypeLabels[type]));
      choice.addEventListener('click',()=>activate(type));
      choices.push(choice);
      options.append(choice);
    });
    if(!choices.length)options.append(node('span',{className:'canvas-slash-title'},'일치하는 블록이 없습니다.'));
    highlight();
  };
  query.addEventListener('input',render);
  menu.addEventListener('keydown',event=>{
    if(event.isComposing||event.keyCode===229)return;
    if(event.key==='Escape'){
      event.preventDefault();
      menu.remove();
      input.focus();
    }else if(event.key==='Enter'&&event.target===query){
      event.preventDefault();
      choices[selected]?.click();
    }else if(choices.length&&(event.key==='ArrowDown'||event.key==='ArrowUp')){
      event.preventDefault();
      selected=(selected+(event.key==='ArrowDown'?1:-1)+choices.length)%choices.length;
      query.focus({preventScroll:true});
      highlight();
    }
  });
  menu.addEventListener('focusout',event=>{
    if(!menu.contains(event.relatedTarget))menu.remove();
  });
  menu.append(query,options);
  row.append(menu);
  render();
  query.focus({preventScroll:true});
}
function canvasReadTable(block){
  return JSON.parse(block.content);
}
function canvasRenderTable(block,readOnly=false){
  const rows=canvasReadTable(block);
  const wrapper=node('div',{className:'canvas-table-wrapper'});
  const table=node('table',{className:'canvas-table','aria-label':'표'});
  const head=node('thead'),body=node('tbody');
  const status=node('span',{className:'canvas-table-status',role:'status'});
  const commit=()=>{
    const content=JSON.stringify(rows);
    if(Array.from(content).length>4000){
      status.textContent='표가 최대 길이에 도달했습니다. 일부 셀 내용을 줄여 주세요.';
      return false;
    }
    block.content=content;
    status.textContent='';
    canvasMarkDirty();
    return true;
  };
  const controls=node('div',{className:'canvas-table-controls'});
  const add=node('button',{type:'button',className:'canvas-table-add'},'+ 행 추가');
  const render=()=>{
    head.replaceChildren();
    body.replaceChildren();
    rows.forEach((cells,rowIndex)=>{
      const row=node('tr');
      cells.forEach((text,columnIndex)=>{
        const cell=rowIndex===0?node('th',{scope:'col'}):node('td');
        if(readOnly)cell.textContent=text;
        else{
          const input=node('textarea',{className:'canvas-table-cell',rows:'1',maxlength:'256',
            'aria-label':rowIndex===0?'열 '+(columnIndex+1)+' 제목':rowIndex+'행 '+(columnIndex+1)+'열'});
          input.value=text;
          input.addEventListener('input',()=>{
            const previous=rows[rowIndex][columnIndex];
            rows[rowIndex][columnIndex]=input.value;
            if(!commit())input.value=rows[rowIndex][columnIndex]=previous;
          });
          cell.append(input);
        }
        row.append(cell);
      });
      if(!readOnly){
        const actions=rowIndex===0?node('th',{scope:'col','aria-label':'행 편집'}):node('td',{className:'canvas-table-row-actions'});
        if(rowIndex!==0){
          const remove=node('button',{type:'button',className:'canvas-table-remove','aria-label':rowIndex+'행 삭제'},'×');
          remove.disabled=rows.length<=2;
          remove.addEventListener('click',()=>{
            rows.splice(rowIndex,1);
            commit();
            render();
            (body.rows[rowIndex-1]||body.rows[body.rows.length-1]).querySelector('textarea').focus();
          });
          actions.append(remove);
        }
        row.append(actions);
      }
      (rowIndex===0?head:body).append(row);
    });
    add.disabled=rows.length>=20;
  };
  add.addEventListener('click',()=>{
    rows.push(Array(rows[0].length).fill(''));
    if(!commit()){
      rows.pop();
      return;
    }
    render();
    body.rows[body.rows.length-1].querySelector('textarea').focus();
  });
  controls.append(add,status);
  render();
  table.append(head,body);
  wrapper.append(table);
  if(!readOnly)wrapper.append(controls);
  return wrapper;
}
function canvasRenderBlocks(){
  const root=el('canvas-blocks');
  root.replaceChildren();
  if(!canvasBlocks.length){
    const start=node('button',{type:'button',className:'canvas-start-block'},'텍스트 블록 추가');
    start.addEventListener('click',()=>canvasAddBlock());
    root.append(start);
    return;
  }
  canvasBlocks.forEach((block,index)=>{
    const row=node('div',{className:'canvas-block block-'+block.type,'data-block-id':block.id});
    const tools=node('div',{className:'block-tools'});
    const add=node('button',{type:'button',className:'block-tool-button block-tool-add','aria-label':'아래 블록 추가',title:'아래 블록 추가'},'+');
    add.addEventListener('click',()=>canvasAddBlock('paragraph',index+1));
    tools.append(add);
    const more=node('button',{type:'button',className:'block-tool-button block-tool-menu','aria-label':'블록 도구','aria-expanded':'false'},'⋮⋮');
    more.addEventListener('click',()=>more.setAttribute('aria-expanded',String(row.classList.toggle('tools-open'))));
    tools.append(more);
    const options=node('div',{className:'block-tool-options'});
    const chooser=node('select',{className:'block-type','aria-label':'블록 유형'});
    canvasBlockTypes.forEach(type=>chooser.append(node('option',{value:type},canvasTypeLabels[type])));
    chooser.value=block.type;
    chooser.addEventListener('change',()=>canvasChangeBlockType(block,index,chooser.value));
    options.append(chooser);
    const removeBlock=()=>{
      canvasBlocks.splice(index,1);
      canvasMarkDirty();
      canvasRenderBlocks();
      if(canvasBlocks.length)canvasFocusBlock(Math.max(0,index-1));
      else root.querySelector('button').focus();
    };
    for(const [icon,label,action,disabled] of [
      ['↑','블록 위로 이동',()=>canvasMoveBlock(index,-1),index===0],
      ['↓','블록 아래로 이동',()=>canvasMoveBlock(index,1),index===canvasBlocks.length-1],
      ['×','블록 삭제',removeBlock,false]
    ]){
      const button=node('button',{type:'button',className:'block-tool-button','aria-label':label,title:label},icon);
      button.disabled=disabled;
      button.addEventListener('click',action);
      options.append(button);
    }
    tools.append(options);
    row.append(tools);
    const content=node('div',{className:'block-content'});
    if(block.type==='divider')content.append(node('hr'));
    else if(block.type==='table')content.append(canvasRenderTable(block));
    else{
      const input=node('textarea',{className:'canvas-block-text','aria-label':canvasTypeLabels[block.type],rows:block.type==='code'?4:1,maxlength:'4000',placeholder:block.type==='paragraph'?'텍스트를 입력하거나 /를 눌러 블록을 추가하세요':''});
      input.value=block.content;
      const fit=()=>{
        input.style.height='auto';
        input.style.height=Math.min(400,Math.max(31,input.scrollHeight+2))+'px';
      };
      input.addEventListener('input',()=>{
        block.content=input.value;
        canvasMarkDirty();
        fit();
      });
      if(block.type==='todo'){
        const checkbox=node('input',{type:'checkbox','aria-label':'체크리스트 완료'});
        checkbox.checked=block.checked;
        row.classList.toggle('checked',block.checked);
        checkbox.addEventListener('change',()=>{
          block.checked=checkbox.checked;
          row.classList.toggle('checked',checkbox.checked);
          canvasMarkDirty();
        });
        content.append(checkbox);
      }
      if(block.type==='bullet')content.append(node('span',{className:'block-prefix','aria-hidden':'true'},'•'));
      if(block.type==='quote')content.append(node('span',{className:'block-prefix','aria-hidden':'true'},'│'));
      if(block.type==='toggle'){
        const toggle=node('button',{type:'button',className:'toggle-caret','aria-label':'내용 접기 또는 펼치기','aria-expanded':'true'},'▾');
        toggle.addEventListener('click',()=>{
          const collapsed=input.classList.toggle('hidden');
          toggle.textContent=collapsed?'▸':'▾';
          toggle.setAttribute('aria-expanded',String(!collapsed));
        });
        content.append(toggle);
      }
      input.addEventListener('keydown',event=>{
        if(event.isComposing||event.keyCode===229)return;
        if(event.key==='/'&&input.value===''&&block.type==='paragraph'){
          event.preventDefault();
          canvasSlashMenu(row,block,index,input);
        }else if(event.key==='Enter'&&!event.shiftKey&&block.type!=='code'&&block.type!=='toggle'){
          event.preventDefault();
          const nextType=['bullet','todo'].includes(block.type)&&input.value.trim()?block.type:'paragraph';
          if(!canvasInsertBlock(index+1,nextType,input.value.slice(input.selectionEnd)))return;
          block.content=input.value.slice(0,input.selectionStart);
          canvasMarkDirty();
          canvasRenderBlocks();
          canvasFocusBlock(index+1);
        }else if(event.key==='Backspace'&&input.value===''&&index>0){
          event.preventDefault();
          removeBlock();
        }
      });
      content.append(input);
      queueMicrotask(fit);
    }
    row.append(content);
    root.append(row);
  });
}
function canvasSidebarTree(docs){
  renderWorkspaceTabs(docs);
  canvasShortcuts(docs);
  const root=el('sidebar-page-tree');
  root.replaceChildren();
  const byParent=new Map();
  const available=new Set(docs.map(doc=>doc.id));
  for(const doc of docs){
    const parent=doc.parent_id&&available.has(doc.parent_id)?doc.parent_id:null;
    if(!byParent.has(parent))byParent.set(parent,[]);
    byParent.get(parent).push(doc);
  }
  if(!docs.length){
    root.append(node('span',{className:'sidebar-empty'},'페이지가 없습니다'));
    return;
  }
  const seen=new Set();
  const addGroup=(children,depth)=>{
    for(const doc of children){
      if(seen.has(doc.id))continue;
      seen.add(doc.id);
      const selected=doc.id===canvasPageId;
      const row=node('div',{className:'sidebar-page-row'});
      row.style.paddingLeft=(8+Math.min(depth,9)*13)+'px';
      const button=node('button',{type:'button',className:'sidebar-page'+(selected?' selected':''),'data-page-id':doc.id},'▤ '+doc.title);
      button.dataset.tabColor=pageTabColor(doc);
      if(selected)button.setAttribute('aria-current','page');
      button.addEventListener('click',()=>openCanvas(doc.id));
      const add=node('button',{type:'button',className:'sidebar-page-add','aria-label':doc.title+' 하위 페이지 추가'},'+');
      add.addEventListener('click',()=>createCanvasPage(doc.id).catch(error=>toast(error.message)));
      row.append(button,add);
      root.append(row);
      addGroup(byParent.get(doc.id)||[],depth+1);
    }
  };
  addGroup(byParent.get(null)||[],0);
  addGroup(docs,0);
}
function canvasShowEmpty(){
  canvasPage=null;
  canvasBlocks=[];
  el('canvas-empty').classList.remove('hidden');
  el('canvas-editing').classList.add('hidden');
  el('canvas-head-actions').classList.add('hidden');
  el('canvas-breadcrumb').textContent='내 페이지';
  canvasResetDirty();
}
function canvasTemplateSummary(page){
  const box=el('canvas-template-summary');
  box.replaceChildren();
  const template=catalog.find(item=>item.id===page.template_id);
  const legacyForm=template&&!page.from_template;
  const hasLegacyValues=legacyForm&&Object.values(page.values||{}).some(Boolean);
  el('canvas-template-edit').classList.toggle('hidden',!legacyForm);
  box.classList.toggle('hidden',!hasLegacyValues);
  if(!hasLegacyValues)return;
  box.append(node('strong',{},'이전 버전 템플릿 필드 · '+template.name));
  for(const field of template.fields){
    const value=page.values?.[field.id];
    if(!value)continue;
    const line=node('div',{className:'canvas-template-field'});
    line.append(node('small',{},field.label),node('p',{},value));
    box.append(line);
  }
}
function canvasBreadcrumb(page,docs){
  const path=[];
  const byId=new Map(docs.map(item=>[item.id,item]));
  const seen=new Set();
  let item=page;
  while(item&&!seen.has(item.id)&&path.length<15){
    path.unshift(item.title);
    seen.add(item.id);
    item=byId.get(item.parent_id);
  }
  el('canvas-breadcrumb').textContent='개인 Workspace / '+path.join(' / ');
}
function canvasPageMeta(page){
  const template=catalog.find(item=>item.id===page.template_id);
  el('canvas-meta').textContent=[template?.name||'개인 페이지','Revision '+page.revision,
    new Date(page.updated_at).toLocaleString('ko-KR')].join(' · ');
}
function canvasDisplayPage(page,docs,created=false){
  const known=canvasPropertyCache.get(page.id);
  if(known&&known.revision>page.properties.revision)page.properties=known;
  else canvasPropertyCache.set(page.id,page.properties);
  canvasPage=page;
  canvasPageId=page.id;
  canvasBlocks=page.blocks.map(block=>({...block}));
  el('canvas-empty').classList.add('hidden');
  el('canvas-editing').classList.remove('hidden');
  el('canvas-head-actions').classList.remove('hidden');
  el('canvas-title').value=page.title;
  canvasPageMeta(page);
  canvasPageMasthead(page);
  canvasBreadcrumb(page,docs);
  canvasTemplateSummary(page);
  canvasRenderBlocks();
  canvasResetDirty();
  if(!workspaceOpenTabs.includes(page.id)){
    workspaceOpenTabs.push(page.id);
    if(workspaceOpenTabs.length>24)workspaceOpenTabs.shift();
    canvasSetShortcutIDs('tabs',workspaceOpenTabs);
  }
  el('page-tag-input').value='';
  el('page-tag-status').textContent='';
  showPageTags(page.properties.tags);
  canvasSetShortcutIDs('recent',[page.id,...canvasShortcutIDs('recent').filter(id=>id!==page.id)].slice(0,8));
  document.dispatchEvent(new CustomEvent('workspace-page-opened',{detail:{id:page.id,created,properties:page.properties}}));
}
function canvasUpdateTree(page,docs){
  pageDocuments=docs;
  canvasMergePageIntoTree(page);
  canvasBreadcrumb(page,pageDocuments);
}
function canvasMergePageIntoTree(page){
  const existing=pageDocuments.find(item=>item.id===page.id);
  if(!existing)pageDocuments=[...pageDocuments,page];
  else if(page.revision>=existing.revision)pageDocuments=pageDocuments.map(item=>item.id===page.id?page:item);
  canvasSidebarTree(pageDocuments);
}
async function loadCanvas(createdPage){
  const version=++canvasLoadVersion;
  const requestedId=canvasPageId;
  const active=()=>version===canvasLoadVersion&&currentView==='canvas';
  if(createdPage){
    canvasDisplayPage(createdPage,pageDocuments,true);
    canvasUpdateTree(createdPage,pageDocuments);
  }else{
    canvasPage=null;
    el('canvas-editing').classList.add('hidden');
    el('canvas-empty').classList.add('hidden');
    el('canvas-head-actions').classList.add('hidden');
  }
  const {items:docs}=await api('/api/v1/pages/tree').catch(error=>{
    if(createdPage)return {items:pageDocuments};
    throw error;
  });
  if(!active())return;
  pageDocuments=docs;
  if(createdPage){
    canvasUpdateTree(canvasPage,docs);
    return;
  }
  const id=requestedId||docs[0]?.id;
  if(!id){
    canvasPageId=null;
    canvasSidebarTree(docs);
    canvasShowEmpty();
    return;
  }
  const page=await api('/api/v1/pages/'+id+'/content');
  if(!active())return;
  canvasDisplayPage(page,docs);
  canvasUpdateTree(page,docs);
}
async function openCanvas(pageId,createdPage){
  return selectView('canvas',{pageId,createdPage});
}
async function createCanvasPage(parent=null,starter=false){
  if(canvasCreating)return;
  canvasCreating=true;
  try{
    if(!await canvasMayNavigate())return;
    const page=await api('/api/v1/pages',{method:'POST',headers:requestHeaders,
      body:JSON.stringify({title:starter?'시작하기':'제목 없음',parent_id:parent})});
    if(!await openCanvas(page.id,page))return;
    if(starter){
      canvasBlocks=[
        canvasNewBlock('heading_1','나의 Workspace'),
        canvasNewBlock('paragraph','이 페이지는 나만의 작업 공간입니다. 텍스트 블록을 추가하거나 아래 항목을 수정해 보세요.'),
        canvasNewBlock('todo','첫 문서 작성하기'),
        canvasNewBlock('todo','하위 페이지 만들기'),
        canvasNewBlock('toggle','안전한 사용 안내: 승인 전에는 업무상 기밀 자료를 입력하지 않습니다.')
      ];
      canvasRenderBlocks();
      canvasMarkDirty();
      await saveCanvas(true);
    }
    el('canvas-title').focus();
    loadDocuments().catch(()=>{});
  }finally{
    canvasCreating=false;
  }
}
async function saveCanvas(silent=false){
  while(canvasSavePromise)await canvasSavePromise;
  if(!canvasPage||!canvasDirty)return;
  canvasClearTimer();
  const page=canvasPage;
  const title=el('canvas-title').value.trim();
  const snapshot=JSON.stringify({title,blocks:canvasBlocks,expected_revision:page.revision});
  canvasStatus('저장 중…');
  const request=(async()=>{
    if(!title)throw Error('페이지 제목을 입력해 주세요.');
    return api('/api/v1/pages/'+page.id+'/content',{method:'PUT',headers:requestHeaders,body:snapshot});
  })();
  canvasSavePromise=request.then(updated=>{
    if(canvasPage?.id!==page.id)return;
    if(canvasPage.properties.revision>updated.properties.revision)updated.properties=canvasPage.properties;
    const current=JSON.stringify({title:el('canvas-title').value.trim(),blocks:canvasBlocks,expected_revision:page.revision});
    canvasPage=updated;
    if(snapshot===current)canvasResetDirty();
    else{
      canvasStatus('새 변경사항 저장 대기 중');
      canvasScheduleSave();
    }
    canvasPageMeta(updated);
    canvasUpdateTree(updated,pageDocuments);
    if(!silent)toast('페이지를 저장했습니다.');
  }).catch(error=>{
    canvasClearTimer();
    canvasStatus(error.status===409?'다른 창에서 변경된 페이지입니다. 현재 편집 내용은 화면에 남아 있습니다.':'저장 실패 · '+error.message,true);
    throw error;
  }).finally(()=>{
    canvasSavePromise=null;
  });
  return canvasSavePromise;
}
async function restoreCanvasRevision(snapshot,button){
  const page=canvasPage;
  if(!page||!window.confirm('이 버전의 내용을 새 리비전으로 복원할까요?'))return;
  button.disabled=true;
  try{
    const restored=await api('/api/v1/pages/'+page.id+'/history/'+snapshot.revision+'/restore',{
      method:'POST',headers:requestHeaders,body:JSON.stringify({expected_revision:page.revision})});
    if(canvasPage?.id!==page.id)return;
    el('canvas-history-dialog').close();
    canvasDisplayPage(restored,pageDocuments);
    canvasUpdateTree(restored,pageDocuments);
    toast('선택한 버전을 새 리비전으로 복원했습니다.');
  }catch(error){
    el('canvas-history-status').textContent=error.message;
  }finally{
    button.disabled=false;
  }
}
function canvasRenderHistory(snapshot){
  const preview=el('canvas-history-preview');
  preview.replaceChildren(node('h3',{},snapshot.title));
  if(snapshot.revision!==canvasPage?.revision){
    const restore=node('button',{id:'canvas-history-restore',type:'button',className:'secondary-button'},'이 버전 복원');
    restore.addEventListener('click',()=>restoreCanvasRevision(snapshot,restore));
    preview.append(restore);
  }
  const template=catalog.find(item=>item.id===canvasPage?.template_id);
  for(const field of template?.fields||[]){
    const value=snapshot.values?.[field.id];
    if(value)preview.append(node('strong',{},field.label),node('p',{className:'canvas-history-text'},value));
  }
  for(const block of snapshot.blocks){
    if(block.type==='divider')preview.append(node('hr'));
    else if(block.type==='table')preview.append(canvasRenderTable(block,true));
    else{
      const tag={heading_1:'h4',heading_2:'h5',code:'pre',quote:'blockquote'}[block.type]||'p';
      const prefix=block.type==='todo'?(block.checked?'☑ ':'☐ '):block.type==='bullet'?'• ':'';
      preview.append(node(tag,{className:'canvas-history-text'},prefix+block.content));
    }
  }
}
async function duplicateCanvasPage(){
  if(pageCopyInProgress||!canvasPage)return;
  const sourceId=canvasPage.id;
  pageCopyInProgress=true;
  const button=el('canvas-duplicate');
  button.disabled=true;
  try{
    await saveCanvas(true);
    await canvasPropertyQueue;
    const page=canvasPage;
    if(currentView!=='canvas'||page?.id!==sourceId)return;
    if(pendingPageCopy?.id!==page.id||pendingPageCopy?.revision!==page.revision){
      pendingPageCopy={id:page.id,revision:page.revision,requestId:crypto.randomUUID()};
    }
    const copy=await api('/api/v1/pages/'+page.id+'/duplicate',{method:'POST',headers:requestHeaders,
      body:JSON.stringify({expected_revision:page.revision,request_id:pendingPageCopy.requestId})});
    pendingPageCopy=null;
    canvasMergePageIntoTree(copy);
    if(currentView==='canvas'&&canvasPage?.id===page.id)await openCanvas(copy.id,copy);
    loadDocuments().catch(()=>{});
  }catch(error){
    if(error.status>=400&&error.status<500)pendingPageCopy=null;
    toast('페이지 복제 실패 · '+error.message);
  }finally{
    button.disabled=false;
    pageCopyInProgress=false;
  }
}
function installCanvasCommands(){
  const cover=node('div',{id:'canvas-template-cover',className:'canvas-template-cover hidden'});
  el('canvas-title').before(cover);
  const favorite=node('button',{id:'canvas-favorite',type:'button',className:'secondary-button canvas-star',
    'aria-label':'페이지 즐겨찾기','aria-pressed':'false'},'☆');
  const duplicate=node('button',{id:'canvas-duplicate',type:'button',className:'secondary-button'},'페이지 복제');
  el('canvas-history').before(favorite,duplicate);
  favorite.addEventListener('click',()=>{
    if(!canvasPage)return;
    const ids=canvasShortcutIDs('favorites');
    const id=canvasPage.id;
    canvasSetShortcutIDs('favorites',ids.includes(id)?ids.filter(item=>item!==id):[id,...ids]);
    canvasShortcuts(pageDocuments);
  });
  duplicate.addEventListener('click',duplicateCanvasPage);
  for(const [key,label] of [['favorites','즐겨찾기'],['recent','최근 페이지']]){
    const details=node('details',{id:'canvas-shortcuts-'+key,className:'sidebar-shortcuts hidden'});
    details.open=key==='favorites';
    details.append(node('summary',{},label),node('div'));
    el('sidebar-page-tree').parentElement.before(details);
  }
}
installCanvasCommands();
el('page-tag-editor').addEventListener('submit',async event=>{
  event.preventDefault();
  const input=el('page-tag-input');
  const status=el('page-tag-status');
  if(!canvasPage||!input.value.trim())return;
  const label=input.value.normalize('NFKC').trim().replace(/^#+/,'').trim().replace(/\s+/g,' ');
  if(!label)return;
  const tags=canvasPage.properties.tags;
  if(tags.some(tag=>tag.toLowerCase()===label.toLowerCase())){
    status.textContent='이미 추가된 태그입니다.';
    return;
  }
  if(tags.length>=16){status.textContent='페이지당 태그는 최대 16개입니다.';return;}
  const pageId=canvasPage.id;
  const submit=event.currentTarget.querySelector('[type=submit]');
  submit.disabled=true;
  try{
    await changeCanvasProperties(current=>({tags:[...current.tags,label]}));
    if(canvasPage?.id===pageId){input.value='';status.textContent='태그를 저장했습니다.';}
  }catch(error){if(canvasPage?.id===pageId)status.textContent=error.message;}
  finally{submit.disabled=false;}
});
async function canvasShowHistory(){
  if(!canvasPage)return;
  const pageId=canvasPage.id;
  const version=++canvasHistoryVersion;
  await saveCanvas(true);
  if(version!==canvasHistoryVersion||currentView!=='canvas'||canvasPage?.id!==pageId)return;
  const dialog=el('canvas-history-dialog');
  const list=el('canvas-history-revisions');
  const preview=el('canvas-history-preview');
  const more=el('canvas-history-more');
  list.replaceChildren();
  preview.replaceChildren();
  more.classList.add('hidden');
  more.onclick=null;
  el('canvas-history-status').textContent='페이지 이력 불러오는 중…';
  if(!dialog.open)dialog.showModal();
  const active=()=>version===canvasHistoryVersion&&dialog.open&&canvasPage?.id===pageId;
  let revisionVersion=0;
  const load=async before=>{
    more.disabled=true;
    try{
      const {items}=await api('/api/v1/pages/'+pageId+'/history'+(before?'?before_revision='+before:''));
      if(!active())return;
      for(const item of items){
        const button=node('button',{type:'button',className:'secondary-button','data-revision':item.revision,'aria-pressed':'false'},
          'Revision '+item.revision+' · '+new Date(item.created_at).toLocaleString('ko-KR'));
        button.addEventListener('click',async()=>{
          const selected=++revisionVersion;
          for(const other of list.children)other.setAttribute('aria-pressed',String(other===button));
          preview.replaceChildren(node('p',{},'저장된 내용 불러오는 중…'));
          try{
            const snapshot=await api('/api/v1/pages/'+pageId+'/history/'+item.revision);
            if(active()&&selected===revisionVersion)canvasRenderHistory(snapshot);
          }catch(error){
            if(active()&&selected===revisionVersion)preview.replaceChildren(node('p',{},error.message));
          }
        });
        list.append(button);
      }
      el('canvas-history-status').textContent=list.children.length?'버전을 선택해 내용을 확인하세요.':'저장된 페이지 이력이 없습니다.';
      more.classList.toggle('hidden',items.length<100);
      more.onclick=items.length>=100?()=>load(items.at(-1).revision):null;
    }catch(error){
      if(active())el('canvas-history-status').textContent=error.message;
    }finally{
      if(active())more.disabled=false;
    }
  };
  await load();
}
el('nav-canvas').addEventListener('click',()=>selectView('canvas'));
el('sidebar-create-page').addEventListener('click',()=>createCanvasPage().catch(error=>toast(error.message)));
el('canvas-create-start').addEventListener('click',()=>createCanvasPage(null,true).catch(error=>toast(error.message)));
el('canvas-create-empty').addEventListener('click',()=>createCanvasPage().catch(error=>toast(error.message)));
el('canvas-save').addEventListener('click',()=>saveCanvas().catch(error=>toast('저장 실패: '+error.message)));
el('canvas-title').addEventListener('input',canvasMarkDirty);
el('canvas-add-block').addEventListener('click',()=>canvasAddBlock(el('canvas-new-type').value));
el('canvas-template-edit').addEventListener('click',async()=>{
  if(!canvasPage||!await canvasMayNavigate())return;
  const template=catalog.find(item=>item.id===canvasPage?.template_id);
  if(template)openEditor(template,canvasPage);
});
el('canvas-history').addEventListener('click',()=>canvasShowHistory().catch(error=>{
  if(el('canvas-history-dialog').open)el('canvas-history-status').textContent=error.message;
  else toast('페이지 이력 열기 실패: '+error.message);
}));
el('canvas-history-close').addEventListener('click',()=>el('canvas-history-dialog').close());
window.addEventListener('beforeunload',event=>{
  if(canvasDirty){
    event.preventDefault();
    event.returnValue='';
  }
});
document.addEventListener('keydown',event=>{
  if(!event.isComposing&&(event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='s'&&currentView==='canvas'){
    event.preventDefault();
    saveCanvas().catch(error=>toast(error.message));
  }
});

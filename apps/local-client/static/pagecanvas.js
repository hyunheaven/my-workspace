'use strict';
// Page Canvas accepts only plain text and structured text tables.
let canvasPageId=null;
let canvasPage=null;
let canvasBlocks=[];
let canvasTitle='';
let canvasDirty=false;
let canvasAutoSaveTimer=null;
let canvasSavePromise=null;
let canvasConflict=false;
let canvasComposing=null;
let canvasDraftStored=false;
let canvasDraftRestored=false;
let canvasDraftBase=null;
let canvasUndoStack=[],canvasRedoStack=[],canvasEditGroup=null;
let canvasBlockSelection=null,canvasDraggedId=null;
const canvasCollapsed=new Set();
let canvasLoadVersion=0;
let canvasHistoryVersion=0;
let canvasCreating=false;
let pageCopyInProgress=false;
let pendingPageCopy=null;
const workspaceOpenTabs=canvasShortcutIDs('tabs');
const canvasPropertyCache=new Map();
let canvasPropertyQueue=Promise.resolve();
const canvasBlockTypes=['paragraph','heading_1','heading_2','bullet','ordered_list','todo','toggle','quote','code','divider','table','page_link'];
const canvasTypeLabels={paragraph:'텍스트',heading_1:'큰 제목',heading_2:'소제목',bullet:'글머리 기호',ordered_list:'번호 목록',todo:'체크리스트',toggle:'토글',quote:'인용',code:'코드 텍스트',divider:'구분선',table:'표',page_link:'페이지 링크'};
const canvasDefaultTable=[['항목','내용'],['','']];
const canvasMaxBlocks=120;
const canvasMaxDepth=6;
const canvasClipboardType='application/x-my-workspace-blocks';
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
  el('canvas-save').textContent=failed?'저장 다시 시도':'페이지 저장';
}
function canvasScheduleSave(){
  canvasClearTimer();
  if(canvasComposing||canvasConflict)return;
  canvasAutoSaveTimer=setTimeout(()=>{
    canvasAutoSaveTimer=null;
    saveCanvas(true).catch(()=>{});
  },canvasAutoSaveDelay);
}
function canvasDraftKey(id){return 'myai-page-draft-v1-'+workspaceDraftScope+'-'+id;}
function canvasDraftRead(id){
  try{return JSON.parse(sessionStorage.getItem(canvasDraftKey(id)));}
  catch{return null;}
}
function canvasDraftRemove(id){
  try{sessionStorage.removeItem(canvasDraftKey(id));}catch{}
}
function canvasSameContent(title,blocks,other){
  return title===other.title&&Array.isArray(other.blocks)&&blocks.length===other.blocks.length&&blocks.every((block,index)=>{
    const saved=other.blocks[index];
    return block.id===saved.id&&block.type===saved.type&&block.content===saved.content&&block.checked===saved.checked&&
      canvasDepth(block)===canvasDepth(saved);
  });
}
function canvasPersistDraft(){
  if(!canvasPage)return;
  try{
    const {id,title,blocks}=canvasPage;
    const base=canvasDraftBase||{title,blocks};
    sessionStorage.setItem(canvasDraftKey(id),JSON.stringify({title:canvasTitle,blocks:canvasBlocks,base}));
    canvasDraftStored=true;
  }catch{canvasDraftStored=false;}
}
function canvasMarkDirty(){
  canvasDirty=true;
  canvasDraftRestored=false;
  canvasPersistDraft();
  if(!canvasConflict)canvasStatus('저장 대기 중');
  canvasScheduleSave();
}
function canvasResetDirty(){
  canvasDirty=false;
  canvasConflict=false;
  canvasDraftStored=false;
  canvasDraftRestored=false;
  canvasDraftBase=null;
  if(canvasPage)canvasDraftRemove(canvasPage.id);
  canvasClearTimer();
  canvasStatus('변경사항 저장됨');
}
function canvasRestoreDraft(page){
  const draft=canvasDraftRead(page.id);
  if(!draft||typeof draft.title!=='string'||!Array.isArray(draft.blocks)||!draft.base||
      canvasSameContent(draft.title.trim(),draft.blocks,page)){
    canvasResetDirty();
    return;
  }
  canvasTitle=draft.title;
  canvasBlocks=draft.blocks;
  canvasDirty=true;
  canvasDraftStored=true;
  canvasDraftRestored=true;
  canvasDraftBase=draft.base;
  canvasConflict=!canvasSameContent(page.title,page.blocks,draft.base);
  canvasStatus(canvasConflict?'다른 창의 저장본이 있습니다. 이 탭의 초안은 보존되었습니다.':'이 탭의 초안을 복구했습니다. 저장 버튼을 눌러 반영하세요.',canvasConflict);
  // A copied SQLite file may have the same page ID and revision. Wait for an edit or an explicit save.
}
async function canvasMayNavigate(departing=false){
  if(canvasComposing)return false;
  if(!canvasDirty)return true;
  if(canvasDraftRestored){
    if(!departing)toast('복구한 초안을 먼저 저장해 주세요.');
    return departing;
  }
  try{
    while(canvasDirty){
      if(canvasComposing)return false;
      await saveCanvas(true);
    }
    return !canvasComposing;
  }catch(e){
    if(!departing){toast('페이지를 먼저 저장해 주세요.');return false;}
    if(!canvasDraftStored)return false;
    return window.confirm('페이지를 저장하지 못했습니다. 이 탭에 초안을 남기고 이동하시겠습니까?');
  }
}
function canvasEditState(){
  const target=document.activeElement;
  const row=target.closest('.canvas-block');
  const index=row?[...row.parentElement.children].indexOf(row):-1;
  const column=row?[...row.querySelectorAll('.canvas-table-cell')].indexOf(target):-1;
  return {title:canvasTitle,blocks:canvasBlocks.map(block=>({...block})),index,column,selection:canvasBlockSelection,
    position:target.selectionStart||0};
}
function canvasTrackEdit(target=null){
  const now=performance.now();
  if(!target||target!==canvasEditGroup?.target||now-canvasEditGroup.time>750){
    canvasUndoStack.push(canvasEditState());
    if(canvasUndoStack.length>40)canvasUndoStack.shift();
  }
  canvasRedoStack=[];
  canvasEditGroup=target?{target,time:now}:null;
  canvasUpdateHistoryButtons();
}
function canvasUpdateHistoryButtons(){
  el('canvas-undo').disabled=!canvasUndoStack.length;
  el('canvas-redo').disabled=!canvasRedoStack.length;
}
function canvasUndoEdit(redo=false){
  if(canvasComposing)return;
  const from=redo?canvasRedoStack:canvasUndoStack;
  const to=redo?canvasUndoStack:canvasRedoStack;
  if(!from.length)return;
  to.push(canvasEditState());
  const {title,blocks,index,column,position,selection}=from.pop();
  canvasTitle=title;
  el('canvas-title').value=title;
  canvasBlocks=blocks;
  canvasBlockSelection=selection;
  canvasEditGroup=null;
  canvasMarkDirty();
  canvasRenderBlocks();
  canvasUpdateHistoryButtons();
  const cell=el('canvas-blocks').children[index]?.querySelectorAll('.canvas-table-cell')[column];
  if(selection)canvasFocusSelection(selection.extent);
  else if(cell){cell.focus();cell.setSelectionRange(position,position);}
  else if(index>=0)canvasFocusBlock(index,position);
  else{el('canvas-title').focus();el('canvas-title').setSelectionRange(position,position);}
}
function canvasBindTextInput(input,apply){
  const finish=()=>{
    if(canvasComposing===input)canvasComposing=null;
    apply();
    if(canvasDirty&&!canvasDraftRestored)canvasScheduleSave();
  };
  input.addEventListener('compositionstart',()=>{
    canvasComposing=input;
    canvasClearTimer();
  });
  input.addEventListener('compositionend',finish);
  input.addEventListener('blur',()=>{if(canvasComposing===input)finish();});
  input.addEventListener('input',event=>{
    if(!event.isComposing&&canvasComposing!==input)apply();
  });
}
function canvasDepth(block){return block?.depth??0;}
function canvasSetDepth(block,depth){
  if(depth)block.depth=depth;
  else delete block.depth;
  return block;
}
function canvasSubtreeEnd(index){
  let end=index+1;
  while(end<canvasBlocks.length&&canvasDepth(canvasBlocks[end])>canvasDepth(canvasBlocks[index]))end++;
  return end;
}
function canvasParentIndex(index){
  const depth=canvasDepth(canvasBlocks[index]);
  if(depth===0)return -1;
  for(let i=index-1;i>=0;i--)if(canvasDepth(canvasBlocks[i])<depth)return i;
  return -1;
}
function canvasPreviousSibling(index){
  const depth=canvasDepth(canvasBlocks[index]);
  for(let i=index-1;i>=0;i--){
    const previous=canvasDepth(canvasBlocks[i]);
    if(previous===depth)return i;
    if(previous<depth)break;
  }
  return -1;
}
function canvasNextSibling(index){
  const end=canvasSubtreeEnd(index);
  return end<canvasBlocks.length&&canvasDepth(canvasBlocks[end])===canvasDepth(canvasBlocks[index])?end:-1;
}
function canvasNewBlock(type='paragraph',content='',checked=false,depth=0){
  return canvasSetDepth({id:crypto.randomUUID(),type,content:type==='table'?JSON.stringify(canvasDefaultTable):content,checked},depth);
}
function canvasInsertBlock(index,type='paragraph',content='',depth=0){
  if(canvasBlocks.length>=canvasMaxBlocks){
    toast('페이지당 최대 '+canvasMaxBlocks+'개 블록을 사용할 수 있습니다.');
    return null;
  }
  canvasTrackEdit();
  const block=canvasNewBlock(type,content,false,depth);
  canvasBlocks.splice(index,0,block);
  return block;
}
function canvasFocusBlock(index,position=0){
  const row=el('canvas-blocks').children[index];
  const input=row?.querySelector('.canvas-block-text, .canvas-table-cell, .canvas-page-link-target')||row?.querySelector('.block-tool-add');
  if(!input)return;
  input.focus({preventScroll:true});
  input.setSelectionRange?.(position,position);
  input.scrollIntoView({block:'nearest'});
}
function canvasVisibleSibling(index,step){
  const rows=el('canvas-blocks').children;
  for(let next=index+step;next>=0&&next<rows.length;next+=step)if(!rows[next].hidden)return next;
  return -1;
}
function canvasAddBlock(type='paragraph',index=canvasBlocks.length,depth=0){
  if(!canvasInsertBlock(index,type,'',depth))return;
  canvasBlockSelection=null;
  canvasMarkDirty();
  canvasRenderBlocks();
  canvasFocusBlock(index);
}
function canvasMoveBlock(index,step){
  const sibling=step<0?canvasPreviousSibling(index):canvasNextSibling(index);
  if(sibling<0)return;
  canvasMoveSubtree(index,step<0?sibling:canvasSubtreeEnd(sibling));
}
function canvasMoveSubtree(index,destination,depthDelta=0){
  const end=canvasSubtreeEnd(index);
  if((destination>index&&destination<end)||(!depthDelta&&(destination===index||destination===end)))return;
  canvasTrackEdit();
  const branch=canvasBlocks.splice(index,end-index);
  if(depthDelta)for(const block of branch)canvasSetDepth(block,canvasDepth(block)+depthDelta);
  const next=destination>=end?destination-branch.length:destination;
  canvasBlocks.splice(next,0,...branch);
  canvasBlockSelection=null;
  canvasMarkDirty();
  canvasRenderBlocks();
  canvasFocusBlock(next);
}
function canvasCanIndent(index){
  return canvasPreviousSibling(index)>=0&&canvasBlocks.slice(index,canvasSubtreeEnd(index)).every(block=>canvasDepth(block)<canvasMaxDepth);
}
function canvasIndentBlock(index,delta){
  if(delta>0){
    if(!canvasCanIndent(index))return;
    const previous=canvasBlocks[canvasPreviousSibling(index)];
    canvasCollapsed.delete(previous.id);
    canvasMoveSubtree(index,index,1);
  }else{
    const parent=canvasParentIndex(index);
    if(parent>=0)canvasMoveSubtree(index,canvasSubtreeEnd(parent),-1);
  }
}
function canvasRemoveBlock(index){
  const end=canvasSubtreeEnd(index);
  canvasTrackEdit();
  for(let child=index+1;child<end;child++)canvasSetDepth(canvasBlocks[child],canvasDepth(canvasBlocks[child])-1);
  canvasBlocks.splice(index,1);
  canvasBlockSelection=null;
  canvasMarkDirty();
  canvasRenderBlocks();
  if(canvasBlocks.length)canvasFocusBlock(Math.max(0,index-1));
  else el('canvas-blocks').querySelector('button').focus();
}
function canvasSelectionBounds(){
  if(!canvasBlockSelection)return null;
  const {anchor,extent}=canvasBlockSelection;
  const start=Math.min(anchor,extent);
  let end=Math.max(anchor,extent)+1;
  for(let index=start;index<end;index=canvasSubtreeEnd(index))end=Math.max(end,canvasSubtreeEnd(index));
  return [start,end];
}
function canvasRenderSelection(){
  const bounds=canvasSelectionBounds();
  [...el('canvas-blocks').children].forEach((row,index)=>{
    const selected=Boolean(bounds&&index>=bounds[0]&&index<bounds[1]);
    row.classList.toggle('canvas-block-selected',selected);
    row.querySelector('.block-tool-select')?.setAttribute('aria-pressed',String(selected));
  });
}
function canvasFocusSelection(index){
  el('canvas-blocks').children[index]?.querySelector('.block-tool-select')?.focus();
}
function canvasSelectBlock(index,extend=false){
  const anchor=extend?canvasBlockSelection?.anchor??index:index;
  canvasBlockSelection={anchor,extent:index};
  canvasRenderSelection();
  canvasFocusSelection(index);
}
function canvasRemoveSelection(){
  const bounds=canvasSelectionBounds();
  if(!bounds)return;
  const [start,end]=bounds;
  canvasTrackEdit();
  canvasBlocks.splice(start,end-start);
  canvasBlockSelection=null;
  canvasMarkDirty();
  canvasRenderBlocks();
  if(canvasBlocks.length)canvasFocusBlock(Math.min(start,canvasBlocks.length-1));
  else el('canvas-blocks').querySelector('button').focus();
}
function canvasClipboardPayload(){
  const bounds=canvasSelectionBounds();
  if(!bounds)return null;
  const blocks=canvasBlocks.slice(...bounds);
  let base=canvasDepth(blocks[0]);
  return blocks.map(block=>{
    base=Math.min(base,canvasDepth(block));
    return canvasSetDepth({type:block.type,content:block.content,checked:block.checked},canvasDepth(block)-base);
  });
}
function canvasClipboardText(block){
  const prefix={bullet:'- ',ordered_list:'1. ',todo:block.checked?'- [x] ':'- [ ] '};
  const content=block.type==='table'?canvasReadTable(block).map(row=>row.join('\t')).join('\n'):
    block.type==='page_link'?pageDocuments.find(page=>page.id===block.content)?.title||'':block.content;
  return '  '.repeat(canvasDepth(block))+(prefix[block.type]||'')+content;
}
function canvasCopyBlocks(event){
  if(canvasComposing)return;
  const blocks=canvasClipboardPayload();
  if(!blocks||!event.clipboardData)return;
  event.preventDefault();
  event.clipboardData.setData('text/plain',blocks.map(canvasClipboardText).join('\n'));
  event.clipboardData.setData(canvasClipboardType,JSON.stringify(blocks));
  if(event.type==='cut')canvasRemoveSelection();
}
function canvasValidClipboardBlock(block){
  if(!block||!canvasBlockTypes.includes(block.type)||typeof block.content!=='string'||Array.from(block.content).length>4000||
      typeof block.checked!=='boolean'||!Number.isInteger(canvasDepth(block))||canvasDepth(block)<0||canvasDepth(block)>canvasMaxDepth)return false;
  if(['table','ordered_list','page_link'].includes(block.type)&&block.checked)return false;
  if(block.type==='page_link')return !block.content||/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/.test(block.content);
  if(block.type!=='table')return true;
  try{
    const rows=canvasReadTable(block);
    return Array.isArray(rows)&&rows.length>=2&&rows.length<=20&&rows.every(row=>Array.isArray(row)&&
      row.length>=2&&row.length<=8&&row.length===rows[0].length&&row.every(cell=>typeof cell==='string'&&Array.from(cell).length<=256));
  }catch{return false;}
}
function canvasPasteBlocks(event){
  if(canvasComposing||!event.clipboardData)return;
  const bounds=canvasSelectionBounds();
  const encoded=event.clipboardData.getData(canvasClipboardType);
  if(!bounds&&!encoded)return;
  event.preventDefault();
  let blocks;
  try{blocks=encoded?JSON.parse(encoded):event.clipboardData.getData('text/plain').split(/\r\n|\r|\n/)
    .map(content=>({type:'paragraph',content,checked:false}));}
  catch{toast('복사한 블록을 읽을 수 없습니다.');return;}
  const row=event.target.closest('.canvas-block');
  const current=row?[...row.parentElement.children].indexOf(row):-1;
  const after=current<0?canvasBlocks.length:canvasSubtreeEnd(current);
  const [start,end]=bounds||[after,after];
  const base=bounds?canvasDepth(canvasBlocks[start]):canvasDepth(canvasBlocks[current]);
  if(!Array.isArray(blocks)||!blocks.length||canvasBlocks.length-end+start+blocks.length>canvasMaxBlocks||
      blocks.some((block,i)=>!canvasValidClipboardBlock(block)||base+canvasDepth(block)>canvasMaxDepth||
        canvasDepth(block)>(i?canvasDepth(blocks[i-1])+1:0))){
    toast('블록을 붙여넣을 수 없습니다. 블록 수, 길이, 들여쓰기 깊이를 확인해 주세요.');
    return;
  }
  canvasTrackEdit();
  const added=blocks.map(({type,content,checked,depth=0})=>canvasSetDepth({id:crypto.randomUUID(),type,content,checked},base+depth));
  canvasBlocks.splice(start,end-start,...added);
  canvasBlockSelection={anchor:start,extent:start+added.length-1};
  canvasMarkDirty();
  canvasRenderBlocks();
  canvasFocusSelection(start);
}
function canvasDropDestination(event,index){
  const source=canvasBlocks.findIndex(block=>block.id===canvasDraggedId);
  if(source<0||source===index||canvasParentIndex(source)!==canvasParentIndex(index))return null;
  const rect=event.currentTarget.getBoundingClientRect();
  const above=event.clientY<rect.top+rect.height/2;
  return {source,above,index:above?index:canvasSubtreeEnd(index)};
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
      canvasTrackEdit();
      block.content=JSON.stringify(rows);
    }else if(type==='page_link'){
      if(block.content){toast('페이지 링크는 빈 블록에서 추가해 주세요.');canvasRenderBlocks();canvasFocusBlock(index);return;}
      canvasTrackEdit();
    }else if(block.type==='table'){
      canvasTrackEdit();
      block.content=canvasReadTable(block).map(row=>row.join('\t')).join('\n');
    }else canvasTrackEdit();
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
  const glyph={paragraph:'T',heading_1:'H₁',heading_2:'H₂',bullet:'•',ordered_list:'1.',todo:'☑',toggle:'▸',quote:'❝',code:'{ }',divider:'─',table:'▦',page_link:'↗'};
  const aliases={paragraph:'text',heading_1:'h1 heading',heading_2:'h2 heading',bullet:'list bullet',ordered_list:'list number',todo:'task check checklist',page_link:'link page'};
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
  const commit=target=>{
    const content=JSON.stringify(rows);
    if(Array.from(content).length>4000){
      status.textContent='표가 최대 길이에 도달했습니다. 일부 셀 내용을 줄여 주세요.';
      return false;
    }
    canvasTrackEdit(target);
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
          canvasBindTextInput(input,()=>{
            const previous=rows[rowIndex][columnIndex];
            if(previous===input.value)return;
            rows[rowIndex][columnIndex]=input.value;
            if(!commit(input))input.value=rows[rowIndex][columnIndex]=previous;
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
function canvasRenderPageLink(block){
  const link=node('a',{className:'canvas-page-link'});
  const target=node('select',{className:'canvas-page-link-target','aria-label':'연결할 페이지'});
  target.append(node('option',{value:''},'연결할 페이지 선택'));
  const update=()=>{
    const page=pageDocuments.find(item=>item.id===block.content);
    link.textContent=page?.title||'연결된 페이지';
    link.classList.toggle('hidden',!block.content);
    if(block.content)link.href='#page='+encodeURIComponent(block.content);
    else link.removeAttribute('href');
  };
  for(const page of pageDocuments)target.append(node('option',{value:page.id},page.title));
  if(block.content&&!pageDocuments.some(page=>page.id===block.content)){
    target.append(node('option',{value:block.content},'연결된 페이지'));
  }
  target.value=block.content;
  target.addEventListener('change',()=>{
    canvasTrackEdit();
    block.content=target.value;
    canvasMarkDirty();
    update();
  });
  update();
  const wrapper=node('div',{className:'canvas-page-link-controls'});
  wrapper.append(link,target);
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
  const resize=[];
  const listNumbers=[];
  let foldedDepth=null;
  canvasBlocks.forEach((block,index)=>{
    const depth=canvasDepth(block);
    const hasChildren=canvasSubtreeEnd(index)>index+1;
    if(foldedDepth!==null&&depth<=foldedDepth)foldedDepth=null;
    listNumbers.length=depth+1;
    listNumbers[depth]=block.type==='ordered_list'?(listNumbers[depth]||0)+1:0;
    const row=node('div',{className:'canvas-block block-'+block.type,'data-block-id':block.id,'data-block-depth':depth});
    row.style.setProperty('--block-depth-offset',depth*18+'px');
    row.hidden=foldedDepth!==null;
    if(!row.hidden&&hasChildren&&block.type==='toggle'&&canvasCollapsed.has(block.id))foldedDepth=depth;
    row.addEventListener('dragover',event=>{
      const drop=canvasDropDestination(event,index);
      if(!drop)return;
      event.preventDefault();
      event.dataTransfer.dropEffect='move';
      row.dataset.dropPosition=drop.above?'before':'after';
    });
    row.addEventListener('dragleave',event=>{if(!row.contains(event.relatedTarget))delete row.dataset.dropPosition;});
    row.addEventListener('drop',event=>{
      delete row.dataset.dropPosition;
      const drop=canvasDropDestination(event,index);
      if(!drop)return;
      event.preventDefault();
      canvasDraggedId=null;
      canvasMoveSubtree(drop.source,drop.index);
    });
    const tools=node('div',{className:'block-tools'});
    const add=node('button',{type:'button',className:'block-tool-button block-tool-add','aria-label':'아래 블록 추가',title:'아래 블록 추가'},'+');
    add.addEventListener('click',()=>canvasAddBlock('paragraph',canvasSubtreeEnd(index),depth));
    const select=node('button',{type:'button',className:'block-tool-button block-tool-select',draggable:'true',
      'aria-label':'블록 선택 또는 끌어서 이동',title:'블록 선택 · Shift로 범위 선택 · 끌어서 이동','aria-pressed':'false'},'⠿');
    select.addEventListener('click',event=>canvasSelectBlock(index,event.shiftKey));
    select.addEventListener('dragstart',event=>{
      canvasDraggedId=block.id;
      event.dataTransfer.effectAllowed='move';
      event.dataTransfer.setData('application/x-my-workspace-block-move',block.id);
    });
    select.addEventListener('dragend',()=>{
      canvasDraggedId=null;
      root.querySelectorAll('[data-drop-position]').forEach(target=>delete target.dataset.dropPosition);
    });
    tools.append(add,select);
    const more=node('button',{type:'button',className:'block-tool-button block-tool-menu','aria-label':'블록 도구','aria-expanded':'false'},'⋮⋮');
    more.addEventListener('click',()=>more.setAttribute('aria-expanded',String(row.classList.toggle('tools-open'))));
    tools.append(more);
    const options=node('div',{className:'block-tool-options'});
    const chooser=node('select',{className:'block-type','aria-label':'블록 유형'});
    canvasBlockTypes.forEach(type=>chooser.append(node('option',{value:type},canvasTypeLabels[type])));
    chooser.value=block.type;
    chooser.addEventListener('change',()=>canvasChangeBlockType(block,index,chooser.value));
    options.append(chooser);
    for(const [icon,label,action,disabled] of [
      ['↑','블록 위로 이동',()=>canvasMoveBlock(index,-1),canvasPreviousSibling(index)<0],
      ['↓','블록 아래로 이동',()=>canvasMoveBlock(index,1),canvasNextSibling(index)<0],
      ['←','블록 내어쓰기',()=>canvasIndentBlock(index,-1),depth===0],
      ['→','블록 들여쓰기',()=>canvasIndentBlock(index,1),!canvasCanIndent(index)],
      ['×','블록 삭제',()=>canvasRemoveBlock(index),false]
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
    else if(block.type==='page_link')content.append(canvasRenderPageLink(block));
    else{
      const input=node('textarea',{className:'canvas-block-text','aria-label':canvasTypeLabels[block.type],rows:block.type==='code'?4:1,maxlength:'4000',placeholder:block.type==='paragraph'?'텍스트를 입력하거나 /를 눌러 블록을 추가하세요':''});
      input.value=block.content;
      const fit=()=>{
        input.style.height='auto';
        input.style.height=Math.min(400,Math.max(31,input.scrollHeight+2))+'px';
      };
      canvasBindTextInput(input,()=>{
        if(block.content===input.value)return;
        canvasTrackEdit(input);
        block.content=input.value;
        canvasMarkDirty();
        fit();
      });
      if(block.type==='todo'){
        const checkbox=node('input',{type:'checkbox','aria-label':'체크리스트 완료'});
        checkbox.checked=block.checked;
        row.classList.toggle('checked',block.checked);
        checkbox.addEventListener('change',()=>{
          canvasTrackEdit();
          block.checked=checkbox.checked;
          row.classList.toggle('checked',checkbox.checked);
          canvasMarkDirty();
        });
        content.append(checkbox);
      }
      if(block.type==='bullet')content.append(node('span',{className:'block-prefix','aria-hidden':'true'},'•'));
      if(block.type==='ordered_list')content.append(node('span',{className:'block-prefix','aria-hidden':'true'},listNumbers[depth]+'.'));
      if(block.type==='quote')content.append(node('span',{className:'block-prefix','aria-hidden':'true'},'│'));
      if(block.type==='toggle'){
        const collapsed=hasChildren&&canvasCollapsed.has(block.id);
        const toggle=node('button',{type:'button',className:'toggle-caret','aria-label':'내용 접기 또는 펼치기','aria-expanded':String(!collapsed)},collapsed?'▸':'▾');
        toggle.addEventListener('click',()=>{
          if(hasChildren){
            if(canvasCollapsed.has(block.id))canvasCollapsed.delete(block.id);
            else canvasCollapsed.add(block.id);
            canvasBlockSelection=null;
            canvasRenderBlocks();
            root.children[index].querySelector('.toggle-caret').focus();
            return;
          }
          const collapsed=input.classList.toggle('hidden');
          toggle.textContent=collapsed?'▸':'▾';
          toggle.setAttribute('aria-expanded',String(!collapsed));
        });
        content.append(toggle);
      }
      input.addEventListener('keydown',event=>{
        if(event.isComposing||event.keyCode===229||canvasComposing)return;
        if(event.key==='/'&&input.value===''&&block.type==='paragraph'){
          event.preventDefault();
          canvasSlashMenu(row,block,index,input);
        }else if(event.key==='Enter'&&!event.shiftKey&&block.type!=='code'&&block.type!=='toggle'){
          event.preventDefault();
          const nextType=['bullet','ordered_list','todo'].includes(block.type)&&input.value.trim()?block.type:'paragraph';
          const next=canvasSubtreeEnd(index);
          if(!canvasInsertBlock(next,nextType,input.value.slice(input.selectionEnd),depth))return;
          block.content=input.value.slice(0,input.selectionStart);
          canvasMarkDirty();
          canvasRenderBlocks();
          canvasFocusBlock(next);
        }else if(event.key==='Backspace'&&input.value===''&&index>0){
          event.preventDefault();
          canvasRemoveBlock(index);
        }else if(!event.altKey&&!event.shiftKey&&!event.ctrlKey&&!event.metaKey&&(
            (event.key==='ArrowUp'&&input.selectionStart===0&&input.selectionEnd===0&&index>0)||
            (event.key==='ArrowDown'&&input.selectionStart===input.value.length&&input.selectionEnd===input.value.length&&index<canvasBlocks.length-1))){
          event.preventDefault();
          const previous=event.key==='ArrowUp';
          const target=canvasVisibleSibling(index,previous?-1:1);
          if(target>=0)canvasFocusBlock(target,previous?canvasBlocks[target].content.length:0);
        }
      });
      content.append(input);
      resize.push(input);
    }
    row.append(content);
    root.append(row);
  });
  canvasRenderSelection();
  requestAnimationFrame(()=>{
    const heights=resize.map(input=>input.scrollHeight);
    resize.forEach((input,index)=>{if(heights[index])input.style.height=Math.min(400,Math.max(31,heights[index]+2))+'px';});
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
  canvasTitle=page.title;
  canvasComposing=null;
  canvasBlockSelection=null;
  canvasDraggedId=null;
  canvasUndoStack=[];
  canvasRedoStack=[];
  canvasEditGroup=null;
  canvasUpdateHistoryButtons();
  canvasRestoreDraft(page);
  el('canvas-empty').classList.add('hidden');
  el('canvas-editing').classList.remove('hidden');
  el('canvas-head-actions').classList.remove('hidden');
  el('canvas-title').value=canvasTitle;
  canvasPageMeta(page);
  canvasPageMasthead(page);
  canvasBreadcrumb(page,docs);
  canvasTemplateSummary(page);
  canvasRenderBlocks();
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
  if(requestedId&&!docs.some(doc=>doc.id===requestedId)){
    canvasPageId=null;
    canvasSidebarTree(docs);
    canvasShowEmpty();
    throw Error('페이지를 열 수 없습니다. 휴지통이나 페이지 목록을 확인해 주세요.');
  }
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
      canvasTrackEdit();
      canvasBlocks=[
        canvasNewBlock('heading_1','나의 Workspace'),
        canvasNewBlock('paragraph','이 페이지는 나만의 작업 공간입니다. 텍스트 블록을 추가하거나 아래 항목을 수정해 보세요.'),
        canvasNewBlock('todo','첫 문서 작성하기'),
        canvasNewBlock('todo','하위 페이지 만들기'),
        canvasNewBlock('toggle','템플릿 라이브러리에서 새 페이지 만들기')
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
async function canvasWriteSnapshot(page,snapshot,silent){
  const path='/api/v1/pages/'+page.id+'/content';
  const put=revision=>api(path,{method:'PUT',headers:requestHeaders,
    body:JSON.stringify({...snapshot,expected_revision:revision})});
  if(!canvasConflict){
    try{return await put(page.revision);}
    catch(error){if(error.status!==409)throw error;}
  }
  const latest=await api(path);
  if(canvasSameContent(snapshot.title,snapshot.blocks,latest))return latest;
  if(!canvasConflict&&canvasSameContent(page.title,page.blocks,latest))return put(latest.revision);
  if(silent||!window.confirm('다른 창에서 저장한 변경사항이 있습니다. 현재 초안으로 저장본을 교체하시겠습니까?')){
    const error=Error('다른 창에서 변경된 페이지입니다.');
    error.status=409;
    throw error;
  }
  return put(latest.revision);
}
async function saveCanvas(silent=false){
  while(canvasSavePromise)await canvasSavePromise;
  if(!canvasPage||!canvasDirty||canvasComposing)return;
  if(silent&&canvasDraftRestored)throw Error('복구한 초안을 먼저 저장해 주세요.');
  canvasClearTimer();
  const page=canvasPage;
  const title=canvasTitle.trim();
  const snapshot={title,blocks:canvasBlocks.map(block=>({...block}))};
  canvasStatus('저장 중…');
  const request=(async()=>{
    if(!title)throw Error('페이지 제목을 입력해 주세요.');
    if(snapshot.blocks.reduce((total,block)=>total+Array.from(block.content).length,0)>45000){
      throw Error('한 페이지에 최대 45,000자를 저장할 수 있습니다.');
    }
    return canvasWriteSnapshot(page,snapshot,silent);
  })();
  canvasSavePromise=request.then(updated=>{
    if(canvasPage?.id!==page.id)return;
    if(canvasPage.properties.revision>updated.properties.revision)updated.properties=canvasPage.properties;
    canvasPage=updated;
    canvasConflict=false;
    canvasDraftBase=null;
    canvasDraftRestored=false;
    if(canvasSameContent(canvasTitle.trim(),canvasBlocks,snapshot))canvasResetDirty();
    else{
      canvasPersistDraft();
      canvasStatus('새 변경사항 저장 대기 중');
      canvasScheduleSave();
    }
    canvasPageMeta(updated);
    canvasUpdateTree(updated,pageDocuments);
    if(!silent)toast('페이지를 저장했습니다.');
  }).catch(error=>{
    canvasClearTimer();
    canvasConflict=canvasConflict||error.status===409;
    const recovery=canvasDraftStored?' 이 탭에 초안이 보존되었습니다.':' 페이지를 닫기 전에 다시 시도해 주세요.';
    canvasStatus((canvasConflict?'다른 창의 저장본이 있습니다.':'저장 실패 · '+error.message)+recovery,true);
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
  const listNumbers=[];
  for(const block of snapshot.blocks){
    const depth=canvasDepth(block);
    listNumbers.length=depth+1;
    listNumbers[depth]=block.type==='ordered_list'?(listNumbers[depth]||0)+1:0;
    let item;
    if(block.type==='divider')item=node('hr');
    else if(block.type==='table')item=canvasRenderTable(block,true);
    else if(block.type==='page_link')item=node('p',{className:'canvas-history-text'},
      pageDocuments.find(page=>page.id===block.content)?.title||'페이지 링크');
    else{
      const tag={heading_1:'h4',heading_2:'h5',code:'pre',quote:'blockquote'}[block.type]||'p';
      const prefix={todo:block.checked?'☑ ':'☐ ',bullet:'• ',ordered_list:listNumbers[depth]+'. '}[block.type]||'';
      item=node(tag,{className:'canvas-history-text'},prefix+block.content);
    }
    if(depth)item.style.marginInlineStart=depth*12+'px';
    preview.append(item);
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
  const undo=node('button',{id:'canvas-undo',type:'button',className:'secondary-button','aria-label':'실행 취소',title:'실행 취소 (Ctrl+Z)'},'↶');
  const redo=node('button',{id:'canvas-redo',type:'button',className:'secondary-button','aria-label':'다시 실행',title:'다시 실행 (Ctrl+Shift+Z)'},'↷');
  undo.addEventListener('click',()=>canvasUndoEdit());
  redo.addEventListener('click',()=>canvasUndoEdit(true));
  el('canvas-save').before(undo,redo);
  canvasUpdateHistoryButtons();
  const typeSelect=el('canvas-new-type');
  typeSelect.replaceChildren(...canvasBlockTypes.map(type=>node('option',{value:type},canvasTypeLabels[type])));
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
const canvasTitleInput=el('canvas-title');
canvasBindTextInput(canvasTitleInput,()=>{
  if(canvasTitle===canvasTitleInput.value)return;
  canvasTrackEdit(canvasTitleInput);
  canvasTitle=canvasTitleInput.value;
  canvasMarkDirty();
});
const canvasBlockRoot=el('canvas-blocks');
canvasBlockRoot.addEventListener('copy',canvasCopyBlocks);
canvasBlockRoot.addEventListener('cut',canvasCopyBlocks);
canvasBlockRoot.addEventListener('paste',canvasPasteBlocks);
canvasBlockRoot.addEventListener('focusin',event=>{
  if(canvasBlockSelection&&!event.target.closest('.block-tool-select')){
    canvasBlockSelection=null;
    canvasRenderSelection();
  }
});
canvasBlockRoot.addEventListener('keydown',event=>{
  if(event.isComposing||event.keyCode===229||canvasComposing)return;
  const row=event.target.closest('.canvas-block');
  if(!row)return;
  const index=[...canvasBlockRoot.children].indexOf(row);
  const {key}=event;
  if(event.altKey&&['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(key)){
    event.preventDefault();
    event.stopPropagation();
    if(key==='ArrowUp'||key==='ArrowDown')canvasMoveBlock(index,key==='ArrowUp'?-1:1);
    else canvasIndentBlock(index,key==='ArrowLeft'?-1:1);
  }else if(event.target.closest('.block-tool-select')){
    if(event.shiftKey&&(key==='ArrowUp'||key==='ArrowDown')){
      event.preventDefault();
      if(!canvasBlockSelection)canvasBlockSelection={anchor:index,extent:index};
      const next=canvasVisibleSibling(index,key==='ArrowUp'?-1:1);
      if(next>=0)canvasSelectBlock(next,true);
    }else if(canvasBlockSelection&&(key==='Delete'||key==='Backspace')){
      event.preventDefault();
      canvasRemoveSelection();
    }else if(canvasBlockSelection&&key==='Escape'){
      canvasBlockSelection=null;
      canvasRenderSelection();
    }
  }
},true);
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
  if(currentView==='canvas'&&(canvasDirty||canvasComposing)){
    event.preventDefault();
    event.returnValue='';
  }
});
document.addEventListener('keydown',event=>{
  if(event.isComposing||event.keyCode===229||canvasComposing||!(event.ctrlKey||event.metaKey)||currentView!=='canvas')return;
  const key=event.key.toLowerCase();
  if(key==='s'){
    event.preventDefault();
    saveCanvas().catch(error=>toast(error.message));
  }else if((key==='z'||key==='y')&&event.target.closest('#canvas-blocks, #canvas-title, #canvas-head-actions')){
    event.preventDefault();
    canvasUndoEdit(key==='y'||event.shiftKey);
  }
});

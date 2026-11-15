'use strict';
const el=id=>document.getElementById(id);
let catalog=[],selectedTemplate=null,editingDocument=null,currentView='start',discoveryMode='all',discoveryLimit=24;
let navigationVersion=0,creatingTemplate=false;
const templateRequestIds=new Map();
const requestHeaders={'Content-Type':'application/json','X-EAW-Request':'local-template-editor'};
async function api(path,options={}){
  const response=await fetch(path,{cache:'no-store',credentials:'same-origin',...options});
  let data;try{data=await response.json()}catch{throw Error('서버 응답을 해석할 수 없습니다.');}
  if(!response.ok){
    const error=Error(typeof data.detail==='string'?data.detail:'요청 내용을 확인해 주세요.');
    error.status=response.status;
    throw error;
  }
  return data;
}
function node(tag,props={},text){const n=document.createElement(tag);for(const [k,v] of Object.entries(props)){if(k==='className')n.className=v;else if(k==='type')n.type=v;else n.setAttribute(k,v);}if(text!==undefined)n.textContent=String(text);return n;}
function toast(message){const t=el('toast');t.textContent=message;t.classList.remove('hidden');}
function clearToast(){el('toast').classList.add('hidden');}
async function selectView(view,{pageId,createdPage,parentId=null}={}){
  const views=['canvas','home','start','library','documents','pages','database','projects','calendar'];
  if(!views.includes(view))return false;
  if(view==='canvas'&&currentView==='canvas'&&canvasPage&&(!pageId||pageId===canvasPageId)){
    closeEditor();
    return true;
  }
  const navigation=++navigationVersion;
  if(currentView==='canvas'&&!await canvasMayNavigate())return false;
  if(navigation!==navigationVersion)return false;
  if(view==='canvas'&&pageId)canvasPageId=pageId;
  pendingParentId=view==='library'?parentId:null;
  currentView=view;
  renderWorkspaceTabs();
  const viewNames={canvas:'내 페이지',home:'홈',start:'시작하기',library:'템플릿 라이브러리',documents:'모든 문서',pages:'페이지 구조 관리',database:'업무 데이터베이스',projects:'프로젝트',calendar:'캘린더'};
  if(el('topbar-section'))el('topbar-section').textContent=viewNames[view]||'My AI Workspace';
  for(const v of views){el('nav-'+v).classList.toggle('active',v===view);el(v+'-panel').classList.toggle('hidden',v!==view);}
  closeEditor();
  el('layout').classList.toggle('canvas-mode',view==='canvas');
  clearToast();
  window.scrollTo(0,0);
  if(view==='library')renderTemplateTarget();
  const loader={canvas:loadCanvas,home:loadDashboard,documents:loadDocuments,pages:loadPages,database:loadTasks,projects:loadProjects,calendar:loadCalendar}[view];
  if(loader){
    try{
      await (view==='canvas'?loader(createdPage):loader());
    }catch(e){
      if(navigation===navigationVersion)toast(e.message);
      return false;
    }
  }
  return navigation===navigationVersion;
}
function uniqueValues(key,items){return [...new Set(items.map(t=>t[key]))].sort((a,b)=>a.localeCompare(b,'ko'));}
function fillSelect(id,items,label,keep){const select=el(id);const prev=keep?select.value:'';select.replaceChildren(node('option',{value:''},label));for(const name of items)select.append(node('option',{value:name},name));select.value=items.includes(prev)?prev:'';}
function filtersChanged(changed){discoveryLimit=24;const section=el('section-filter').value;const department=el('department-filter').value;const families=catalog.filter(t=>(!section||t.section===section)&&(!department||t.department===department));fillSelect('family-filter',uniqueValues('job_family',families),'전체 직무군',!['section','department'].includes(changed));const family=el('family-filter').value;const roles=families.filter(t=>!family||t.job_family===family);fillSelect('role-filter',uniqueValues('job_role',roles),'전체 직무',changed==='role');renderTemplates();}
const templatePageSize=24;
const templateSavedKey='my-ai-workspace.template-favorites.v1';
const templateFeaturedOrder=['library-project-dependency-map','library-term-dashboard','library-weekly-intention',
  'library-wiki-index-design','library-reading-synthesis','library-trip-day-plan'];
const templateTabTitles={all:'전체 템플릿',recommended:'추천 템플릿',popular_category:'인기 주제 템플릿',saved:'즐겨찾기'};
const templateFavorites=readTemplateFavorites();
let activeCollection='',previewedTemplate=null,previewVersion=0;

function readTemplateFavorites(){
  try{
    const ids=JSON.parse(localStorage.getItem(templateSavedKey)||'[]');
    return new Set(Array.isArray(ids)?ids.filter(id=>typeof id==='string'):[]);
  }catch{return new Set();}
}
function templateCollection(template){return template.collection||template.section;}
function templateDiscoveryMatches(template){
  if(discoveryMode==='saved')return templateFavorites.has(template.id);
  if(discoveryMode==='recommended')return template.discovery==='recommended'||['research-experiment','general-meeting'].includes(template.id);
  return discoveryMode==='all'||template.discovery===discoveryMode;
}
function updateTemplateFavoriteCount(){
  const count=catalog.filter(template=>templateFavorites.has(template.id)).length;
  el('template-saved-count').textContent=String(count);
}
function updateTemplateFavoriteButton(button,template){
  const selected=templateFavorites.has(template.id);
  button.textContent=selected?'★':'☆';
  button.setAttribute('aria-pressed',String(selected));
  button.setAttribute('aria-label',template.name+(selected?' 즐겨찾기 해제':' 즐겨찾기 추가'));
  button.title=selected?'즐겨찾기 해제':'즐겨찾기 추가';
}
function toggleTemplateFavorite(button,template){
  const remove=templateFavorites.has(template.id);
  if(remove)templateFavorites.delete(template.id);
  else templateFavorites.add(template.id);
  try{
    localStorage.setItem(templateSavedKey,JSON.stringify([...templateFavorites]));
  }catch{
    toast('즐겨찾기를 이 브라우저에 저장할 수 없습니다.');
  }
  updateTemplateFavoriteCount();
  if(discoveryMode==='saved'&&remove){
    renderTemplates();
    (el('template-grid').querySelector('.template-save-button')||document.querySelector('[data-discovery="saved"]')).focus();
  }else updateTemplateFavoriteButton(button,template);
}
function renderTemplateCollections(items){
  const groups=new Map();
  for(const template of items){
    const name=templateCollection(template);
    groups.set(name,(groups.get(name)||0)+1);
  }
  const wrap=el('template-collections');
  const focusedCollection=document.activeElement?.dataset?.collection;
  wrap.replaceChildren();
  if(activeCollection&&!groups.has(activeCollection))groups.set(activeCollection,0);
  const entries=[['',items.length],...[...groups].sort(([a],[b])=>a.localeCompare(b,'ko'))];
  if(!items.length&&!activeCollection)return;
  for(const [name,count] of entries){
    const active=name===activeCollection;
    const filter=node('button',{type:'button',className:'collection-filter','aria-pressed':String(active),'data-collection':name});
    filter.append(node('span',{},name||'모든 주제'),node('small',{'aria-hidden':'true'},count));
    filter.addEventListener('click',()=>{
      activeCollection=name;
      discoveryLimit=templatePageSize;
      renderTemplates();
    });
    wrap.append(filter);
    if(focusedCollection===name)filter.focus({preventScroll:true});
  }
}
function templateArtwork(template){
  const art=node('span',{className:'template-art','aria-hidden':'true'});
  const colorKey=Array.from(templateCollection(template)).reduce((total,char)=>total+char.codePointAt(0),0);
  art.classList.add('template-tone-'+(colorKey%6));
  const structuralText=[template.name,template.job_family,...(template.tags||[])].join(' ').toLowerCase();
  const style=/check|준비|습관/.test(structuralText)?'check':
    /plan|tracker|관리|예산|일정|기록|의존성|상황판/.test(structuralText)?'table':'notes';
  const sheet=node('span',{className:'template-mini-sheet template-mini-'+style});
  sheet.append(
    node('span',{className:'template-mini-icon'},style==='table'?'▦':style==='check'?'✓':'▤'),
    node('strong',{},template.name)
  );
  const diagram=node('span',{className:'template-mini-content'});
  for(const field of template.fields.slice(0,3)){
    const row=node('span',{className:'template-mini-row'});
    row.append(node('span',{},field.label),node('i'));
    diagram.append(row);
  }
  sheet.append(diagram);
  art.append(sheet);
  return art;
}
function templateCard(template){
  const card=node('article',{className:'template-card-shell'});
  const open=node('button',{className:'template-card',type:'button','data-template-id':template.id,'aria-label':template.name+' 페이지 만들기'});
  open.disabled=creatingTemplate;
  const context=node('span',{className:'template-context'},templateCollection(template));
  if(template.discovery){
    const label=template.discovery==='recommended'?'추천':'인기 주제';
    context.append(node('span',{className:'template-context-label'},label));
  }
  const copy=node('span',{className:'template-card-copy'});
  copy.append(context,node('span',{className:'template-card-title'},template.name),node('span',{className:'template-card-description'},template.description));
  open.append(templateArtwork(template),copy);
  open.addEventListener('click',()=>createPageFromTemplate(template));

  const preview=node('button',{type:'button',className:'template-preview-button','aria-label':template.name+' 미리보기'},'미리보기');
  const save=node('button',{type:'button',className:'template-save-button'});
  preview.disabled=save.disabled=creatingTemplate;
  preview.addEventListener('click',()=>openTemplatePreview(template));
  updateTemplateFavoriteButton(save,template);
  save.addEventListener('click',()=>toggleTemplateFavorite(save,template));
  const tools=node('div',{className:'template-card-actions'});
  const tags=(template.tags||[]).slice(0,2);
  tools.append(node('span',{className:'template-card-keywords'},tags.length?tags.join(' · '):template.section),preview,save);
  card.append(open,tools);
  return card;
}
function renderTemplates(){
  const grid=el('template-grid');
  grid.replaceChildren();
  const dept=el('department-filter').value,fam=el('family-filter').value,role=el('role-filter').value;
  const section=el('section-filter').value;
  const words=el('template-search').value.normalize('NFKC').trim().toLocaleLowerCase('ko-KR').split(/\s+/).filter(Boolean);
  const matching=catalog.filter(template=>{
    if(!templateDiscoveryMatches(template)||
       (section&&template.section!==section)||(dept&&template.department!==dept)||
       (fam&&template.job_family!==fam)||(role&&template.job_role!==role))return false;
    if(!words.length)return true;
    const searchValues=[template.name,template.description,template.department,template.job_family,template.job_role,
      templateCollection(template),...(template.tags||[])].join(' ').normalize('NFKC').toLocaleLowerCase('ko-KR');
    return words.every(word=>searchValues.includes(word));
  });
  if(!words.length&&!activeCollection&&(discoveryMode==='all'||discoveryMode==='recommended')){
    const priority=new Map(templateFeaturedOrder.map((id,index)=>[id,index]));
    matching.sort((left,right)=>(priority.get(left.id)??priority.size)-(priority.get(right.id)??priority.size));
  }
  renderTemplateCollections(matching);
  const items=activeCollection?matching.filter(template=>templateCollection(template)===activeCollection):matching;
  el('library-results-title').textContent=activeCollection||templateTabTitles[discoveryMode];
  el('result-count').textContent=items.length+' / '+catalog.length+'개 템플릿';
  updateTemplateFavoriteCount();
  const visible=items.slice(0,discoveryLimit);
  el('template-more').classList.toggle('hidden',visible.length>=items.length);
  el('template-progress').textContent=visible.length&&visible.length<items.length?visible.length+'개 표시':'';
  if(!items.length){
    const empty=discoveryMode==='saved'&&!templateFavorites.size
      ?'템플릿 카드의 별표를 눌러 즐겨찾기에 추가하세요.':'조건에 맞는 템플릿이 없습니다.';
    grid.append(node('p',{className:'library-empty'},empty));
    return;
  }
  grid.append(...visible.map(templateCard));
}
function templatePreviewBlock(block){
  if(block.type==='divider')return node('hr');
  if(block.type==='table'){
    const rows=Array.isArray(block.content)?block.content:JSON.parse(block.content);
    const wrapper=node('div',{className:'template-preview-table'});
    const table=node('table');
    const head=node('thead'),body=node('tbody');
    rows.forEach((cells,index)=>{
      const row=node('tr');
      for(const cell of cells)row.append(node(index?'td':'th',index?{}:{scope:'col'},cell));
      (index?body:head).append(row);
    });
    table.append(head,body);wrapper.append(table);
    return wrapper;
  }
  const headings={heading_1:'h3',heading_2:'h4'};
  if(headings[block.type])return node(headings[block.type],{},block.content);
  if(block.type==='todo'||block.type==='bullet'){
    const line=node('p',{className:'template-preview-list'});
    line.append(node('span',{'aria-hidden':'true'},block.type==='todo'?'□':'•'),node('span',{},block.content));
    return line;
  }
  if(block.type==='toggle'){
    const details=node('details');
    details.append(node('summary',{},'상세 내용'),node('p',{},block.content));
    return details;
  }
  return node(block.type==='code'?'pre':block.type==='quote'?'blockquote':'p',{},block.content);
}
async function openTemplatePreview(template){
  const dialog=el('template-preview-dialog');
  const preview=el('template-preview-content');
  const version=++previewVersion;
  previewedTemplate=template;
  el('template-preview-title').textContent=template.name;
  el('template-preview-meta').textContent=[template.section,templateCollection(template),template.job_role]
    .filter((part,index,parts)=>parts.indexOf(part)===index).join(' · ');
  el('template-preview-description').textContent=template.description;
  preview.replaceChildren(node('p',{role:'status'},'페이지 구성 불러오는 중…'));
  preview.setAttribute('aria-busy','true');
  if(!dialog.open)dialog.showModal();
  try{
    const data=await api('/api/v1/templates/'+encodeURIComponent(template.id)+'/preview');
    if(version!==previewVersion||!dialog.open)return;
    preview.replaceChildren(...data.blocks.map(templatePreviewBlock));
    preview.scrollTop=0;
  }catch(error){
    if(version===previewVersion&&dialog.open)preview.replaceChildren(node('p',{role:'status'},'미리보기를 열 수 없습니다. '+error.message));
  }finally{
    if(version===previewVersion)preview.setAttribute('aria-busy','false');
  }
}
el('template-preview-close').addEventListener('click',()=>el('template-preview-dialog').close());
el('template-preview-create').addEventListener('click',()=>{
  const template=previewedTemplate;
  if(!template)return;
  el('template-preview-dialog').close();
  createPageFromTemplate(template);
});
function renderTemplateTarget(){
  const target=el('template-target');
  target.classList.toggle('hidden',!pendingParentId);
  el('template-target-name').textContent=pageDocuments.find(page=>page.id===pendingParentId)?.title||'선택한 상위 페이지';
}
el('template-target-reset').addEventListener('click',()=>{pendingParentId=null;renderTemplateTarget();});
async function createPageFromTemplate(template){
  if(creatingTemplate||currentView!=='library')return;
  const parentId=pendingParentId;
  const navigation=navigationVersion;
  const key=JSON.stringify([template.id,parentId]);
  const requestId=templateRequestIds.get(key)||crypto.randomUUID();
  templateRequestIds.set(key,requestId);
  creatingTemplate=true;
  for(const card of el('template-grid').querySelectorAll('button'))card.disabled=true;
  el('template-grid').setAttribute('aria-busy','true');
  el('template-create-status').textContent=template.name+' 페이지 만드는 중…';
  clearToast();
  try{
    const page=await api('/api/v1/pages/from-template',{method:'POST',headers:requestHeaders,
      body:JSON.stringify({template_id:template.id,parent_id:parentId,request_id:requestId})});
    templateRequestIds.delete(key);
    if(navigation===navigationVersion){
      const opened=await openCanvas(page.id,page);
      if(opened)el('canvas-title').focus({preventScroll:true});
    }else{
      canvasMergePageIntoTree(page);
      toast('페이지를 만든 위치는 사이드바에서 확인할 수 있습니다.');
    }
    loadDocuments().catch(()=>{});
  }catch(e){
    if(e.status>=400&&e.status<500)templateRequestIds.delete(key);
    toast('페이지 생성 실패. 다시 시도해 주세요. '+e.message);
  }finally{
    creatingTemplate=false;
    el('template-grid').setAttribute('aria-busy','false');
    el('template-create-status').textContent='';
    for(const card of el('template-grid').querySelectorAll('button'))card.disabled=false;
  }
}
function openEditor(template,doc){
  selectedTemplate=template;
  editingDocument=doc;
  el('editor-panel').classList.remove('hidden');
  el('template-path').textContent=template.department+' / '+template.job_family+' / '+template.job_role;
  el('editor-description').textContent=template.name+' — '+template.description;
  el('doc-title').value=doc.title;
  const fields=el('editor-fields');
  fields.replaceChildren();
  for(const field of template.fields){
    const label=node('label',{className:'field'});
    label.append(document.createTextNode(field.label+(field.required?' *':'')));
    const attributes={id:'field-'+field.id,placeholder:field.placeholder||'',maxlength:'8192'};
    let control;
    if(field.type==='multiline')control=node('textarea',{...attributes,rows:'4'});
    else if(field.type==='select'){
      control=node('select',{id:attributes.id});
      control.append(node('option',{value:''},'선택하지 않음'));
      for(const choice of field.options)control.append(node('option',{value:choice},choice));
    }else control=node('input',{...attributes,type:field.type==='date'?'date':'text'});
    control.value=doc.values?.[field.id]||'';
    control.required=field.required;
    label.append(control);
    fields.append(label);
  }
  el('editor-panel').scrollIntoView({block:'start',behavior:'smooth'});
}
let documentSearchVersion=0;
let documentSearchTimer;
let documentTag='';
function showDocumentsWithTag(tag){
  documentTag=tag;
  el('doc-search').value='';
  return selectView('documents');
}
async function loadDocuments(){
  const version=++documentSearchVersion;
  const query=el('doc-search').value.trim();
  const tag=documentTag;
  const params=new URLSearchParams({q:query,tag});
  const [result, facets]=await Promise.all([
    api(query||tag?'/api/v1/search/pages?'+params:'/api/v1/documents'),
    currentView==='documents'?api('/api/v1/page-tags'):Promise.resolve(null)
  ]);
  if(version!==documentSearchVersion||query!==el('doc-search').value.trim()||tag!==documentTag)return;
  const {items}=result;
  if(facets){
    const select=el('doc-tag-filter');
    select.replaceChildren(node('option',{value:''},'모든 태그'));
    for(const entry of facets.items)select.append(node('option',{value:entry.label},entry.label+' ('+entry.count+')'));
    const key=value=>value.normalize('NFKC').toLocaleLowerCase('ko-KR');
    const match=facets.items.find(entry=>key(entry.label)===key(tag));
    if(tag&&!match)select.append(node('option',{value:tag},tag));
    select.value=match?.label||tag;
  }
  if(!query&&!tag)el('doc-count').textContent=String(items.length);
  const list=el('document-list');
  list.replaceChildren();
  if(!items.length){
    list.append(node('div',{className:'empty'},query||tag?'검색어와 일치하는 문서가 없습니다.':'아직 저장된 문서가 없습니다.'));
    return;
  }
  for(const doc of items){
    const template=catalog.find(item=>item.id===doc.template_id);
    const button=node('button',{className:'doc-row',type:'button'});
    button.dataset.tabColor=doc.tab_color||'none';
    const details=node('span');
    details.append(node('strong',{},doc.title),node('small',{},(template?.name||'개인 페이지')+' · Revision '+doc.revision));
    button.append(details,node('small',{},new Date(doc.updated_at).toLocaleString('ko-KR')));
    button.addEventListener('click',()=>openCanvas(doc.id).catch(error=>toast(error.message)));
    list.append(button);
  }
}
el('doc-tag-filter').addEventListener('change',event=>{
  documentTag=event.target.value;
  loadDocuments().catch(error=>toast(error.message));
});
el('nav-start').addEventListener('click',()=>selectView('start'));el('start-browse').addEventListener('click',()=>selectView('library'));el('nav-library').addEventListener('click',()=>selectView('library'));el('nav-documents').addEventListener('click',()=>selectView('documents'));
el('section-filter').addEventListener('change',()=>{const section=el('section-filter').value;const all=catalog.filter(t=>!section||t.section===section);fillSelect('department-filter',uniqueValues('department',all),'전체 부서',false);filtersChanged('section');});el('template-search').addEventListener('input',()=>{discoveryLimit=24;renderTemplates();});el('department-filter').addEventListener('change',()=>filtersChanged('department'));el('family-filter').addEventListener('change',()=>filtersChanged('family'));el('role-filter').addEventListener('change',()=>filtersChanged('role'));
el('doc-search').addEventListener('input',()=>{
  clearTimeout(documentSearchTimer);
  documentSearchTimer=setTimeout(()=>loadDocuments().catch(error=>toast(error.message)),180);
});
function closeEditor(){el('editor-panel').classList.add('hidden');selectedTemplate=null;editingDocument=null;}
el('editor-close').addEventListener('click',closeEditor);el('editor-cancel').addEventListener('click',closeEditor);
el('editor-form').addEventListener('submit',async event=>{
  event.preventDefault();
  if(!selectedTemplate||!editingDocument)return;
  const values=Object.fromEntries(selectedTemplate.fields.map(field=>[field.id,el('field-'+field.id).value]));
  const title=el('doc-title').value;
  const {id,revision}=editingDocument;
  try{
    if(!await canvasMayNavigate())return;
    await api('/api/v1/documents/'+id,{method:'PUT',headers:requestHeaders,body:JSON.stringify({expected_revision:revision,title,values})});
    closeEditor();
    if(currentView==='canvas'&&canvasPageId===id)await loadCanvas();
    await loadDocuments();
    toast('템플릿 필드를 저장했습니다.');
  }catch(e){toast('저장 실패: '+e.message);}
});
window.addEventListener('dragover',event=>event.preventDefault());window.addEventListener('drop',event=>event.preventDefault());
(async()=>{
  try{
    const data=await api('/api/v1/templates');
    catalog=data.items;
    fillSelect('department-filter',uniqueValues('department',catalog),'전체 부서',false);
    filtersChanged('department');
    await loadDocuments();
    if(navigationVersion===0)await selectView('canvas');
  }catch(e){toast('초기화 실패: '+e.message);}
})();


// Integrated Workspace local-only modules (v0.9): Page Tree, Projects, Task Database and Calendar.
let pageDocuments=[],projectItems=[],taskItems=[],editingProject=null,editingTask=null,editingEvent=null,pendingParentId=null;
const statusLabel={planned:'계획',active:'진행',on_hold:'보류',completed:'완료',todo:'할 일',in_progress:'진행 중',blocked:'차단',done:'완료',archived:'보관'};
let calendarCursor=seoulTodayDate();
function seoulTodayDate(){const parts=new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Seoul',year:'numeric',month:'numeric',day:'numeric'}).formatToParts(new Date());const get=k=>Number(parts.find(p=>p.type===k).value);return new Date(Date.UTC(get('year'),get('month')-1,get('day')));}
function isoDay(d){return [d.getUTCFullYear(),String(d.getUTCMonth()+1).padStart(2,'0'),String(d.getUTCDate()).padStart(2,'0')].join('-');}
function addDays(d,n){const next=new Date(d.getTime());next.setUTCDate(next.getUTCDate()+n);return next;}
function fromIsoDate(s){const [y,m,d]=s.split('-').map(Number);return new Date(Date.UTC(y,m-1,d));}
function resetSelect(id,items,emptyText){const select=el(id),old=select.value;select.replaceChildren(node('option',{value:''},emptyText));for(const x of items)select.append(node('option',{value:x.id},x.title));if(items.some(x=>x.id===old))select.value=old;}
async function refreshDocOptions(){const data=await api('/api/v1/pages/tree');pageDocuments=data.items;
  for(const id of ['task-document','cal-document','page-move-source','page-move-target']){
    resetSelect(id,pageDocuments,id==='page-move-target'?'최상위 / 없음':'선택하지 않음');
  }
}
async function loadPages(){await refreshDocOptions();renderPageTree();}
function renderPageTree(){const tree=el('page-tree');tree.replaceChildren();if(!pageDocuments.length){tree.append(node('p',{className:'empty'},'페이지가 없습니다. Template Library에서 문서를 생성하세요.'));return;}
  const byParent=new Map();for(const d of pageDocuments){const parent=d.parent_id||'';if(!byParent.has(parent))byParent.set(parent,[]);byParent.get(parent).push(d);}
  const seen=new Set();const walk=(parent,depth)=>{for(const d of (byParent.get(parent)||[])){
    if(seen.has(d.id))continue;seen.add(d.id);
    const row=node('div',{className:'tree-row'});row.style.paddingLeft=(depth*18+8)+'px';
    const open=node('button',{type:'button',className:'tree-open'},(depth?'└ ':'▤ ')+d.title);
    open.addEventListener('click',async()=>{try{await openCanvas(d.id);}catch(e){toast(e.message);}});
    const child=node('button',{type:'button',className:'tree-add'},'+ 하위 문서');
    child.addEventListener('click',()=>selectView('library',{parentId:d.id}));row.append(open,child);tree.append(row);walk(d.id,depth+1);
  }};walk('',0);
  // Safeguard for imported or orphaned data (unreachable hierarchy).
  for(const d of pageDocuments)if(!seen.has(d.id))walk(d.parent_id||'',0);
}
el('page-new-root').addEventListener('click',()=>createCanvasPage().catch(e=>toast(e.message)));
el('page-move-btn').addEventListener('click',async()=>{try{const ident=el('page-move-source').value;if(!ident)throw Error('이동할 페이지를 선택하세요.');const page=pageDocuments.find(d=>d.id===ident);
  await api('/api/v1/pages/'+ident+'/move',{method:'PUT',headers:requestHeaders,body:JSON.stringify({expected_revision:page.revision,parent_id:el('page-move-target').value||null})});await loadPages();toast('페이지 위치를 변경했습니다.');
}catch(e){toast(e.message);}});
for(const name of ['pages','database','projects','calendar'])el('nav-'+name).addEventListener('click',()=>selectView(name));

async function loadProjects(){const result=await api('/api/v1/projects');projectItems=result.items;
  for(const id of ['task-filter-project','task-project'])resetSelect(id,projectItems,id==='task-filter-project'?'모든 프로젝트':'프로젝트 미지정');
  const box=el('project-list');box.replaceChildren();if(!projectItems.length)box.append(node('p',{className:'empty'},'생성된 프로젝트가 없습니다.'));
  for(const p of projectItems){const item=node('div',{className:'project-row'}),details=node('div');details.append(node('strong',{},p.title),node('small',{},(statusLabel[p.status]||p.status)+' · '+(p.description||'설명 없음')));
    const edit=node('button',{type:'button',className:'secondary-button'},'편집');edit.addEventListener('click',()=>{editingProject=p;el('project-title').value=p.title;el('project-description').value=p.description;el('project-status').value=p.status;});
    const tasks=node('button',{type:'button',className:'secondary-button'},'업무 보기');tasks.addEventListener('click',async()=>{selectView('database');await loadTasks();el('task-filter-project').value=p.id;renderTasks();});
    item.append(details,edit,tasks);box.append(item);
  }
}
function resetProjectForm(){editingProject=null;el('project-form').reset();}
el('project-reset').addEventListener('click',resetProjectForm);
el('project-form').addEventListener('submit',async e=>{e.preventDefault();const data={title:el('project-title').value,description:el('project-description').value,status:el('project-status').value};
  const path=editingProject?'/api/v1/projects/'+editingProject.id:'/api/v1/projects';if(editingProject)data.expected_revision=editingProject.revision;
  try{await api(path,{method:editingProject?'PUT':'POST',headers:requestHeaders,body:JSON.stringify(data)});resetProjectForm();await loadProjects();toast('프로젝트를 저장했습니다.');}catch(err){toast(err.message);}
});

async function loadTasks(){await Promise.all([loadProjects(),refreshDocOptions()]);const data=await api('/api/v1/tasks');taskItems=data.items;
  resetSelect('cal-task',taskItems.filter(x=>x.status!=='archived'),'연결 안 함');renderTasks();}
function renderTasks(){const root=el('task-list');root.replaceChildren();const filter=el('task-filter-project').value;const list=taskItems.filter(t=>!filter||t.project_id===filter);const view=el('task-view').value;
  if(!list.length){root.append(node('p',{className:'empty'},'해당 조건에 업무가 없습니다.'));return;}
  const edit=t=>{editingTask=t;el('task-title').value=t.title;el('task-project').value=t.project_id||'';el('task-status').value=t.status;el('task-priority').value=t.priority;el('task-due').value=t.due_on||'';el('task-document').value=t.document_id||'';el('task-title').focus();};
  if(view==='table'){
    const table=node('table',{className:'task-table'}),head=node('tr');for(const h of ['업무','상태','우선순위','마감일','프로젝트','문서'])head.append(node('th',{},h));table.append(head);
    for(const t of list){const tr=node('tr');const title=node('button',{type:'button',className:'cell-button'},t.title);title.addEventListener('click',()=>edit(t));const cell=node('td');cell.append(title);tr.append(cell);
      for(const value of [statusLabel[t.status]||t.status,t.priority,t.due_on||'—',projectItems.find(p=>p.id===t.project_id)?.title||'—',pageDocuments.find(d=>d.id===t.document_id)?.title||'—'])tr.append(node('td',{},value));table.append(tr);
    }root.append(table);
  }else{
    const board=node('div',{className:'task-board'});for(const status of ['todo','in_progress','blocked','done','archived']){const lane=node('div',{className:'task-lane'});lane.append(node('strong',{},statusLabel[status]));for(const t of list.filter(x=>x.status===status)){
      const card=node('button',{type:'button',className:'board-card'});card.append(node('strong',{},t.title),node('small',{},t.due_on?'마감 '+t.due_on:'마감일 없음'));card.addEventListener('click',()=>edit(t));lane.append(card);
    }board.append(lane);}root.append(board);
  }
}
function resetTaskForm(){editingTask=null;el('task-form').reset();}
el('task-reset').addEventListener('click',resetTaskForm);
el('task-view').addEventListener('change',renderTasks);
el('task-filter-project').addEventListener('change',renderTasks);
el('task-form').addEventListener('submit',async e=>{e.preventDefault();const data={title:el('task-title').value,project_id:el('task-project').value||null,status:el('task-status').value,priority:el('task-priority').value,due_on:el('task-due').value||null,document_id:el('task-document').value||null};
  const path=editingTask?'/api/v1/tasks/'+editingTask.id:'/api/v1/tasks';if(editingTask)data.expected_revision=editingTask.revision;
  try{await api(path,{method:editingTask?'PUT':'POST',headers:requestHeaders,body:JSON.stringify(data)});resetTaskForm();await loadTasks();toast('업무를 저장했습니다. Calendar에 마감일이 자동 표시됩니다.');}catch(err){toast(err.message);}
});

// Date-only calendar grid; timed events require explicit +09:00 offset, converted by API to UTC.
function calView(){return el('cal-view').value;}
function calPeriod(){const pivot=calendarCursor,view=calView();let start,end;
  if(view==='month'){const first=new Date(Date.UTC(pivot.getUTCFullYear(),pivot.getUTCMonth(),1));start=addDays(first,-first.getUTCDay());end=addDays(start,42);}
  else if(view==='week'){start=addDays(pivot,-pivot.getUTCDay());end=addDays(start,7);}
  else {start=pivot;end=addDays(start,1);}return {start,end};
}
async function loadCalendar(){await Promise.all([refreshDocOptions(),api('/api/v1/tasks').then(d=>{taskItems=d.items;resetSelect('cal-task',taskItems.filter(t=>t.status!=='archived'),'연결 안 함');})]);
  const {start,end}=calPeriod();const data=await api('/api/v1/calendar/feed?start='+isoDay(start)+'&end='+isoDay(end));renderCalendar(data.items,start,end);
}
function renderCalendar(items,start,end){const root=el('calendar-grid');root.replaceChildren();const view=calView();el('cal-range-label').textContent=view==='month'?calendarCursor.getUTCFullYear()+'년 '+(calendarCursor.getUTCMonth()+1)+'월':isoDay(start)+(view==='week'?' ~ '+isoDay(addDays(end,-1)):'');
  const weekDays=['일','월','화','수','목','금','토'];const count=Math.round((end-start)/86400000);
  const grid=node('div',{className:view==='month'?'calendar-days month-grid':'calendar-days linear-grid'});
  if(view==='month')for(const text of weekDays)grid.append(node('div',{className:'weekday'},text));
  for(let i=0;i<count;i++){
    const d=addDays(start,i),day=isoDay(d),cell=node('div',{className:'calendar-cell'});
    if(d.getUTCMonth()!==calendarCursor.getUTCMonth()&&view==='month')cell.classList.add('outside-month');
    const choose=node('button',{type:'button',className:'calendar-day-button'},(view==='month'?'':weekDays[d.getUTCDay()]+' ')+day.slice(8));
    choose.addEventListener('click',()=>{editingEvent=null;el('calendar-form').reset();el('cal-start-date').value=day;el('cal-end-date').value=day;el('cal-all-day').dispatchEvent(new Event('change'));el('cal-title').focus();});cell.append(choose);
    for(const entry of items.filter(x=>x.start_date<=day&&x.end_date>day)){
      const chip=node('button',{type:'button',className:entry.kind==='task'?'calendar-chip task-chip':'calendar-chip event-chip'});
      const time=entry.kind==='event'&&!entry.all_day?new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(entry.start_at))+' ':'';
      chip.textContent=(entry.kind==='task'?'■ ':'● ')+time+entry.title;chip.title=entry.kind==='task'?'Task Database 업무 보기':'일정 수정';
      chip.addEventListener('click',()=>{if(entry.kind==='task'){selectView('database');loadTasks().then(()=>{const task=taskItems.find(t=>t.id===entry.id);if(task){editingTask=task;el('task-title').value=task.title;el('task-project').value=task.project_id||'';el('task-status').value=task.status;el('task-priority').value=task.priority;el('task-due').value=task.due_on||'';el('task-document').value=task.document_id||'';}}).catch(e=>toast(e.message));}
        else openCalendarEvent(entry);});cell.append(chip);
    }grid.append(cell);
  }root.append(grid);
}
function openCalendarEvent(event){editingEvent=event;el('cal-title').value=event.title;el('cal-all-day').value=event.all_day?'true':'false';
  if(event.all_day){el('cal-start-date').value=event.start_at;el('cal-end-date').value=isoDay(addDays(fromIsoDate(event.end_at),-1));}
  else {const formatter=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
    const display=iso=>formatter.format(new Date(iso)).replace(' ','T');const first=display(event.start_at),last=display(event.end_at);
    el('cal-start-date').value=first.slice(0,10);el('cal-start-time').value=first.slice(11,16);el('cal-end-date').value=last.slice(0,10);el('cal-end-time').value=last.slice(11,16);}
  el('cal-document').value=event.document_id||'';el('cal-task').value=event.task_id||'';el('cal-all-day').dispatchEvent(new Event('change'));el('cal-title').focus();}
function resetCalForm(){editingEvent=null;el('calendar-form').reset();const today=isoDay(calendarCursor);el('cal-start-date').value=today;el('cal-end-date').value=today;el('cal-start-time').value='09:00';el('cal-end-time').value='10:00';el('cal-all-day').dispatchEvent(new Event('change'));}
el('cal-reset').addEventListener('click',resetCalForm);
el('cal-all-day').addEventListener('change',()=>{for(const n of document.querySelectorAll('.cal-time'))n.classList.toggle('hidden',el('cal-all-day').value==='true');});
el('cal-prev').addEventListener('click',()=>{if(calView()==='month'){calendarCursor.setUTCDate(1);calendarCursor.setUTCMonth(calendarCursor.getUTCMonth()-1);}else calendarCursor=addDays(calendarCursor,calView()==='week'?-7:-1);loadCalendar().catch(e=>toast(e.message));});
el('cal-next').addEventListener('click',()=>{if(calView()==='month'){calendarCursor.setUTCDate(1);calendarCursor.setUTCMonth(calendarCursor.getUTCMonth()+1);}else calendarCursor=addDays(calendarCursor,calView()==='week'?7:1);loadCalendar().catch(e=>toast(e.message));});
el('cal-today').addEventListener('click',()=>{calendarCursor=seoulTodayDate();resetCalForm();loadCalendar().catch(e=>toast(e.message));});
el('cal-view').addEventListener('change',()=>loadCalendar().catch(e=>toast(e.message)));
el('calendar-form').addEventListener('submit',async e=>{e.preventDefault();try{const allDay=el('cal-all-day').value==='true';const first=el('cal-start-date').value,last=el('cal-end-date').value;
    if(!first||!last)throw Error('일정 날짜를 선택하세요.');const payload={title:el('cal-title').value,all_day:allDay,timezone:'Asia/Seoul',document_id:el('cal-document').value||null,task_id:el('cal-task').value||null};
    if(allDay){payload.start_at=first;payload.end_at=isoDay(addDays(fromIsoDate(last),1));}
    else {payload.start_at=first+'T'+el('cal-start-time').value+':00+09:00';payload.end_at=last+'T'+el('cal-end-time').value+':00+09:00';}
    const path=editingEvent?'/api/v1/calendar/events/'+editingEvent.id:'/api/v1/calendar/events';if(editingEvent)payload.expected_revision=editingEvent.revision;
    await api(path,{method:editingEvent?'PUT':'POST',headers:requestHeaders,body:JSON.stringify(payload)});resetCalForm();await loadCalendar();toast('개인 일정을 저장했습니다.');
  }catch(error){toast('일정 저장 실패: '+error.message);}
});
resetCalForm();

// Home dashboard — derived local data only, no exports or telemetry.
async function loadDashboard(){const today=seoulTodayDate(),end=addDays(today,14);
  const [docs,projects,tasks,feed]=await Promise.all([api('/api/v1/documents'),api('/api/v1/projects'),api('/api/v1/tasks'),api('/api/v1/calendar/feed?start='+isoDay(today)+'&end='+isoDay(end))]);
  el('stat-docs').textContent=String(docs.items.length);el('stat-projects').textContent=String(projects.items.length);
  el('stat-tasks').textContent=String(tasks.items.filter(t=>t.status!=='done'&&t.status!=='archived').length);
  el('stat-events').textContent=String(feed.items.filter(x=>x.kind==='event').length);
  const upcoming=el('home-upcoming');upcoming.replaceChildren();if(!feed.items.length){upcoming.append(node('p',{className:'empty'},'앞으로 2주간 등록된 일정이나 마감일이 없습니다.'));return;}
  for(const x of feed.items.slice(0,25)){const row=node('div',{className:'upcoming-row'}),icon=node('span',{},x.kind==='task'?'■':'●');const title=node('span',{},x.start_date+' · '+x.title);
    const btn=node('button',{type:'button',className:'secondary-button'},x.kind==='task'?'업무 보기':'일정 보기');btn.addEventListener('click',()=>selectView(x.kind==='task'?'database':'calendar'));row.append(icon,title,btn);upcoming.append(row);}
}
el('nav-home').addEventListener('click',()=>selectView('home'));
el('home-open-calendar').addEventListener('click',()=>selectView('calendar'));


// Local-only quick navigation; never sends search terms to external endpoints.
for(const tab of document.querySelectorAll('.library-tab'))tab.addEventListener('click',()=>{
  discoveryMode=tab.dataset.discovery||'all';
  activeCollection='';
  discoveryLimit=templatePageSize;
  document.querySelectorAll('.library-tab').forEach(button=>{
    const selected=button===tab;
    button.classList.toggle('selected',selected);
    button.setAttribute('aria-pressed',String(selected));
  });
  renderTemplates();
});
el('sidebar-quick-search').addEventListener('click',async()=>{if(await selectView('library'))el('template-search').focus();});
el('topbar-new-page').addEventListener('click',()=>createCanvasPage().catch(e=>toast(e.message)));
el('sidebar-collapse').addEventListener('click',()=>document.body.classList.toggle('sidebar-collapsed'));
document.addEventListener('keydown',async e=>{
  if(!e.isComposing&&(e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){
    e.preventDefault();if(await selectView('library'))el('template-search').focus();
  }
});

el('template-more').addEventListener('click',()=>{discoveryLimit+=templatePageSize;renderTemplates();});

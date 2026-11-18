'use strict';

const cdbRoot='/api/v1/databases';
const cdbTypes={text:'텍스트',number:'숫자',date:'날짜',checkbox:'체크박스',select:'선택',
  multi_select:'다중 선택',url:'참고 주소',relation:'관계',rollup:'롤업',formula:'수식'};
const cdbKinds={table:'표',board:'보드',calendar:'캘린더',timeline:'타임라인',gallery:'갤러리'};
const cdbRollups={count:'개수',sum:'합계',average:'평균',min:'최솟값',max:'최댓값'};
const cdbFormulas={add:'더하기',subtract:'빼기',multiply:'곱하기',divide:'나누기'};
const cdbDays=['일','월','화','수','목','금','토'];
const cdbViews=new Map();
const cdbLinked=new Map();
let cdbIndex=[],cdbActive=null,cdbLoading=0;
let cdbMonth=cdbMonthStart(seoulTodayDate());
let cdbDragging=null;

function cdbMonthStart(date){
  const first=new Date(date);
  first.setUTCDate(1);
  return first;
}
function cdbDate(value){return new Date(value+'T00:00:00Z');}
function cdbRead(id){return api(cdbRoot+'/'+encodeURIComponent(id));}
function cdbWrite(path,method,body){
  return api(cdbRoot+path,{method,headers:requestHeaders,body:JSON.stringify(body)});
}
function cdbButton(text,action,attributes={}){
  const button=node('button',{type:'button',className:'secondary-button',...attributes},text);
  button.addEventListener('click',()=>Promise.resolve().then(action).catch(error=>toast(error.message)));
  return button;
}
function cdbLabel(label,control){
  const wrap=node('label',{},label);
  if(control.matches('input,select,textarea,output'))control.setAttribute('aria-label',label);
  wrap.append(control);
  return wrap;
}
function cdbSelect(options,value='',placeholder='선택 없음',attributes={}){
  const select=node('select',attributes);
  if(placeholder!==null)select.append(node('option',{value:''},placeholder));
  for(const [id,label] of options)select.append(node('option',{value:id},label));
  select.value=String(value??'');
  if(select.selectedIndex<0)select.selectedIndex=0;
  return select;
}
function cdbInput(value='',attributes={}){
  const input=node('input',{type:'text',...attributes});
  input.value=value??'';
  return input;
}
function cdbArea(value='',attributes={}){
  const area=node('textarea',{rows:'4',...attributes});
  area.value=value??'';
  return area;
}
function cdbOptionRows(items){return items.map(item=>[item.id,item.name]);}
function cdbIsComputed(property){return property.type==='rollup'||property.type==='formula';}
function cdbField(database,id){return database.properties.find(property=>property.id===id);}
function cdbType(database,id){return !id||id==='title'?'text':cdbField(database,id)?.type;}
function cdbValue(record,id){return !id||id==='title'?record.title:record.values[id];}
function cdbWritable(database,values){
  return Object.fromEntries(database.properties.filter(property=>!cdbIsComputed(property)&&values[property.id]!=null)
    .map(property=>[property.id,values[property.id]]));
}
function cdbDisplayValue(property,value,relations){
  if(value==null||value==='')return '—';
  if(property?.type==='relation'){
    const titles=relations.get(property.config.database_id);
    return value.map(id=>titles?.get(id)||'연결된 레코드').join(', ')||'—';
  }
  if(typeof value==='boolean')return value?'선택함':'선택 안 함';
  return Array.isArray(value)?value.join(', ')||'—':String(value);
}

function getActiveCustomDatabase(){return cdbActive;}
async function loadCustomDatabases(){
  const generation=++cdbLoading;
  const {items}=await api(cdbRoot);
  if(generation!==cdbLoading||currentView!=='custom-db')return;
  cdbIndex=items;
  const previous=items.find(item=>item.id===cdbActive?.id);
  await cdbShowDatabase((previous||items[0])?.id);
}
async function refreshCustomDatabase(){
  await loadCustomDatabases();
  cdbRefreshLinked();
}
async function cdbShowDatabase(id){
  const generation=++cdbLoading;
  const root=el('custom-db-content');
  root.setAttribute('aria-busy','true');
  try{
  const database=id?await cdbRead(id):null;
  if(generation!==cdbLoading||currentView!=='custom-db')return;
  cdbActive=database;
  await cdbPaint(database,generation);
  }finally{
    if(generation===cdbLoading)root.setAttribute('aria-busy','false');
  }
}
async function openCustomDatabase(databaseId,recordId){
  if(currentView!=='custom-db'&&!await selectView('custom-db'))return;
  if(cdbActive?.id!==databaseId)await cdbShowDatabase(databaseId);
  if(recordId&&cdbActive?.id===databaseId){
    const record=cdbActive.records.find(item=>item.id===recordId);
    if(record)await cdbRecordDialog(cdbActive,record);
    else toast('레코드를 찾을 수 없습니다.');
  }
}
function cdbActiveView(database){
  return database.views.find(view=>view.id===cdbViews.get(database.id))||database.views[0];
}
async function cdbRelations(database){
  const ids=new Set(database.properties.filter(x=>x.type==='relation').map(x=>x.config.database_id));
  const results=await Promise.all([...ids].map(async id=>{
    const records=id===database.id?database.records:
      (await api(cdbRoot+'/'+encodeURIComponent(id)+'/records')).items;
    return [id,new Map(records.map(record=>[record.id,record.title]))];
  }));
  return new Map(results);
}
async function cdbPaint(database,generation){
  const root=el('custom-db-content');
  const picker=el('custom-db-picker');
  picker.replaceChildren(...cdbIndex.map(item=>node('option',{value:item.id},item.name)));
  if(!database){
    picker.disabled=true;
    root.replaceChildren(node('p',{className:'empty'},'새 데이터베이스를 만들어 레코드를 정리하세요.'));
    document.dispatchEvent(new CustomEvent('custom-database-change',{detail:null}));
    return;
  }
  picker.disabled=false;
  picker.value=database.id;
  document.dispatchEvent(new CustomEvent('custom-database-change',{detail:database}));
  const view=cdbActiveView(database);
  const relationTitles=await cdbRelations(database);
  if(generation!==cdbLoading||currentView!=='custom-db')return;
  const header=node('div',{className:'cdb-title'});
  header.append(node('h3',{'data-cdb-name':''},database.name),
    cdbButton('이름 변경',()=>cdbDatabaseDialog(database)));
  const tabs=node('div',{className:'cdb-tabs','aria-label':'저장된 보기',role:'group'});
  for(const option of database.views){
    tabs.append(cdbButton(option.name,()=>{
      cdbViews.set(database.id,option.id);
      return cdbPaint(database,++cdbLoading);
    },{'aria-pressed':String(option.id===view?.id),'data-cdb-view':option.kind}));
  }
  tabs.append(cdbButton('보기 추가',()=>cdbViewDialog(database),{id:'custom-db-add-view'}));
  const tools=node('div',{className:'cdb-actions'});
  tools.append(cdbButton('새 레코드',()=>cdbRecordDialog(database),{id:'custom-db-add-record',className:'primary-button'}),
    cdbButton('속성 관리',()=>cdbPropertyList(database),{id:'custom-db-properties'}));
  if(view)tools.append(cdbButton('보기 설정',()=>cdbViewDialog(database,view),{id:'custom-db-view-settings'}));
  const layout=node('div',{className:'cdb-view','data-cdb-kind':view?.kind||'table'});
  cdbRenderView(layout,database,view,relationTitles,record=>cdbRecordDialog(database,record),true);
  root.replaceChildren(header,tabs,tools,layout);
}
function cdbModal(title,submit,body,extra,showHistory){
  const dialog=el('custom-db-dialog');
  const head=node('div',{className:'cdb-dialog-head'});
  head.append(node('h3',{id:'custom-db-dialog-title'},title));
  const status=node('p',{role:'alert',className:'cdb-error'});
  const close=cdbButton('닫기',()=>dialog.close());
  const actions=node('div',{className:'cdb-actions'});
  const history=showHistory?cdbButton('변경 이력',()=>showHistory(history)):null;
  if(history)actions.append(history);
  actions.append(close);
  head.append(actions);
  const form=node('form',{className:'cdb-form'});
  form.append(body);
  if(submit){
    const buttons=node('div',{className:'cdb-actions'});
    const save=node('button',{type:'submit',className:'primary-button'},'저장');
    buttons.append(save);
    if(extra){
      buttons.append(cdbButton(extra.label,async()=>{
        save.disabled=true;
        close.disabled=true;
        if(history)history.disabled=true;
        try{await extra.action();dialog.close();await refreshCustomDatabase();}
        catch(error){status.textContent=error.message;}
        finally{save.disabled=false;close.disabled=false;if(history)history.disabled=false;}
      }));
    }
    form.append(buttons);
    form.addEventListener('submit',async event=>{
      event.preventDefault();
      save.disabled=true;
      close.disabled=true;
      if(history)history.disabled=true;
      status.textContent='';
      try{await submit();dialog.close();await refreshCustomDatabase();}
      catch(error){status.textContent=error.message;}
      finally{save.disabled=false;close.disabled=false;if(history)history.disabled=false;}
    });
  }
  dialog.replaceChildren(head,form,status);
  if(!dialog.open)dialog.showModal();
  body.querySelector('input, select, textarea, button')?.focus();
}
function cdbRecordHistoryRows(database,snapshot,relations){
  const rows=[['title','제목',snapshot.title],['notes','메모',snapshot.notes]];
  for(const property of database.properties){
    if(cdbIsComputed(property))continue;
    rows.push([property.id,property.name,cdbDisplayValue(property,snapshot.values[property.id],relations)]);
  }
  return rows;
}
function cdbViewHistoryRows(database,snapshot){
  const config=snapshot.config;
  const propertyName=id=>id==='title'?'레코드 제목':cdbField(database,id)?.name;
  const filter=cdbField(database,config.filter_property);
  const grouped=propertyName(config.group_by);
  const sorted=propertyName(config.sort_by);
  const filtered=propertyName(config.filter_property);
  const direction=config.sort_direction==='desc'?'내림차순':'오름차순';
  return [
    ['name','보기 이름',snapshot.name],['kind','보기 유형',cdbKinds[snapshot.kind]],
    ['start','날짜 속성',propertyName(config.date_property)],['end','종료일 속성',propertyName(config.end_date_property)],
    ['group','그룹 속성',grouped],['sort','정렬',sorted?sorted+' · '+direction:null],
    ['filter','필터',filtered?filtered+' = '+cdbDisplayValue(filter,config.filter_value,new Map()):null],
  ];
}
function cdbHistoryChanges(preview,entries,savedEntries){
  const saved=new Map(savedEntries.map(([key,,value])=>[key,value]));
  const table=node('table',{className:'cdb-table cdb-history-comparison','aria-label':'저장된 내용과 비교'});
  const heading=node('tr');
  for(const label of ['항목','현재 저장본','선택한 버전'])heading.append(node('th',{scope:'col'},label));
  const head=node('thead');
  head.append(heading);
  const body=node('tbody');
  for(const [key,label,value] of entries){
    const current=saved.get(key);
    const row=node('tr');
    if(value!==current)row.setAttribute('data-cdb-history-changed','');
    row.append(node('th',{scope:'row'},label),node('td',{},current||'—'),node('td',{},value||'—'));
    body.append(row);
  }
  table.append(head,body);
  preview.append(table);
}
function cdbHistoryDialog(trigger,{path,kind,expectedRevision,rows,current}){
  if(el('custom-db-history-dialog'))return;
  const editor=el('custom-db-dialog');
  const title=kind==='record'?'레코드 변경 이력':'보기 변경 이력';
  const dialog=node('dialog',{id:'custom-db-history-dialog',className:'cdb-dialog cdb-history-dialog',
    'aria-labelledby':'custom-db-history-title'});
  const head=node('div',{className:'cdb-dialog-head'});
  const status=node('p',{className:'cdb-history-status',role:'status'});
  const close=cdbButton('닫기',()=>dialog.close(),{id:'custom-db-history-close'});
  head.append(node('h3',{id:'custom-db-history-title'},title),close);
  const columns=node('div',{className:'cdb-history-grid'});
  const list=node('div',{className:'cdb-history-list',role:'group','aria-label':'저장된 버전'});
  const preview=node('div',{className:'cdb-history-preview','aria-live':'polite'});
  const revisions=[];
  let selected=null,loading=false,restoring=false;
  const more=cdbButton('이전 버전 더 보기',()=>load(revisions.at(-1)?.revision),{id:'custom-db-history-more'});
  more.hidden=true;
  const rail=node('div');
  rail.append(list,more);
  columns.append(rail,preview);
  dialog.append(head,status,columns);
  document.body.append(dialog);
  dialog.addEventListener('cancel',event=>{if(restoring)event.preventDefault();});
  dialog.addEventListener('close',()=>{
    dialog.remove();
    if(editor.open)trigger.focus();
  });
  dialog.showModal();
  close.focus();
  async function load(before){
    if(loading||restoring)return;
    loading=true;
    more.disabled=true;
    more.textContent='이전 버전 더 보기';
    status.textContent='이력을 불러오는 중…';
    try{
      const query=before?'?before_revision='+before:'';
      const {items}=await api(cdbRoot+path+'/history'+query);
      if(!dialog.open)return;
      revisions.push(...items);
      for(const item of items){
        const date=new Date(item.created_at).toLocaleString('ko-KR');
        const button=cdbButton('버전 '+item.revision,()=>select(item),{
          'data-cdb-history-revision':item.revision,'aria-pressed':'false',
        });
        button.append(node('small',{},date),node('small',{},item.title));
        list.append(button);
      }
      more.hidden=items.length<25;
      if(!selected&&revisions.length)select(revisions[0]);
      status.textContent=revisions.length?'':'저장된 변경 이력이 없습니다.';
    }catch(error){
      if(dialog.open){
        status.textContent=error.message;
        more.hidden=false;
        more.textContent='다시 시도';
      }
    }finally{
      loading=false;
      more.disabled=false;
    }
  }
  function select(item){
    selected=item;
    for(const button of list.children){
      button.setAttribute('aria-pressed',String(Number(button.dataset.cdbHistoryRevision)===item.revision));
    }
    preview.replaceChildren(node('h4',{},item.title));
    const currentVersion=item===revisions[0];
    if(currentVersion)preview.append(node('p',{className:'cdb-history-status'},'가장 최근에 저장된 버전'));
    cdbHistoryChanges(preview,rows(item.snapshot),rows(revisions[0]?.snapshot||current));
    if(currentVersion)return;
    const restore=cdbButton('이 버전 복원',async()=>{
      if(restoring||!window.confirm('이 버전을 복원할까요? 편집 중인 변경 내용은 버려집니다.'))return;
      restoring=true;
      for(const button of dialog.querySelectorAll('button'))button.disabled=true;
      status.textContent='선택한 버전을 복원하는 중…';
      try{
        await cdbWrite(path+'/history/'+item.revision+'/restore','POST',{expected_revision:expectedRevision});
        editor.close();
        dialog.close();
        await refreshCustomDatabase();
        toast('선택한 버전을 복원했습니다.');
      }catch(error){
        if(dialog.open)status.textContent=error.message;
        else toast(error.message);
      }finally{
        restoring=false;
        for(const button of dialog.querySelectorAll('button'))button.disabled=false;
      }
    },{id:'custom-db-history-restore',className:'primary-button'});
    preview.append(restore);
  }
  void load();
}
function cdbDatabaseDialog(database){
  const name=cdbInput(database?.name,{required:'',maxlength:120,'aria-label':'데이터베이스 이름'});
  const body=node('div',{className:'cdb-fields'});
  body.append(cdbLabel('데이터베이스 이름',name));
  cdbModal(database?'데이터베이스 이름 변경':'새 데이터베이스',async()=>{
    cdbActive=database?
      await cdbWrite('/'+database.id,'PUT',{name:name.value,expected_revision:database.revision}):
      await cdbWrite('','POST',{name:name.value});
  },body);
}
function cdbPropertyList(database){
  const body=node('div',{className:'cdb-fields'});
  for(const property of database.properties){
    const row=node('div',{className:'cdb-property'});
    row.append(node('span',{},property.name+' · '+cdbTypes[property.type]),
      cdbButton('편집',()=>cdbPropertyDialog(database,property),{'aria-label':property.name+' 속성 편집'}));
    body.append(row);
  }
  body.append(cdbButton('속성 추가',()=>cdbPropertyDialog(database),{id:'custom-db-add-property'}));
  cdbModal('속성 관리',null,body);
}
async function cdbPropertyDialog(database,property){
  const name=cdbInput(property?.name,{required:'',maxlength:80});
  const kind=cdbSelect(Object.entries(cdbTypes),property?.type??'text',null);
  kind.disabled=Boolean(property);
  const body=node('div',{className:'cdb-fields'});
  const config=node('div',{className:'cdb-fields'});
  body.append(cdbLabel('속성 이름',name),cdbLabel('속성 유형',kind),config);
  const existing=property?.config||{};
  let readConfig=()=>({});
  let generation=0;
  async function options(){
    const token=++generation;
    config.replaceChildren();
    readConfig=()=>({});
    const add=(label,input)=>{config.append(cdbLabel(label,input));return input;};
    if(['select','multi_select'].includes(kind.value)){
      const tags=add('선택 항목 (줄마다 하나)',cdbArea((existing.options||[]).join('\n'),{required:''}));
      readConfig=()=>({options:tags.value.split(/\r?\n/).map(value=>value.trim()).filter(Boolean)});
    }
    if(kind.value==='relation'){
      const target=add('연결할 데이터베이스',cdbSelect(cdbOptionRows(cdbIndex),existing.database_id,'데이터베이스 선택',{required:''}));
      readConfig=()=>({database_id:target.value});
    }
    if(kind.value==='rollup'){
      const relations=database.properties.filter(option=>option.type==='relation');
      const relation=add('관계 속성',cdbSelect(cdbOptionRows(relations),existing.relation_id,'관계 선택',{required:''}));
      const operation=add('집계 방식',cdbSelect(Object.entries(cdbRollups),existing.operation||'count',null));
      const propertySelect=cdbSelect([],null,'속성 선택');
      const propertyLabel=cdbLabel('집계할 숫자 속성',propertySelect);
      config.append(propertyLabel);
      let load=0;
      async function targetOptions(){
        const version=++load;
        propertyLabel.hidden=operation.value==='count';
        propertySelect.disabled=true;
        propertySelect.required=operation.value!=='count';
        if(operation.value==='count')return;
        const definition=relations.find(item=>item.id===relation.value);
        if(!definition){propertySelect.replaceChildren(node('option',{value:''},'관계 선택 필요'));return;}
        const target=definition.config.database_id===database.id?database:await cdbRead(definition.config.database_id);
        if(token!==generation||version!==load)return;
        const choices=cdbSelect(cdbOptionRows(target.properties.filter(item=>item.type==='number')),
          existing.property_id,'속성 선택');
        const value=choices.value;
        propertySelect.replaceChildren(...choices.children);
        propertySelect.value=value;
        if(propertySelect.selectedIndex<0)propertySelect.selectedIndex=0;
        propertySelect.disabled=false;
      }
      for(const input of [relation,operation])input.addEventListener('change',()=>targetOptions().catch(error=>toast(error.message)));
      readConfig=()=>{
        if(operation.value!=='count'&&!propertySelect.value)throw Error('집계할 숫자 속성을 선택해 주세요.');
        return {relation_id:relation.value,operation:operation.value,
          ...(operation.value==='count'?{}:{property_id:propertySelect.value})};
      };
      await targetOptions();
    }
    if(kind.value==='formula'){
      const numeric=cdbOptionRows(database.properties.filter(item=>item.id!==property?.id&&['number','rollup'].includes(item.type)));
      const operation=add('계산 방식',cdbSelect(Object.entries(cdbFormulas),existing.operation||'add',null));
      const first=add('왼쪽 숫자 속성',cdbSelect(numeric,existing.left_id,'속성 선택',{required:''}));
      const second=add('오른쪽 숫자 속성',cdbSelect(numeric,existing.right_id,'속성 선택',{required:''}));
      readConfig=()=>({operation:operation.value,left_id:first.value,right_id:second.value});
    }
  }
  kind.addEventListener('change',()=>options().catch(error=>toast(error.message)));
  await options();
  cdbModal(property?'속성 편집':'속성 추가',async()=>{
    const path='/'+database.id+'/properties'+(property?'/'+property.id:'');
    await cdbWrite(path,property?'PUT':'POST',{name:name.value,type:kind.value,config:readConfig(),expected_revision:database.revision});
  },body);
}
async function cdbRecordDialog(database,record){
  if(el('custom-db-dialog').open)return;
  const title=cdbInput(record?.title,{required:'',maxlength:120});
  const notes=cdbArea(record?.notes,{maxlength:8000});
  const body=node('div',{className:'cdb-fields'});
  body.append(cdbLabel('레코드 제목',title),cdbLabel('메모',notes));
  const relations=await cdbRelations(database);
  if(currentView!=='custom-db'||cdbActive?.id!==database.id||el('custom-db-dialog').open)return;
  const readers=[];
  for(const property of database.properties){
    const value=record?.values[property.id];
    if(cdbIsComputed(property)){
      const readout=node('div',{className:'cdb-computed'});
      readout.append(node('span',{},property.name),
        node('output',{'aria-label':property.name},cdbDisplayValue(property,value,relations)));
      body.append(readout);
      continue;
    }
    const options=property.type==='relation'
      ?[...relations.get(property.config.database_id)]
      :(property.config.options||[]).map(label=>[label,label]);
    const field=cdbValueField(property.type,value,options);
    readers.push([property.id,field.read]);
    body.append(cdbLabel(property.name,field.control));
  }
  const path='/'+database.id+'/records'+(record?'/'+record.id:'');
  const erase=record?{label:'레코드 삭제',action:async()=>{
    await fetch(cdbRoot+path,{method:'DELETE',headers:requestHeaders,
      body:JSON.stringify({expected_revision:record.revision}),cache:'no-store',credentials:'same-origin'})
      .then(async response=>{
        if(response.ok)return;
        const err=await response.json().catch(()=>({}));
        throw Error(typeof err.detail==='string'?err.detail:'레코드를 삭제하지 못했습니다.');
      });
  }}:null;
  if(erase){
    const remove=erase.action;
    erase.action=()=>window.confirm('레코드를 삭제할까요?')?remove():Promise.reject(Error('삭제를 취소했습니다.'));
  }
  cdbModal(record?'레코드 편집':'새 레코드',async()=>{
    const values=Object.fromEntries(readers.map(([id,read])=>[id,read()]));
    const payload={title:title.value,notes:notes.value,values:cdbWritable(database,values)};
    if(record)payload.expected_revision=record.revision;
    const saved=await cdbWrite(path,record?'PUT':'POST',payload);
    const view=cdbActiveView(database);
    const date=view?.config.date_property&&saved.values[view.config.date_property];
    if(date)cdbMonth=cdbMonthStart(cdbDate(date));
  },body,erase,record?trigger=>cdbHistoryDialog(trigger,{
    path,kind:'record',expectedRevision:record.revision,current:record,
    rows:snapshot=>cdbRecordHistoryRows(database,snapshot,relations),
  }):null);
}
function cdbValueField(type,value,options){
  if(type==='checkbox'){
    const control=cdbInput('',{type:'checkbox'});
    control.checked=value===true;
    return {control,read:()=>control.checked};
  }
  if(type==='select'||type==='multi_select'||type==='relation'){
    const multiple=type!=='select';
    const chosen=multiple&&Array.isArray(value)?new Set(value):new Set();
    const control=cdbSelect(options,multiple?'':value,multiple?null:'선택 없음',
      multiple?{multiple:'',size:String(Math.min(6,Math.max(2,options.length)))}:{});
    if(multiple)for(const option of control.options)option.selected=chosen.has(option.value);
    return {control,read:()=>multiple?[...control.selectedOptions].map(option=>option.value):control.value||null};
  }
  if(type==='number'){
    const control=cdbInput(value,{type:'number',step:'any'});
    return {control,read:()=>control.value===''?null:control.valueAsNumber};
  }
  if(type==='date'){
    const control=cdbInput(value,{type:'date'});
    return {control,read:()=>control.value||null};
  }
  if(type==='text'){
    const control=cdbArea(value,{rows:2,maxlength:4000});
    return {control,read:()=>control.value||null};
  }
  const control=cdbInput(value,{inputmode:'url',maxlength:2048});
  return {control,read:()=>control.value||null};
}
function cdbViewDialog(database,view){
  const existing=view?.config||{};
  const name=cdbInput(view?.name,{required:'',maxlength:80});
  const kind=cdbSelect(Object.entries(cdbKinds),view?.kind||'table',null);
  const dates=cdbOptionRows(database.properties.filter(property=>property.type==='date'));
  const groups=cdbOptionRows(database.properties.filter(property=>['select','checkbox'].includes(property.type)));
  const sortable=[['title','레코드 제목'],...cdbOptionRows(database.properties)];
  const filterable=sortable.filter(([id])=>cdbType(database,id)!=='relation');
  const group=cdbSelect(groups,existing.group_by,'그룹 없음');
  const start=cdbSelect(dates,existing.date_property,'날짜 속성 선택');
  const end=cdbSelect(dates,existing.end_date_property,'종료일 없음');
  const sort=cdbSelect(sortable,existing.sort_by,'기본 순서');
  const direction=cdbSelect([['asc','오름차순'],['desc','내림차순']],existing.sort_direction||'asc',null);
  const filter=cdbSelect(filterable,existing.filter_property,'필터 없음');
  const startRow=cdbLabel('날짜 속성',start);
  const endRow=cdbLabel('종료일 속성',end);
  const groupRow=cdbLabel('그룹 속성',group);
  const match=cdbLabel('필터 값',node('span'));
  function adjust(){
    startRow.hidden=!['calendar','timeline'].includes(kind.value);
    start.disabled=startRow.hidden;
    start.required=!startRow.hidden;
    endRow.hidden=kind.value!=='timeline';
    end.disabled=endRow.hidden;
    groupRow.hidden=kind.value!=='board';
    group.required=!groupRow.hidden;
    group.disabled=groupRow.hidden;
  }
  let readFilter=()=>null;
  function changeFilter(useExisting=false){
    match.hidden=!filter.value;
    if(!filter.value)return;
    const type=cdbType(database,filter.value);
    const property=cdbField(database,filter.value);
    const original=useExisting&&filter.value===existing.filter_property?existing.filter_value:null;
    let field;
    if(type==='checkbox'){
      const control=cdbSelect([['true','선택함'],['false','선택 안 함']],original==null?'':String(original),'값 없음');
      field={control,read:()=>control.value===''?null:control.value==='true'};
    }else if(cdbIsComputed(property||{})||type==='number'){
      field=cdbValueField('number',original,[]);
    }else{
      field=cdbValueField(type==='multi_select'?'select':type,original,
        (property?.config.options||[]).map(label=>[label,label]));
    }
    match.lastElementChild.replaceWith(field.control);
    field.control.setAttribute('aria-label','필터 값');
    readFilter=field.read;
  }
  kind.addEventListener('change',adjust);
  filter.addEventListener('change',()=>changeFilter());
  adjust();
  changeFilter(true);
  const body=node('div',{className:'cdb-fields'});
  body.append(cdbLabel('보기 이름',name),cdbLabel('보기 유형',kind),groupRow,startRow,endRow,
    cdbLabel('정렬 속성',sort),cdbLabel('정렬 방향',direction),cdbLabel('필터 속성',filter),match);
  cdbModal(view?'보기 설정':'보기 추가',async()=>{
    const config={};
    if(!group.disabled&&group.value)config.group_by=group.value;
    if(!start.disabled&&start.value)config.date_property=start.value;
    if(!end.disabled&&end.value)config.end_date_property=end.value;
    if(sort.value)Object.assign(config,{sort_by:sort.value,sort_direction:direction.value});
    if(filter.value)Object.assign(config,{filter_property:filter.value,filter_value:readFilter()});
    const saved=await cdbWrite('/'+database.id+'/views'+(view?'/'+view.id:''),view?'PUT':'POST',{
      name:name.value,kind:kind.value,config,expected_revision:database.revision,
    });
    cdbViews.set(database.id,view?.id||saved.views.find(item=>!database.views.some(old=>old.id===item.id))?.id);
  },body,null,view?trigger=>cdbHistoryDialog(trigger,{
    path:'/'+database.id+'/views/'+view.id,kind:'view',expectedRevision:database.revision,current:view,
    rows:snapshot=>cdbViewHistoryRows(database,snapshot),
  }):null);
}

function cdbCompare(left,right){
  if(left==null)return right==null?0:1;
  if(right==null)return -1;
  if(typeof left==='number'&&typeof right==='number')return left-right;
  return String(left).localeCompare(String(right),'ko',{numeric:true,sensitivity:'base'});
}
function cdbRecords(database,view){
  const config=view?.config||{};
  const records=database.records.filter(record=>{
    if(!config.filter_property)return true;
    const value=cdbValue(record,config.filter_property);
    if(Array.isArray(value))return config.filter_value==null?value.length===0:value.includes(config.filter_value);
    return (value??null)===config.filter_value;
  });
  if(config.sort_by){
    const direction=config.sort_direction==='desc'?-1:1;
    records.sort((a,b)=>direction*cdbCompare(cdbValue(a,config.sort_by),cdbValue(b,config.sort_by)));
  }
  return records;
}
function cdbRecordButton(record,openRecord,className='secondary-button'){
  return cdbButton(record.title,()=>openRecord(record),{className,'data-cdb-record':record.id});
}
function cdbTable(root,database,records,relations,openRecord){
  const table=node('table',{className:'cdb-table'});
  const row=node('tr');
  for(const name of ['제목',...database.properties.map(item=>item.name)])row.append(node('th',{scope:'col'},name));
  const head=node('thead');
  head.append(row);
  const body=node('tbody');
  for(const record of records){
    const entry=node('tr',{'data-cdb-row':record.id});
    const title=node('th',{scope:'row'});
    title.append(cdbRecordButton(record,openRecord,'cdb-name-button'));
    entry.append(title);
    for(const property of database.properties){
      entry.append(node('td',{'data-cdb-value':property.id},cdbDisplayValue(property,record.values[property.id],relations)));
    }
    body.append(entry);
  }
  table.append(head,body);
  const wrapper=node('div',{className:'cdb-table-scroll',tabindex:'0','aria-label':'표 스크롤 영역'});
  wrapper.append(table);
  root.append(wrapper);
}
function cdbCard(database,record,relations,openRecord,kind){
  const card=node('article',{className:'cdb-card'});
  const button=cdbRecordButton(record,openRecord,'cdb-name-button');
  card.append(button);
  if(kind==='gallery'){
    const memo=record.notes.trim();
    if(memo)card.append(node('p',{},memo));
    const props=node('dl');
    for(const property of database.properties){
      if(record.values[property.id]==null)continue;
      props.append(node('dt',{},property.name),node('dd',{},cdbDisplayValue(property,record.values[property.id],relations)));
    }
    if(props.children.length)card.append(props);
  }
  return {card,button};
}
function cdbMarkDraggable(button,database,record){
  button.draggable=true;
  button.addEventListener('dragstart',event=>{
    cdbDragging={database:database.id,record};
    event.dataTransfer.effectAllowed='move';
    event.dataTransfer.setData('application/x-local-workspace-record',record.id);
  });
  button.addEventListener('dragend',()=>{
    cdbDragging=null;
    for(const target of document.querySelectorAll('.cdb-drop-here'))target.classList.remove('cdb-drop-here');
  });
}
function cdbDrop(target,database,property,value){
  target.addEventListener('dragover',event=>{
    if(cdbDragging?.database!==database.id)return;
    event.preventDefault();
    event.dataTransfer.dropEffect='move';
    target.classList.add('cdb-drop-here');
  });
  target.addEventListener('dragleave',event=>{
    if(!target.contains(event.relatedTarget))target.classList.remove('cdb-drop-here');
  });
  target.addEventListener('drop',async event=>{
    target.classList.remove('cdb-drop-here');
    if(cdbDragging?.database!==database.id)return;
    event.preventDefault();
    const {record}=cdbDragging;
    cdbDragging=null;
    const values=cdbWritable(database,{...record.values,[property]:value});
    try{
      await cdbWrite('/'+database.id+'/records/'+record.id,'PUT',
        {title:record.title,notes:record.notes,values,expected_revision:record.revision});
      await refreshCustomDatabase();
    }catch(error){toast(error.message);}
  });
}
function cdbBoard(root,database,view,records,relations,openRecord,editable){
  const property=cdbField(database,view.config.group_by);
  if(!property){
    root.append(node('p',{},'보기 설정에서 그룹 속성을 선택하세요.'));
    return;
  }
  const groups=new Map();
  const base=property.type==='checkbox'?[true,false]:property.config.options||[];
  for(const value of [...base,null])groups.set(value,[]);
  for(const record of records){
    const key=record.values[property.id]??null;
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(record);
  }
  const board=node('div',{className:'cdb-board','aria-label':'보드 그룹',tabindex:'0'});
  const draggable=editable&&['select','checkbox'].includes(property.type);
  for(const [value,members] of groups){
    const lane=node('section',{className:'cdb-lane','data-cdb-group':String(value??'')});
    lane.append(node('h4',{},value==null?'미지정':cdbDisplayValue(property,value,relations)));
    for(const record of members){
      const {card,button}=cdbCard(database,record,relations,openRecord,'board');
      if(draggable)cdbMarkDraggable(button,database,record);
      lane.append(card);
    }
    if(draggable)cdbDrop(lane,database,property.id,value);
    board.append(lane);
  }
  root.append(board);
}
function cdbPeriod(root,render,cursor,hasCalendar){
  const bar=node('div',{className:'cdb-period'});
  const date=cursor.date;
  function shift(step){
    const next=new Date(cursor.date);
    next.setUTCMonth(next.getUTCMonth()+step);
    const nextYear=next.getUTCFullYear();
    if(nextYear<2||nextYear>9998)return;
    cursor.date=next;
    render();
  }
  const previous=cdbButton('이전',()=>shift(-1),{'aria-label':'이전 달'});
  const next=cdbButton('다음',()=>shift(1),{'aria-label':'다음 달'});
  bar.append(previous,node('strong',{},`${date.getUTCFullYear()}년 ${date.getUTCMonth()+1}월`),next,
    cdbButton('오늘',()=>{cursor.date=cdbMonthStart(seoulTodayDate());render();}));
  if(hasCalendar)bar.append(node('span',{},'항목을 눌러 상세 보기'));
  root.append(bar);
}
function cdbUnscheduled(root,records,openRecord,label='날짜 미지정'){
  if(!records.length)return;
  const group=node('div',{className:'cdb-unscheduled'});
  group.append(node('h4',{},label),...records.map(record=>cdbRecordButton(record,openRecord)));
  root.append(group);
}
function cdbCalendar(root,database,view,records,openRecord,editable,cursor){
  const property=cdbField(database,view.config.date_property);
  if(!property){
    root.append(node('p',{},'보기 설정에서 날짜 속성을 선택하세요.'));
    return;
  }
  const days=new Map();
  for(const record of records){
    const date=record.values[property.id];
    if(!days.has(date))days.set(date,[]);
    days.get(date).push(record);
  }
  const first=addDays(cursor.date,-cursor.date.getUTCDay());
  const grid=node('div',{className:'cdb-calendar','aria-label':'월간 캘린더'});
  for(const day of cdbDays)grid.append(node('b',{},day));
  for(let i=0;i<42;i++){
    const date=addDays(first,i);
    const day=isoDay(date).padStart(10,'0');
    const cell=node('div',{className:'cdb-day','data-cdb-day':day,'aria-label':day});
    if(date.getUTCMonth()!==cursor.date.getUTCMonth())cell.classList.add('cdb-outside');
    cell.append(node('time',{datetime:day},date.getUTCDate()));
    for(const record of days.get(day)||[]){
      const chip=cdbRecordButton(record,openRecord,'cdb-calendar-record');
      if(editable)cdbMarkDraggable(chip,database,record);
      cell.append(chip);
    }
    if(editable)cdbDrop(cell,database,property.id,day);
    grid.append(cell);
  }
  root.append(grid);
  cdbUnscheduled(root,records.filter(record=>!record.values[property.id]),openRecord);
}
function cdbTimeline(root,database,view,records,openRecord,cursor){
  const start=cdbField(database,view.config.date_property);
  const end=cdbField(database,view.config.end_date_property);
  if(!start){
    root.append(node('p',{},'보기 설정에서 시작 날짜 속성을 선택하세요.'));
    return;
  }
  const first=cursor.date;
  const last=new Date(first);
  last.setUTCMonth(last.getUTCMonth()+1);
  last.setUTCDate(0);
  const labels=[1,8,15,22,last.getUTCDate()];
  const visible=[];
  const missing=[];
  const invalid=[];
  for(const record of records){
    const startText=record.values[start.id];
    const endText=end&&record.values[end.id]||startText;
    if(!startText){missing.push(record);continue;}
    const begin=cdbDate(startText);
    const finish=cdbDate(endText);
    if(finish<begin){invalid.push(record);continue;}
    if(begin>last||finish<first)continue;
    visible.push({record,begin,finish,startText,endText});
  }
  const chart=node('div',{className:'cdb-timeline','aria-label':'월간 타임라인'});
  const axis=node('div',{className:'cdb-timeline-axis','aria-hidden':'true'});
  for(const label of labels)axis.append(node('span',{},label+'일'));
  chart.append(axis);
  for(const {record,begin,finish,startText,endText} of visible){
    const lane=node('div',{className:'cdb-timeline-row'});
    const button=cdbRecordButton(record,openRecord,'cdb-timeline-item');
    button.title=startText+' ~ '+endText;
    button.setAttribute('aria-label',record.title+' '+button.title);
    const dayFrom=begin<first?1:begin.getUTCDate();
    const dayTo=finish>last?last.getUTCDate():finish.getUTCDate();
    button.style.gridColumn=dayFrom+' / '+(dayTo+1);
    lane.style.gridTemplateColumns='repeat('+last.getUTCDate()+', minmax(7px, 1fr))';
    lane.append(button);
    chart.append(lane);
  }
  if(!visible.length)chart.append(node('p',{},'이 달에 표시할 일정이 없습니다.'));
  root.append(chart);
  cdbUnscheduled(root,missing,openRecord);
  cdbUnscheduled(root,invalid,openRecord,'종료일이 시작일보다 빠른 레코드');
}
function cdbRenderView(root,database,view,relations,openRecord,editable=false){
  const records=cdbRecords(database,view);
  const kind=view?.kind||'table';
  if(kind==='calendar'||kind==='timeline'){
    const cursor={date:editable?cdbMonth:cdbMonthStart(seoulTodayDate())};
    if(!editable){
      const sample=records.map(record=>record.values[view.config.date_property]).find(Boolean);
      if(sample)cursor.date=cdbMonthStart(cdbDate(sample));
    }
    const render=()=>{
      if(editable)cdbMonth=cursor.date;
      root.replaceChildren();
      cdbPeriod(root,render,cursor,editable);
      if(kind==='calendar')cdbCalendar(root,database,view,records,openRecord,editable,cursor);
      else cdbTimeline(root,database,view,records,openRecord,cursor);
    };
    render();
  }else if(kind==='board'){
    cdbBoard(root,database,view,records,relations,openRecord,editable);
  }else if(kind==='gallery'){
    const grid=node('div',{className:'cdb-gallery'});
    for(const record of records)grid.append(cdbCard(database,record,relations,openRecord,'gallery').card);
    root.append(grid);
  }else cdbTable(root,database,records,relations,openRecord);
  if(!records.length)root.append(node('p',{className:'cdb-empty'},'이 보기에 표시할 레코드가 없습니다.'));
}

async function linkedDatabaseOptions(){
  const {items}=await api(cdbRoot);
  return await Promise.all(items.map(async item=>{
    const {items:views}=await api(cdbRoot+'/'+encodeURIComponent(item.id)+'/views');
    return {id:item.id,title:item.name,
      views:views.map(view=>({id:view.id,title:view.name,kind:view.kind}))};
  }));
}
async function renderLinkedDatabase(container,databaseId,viewId){
  const visit={databaseId,viewId};
  cdbLinked.set(container,visit);
  const active=()=>cdbLinked.get(container)===visit&&container.isConnected;
  try{
    const database=await cdbRead(databaseId);
    const view=database.views.find(item=>item.id===viewId);
    if(!view)throw Error('연결된 보기를 찾을 수 없습니다.');
    const relations=await cdbRelations(database);
    if(!active())return;
    const layout=node('div',{className:'cdb-view','data-cdb-kind':view.kind});
    const header=node('div',{className:'cdb-title'});
    header.append(cdbButton('원본 열기',()=>openCustomDatabase(database.id)));
    cdbRenderView(layout,database,view,relations,record=>openCustomDatabase(database.id,record.id));
    container.replaceChildren(header,layout);
  }catch(error){
    if(active())container.replaceChildren(node('p',{role:'status'},error.message));
  }
}
function cdbRefreshLinked(){
  for(const [container,{databaseId,viewId}] of cdbLinked){
    if(container.isConnected)void renderLinkedDatabase(container,databaseId,viewId);
    else cdbLinked.delete(container);
  }
}

el('nav-custom-db').addEventListener('click',()=>selectView('custom-db'));
el('custom-db-create').addEventListener('click',()=>cdbDatabaseDialog());
el('custom-db-picker').addEventListener('change',event=>{
  cdbMonth=cdbMonthStart(seoulTodayDate());
  cdbShowDatabase(event.target.value).catch(error=>toast(error.message));
});

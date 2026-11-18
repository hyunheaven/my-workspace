"""Local-only template editor API; no central-server or AI endpoints in this PoC."""
from __future__ import annotations
from hashlib import sha256
import json
from os.path import normcase
import re
import ipaddress
from pathlib import Path
from uuid import uuid4
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlsplit
from unicodedata import normalize
from typing import Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .workspace_store import UUID_PATTERN, WorkspaceStore
from .custom_databases import CustomDatabaseStore, mount_custom_databases
from .storage import default_db_path
from .page_templates import template_blocks
from .page_database_views import mount_page_database_views

CATALOG_PATH=Path(__file__).with_name('catalog.json')
LIBRARY_CATALOG_PATH=Path(__file__).with_name('catalog_library.json')
PUBLIC_DIR=Path(__file__).resolve().parents[2] / 'apps' / 'local-client' / 'static'
MAX_BODY=64 * 1024
MAX_CANVAS_BODY=256 * 1024

PROJECT_STATUS=Literal['planned','active','on_hold','completed']
TASK_STATUS=Literal['todo','in_progress','blocked','done','archived']
PRIORITY=Literal['low','medium','high']

class CreateDoc(BaseModel):
    model_config=ConfigDict(extra='forbid')
    template_id: str = Field(min_length=1,max_length=100)
    title: str=Field(min_length=1,max_length=120)
    values: dict[str,str] = Field(default_factory=dict)
    parent_id: str | None = None

class UpdateDoc(BaseModel):
    model_config=ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=1)
    title: str=Field(min_length=1,max_length=120)
    values: dict[str,str]=Field(default_factory=dict)


# The page canvas is a separate safe editor, not HTML/Markdown execution.
BlockType = Literal['paragraph','heading_1','heading_2','bullet','todo','toggle','quote','code','divider','table',
                    'ordered_list','page_link']

class BlankPage(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title: str=Field(default='제목 없음',min_length=1,max_length=120)
    parent_id: str | None=None

class PageFromTemplate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    template_id: str = Field(min_length=1, max_length=100)
    request_id: str = Field(pattern=UUID_PATTERN)
    parent_id: str | None = Field(default=None, pattern=UUID_PATTERN)

class PageRevisionOperation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=1, le=2**63-1)

class DuplicatePage(PageRevisionOperation):
    request_id: str = Field(pattern=UUID_PATTERN)

class PagePropertiesUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_revision: int = Field(ge=0, le=2**63-1)
    theme: Literal['inherit','warm','sage','indigo','clay','dark','ocean','lavender','rose','slate','contrast'] = 'inherit'
    background: Literal['plain','paper','mint','mist','grid','ruled','graph','margin','cream','rosepaper'] | None = None
    tab_color: Literal['none','sage','ocean','indigo','lavender','rose','clay','gold','slate'] = 'none'
    tags: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode='after')
    def normalize_tags(self):
        if 'tags' not in self.model_fields_set:
            return self
        unique = {}
        for raw in self.tags:
            if len(raw) > 120 or not raw.isprintable():
                raise ValueError('Invalid page tag')
            label = ' '.join(normalize('NFKC', raw).strip().lstrip('#').split())
            if not 1 <= len(label) <= 32:
                raise ValueError('Page tags require 1 to 32 characters')
            unique.setdefault(label.casefold(), label)
        self.tags = list(unique.values())
        return self


def valid_block_text(value: str) -> bool:
    return not any(
        (ord(char) < 32 and char not in '\n\r\t') or 0xD800 <= ord(char) <= 0xDFFF
        for char in value
    )


class CanvasBlock(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id: str=Field(pattern=r'^[a-f0-9-]{36}$')
    type: BlockType
    content: str=Field(default='',max_length=4000)
    checked: bool=False
    depth: int=Field(default=0,ge=0,le=6,strict=True)

    def stored(self) -> dict[str, Any]:
        return self.model_dump(exclude={'depth'} if self.depth == 0 else None)

    @model_validator(mode='after')
    def validate_content(self):
        if not valid_block_text(self.content):
            raise ValueError('Invalid block characters')
        if self.type in ('ordered_list','page_link') and self.checked:
            raise ValueError('This block type cannot be checked')
        if self.type == 'page_link' and self.content and not re.fullmatch(UUID_PATTERN,self.content):
            raise ValueError('Page links require a local page ID')
        if self.type != 'table':
            return self
        if self.checked:
            raise ValueError('Table blocks cannot be checked')
        try:
            rows = json.loads(self.content)
        except (ValueError, RecursionError) as exc:
            raise ValueError('Expected table rows as JSON arrays') from exc
        if not isinstance(rows, list) or not 2 <= len(rows) <= 20:
            raise ValueError('Tables require 2 to 20 rows')
        if not isinstance(rows[0], list) or not 2 <= len(rows[0]) <= 8:
            raise ValueError('Tables require 2 to 8 columns')
        width = len(rows[0])
        for row in rows:
            if not isinstance(row, list) or len(row) != width:
                raise ValueError('Only rectangular tables are supported')
            if any(not isinstance(cell, str) or len(cell) > 256 or not valid_block_text(cell) for cell in row):
                raise ValueError('Table cells require plain text of up to 256 characters')
        return self

class CanvasContent(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title: str=Field(min_length=1,max_length=120)
    blocks: list[CanvasBlock]=Field(default_factory=list,max_length=120)

    @model_validator(mode='after')
    def validate_blocks(self):
        if sum(len(x.content) for x in self.blocks)>45000:
            raise ValueError('Page content is too long')
        ids=[b.id for b in self.blocks]
        if len(set(ids))!=len(ids):raise ValueError('Duplicate block IDs')
        previous=-1
        for block in self.blocks:
            if block.depth>previous+1:
                raise ValueError('Invalid block depth sequence')
            previous=block.depth
        return self

class CanvasUpdate(CanvasContent):
    expected_revision: int=Field(ge=1)

class CanvasImport(CanvasContent):
    parent_id: str | None=Field(default=None,pattern=UUID_PATTERN)

class MovePage(BaseModel):
    model_config=ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=1)
    parent_id: str | None = None

class CreateProject(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title: str=Field(min_length=1,max_length=120)
    description: str=Field(default='',max_length=4000)
    status: PROJECT_STATUS='planned'

class UpdateProject(CreateProject):
    expected_revision: int=Field(ge=1)

class TaskData(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title: str=Field(min_length=1,max_length=120)
    project_id: str | None=None
    document_id: str | None=None
    status: TASK_STATUS='todo'
    priority: PRIORITY='medium'
    due_on: str | None=None
    effort: float | None=Field(default=None,ge=0,le=1_000_000,allow_inf_nan=False,strict=True)
    labels: list[str]=Field(default_factory=list,max_length=20)
    flagged: bool=Field(default=False,strict=True)
    reference_url: str=Field(default='',max_length=2048)
    notes: str=Field(default='',max_length=8000)

class UpdateTask(TaskData):
    expected_revision: int=Field(ge=1)

class EventData(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title: str=Field(min_length=1,max_length=120)
    start_at: str=Field(min_length=10,max_length=40)
    end_at: str=Field(min_length=10,max_length=40)
    all_day: bool=True
    timezone: str=Field(default='Asia/Seoul',min_length=1,max_length=80)
    document_id: str | None=None
    task_id: str | None=None

class UpdateEvent(EventData):
    expected_revision: int=Field(ge=1)

def clean_text(value: str, *, name: str='Text') -> str:
    value=value.strip()
    if not value: raise HTTPException(422,f'{name} cannot be empty')
    if any(ord(c)<32 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise HTTPException(422,f'Invalid {name} characters')
    return value

def valid_date_optional(value: str | None) -> str | None:
    if value in (None,''):return None
    try:
        normalized=date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        raise HTTPException(422,'Invalid YYYY-MM-DD date')
    if normalized != value: raise HTTPException(422,'Date must use YYYY-MM-DD')
    return normalized

def validate_task(body: TaskData, *, updating: bool = False) -> dict[str, Any]:
    data = body.model_dump(exclude={'expected_revision'})
    data['title'] = clean_text(body.title, name='Task title')
    data['due_on'] = valid_date_optional(body.due_on)
    if data['due_on'] == date.max.isoformat():
        raise HTTPException(422, 'Task date must allow a calendar end date')
    if any((ord(c) < 32 and c not in '\r\n\t') or 0xD800 <= ord(c) <= 0xDFFF for c in body.notes):
        raise HTTPException(422, 'Invalid Task notes characters')
    labels = [clean_text(label, name='Task label') for label in body.labels]
    if any(len(label) > 40 or ',' in label for label in labels):
        raise HTTPException(422, 'Task labels must be at most 40 characters and contain no commas')
    data['labels'] = list(dict.fromkeys(labels))
    reference = body.reference_url.strip()
    if reference:
        try:
            if any(c.isspace() or ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in reference):
                raise ValueError('Invalid URL characters')
            parts = urlsplit(reference)
            if parts.scheme not in {'http', 'https'} or not parts.hostname or parts.username is not None:
                raise ValueError('Expected an HTTP(S) address without credentials')
            if parts.port == 0:
                raise ValueError('Invalid port')
        except ValueError:
            raise HTTPException(422, 'Reference must be an HTTP(S) URL without credentials') from None
    data['reference_url'] = reference
    if updating:
        for name in ('effort', 'labels', 'flagged', 'reference_url', 'notes'):
            if name not in body.model_fields_set:
                del data[name]
    return data

def validate_event(body:EventData) -> dict[str,Any]:
    title=clean_text(body.title,name='Event title')
    try:
        zone=ZoneInfo(body.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        # Windows Python may not ship an IANA tz database. Seoul uses UTC+09
        # for current/future dates; no tzdata package is downloaded at runtime.
        if body.timezone=='Asia/Seoul':
            zone=timezone(timedelta(hours=9))
        else:
            raise HTTPException(422,'IANA timezone unavailable on this host')
    if body.all_day:
        start=valid_date_optional(body.start_at)
        end=valid_date_optional(body.end_at)
        if start is None or end is None or end<=start:
            raise HTTPException(422,'All-day end date must be exclusive and later than start')
        if (date.fromisoformat(end)-date.fromisoformat(start)).days>366:
            raise HTTPException(422,'Calendar range exceeds one year')
        return {'title':title,'start_at':start,'end_at':end,'start_date':start,'end_date':end,
                'all_day':True,'timezone':body.timezone,'document_id':body.document_id,'task_id':body.task_id}
    try:
        start_dt=datetime.fromisoformat(body.start_at)
        end_dt=datetime.fromisoformat(body.end_at)
    except ValueError:
        raise HTTPException(422,'Timed events require ISO 8601 datetimes')
    if start_dt.tzinfo is None or end_dt.tzinfo is None or start_dt.utcoffset() is None or end_dt.utcoffset() is None:
        raise HTTPException(422,'Timed events require explicit UTC offsets')
    start_utc=start_dt.astimezone(timezone.utc)
    end_utc=end_dt.astimezone(timezone.utc)
    if end_utc<=start_utc or end_utc-start_utc>timedelta(days=366):
        raise HTTPException(422,'Invalid event time range')
    # The returned range uses local calendar dates; end_date is exclusive.
    local_first=start_utc.astimezone(zone).date()
    local_last=(end_utc-timedelta(microseconds=1)).astimezone(zone).date()
    return {'title':title,'start_at':start_utc.isoformat(),'end_at':end_utc.isoformat(),
            'start_date':local_first.isoformat(),'end_date':(local_last+timedelta(days=1)).isoformat(),
            'all_day':False,'timezone':body.timezone,'document_id':body.document_id,'task_id':body.task_id}

def verify_range(start: str,end: str):
    start_day=valid_date_optional(start);end_day=valid_date_optional(end)
    if not start_day or not end_day or end_day<=start_day:
        raise HTTPException(422,'Invalid calendar range')
    if (date.fromisoformat(end_day)-date.fromisoformat(start_day)).days>370:
        raise HTTPException(422,'Calendar query range too wide')
    return start_day,end_day

def ref_error(exc:ValueError):
    raise HTTPException(422,str(exc))

def valid_values(template: dict[str,Any], title: str, values: dict[str,str]) -> tuple[str,dict[str,str]]:
    title=title.strip()
    if not title: raise HTTPException(422,'Title cannot be blank')
    if any(ord(ch)<32 for ch in title): raise HTTPException(422,'Invalid title characters')
    fields={f['id']:f for f in template['fields']}
    if set(values)-set(fields): raise HTTPException(422,'Unknown template fields')
    clean={}
    for field_id, value in values.items():
        if not isinstance(value,str): raise HTTPException(422,'Only text values are allowed')
        f=fields[field_id]
        if len(value)>8192: raise HTTPException(422,'Field is too long')
        if any(ord(ch)<32 and ch not in '\n\t\r' for ch in value): raise HTTPException(422,'Invalid control characters')
        if f['type']=='select' and value and value not in f['options']:
            raise HTTPException(422,'Invalid selection')
        if f['type']=='date' and value:
            try: date.fromisoformat(value)
            except ValueError: raise HTTPException(422,'Invalid date')
        clean[field_id]=value
    for f in fields.values():
        if f.get('required') and not clean.get(f['id'],'').strip():
            raise HTTPException(422,f"Required field: {f['id']}")
    return title,clean


def create_app(db_path:Path | None = None) -> FastAPI:
    app=FastAPI(title='My Workspace Local Core PoC',version='1.3.0',docs_url=None,redoc_url=None,openapi_url=None)
    store=WorkspaceStore(db_path or default_db_path())
    custom_store = CustomDatabaseStore(store)
    draft_scope=sha256(normcase(str(store.path.resolve())).encode('utf-8')).hexdigest()
    catalog=json.loads(CATALOG_PATH.read_text(encoding='utf-8'))
    catalog.extend(json.loads(LIBRARY_CATALOG_PATH.read_text(encoding='utf-8')))
    templates={t['id']:t for t in catalog}
    if len(templates) != len(catalog):
        raise ValueError('Duplicate ID in bundled template catalogs')
    catalog_index=[{key:value for key,value in template.items() if key!='blocks'} for template in catalog]

    @app.middleware('http')
    async def local_security(request:Request,call_next):
        peer=request.client.host if request.client else ''
        try:
            loopback=ipaddress.ip_address(peer).is_loopback
        except ValueError:
            loopback=False
        if not loopback:
            return JSONResponse({'detail':'Local connections only'},status_code=403)
        host=request.headers.get('host','').split(':')[0].lower()
        if host not in ('127.0.0.1','localhost'):
            return JSONResponse({'detail':'Local hostname required'},status_code=403)
        origin=request.headers.get('origin')
        if origin:
            parts=urlsplit(origin)
            if parts.scheme!='http' or parts.hostname!=host or parts.port != request.url.port:
                return JSONResponse({'detail':'Untrusted origin'},status_code=403)
        if request.method not in ('GET','HEAD'):
            if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':
                return JSONResponse({'detail':'JSON only'},status_code=415)
            if request.headers.get('x-eaw-request')!='local-template-editor':
                return JSONResponse({'detail':'Missing local request marker'},status_code=403)
            body=await request.body()
            path = request.url.path
            is_canvas_write = request.method == 'PUT' and re.fullmatch(r'/api/v1/pages/[^/]+/content', path)
            is_import = request.method == 'POST' and (
                path == '/api/v1/pages/import' or re.fullmatch(r'/api/v1/databases/[^/]+/records/batch', path)
            )
            if len(body)>(MAX_CANVAS_BODY if is_canvas_write or is_import else MAX_BODY):
                return JSONResponse({'detail':'Request too large'},status_code=413)
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=(), display-capture=(), autoplay=()'
        response.headers['Content-Security-Policy']=("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
                    "img-src 'none'; media-src 'none'; object-src 'none'; frame-src 'none'; frame-ancestors 'none'; "
                    "form-action 'none'; base-uri 'none'")
        return response

    @app.get('/api/v1/health')
    def health(): return {'status':'ok','mode':'local_private','version':app.version,'ai_enabled':False,
                          'sharing_enabled':False,'draft_scope':draft_scope}

    @app.get('/api/v1/templates')
    def get_templates(department:str='',job_family:str='',job_role:str='',section:str='',q:str='',collection:str=''):
        if len(q)>120: raise HTTPException(422,'Search query is too long')
        needle=q.strip().casefold()
        results=[t for t in catalog_index if (not department or t['department']==department) and
                 (not job_family or t['job_family']==job_family) and (not job_role or t['job_role']==job_role) and
                 (not section or t.get('section')==section) and
                 (not collection or t.get('collection')==collection) and
                 (not needle or needle in ' '.join((t['name'],t['description'],t['department'],t['job_family'],
                  t['job_role'],t.get('collection',''),*t.get('tags',()))).casefold())]
        return {'items':results,'total':len(results)}

    @app.get('/api/v1/templates/{template_id}/preview')
    def get_template_preview(template_id: str):
        template = templates.get(template_id)
        if template is None:
            raise HTTPException(404, 'Template not found')
        return {'id': template_id, 'title': template['name'], 'blocks': template_blocks(template)}

    @app.get('/api/v1/template-catalog/stats')
    def catalog_stats():
        from collections import Counter
        return {'total':len(catalog),
                'by_department':dict(sorted(Counter(t['department'] for t in catalog).items())),
                'by_section':dict(sorted(Counter(t['section'] for t in catalog).items())),
                'source_type':'project_original', 'third_party_imported':0}

    @app.get('/api/v1/documents')
    def get_documents(q:str=''):
        return {'items':store.all_docs(q[:120])}

    @app.get('/api/v1/search/pages')
    def search_pages(q: str = Query(default='', max_length=120), tag: str = Query(default='', max_length=32)):
        return {'items': store.search_pages(q, tag=tag)}

    @app.get('/api/v1/search')
    def search_workspace(q: str = Query(default='', max_length=120), tag: str = Query(default='', max_length=32)):
        return {
            'pages': store.search_pages(q, tag=tag),
            'tasks': [] if tag.strip() else store.search_tasks(q),
            'databases': [] if tag.strip() else custom_store.search(q),
        }

    @app.get('/api/v1/page-tags')
    def get_page_tags():
        return {'items': store.page_tags()}

    @app.post('/api/v1/documents',status_code=201)
    def create_document(body:CreateDoc):
        template=templates.get(body.template_id)
        if template is None: raise HTTPException(404,'Template not found')
        title,values=valid_values(template,body.title,body.values)
        result=store.create_doc(str(uuid4()),template['id'],template['version'],title,values,body.parent_id)
        if result.get('error'): raise HTTPException(422,'Parent page does not exist')
        return result

    @app.get('/api/v1/documents/{document_id}')
    def get_document(document_id:str):
        if not re.fullmatch(r'[a-f0-9-]{36}',document_id): raise HTTPException(404,'Document not found')
        doc=store.get_doc(document_id)
        if doc is None: raise HTTPException(404,'Document not found')
        return doc

    @app.put('/api/v1/documents/{document_id}')
    def update_document(document_id:str,body:UpdateDoc):
        current=store.get_doc(document_id)
        if current is None: raise HTTPException(404,'Document not found')
        template=templates.get(current['template_id'])
        if template is None: raise HTTPException(500,'Missing template definition')
        title,values=valid_values(template,body.title,body.values)
        state,doc=store.update_doc(document_id,body.expected_revision,title,values)
        if state=='not_found': raise HTTPException(404,'Document not found')
        if state=='conflict': raise HTTPException(409,'Document was modified. Reload before saving.')
        if state=='canvas_only': raise HTTPException(409,'This page is edited through the page canvas')
        return doc


    # Blank pages are independent from the bundled template catalog.
    @app.post('/api/v1/pages',status_code=201)
    def create_blank_page(body:BlankPage):
        result=store.create_doc(str(uuid4()),'__blank_page__',1,
                                clean_text(body.title,name='Page title'),{},body.parent_id)
        if result.get('error'):raise HTTPException(422,'Parent page does not exist')
        return store.get_canvas(result['id'])

    @app.post('/api/v1/pages/from-template', status_code=201)
    def create_page_from_template(body: PageFromTemplate, response: Response):
        template = templates.get(body.template_id)
        if template is None:
            raise HTTPException(404, 'Template not found')
        state, page = store.create_template_page(
            template['id'], template['version'], template['name'], body.parent_id,
            body.request_id, template_blocks(template),
            PagePropertiesUpdate(expected_revision=0, tags=template.get('tags', [])).tags,
        )
        if state == 'parent_not_found':
            raise HTTPException(422, 'Parent page not found')
        if state == 'not_found':
            raise HTTPException(404, 'Page is in the trash')
        if state == 'conflict':
            raise HTTPException(409, 'Request ID belongs to another template or parent')
        if state == 'replayed':
            response.status_code = 200
        return page

    @app.post('/api/v1/pages/import', status_code=201)
    def import_local_page(body: CanvasImport):
        page_id = str(uuid4())
        blocks = [block.stored() for block in body.blocks]
        if any(not re.fullmatch(UUID_PATTERN, block['id']) for block in blocks):
            raise HTTPException(422, 'New block IDs must be canonical UUIDs')
        result = store.create_doc(page_id, '__blank_page__', 1,
                                  clean_text(body.title, name='Page title'), {}, body.parent_id,
                                  blocks=blocks)
        if result.get('error') == 'parent_not_found':
            raise HTTPException(422, 'Parent page not found')
        if result.get('error') == 'block_conflict':
            raise HTTPException(409, 'A block ID belongs to another page')
        return store.get_canvas(page_id)

    @app.get('/api/v1/pages/{page_id}/content')
    def get_page_canvas(page_id:str):
        page=store.get_canvas(page_id)
        if page is None:raise HTTPException(404,'Page not found')
        return page

    @app.patch('/api/v1/pages/{page_id}/properties')
    def update_page_properties(page_id: str, body: PagePropertiesUpdate):
        changes = body.model_dump(exclude_unset=True, exclude={'expected_revision'})
        state, properties = store.update_page_properties(page_id, body.expected_revision, changes)
        if state == 'not_found':
            raise HTTPException(404, '페이지를 찾을 수 없습니다.')
        if state == 'conflict':
            raise HTTPException(409, '다른 창에서 페이지 속성을 변경했습니다. 현재 설정을 다시 불러왔습니다.')
        return properties

    @app.post('/api/v1/pages/{page_id}/duplicate', status_code=201)
    def duplicate_page(page_id: str, body: DuplicatePage, response: Response):
        state, page = store.duplicate_page(page_id, body.expected_revision, body.request_id)
        if state == 'not_found':
            raise HTTPException(404, '페이지를 찾을 수 없습니다.')
        if state == 'conflict':
            raise HTTPException(409, '페이지가 변경됐거나 같은 복제 키가 이미 사용됐습니다.')
        if state == 'replayed':
            response.status_code = 200
        return page

    @app.post('/api/v1/pages/{page_id}/history/{revision}/restore')
    def restore_page_revision(page_id: str, revision: int, body: PageRevisionOperation):
        if not 1 <= revision <= 2**63-1:
            raise HTTPException(404, '저장된 이력을 찾을 수 없습니다.')
        state, page = store.restore_page_revision(page_id, body.expected_revision, revision)
        if state in ('not_found', 'revision_not_found'):
            raise HTTPException(404, '저장된 이력을 찾을 수 없습니다.')
        if state == 'conflict':
            raise HTTPException(409, '다른 창에서 변경된 페이지입니다. 다시 열어 확인해 주세요.')
        if state == 'block_conflict':
            raise HTTPException(409, '다른 페이지의 블록과 충돌해 복원하지 못했습니다.')
        return page

    @app.put('/api/v1/pages/{page_id}/content')
    def save_page_canvas(page_id:str,body:CanvasUpdate):
        title=clean_text(body.title,name='Page title')
        state,data=store.update_canvas(page_id,body.expected_revision,title,
                                     [b.stored() for b in body.blocks])
        if state=='not_found':raise HTTPException(404,'Page not found')
        if state=='conflict':raise HTTPException(409,'Page changed; reload and review your edits')
        if state=='block_conflict':raise HTTPException(409,'A block ID belongs to another page')
        if state=='invalid_block_id':raise HTTPException(422,'New block IDs must be canonical UUIDs')
        return data

    @app.get('/api/v1/pages/{page_id}/history')
    def list_page_history(page_id: str, before_revision: int | None = Query(default=None, ge=1, le=2**63-1)):
        items = store.list_page_history(page_id, before_revision)
        if items is None:
            raise HTTPException(404, 'Page not found')
        return {'items': items}

    @app.get('/api/v1/pages/{page_id}/history/{revision}')
    def get_page_history(page_id: str, revision: int):
        if not 0 < revision <= 2**63-1:
            raise HTTPException(404, 'Page revision not found')
        item = store.get_page_history(page_id, revision)
        if item is None:
            raise HTTPException(404, 'Page revision not found')
        return item

    # Page Tree: only local-private pages; moves reject cycles and stale revisions.
    @app.get('/api/v1/pages/tree')
    def page_tree():
        return {'items':store.all_docs(for_tree=True),'scope':'local_private'}

    @app.get('/api/v1/pages/trash')
    def list_page_trash():
        return {'items': store.list_trash()}

    @app.post('/api/v1/pages/{page_id}/trash')
    def trash_page(page_id: str, body: PageRevisionOperation):
        state = store.trash_page(page_id, body.expected_revision)
        if state == 'not_found':
            raise HTTPException(404, '페이지를 찾을 수 없습니다.')
        if state == 'conflict':
            raise HTTPException(409, '변경된 페이지입니다. 다시 열어 확인해 주세요.')
        return {'status': 'trashed'}

    @app.post('/api/v1/pages/{page_id}/restore')
    def restore_trashed_page(page_id: str, body: PageRevisionOperation):
        state = store.restore_trashed_page(page_id, body.expected_revision)
        if state == 'not_found':
            raise HTTPException(404, '휴지통에서 페이지를 찾을 수 없습니다.')
        if state == 'parent_in_trash':
            raise HTTPException(409, '상위 페이지를 먼저 복원해 주세요.')
        if state == 'conflict':
            raise HTTPException(409, '휴지통 목록이 변경됐습니다. 다시 열어 확인해 주세요.')
        return {'status': 'restored'}

    @app.put('/api/v1/pages/{page_id}/move')
    def move_page(page_id:str,body:MovePage):
        state,data=store.move_page(page_id,body.expected_revision,body.parent_id)
        if state=='not_found':raise HTTPException(404,'Page not found')
        if state=='parent_not_found':raise HTTPException(422,'Parent page not found')
        if state=='cycle':raise HTTPException(422,'Page nesting cycle prohibited')
        if state=='conflict':raise HTTPException(409,'Page modified elsewhere')
        return data

    @app.get('/api/v1/projects')
    def list_projects():return {'items':store.list_projects()}

    @app.post('/api/v1/projects',status_code=201)
    def create_project(body:CreateProject):
        return store.create_project(clean_text(body.title,name='Project title'),body.description,body.status)

    @app.put('/api/v1/projects/{project_id}')
    def update_project(project_id:str,body:UpdateProject):
        state,item=store.update_project(project_id,body.expected_revision,clean_text(body.title,name='Project title'),body.description,body.status)
        if state=='not_found':raise HTTPException(404,'Project not found')
        if state=='conflict':raise HTTPException(409,'Project changed; reload')
        return item

    @app.get('/api/v1/tasks')
    def list_tasks(project_id:str=''):
        return {'items':store.tasks(project_id or None)}

    @app.post('/api/v1/tasks',status_code=201)
    def create_task(body:TaskData):
        data=validate_task(body)
        try:return store.create_task(**data)
        except ValueError as e:ref_error(e)

    @app.get('/api/v1/tasks/{task_id}')
    def get_task(task_id:str):
        item=store.task(task_id)
        if item is None:raise HTTPException(404,'Task not found')
        return item

    @app.put('/api/v1/tasks/{task_id}')
    def update_task(task_id:str,body:UpdateTask):
        data=validate_task(body, updating=True)
        try:state,item=store.update_task(task_id,body.expected_revision,**data)
        except ValueError as e:ref_error(e)
        if state=='not_found':raise HTTPException(404,'Task not found')
        if state=='conflict':raise HTTPException(409,'Task changed; reload')
        return item

    @app.get('/api/v1/calendar/feed')
    def calendar_feed(start:str,end:str):
        start,end=verify_range(start,end)
        return {'items':store.calendar_feed(start,end),'scope':'local_private'}

    @app.get('/api/v1/calendar/events')
    def list_calendar_events(start:str,end:str):
        start,end=verify_range(start,end)
        return {'items':store.events_between(start,end)}

    @app.post('/api/v1/calendar/events',status_code=201)
    def create_event(body:EventData):
        try:return store.create_event(**validate_event(body))
        except ValueError as e:ref_error(e)

    @app.get('/api/v1/calendar/events/{event_id}')
    def get_calendar_event(event_id:str):
        event=store.event(event_id)
        if event is None:raise HTTPException(404,'Event not found')
        return event

    @app.put('/api/v1/calendar/events/{event_id}')
    def update_event(event_id:str,body:UpdateEvent):
        try:state,item=store.update_event(event_id,body.expected_revision,**validate_event(body))
        except ValueError as e:ref_error(e)
        if state=='not_found':raise HTTPException(404,'Event not found')
        if state=='conflict':raise HTTPException(409,'Event changed; reload')
        return item

    @app.get('/')
    def ui(): return FileResponse(PUBLIC_DIR/'index.html',media_type='text/html')

    @app.get('/assets/{filename}')
    def assets(filename:str):
        if filename not in ('app.js','app.css','pagecanvas.js','themes.js','themes.css',
                            'custom-databases.js','custom-databases.css','workspace-transfer.js',
                            'page-database-views.js','workspace-tools.css'):
            raise HTTPException(404,'Not found')
        return FileResponse(PUBLIC_DIR/filename,media_type='text/javascript' if filename.endswith('.js') else 'text/css')
    mount_page_database_views(app, store)
    mount_custom_databases(app, custom_store)
    return app

app=create_app()

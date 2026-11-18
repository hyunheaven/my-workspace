"""Local-first structured data. No network, media, shared persistence, or external integrations."""
from __future__ import annotations
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
import json
import re
import sqlite3
from typing import Any
from unicodedata import normalize
from uuid import uuid4
from .storage import LocalStore

UTC = timezone.utc
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
TASK_PROPERTY_DEFAULTS: dict[str, Any] = {
    'effort': None, 'labels': '[]', 'flagged': 0, 'reference_url': '', 'notes': '',
}

def now_utc() -> str:
    return datetime.now(UTC).isoformat()

class WorkspaceStore(LocalStore):
    def __init__(self, path: Path):
        super().__init__(path)
        with self.conn() as db:
            db.executescript('''
                BEGIN IMMEDIATE;
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL CHECK(status IN ('planned','active','on_hold','completed')),
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT REFERENCES projects(id),
                    document_id TEXT REFERENCES documents(id),
                    title TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('todo','in_progress','blocked','done','archived')),
                    priority TEXT NOT NULL CHECK(priority IN ('low','medium','high')),
                    due_on TEXT,
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_on);
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    all_day INTEGER NOT NULL CHECK(all_day IN (0,1)),
                    timezone TEXT NOT NULL,
                    document_id TEXT REFERENCES documents(id),
                    task_id TEXT REFERENCES tasks(id),
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_event_dates ON calendar_events(start_date,end_date);
                CREATE TABLE IF NOT EXISTS page_blocks (
                    id TEXT PRIMARY KEY,
                    page_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    block_type TEXT NOT NULL CHECK(block_type IN
                        ('paragraph','heading_1','heading_2','bullet','todo','toggle','quote','code','divider')),
                    content TEXT NOT NULL DEFAULT '',
                    checked INTEGER NOT NULL DEFAULT 0 CHECK(checked IN (0,1)),
                    UNIQUE(page_id,position)
                );
                CREATE INDEX IF NOT EXISTS idx_page_blocks ON page_blocks(page_id,position);
            ''')
            document_columns = {row['name'] for row in db.execute('PRAGMA table_info(documents)')}
            task_columns = {row['name'] for row in db.execute('PRAGMA table_info(tasks)')}
            for name, definition in {
                'effort': 'REAL',
                'labels': "TEXT NOT NULL DEFAULT '[]'",
                'flagged': 'INTEGER NOT NULL DEFAULT 0 CHECK(flagged IN (0,1))',
                'reference_url': "TEXT NOT NULL DEFAULT ''",
                'notes': "TEXT NOT NULL DEFAULT ''",
            }.items():
                if name not in task_columns:
                    db.execute(f'ALTER TABLE tasks ADD COLUMN {name} {definition}')
            if 'parent_id' not in document_columns:
                db.execute('ALTER TABLE documents ADD COLUMN parent_id TEXT REFERENCES documents(id)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_docs_parent ON documents(parent_id)')
            columns = {row['name'] for row in db.execute('PRAGMA table_info(page_blocks)')}
            if 'is_table' not in columns:
                # Use the existing paragraph storage slot to retain the v0.11 SQLite CHECK.
                db.execute("""ALTER TABLE page_blocks ADD COLUMN is_table INTEGER NOT NULL DEFAULT 0
                              CHECK(is_table IN (0,1) AND
                                    (is_table=0 OR (block_type='paragraph' AND checked=0)))""")
            if 'extension_type' not in columns:
                db.execute("""ALTER TABLE page_blocks ADD COLUMN extension_type TEXT
                              CHECK(extension_type IS NULL OR (
                                  extension_type IN ('ordered_list','page_link') AND
                                  is_table=0 AND block_type='paragraph' AND checked=0))""")
            if 'depth' not in columns:
                db.execute('ALTER TABLE page_blocks ADD COLUMN depth INTEGER NOT NULL DEFAULT 0 CHECK(depth BETWEEN 0 AND 6)')
            db.execute('''CREATE TABLE IF NOT EXISTS page_template_requests (
                request_id TEXT PRIMARY KEY NOT NULL,
                page_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                template_id TEXT NOT NULL,
                requested_parent_id TEXT
            )''')
            db.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_template_requests_page
                          ON page_template_requests(page_id)''')
            db.execute('''CREATE TABLE IF NOT EXISTS page_duplicate_requests (
                request_id TEXT PRIMARY KEY NOT NULL,
                source_page_id TEXT NOT NULL,
                source_revision INTEGER NOT NULL,
                page_id TEXT NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
                from_template INTEGER NOT NULL CHECK(from_template IN (0,1))
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS page_history (
                page_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                revision INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                snapshot TEXT NOT NULL,
                PRIMARY KEY(page_id, revision)
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS page_properties (
                page_id TEXT PRIMARY KEY NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                theme TEXT NOT NULL DEFAULT 'inherit',
                background TEXT,
                tab_color TEXT NOT NULL DEFAULT 'none',
                tags TEXT NOT NULL DEFAULT '[]',
                revision INTEGER NOT NULL DEFAULT 1
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS page_trash (
                page_id TEXT PRIMARY KEY NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                root_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                trashed_at TEXT NOT NULL
            )''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_page_trash_root ON page_trash(root_id)')
            db.execute('''CREATE VIEW IF NOT EXISTS active_documents AS
                          SELECT d.* FROM documents AS d WHERE NOT EXISTS
                          (SELECT 1 FROM page_trash AS t WHERE t.page_id=d.id)''')

    def all_docs(self, query: str = '', *, for_tree: bool = False) -> list[dict[str,Any]]:
        sql = '''SELECT d.id,d.parent_id,d.template_id,d.template_version,d.title,d.revision,
                        d.scope,d.created_at,d.updated_at,p.tab_color
                 FROM active_documents AS d LEFT JOIN page_properties AS p ON p.page_id=d.id'''
        args: tuple[Any,...]=()
        if query:
            sql += " WHERE title LIKE ? ESCAPE '\\'"
            args = ('%'+query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%',)
        sql += ' ORDER BY created_at ASC,id ASC'
        if not for_tree:
            sql += ' LIMIT 500'
        with self.conn() as db:
            return [dict(x) for x in db.execute(sql,args)]

    def search_pages(self, query: str, limit: int = 100, *, tag: str = '') -> list[dict[str, Any]]:
        needle = normalize('NFKC', query.strip()).casefold()
        tag_key = normalize('NFKC', tag.strip()).casefold()
        if not (needle or tag_key) or limit <= 0:
            return []

        def text_matches(value: str) -> bool:
            return needle in normalize('NFKC', value).casefold()

        def fields_match(raw_values: str) -> bool:
            return any(text_matches(value) for value in json.loads(raw_values).values())

        def block_matches(content: str, is_table: int) -> bool:
            if not is_table:
                return text_matches(content)
            return any(text_matches(cell) for row in json.loads(content) for cell in row)

        def tag_matches(raw_tags: str | None, exact: int) -> bool:
            if not raw_tags:
                return False
            tags = json.loads(raw_tags)
            if exact:
                return any(normalize('NFKC', value).casefold() == tag_key for value in tags)
            return any(text_matches(value) for value in tags)

        with self.conn() as db:
            db.create_function('page_text_matches', 1, text_matches)
            db.create_function('page_fields_match', 1, fields_match)
            db.create_function('page_block_matches', 2, block_matches)
            db.create_function('page_tag_matches', 2, tag_matches)
            rows = db.execute(
                '''SELECT d.id,d.parent_id,d.template_id,d.template_version,d.title,d.revision,
                          d.scope,d.created_at,d.updated_at,p.tab_color
                   FROM active_documents AS d LEFT JOIN page_properties AS p ON p.page_id=d.id
                   WHERE (?='' OR page_tag_matches(p.tags,1)) AND
                    (?='' OR page_text_matches(d.title) OR page_fields_match(d.field_values)
                       OR page_tag_matches(p.tags,0) OR EXISTS (
                       SELECT 1 FROM page_blocks AS b WHERE b.page_id=d.id
                           AND page_block_matches(b.content,b.is_table)
                   ))
                   ORDER BY d.updated_at DESC,d.id LIMIT ?''',
                (tag_key, needle, min(limit, 100)),
            )
            return [dict(row) for row in rows]

    def search_tasks(self, query: str) -> list[dict[str, Any]]:
        needle = normalize('NFKC', query.strip()).casefold()
        if not needle:
            return []

        def task_matches(title: str, notes: str, labels: str) -> bool:
            return any(needle in normalize('NFKC', text).casefold()
                       for text in (title, notes, *json.loads(labels)))

        with self.conn() as db:
            db.create_function('task_matches', 3, task_matches)
            rows = db.execute('''SELECT id,title,status,due_on,updated_at FROM tasks
                                 WHERE task_matches(title,notes,labels)
                                 ORDER BY updated_at DESC,id LIMIT 100''')
            return [dict(row) for row in rows]

    def get_doc(self, doc_id: str) -> dict[str, Any] | None:
        with self.conn() as db:
            row = db.execute('SELECT * FROM active_documents WHERE id=?', (doc_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        result['values'] = json.loads(result.pop('field_values'))
        return result

    def list_trash(self) -> list[dict[str, Any]]:
        with self.conn() as db:
            rows = db.execute('''SELECT roots.page_id AS id,d.title,d.parent_id,d.revision,
                                        roots.trashed_at,COUNT(members.page_id) AS page_count
                                 FROM page_trash AS roots
                                 JOIN documents AS d ON d.id=roots.page_id
                                 JOIN page_trash AS members ON members.root_id=roots.page_id
                                 WHERE roots.page_id=roots.root_id
                                 GROUP BY roots.page_id
                                 ORDER BY roots.trashed_at DESC,roots.page_id''')
            return [dict(row) for row in rows]

    def trash_page(self, page_id: str, expected_revision: int) -> str:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            root = db.execute('SELECT revision FROM active_documents WHERE id=?', (page_id,)).fetchone()
            if root is None:
                return 'not_found'
            if root['revision'] != expected_revision:
                return 'conflict'
            db.execute('''WITH RECURSIVE subtree(id) AS (
                              SELECT id FROM active_documents WHERE id=?
                              UNION
                              SELECT d.id FROM active_documents AS d JOIN subtree AS s ON d.parent_id=s.id
                          )
                          INSERT INTO page_trash(page_id,root_id,trashed_at)
                          SELECT id,?,? FROM subtree''', (page_id, page_id, now_utc()))
            db.execute('''UPDATE documents SET revision=revision+1
                          WHERE id IN (SELECT page_id FROM page_trash WHERE root_id=?)''', (page_id,))
            return 'updated'

    def restore_trashed_page(self, page_id: str, expected_revision: int) -> str:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            root = db.execute('''SELECT d.revision,d.parent_id FROM documents AS d
                                 JOIN page_trash AS t ON t.page_id=d.id
                                 WHERE t.root_id=d.id AND d.id=?''', (page_id,)).fetchone()
            if root is None:
                return 'not_found'
            if root['revision'] != expected_revision:
                return 'conflict'
            if root['parent_id'] and not db.execute('SELECT 1 FROM active_documents WHERE id=?',
                                                    (root['parent_id'],)).fetchone():
                return 'parent_in_trash'
            db.execute('DELETE FROM page_trash WHERE root_id=?', (page_id,))
            return 'updated'

    @staticmethod
    def _read_properties(db: sqlite3.Connection, page_id: str) -> dict[str, Any]:
        row = db.execute('SELECT theme,background,tab_color,tags,revision FROM page_properties WHERE page_id=?',
                         (page_id,)).fetchone()
        if not row:
            return {'theme': 'inherit', 'background': None, 'tab_color': 'none', 'tags': [], 'revision': 0}
        result = dict(row)
        result['tags'] = json.loads(result['tags'])
        return result

    def update_page_properties(
        self, page_id: str, revision: int, changes: dict[str, Any],
    ) -> tuple[str, dict[str, Any] | None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM active_documents WHERE id=?', (page_id,)).fetchone():
                return 'not_found', None
            current = self._read_properties(db, page_id)
            if current['revision'] != revision:
                return 'conflict', current
            updated = {**current, **changes}
            if updated == current:
                return 'updated', current
            updated['revision'] += 1
            db.execute('''INSERT INTO page_properties(page_id,theme,background,tab_color,tags,revision)
                          VALUES(?,?,?,?,?,?) ON CONFLICT(page_id) DO UPDATE SET
                             theme=excluded.theme,background=excluded.background,tab_color=excluded.tab_color,
                             tags=excluded.tags,revision=excluded.revision''',
                       (page_id, updated['theme'], updated['background'], updated['tab_color'],
                        json.dumps(updated['tags'], ensure_ascii=False), updated['revision']))
            return 'updated', updated

    def page_tags(self) -> list[dict[str, Any]]:
        tags: dict[str, dict[str, Any]] = {}
        with self.conn() as db:
            for row in db.execute('''SELECT p.tags FROM page_properties AS p
                                     JOIN active_documents AS d ON d.id=p.page_id ORDER BY p.rowid'''):
                for label in json.loads(row['tags']):
                    key = normalize('NFKC', label).casefold()
                    entry = tags.setdefault(key, {'label': label, 'count': 0})
                    entry['count'] += 1
        return [tags[key] for key in sorted(tags)]

    def create_doc(
        self, doc_id: str, template_id: str, version: int, title: str,
        values: dict[str, str], parent_id: str | None = None, *,
        blocks: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            if parent_id and not db.execute('SELECT 1 FROM active_documents WHERE id=?',(parent_id,)).fetchone():
                return {'error':'parent_not_found'}
            if blocks and self._has_foreign_block(db, doc_id, blocks):
                return {'error': 'block_conflict'}
            self._insert_doc(db, doc_id, template_id, version, title, values, parent_id)
            if blocks:
                self._write_blocks(db, doc_id, blocks)
            created = self._read_canvas(db, doc_id)
            assert created is not None
            self._record_history(db, created)
            return self._doc_payload(created)

    @staticmethod
    def _doc_payload(page: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in page.items() if key not in ('blocks', 'from_template', 'properties')}

    @staticmethod
    def _insert_doc(
        db: sqlite3.Connection, doc_id: str, template_id: str, version: int,
        title: str, values: dict[str, str], parent_id: str | None,
    ) -> None:
        now = now_utc()
        db.execute('''INSERT INTO documents(
                          id,parent_id,template_id,template_version,title,field_values,
                          revision,scope,created_at,updated_at
                      ) VALUES(?,?,?,?,?,?,1,'local_private',?,?)''',
                   (doc_id,parent_id,template_id,version,title,json.dumps(values,ensure_ascii=False),now,now))

    def create_template_page(
        self, template_id: str, version: int, title: str, parent_id: str | None,
        request_id: str, blocks: list[dict[str, Any]], tags: list[str],
    ) -> tuple[str, dict[str, Any] | None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            request = db.execute(
                'SELECT page_id,template_id,requested_parent_id FROM page_template_requests WHERE request_id=?',
                (request_id,),
            ).fetchone()
            if request:
                if (request['template_id'], request['requested_parent_id']) != (template_id, parent_id):
                    return 'conflict', None
                page = self._read_canvas(db, request['page_id'])
                return ('replayed', page) if page else ('not_found', None)
            if parent_id and not db.execute('SELECT 1 FROM active_documents WHERE id=?', (parent_id,)).fetchone():
                return 'parent_not_found', None
            page_id = str(uuid4())
            self._insert_doc(db, page_id, template_id, version, title, {}, parent_id)
            self._write_blocks(db, page_id, blocks)
            if tags:
                db.execute('INSERT INTO page_properties(page_id,tags) VALUES(?,?)',
                           (page_id, json.dumps(tags, ensure_ascii=False)))
            db.execute(
                'INSERT INTO page_template_requests(request_id,page_id,template_id,requested_parent_id) VALUES(?,?,?,?)',
                (request_id, page_id, template_id, parent_id),
            )
            created = self._read_canvas(db, page_id)
            assert created is not None
            self._record_history(db, created)
            return 'created', created

    def duplicate_page(
        self, page_id: str, expected_revision: int, request_id: str,
    ) -> tuple[str, dict[str, Any] | None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            request = db.execute(
                '''SELECT page_id,source_page_id,source_revision
                   FROM page_duplicate_requests WHERE request_id=?''',
                (request_id,),
            ).fetchone()
            if request:
                if (request['source_page_id'], request['source_revision']) != (page_id, expected_revision):
                    return 'conflict', None
                page = self._read_canvas(db, request['page_id'])
                return ('replayed', page) if page else ('not_found', None)

            source = self._read_canvas(db, page_id)
            if source is None:
                return 'not_found', None
            if source['revision'] != expected_revision:
                return 'conflict', None

            duplicate_id = str(uuid4())
            suffix = ' (복제본)'
            title = source['title'][:120 - len(suffix)].rstrip() + suffix
            self._insert_doc(
                db, duplicate_id, source['template_id'], source['template_version'],
                title, source['values'], source['parent_id'],
            )
            self._write_blocks(
                db, duplicate_id, [{**block, 'id': str(uuid4())} for block in source['blocks']],
            )
            db.execute('''INSERT INTO page_properties(page_id,theme,background,tab_color,tags,revision)
                          SELECT ?,theme,background,tab_color,tags,1 FROM page_properties WHERE page_id=?''',
                       (duplicate_id, page_id))
            db.execute(
                '''INSERT INTO page_duplicate_requests(request_id,source_page_id,source_revision,page_id,from_template)
                   VALUES(?,?,?,?,?)''',
                (request_id, page_id, expected_revision, duplicate_id, int(source['from_template'])),
            )
            duplicate = self._read_canvas(db, duplicate_id)
            assert duplicate is not None
            self._record_history(db, duplicate)
            return 'created', duplicate

    def move_page(self, doc_id: str, expected_revision: int, parent_id: str|None) -> tuple[str,dict[str,Any]|None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            old=self._read_canvas(db, doc_id)
            if not old: return 'not_found',None
            if old['revision']!=expected_revision: return 'conflict',None
            if parent_id:
                if parent_id==doc_id: return 'cycle',None
                if not db.execute('SELECT 1 FROM active_documents WHERE id=?',(parent_id,)).fetchone():
                    return 'parent_not_found',None
                pointer=parent_id
                visited={doc_id}
                while pointer is not None:
                    if pointer in visited: return 'cycle',None
                    visited.add(pointer)
                    row=db.execute('SELECT parent_id FROM documents WHERE id=?',(pointer,)).fetchone()
                    pointer=row['parent_id'] if row else None
            self._record_history(db, old)
            db.execute('UPDATE documents SET parent_id=?,revision=revision+1,updated_at=? WHERE id=?',
                       (parent_id,now_utc(),doc_id))
            moved = self._read_canvas(db, doc_id)
            assert moved is not None
            self._record_history(db, moved)
            return 'updated', self._doc_payload(moved)

    def update_doc(
        self, doc_id: str, expected_revision: int, title: str, values: dict[str, str],
    ) -> tuple[str, dict[str, Any] | None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            current = self._read_canvas(db, doc_id)
            if current is None:
                return 'not_found', None
            if current['from_template']:
                return 'canvas_only', None
            if current['revision'] != expected_revision:
                return 'conflict', None
            self._record_history(db, current)
            db.execute('''UPDATE documents SET title=?,field_values=?,revision=revision+1,
                          updated_at=? WHERE id=?''',
                       (title, json.dumps(values, ensure_ascii=False), now_utc(), doc_id))
            updated = self._read_canvas(db, doc_id)
            assert updated is not None
            self._record_history(db, updated)
            return 'updated', self._doc_payload(updated)

    def list_projects(self):
        with self.conn() as db:
            return [dict(x) for x in db.execute('SELECT * FROM projects ORDER BY updated_at DESC LIMIT 300')]

    def project(self, project_id: str):
        with self.conn() as db:
            row=db.execute('SELECT * FROM projects WHERE id=?',(project_id,)).fetchone()
            return dict(row) if row else None

    def create_project(self,title:str,description:str,status:str):
        ident=str(uuid4()); now=now_utc()
        with self.conn() as db:
            db.execute('INSERT INTO projects VALUES(?,?,?,?,1,?,?)',(ident,title,description,status,now,now))
        return self.project(ident)

    def update_project(self,ident:str,expected_revision:int,title:str,description:str,status:str):
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT revision FROM projects WHERE id=?',(ident,)).fetchone()
            if not current:return 'not_found',None
            if current['revision']!=expected_revision:return 'conflict',None
            db.execute('UPDATE projects SET title=?,description=?,status=?,revision=revision+1,updated_at=? WHERE id=?',
                       (title,description,status,now_utc(),ident))
            db.commit()
        return 'updated',self.project(ident)

    def tasks(self,project_id:str|None=None):
        with self.conn() as db:
            if project_id:
                rows=db.execute('SELECT * FROM tasks WHERE project_id=? ORDER BY due_on IS NULL,due_on,updated_at DESC,id',(project_id,))
            else:
                rows=db.execute('SELECT * FROM tasks ORDER BY due_on IS NULL,due_on,updated_at DESC,id')
            return [self._decode_task(row) for row in rows]

    def task(self,ident:str):
        with self.conn() as db:
            row=db.execute('SELECT * FROM tasks WHERE id=?',(ident,)).fetchone()
            return self._decode_task(row) if row else None

    @staticmethod
    def _decode_task(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result['labels'] = json.loads(result['labels'])
        result['flagged'] = bool(result['flagged'])
        return result

    @staticmethod
    def _task_properties(data: dict[str, Any], current: sqlite3.Row | None = None) -> tuple[Any, ...]:
        values = dict(TASK_PROPERTY_DEFAULTS if current is None else current)
        values.update(data)
        if 'labels' in data:
            values['labels'] = json.dumps(data['labels'], ensure_ascii=False)
        return tuple(values[key] for key in TASK_PROPERTY_DEFAULTS)

    def create_task(self,**data):
        ident=str(uuid4()); now=now_utc()
        with self.conn() as db:
            self._check_refs(db,data.get('project_id'),data.get('document_id'))
            db.execute('''INSERT INTO tasks(id,project_id,document_id,title,status,priority,due_on,revision,created_at,updated_at,
                                            effort,labels,flagged,reference_url,notes)
                          VALUES(?,?,?,?,?,?,?,1,?,?,?,?,?,?,?)''',
                       (ident,data['project_id'],data['document_id'],data['title'],data['status'],data['priority'],data['due_on'],
                        now,now,*self._task_properties(data)))
            return self._decode_task(db.execute('SELECT * FROM tasks WHERE id=?',(ident,)).fetchone())

    def update_task(self,ident:str,expected_revision:int,**data):
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT * FROM tasks WHERE id=?',(ident,)).fetchone()
            if not current:return 'not_found',None
            if current['revision']!=expected_revision:return 'conflict',None
            self._check_refs(db,data.get('project_id'),data.get('document_id'))
            db.execute('''UPDATE tasks SET project_id=?,document_id=?,title=?,status=?,priority=?,due_on=?,
                                            effort=?,labels=?,flagged=?,reference_url=?,notes=?,
                                            revision=revision+1,updated_at=? WHERE id=?''',
                       (data['project_id'],data['document_id'],data['title'],data['status'],data['priority'],data['due_on'],
                        *self._task_properties(data, current),now_utc(),ident))
            return 'updated',self._decode_task(db.execute('SELECT * FROM tasks WHERE id=?',(ident,)).fetchone())

    @staticmethod
    def _check_refs(db:sqlite3.Connection, project_id:str|None,document_id:str|None):
        if project_id and not db.execute('SELECT 1 FROM projects WHERE id=?',(project_id,)).fetchone():raise ValueError('Project not found')
        if document_id and not db.execute('SELECT 1 FROM documents WHERE id=?',(document_id,)).fetchone():raise ValueError('Document not found')

    def event(self,ident:str):
        with self.conn() as db:
            row=db.execute('SELECT * FROM calendar_events WHERE id=?',(ident,)).fetchone()
            return dict(row) if row else None

    def events_between(self, start_date:str,end_date:str):
        with self.conn() as db:
            return [dict(x) for x in db.execute('''SELECT * FROM calendar_events WHERE start_date<? AND end_date>? ORDER BY start_date,start_at LIMIT 1000''',(end_date,start_date))]

    def calendar_feed(self,start_date:str,end_date:str):
        feed=[{**x,'kind':'event'} for x in self.events_between(start_date,end_date)]
        with self.conn() as db:
            rows=db.execute('''SELECT id,title,due_on,status,project_id,document_id FROM tasks WHERE due_on>=? AND due_on<? AND status!='archived' ORDER BY due_on LIMIT 1000''',(start_date,end_date))
            for x in rows:
                item=dict(x)
                feed.append({'kind':'task','id':item['id'],'title':item['title'],'start_date':item['due_on'],
                             'end_date':(date.fromisoformat(item['due_on'])+timedelta(days=1)).isoformat(),
                             'all_day':1,'document_id':item['document_id'],'project_id':item['project_id'], 'status':item['status']})
        return sorted(feed,key=lambda e:(e['start_date'],e['kind'],e['title']))

    def create_event(self,**data):
        ident=str(uuid4()); now=now_utc()
        with self.conn() as db:
            self._check_event_links(db,data)
            db.execute('''INSERT INTO calendar_events(id,title,start_at,end_at,start_date,end_date,all_day,timezone,document_id,task_id,revision,created_at,updated_at)
                          VALUES(?,?,?,?,?,?,?,?,?,?,1,?,?)''',
                       (ident,data['title'],data['start_at'],data['end_at'],data['start_date'],data['end_date'],int(data['all_day']),data['timezone'],data.get('document_id'),data.get('task_id'),now,now))
        return self.event(ident)

    def update_event(self,ident:str,expected_revision:int,**data):
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT revision FROM calendar_events WHERE id=?',(ident,)).fetchone()
            if not current:return 'not_found',None
            if current['revision']!=expected_revision:return 'conflict',None
            self._check_event_links(db,data)
            db.execute('''UPDATE calendar_events SET title=?,start_at=?,end_at=?,start_date=?,end_date=?,all_day=?,timezone=?,document_id=?,task_id=?,revision=revision+1,updated_at=? WHERE id=?''',
                       (data['title'],data['start_at'],data['end_at'],data['start_date'],data['end_date'],int(data['all_day']),data['timezone'],data.get('document_id'),data.get('task_id'),now_utc(),ident))
            db.commit()
        return 'updated',self.event(ident)

    @staticmethod
    def _check_event_links(db:sqlite3.Connection,data:dict):
        if data.get('document_id') and not db.execute('SELECT 1 FROM documents WHERE id=?',(data['document_id'],)).fetchone():raise ValueError('Document not found')
        if data.get('task_id') and not db.execute('SELECT 1 FROM tasks WHERE id=?',(data['task_id'],)).fetchone():raise ValueError('Task not found')

    @staticmethod
    def _read_canvas(db: sqlite3.Connection, page_id: str) -> dict[str, Any] | None:
        document = db.execute(
            '''SELECT documents.*, (
                   EXISTS (SELECT 1 FROM page_template_requests WHERE page_id=documents.id)
                   OR EXISTS (
                       SELECT 1 FROM page_duplicate_requests WHERE page_id=documents.id AND from_template=1
                   )
               ) AS from_template FROM active_documents AS documents WHERE id=?''',
            (page_id,),
        ).fetchone()
        if document is None:
            return None
        page = dict(document)
        page['values'] = json.loads(page.pop('field_values'))
        page['from_template'] = bool(page['from_template'])
        page['properties'] = WorkspaceStore._read_properties(db, page_id)
        page['blocks'] = [
            {'id': row['id'], 'type': 'table' if row['is_table'] else row['extension_type'] or row['block_type'],
             'content': row['content'], 'checked': bool(row['checked']),
             **({'depth': row['depth']} if row['depth'] else {})}
            for row in db.execute(
                '''SELECT id,block_type,content,checked,is_table,extension_type,depth
                   FROM page_blocks WHERE page_id=? ORDER BY position''',
                (page_id,),
            )
        ]
        return page

    @staticmethod
    def _write_blocks(db: sqlite3.Connection, page_id: str, blocks: list[dict[str, Any]]) -> None:
        extended_types = {'ordered_list','page_link'}
        db.executemany(
            '''INSERT INTO page_blocks(id,page_id,position,block_type,content,checked,is_table,extension_type,depth)
               VALUES(?,?,?,?,?,?,?,?,?)''',
            ((block['id'], page_id, index,
              'paragraph' if block['type'] == 'table' or block['type'] in extended_types else block['type'],
              block['content'], int(block['checked']), int(block['type'] == 'table'),
              block['type'] if block['type'] in extended_types else None,
              block.get('depth', 0))
             for index, block in enumerate(blocks)),
        )

    @staticmethod
    def _history_snapshot(page: dict[str, Any]) -> dict[str, Any]:
        return {
            'revision': page['revision'],
            'title': page['title'],
            'created_at': page['updated_at'],
            'parent_id': page['parent_id'],
            'values': page['values'],
            'blocks': page['blocks'],
        }

    def _record_history(self, db: sqlite3.Connection, page: dict[str, Any]) -> None:
        snapshot = self._history_snapshot(page)
        db.execute(
            '''INSERT INTO page_history(page_id,revision,title,created_at,snapshot) VALUES(?,?,?,?,?)
               ON CONFLICT(page_id,revision) DO NOTHING''',
            (page['id'], snapshot['revision'], snapshot['title'], snapshot['created_at'],
             json.dumps(snapshot, ensure_ascii=False)),
        )

    def get_canvas(self, page_id: str) -> dict[str, Any] | None:
        with self.conn() as db:
            db.execute('BEGIN')
            return self._read_canvas(db, page_id)

    def list_page_history(
        self, page_id: str, before_revision: int | None,
    ) -> list[dict[str, Any]] | None:
        with self.conn() as db:
            db.execute('BEGIN')
            page = db.execute('SELECT revision,title,updated_at FROM active_documents WHERE id=?', (page_id,)).fetchone()
            if page is None:
                return None
            rows = db.execute(
                '''SELECT revision,title,created_at FROM page_history
                   WHERE page_id=? AND (? IS NULL OR revision < ?)
                   ORDER BY revision DESC LIMIT 100''',
                (page_id, before_revision, before_revision),
            ).fetchall()
            if not rows and (before_revision is None or before_revision > page['revision']):
                return [{'revision': page['revision'], 'title': page['title'], 'created_at': page['updated_at']}]
            return [dict(row) for row in rows]

    def get_page_history(self, page_id: str, revision: int) -> dict[str, Any] | None:
        with self.conn() as db:
            db.execute('BEGIN')
            if not db.execute('SELECT 1 FROM active_documents WHERE id=?', (page_id,)).fetchone():
                return None
            stored = self._read_page_snapshot(db, page_id, revision)
            if stored is not None:
                return stored
            page = self._read_canvas(db, page_id)
            if page is not None and page['revision'] == revision:
                return self._history_snapshot(page)
            return None

    @staticmethod
    def _read_page_snapshot(
        db: sqlite3.Connection, page_id: str, revision: int,
    ) -> dict[str, Any] | None:
        row = db.execute(
            'SELECT snapshot FROM page_history WHERE page_id=? AND revision=?', (page_id, revision),
        ).fetchone()
        return json.loads(row['snapshot']) if row else None

    def restore_page_revision(
        self, page_id: str, expected_revision: int, revision: int,
    ) -> tuple[str, dict[str, Any] | None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            current = self._read_canvas(db, page_id)
            if current is None:
                return 'not_found', None
            if current['revision'] != expected_revision:
                return 'conflict', None
            if current['revision'] == revision:
                return 'updated', current
            snapshot = self._read_page_snapshot(db, page_id, revision)
            if snapshot is None:
                return 'revision_not_found', None
            if self._has_foreign_block(db, page_id, snapshot['blocks']):
                return 'block_conflict', None

            restored = self._write_canvas_revision(
                db, current, snapshot['title'], snapshot['blocks'], values=snapshot['values'],
            )
            return 'updated', restored

    @staticmethod
    def _has_foreign_block(
        db: sqlite3.Connection, page_id: str, blocks: list[dict[str, Any]],
    ) -> bool:
        if not blocks:
            return False
        placeholders = ','.join('?' for _ in blocks)
        return db.execute(
            f'SELECT 1 FROM page_blocks WHERE page_id<>? AND id IN ({placeholders}) LIMIT 1',
            (page_id, *(block['id'] for block in blocks)),
        ).fetchone() is not None

    def _write_canvas_revision(
        self, db: sqlite3.Connection, current: dict[str, Any],
        title: str, blocks: list[dict[str, Any]], *, values: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        page_id = current['id']
        self._record_history(db, current)
        db.execute(
            '''UPDATE documents SET title=?,field_values=COALESCE(?,field_values),
                      revision=revision+1,updated_at=? WHERE id=?''',
            (title, json.dumps(values, ensure_ascii=False) if values is not None else None, now_utc(), page_id),
        )
        db.execute('DELETE FROM page_blocks WHERE page_id=?', (page_id,))
        self._write_blocks(db, page_id, blocks)
        updated = self._read_canvas(db, page_id)
        assert updated is not None
        self._record_history(db, updated)
        return updated

    def update_canvas(
        self, page_id: str, expected_revision: int, title: str, blocks: list[dict[str, Any]],
    ) -> tuple[str, dict[str, Any] | None]:
        with self.conn() as db:
            db.execute('BEGIN IMMEDIATE')
            current = self._read_canvas(db, page_id)
            if current is None:
                return 'not_found', None
            if current['revision'] != expected_revision:
                return 'conflict', None
            if current['title'] == title and current['blocks'] == blocks:
                return 'updated', current
            if blocks:
                existing_ids = {block['id'] for block in current['blocks']}
                if any(block['id'] not in existing_ids and not re.fullmatch(UUID_PATTERN, block['id'])
                       for block in blocks):
                    return 'invalid_block_id', None
            if self._has_foreign_block(db, page_id, blocks):
                return 'block_conflict', None
            updated = self._write_canvas_revision(db, current, title, blocks)
            return 'updated', updated

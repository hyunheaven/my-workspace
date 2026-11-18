"""Local user-defined databases and their records, properties and views."""
from __future__ import annotations

from contextlib import closing, contextmanager
from datetime import date
import json
import math
import sqlite3
from typing import Any, Iterator, Literal
from unicodedata import normalize
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Path, Query, Response
from pydantic import BaseModel, ConfigDict, Field

from .workspace_store import WorkspaceStore, now_utc

PropertyType = Literal[
    'text', 'number', 'date', 'checkbox', 'select', 'multi_select', 'url', 'relation', 'rollup', 'formula'
]
ViewKind = Literal['table', 'board', 'calendar', 'timeline', 'gallery']
HistoryKind = Literal['record', 'view']
Scalar = str | int | float | bool | None
COMPUTED = frozenset({'formula', 'rollup'})
MAX_PROPERTIES = 48
MAX_VIEWS = 32
MAX_DATABASES = 100
MAX_RECORDS = 2000
MAX_RELATIONS = 100
MAX_BATCH = 100
MAX_NUMBER = 1e15
HISTORY_PAGE_SIZE = 25
MAX_REVISION = 2**63 - 1
HISTORY_TABLES = {'record': ('custom_record_history', 'record_id'),
                  'view': ('custom_view_history', 'view_id')}


def _invalid(message: str) -> HTTPException:
    return HTTPException(422, message)


def _missing(resource: str) -> HTTPException:
    return HTTPException(404, f'{resource} not found')


def _conflict(message: str) -> HTTPException:
    return HTTPException(409, message)


def _encode(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def _text(value: Any, max_length: int, *, required: bool = False, multiline: bool = False) -> str:
    if not isinstance(value, str) or len(value) > max_length:
        raise _invalid(f'Text must have at most {max_length} characters')
    if any((ord(ch) < 32 and not (multiline and ch in '\n\r\t')) or
           0xD800 <= ord(ch) <= 0xDFFF or ch == '\x7f' for ch in value):
        raise _invalid('Invalid text characters')
    if required:
        value = value.strip()
        if not value:
            raise _invalid('Name or title is required')
    return value


def _key(value: str) -> str:
    return normalize('NFKC', value).casefold()


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class Revision(Input):
    expected_revision: int = Field(ge=1, le=2**63 - 1)


class DatabaseInput(Input):
    name: str = Field(max_length=120)


class DatabaseUpdate(DatabaseInput, Revision):
    pass


class PropertyInput(Revision):
    name: str = Field(max_length=80)
    type: PropertyType
    config: dict[str, Any] = Field(default_factory=dict, max_length=8)


class ViewConfig(Input):
    group_by: str | None = None
    date_property: str | None = None
    end_date_property: str | None = None
    sort_by: str | None = None
    sort_direction: Literal['asc', 'desc'] = 'asc'
    filter_property: str | None = None
    filter_value: Scalar = None


class ViewInput(Revision):
    name: str = Field(max_length=80)
    kind: ViewKind
    config: ViewConfig = Field(default_factory=ViewConfig)


class RecordInput(Input):
    title: str = Field(max_length=120)
    notes: str = Field(default='', max_length=8000)
    values: dict[str, Any] = Field(default_factory=dict, max_length=MAX_PROPERTIES)


class RecordUpdate(RecordInput, Revision):
    pass


class RecordBatch(Input):
    records: list[RecordInput] = Field(min_length=1, max_length=MAX_BATCH)


class CustomDatabaseStore:
    def __init__(self, workspace: WorkspaceStore):
        self.workspace = workspace
        with closing(workspace.conn()) as db:
            db.executescript("""
                BEGIN IMMEDIATE;
                CREATE TABLE IF NOT EXISTS custom_databases (
                    id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL,
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS custom_properties (
                    id TEXT PRIMARY KEY NOT NULL,
                    database_id TEXT NOT NULL REFERENCES custom_databases(id),
                    name TEXT NOT NULL, type TEXT NOT NULL, config TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    UNIQUE(database_id, position)
                );
                CREATE TABLE IF NOT EXISTS custom_views (
                    id TEXT PRIMARY KEY NOT NULL,
                    database_id TEXT NOT NULL REFERENCES custom_databases(id),
                    name TEXT NOT NULL, kind TEXT NOT NULL, config TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    UNIQUE(database_id, position)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS uq_custom_views_database_id
                    ON custom_views(database_id, id);
                CREATE TABLE IF NOT EXISTS custom_records (
                    id TEXT PRIMARY KEY NOT NULL,
                    database_id TEXT NOT NULL REFERENCES custom_databases(id),
                    title TEXT NOT NULL, notes TEXT NOT NULL, field_values TEXT NOT NULL,
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_custom_records_database
                    ON custom_records(database_id, created_at, id);
                CREATE TABLE IF NOT EXISTS custom_record_links (
                    record_id TEXT NOT NULL REFERENCES custom_records(id) ON DELETE CASCADE,
                    property_id TEXT NOT NULL REFERENCES custom_properties(id),
                    target_id TEXT NOT NULL REFERENCES custom_records(id) ON DELETE RESTRICT,
                    PRIMARY KEY(record_id, property_id, target_id)
                );
                CREATE INDEX IF NOT EXISTS ix_custom_record_link_target
                    ON custom_record_links(target_id);
                CREATE TABLE IF NOT EXISTS custom_record_history (
                    record_id TEXT NOT NULL REFERENCES custom_records(id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL, created_at TEXT NOT NULL,
                    title TEXT NOT NULL, snapshot TEXT NOT NULL,
                    PRIMARY KEY(record_id, revision)
                );
                CREATE TABLE IF NOT EXISTS custom_view_history (
                    view_id TEXT NOT NULL REFERENCES custom_views(id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL, created_at TEXT NOT NULL,
                    title TEXT NOT NULL, snapshot TEXT NOT NULL,
                    PRIMARY KEY(view_id, revision)
                );
                COMMIT;
            """)

    @contextmanager
    def _transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        with closing(self.workspace.conn()) as db, db:
            db.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield db

    @staticmethod
    def _db(db: sqlite3.Connection, database_id: str) -> sqlite3.Row:
        row = db.execute('SELECT * FROM custom_databases WHERE id=?', (database_id,)).fetchone()
        if row is None:
            raise _missing('Database')
        return row

    @staticmethod
    def _record(db: sqlite3.Connection, database_id: str, record_id: str) -> sqlite3.Row:
        row = db.execute(
            'SELECT * FROM custom_records WHERE database_id=? AND id=?', (database_id, record_id)
        ).fetchone()
        if row is None:
            raise _missing('Record')
        return row

    @staticmethod
    def _view(db: sqlite3.Connection, database_id: str, view_id: str) -> sqlite3.Row:
        row = db.execute(
            'SELECT * FROM custom_views WHERE database_id=? AND id=?', (database_id, view_id)
        ).fetchone()
        if row is None:
            raise _missing('View')
        return row

    @staticmethod
    def _check_revision(row: sqlite3.Row, revision: int) -> None:
        if row['revision'] != revision:
            raise _conflict('Another edit changed this item. Reload before writing again.')

    @staticmethod
    def _definitions(db: sqlite3.Connection, database_id: str, definition: str) -> list[dict[str, Any]]:
        sql = {
            'property': 'SELECT id,name,type,config FROM custom_properties WHERE database_id=? ORDER BY position',
            'view': 'SELECT id,name,kind,config FROM custom_views WHERE database_id=? ORDER BY position',
        }[definition]
        return [{**row, 'config': json.loads(row['config'])} for row in db.execute(sql, (database_id,))]

    @staticmethod
    def _property(db: sqlite3.Connection, database_id: str, property_id: Any) -> sqlite3.Row:
        if not isinstance(property_id, str):
            raise _invalid('Expected a property ID')
        target = db.execute(
            'SELECT * FROM custom_properties WHERE database_id=? AND id=?', (database_id, property_id)
        ).fetchone()
        if target is None:
            raise _invalid('Unknown property in this database')
        return target

    @staticmethod
    def _touch(db: sqlite3.Connection, database_id: str) -> None:
        db.execute(
            'UPDATE custom_databases SET revision=revision+1,updated_at=? WHERE id=?',
            (now_utc(), database_id),
        )

    @staticmethod
    def _history_entry(kind: HistoryKind, row: sqlite3.Row,
                       database: sqlite3.Row) -> dict[str, Any]:
        if kind == 'record':
            return {'revision': row['revision'], 'created_at': row['updated_at'],
                    'title': row['title'], 'snapshot': {
                        'title': row['title'], 'notes': row['notes'],
                        'values': json.loads(row['field_values']),
                    }}
        return {'revision': database['revision'], 'created_at': database['updated_at'],
                'title': row['name'], 'snapshot': {
                    'name': row['name'], 'kind': row['kind'], 'config': json.loads(row['config']),
                }}

    @staticmethod
    def _save_history(db: sqlite3.Connection, kind: HistoryKind, item_id: str,
                      entry: dict[str, Any]) -> None:
        table, column = HISTORY_TABLES[kind]
        db.execute(f'''INSERT INTO {table}({column},revision,created_at,title,snapshot)
                       VALUES(?,?,?,?,?) ON CONFLICT({column},revision) DO NOTHING''',
                   (item_id, entry['revision'], entry['created_at'], entry['title'],
                    _encode(entry['snapshot'])))

    def list_history(self, database_id: str, kind: HistoryKind, item_id: str,
                     before_revision: int | None) -> list[dict[str, Any]]:
        table, column = HISTORY_TABLES[kind]
        with self._transaction() as db:
            database = self._db(db, database_id)
            current = (self._record if kind == 'record' else self._view)(db, database_id, item_id)
            rows = db.execute(f'''SELECT revision,created_at,title,snapshot FROM {table}
                                  WHERE {column}=? AND (? IS NULL OR revision<?)
                                  ORDER BY revision DESC LIMIT ?''',
                              (item_id, before_revision, before_revision, HISTORY_PAGE_SIZE)).fetchall()
            if rows:
                return [{**row, 'snapshot': json.loads(row['snapshot'])} for row in rows]
            if db.execute(f'SELECT 1 FROM {table} WHERE {column}=? LIMIT 1', (item_id,)).fetchone():
                return []
            baseline = self._history_entry(kind, current, database)
            return [baseline] if before_revision is None or baseline['revision'] < before_revision else []

    def _restore_snapshot(self, db: sqlite3.Connection, kind: HistoryKind, current: sqlite3.Row,
                          database: sqlite3.Row, revision: int) -> dict[str, Any]:
        table, column = HISTORY_TABLES[kind]
        row = db.execute(f'SELECT snapshot FROM {table} WHERE {column}=? AND revision=?',
                         (current['id'], revision)).fetchone()
        if row:
            return json.loads(row['snapshot'])
        if not db.execute(f'SELECT 1 FROM {table} WHERE {column}=? LIMIT 1', (current['id'],)).fetchone():
            baseline = self._history_entry(kind, current, database)
            if baseline['revision'] == revision:
                return baseline['snapshot']
        raise _missing('Revision')

    def list_databases(self) -> list[dict[str, Any]]:
        with self._transaction() as db:
            return [dict(row) for row in db.execute(
                'SELECT id,name,revision FROM custom_databases ORDER BY created_at,id'
            )]

    def read_database(self, database_id: str) -> dict[str, Any]:
        with self._transaction() as db:
            return self._snapshot(db, database_id)

    def list_views(self, database_id: str) -> list[dict[str, Any]]:
        with self._transaction() as db:
            self._db(db, database_id)
            return self._definitions(db, database_id, 'view')

    def record_titles(self, database_id: str) -> list[dict[str, Any]]:
        with self._transaction() as db:
            self._db(db, database_id)
            rows = db.execute('SELECT id,title FROM custom_records WHERE database_id=? ORDER BY created_at,id',
                              (database_id,))
            return [dict(row) for row in rows]

    def create_database(self, body: DatabaseInput) -> dict[str, Any]:
        name = _text(body.name, 120, required=True)
        database_id, timestamp = str(uuid4()), now_utc()
        with self._transaction(write=True) as db:
            if db.execute('SELECT COUNT(*) FROM custom_databases').fetchone()[0] >= MAX_DATABASES:
                raise _invalid('Database limit reached')
            db.execute('INSERT INTO custom_databases(id,name,created_at,updated_at) VALUES(?,?,?,?)',
                       (database_id, name, timestamp, timestamp))
            view_id = str(uuid4())
            db.execute('INSERT INTO custom_views VALUES(?,?,?,?,?,?)',
                       (view_id, database_id, '표', 'table', '{}', 0))
            self._record_view_version(db, database_id, view_id)
            return self._snapshot(db, database_id)

    def rename_database(self, database_id: str, body: DatabaseUpdate) -> dict[str, Any]:
        name = _text(body.name, 120, required=True)
        with self._transaction(write=True) as db:
            self._check_revision(self._db(db, database_id), body.expected_revision)
            db.execute('UPDATE custom_databases SET name=? WHERE id=?', (name, database_id))
            self._touch(db, database_id)
            return self._snapshot(db, database_id)

    @staticmethod
    def _unique_name(definitions: list[dict[str, Any]], name: str, definition_id: str | None) -> None:
        if any(_key(item['name']) == _key(name) and item['id'] != definition_id for item in definitions):
            raise _invalid('Another definition already uses this name')

    def write_property(self, database_id: str, body: PropertyInput,
                       property_id: str | None = None) -> dict[str, Any]:
        name = _text(body.name, 80, required=True)
        with self._transaction(write=True) as db:
            self._check_revision(self._db(db, database_id), body.expected_revision)
            properties = self._definitions(db, database_id, 'property')
            self._unique_name(properties, name, property_id)
            config = self._property_config(db, database_id, body.type, body.config)
            if property_id is None:
                if len(properties) >= MAX_PROPERTIES:
                    raise _invalid('Property limit reached')
                property_id = str(uuid4())
                db.execute('INSERT INTO custom_properties VALUES(?,?,?,?,?,?)',
                           (property_id, database_id, name, body.type, _encode(config), len(properties)))
            else:
                previous = self._property(db, database_id, property_id)
                if previous['type'] != body.type:
                    raise _invalid('Create a new property to change the type')
                self._preserve_property_values(db, previous, config)
                db.execute('UPDATE custom_properties SET name=?,config=? WHERE id=?',
                           (name, _encode(config), property_id))
            self._touch(db, database_id)
            return self._snapshot(db, database_id)

    def _preserve_property_values(self, db: sqlite3.Connection, previous: sqlite3.Row,
                                  config: dict[str, Any]) -> None:
        old_config = json.loads(previous['config'])
        if previous['type'] == 'relation' and config != old_config:
            # A rollup may reference the old target even if no records have links.
            raise _invalid('Create a new relation to select another database')
        if previous['type'] not in ('select', 'multi_select') or config == old_config:
            return
        # Options can be extended and reordered. Reject removing options that would
        # invalidate stored records or saved filters.
        removed = set(old_config['options']) - set(config['options'])
        for row in db.execute('SELECT field_values FROM custom_records WHERE database_id=?',
                              (previous['database_id'],)):
            value = json.loads(row['field_values']).get(previous['id'])
            used = value if isinstance(value, list) else [value]
            if removed.intersection(used):
                raise _invalid('An existing record uses an option you removed')
        for view in self._definitions(db, previous['database_id'], 'view'):
            settings = view['config']
            if settings.get('filter_property') == previous['id'] and settings.get('filter_value') in removed:
                raise _invalid('A saved view uses an option you removed')

    def _property_config(self, db: sqlite3.Connection, database_id: str, kind: str,
                         config: dict[str, Any]) -> dict[str, Any]:
        if kind in ('select', 'multi_select'):
            self._keys(config, {'options'})
            entries = config.get('options')
            if not isinstance(entries, list) or not 1 <= len(entries) <= 100:
                raise _invalid('Select properties require 1 to 100 options')
            options = [_text(entry, 80, required=True) for entry in entries]
            if len({_key(option) for option in options}) != len(options):
                raise _invalid('Select options must be unique')
            return {'options': options}
        if kind == 'relation':
            self._keys(config, {'database_id'})
            target_id = config.get('database_id')
            if not isinstance(target_id, str):
                raise _invalid('Relation requires a target database')
            self._db(db, target_id)
            return {'database_id': target_id}
        if kind == 'rollup':
            self._keys(config, {'operation', 'relation_id', 'property_id'})
            operation = config.get('operation')
            if operation not in ('count', 'sum', 'average', 'min', 'max'):
                raise _invalid('Unsupported rollup operation')
            relation = self._property(db, database_id, config.get('relation_id'))
            if relation['type'] != 'relation':
                raise _invalid('Rollups require a relation property')
            result = {'operation': operation, 'relation_id': relation['id']}
            target_id = config.get('property_id')
            if operation != 'count':
                target_database_id = json.loads(relation['config'])['database_id']
                target = self._property(db, target_database_id, target_id)
                if target['type'] != 'number':
                    raise _invalid('Numeric rollups require a target number property')
                result['property_id'] = target['id']
            elif target_id is not None:
                raise _invalid('Count rollup does not take a number property')
            return result
        if kind == 'formula':
            self._keys(config, {'operation', 'left_id', 'right_id'})
            operation = config.get('operation')
            if operation not in ('add', 'subtract', 'multiply', 'divide'):
                raise _invalid('Unsupported formula operation')
            result = {'operation': operation}
            for key in ('left_id', 'right_id'):
                operand = self._property(db, database_id, config.get(key))
                if operand['type'] not in ('number', 'rollup'):
                    raise _invalid('Formula operands must be number or rollup properties')
                result[key] = operand['id']
            return result
        self._keys(config, set())
        return {}

    @staticmethod
    def _keys(config: dict[str, Any], allowed: set[str]) -> None:
        if not set(config).issubset(allowed):
            raise _invalid('Unsupported property configuration key')

    def write_view(self, database_id: str, body: ViewInput, view_id: str | None = None) -> dict[str, Any]:
        with self._transaction(write=True) as db:
            return self._write_view(db, database_id, body, view_id)

    def _record_view_version(self, db: sqlite3.Connection, database_id: str, view_id: str) -> None:
        entry = self._history_entry('view', self._view(db, database_id, view_id), self._db(db, database_id))
        self._save_history(db, 'view', view_id, entry)

    def _write_view(self, db: sqlite3.Connection, database_id: str, body: ViewInput,
                    view_id: str | None) -> dict[str, Any]:
        self._check_revision(self._db(db, database_id), body.expected_revision)
        name = _text(body.name, 80, required=True)
        views = self._definitions(db, database_id, 'view')
        self._unique_name(views, name, view_id)
        config = self._view_config(db, database_id, body)
        if view_id is None:
            if len(views) >= MAX_VIEWS:
                raise _invalid('View limit reached')
            view_id = str(uuid4())
            db.execute('INSERT INTO custom_views VALUES(?,?,?,?,?,?)',
                       (view_id, database_id, name, body.kind, _encode(config), len(views)))
        else:
            if not db.execute('SELECT 1 FROM custom_view_history WHERE view_id=? LIMIT 1', (view_id,)).fetchone():
                self._record_view_version(db, database_id, view_id)
            result = db.execute('UPDATE custom_views SET name=?,kind=?,config=? WHERE database_id=? AND id=?',
                                (name, body.kind, _encode(config), database_id, view_id))
            if not result.rowcount:
                raise _missing('View')
        self._touch(db, database_id)
        self._record_view_version(db, database_id, view_id)
        return self._snapshot(db, database_id)

    def restore_view(self, database_id: str, view_id: str, revision: int,
                     body: Revision) -> dict[str, Any]:
        with self._transaction(write=True) as db:
            database = self._db(db, database_id)
            self._check_revision(database, body.expected_revision)
            current = self._view(db, database_id, view_id)
            snapshot = self._restore_snapshot(db, 'view', current, database, revision)
            return self._write_view(db, database_id, ViewInput(**snapshot, **body.model_dump()), view_id)

    def _view_config(self, db: sqlite3.Connection, database_id: str, body: ViewInput) -> dict[str, Any]:
        config = body.config.model_dump(exclude_none=True, exclude_unset=True)
        for key, expected in (
            ('group_by', ('select', 'checkbox')),
            ('date_property', ('date',)),
            ('end_date_property', ('date',)),
            ('sort_by', None),
        ):
            value = config.get(key)
            if value is None or key == 'sort_by' and value == 'title':
                continue
            field = self._property(db, database_id, value)
            if expected is not None and field['type'] not in expected:
                raise _invalid(f'Invalid property type for {key}')
        if config.get('end_date_property') and not config.get('date_property'):
            raise _invalid('An end date requires a start date property')
        if body.kind in ('calendar', 'timeline') and not config.get('date_property'):
            raise _invalid('Calendar and timeline views require a date property')
        if body.kind == 'board' and not config.get('group_by'):
            raise _invalid('A board requires a group property')
        filter_property = config.get('filter_property')
        filter_value = body.config.filter_value
        if filter_property:
            if filter_property == 'title':
                normalized = None if filter_value is None else _text(filter_value, 120)
            else:
                field = self._property(db, database_id, filter_property)
                field_kind = field['type']
                if field_kind == 'relation':
                    raise _invalid('Filtering by relation is unsupported')
                if field_kind == 'multi_select':
                    field_kind = 'select'
                if field_kind in COMPUTED:
                    field_kind = 'number'
                normalized = self._value(db, field_kind, json.loads(field['config']), filter_value)
            config['filter_value'] = normalized
        elif 'filter_value' in config:
            raise _invalid('A filter value requires a property')
        return config

    def add_records(self, database_id: str, records: list[RecordInput]) -> list[dict[str, Any]]:
        with self._transaction(write=True) as db:
            database = self._db(db, database_id)
            size = db.execute('SELECT COUNT(*) FROM custom_records WHERE database_id=?',
                              (database_id,)).fetchone()[0]
            if size + len(records) > MAX_RECORDS:
                raise _invalid('Record limit reached')
            properties = self._definitions(db, database_id, 'property')
            result = []
            for record in records:
                record_id, timestamp = str(uuid4()), now_utc()
                title, notes, values = self._record_values(db, properties, record)
                db.execute('''INSERT INTO custom_records(
                    id,database_id,title,notes,field_values,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)''',
                           (record_id, database_id, title, notes, _encode(values), timestamp, timestamp))
                self._write_links(db, record_id, properties, values)
                stored = self._record(db, database_id, record_id)
                self._save_history(db, 'record', record_id, self._history_entry('record', stored, database))
                result.append(self._record_payload(stored, properties, self._target_values(db, properties, [stored])))
            return result

    def update_record(self, database_id: str, record_id: str, body: RecordUpdate) -> dict[str, Any]:
        with self._transaction(write=True) as db:
            row = self._record(db, database_id, record_id)
            self._check_revision(row, body.expected_revision)
            return self._update_record(db, self._db(db, database_id), row, body)

    def _update_record(self, db: sqlite3.Connection, database: sqlite3.Row,
                       row: sqlite3.Row, body: RecordInput) -> dict[str, Any]:
        record_id, database_id = row['id'], database['id']
        properties = self._definitions(db, database_id, 'property')
        title, notes, values = self._record_values(db, properties, body)
        self._save_history(db, 'record', record_id, self._history_entry('record', row, database))
        db.execute('''UPDATE custom_records
                      SET title=?,notes=?,field_values=?,revision=revision+1,updated_at=? WHERE id=?''',
                   (title, notes, _encode(values), now_utc(), record_id))
        db.execute('DELETE FROM custom_record_links WHERE record_id=?', (record_id,))
        self._write_links(db, record_id, properties, values)
        stored = self._record(db, database_id, record_id)
        self._save_history(db, 'record', record_id, self._history_entry('record', stored, database))
        return self._record_payload(stored, properties, self._target_values(db, properties, [stored]))

    def restore_record(self, database_id: str, record_id: str, revision: int,
                       body: Revision) -> dict[str, Any]:
        with self._transaction(write=True) as db:
            current = self._record(db, database_id, record_id)
            self._check_revision(current, body.expected_revision)
            database = self._db(db, database_id)
            snapshot = self._restore_snapshot(db, 'record', current, database, revision)
            return self._update_record(db, database, current, RecordInput(**snapshot))

    def delete_record(self, database_id: str, record_id: str, body: Revision) -> None:
        with self._transaction(write=True) as db:
            self._check_revision(self._record(db, database_id, record_id), body.expected_revision)
            inbound = db.execute(
                'SELECT 1 FROM custom_record_links WHERE target_id=? AND record_id!=? LIMIT 1',
                (record_id, record_id),
            ).fetchone()
            if inbound:
                raise _conflict('Clear the relations pointing to this record before deleting it.')
            db.execute('DELETE FROM custom_record_links WHERE record_id=?', (record_id,))
            db.execute('DELETE FROM custom_records WHERE id=?', (record_id,))

    def _record_values(self, db: sqlite3.Connection, properties: list[dict[str, Any]],
                       body: RecordInput) -> tuple[str, str, dict[str, Any]]:
        title = _text(body.title, 120, required=True)
        notes = _text(body.notes, 8000, multiline=True)
        by_id = {field['id']: field for field in properties}
        values = {}
        for key, value in body.values.items():
            field = by_id.get(key)
            if field is None:
                raise _invalid('Unknown record property')
            if field['type'] in COMPUTED:
                raise _invalid('Computed property values are read-only')
            checked = self._value(db, field['type'], field['config'], value)
            if checked is not None:
                values[key] = checked
        return title, notes, values

    @staticmethod
    def _value(db: sqlite3.Connection, kind: str, config: dict[str, Any], value: Any) -> Any:
        if value is None:
            return None
        if kind == 'text':
            return _text(value, 4000, multiline=True)
        if kind == 'number':
            if type(value) not in (int, float) or not -MAX_NUMBER <= value <= MAX_NUMBER:
                raise _invalid('Expected a finite number in the supported range')
            return value
        if kind == 'checkbox':
            if type(value) is not bool:
                raise _invalid('Expected a checkbox boolean')
            return value
        if kind == 'date':
            try:
                if isinstance(value, str) and len(value) == 10 and date.fromisoformat(value).isoformat() == value:
                    return value
            except ValueError:
                pass
            raise _invalid('Expected a valid date in YYYY-MM-DD format')
        if kind == 'url':
            value = _text(value, 2048, required=True)
            try:
                parts = urlsplit(value)
                if (parts.scheme in ('http', 'https') and parts.hostname and parts.username is None
                        and parts.password is None and not any(ch.isspace() for ch in value)):
                    _ = parts.port
                    return value
            except ValueError:
                pass
            raise _invalid('Expected a plain HTTP or HTTPS URL without credentials')
        if kind == 'select':
            if not isinstance(value, str) or value not in config['options']:
                raise _invalid('Choose an existing option')
            return value
        if kind == 'multi_select':
            if not isinstance(value, list) or len(value) > len(config['options']):
                raise _invalid('Choose a list of existing options')
            if any(not isinstance(option, str) or option not in config['options'] for option in value):
                raise _invalid('Choose a list of existing options')
            return list(dict.fromkeys(value))
        if kind == 'relation':
            if not isinstance(value, list) or len(value) > MAX_RELATIONS or any(
                not isinstance(item, str) or len(item) != 36 for item in value
            ):
                raise _invalid('Choose up to 100 valid relation records')
            identifiers = list(dict.fromkeys(value))
            if identifiers:
                placeholders = ','.join('?' for _ in identifiers)
                matched = db.execute(
                    f'SELECT COUNT(*) FROM custom_records WHERE database_id=? AND id IN ({placeholders})',
                    (config['database_id'], *identifiers),
                ).fetchone()[0]
                if matched != len(identifiers):
                    raise _invalid('A relation record is missing or belongs to another database')
            return identifiers
        raise _invalid('Unsupported record property type')

    @staticmethod
    def _write_links(db: sqlite3.Connection, record_id: str, properties: list[dict[str, Any]],
                     values: dict[str, Any]) -> None:
        db.executemany('INSERT INTO custom_record_links VALUES(?,?,?)', (
            (record_id, field['id'], target_id)
            for field in properties if field['type'] == 'relation'
            for target_id in values.get(field['id'], [])
        ))

    @staticmethod
    def _target_values(db: sqlite3.Connection, properties: list[dict[str, Any]],
                       records: list[sqlite3.Row]) -> dict[str, dict[str, Any]]:
        needed = {
            field['config']['relation_id'] for field in properties
            if field['type'] == 'rollup' and field['config']['operation'] != 'count'
        }
        if not needed:
            return {}
        identifiers = sorted({
            target_id for row in records for prop, value in json.loads(row['field_values']).items()
            if prop in needed for target_id in value
        })
        result = {}
        for offset in range(0, len(identifiers), 500):
            batch = identifiers[offset:offset + 500]
            placeholders = ','.join('?' for _ in batch)
            rows = db.execute(f'SELECT id,field_values FROM custom_records WHERE id IN ({placeholders})', batch)
            result.update({row['id']: json.loads(row['field_values']) for row in rows})
        return result

    def _snapshot(self, db: sqlite3.Connection, database_id: str) -> dict[str, Any]:
        database = dict(self._db(db, database_id))
        properties = self._definitions(db, database_id, 'property')
        views = self._definitions(db, database_id, 'view')
        rows = db.execute('SELECT * FROM custom_records WHERE database_id=? ORDER BY created_at,id',
                          (database_id,)).fetchall()
        targets = self._target_values(db, properties, rows)
        return {
            **database, 'properties': properties, 'views': views,
            'records': [self._record_payload(row, properties, targets) for row in rows],
        }

    @staticmethod
    def _record_payload(row: sqlite3.Row, properties: list[dict[str, Any]],
                        target_values: dict[str, dict[str, Any]]) -> dict[str, Any]:
        item = dict(row)
        values = json.loads(item.pop('field_values'))
        for field in properties:
            if field['type'] != 'rollup':
                continue
            config = field['config']
            links = values.get(config['relation_id'], [])
            operation = config['operation']
            if operation == 'count':
                values[field['id']] = len(links)
                continue
            inputs = []
            for target in links:
                value = target_values.get(target, {}).get(config['property_id'])
                if value is not None:
                    inputs.append(value)
            if operation == 'sum':
                result = sum(inputs)
            elif not inputs:
                result = None
            elif operation == 'average':
                result = sum(inputs) / len(inputs)
            elif operation == 'min':
                result = min(inputs)
            else:
                result = max(inputs)
            values[field['id']] = result
        for field in properties:
            if field['type'] != 'formula':
                continue
            config = field['config']
            left, right = values.get(config['left_id']), values.get(config['right_id'])
            operation = config['operation']
            result = None
            if left is not None and right is not None:
                if operation == 'add':
                    result = left + right
                elif operation == 'subtract':
                    result = left - right
                elif operation == 'multiply':
                    result = left * right
                elif right != 0:
                    result = left / right
            values[field['id']] = result if result is None or math.isfinite(result) else None
        return {**item, 'values': values}

    def search(self, query: str) -> list[dict[str, Any]]:
        needle = _key(query.strip())
        if not needle:
            return []

        def matches(*values: str) -> bool:
            return any(needle in _key(value) for value in values)

        def values_match(raw: str) -> bool:
            def visible(value: Any) -> str:
                return ' '.join(str(part) for part in value) if isinstance(value, list) else str(value)
            return any(matches(visible(value)) for value in json.loads(raw).values())

        with self._transaction() as db:
            db.create_function('custom_name_matches', 1, matches)
            db.create_function('custom_record_matches', 2, matches)
            db.create_function('custom_values_match', 1, values_match)
            rows = db.execute("""
                SELECT id AS database_id,name AS database_name,id,name AS title,
                       'database' AS kind,updated_at
                FROM custom_databases WHERE custom_name_matches(name)
                UNION ALL
                SELECT d.id AS database_id,d.name AS database_name,r.id,r.title,
                       'record' AS kind,r.updated_at
                FROM custom_records AS r JOIN custom_databases AS d ON d.id=r.database_id
                WHERE custom_record_matches(r.title,r.notes) OR custom_values_match(r.field_values)
                ORDER BY updated_at DESC,id LIMIT 100
            """)
            return [dict(row) for row in rows]


def mount_custom_databases(app: FastAPI, store: CustomDatabaseStore) -> None:
    router = APIRouter(prefix='/api/v1/databases')

    @router.get('')
    def list_databases():
        return {'items': store.list_databases()}

    @router.post('', status_code=201)
    def create_database(body: DatabaseInput):
        return store.create_database(body)

    @router.get('/{database_id}')
    def read_database(database_id: str):
        return store.read_database(database_id)

    @router.put('/{database_id}')
    def rename_database(database_id: str, body: DatabaseUpdate):
        return store.rename_database(database_id, body)

    @router.post('/{database_id}/properties', status_code=201)
    def add_property(database_id: str, body: PropertyInput):
        return store.write_property(database_id, body)

    @router.put('/{database_id}/properties/{property_id}')
    def edit_property(database_id: str, property_id: str, body: PropertyInput):
        return store.write_property(database_id, body, property_id)

    @router.post('/{database_id}/views', status_code=201)
    def add_view(database_id: str, body: ViewInput):
        return store.write_view(database_id, body)

    @router.get('/{database_id}/views')
    def list_views(database_id: str):
        return {'items': store.list_views(database_id)}

    @router.put('/{database_id}/views/{view_id}')
    def edit_view(database_id: str, view_id: str, body: ViewInput):
        return store.write_view(database_id, body, view_id)

    @router.get('/{database_id}/views/{view_id}/history')
    def view_history(database_id: str, view_id: str,
                     before_revision: int | None = Query(None, ge=1, le=MAX_REVISION)):
        return {'items': store.list_history(database_id, 'view', view_id, before_revision)}

    @router.post('/{database_id}/views/{view_id}/history/{revision}/restore')
    def restore_view(database_id: str, view_id: str, body: Revision,
                     revision: int = Path(ge=1, le=MAX_REVISION)):
        return store.restore_view(database_id, view_id, revision, body)

    @router.post('/{database_id}/records', status_code=201)
    def add_record(database_id: str, body: RecordInput):
        return store.add_records(database_id, [body])[0]

    @router.get('/{database_id}/records')
    def record_titles(database_id: str):
        return {'items': store.record_titles(database_id)}

    @router.post('/{database_id}/records/batch', status_code=201)
    def add_records(database_id: str, body: RecordBatch):
        return {'items': store.add_records(database_id, body.records)}

    @router.put('/{database_id}/records/{record_id}')
    def update_record(database_id: str, record_id: str, body: RecordUpdate):
        return store.update_record(database_id, record_id, body)

    @router.get('/{database_id}/records/{record_id}/history')
    def record_history(database_id: str, record_id: str,
                       before_revision: int | None = Query(None, ge=1, le=MAX_REVISION)):
        return {'items': store.list_history(database_id, 'record', record_id, before_revision)}

    @router.post('/{database_id}/records/{record_id}/history/{revision}/restore')
    def restore_record(database_id: str, record_id: str, body: Revision,
                       revision: int = Path(ge=1, le=MAX_REVISION)):
        return store.restore_record(database_id, record_id, revision, body)

    @router.delete('/{database_id}/records/{record_id}', status_code=204)
    def delete_record(database_id: str, record_id: str, body: Revision):
        store.delete_record(database_id, record_id, body)
        return Response(status_code=204)

    app.include_router(router)

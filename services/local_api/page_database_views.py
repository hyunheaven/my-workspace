"""Persistent references from personal pages to views in a local database."""
from __future__ import annotations

from contextlib import closing
import sqlite3
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .workspace_store import UUID_PATTERN, WorkspaceStore


class LinkRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    database_id: str = Field(pattern=UUID_PATTERN)
    view_id: str = Field(pattern=UUID_PATTERN)


class UnlinkRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')


def mount_page_database_views(app: FastAPI, store: WorkspaceStore) -> None:
    with closing(store.conn()) as db, db:
        db.execute('''CREATE TABLE IF NOT EXISTS page_database_views (
            id TEXT PRIMARY KEY NOT NULL,
            page_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            database_id TEXT NOT NULL REFERENCES custom_databases(id) ON DELETE CASCADE,
            view_id TEXT NOT NULL,
            FOREIGN KEY (database_id,view_id) REFERENCES custom_views(database_id,id) ON DELETE CASCADE,
            UNIQUE(page_id,view_id)
        )''')

    def check_page(db: sqlite3.Connection, page_id: str) -> None:
        if db.execute('SELECT 1 FROM active_documents WHERE id=?', (page_id,)).fetchone() is None:
            raise HTTPException(404, '페이지를 찾을 수 없습니다.')

    @app.get('/api/v1/pages/{page_id}/linked-views')
    def list_links(page_id: str):
        with closing(store.conn()) as db, db:
            db.execute('BEGIN')
            check_page(db, page_id)
            rows = db.execute('''SELECT links.id,links.database_id,links.view_id,
                                        databases.name AS database_name,views.name AS view_name
                                 FROM page_database_views AS links
                                 JOIN custom_databases AS databases ON databases.id=links.database_id
                                 JOIN custom_views AS views ON views.id=links.view_id
                                 WHERE links.page_id=? ORDER BY links.rowid''', (page_id,))
            return {'items': [dict(row) for row in rows]}

    @app.post('/api/v1/pages/{page_id}/linked-views', status_code=201)
    def add_link(page_id: str, body: LinkRequest):
        with closing(store.conn()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            check_page(db, page_id)
            if not db.execute('SELECT 1 FROM custom_views WHERE database_id=? AND id=?',
                              (body.database_id, body.view_id)).fetchone():
                raise HTTPException(404, '이 데이터베이스에서 보기를 찾을 수 없습니다.')
            db.execute('''INSERT INTO page_database_views(id,page_id,database_id,view_id)
                          VALUES(?,?,?,?) ON CONFLICT(page_id,view_id) DO NOTHING''',
                       (str(uuid4()), page_id, body.database_id, body.view_id))
            row = db.execute('SELECT id,database_id,view_id FROM page_database_views WHERE page_id=? AND view_id=?',
                             (page_id, body.view_id)).fetchone()
            return dict(row)

    @app.delete('/api/v1/pages/{page_id}/linked-views/{link_id}')
    def remove_link(page_id: str, link_id: str, body: UnlinkRequest):
        with closing(store.conn()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            check_page(db, page_id)
            db.execute('DELETE FROM page_database_views WHERE page_id=? AND id=?', (page_id, link_id))
        return {'status': 'unlinked'}

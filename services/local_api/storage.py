"""SQLite local-private storage. No file upload, network, or shared-workspace persistence."""
from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


def default_db_path() -> Path:
    override = os.environ.get("EAW_DATA_DIR")
    if override:
        root = Path(override).expanduser()
    elif os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "EnterpriseAIWorkspace"
    else:
        root = Path.home() / ".local" / "share" / "enterprise-ai-workspace"
    return root / "workspace.db"


class LocalStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.conn() as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS documents (
                 id TEXT PRIMARY KEY,
                 template_id TEXT NOT NULL,
                 template_version INTEGER NOT NULL,
                 title TEXT NOT NULL,
                 field_values TEXT NOT NULL,
                 revision INTEGER NOT NULL DEFAULT 1,
                 scope TEXT NOT NULL DEFAULT 'local_private' CHECK (scope='local_private'),
                 created_at TEXT NOT NULL,
                 updated_at TEXT NOT NULL
              );
              CREATE INDEX IF NOT EXISTS idx_docs_updated ON documents(updated_at DESC);
            """)

    def conn(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def all_docs(self, query: str = "") -> list[dict[str, Any]]:
        sql = "SELECT id,template_id,template_version,title,revision,scope,created_at,updated_at FROM documents"
        params: tuple[Any, ...] = ()
        if query:
            sql += " WHERE title LIKE ? ESCAPE '\\' "
            params = ('%' + query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_') + '%',)
        sql += " ORDER BY updated_at DESC LIMIT 100"
        with self.conn() as db:
            return [dict(row) for row in db.execute(sql, params).fetchall()]

    def get_doc(self, doc_id: str) -> dict[str, Any] | None:
        with self.conn() as db:
            row = db.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        if not row: return None
        out = dict(row)
        out['values'] = json.loads(out.pop('field_values'))
        return out

    def create_doc(self, doc_id: str, template_id: str, version: int, title: str, values: dict[str,str]) -> dict[str, Any]:
        now=datetime.now(timezone.utc).isoformat()
        with self.conn() as db:
            db.execute("INSERT INTO documents(id,template_id,template_version,title,field_values,revision,scope,created_at,updated_at) VALUES(?,?,?,?,?,1,'local_private',?,?)",
                       (doc_id,template_id,version,title,json.dumps(values,ensure_ascii=False),now,now))
            db.commit()
        return self.get_doc(doc_id)

    def update_doc(self, doc_id: str, expected_revision: int, title: str, values: dict[str,str]) -> tuple[str, dict[str,Any] | None]:
        now=datetime.now(timezone.utc).isoformat()
        with self.conn() as db:
            cur=db.execute("UPDATE documents SET title=?,field_values=?,revision=revision+1,updated_at=? WHERE id=? AND revision=?",
                           (title,json.dumps(values,ensure_ascii=False),now,doc_id,expected_revision))
            db.commit()
        if cur.rowcount == 1: return 'updated',self.get_doc(doc_id)
        if self.get_doc(doc_id) is None: return 'not_found',None
        return 'conflict',None

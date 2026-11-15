-- Synthetic fixture generated with the original v0.11 stores.
BEGIN TRANSACTION;
CREATE TABLE calendar_events (
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
INSERT INTO "calendar_events" VALUES('ea84e7fc-edb6-4027-9a89-4777132dd251','Synthetic legacy event','2026-12-14','2026-12-15','2026-12-14','2026-12-15',1,'Asia/Seoul','00000000-0000-4000-8000-000000000012',NULL,1,'2026-11-15T06:17:14.416667+00:00','2026-11-15T06:17:14.416667+00:00');
CREATE TABLE documents (
                 id TEXT PRIMARY KEY,
                 template_id TEXT NOT NULL,
                 template_version INTEGER NOT NULL,
                 title TEXT NOT NULL,
                 field_values TEXT NOT NULL,
                 revision INTEGER NOT NULL DEFAULT 1,
                 scope TEXT NOT NULL DEFAULT 'local_private' CHECK (scope='local_private'),
                 created_at TEXT NOT NULL,
                 updated_at TEXT NOT NULL
              , parent_id TEXT REFERENCES documents(id));
INSERT INTO "documents" VALUES('00000000-0000-4000-8000-000000000011','general-meeting',1,'Synthetic legacy agenda','{"agenda": "Legacy template values"}',1,'local_private','2026-11-15T06:17:14.405297+00:00','2026-11-15T06:17:14.405297+00:00',NULL);
INSERT INTO "documents" VALUES('00000000-0000-4000-8000-000000000012','__blank_page__',1,'Synthetic child','{}',2,'local_private','2026-11-15T06:17:14.407539+00:00','2026-11-15T06:17:14.409286+00:00','00000000-0000-4000-8000-000000000011');
CREATE TABLE page_blocks (
                    id TEXT PRIMARY KEY,
                    page_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    block_type TEXT NOT NULL CHECK(block_type IN
                        ('paragraph','heading_1','heading_2','bullet','todo','toggle','quote','code','divider')),
                    content TEXT NOT NULL DEFAULT '',
                    checked INTEGER NOT NULL DEFAULT 0 CHECK(checked IN (0,1)),
                    UNIQUE(page_id,position)
                );
INSERT INTO "page_blocks" VALUES('00000000-0000-4000-8000-000000000013','00000000-0000-4000-8000-000000000012',0,'todo','Preserve this checked item',1);
-- The v0.11 API admitted any 36 characters matching [a-f0-9-].
INSERT INTO "page_blocks" VALUES('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','00000000-0000-4000-8000-000000000012',1,'paragraph','Preserve old block IDs',0);
CREATE TABLE projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL CHECK(status IN ('planned','active','on_hold','completed')),
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
INSERT INTO "projects" VALUES('394d36b9-0dbb-4cb8-a5d5-ae82d6bb8e1e','Synthetic legacy project','Project from v0.11','active',1,'2026-11-15T06:17:14.412219+00:00','2026-11-15T06:17:14.412219+00:00');
CREATE TABLE tasks (
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
INSERT INTO "tasks" VALUES('4fb422ba-97af-4bdc-8891-1c8faadbbc06','394d36b9-0dbb-4cb8-a5d5-ae82d6bb8e1e','00000000-0000-4000-8000-000000000011','Synthetic legacy task','todo','high','2026-12-15',1,'2026-11-15T06:17:14.414438+00:00','2026-11-15T06:17:14.414438+00:00');
CREATE INDEX idx_docs_updated ON documents(updated_at DESC);
CREATE INDEX idx_docs_parent ON documents(parent_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_due ON tasks(due_on);
CREATE INDEX idx_event_dates ON calendar_events(start_date,end_date);
CREATE INDEX idx_page_blocks ON page_blocks(page_id,position);
COMMIT;

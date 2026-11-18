<!-- METADATA: {"source_path": "services/local_api/workspace_store.py", "source_sha": "e260c5e9d0f359919406dbe7a7a5b1b70f74089e", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:20:15Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "services/local_api/workspace_store.py",
  "source_hash": "41129a989d68a3b351252ab890b43c174f7bce933a33080d13aba213716d5837",
  "last_updated": "2026-11-18T03:18:57.885095+00:00",
  "git_sha": "e260c5e9d0f359919406dbe7a7a5b1b70f74089e",
  "tokens_used": 23847,
  "complexity_score": 8,
  "estimated_review_time_minutes": 40,
  "external_dependencies": [
    "__future__",
    "datetime",
    "pathlib",
    "json",
    "re",
    "sqlite3",
    "typing",
    "unicodedata",
    "uuid"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [services](../README.md) > [local_api](./README.md) > **workspace_store**

---

# workspace_store.py

> **File:** `services/local_api/workspace_store.py`

![Complexity: High](https://img.shields.io/badge/Complexity-High-red) ![Review Time: 40min](https://img.shields.io/badge/Review_Time-40min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module implements a local-first workspace storage component for structured data. It defines a WorkspaceStore class that extends a LocalStore base and is responsible for managing workspace-related data without network, media, or external integrations. The module also provides small utilities and constants used by the store, including a now_utc function for consistent UTC timestamps, a UUID regular expression pattern, and a map of default task properties to ensure consistent task records.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `__future__` | from __future__ import annotations |
| `datetime` | from datetime import date, datetime, timezone, timedelta |
| `pathlib` | from pathlib import Path |
| `json` | import json |
| `re` | import re |
| `sqlite3` | import sqlite3 |
| `typing` | from typing import Any |
| `unicodedata` | from unicodedata import normalize |
| `uuid` | from uuid import uuid4 |

### Internal Dependencies

| Module | Usage |
| --- | --- |
| `storage` | from .storage import LocalStore |

## 📁 Directory

This file is part of the **local_api** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Subclassing: WorkspaceStore extends a LocalStore base class to specialize local storage behavior.
- Use of sqlite3 for embedded local persistence.
- Explicit handling of identifiers and normalization via uuid4 and unicodedata.normalize.
- Definition of module-level constants for defaults and validation (UTC, UUID_PATTERN, TASK_PROPERTY_DEFAULTS).

## Maintenance Notes

- Provide a WorkspaceStore implementation that inherits from LocalStore and encapsulates local workspace persistence and operations.
- Offer a now_utc helper for obtaining timezone-aware UTC timestamps used by the store.
- Define shared constants used by the store and its clients, including a canonical UUID regex (UUID_PATTERN) and TASK_PROPERTY_DEFAULTS for task record initialization.
- Use sqlite3, uuid4, and unicode normalization utilities to manage local storage, generate identifiers, and normalize textual data.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `UTC` | — | `timezone.utc` |
| `UUID_PATTERN` | — | `'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'` |
| `TASK_PROPERTY_DEFAULTS` | `dict[str, Any]` | `{'effort': None, 'labels': '[]', 'flagged': 0, 'reference_url': '', 'notes': ''}` |



---

## Functions and Classes


### now_utc

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def now_utc() -> str:
```

#### Description

Return the current time in UTC as a string.

The function provides a simple way to get the current UTC timestamp from the workspace store module.

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### WorkspaceStore

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Methods: 47](https://img.shields.io/badge/Methods-47-blue)

#### Description

WorkspaceStore is a local store implementation responsible for managing workspace documents, pages, projects, tasks, and related metadata.

Within services/local_api/workspace_store.py, WorkspaceStore acts as the central class that encapsulates local persistence and manipulation logic for workspace-related resources, serving as the main interface other parts of the local API use to interact with documents, pages, projects, and tasks.

Responsibilities:
- List, retrieve, create, update, duplicate, move, trash and restore documents and pages (all_docs, get_doc, create_doc, update_doc, duplicate_page, move_page, trash_page, restore_trashed_page, create_template_page).
- Search and query workspace content and task-related data (search_pages, search_tasks, tasks, task, list_trash).
- Manage project entities including listing, retrieving, creating and updating projects (list_projects, project, create_project, update_project).
- Handle task creation, decoding, updating and validation of references (create_task, update_task, _decode_task, _task_properties, _check_refs).
- Read and update page properties, tags and event handling for workspace changes ( _read_properties, update_page_properties, page_tags, event).

#### Inheritance

**Inherits from:** `LocalStore`

#### Methods

##### Public Methods

| Method | Type | Description |
| --- | --- | --- |
| `__init__` | instance | Method __init__.<br>**Signature:** `def __init__(self, path: Path):` |
| `all_docs` | instance | Method all_docs.<br>**Signature:** `def all_docs(self, query: str = '', *, for_tree: bool = False) -> list[dict[str, Any]]:` |
| `search_pages` | instance | Method search_pages.<br>**Signature:** `def search_pages(self, query: str, limit: int = 100, *, tag: str = '') -> list[dict[str, Any]]:` |
| `search_tasks` | instance | Method search_tasks.<br>**Signature:** `def search_tasks(self, query: str) -> list[dict[str, Any]]:` |
| `get_doc` | instance | Method get_doc.<br>**Signature:** `def get_doc(self, doc_id: str) -> dict[str, Any] | None:` |
| `list_trash` | instance | Method list_trash.<br>**Signature:** `def list_trash(self) -> list[dict[str, Any]]:` |
| `trash_page` | instance | Method trash_page.<br>**Signature:** `def trash_page(self, page_id: str, expected_revision: int) -> str:` |
| `restore_trashed_page` | instance | Method restore_trashed_page.<br>**Signature:** `def restore_trashed_page(self, page_id: str, expected_revision: int) -> str:` |
| `update_page_properties` | instance | Method update_page_properties.<br>**Signature:** `def update_page_properties(self, page_id: str, revision: int, changes: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:` |
| `page_tags` | instance | Method page_tags.<br>**Signature:** `def page_tags(self) -> list[dict[str, Any]]:` |
| `create_doc` | instance | Method create_doc.<br>**Signature:** `def create_doc(self, doc_id: str, template_id: str, version: int, title: str, values: dict[str, str], parent_id: str | None = None, *, blocks: list[dict[str, Any]] | None = None) -> dict[str, Any]:` |
| `create_template_page` | instance | Method create_template_page.<br>**Signature:** `def create_template_page(self, template_id: str, version: int, title: str, parent_id: str | None, request_id: str, blocks: list[dict[str, Any]], tags: list[str]) -> tuple[str, dict[str, Any] | None]:` |
| `duplicate_page` | instance | Method duplicate_page.<br>**Signature:** `def duplicate_page(self, page_id: str, expected_revision: int, request_id: str) -> tuple[str, dict[str, Any] | None]:` |
| `move_page` | instance | Method move_page.<br>**Signature:** `def move_page(self, doc_id: str, expected_revision: int, parent_id: str | None) -> tuple[str, dict[str, Any] | None]:` |
| `update_doc` | instance | Method update_doc.<br>**Signature:** `def update_doc(self, doc_id: str, expected_revision: int, title: str, values: dict[str, str]) -> tuple[str, dict[str, Any] | None]:` |
| `list_projects` | instance | Method list_projects.<br>**Signature:** `def list_projects(self):` |
| `project` | instance | Method project.<br>**Signature:** `def project(self, project_id: str):` |
| `create_project` | instance | Method create_project.<br>**Signature:** `def create_project(self, title: str, description: str, status: str):` |
| `update_project` | instance | Method update_project.<br>**Signature:** `def update_project(self, ident: str, expected_revision: int, title: str, description: str, status: str):` |
| `tasks` | instance | Method tasks.<br>**Signature:** `def tasks(self, project_id: str | None = None):` |
| `task` | instance | Method task.<br>**Signature:** `def task(self, ident: str):` |
| `create_task` | instance | Method create_task.<br>**Signature:** `def create_task(self, **data):` |
| `update_task` | instance | Method update_task.<br>**Signature:** `def update_task(self, ident: str, expected_revision: int, **data):` |
| `event` | instance | Method event.<br>**Signature:** `def event(self, ident: str):` |
| `events_between` | instance | Method events_between.<br>**Signature:** `def events_between(self, start_date: str, end_date: str):` |
| `calendar_feed` | instance | Method calendar_feed.<br>**Signature:** `def calendar_feed(self, start_date: str, end_date: str):` |
| `create_event` | instance | Method create_event.<br>**Signature:** `def create_event(self, **data):` |
| `update_event` | instance | Method update_event.<br>**Signature:** `def update_event(self, ident: str, expected_revision: int, **data):` |
| `get_canvas` | instance | Method get_canvas.<br>**Signature:** `def get_canvas(self, page_id: str) -> dict[str, Any] | None:` |
| `list_page_history` | instance | Method list_page_history.<br>**Signature:** `def list_page_history(self, page_id: str, before_revision: int | None) -> list[dict[str, Any]] | None:` |
| `get_page_history` | instance | Method get_page_history.<br>**Signature:** `def get_page_history(self, page_id: str, revision: int) -> dict[str, Any] | None:` |
| `restore_page_revision` | instance | Method restore_page_revision.<br>**Signature:** `def restore_page_revision(self, page_id: str, expected_revision: int, revision: int) -> tuple[str, dict[str, Any] | None]:` |
| `update_canvas` | instance | Method update_canvas.<br>**Signature:** `def update_canvas(self, page_id: str, expected_revision: int, title: str, blocks: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:` |

##### Protected Methods

| Method | Type | Description |
| --- | --- | --- |
| `_read_properties` | static | Method _read_properties.<br>**Signature:** `def _read_properties(db: sqlite3.Connection, page_id: str) -> dict[str, Any]:` |
| `_doc_payload` | static | Method _doc_payload.<br>**Signature:** `def _doc_payload(page: dict[str, Any]) -> dict[str, Any]:` |
| `_insert_doc` | static | Method _insert_doc.<br>**Signature:** `def _insert_doc(db: sqlite3.Connection, doc_id: str, template_id: str, version: int, title: str, values: dict[str, str], parent_id: str | None) -> None:` |
| `_decode_task` | static | Method _decode_task.<br>**Signature:** `def _decode_task(row: sqlite3.Row) -> dict[str, Any]:` |
| `_task_properties` | static | Method _task_properties.<br>**Signature:** `def _task_properties(data: dict[str, Any], current: sqlite3.Row | None = None) -> tuple[Any, ...]:` |
| `_check_refs` | static | Method _check_refs.<br>**Signature:** `def _check_refs(db: sqlite3.Connection, project_id: str | None, document_id: str | None):` |
| `_check_event_links` | static | Method _check_event_links.<br>**Signature:** `def _check_event_links(db: sqlite3.Connection, data: dict):` |
| `_read_canvas` | static | Method _read_canvas.<br>**Signature:** `def _read_canvas(db: sqlite3.Connection, page_id: str) -> dict[str, Any] | None:` |
| `_write_blocks` | static | Method _write_blocks.<br>**Signature:** `def _write_blocks(db: sqlite3.Connection, page_id: str, blocks: list[dict[str, Any]]) -> None:` |
| `_history_snapshot` | static | Method _history_snapshot.<br>**Signature:** `def _history_snapshot(page: dict[str, Any]) -> dict[str, Any]:` |
| `_record_history` | instance | Method _record_history.<br>**Signature:** `def _record_history(self, db: sqlite3.Connection, page: dict[str, Any]) -> None:` |
| `_read_page_snapshot` | static | Method _read_page_snapshot.<br>**Signature:** `def _read_page_snapshot(db: sqlite3.Connection, page_id: str, revision: int) -> dict[str, Any] | None:` |
| `_has_foreign_block` | static | Method _has_foreign_block.<br>**Signature:** `def _has_foreign_block(db: sqlite3.Connection, page_id: str, blocks: list[dict[str, Any]]) -> bool:` |
| `_write_canvas_revision` | instance | Method _write_canvas_revision.<br>**Signature:** `def _write_canvas_revision(self, db: sqlite3.Connection, current: dict[str, Any], title: str, blocks: list[dict[str, Any]], *, values: dict[str, str] | None = None) -> dict[str, Any]:` |

---



### __init__

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def __init__(self, path: Path):
```

#### Description

Initialize a WorkspaceStore instance using the given filesystem path.

This constructor records the provided Path and performs any setup required for the workspace store to operate at that location.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | `Path` | ✅ | — |

#### Complexity

Not analyzed

---



### all_docs

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def all_docs(self, query: str = '', *, for_tree: bool = False) -> list[dict[str, Any]]:
```

#### Description

Retrieve and return a list of document records from the workspace store, optionally filtered by a query string and formatted for use in a tree view when for_tree is True.

The function collects documents matching the provided criteria and returns them as a list of dictionaries.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` = `''` | `str` | ❌ | — |
| `for_tree` = `False` | `bool` | ❌ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### search_pages

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def search_pages(self, query: str, limit: int = 100, *, tag: str = '') -> list[dict[str, Any]]:
```

#### Description

Searches stored pages in the workspace for entries that match the given query, optionally filtering by a tag and limiting the number of results.

The method uses several nested helper functions (text_matches, fields_match, block_matches, tag_matches) to determine whether a page satisfies the search criteria and returns matching page records up to the specified limit.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `str` | ✅ | — |
| `limit` = `100` | `int` | ❌ | — |
| `tag` = `''` | `str` | ❌ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### text_matches

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def text_matches(value: str) -> bool:
```

#### Description

Determine whether the provided string meets the match criteria used by the search_pages routine in the workspace store.

It evaluates the given text and returns a boolean indicating whether it is considered a match.


value is the text string to be tested for a match against the search criteria.

Returns True if the provided string matches the search criteria, otherwise False.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `str` | ✅ | — |

#### Returns

**Type:** `bool`

Returns True if the provided string matches the search criteria, otherwise False.

#### Complexity

Not analyzed

---



### fields_match

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def fields_match(raw_values: str) -> bool:
```

#### Description

Determines whether the provided raw_values string satisfies the field-matching criteria used by the WorkspaceStore.search_pages operation.

It evaluates the input text and returns True when the raw_values meet the expected match conditions and False otherwise.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `raw_values` | `str` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### block_matches

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def block_matches(content: str, is_table: int) -> bool:
```

#### Description

Determine whether a given workspace block should be considered a match for a search or filter based on its textual content and whether it represents a table.

The function inspects the provided content and the is_table flag to decide if the block qualifies as a matching item.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `content` | `str` | ✅ | — |
| `is_table` | `int` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### tag_matches

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def tag_matches(raw_tags: str | None, exact: int) -> bool:
```

#### Description

Determines whether a provided raw tag string satisfies the tag-matching criteria used by the search_pages routine.

The function uses the numeric exact flag to control whether matching requires an exact tag match or can be a looser/partial match.


raw_tags is the tag data as a string (or None) to be tested; exact is an integer flag that indicates whether matching should be exact (e.g., exact=1) or non-exact/partial (e.g., exact=0).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `raw_tags` | `str | None` | ✅ | — |
| `exact` | `int` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### search_tasks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def search_tasks(self, query: str) -> list[dict[str, Any]]:
```

#### Description

Search the store's tasks for entries that match the provided query string and return the matching task records.

The function uses an internal helper task_matches to test whether each task satisfies the query and collects those that do into a list.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `str` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### task_matches

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def task_matches(title: str, notes: str, labels: str) -> bool:
```

#### Description

Determine whether a task described by the given title, notes, and labels satisfies the search criteria used by WorkspaceStore.search_tasks; returns True when the task matches and False otherwise.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | `str` | ✅ | — |
| `notes` | `str` | ✅ | — |
| `labels` | `str` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### get_doc

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_doc(self, doc_id: str) -> dict[str, Any] | None:
```

#### Description

Retrieve a document from the workspace store by its identifier.

The method looks up the document with the given doc_id and returns its data as a dictionary, or None if no document with that id exists.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `doc_id` | `str` | ✅ | — |

#### Returns

**Type:** `dict[str, Any] | None`

—

#### Complexity

Not analyzed

---



### list_trash

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_trash(self) -> list[dict[str, Any]]:
```

#### Description

Return a listing of items currently in the workspace trash.

This method retrieves and returns metadata for each trashed workspace item so callers can inspect or act on those entries.

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### trash_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def trash_page(self, page_id: str, expected_revision: int) -> str:
```

#### Description

Move or mark a page identified by page_id as trashed within the workspace store, performing the operation only if the current revision matches expected_revision to avoid conflicts.

It likely updates internal state and returns a string result such as the new revision id or a status indicator.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### restore_trashed_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_trashed_page(self, page_id: str, expected_revision: int) -> str:
```

#### Description

Restore a page that was previously moved to the trash in the workspace store, using the provided page identifier and an expected revision number to validate the operation.

The method performs the restoration and returns an identifier or status string indicating the result of the restore.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### _read_properties

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _read_properties(db: sqlite3.Connection, page_id: str) -> dict[str, Any]:
```

#### Description

Open and query the given SQLite connection to load and return the stored properties for the workspace page identified by page_id.

It gathers the page's properties from the database and returns them as a Python dictionary.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page_id` | `str` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### update_page_properties

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_page_properties(self, page_id: str, revision: int, changes: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Apply a set of property changes to a stored page identified by page_id at a specific revision.

The method attempts to update the page's properties with the provided changes and returns a status plus any resulting data about the update.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |
| `changes` | `dict[str, Any]` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

—

#### Complexity

Not analyzed

---



### page_tags

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def page_tags(self) -> list[dict[str, Any]]:
```

#### Description

Retrieve and return a collection of tag records associated with the workspace.

The method gathers tag data and presents it as a list of dictionaries, each dictionary representing one tag's attributes.

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### create_doc

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_doc(self, doc_id: str, template_id: str, version: int, title: str, values: dict[str, str], parent_id: str | None = None, *, blocks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
```

#### Description

Create a new document entry in the workspace store using the given document id, template id and template version, along with a title and a mapping of template values.

Optionally associate the document with a parent document and supply explicit content blocks.


doc_id, template_id, version, title, and values are required; parent_id is an optional parent document identifier, and blocks (keyword-only) is an optional list of block dictionaries that can provide the document's content structure.

A dictionary representing the created document record (its stored fields and metadata).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `doc_id` | `str` | ✅ | — |
| `template_id` | `str` | ✅ | — |
| `version` | `int` | ✅ | — |
| `title` | `str` | ✅ | — |
| `values` | `dict[str, str]` | ✅ | — |
| `parent_id` = `None` | `str | None` | ❌ | — |
| `blocks` = `None` | `list[dict[str, Any]] | None` | ❌ | — |

#### Returns

**Type:** `dict[str, Any]`

A dictionary representing the created document record (its stored fields and metadata).

#### Complexity

Not analyzed

---



### _doc_payload

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _doc_payload(page: dict[str, Any]) -> dict[str, Any]:
```

#### Description

Constructs and returns a document payload dictionary derived from the provided page mapping.

It transforms or extracts the necessary fields from the input page dict into the shape expected by the workspace store for downstream use.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `dict[str, Any]` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _insert_doc

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _insert_doc(db: sqlite3.Connection, doc_id: str, template_id: str, version: int, title: str, values: dict[str, str], parent_id: str | None) -> None:
```

#### Description

Insert a document record into the workspace SQLite database using the provided connection and metadata.

It takes the document identifier, associated template and version, a title, a mapping of field values, and an optional parent document id, and writes that information into the database.


values is a mapping of field names to their string values to be stored with the document; parent_id, if provided, links this document to a parent document in the workspace hierarchy. Other parameters are self-explanatory given their names and types.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `doc_id` | `str` | ✅ | — |
| `template_id` | `str` | ✅ | — |
| `version` | `int` | ✅ | — |
| `title` | `str` | ✅ | — |
| `values` | `dict[str, str]` | ✅ | — |
| `parent_id` | `str | None` | ✅ | — |

#### Complexity

Not analyzed

---



### create_template_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_template_page(self, template_id: str, version: int, title: str, parent_id: str | None, request_id: str, blocks: list[dict[str, Any]], tags: list[str]) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Creates a new page in the workspace based on a specified template version, using the provided title, optional parent page, content blocks, and tags, and associates the operation with a request ID.

It returns an identifier for the created page and any additional metadata produced by the operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `template_id` | `str` | ✅ | — |
| `version` | `int` | ✅ | — |
| `title` | `str` | ✅ | — |
| `parent_id` | `str | None` | ✅ | — |
| `request_id` | `str` | ✅ | — |
| `blocks` | `list[dict[str, Any]]` | ✅ | — |
| `tags` | `list[str]` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

—

#### Complexity

Not analyzed

---



### duplicate_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def duplicate_page(self, page_id: str, expected_revision: int, request_id: str) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Create a duplicate of an existing page identified by page_id, using expected_revision to ensure the source page is at the expected version and request_id to correlate or make the request idempotent.

The method returns identifying information about the created duplicate and any associated metadata or error details.


page_id is the identifier of the page to duplicate; expected_revision is used for optimistic concurrency control to ensure the source page has the expected revision before duplicating; request_id is used to trace or make the operation idempotent across retries.

Returns a tuple where the first element is a string (typically the new duplicate page's identifier) and the second element is an optional dictionary with additional information or None.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `request_id` | `str` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

Returns a tuple where the first element is a string (typically the new duplicate page's identifier) and the second element is an optional dictionary with additional information or None.

#### Complexity

Not analyzed

---



### move_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def move_page(self, doc_id: str, expected_revision: int, parent_id: str | None) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Move a page (document) identified by doc_id to a new parent within the workspace, using expected_revision to ensure the caller has the correct current revision before performing the move.

The function returns information about the result of the operation.


Returns a tuple where the first element is a string (e.g., a new revision id or status token) and the second element is either a dictionary with additional result/metadata or None.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `doc_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `parent_id` | `str | None` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

Returns a tuple where the first element is a string (e.g., a new revision id or status token) and the second element is either a dictionary with additional result/metadata or None.

#### Complexity

Not analyzed

---



### update_doc

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_doc(self, doc_id: str, expected_revision: int, title: str, values: dict[str, str]) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Update an existing document in the workspace store identified by doc_id, validating that the current revision matches expected_revision, and applying a new title and a mapping of string values.

It returns an identifier (likely the new revision or status) and an optional dictionary with additional details or metadata about the update.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `doc_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `title` | `str` | ✅ | — |
| `values` | `dict[str, str]` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

—

#### Complexity

Not analyzed

---



### list_projects

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_projects(self):
```

#### Description

Enumerates and returns the projects known to this WorkspaceStore instance, retrieving the stored project entries for the workspace.

A collection (for example, a list) of project records or identifiers representing the projects present in the workspace.

#### Complexity

Not analyzed

---



### project

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def project(self, project_id: str):
```

#### Description

Retrieve and return the project record with the given project_id from the workspace store.

This method looks up the stored project corresponding to the provided identifier and returns it for use by callers.


Returns the project object corresponding to project_id (or a falsy/None value if no such project exists).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### create_project

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_project(self, title: str, description: str, status: str):
```

#### Description

Create a new project entry in the workspace store using the provided title, description, and status.

This method encapsulates the creation logic for adding a project to the store managed by the WorkspaceStore instance.


Returns the created project representation or identifier (the exact return type is determined by the store's implementation).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | `str` | ✅ | — |
| `description` | `str` | ✅ | — |
| `status` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### update_project

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_project(self, ident: str, expected_revision: int, title: str, description: str, status: str):
```

#### Description

Update the project identified by ident with new title, description, and status, using expected_revision for optimistic concurrency control.

This method applies the provided changes to the stored project record within the workspace store.


Returns the updated project representation after applying the changes (exact return type is not specified in the signature).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ident` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `title` | `str` | ✅ | — |
| `description` | `str` | ✅ | — |
| `status` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### tasks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def tasks(self, project_id: str | None = None):
```

#### Description

Retrieve tasks that belong to the workspace, optionally filtering them to only those associated with a specific project.

When project_id is provided, the method limits the returned tasks to that project; otherwise it returns tasks across the workspace.


Returns the collection of tasks from the workspace, filtered by project_id when supplied.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` = `None` | `str | None` | ❌ | — |

#### Complexity

Not analyzed

---



### task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def task(self, ident: str):
```

#### Description

Retrieve and return a stored task from the workspace store identified by the given identifier.

The method looks up the task resource corresponding to the provided string id and returns it to the caller.


Returns the task object or record associated with the provided identifier, or None if no such task exists.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ident` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### _decode_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _decode_task(row: sqlite3.Row) -> dict[str, Any]:
```

#### Description

Convert a sqlite3.Row representing a stored task into a plain Python dictionary with the task's fields and values.

This helper extracts columns from the database row and returns a dictionary suitable for use elsewhere in the application.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `row` | `sqlite3.Row` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _task_properties

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _task_properties(data: dict[str, Any], current: sqlite3.Row | None = None) -> tuple[Any, ...]:
```

#### Description

Prepare a sequence of task property values derived from the provided data dictionary (and optional existing row) for use in database operations.

It consolidates incoming task fields and falls back to values from the current sqlite3.Row when necessary, returning them as an ordered tuple.


data is a dictionary of task attributes to apply; current is an optional sqlite3.Row representing the existing database row used to supply defaults or preserve unchanged fields.

Returns an ordered tuple of values (tuple[Any, ...]) suitable for use in SQL INSERT/UPDATE parameter binding.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `dict[str, Any]` | ✅ | — |
| `current` = `None` | `sqlite3.Row | None` | ❌ | — |

#### Returns

**Type:** `tuple[Any, ...]`

Returns an ordered tuple of values (tuple[Any, ...]) suitable for use in SQL INSERT/UPDATE parameter binding.

#### Complexity

Not analyzed

---



### create_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_task(self, **data):
```

#### Description

Create a new task record in the workspace store using the keyword arguments provided.

The method accepts arbitrary task attributes via the data mapping and persists or registers a task entry associated with this WorkspaceStore instance.


The data parameter is a dict of keyword attributes describing the task to create (e.g., title, description, metadata); each key/value pair is used to populate the new task record.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### update_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_task(self, ident: str, expected_revision: int, **data):
```

#### Description

Update an existing task in the workspace store identified by ident, applying the provided fields in data while enforcing optimistic concurrency using expected_revision.

The signature does not specify a return type; it likely returns the updated task representation or a status indicating success (or may raise on conflict), but the exact return value is not specified here.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ident` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `data` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### _check_refs

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _check_refs(db: sqlite3.Connection, project_id: str | None, document_id: str | None):
```

#### Description

Perform internal validation of database references related to a workspace entity, using the given SQLite connection and optional project or document identifiers.

It ensures any references for the provided project_id or document_id are checked before operations that depend on referential integrity.


Returns None; it is used for side-effect validation and may raise an exception if referenced constraints or checks fail.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `project_id` | `str | None` | ✅ | — |
| `document_id` | `str | None` | ✅ | — |

#### Complexity

Not analyzed

---



### event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def event(self, ident: str):
```

#### Description

Provide access to an event object or event stream associated with a workspace identified by the given identifier.

It looks up (and possibly creates or returns) the event handle tied to that workspace so callers can subscribe to or emit workspace-related events.


Returns the event object or handler corresponding to the workspace identified by the ident string (the exact event type or interface is not specified here).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ident` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### events_between

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def events_between(self, start_date: str, end_date: str):
```

#### Description

Retrieve or collect workspace events that occur on or between the two given dates.

The method accepts a start and end date (as strings) and returns the events that fall within that inclusive range.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `start_date` | `str` | ✅ | — |
| `end_date` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### calendar_feed

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def calendar_feed(self, start_date: str, end_date: str):
```

#### Description

Generate and return a calendar feed for this workspace covering the inclusive date range between start_date and end_date.

It gathers the workspace's scheduled items (such as events, tasks, or bookings) that fall within the provided date range and packages them into a feed suitable for consumption by calendar clients or APIs.


Returns the calendar feed data for the specified range — typically a collection (e.g., list) of event/entry objects or dictionaries representing the workspace calendar items that occur between start_date and end_date.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `start_date` | `str` | ✅ | — |
| `end_date` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### create_event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_event(self, **data):
```

#### Description

Create a new event record in the workspace store using the provided keyword arguments.

The method accepts arbitrary event-related fields via kwargs and persists them into the store associated with this WorkspaceStore instance.


data is a catch-all for event attributes supplied as keyword arguments (for example: timestamp, type, payload, user_id); the exact accepted keys depend on the workspace store's event schema.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### update_event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_event(self, ident: str, expected_revision: int, **data):
```

#### Description

Update an existing event record identified by ident with the supplied keyword data, using optimistic concurrency control by checking that the current revision equals expected_revision before applying changes.

It applies the provided fields to the stored event and persists the updated state.


ident is the unique identifier of the event to update; expected_revision is the revision number the caller believes the event is at and is used to prevent concurrent modifications. The variable keyword arguments (data) contain the fields and values to be updated on the event.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ident` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `data` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### _check_event_links

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _check_event_links(db: sqlite3.Connection, data: dict):
```

#### Description

Validate or verify event link information in the workspace using the provided SQLite database connection and the data dictionary.

This internal helper inspects the provided data and checks related records in the db to ensure event link consistency or correctness.


Returns None (performs its checks as a side effect; may raise an exception on validation failure).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `data` | `dict` | ✅ | — |

#### Complexity

Not analyzed

---



### _read_canvas

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _read_canvas(db: sqlite3.Connection, page_id: str) -> dict[str, Any] | None:
```

#### Description

Open and read the canvas data for a given page from the provided SQLite database connection and return it as a Python dictionary.

If the specified page does not exist in the database, return None.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page_id` | `str` | ✅ | — |

#### Returns

**Type:** `dict[str, Any] | None`

—

#### Complexity

Not analyzed

---



### _write_blocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _write_blocks(db: sqlite3.Connection, page_id: str, blocks: list[dict[str, Any]]) -> None:
```

#### Description

Persist a list of block records into the SQLite database for the specified page.

This static helper takes a database connection, a page identifier, and a list of block dictionaries, and writes those blocks into the underlying storage associated with that page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `blocks` | `list[dict[str, Any]]` | ✅ | — |

#### Complexity

Not analyzed

---



### _history_snapshot

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _history_snapshot(page: dict[str, Any]) -> dict[str, Any]:
```

#### Description

Create and return a snapshot representation of a history page.

It takes a page dictionary and produces a new dictionary representing that page's snapshot state (e.g., for storage or serialization).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `dict[str, Any]` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _record_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _record_history(self, db: sqlite3.Connection, page: dict[str, Any]) -> None:
```

#### Description

Insert or update an entry in the workspace history table using the provided SQLite connection and the given page data.

In other words, persist the page's state or metadata into the database history for later retrieval.


db is an open sqlite3.Connection used to execute the database writes; page is a dictionary containing the page's data or metadata that should be recorded into the history (e.g., identifiers, timestamps, and content).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page` | `dict[str, Any]` | ✅ | — |

#### Complexity

Not analyzed

---



### get_canvas

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_canvas(self, page_id: str) -> dict[str, Any] | None:
```

#### Description

Retrieve the canvas data for a specific page from the workspace store using the page's identifier.

The method looks up and returns the stored canvas representation associated with the given page_id, or None if no canvas exists for that page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |

#### Returns

**Type:** `dict[str, Any] | None`

—

#### Complexity

Not analyzed

---



### list_page_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_page_history(self, page_id: str, before_revision: int | None) -> list[dict[str, Any]] | None:
```

#### Description

Retrieve the revision history for a specific page.

It returns the stored history entries for the page identified by page_id, optionally limited to revisions earlier than the given before_revision.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `before_revision` | `int | None` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]] | None`

—

#### Complexity

Not analyzed

---



### get_page_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_page_history(self, page_id: str, revision: int) -> dict[str, Any] | None:
```

#### Description

Retrieve the stored history entry for a specific page at a given revision number from the local workspace store.

It looks up the historical record identified by the page_id and revision and returns the data if found.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |

#### Returns

**Type:** `dict[str, Any] | None`

—

#### Complexity

Not analyzed

---



### _read_page_snapshot

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _read_page_snapshot(db: sqlite3.Connection, page_id: str, revision: int) -> dict[str, Any] | None:
```

#### Description

Fetches a stored snapshot of a workspace page at a specific revision from the provided SQLite database connection.

It looks up the page identified by page_id and the given revision number and returns its stored data as a dictionary, or None if no matching snapshot exists.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |

#### Returns

**Type:** `dict[str, Any] | None`

—

#### Complexity

Not analyzed

---



### restore_page_revision

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_page_revision(self, page_id: str, expected_revision: int, revision: int) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Restore the stored page identified by page_id to the specified revision number, using expected_revision to check or enforce the current revision before performing the restore.

The method performs the restore operation and returns a status string and optional additional data about the operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `revision` | `int` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

—

#### Complexity

Not analyzed

---



### _has_foreign_block

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _has_foreign_block(db: sqlite3.Connection, page_id: str, blocks: list[dict[str, Any]]) -> bool:
```

#### Description

Checks whether any of the block entries in the provided list represent blocks that belong to a different page than the given page_id, using the provided sqlite database connection to validate ownership or association.

It returns True if at least one block is determined to be "foreign" relative to page_id, otherwise False.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `blocks` | `list[dict[str, Any]]` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### _write_canvas_revision

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _write_canvas_revision(self, db: sqlite3.Connection, current: dict[str, Any], title: str, blocks: list[dict[str, Any]], *, values: dict[str, str] | None = None) -> dict[str, Any]:
```

#### Description

Create or update a canvas revision record in the workspace store using the provided database connection.

It takes the current revision metadata, a new title and block list (and optional substitution values) and persists the updated revision, returning the resulting revision data as a dictionary.


db is the sqlite3 connection used for persistence; current is the existing revision metadata being updated; title is the revision title and blocks is the list of block dictionaries that make up the canvas. values is an optional mapping of string substitutions or extra string fields to apply when writing the revision.

Returns a dictionary representing the saved revision record (the created or updated canvas revision).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `current` | `dict[str, Any]` | ✅ | — |
| `title` | `str` | ✅ | — |
| `blocks` | `list[dict[str, Any]]` | ✅ | — |
| `values` = `None` | `dict[str, str] | None` | ❌ | — |

#### Returns

**Type:** `dict[str, Any]`

Returns a dictionary representing the saved revision record (the created or updated canvas revision).

#### Complexity

Not analyzed

---



### update_canvas

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_canvas(self, page_id: str, expected_revision: int, title: str, blocks: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
```

#### Description

Update the canvas data for a given page identified by page_id, using an expected revision for optimistic concurrency, and replacing the page's title and list of block objects.

The method applies the change and returns a status along with optional additional data (for example the updated page representation or error details).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `expected_revision` | `int` | ✅ | — |
| `title` | `str` | ✅ | — |
| `blocks` | `list[dict[str, Any]]` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, Any] | None]`

—

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

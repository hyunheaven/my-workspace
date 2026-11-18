<!-- METADATA: {"source_path": "tests/browser/workspace_v130.py", "source_sha": "938f08d830333fcdbceca0d6298ebb911fa07df7", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/browser/workspace_v130.py",
  "source_hash": "37952b61acb0f8f81c842846dcc54697b95c68619f7364b27e344a37ad5a7bad",
  "last_updated": "2026-11-18T03:20:56.132305+00:00",
  "git_sha": "938f08d830333fcdbceca0d6298ebb911fa07df7",
  "tokens_used": 3471,
  "complexity_score": 1,
  "estimated_review_time_minutes": 8,
  "external_dependencies": [
    "argparse",
    "contextlib",
    "pathlib",
    "sqlite3",
    "tempfile",
    "playwright.sync_api",
    "workspace_v012",
    "workspace_v120"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [tests](../README.md) > [browser](./README.md) > **workspace_v130**

---

# workspace_v130.py

> **File:** `tests/browser/workspace_v130.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 8min](https://img.shields.io/badge/Review_Time-8min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module provides browser-based acceptance tests and helper routines for validating database record and view history restoration in a web application. It declares a set of constants that name the database, records, views, and notes involved in the tests and imports test utilities for creating databases, views and properties, interacting with local test servers, and manipulating the browser via Playwright's synchronous API. The available functions exercise workflows such as opening linked pages, setting up test state, recording and restoring history, and inspecting view history, and they rely on SQLite and temporary directories to manage test fixtures and persistence.

The file is structured around small, focused functions that orchestrate end-to-end browser interactions and server-backed state changes. Test helpers from earlier workspace modules (workspace_v012 and workspace_v120) are reused for common operations like creating databases, adding markdown, and saving dialogs; Playwright is used to navigate UI elements and assert expected behaviors. The module is intended to be run as part of an acceptance test suite verifying that edit and restore operations behave correctly across records and views.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `argparse` | import argparse |
| `contextlib` | from contextlib import closing |
| `pathlib` | from pathlib import Path |
| `sqlite3` | import sqlite3 |
| `tempfile` | from tempfile import TemporaryDirectory |
| `playwright.sync_api` | from playwright.sync_api import Page, expect, sync_playwright |
| `workspace_v012` | from workspace_v012 import api_items, api_json, free_port, local_server |
| `workspace_v120` | from workspace_v120 import add_markdown, create_database, create_property, create_view, record_dialog, save_database_dialog |

## 📁 Directory

This file is part of the **browser** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses Playwright synchronous API for browser automation (Page, sync_playwright, expect).
- Reuses test helper functions from other workspace modules (workspace_v012 and workspace_v120).
- Combines filesystem and database fixtures with TemporaryDirectory and sqlite3 for test state management.
- Defines string constants for reuse across multiple test scenarios to describe databases, records and views.

## Maintenance Notes

- Define constants naming the test database, records, views, and note used for history and restore scenarios.
- Provide functions to open linked pages in the browser and to set up test state and fixtures for acceptance tests.
- Record and restore edit history for database records and verify the restoration behavior via browser interactions.
- Inspect and validate view history, including scenarios with filtered gallery views and their restoration outcomes.
- Coordinate use of local test servers, temporary directories, and SQLite to persist and manage test data during browser-based tests.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `DATABASE` | — | `'변경 이력 검증 · 합성 예시'` |
| `RECORD` | — | `'원본 레코드 · 합성 예시'` |
| `EDITED_RECORD` | — | `'수정 레코드 · 합성 예시'` |
| `ORIGINAL_NOTE` | — | `'복원하려는 합성 메모'` |
| `VIEW` | — | `'원본 갤러리 보기'` |
| `FILTERED_VIEW` | — | `'필터를 적용한 갤러리 보기'` |



---

## Functions and Classes


### open_linked_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def open_linked_page(page: Page, url: str, page_id: str) -> None:
```

#### Description

Open or navigate to a linked page in a browser test context using the provided Playwright Page object, targeting the given URL and associating the navigation with the supplied page identifier.

The function performs the operation without returning a value.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### setup

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def setup(page: Page, url: str) -> tuple[str, str, dict, dict]:
```

#### Description

Prepare a browser-based test workspace using the provided Playwright Page and target URL; performs whatever initialization is needed for the tests in this module and returns four values needed by callers.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |

#### Returns

**Type:** `tuple[str, str, dict, dict]`

—

#### Complexity

Not analyzed

---



### restore_previous

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_previous(page: Page, path: str, revision: int, preview_text: str) -> None:
```

#### Description

Restore a previous revision of a file in a browser-based test by interacting with the given Page object.

It navigates or manipulates the UI at the given path to select the specified revision and verifies that the displayed preview matches preview_text before completing the restore action.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `path` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |
| `preview_text` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### record_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def record_history(page: Page, url: str, page_id: str, database: str, original: dict) -> None:
```

#### Description

Record a historical snapshot or change for a web page into a test workspace or database context.

It uses the provided Page object and URL along with identifiers and original data to store or update history entries associated with the given page_id and database.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `database` | `str` | ✅ | — |
| `original` | `dict` | ✅ | — |

#### Complexity

Not analyzed

---



### view_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def view_history(page: Page, url: str, page_id: str, database: str, original: dict) -> None:
```

#### Description

Automates a browser interaction to view the history of a specific workspace page: it uses the provided Playwright Page to navigate to the given URL and perform actions that inspect or display the revision/history for the page identified by page_id, using the provided database context and original state dictionary as needed.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `database` | `str` | ✅ | — |
| `original` | `dict` | ✅ | — |

#### Complexity

Not analyzed

---



### main

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def main() -> None:
```

#### Description

Acts as the entry point for running the test routine in the tests/browser/workspace_v130.py module — it orchestrates setup and execution of the workspace-related browser tests for version 1.30.

It likely initializes test environment, runs the test cases, and performs any necessary teardown or reporting.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

<!-- METADATA: {"source_path": "tests/browser/workspace_v120.py", "source_sha": "45017619fea7eb10220074412c183cbd7a278e46", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/browser/workspace_v120.py",
  "source_hash": "4839992f109304faa216560f0c79b5360a9f72ab31bacbc874bb113779044ee3",
  "last_updated": "2026-11-18T03:21:17.786056+00:00",
  "git_sha": "45017619fea7eb10220074412c183cbd7a278e46",
  "tokens_used": 8292,
  "complexity_score": 4,
  "estimated_review_time_minutes": 15,
  "external_dependencies": [
    "argparse",
    "contextlib",
    "csv",
    "io",
    "pathlib",
    "sqlite3",
    "tempfile",
    "playwright.sync_api",
    "workspace_v012"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [tests](../README.md) > [browser](./README.md) > **workspace_v120**

---

# workspace_v120.py

> **File:** `tests/browser/workspace_v120.py`

![Complexity: Medium](https://img.shields.io/badge/Complexity-Medium-yellow) ![Review Time: 15min](https://img.shields.io/badge/Review_Time-15min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module contains browser-based acceptance test helpers and end-to-end scenarios for workspace version 1.20, focused on local text transfers and custom database workflows. It provides a set of functions that automate interactions with a browser using the Playwright synchronous API to create and manipulate markdown content, create and persist databases and schemas, define properties and views, import and export CSV data, and verify that records, linked views, and markdown content survive save/load cycles. The module also defines a few project-scoped constants used by the tests (MARKDOWN, CATALOG, DATA, RECORD) and relies on standard libraries (csv, sqlite3, tempfile) and utilities imported from workspace_v012 to drive local servers and saved-state fixtures.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `argparse` | import argparse |
| `contextlib` | from contextlib import closing |
| `csv` | import csv |
| `io` | import io |
| `pathlib` | from pathlib import Path |
| `sqlite3` | import sqlite3 |
| `tempfile` | from tempfile import TemporaryDirectory |
| `playwright.sync_api` | from playwright.sync_api import Locator, Page, expect, sync_playwright |
| `workspace_v012` | from workspace_v012 import api_json, free_port, local_server, saved |

## 📁 Directory

This file is part of the **browser** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses Playwright synchronous API (Locator, Page, sync_playwright, expect) for browser automation.
- Combines browser-driven UI actions with local resources: sqlite3 databases, CSV handling, and TemporaryDirectory usage.
- Organizes functionality into focused helper functions named for specific UI/dialog operations and round-trip verification scenarios.
- Imports shared test utilities and fixtures from a previous workspace module (workspace_v012) to manage servers and saved states.

## Maintenance Notes

- Add and round-trip markdown content in the browser UI (add_markdown, markdown_roundtrip).
- Create, configure, save, and choose custom databases and schemas, including dialogs for saving databases and properties (create_database, create_schema, save_database_dialog, choose_database, property_dialog, save_property).
- Define properties and views and exercise linked record/view behavior across save/load operations (create_property, create_view, linked_view_roundtrip, record_dialog).
- Import and export tabular data via CSV and validate round-trip integrity (csv_roundtrip, fill_records_and_views).
- Provide higher-level orchestration and entry point for running the scenarios (main, search_and_reopen, block_values).


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `MARKDOWN` | — | `'# 합성 Markdown 문서\n\n검토 계획의 합성 본문입니다.\n\n- 첫 작업\n - 하위 작업\n- [x] 확인 완료\n\n> 화면에는 문자로 표시할…` |
| `CATALOG` | — | `'합성 프로젝트 목록'` |
| `DATA` | — | `'합성 실험 기록'` |
| `RECORD` | — | `'합성 실험 A'` |



---

## Functions and Classes


### add_markdown

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_markdown(page: Page, *, text: str | None = None, file: Path | None = None) -> dict:
```

#### Description

Add a markdown item to the given Page using either a provided text string or the contents of a file.

The function creates and attaches a markdown block to the specified Page and returns information about the created block.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `text` = `None` | `str | None` | ❌ | — |
| `file` = `None` | `Path | None` | ❌ | — |

#### Returns

**Type:** `dict`

—

#### Complexity

Not analyzed

---



### block_values

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def block_values(record: dict) -> list[tuple]:
```

#### Description

Extracts and returns the values associated with a block from the given record dictionary as a sequence of tuples.

Each tuple in the returned list represents a grouped set of values derived from the input record.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `record` | `dict` | ✅ | — |

#### Returns

**Type:** `list[tuple]`

—

#### Complexity

Not analyzed

---



### markdown_roundtrip

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def markdown_roundtrip(page: Page, url: str, folder: Path) -> str:
```

#### Description

Performs a markdown roundtrip operation using the provided browser Page, a target URL, and a filesystem folder; it carries out whatever steps are needed to exercise markdown handling and returns a result as a string.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `folder` | `Path` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### save_database_dialog

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def save_database_dialog(page: Page, endpoint: str, method: str = 'POST') -> dict:
```

#### Description

Opens and drives a save-database dialog in a browser testing Page, submitting the database save request to the given endpoint using the specified HTTP method.

It automates the UI interactions required to save a database and returns the result of that operation as a dictionary.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `endpoint` | `str` | ✅ | — |
| `method` = `'POST'` | `str` | ❌ | — |

#### Returns

**Type:** `dict`

—

#### Complexity

Not analyzed

---



### create_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_database(page: Page, name: str) -> str:
```

#### Description

Automates the creation of a database in a browser-driven test using the provided Page object and the supplied database name.

It performs the necessary UI interactions to create the database and returns a string result related to the created database.


page is a Playwright Page object used to drive browser interactions during the test; name is the desired name for the database to be created.

Returns a string that identifies or represents the created database (for example, the created database's name or identifier).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `name` | `str` | ✅ | — |

#### Returns

**Type:** `str`

Returns a string that identifies or represents the created database (for example, the created database's name or identifier).

#### Complexity

Not analyzed

---



### property_dialog

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def property_dialog(page: Page, name: str, kind: str) -> Locator:
```

#### Description

Locate and return the UI locator for a property dialog on the given Playwright page that corresponds to a property identified by the provided name and kind.

The function encapsulates the selector logic so callers can interact with the dialog for that specific property.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `name` | `str` | ✅ | — |
| `kind` | `str` | ✅ | — |

#### Returns

**Type:** `Locator`

—

#### Complexity

Not analyzed

---



### create_property

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_property(page: Page, database: str, name: str, kind: str) -> None:
```

#### Description

Interacts with a browser Page to create a new property on a specified database within the workspace.

It uses the provided database identifier, property name, and property kind to drive the UI actions required to add that property in tests.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `database` | `str` | ✅ | — |
| `name` | `str` | ✅ | — |
| `kind` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### save_property

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def save_property(page: Page, database: str, name: str) -> None:
```

#### Description

Interacts with a Playwright Page to save or persist a property entry for a given database and property name in the test workspace.

It automates the UI steps necessary to store the specified property into the indicated database within the test environment.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `database` | `str` | ✅ | — |
| `name` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### create_schema

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_schema(page: Page) -> tuple[str, str]:
```

#### Description

Use a browser automation Page to create a schema in the workspace test flow.

The function performs the UI interactions necessary to create the schema and collects the resulting identifying information.


page is a Playwright Page object used to drive and inspect the web UI during the schema creation process.

Returns a tuple of two strings containing the primary pieces of information produced by the creation step (for example, the schema name and an associated identifier).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |

#### Returns

**Type:** `tuple[str, str]`

Returns a tuple of two strings containing the primary pieces of information produced by the creation step (for example, the schema name and an associated identifier).

#### Complexity

Not analyzed

---



### choose_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def choose_database(page: Page, database: str, name: str) -> None:
```

#### Description

Interacts with a Playwright Page to select or switch to a specific database entry in the workspace UI.

It uses the provided database type/identifier and a name to locate and choose the correct database within the page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `database` | `str` | ✅ | — |
| `name` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### record_dialog

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def record_dialog(page: Page, record_id: str | None = None) -> Locator:
```

#### Description

Locate and return the dialog element used for recording on a Playwright Page.

If a record_id is provided, the locator is scoped to the dialog instance associated with that record identifier.


page is the Playwright Page to search in; record_id is an optional string used to target a specific record's dialog when multiple dialogs may exist.

Returns a Playwright Locator that points to the record dialog element on the page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `record_id` = `None` | `str | None` | ❌ | — |

#### Returns

**Type:** `Locator`

Returns a Playwright Locator that points to the record dialog element on the page.

#### Complexity

Not analyzed

---



### create_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_view(page: Page, database: str, name: str, kind: str) -> None:
```

#### Description

Automates the creation of a view in the test workspace UI by using the provided Page object to interact with the application and create a view with the given name and kind inside the specified database.

It performs the browser steps necessary to add that view in the workspace_v120 test context.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `database` | `str` | ✅ | — |
| `name` | `str` | ✅ | — |
| `kind` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### fill_records_and_views

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def fill_records_and_views(page: Page, catalog: str, database: str) -> tuple[str, str]:
```

#### Description

Interacts with a browser Page to populate or configure records and views for a specific catalog and database in the test workspace.

It performs the necessary UI actions to create or fill the data structures required by tests and returns identifiers for the created record and view.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `catalog` | `str` | ✅ | — |
| `database` | `str` | ✅ | — |

#### Returns

**Type:** `tuple[str, str]`

—

#### Complexity

Not analyzed

---



### linked_view_roundtrip

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def linked_view_roundtrip(page: Page, url: str, page_id: str, catalog: str, target: str, database: str, record: str) -> None:
```

#### Description

Uses a Playwright Page to exercise a linked-view roundtrip in the browser: it navigates to the given URL and interacts with or verifies a linked view identified by the provided page_id, catalog, target, database, and record parameters.

The function is intended as a browser-based test helper that checks that a linked view can be opened, navigated, and returned from correctly.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `catalog` | `str` | ✅ | — |
| `target` | `str` | ✅ | — |
| `database` | `str` | ✅ | — |
| `record` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### csv_roundtrip

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def csv_roundtrip(page: Page, url: str, folder: Path, database: str) -> None:
```

#### Description

Runs a CSV import/export round-trip test in a browser workspace.

The function drives a Page to a given URL, uses a filesystem folder and database name to import or export CSV data, and verifies that the round-trip operation completes successfully.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `folder` | `Path` | ✅ | — |
| `database` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### search_and_reopen

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def search_and_reopen(page: Page, url: str, page_id: str, database: str, record: str) -> None:
```

#### Description

Drive a browser page to perform a search for a specific record in a given database and then reopen that record's page.

It uses the provided Page instance and URL along with identifiers (page_id, database, record) to locate and open the target item in the web UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |
| `database` | `str` | ✅ | — |
| `record` | `str` | ✅ | — |

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

Entry point for the test module tests/browser/workspace_v120.py; when called, main runs the test scenario(s) defined in that module related to the workspace v1.20 browser behaviors.

It orchestrates the setup, execution, and teardown of those tests within this file.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

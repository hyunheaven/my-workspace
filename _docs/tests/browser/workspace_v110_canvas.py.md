<!-- METADATA: {"source_path": "tests/browser/workspace_v110_canvas.py", "source_sha": "0ee2a03f1d13f19544f118d0077104122e4fa6c1", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/browser/workspace_v110_canvas.py",
  "source_hash": "377a8460ec15c8fc3bae00b70e27f1543ea84429629d71a1441d3c008071c6da",
  "last_updated": "2026-11-18T03:21:01.313652+00:00",
  "git_sha": "0ee2a03f1d13f19544f118d0077104122e4fa6c1",
  "tokens_used": 4291,
  "complexity_score": 1,
  "estimated_review_time_minutes": 8,
  "external_dependencies": [
    "argparse",
    "contextlib",
    "pathlib",
    "sqlite3",
    "tempfile",
    "uuid",
    "playwright.sync_api",
    "workspace_v012"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [tests](../README.md) > [browser](./README.md) > **workspace_v110_canvas**

---

# workspace_v110_canvas.py

> **File:** `tests/browser/workspace_v110_canvas.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 8min](https://img.shields.io/badge/Review_Time-8min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module contains a collection of test helper functions and check routines that drive Chromium-based browser interactions to verify editor behaviors such as draft recovery, IME composition, block command handling, and long-document handling. The file uses Playwright for synchronized browser automation and relies on local test infrastructure utilities imported from a companion module to start servers, provide API fixtures, and manage saved state. Individual functions encapsulate specific scenarios and assertions to be executed against a running page instance created by a create_page helper.

The tests interact with temporary working directories, SQLite, and unique identifiers to isolate runs, and they exercise editing and save-conflict conditions, block-level editor commands, and behavior when operating on lengthy documents. The module exposes a main entry point intended to wire these checks together when executed, and a set of standalone check_* functions that implement the concrete verification logic used by test runs.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `argparse` | import argparse |
| `contextlib` | from contextlib import closing |
| `pathlib` | from pathlib import Path |
| `sqlite3` | import sqlite3 |
| `tempfile` | from tempfile import TemporaryDirectory |
| `uuid` | from uuid import uuid4 |
| `playwright.sync_api` | from playwright.sync_api import expect, sync_playwright |
| `workspace_v012` | from workspace_v012 import api_items, api_json, free_port, local_server, saved |

## 📁 Directory

This file is part of the **browser** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses Playwright synchronous API for browser automation and assertions.
- Imports and reuses helper utilities from a local workspace_v012 module for server, API, and saved-state management.
- Employs temporary directories, SQLite, and UUIDs to create isolated, reproducible test environments.
- Organizes tests as standalone functions that operate on a page instance rather than as class-based test cases.

## Maintenance Notes

- create_page: initialize and return a Playwright-driven browser page configured for the tests.
- check_draft_recovery: verify that the editor recovers in-progress drafts after interruptions or reloads.
- check_conflicting_save: exercise and assert correct behavior when concurrent or conflicting save operations occur.
- check_blocks: validate block-level editor commands and their effects within the document.
- check_long_document: test editor behavior, performance, and integrity when handling very long documents.
- main: coordinate setup and execution of the defined checks, integrating local server and test fixtures.


---

## Functions and Classes


### create_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_page(page, url, title):
```

#### Description

Create a new canvas page in the test workspace using the provided URL and title.

It sets up or registers a page resource identified by url and assigns it the given title within the workspace context.


Returns the created page object (the workspace canvas page representation) so the caller can interact with or inspect the newly created page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `url` | `Unknown` | ✅ | — |
| `title` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### check_draft_recovery

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def check_draft_recovery(page, url, source):
```

#### Description

Runs a browser-based test that verifies draft recovery behavior in the Canvas workspace at a given URL using the provided page object and content source.

It exercises saving/recovering a draft and includes an inner helper (reject_save) to simulate or handle a rejected save attempt during the test.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `url` | `Unknown` | ✅ | — |
| `source` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### reject_save

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def reject_save(route):
```

#### Description

Act as a test route handler that causes a save request to be rejected (used in draft recovery tests).

It simulates a failing save operation so the test can verify how the application responds when a save is refused.


route is the intercepted network route object (e.g., a Playwright route) representing the save request to be handled and rejected by this function.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `route` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### check_conflicting_save

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def check_conflicting_save(page, url, source):
```

#### Description

Checks the behavior of a conflicting save operation in the workspace canvas: it exercises saving content from a given source at a specified URL and verifies that the application correctly detects or handles save conflicts.

The function drives a browser page to reproduce and assert the expected conflict-related UI or state changes.


page is the browser automation Page object used to drive the UI; url is the target page address to open and test; source is the content or source identifier that the test attempts to save and that should produce a conflict.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `url` | `Unknown` | ✅ | — |
| `source` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### check_blocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def check_blocks(page, url, source, target):
```

#### Description

Checks or validates block-related behavior on a workspace canvas for a browser test using the provided page and url, and operates with a source and a target.

It likely performs assertions or manipulations involving blocks (with a nested helper function add) to confirm expected behavior between the source and target on the canvas.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `url` | `Unknown` | ✅ | — |
| `source` | `Unknown` | ✅ | — |
| `target` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### add

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add(kind):
```

#### Description

Add a block of the specified kind to the canvas/check blocks collection.

The function creates or inserts a new block element identified by the provided kind value into the workspace.


kind is the identifier for the type of block to add (for example a string or enum value that names the block kind).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `kind` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### check_long_document

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def check_long_document(page, url, target):
```

#### Description

Runs verification steps for a long document in the workspace_v110 canvas.

Using the provided page controller it loads the given URL and exercises checks related to the specified target within that document.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `url` | `Unknown` | ✅ | — |
| `target` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### main

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def main():
```

#### Description

Acts as the entry point for running the test routines located in the tests/browser/workspace_v110_canvas.py module.

It coordinates or invokes the sequence of browser-based checks related to the workspace v1.10 canvas functionality when executed.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

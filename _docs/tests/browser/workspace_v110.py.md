<!-- METADATA: {"source_path": "tests/browser/workspace_v110.py", "source_sha": "233fc4e8656fb2deeb66e6ae8fac2082af374819", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/browser/workspace_v110.py",
  "source_hash": "5417dace3dff2407e8c7a5dbe622d3cdd114101498dbf7413f2bd3f09a1115cd",
  "last_updated": "2026-11-18T03:20:53.698125+00:00",
  "git_sha": "233fc4e8656fb2deeb66e6ae8fac2082af374819",
  "tokens_used": 3208,
  "complexity_score": 1,
  "estimated_review_time_minutes": 9,
  "external_dependencies": [
    "argparse",
    "datetime",
    "pathlib",
    "sqlite3",
    "tempfile",
    "playwright.sync_api",
    "workspace_v012"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [tests](../README.md) > [browser](./README.md) > **workspace_v110**

---

# workspace_v110.py

> **File:** `tests/browser/workspace_v110.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 9min](https://img.shields.io/badge/Review_Time-9min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module implements a set of browser-based regression tests that exercise template persistence, shared task views, and link handling across restarts of a local workspace. The file defines five top-level functions that drive Playwright browser interactions and local server setup, exercising scenarios such as recording page content, restoring state after an application restart, verifying shared task views, and moving and restoring page links. The tests make use of temporary directories, an SQLite database, and several helpers imported from a prior workspace test module to configure the server and API endpoints used during the browser interactions.

The constants at module scope provide reusable textual fixtures (page title, page text, task titles, and task notes) used by the test flows. The main function likely ties the individual scenario functions together so the module can be executed as a standalone test script using the Playwright sync API and local server utilities to validate end-to-end behaviors that should persist across restarts and be visible to shared viewers.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `argparse` | import argparse |
| `datetime` | from datetime import date |
| `pathlib` | from pathlib import Path |
| `sqlite3` | import sqlite3 |
| `tempfile` | from tempfile import TemporaryDirectory |
| `playwright.sync_api` | from playwright.sync_api import Page, expect, sync_playwright |
| `workspace_v012` | from workspace_v012 import api_items, api_json, free_port, local_server, saved |

## 📁 Directory

This file is part of the **browser** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses Playwright's synchronous API (sync_playwright, Page, expect) for browser-driven tests.
- Interacts with a local SQLite database and TemporaryDirectory for ephemeral test state.
- Reuses test helper functions and fixtures from a separate workspace_v012 module to configure API endpoints and server state.

## Maintenance Notes

- page_record: drive a browser session to create and record a page with predefined title and text using Playwright interactions.
- restore_after_restart: verify that recorded pages and state persist after restarting the application or local server.
- shared_task_views: exercise shared task presentation and visibility, ensuring tasks and notes are rendered correctly for shared viewers.
- link_move_and_restore: test moving page links and validate that links are correctly restored or maintained across restarts.
- main: coordinate execution of the test scenarios, setting up temporary resources, local server, and Playwright runtime to run the regressions.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `PAGE_TITLE` | — | `'검증 회의 · 합성 예시'` |
| `PAGE_TEXT` | — | `'자동 저장 후 찾아볼 한국어 합성 문장'` |
| `TASK_TITLE` | — | `'표에서 만든 합성 업무'` |
| `TASK_NOTE` | — | `'업무 상세에서 남긴 합성 메모'` |
| `UNDATED_TASK_TITLE` | — | `'마감일 없는 완료 업무 · 합성 예시'` |



---

## Functions and Classes


### page_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def page_record(page: Page, url: str) -> str:
```

#### Description

Operates on a Page object for the provided URL to record or capture information about that page and produce a textual result.

The function encapsulates the recording/capture workflow and returns a string that represents the outcome of that recording process.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### restore_after_restart

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_after_restart(page: Page, url: str, page_id: str) -> None:
```

#### Description

Restore a browser workspace or test page to a known state after an application or test restart by using the provided Page object to navigate to the given URL and re-establish or verify the page identified by page_id.

This is intended to be used in tests to recover and continue interactions with the same logical page after restarting the environment.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### shared_task_views

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def shared_task_views(page: Page, url: str) -> None:
```

#### Description

Uses a Playwright Page object to exercise or verify the shared task views for the workspace v110 test suite by navigating to and interacting with the given URL.

It performs browser-driven checks and interactions related to shared task views in that workspace context.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### link_move_and_restore

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def link_move_and_restore(page: Page, url: str, page_id: str) -> None:
```

#### Description

Performs an automated browser test that exercises linking, moving, and restoring behavior for a workspace page.

The function uses a Playwright Page object to navigate to the given URL and operate on the page identified by page_id to verify link move and restore functionality.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Page` | ✅ | — |
| `url` | `str` | ✅ | — |
| `page_id` | `str` | ✅ | — |

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

Entry point for the tests in the tests/browser/workspace_v110.py module; it runs the module's main logic for exercising or validating the workspace v1.10 browser functionality.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

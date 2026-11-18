<!-- METADATA: {"source_path": "tests/test_integrated_workspace_v09.py", "source_sha": "f82ccc77853a1201770c72893cf1b02bb9f1ca3e", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/test_integrated_workspace_v09.py",
  "source_hash": "d5b7140a6c7068bed658a6741b62615f97cdfd5f431644ac8acbceeae54df109",
  "last_updated": "2026-11-18T03:21:27.414808+00:00",
  "git_sha": "f82ccc77853a1201770c72893cf1b02bb9f1ca3e",
  "tokens_used": 6030,
  "complexity_score": 3,
  "estimated_review_time_minutes": 9,
  "external_dependencies": [
    "datetime",
    "pathlib",
    "sqlite3",
    "pytest",
    "fastapi.testclient",
    "services.local_api.app",
    "services.local_api.storage"
  ]
}
```

</details>

[Documentation Home](../README.md) > [tests](./README.md) > **test_integrated_workspace_v09**

---

# test_integrated_workspace_v09.py

> **File:** `tests/test_integrated_workspace_v09.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 9min](https://img.shields.io/badge/Review_Time-9min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module contains synthetic-only local integration tests for version 0.9 of the local API. It defines pytest test functions that exercise the application created by services.local_api.app.create_app using FastAPI's TestClient and a LocalStore-backed sqlite3 environment. The tests cover a broad range of behaviors relevant to project templates, page tree operations, project/task database revisions, document linking, calendar event CRUD and feeds, timezone and input validation errors, migration from v0.8 databases, and task view upgrade semantics.

The module exposes helper fixtures and utilities (client, post, put, doc) alongside thirteen targeted test functions that validate API behavior and side-effects in isolation (ensuring no remote side effects). Two module-level constants (HEADERS and URL) provide default request headers and a base URL used by the tests.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `datetime` | from datetime import date, timedelta |
| `pathlib` | from pathlib import Path |
| `sqlite3` | import sqlite3 |
| `pytest` | import pytest |
| `fastapi.testclient` | from fastapi.testclient import TestClient |
| `services.local_api.app` | from services.local_api.app import create_app |
| `services.local_api.storage` |     from services.local_api.storage import LocalStore |

## 📁 Directory

This file is part of the **tests** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses pytest for test organization and fixtures
- Exercises a FastAPI application via fastapi.testclient.TestClient
- Interacts with a sqlite3-backed LocalStore for storage-level integration testing
- Defines shared request headers and a local base URL as module-level constants

## Maintenance Notes

- Provide a TestClient fixture and simple HTTP helper fixtures (post, put) for exercising the local FastAPI application.
- Define a doc fixture for creating and referencing documents within the LocalStore-backed test environment.
- Assert correct behavior of existing templates and initial getting-started flows for the v0.9 API.
- Validate page-tree operations including creation, move semantics, cycle detection, and handling of stale revisions.
- Verify project/task database revision behavior, document linking, calendar event CRUD and projection to tasks, and timezone/input validation.
- Ensure local operations produce no unintended remote side effects and that migration from v0.8 preserves documents and expected task view identity/behavior.
- Check that invalid task properties are rejected and not persisted by the storage layer.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `HEADERS` | — | `{'Content-Type': 'application/json', 'X-EAW-Request': 'local-template-editor'}` |
| `URL` | — | `'http://127.0.0.1:8765'` |



---

## Functions and Classes


### client

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def client(tmp_path: Path):
```

#### Description

A pytest fixture that provides a test client for the integrated workspace tests.

It takes a temporary filesystem path and prepares a client instance usable by test functions.


Yields or returns a configured test client instance that tests can use, created using the provided temporary Path.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Path` | ✅ | — |

#### Complexity

Not analyzed

---



### post

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def post(client, path, payload):
```

#### Description

Send an HTTP POST request using the provided test client to the given path with the supplied payload and return the resulting response.

This helper is used in integration tests to exercise endpoints under test.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `path` | `Unknown` | ✅ | — |
| `payload` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### put

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def put(client, path, payload):
```

#### Description

Helper function used in tests to send an HTTP PUT request using the provided test client to the given path with the given payload.

It encapsulates performing the PUT operation against the test server endpoint within the integrated workspace v0.9 test suite.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `path` | `Unknown` | ✅ | — |
| `payload` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### doc

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def doc(client, title, parent_id=None):
```

#### Description

Creates (or opens) a workspace document within the integrated test workspace using the provided client, assigning it the given title and optionally placing it under a specified parent.

It is intended for use in tests to set up or reference a document resource.


client is the test API/client object used to perform workspace operations; title is the desired document title; parent_id, if provided, is the identifier of the parent container under which the document should be created.

Returns the created or retrieved document representation (e.g., an API response or document object) so the test can interact with it.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `title` | `Unknown` | ✅ | — |
| `parent_id` = `None` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### test_existing_templates_and_getting_started_remain

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_existing_templates_and_getting_started_remain(client):
```

#### Description

This test verifies that existing templates and the "Getting Started" entry are still present in the integrated workspace (v0.9) when exercised via the provided test client.

It exercises the application state through the client and asserts that those items remain available.


client is a test HTTP/client fixture used to make requests against the application under test (provides access to endpoints and application state during the test).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_page_tree_create_move_cycle_and_stale_revision

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_page_tree_create_move_cycle_and_stale_revision(client):
```

#### Description

This test exercises the page tree behavior in the integrated workspace v0.9: it creates pages, performs move operations (including attempts that would create cycles), and verifies how stale revisions are handled after those moves.

It ensures that move operations are correctly applied or rejected to prevent cycles and that revision state is consistent when pages are relocated or updated.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_project_task_database_revision_and_document_link

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_project_task_database_revision_and_document_link(client):
```

#### Description

This test exercises project task behavior in an integrated workspace by verifying database revision handling and document link functionality.

It likely creates or modifies a project task via the provided client and asserts that the database revision is updated and that document links are created or maintained correctly.


client is a test client fixture used to make requests against the application under test (e.g., an HTTP or application test client).

This test function does not return a value (it relies on assertions); therefore it returns None.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_calendar_event_crud_feed_and_task_projection

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_calendar_event_crud_feed_and_task_projection(client):
```

#### Description

This is a test function that exercises create, read, update, and delete (CRUD) operations for calendar events and verifies their effects on the feed and task projection within the integrated workspace v0.9.

It uses a provided test client to perform API interactions and assert that the event lifecycle updates the feed and task views as expected.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_timezone_and_calendar_input_errors

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_timezone_and_calendar_input_errors(client):
```

#### Description

This test exercises the integrated workspace v0.9 behavior when presented with invalid timezone and calendar inputs, asserting that the system returns the appropriate input validation errors.

It sends requests using the provided test client and verifies that error responses are produced for malformed or unsupported timezone/calendar values.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_local_no_remote_side_effects

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_local_no_remote_side_effects(client):
```

#### Description

This test verifies that performing local operations using the provided client does not produce any unintended side effects on the remote system.

It likely runs a sequence of local workspace actions and asserts that remote state remains unchanged.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_migrate_v08_database_without_losing_documents

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_migrate_v08_database_without_losing_documents(tmp_path):
```

#### Description

This test verifies that migrating a workspace database from version 0.8 to the newer format preserves existing documents and does not lose data during the migration process.

It exercises the migration logic end-to-end using a temporary filesystem location to simulate the older database state and confirms documents remain accessible after migration.


tmp_path is a pytest-provided temporary directory (pathlib.Path) used as an isolated filesystem location for creating the legacy v0.8 database and performing the migration.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_task_views_keep_identity_and_new_properties_on_upgraded_copy

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_task_views_keep_identity_and_new_properties_on_upgraded_copy(tmp_path):
```

#### Description

This test verifies that when a workspace (or task views within it) is upgraded/copied to a newer version, the task views retain their identity (i.e., remain the same logical objects) and also keep any new properties introduced by the upgrade.

It ensures that an upgraded copy preserves both identity and newly added properties for task views.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_invalid_task_properties_do_not_persist

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_invalid_task_properties_do_not_persist(client, property_value):
```

#### Description

A test that verifies invalid task property values are rejected and are not saved to the integrated workspace.

It exercises the API via the provided client and uses different property_value inputs (via parametrize) to ensure invalid values do not persist on the task.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `property_value` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

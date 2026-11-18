<!-- METADATA: {"source_path": "tests/test_page_canvas_v10.py", "source_sha": "7ed97ded8b9c9f7515f3f72115f056a32890514a", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/test_page_canvas_v10.py",
  "source_hash": "744187e4023ee0f7e52e5a958ab9d001d4665474f07b5580dc3d7e9458092e7f",
  "last_updated": "2026-11-18T03:21:07.755314+00:00",
  "git_sha": "7ed97ded8b9c9f7515f3f72115f056a32890514a",
  "tokens_used": 4073,
  "complexity_score": 1,
  "estimated_review_time_minutes": 5,
  "external_dependencies": [
    "pathlib",
    "uuid",
    "pytest",
    "fastapi.testclient",
    "services.local_api.app",
    "services.local_api.storage"
  ]
}
```

</details>

[Documentation Home](../README.md) > [tests](./README.md) > **test_page_canvas_v10**

---

# test_page_canvas_v10.py

> **File:** `tests/test_page_canvas_v10.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 5min](https://img.shields.io/badge/Review_Time-5min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This test module contains a suite of pytest-based checks that exercise page block handling in a local FastAPI service. It defines a test client fixture and seven test functions that together verify persistence, revision validation and size limits, template integrity when blocks are added, migration from a legacy SQLite store without data loss, enforcement of local security rules, correct round-trip behavior for long Korean content and link validation, and preservation and validation of nested block depth. The tests interact with the service using a TestClient pointed at a local URL and common JSON headers.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `pathlib` | from pathlib import Path |
| `uuid` | from uuid import uuid4 |
| `pytest` | import pytest |
| `fastapi.testclient` | from fastapi.testclient import TestClient |
| `services.local_api.app` | from services.local_api.app import create_app |
| `services.local_api.storage` | from services.local_api.storage import LocalStore |

## 📁 Directory

This file is part of the **tests** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses pytest for test functions and fixtures
- Exercises a FastAPI TestClient created from services.local_api.app.create_app
- Interacts with a LocalStore abstraction for storage-related tests
- Defines shared request constants (URL and HEADERS) for tests
- Uses uuid4 to generate unique identifiers within tests

## Maintenance Notes

- Provide a TestClient fixture for the local FastAPI application to be used by the test cases.
- Verify that page creation and synthetic blocks persist correctly across operations.
- Validate revision handling and enforce maximum size constraints for page content.
- Ensure that a template document is preserved when new blocks are added to a page.
- Check that legacy SQLite storage is migrated to the local store without losing data and that local security rules and nested-block validations behave as expected.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `URL` | — | `'http://127.0.0.1:8765'` |
| `HEADERS` | — | `{'Content-Type': 'application/json', 'X-EAW-Request': 'local-template-editor'}` |



---

## Functions and Classes


### client

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def client(tmp_path: Path):
```

#### Description

This is a pytest fixture named 'client' defined in tests/test_page_canvas_v10.py.

It provides a test client for use in tests and accepts a temporary filesystem path to set up any required test resources.


Returns a test client object instantiated for use by the tests (exact type/value provided by the fixture implementation).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Path` | ✅ | — |

#### Complexity

Not analyzed

---



### test_page_creation_and_blocks_persist

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_page_creation_and_blocks_persist(client):
```

#### Description

This test verifies that a page can be created via the application's API (or test client) and that any blocks added to that page persist as expected.

It exercises page creation and then checks that the block contents or structure remain after creation, ensuring persistence behaviour is correct.


client is the test HTTP client fixture used to make requests against the application under test (e.g., to create pages and retrieve them).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_revision_validation_and_max_size

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_revision_validation_and_max_size(client):
```

#### Description

This test verifies that revision objects are validated correctly and that any size limits on revisions (maximum allowed size) are enforced by the application.

It exercises the endpoint(s) using the provided test client to ensure that oversized or otherwise invalid revision payloads are rejected and valid revisions are accepted.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_template_document_preserved_when_adding_blocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_template_document_preserved_when_adding_blocks(client):
```

#### Description

This test verifies that when new blocks are added to a page canvas, the original template document remains unchanged and is preserved.

It exercises the code path that mutates a page by adding blocks and asserts that the template document content or structure is not modified as a result.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_legacy_sqlite_is_migrated_without_data_loss

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_legacy_sqlite_is_migrated_without_data_loss(tmp_path: Path):
```

#### Description

This test verifies that a legacy SQLite database used by the application is migrated to the current schema or storage format without losing any data.

It exercises the migration path using a temporary filesystem location and asserts that all expected records and structure survive the migration process.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Path` | ✅ | — |

#### Complexity

Not analyzed

---



### test_local_security_still_applies

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_local_security_still_applies(client):
```

#### Description

Verifies that the local security rules are still enforced when interacting with the page canvas v10 endpoints.

The test uses the provided test client to make requests and assert that unauthorized or locally-restricted actions remain blocked as expected.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_long_korean_canvas_round_trip_and_local_link_validation

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_long_korean_canvas_round_trip_and_local_link_validation(client):
```

#### Description

This test verifies that a Canvas page containing long Korean text can be serialized and deserialized (round-tripped) correctly and that local links within that canvas content are validated as expected.

It exercises the page/canvas handling code via the provided test client to ensure text integrity and link validation behavior.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_nested_blocks_are_preserved_and_invalid_depth_is_rejected

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_nested_blocks_are_preserved_and_invalid_depth_is_rejected(client):
```

#### Description

This test verifies that nested blocks in the page canvas API are preserved correctly and that requests which attempt to exceed the allowed nesting depth are rejected.

It exercises the endpoint behavior by submitting payloads with valid nested structures and invalid (too-deep) structures and asserts the appropriate acceptance or error responses.


client is a test HTTP client fixture used to make requests to the application endpoints under test.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

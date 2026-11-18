<!-- METADATA: {"source_path": "tests/test_custom_databases.py", "source_sha": "25facb7bcb7e89d338ecad472ebc4b81e8ab0930", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/test_custom_databases.py",
  "source_hash": "5668bb89a75c0fa53c0291792bc73f95fffba39447abc53e2f2204caf5567a7a",
  "last_updated": "2026-11-18T03:21:14.632565+00:00",
  "git_sha": "25facb7bcb7e89d338ecad472ebc4b81e8ab0930",
  "tokens_used": 6476,
  "complexity_score": 4,
  "estimated_review_time_minutes": 12,
  "external_dependencies": [
    "__future__",
    "sqlite3",
    "fastapi.testclient",
    "pytest",
    "services.local_api.app"
  ]
}
```

</details>

[Documentation Home](../README.md) > [tests](./README.md) > **test_custom_databases**

---

# test_custom_databases.py

> **File:** `tests/test_custom_databases.py`

![Complexity: Medium](https://img.shields.io/badge/Complexity-Medium-yellow) ![Review Time: 12min](https://img.shields.io/badge/Review_Time-12min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This test module contains behavioral tests for local schemas, typed records, views, and relations against a local API. It defines helper factories and fixtures (such as client_for and database_client) and a set of test functions that exercise persistence and history behavior: durability of schemas and views, rollups and formula propagation through relations, transactional behavior on invalid batches, record history pagination and restoration, relation restoration rejection for deleted targets, and view history tracking.

The module relies on FastAPI's TestClient and pytest to drive HTTP interactions with a created application instance (create_app) and uses sqlite3 for local database interactions in the tests. A small set of module-level constants (BASE, ORIGIN, HEADERS) centralize API path and header values used across the tests and helpers.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `__future__` | from __future__ import annotations |
| `sqlite3` | import sqlite3 |
| `fastapi.testclient` | from fastapi.testclient import TestClient |
| `pytest` | import pytest |
| `services.local_api.app` | from services.local_api.app import create_app |

## 📁 Directory

This file is part of the **tests** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses pytest for test definition and FastAPI TestClient to exercise API endpoints
- Interacts with a local SQLite database via sqlite3 for persistence in tests
- Centralizes API path and test headers in module-level constants for reuse

## Maintenance Notes

- Provide a TestClient-bound factory (client_for) and a pytest-compatible database_client fixture to create and manage test clients and databases for the local API.
- Offer helper functions for constructing and inspecting test payloads and entities, including create_database, path_of, property_of, record_of, revise_record, and checked.
- Define a suite of behavioral tests that verify durability, relation rollups, transactional rollback on invalid batches, record history pagination and restoration, rejection of relations to deleted records, and preservation of view identity across history changes.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `BASE` | — | `'/api/v1/databases'` |
| `ORIGIN` | — | `'http://127.0.0.1:8765'` |
| `HEADERS` | — | `{'X-EAW-Request': 'local-template-editor'}` |



---

## Functions and Classes


### client_for

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def client_for(path):
```

#### Description

Create and return a test client configured for the provided filesystem path.

The function is intended to produce a client instance that operates against resources or a database located at the given path, enabling tests to interact with that target.


Returns a client instance tied to the supplied path for use in tests.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### database_client

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def database_client(tmp_path):
```

#### Description

A pytest fixture that sets up and provides a database client for tests in tests/test_custom_databases.py.

It uses the pytest-provided temporary path to isolate any on-disk storage for each test.


Returns a database client instance configured to use the given temporary directory for its storage.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### checked

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def checked(response, status=200):
```

#### Description

Test helper that checks a response object against an expected HTTP status code.

It is intended for use in tests to verify that the provided response has the expected status (defaulting to 200).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `response` | `Unknown` | ✅ | — |
| `status` = `200` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### create_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_database(client, name):
```

#### Description

Create a new database resource using the provided client with the given name for use in tests.

It encapsulates the setup step of provisioning or registering a database identified by the name with the test client.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `name` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### path_of

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def path_of(db):
```

#### Description

Determine and return the filesystem path associated with the given test database.

Used in tests to obtain the on-disk location of a database object or identifier.


Returns the path to the database as a string.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### property_of

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def property_of(client, db, name, kind, **config):
```

#### Description

This function defines or checks a property for a custom database within the test suite.

Given a client, a database object or identifier, a property name, its kind, and additional configuration, it sets up or validates that property in the context of tests.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `db` | `Unknown` | ✅ | — |
| `name` | `Unknown` | ✅ | — |
| `kind` | `Unknown` | ✅ | — |
| `config` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### record_of

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def record_of(client, db, title, values=None, notes=''):
```

#### Description

Create or retrieve a test record in a custom database using the provided client and database identifier, setting its title and optional field values and notes.

This helper is intended for use in test cases to set up or inspect database records consistently.


client is the test client or API wrapper used to interact with the database; db identifies which custom database to use; title is the record title. values is an optional mapping of field names to values to populate the record, and notes is an optional string to attach as record notes.

Returns the created or retrieved record object representing the database entry (used by tests to inspect or assert state).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `db` | `Unknown` | ✅ | — |
| `title` | `Unknown` | ✅ | — |
| `values` = `None` | `Unknown` | ❌ | — |
| `notes` = `''` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### revise_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def revise_record(client, db, record, values):
```

#### Description

Update or modify an existing record in a custom database test using the provided client.

The function takes a database identifier and a record reference, applies the given values to revise that record, and exercises the code paths involved in record revision within tests.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `client` | `Unknown` | ✅ | — |
| `db` | `Unknown` | ✅ | — |
| `record` | `Unknown` | ✅ | — |
| `values` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_schema_and_views_are_durable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_schema_and_views_are_durable(tmp_path):
```

#### Description

This is a test function that verifies that database schema definitions and materialized or regular views remain durable across the operations being tested.

It likely sets up a temporary database, creates schemas and views, performs actions that could affect persistence, and then asserts that the schema and views are still present and unchanged.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_relations_rollups_and_formula_follow_source_edits

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_relations_rollups_and_formula_follow_source_edits(database_client):
```

#### Description

This test verifies that when source records in a custom database are edited, related properties (relations and rollups) and formula fields correctly follow and reflect those source edits.

It exercises relations, rollups, and formula behavior to ensure updates propagate as expected.


database_client is a test fixture or helper that provides access to the test database and operations for creating, updating, and querying records used by the test.

This test does not return a value; it asserts expected behavior and raises on failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_invalid_batch_rolls_back_and_stale_mutations_are_rejected

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_invalid_batch_rolls_back_and_stale_mutations_are_rejected(database_client):
```

#### Description

This test verifies that when an invalid batch operation is attempted against a custom database, the entire batch is rolled back and no partial changes are committed.

It also checks that any stale or outdated mutations are rejected by the database client to ensure consistency.


database_client is a test fixture providing a connection or client for interacting with the custom database under test; it is used to submit the batch and to observe resulting state/behavior.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_record_history_paginates_and_restores_as_new_revision

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_record_history_paginates_and_restores_as_new_revision(database_client):
```

#### Description

This test verifies that a database record's revision history can be paginated through and that restoring a previous revision creates a new revision rather than overwriting history.

It ensures pagination of history entries works correctly and that performing a restore results in a new revision entry being added.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_restore_rejects_a_historical_relation_to_a_deleted_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_restore_rejects_a_historical_relation_to_a_deleted_record(database_client):
```

#### Description

This test verifies that attempting to restore a historical relation that points to a record which has been deleted is rejected.

It ensures the restore operation does not re-establish relations to records that no longer exist, validating correct handling of historical relations to deleted records.


database_client: a test fixture or helper providing access to the database and operations needed to create, delete, and attempt restoration of records and relations.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_view_history_tracks_settings_and_preserves_the_view_identity

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_view_history_tracks_settings_and_preserves_the_view_identity(database_client):
```

#### Description

This test verifies that a database view's history correctly records its settings and that the view's identity (likely its identifier or identity-related properties) is preserved across operations that affect or inspect its history.

It exercises the view-history tracking behavior and asserts that configuration/settings are captured and that the view remains the same logical entity.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_client` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

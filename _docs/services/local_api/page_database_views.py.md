<!-- METADATA: {"source_path": "services/local_api/page_database_views.py", "source_sha": "e51d76b8316556c2b5f49df8aac9032f81115001", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:20:15Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "services/local_api/page_database_views.py",
  "source_hash": "6337cb512e66c5c25e12aa8ee8464916b5d597c92df6d9751b97d6ed3a420487",
  "last_updated": "2026-11-18T03:17:21.839798+00:00",
  "git_sha": "e51d76b8316556c2b5f49df8aac9032f81115001",
  "tokens_used": 3944,
  "complexity_score": 2,
  "estimated_review_time_minutes": 5,
  "external_dependencies": [
    "__future__",
    "contextlib",
    "sqlite3",
    "uuid",
    "fastapi",
    "pydantic"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [services](../README.md) > [local_api](./README.md) > **page_database_views**

---

# page_database_views.py

> **File:** `services/local_api/page_database_views.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 5min](https://img.shields.io/badge/Review_Time-5min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module implements the pieces needed to persistently associate personal pages with views stored in a local SQLite database. It defines Pydantic request models for linking and unlinking operations and exposes a function to mount the HTTP handlers onto a FastAPI application. The module imports utilities for working with UUIDs, a workspace storage abstraction, and SQLite, indicating that the mounting function wires HTTP endpoints to operations that validate requests, interact with the local database, and update workspace-backed state.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `__future__` | from __future__ import annotations |
| `contextlib` | from contextlib import closing |
| `sqlite3` | import sqlite3 |
| `uuid` | from uuid import uuid4 |
| `fastapi` | from fastapi import FastAPI, HTTPException |
| `pydantic` | from pydantic import BaseModel, ConfigDict, Field |

### Internal Dependencies

| Module | Usage |
| --- | --- |
| `workspace_store` | from .workspace_store import UUID_PATTERN, WorkspaceStore |

## 📁 Directory

This file is part of the **local_api** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses Pydantic models for request validation
- Integrates with FastAPI to expose HTTP endpoints
- Interacts with a local SQLite database (sqlite3) and a WorkspaceStore abstraction
- Uses UUID utilities and a shared UUID_PATTERN for identifier validation

## Maintenance Notes

- Define request payload schemas for link and unlink operations using Pydantic (LinkRequest and UnlinkRequest).
- Provide a mount_page_database_views function that attaches the page-to-database-view endpoints to a FastAPI application.
- Validate incoming requests against a UUID pattern and workspace data structures when processing link/unlink actions.
- Coordinate persistence of page-to-view references in a local SQLite-backed workspace store and raise HTTP errors when operations fail.


---

## Functions and Classes


### LinkRequest

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

LinkRequest is a pydantic data model that represents a request to link or reference a specific view within a particular database.

Within services/local_api/page_database_views.py, this model acts as the canonical request payload for operations that need to refer to a specific view in a database. It standardizes the format and validation of database/view identifiers used by other components in the module.

Responsibilities:
- Validate and store the identifier of the target database (database_id).
- Validate and store the identifier of the target view within that database (view_id).
- Provide pydantic model configuration via model_config to control validation/serialization behavior.
- Serve as a clear, typed carrier object for passing database and view identifiers through the local API layer.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `database_id` (class) | `str` | 🔓 public | Class attribute database_id<br>**Default:** `Field(pattern=UUID_PATTERN)` |
| `view_id` (class) | `str` | 🔓 public | Class attribute view_id<br>**Default:** `Field(pattern=UUID_PATTERN)` |

---



### UnlinkRequest

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

UnlinkRequest is a Pydantic model used to represent and validate the data structure for an unlink request within the page_database_views module.

Within services/local_api/page_database_views.py, UnlinkRequest defines the schema and validation rules for unlink operations, integrating request data handling into the module's API layer. It acts as the canonical request type used by the module when processing unlink-related requests.

Responsibilities:
- Provide a typed container for unlink request data so incoming payloads can be validated.
- Expose model configuration through model_config to control Pydantic behaviors (serialization, validation rules, etc.).
- Enable consistent serialization and deserialization of unlink request instances when communicating with other parts of the local API.
- Serve as a clear schema for consumers of the API to understand the expected shape of unlink request payloads.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |

---



### mount_page_database_views

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def mount_page_database_views(app: FastAPI, store: WorkspaceStore) -> None:
```

#### Description

Register a set of HTTP endpoints (page-database views) on the provided FastAPI app that operate against the given WorkspaceStore.

The mounted endpoints provide functionality for checking pages and listing, adding, and removing links related to pages (implemented by the nested handlers check_page, list_links, add_link, remove_link).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `app` | `FastAPI` | ✅ | — |
| `store` | `WorkspaceStore` | ✅ | — |

#### Complexity

Not analyzed

---



### check_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def check_page(db: sqlite3.Connection, page_id: str) -> None:
```

#### Description

Performs a verification or validation operation for a page identified by page_id using the provided sqlite3.Connection.

It is intended to check the page record in the database (for example existence or validity) and may raise an error or take action if the check fails.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `page_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### list_links

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_links(page_id: str):
```

#### Description

HTTP GET endpoint function that returns a list of links associated with a specific page identified by page_id.

It is registered on the app with the @app.get decorator and is intended to retrieve link information for the given page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### add_link

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_link(page_id: str, body: LinkRequest):
```

#### Description

HTTP POST endpoint that creates or attaches a link to the page identified by page_id using the data provided in the LinkRequest body.

It accepts a page identifier and a LinkRequest payload and performs the operation to add that link to the specified page.


Returns an HTTP response indicating the result of the add-link operation (e.g., success or failure) and any relevant payload such as the created link or error information.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `LinkRequest` | ✅ | — |

#### Complexity

Not analyzed

---



### remove_link

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def remove_link(page_id: str, link_id: str, body: UnlinkRequest):
```

#### Description

HTTP DELETE endpoint that removes an existing link from a page.

It unlinks the resource identified by link_id from the page identified by page_id using the details provided in the UnlinkRequest body.


Returns an HTTP response indicating the outcome of the unlink operation (e.g., success or error status).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `link_id` | `str` | ✅ | — |
| `body` | `UnlinkRequest` | ✅ | — |

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

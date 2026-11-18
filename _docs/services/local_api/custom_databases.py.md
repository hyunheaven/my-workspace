<!-- METADATA: {"source_path": "services/local_api/custom_databases.py", "source_sha": "1dfb3ca7df5a8d486f93bb085e618af12f073908", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:20:15Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "services/local_api/custom_databases.py",
  "source_hash": "e7098f3ad842b493dcb4083f67111618cf3d9950319c9afae12e78a51f6cb798",
  "last_updated": "2026-11-18T03:19:59.030433+00:00",
  "git_sha": "1dfb3ca7df5a8d486f93bb085e618af12f073908",
  "tokens_used": 35114,
  "complexity_score": 10,
  "estimated_review_time_minutes": 54,
  "external_dependencies": [
    "__future__",
    "contextlib",
    "datetime",
    "json",
    "math",
    "sqlite3",
    "typing",
    "unicodedata",
    "urllib.parse",
    "uuid",
    "fastapi",
    "pydantic"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [services](../README.md) > [local_api](./README.md) > **custom_databases**

---

# custom_databases.py

> **File:** `services/local_api/custom_databases.py`

![Complexity: High](https://img.shields.io/badge/Complexity-High-red) ![Review Time: 54min](https://img.shields.io/badge/Review_Time-54min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module implements a local, user-configurable database layer for storing custom databases, their properties, views, records and revision history. It defines Pydantic models for inputs and revisions (Input, Revision, DatabaseInput, DatabaseUpdate, PropertyInput, ViewConfig, ViewInput, RecordInput, RecordUpdate, RecordBatch) that represent the shapes of databases, properties, views and record payloads. A CustomDatabaseStore class encapsulates the operational logic for managing these entities and their histories. The module also exposes helper functions for common HTTP error responses and encoding/normalization utilities, as well as a mount_custom_databases function intended to attach the custom database API into a FastAPI application or router.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `__future__` | from __future__ import annotations |
| `contextlib` | from contextlib import closing, contextmanager |
| `datetime` | from datetime import date |
| `json` | import json |
| `math` | import math |
| `sqlite3` | import sqlite3 |
| `typing` | from typing import Any, Iterator, Literal |
| `unicodedata` | from unicodedata import normalize |
| `urllib.parse` | from urllib.parse import urlsplit |
| `uuid` | from uuid import uuid4 |
| `fastapi` | from fastapi import APIRouter, FastAPI, HTTPException, Path, Query, Response |
| `pydantic` | from pydantic import BaseModel, ConfigDict, Field |

### Internal Dependencies

| Module | Usage |
| --- | --- |
| `workspace_store` | from .workspace_store import WorkspaceStore, now_utc |

## 📁 Directory

This file is part of the **local_api** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- uses Pydantic models (BaseModel) to represent request and update payloads
- integrates with FastAPI via APIRouter/FastAPI and custom mounting function
- persists data using sqlite3 and manages revision/history tables
- defines numerous module-level constants to enforce limits and types (MAX_PROPERTIES, MAX_VIEWS, HISTORY_PAGE_SIZE, etc.)
- includes text normalization and key-generation utilities (unicodedata.normalize, uuid4, urlsplit)

## Maintenance Notes

- Define the input and update schemas for databases, views, properties and records using Pydantic models to drive validation and serialization.
- Provide a CustomDatabaseStore that manages persistence, revision tracking and constraints for local user-defined databases and their records.
- Offer helper functions for normalized text/keys, encoding and consistent HTTP error responses used by the API layer.
- Supply a mount_custom_databases function to integrate the custom databases endpoints into a FastAPI application or APIRouter.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `PropertyType` | — | `Literal['text', 'number', 'date', 'checkbox', 'select', 'multi_select', 'url', 'relation'…` |
| `ViewKind` | — | `Literal['table', 'board', 'calendar', 'timeline', 'gallery']` |
| `HistoryKind` | — | `Literal['record', 'view']` |
| `Scalar` | — | `str \| int \| float \| bool \| None` |
| `COMPUTED` | — | `frozenset({'formula', 'rollup'})` |
| `MAX_PROPERTIES` | — | `48` |
| `MAX_VIEWS` | — | `32` |
| `MAX_DATABASES` | — | `100` |
| `MAX_RECORDS` | — | `2000` |
| `MAX_RELATIONS` | — | `100` |
| `MAX_BATCH` | — | `100` |
| `MAX_NUMBER` | — | `1000000000000000.0` |
| `HISTORY_PAGE_SIZE` | — | `25` |
| `MAX_REVISION` | — | `2 ** 63 - 1` |
| `HISTORY_TABLES` | — | `{'record': ('custom_record_history', 'record_id'), 'view': ('custom_view_history', 'view_…` |



---

## Functions and Classes


### _invalid

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _invalid(message: str) -> HTTPException:
```

#### Description

Create and return an HTTPException representing an invalid request or operation using the provided message.

This helper centralizes construction of HTTP error responses for invalid custom database operations in the local API.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `message` | `str` | ✅ | — |

#### Returns

**Type:** `HTTPException`

—

#### Complexity

Not analyzed

---



### _missing

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _missing(resource: str) -> HTTPException:
```

#### Description

Constructs and returns an HTTPException indicating that a requested custom database resource is missing.

It takes the resource identifier and produces the appropriate HTTP error to be raised by the local API.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `resource` | `str` | ✅ | — |

#### Returns

**Type:** `HTTPException`

—

#### Complexity

Not analyzed

---



### _conflict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _conflict(message: str) -> HTTPException:
```

#### Description

Create and return an HTTPException representing a conflict (HTTP 409) using the provided message.

This helper centralizes construction of conflict errors for the local custom databases service.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `message` | `str` | ✅ | — |

#### Returns

**Type:** `HTTPException`

—

#### Complexity

Not analyzed

---



### _encode

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _encode(value: Any) -> str:
```

#### Description

Converts or serializes the provided Python value into a string representation.

This string is intended to be used wherever the module needs a textual form of arbitrary values (for example, for storage or transmission).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `Any` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### _text

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _text(value: Any, max_length: int, *, required: bool = False, multiline: bool = False) -> str:
```

#### Description

Validate and normalize an input value into a string that represents text constrained by a maximum length.

The function enforces whether the value is required and whether multi-line content is allowed, producing a sanitized string suitable for storage or further processing.


max_length limits the allowed length of the resulting string; required indicates that a missing or empty value should be treated as an error; multiline controls whether line breaks are permitted in the returned text.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `Any` | ✅ | — |
| `max_length` | `int` | ✅ | — |
| `required` = `False` | `bool` | ❌ | — |
| `multiline` = `False` | `bool` | ❌ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### _key

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _key(value: str) -> str:
```

#### Description

Generate and return a string key based on the provided input value.

The function accepts a string and produces another string intended to be used as a key within the custom databases module.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `str` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### Input

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

Input is a Pydantic model that represents and validates incoming data for the custom_databases module.

This class acts as the canonical input data transfer object within services/local_api/custom_databases.py, ensuring that data consumed by the module conforms to the expected schema and configuration.

Responsibilities:
- Define a typed schema for input data via inheritance from BaseModel.
- Provide validation and parsing behavior for input instances according to Pydantic rules.
- Expose model-level configuration through the model_config attribute to control serialization/validation behavior.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid', strict=True)` |

---



### Revision

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

Revision represents an input model that carries an expected revision number for a custom database operation.

Within services/local_api/custom_databases.py, Revision functions as the simple input model used by the module's operations to pass and check an expected revision number. It integrates with the module's input handling by providing a single, typed attribute for revision-related logic.

Responsibilities:
- Hold an integer value named expected_revision that represents the expected state or version of a resource.
- Provide a typed input container (as a subclass of Input) to be used wherever revision verification is required.
- Serve as a clear contract for callers and handlers to supply the expected revision number in API interactions.
- Enable validation and consistency checks elsewhere in the module by centralizing the expected revision datum.

#### Inheritance

**Inherits from:** `Input`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1, le=2 ** 63 - 1)` |

---



### DatabaseInput

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

DatabaseInput is a data holder type representing an input configuration for a custom database.

Within services/local_api/custom_databases.py, DatabaseInput functions as the canonical Input-derived representation of a database input, supplying a standardized name attribute for use by the module's database management and wiring logic.

Responsibilities:
- Provide a typed attribute 'name' (string) to identify or reference a custom database input.
- Serve as a concrete Input subclass used wherever input objects are required by the local API.
- Carry minimal, explicit metadata about a database input to ensure consistent handling across the module.
- Act as a simple, validated container that other components can inspect or serialize when managing custom databases.

#### Inheritance

**Inherits from:** `Input`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `name` (class) | `str` | 🔓 public | Class attribute name<br>**Default:** `Field(max_length=120)` |

---



### DatabaseUpdate

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green)

#### Description

DatabaseUpdate represents an update payload for a custom database, combining the input fields that define a database with revision metadata.

Within services/local_api/custom_databases.py this class functions as the canonical representation of an update operation for custom databases, bridging input data and revision tracking so the module can consistently handle modifications to stored databases.

Responsibilities:
- Encapsulate the editable properties of a custom database as defined by DatabaseInput.
- Include and expose revision information from the Revision base class to support versioning and concurrency control.
- Serve as a typed data structure used when submitting or processing updates to an existing custom database.
- Act as an interoperable object between components that create, validate, and persist database updates within the local API.

#### Inheritance

**Inherits from:** `DatabaseInput`, `Revision`

---



### PropertyInput

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

Represents a single property definition used when creating or updating a custom database schema.

Within services/local_api/custom_databases.py, this class models individual property inputs that compose a custom database schema and provides a structured way to pass property metadata and configuration through the module's revision and schema management logic.

Responsibilities:
- Hold the canonical name of the property as a string identifier.
- Specify the property's data or schema type via the PropertyType attribute.
- Store arbitrary configuration options for the property in a dictionary for use by revision or schema operations.
- Serve as a revisionable unit (via inheritance from Revision) so property definitions can be tracked or applied in revision workflows.

#### Inheritance

**Inherits from:** `Revision`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `name` (class) | `str` | 🔓 public | Class attribute name<br>**Default:** `Field(max_length=80)` |
| `type` (class) | `PropertyType` | 🔓 public | Class attribute type |
| `config` (class) | `dict[str, Any]` | 🔓 public | Class attribute config<br>**Default:** `Field(default_factory=dict, max_length=8)` |

---



### ViewConfig

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 7](https://img.shields.io/badge/Attributes-7-blue)

#### Description

ViewConfig models the configuration options for presenting or querying a custom database view.

Within services/local_api/custom_databases.py, ViewConfig serves as a structured input object that centralizes view-related parameters for custom database queries and presentations, enabling other components to consume consistent configuration data.

Responsibilities:
- Represent grouping configuration via an optional group_by property to determine how records are grouped in the view.
- Hold date-related configuration using date_property and end_date_property to indicate which fields represent single dates or date ranges.
- Specify sorting behavior with sort_by and sort_direction to control the ordering of records.
- Define a simple filter through filter_property and filter_value to limit which records are included in the view.

#### Inheritance

**Inherits from:** `Input`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `group_by` (class) | `str | None` | 🔓 public | Class attribute group_by<br>**Default:** `None` |
| `date_property` (class) | `str | None` | 🔓 public | Class attribute date_property<br>**Default:** `None` |
| `end_date_property` (class) | `str | None` | 🔓 public | Class attribute end_date_property<br>**Default:** `None` |
| `sort_by` (class) | `str | None` | 🔓 public | Class attribute sort_by<br>**Default:** `None` |
| `sort_direction` (class) | `Literal['asc', 'desc']` | 🔓 public | Class attribute sort_direction<br>**Default:** `'asc'` |
| `filter_property` (class) | `str | None` | 🔓 public | Class attribute filter_property<br>**Default:** `None` |
| `filter_value` (class) | `Scalar` | 🔓 public | Class attribute filter_value<br>**Default:** `None` |

---



### ViewInput

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

ViewInput represents a versioned description of a database view within the custom databases API.

Within services/local_api/custom_databases.py, ViewInput acts as the structured, versioned input object used when creating or updating views in custom databases, providing a compact representation of what a view is and how it should be configured.

Responsibilities:
- Carry the view's identifier through the revision lifecycle via the name attribute.
- Specify the semantic category of the view using the kind attribute (ViewKind).
- Contain the configuration details required to instantiate or modify the view via the config attribute (ViewConfig).
- Serve as a revisioned payload by inheriting from Revision, enabling change tracking and versioning of view definitions.

#### Inheritance

**Inherits from:** `Revision`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `name` (class) | `str` | 🔓 public | Class attribute name<br>**Default:** `Field(max_length=80)` |
| `kind` (class) | `ViewKind` | 🔓 public | Class attribute kind |
| `config` (class) | `ViewConfig` | 🔓 public | Class attribute config<br>**Default:** `Field(default_factory=ViewConfig)` |

---



### RecordInput

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

RecordInput is a data container class that represents an input record for the custom databases API.

Within services/local_api/custom_databases.py, this class models the structure of a single database record incoming to the local API, providing a consistent shape (title, notes, values) for other components to consume and validate.

Responsibilities:
- Hold the record's title as a short string identifier.
- Store freeform notes or description text associated with the record.
- Contain the record's data fields as a mapping from string keys to arbitrary values.
- Serve as a typed Input subclass used wherever structured record input is required by the module.

#### Inheritance

**Inherits from:** `Input`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(max_length=120)` |
| `notes` (class) | `str` | 🔓 public | Class attribute notes<br>**Default:** `Field(default='', max_length=8000)` |
| `values` (class) | `dict[str, Any]` | 🔓 public | Class attribute values<br>**Default:** `Field(default_factory=dict, max_length=MAX_PROPERTIES)` |

---



### RecordUpdate

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green)

#### Description

RecordUpdate is a data-model class that represents an update operation for a database record.

Within services/local_api/custom_databases.py, RecordUpdate acts as the combined input/revision representation used by the module's update-related logic. It provides a clear, reusable type for functions and endpoints that need to accept or process record updates.

Responsibilities:
- Encapsulate the fields required to submit an update to an existing record by inheriting the input schema from RecordInput.
- Carry revision information by inheriting from Revision so updates can be associated with or validated against a specific record version.
- Serve as the typed payload used by local API code paths that perform record update operations.
- Provide a single composite type that ensures update requests include both record content and revision context.

#### Inheritance

**Inherits from:** `RecordInput`, `Revision`

---



### RecordBatch

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

RecordBatch is a typed container that represents a collection of records intended to be provided as input.

Within services/local_api/custom_databases.py, RecordBatch serves as the concrete input model for supplying multiple records at once to local database-related operations and APIs. It functions as the module's representation of a batch payload composed of RecordInput entries.

Responsibilities:
- Hold an ordered list of RecordInput objects in the records attribute.
- Provide a single input structure that groups multiple records for batch operations.
- Ensure the batch is represented using the Input base class contract so it can be accepted wherever Input types are required.

#### Inheritance

**Inherits from:** `Input`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `records` (class) | `list[RecordInput]` | 🔓 public | Class attribute records<br>**Default:** `Field(min_length=1, max_length=MAX_BATCH)` |

---



### CustomDatabaseStore

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Methods: 41](https://img.shields.io/badge/Methods-41-blue)

#### Description

CustomDatabaseStore manages the storage, versioning, and access of user-defined databases, records, and views within the local API.

This class acts as the central storage manager within services/local_api/custom_databases.py, encapsulating persistence logic, transactional semantics, and historical tracking so other parts of the module can interact with custom databases and views through a stable API.

Responsibilities:
- Provide transactional access and low-level helpers for database, record, and view objects (_transaction, _db, _record, _view).
- Create, read, list and rename databases and views, and manage their persisted configurations (create_database, read_database, list_databases, list_views, rename_database, write_view).
- Manage record-level operations including adding records, computing record titles, and enforcing revision checks (_check_revision, add_records, record_titles).
- Maintain change history and snapshots for databases and views, including saving and listing history and restoring snapshots (_save_history, list_history, _restore_snapshot, _history_entry).
- Handle property-level persistence and configuration, unique naming, and versioning details for views and properties (write_property, _preserve_property_values, _property_config, _unique_name, _record_view_version).

#### Methods

##### Public Methods

| Method | Type | Description |
| --- | --- | --- |
| `__init__` | instance | Method __init__.<br>**Signature:** `def __init__(self, workspace: WorkspaceStore):` |
| `list_history` | instance | Method list_history.<br>**Signature:** `def list_history(self, database_id: str, kind: HistoryKind, item_id: str, before_revision: int | None) -> list[dict[str, Any]]:` |
| `list_databases` | instance | Method list_databases.<br>**Signature:** `def list_databases(self) -> list[dict[str, Any]]:` |
| `read_database` | instance | Method read_database.<br>**Signature:** `def read_database(self, database_id: str) -> dict[str, Any]:` |
| `list_views` | instance | Method list_views.<br>**Signature:** `def list_views(self, database_id: str) -> list[dict[str, Any]]:` |
| `record_titles` | instance | Method record_titles.<br>**Signature:** `def record_titles(self, database_id: str) -> list[dict[str, Any]]:` |
| `create_database` | instance | Method create_database.<br>**Signature:** `def create_database(self, body: DatabaseInput) -> dict[str, Any]:` |
| `rename_database` | instance | Method rename_database.<br>**Signature:** `def rename_database(self, database_id: str, body: DatabaseUpdate) -> dict[str, Any]:` |
| `write_property` | instance | Method write_property.<br>**Signature:** `def write_property(self, database_id: str, body: PropertyInput, property_id: str | None = None) -> dict[str, Any]:` |
| `write_view` | instance | Method write_view.<br>**Signature:** `def write_view(self, database_id: str, body: ViewInput, view_id: str | None = None) -> dict[str, Any]:` |
| `restore_view` | instance | Method restore_view.<br>**Signature:** `def restore_view(self, database_id: str, view_id: str, revision: int, body: Revision) -> dict[str, Any]:` |
| `add_records` | instance | Method add_records.<br>**Signature:** `def add_records(self, database_id: str, records: list[RecordInput]) -> list[dict[str, Any]]:` |
| `update_record` | instance | Method update_record.<br>**Signature:** `def update_record(self, database_id: str, record_id: str, body: RecordUpdate) -> dict[str, Any]:` |
| `restore_record` | instance | Method restore_record.<br>**Signature:** `def restore_record(self, database_id: str, record_id: str, revision: int, body: Revision) -> dict[str, Any]:` |
| `delete_record` | instance | Method delete_record.<br>**Signature:** `def delete_record(self, database_id: str, record_id: str, body: Revision) -> None:` |
| `search` | instance | Method search.<br>**Signature:** `def search(self, query: str) -> list[dict[str, Any]]:` |

##### Protected Methods

| Method | Type | Description |
| --- | --- | --- |
| `_transaction` | instance | Method _transaction.<br>**Signature:** `def _transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:` |
| `_db` | static | Method _db.<br>**Signature:** `def _db(db: sqlite3.Connection, database_id: str) -> sqlite3.Row:` |
| `_record` | static | Method _record.<br>**Signature:** `def _record(db: sqlite3.Connection, database_id: str, record_id: str) -> sqlite3.Row:` |
| `_view` | static | Method _view.<br>**Signature:** `def _view(db: sqlite3.Connection, database_id: str, view_id: str) -> sqlite3.Row:` |
| `_check_revision` | static | Method _check_revision.<br>**Signature:** `def _check_revision(row: sqlite3.Row, revision: int) -> None:` |
| `_definitions` | static | Method _definitions.<br>**Signature:** `def _definitions(db: sqlite3.Connection, database_id: str, definition: str) -> list[dict[str, Any]]:` |
| `_property` | static | Method _property.<br>**Signature:** `def _property(db: sqlite3.Connection, database_id: str, property_id: Any) -> sqlite3.Row:` |
| `_touch` | static | Method _touch.<br>**Signature:** `def _touch(db: sqlite3.Connection, database_id: str) -> None:` |
| `_history_entry` | static | Method _history_entry.<br>**Signature:** `def _history_entry(kind: HistoryKind, row: sqlite3.Row, database: sqlite3.Row) -> dict[str, Any]:` |
| `_save_history` | static | Method _save_history.<br>**Signature:** `def _save_history(db: sqlite3.Connection, kind: HistoryKind, item_id: str, entry: dict[str, Any]) -> None:` |
| `_restore_snapshot` | instance | Method _restore_snapshot.<br>**Signature:** `def _restore_snapshot(self, db: sqlite3.Connection, kind: HistoryKind, current: sqlite3.Row, database: sqlite3.Row, revision: int) -> dict[str, Any]:` |
| `_unique_name` | static | Method _unique_name.<br>**Signature:** `def _unique_name(definitions: list[dict[str, Any]], name: str, definition_id: str | None) -> None:` |
| `_preserve_property_values` | instance | Method _preserve_property_values.<br>**Signature:** `def _preserve_property_values(self, db: sqlite3.Connection, previous: sqlite3.Row, config: dict[str, Any]) -> None:` |
| `_property_config` | instance | Method _property_config.<br>**Signature:** `def _property_config(self, db: sqlite3.Connection, database_id: str, kind: str, config: dict[str, Any]) -> dict[str, Any]:` |
| `_keys` | static | Method _keys.<br>**Signature:** `def _keys(config: dict[str, Any], allowed: set[str]) -> None:` |
| `_record_view_version` | instance | Method _record_view_version.<br>**Signature:** `def _record_view_version(self, db: sqlite3.Connection, database_id: str, view_id: str) -> None:` |
| `_write_view` | instance | Method _write_view.<br>**Signature:** `def _write_view(self, db: sqlite3.Connection, database_id: str, body: ViewInput, view_id: str | None) -> dict[str, Any]:` |
| `_view_config` | instance | Method _view_config.<br>**Signature:** `def _view_config(self, db: sqlite3.Connection, database_id: str, body: ViewInput) -> dict[str, Any]:` |
| `_update_record` | instance | Method _update_record.<br>**Signature:** `def _update_record(self, db: sqlite3.Connection, database: sqlite3.Row, row: sqlite3.Row, body: RecordInput) -> dict[str, Any]:` |
| `_record_values` | instance | Method _record_values.<br>**Signature:** `def _record_values(self, db: sqlite3.Connection, properties: list[dict[str, Any]], body: RecordInput) -> tuple[str, str, dict[str, Any]]:` |
| `_value` | static | Method _value.<br>**Signature:** `def _value(db: sqlite3.Connection, kind: str, config: dict[str, Any], value: Any) -> Any:` |
| `_write_links` | static | Method _write_links.<br>**Signature:** `def _write_links(db: sqlite3.Connection, record_id: str, properties: list[dict[str, Any]], values: dict[str, Any]) -> None:` |
| `_target_values` | static | Method _target_values.<br>**Signature:** `def _target_values(db: sqlite3.Connection, properties: list[dict[str, Any]], records: list[sqlite3.Row]) -> dict[str, dict[str, Any]]:` |
| `_snapshot` | instance | Method _snapshot.<br>**Signature:** `def _snapshot(self, db: sqlite3.Connection, database_id: str) -> dict[str, Any]:` |
| `_record_payload` | static | Method _record_payload.<br>**Signature:** `def _record_payload(row: sqlite3.Row, properties: list[dict[str, Any]], target_values: dict[str, dict[str, Any]]) -> dict[str, Any]:` |

---



### __init__

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def __init__(self, workspace: WorkspaceStore):
```

#### Description

Initializes a CustomDatabaseStore instance and associates it with a given workspace.

This sets up the object so it can manage custom databases within the provided workspace context.


workspace is a WorkspaceStore representing the workspace context that this CustomDatabaseStore will operate against; it is stored for later use when performing workspace-scoped database operations.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `workspace` | `WorkspaceStore` | ✅ | — |

#### Complexity

Not analyzed

---



### _transaction

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
```

#### Description

A context manager method that provides a transactional sqlite3.Connection for performing database operations.

It yields a connection configured for either read-only use or for performing writes depending on the write flag.


write controls whether the yielded connection is intended for write operations (True) or for read-only access (False), affecting transaction behavior such as committing changes.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `write` = `False` | `bool` | ❌ | — |

#### Returns

**Type:** `Iterator[sqlite3.Connection]`

—

#### Complexity

Not analyzed

---



### _db

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _db(db: sqlite3.Connection, database_id: str) -> sqlite3.Row:
```

#### Description

Retrieve a single database record from the given SQLite connection corresponding to the provided database_id.

This static helper looks up and returns the database row for use by the CustomDatabaseStore.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |

#### Returns

**Type:** `sqlite3.Row`

—

#### Complexity

Not analyzed

---



### _record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _record(db: sqlite3.Connection, database_id: str, record_id: str) -> sqlite3.Row:
```

#### Description

Retrieve a single record row from a local SQLite database for the specified custom database and record identifiers.

This static method queries the provided sqlite3.Connection using the given database_id and record_id and returns the matching sqlite3.Row.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |

#### Returns

**Type:** `sqlite3.Row`

—

#### Complexity

Not analyzed

---



### _view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _view(db: sqlite3.Connection, database_id: str, view_id: str) -> sqlite3.Row:
```

#### Description

Fetches and returns a single view record for a given custom database from the provided SQLite connection.

The function looks up the view identified by view_id within the database identified by database_id and returns the corresponding row.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `view_id` | `str` | ✅ | — |

#### Returns

**Type:** `sqlite3.Row`

—

#### Complexity

Not analyzed

---



### _check_revision

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _check_revision(row: sqlite3.Row, revision: int) -> None:
```

#### Description

Validate that the provided sqlite3.Row corresponds to the expected revision number; if the row is missing or its stored revision does not match the given revision, the method will raise an error (ensuring callers do not proceed with an out-of-date or non-existent record).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `row` | `sqlite3.Row` | ✅ | — |
| `revision` | `int` | ✅ | — |

#### Complexity

Not analyzed

---



### _definitions

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _definitions(db: sqlite3.Connection, database_id: str, definition: str) -> list[dict[str, Any]]:
```

#### Description

Using the provided sqlite3 connection, this static helper produces the stored or computed definitions associated with the custom database identified by database_id, using the supplied definition string as the source or filter.

It returns those definitions represented as a list of dictionaries.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `definition` | `str` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### _property

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _property(db: sqlite3.Connection, database_id: str, property_id: Any) -> sqlite3.Row:
```

#### Description

Retrieve a single property row from a local custom databases table using the provided SQLite connection, database identifier, and property identifier.

This static method performs a database query against the given sqlite3.Connection and returns the matching row.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `property_id` | `Any` | ✅ | — |

#### Returns

**Type:** `sqlite3.Row`

—

#### Complexity

Not analyzed

---



### _touch

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _touch(db: sqlite3.Connection, database_id: str) -> None:
```

#### Description

Updates the state of a custom database entry identified by database_id in the provided sqlite3 connection to mark it as touched or recently used (e.g., updating a timestamp or ensuring the record exists).

It performs this operation without returning a value.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### _history_entry

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _history_entry(kind: HistoryKind, row: sqlite3.Row, database: sqlite3.Row) -> dict[str, Any]:
```

#### Description

Builds and returns a dictionary representing a history entry for a custom database change.

It takes a history kind enum and two sqlite3.Row objects (one for the history row and one for the database row) and composes a serializable dict containing the combined information.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `kind` | `HistoryKind` | ✅ | — |
| `row` | `sqlite3.Row` | ✅ | — |
| `database` | `sqlite3.Row` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _save_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _save_history(db: sqlite3.Connection, kind: HistoryKind, item_id: str, entry: dict[str, Any]) -> None:
```

#### Description

Insert or update a history entry for a specific item into the provided SQLite database.

The method records an entry of the given HistoryKind associated with the item_id using the provided dictionary of entry data.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `kind` | `HistoryKind` | ✅ | — |
| `item_id` | `str` | ✅ | — |
| `entry` | `dict[str, Any]` | ✅ | — |

#### Complexity

Not analyzed

---



### list_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_history(self, database_id: str, kind: HistoryKind, item_id: str, before_revision: int | None) -> list[dict[str, Any]]:
```

#### Description

Retrieve the historical change records for a specific item in a custom database.

It fetches history entries of the given kind for the item identified by item_id within the database identified by database_id, optionally limited to entries before a given revision.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `kind` | `HistoryKind` | ✅ | — |
| `item_id` | `str` | ✅ | — |
| `before_revision` | `int | None` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### _restore_snapshot

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _restore_snapshot(self, db: sqlite3.Connection, kind: HistoryKind, current: sqlite3.Row, database: sqlite3.Row, revision: int) -> dict[str, Any]:
```

#### Description

Restore a saved snapshot of a custom database into the provided sqlite3.Connection according to the given history kind and revision.

It applies the snapshot represented by the provided rows (current and database) for the specified revision and updates the database state accordingly.


db is the sqlite3.Connection to modify; kind is an enum indicating which type of history or snapshot to restore. current and database are sqlite3.Row objects describing the current snapshot/state and the database metadata to be restored, and revision is the integer revision number to restore.

Returns a dict mapping string keys to values with details about the restoration operation (e.g., status, updated metadata, or error information).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `kind` | `HistoryKind` | ✅ | — |
| `current` | `sqlite3.Row` | ✅ | — |
| `database` | `sqlite3.Row` | ✅ | — |
| `revision` | `int` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

Returns a dict mapping string keys to values with details about the restoration operation (e.g., status, updated metadata, or error information).

#### Complexity

Not analyzed

---



### list_databases

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_databases(self) -> list[dict[str, Any]]:
```

#### Description

Retrieve all custom database entries managed by this CustomDatabaseStore.

The method returns the collection of database records as in-memory Python dictionaries so callers can inspect or iterate over the stored custom database definitions.

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### read_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def read_database(self, database_id: str) -> dict[str, Any]:
```

#### Description

Retrieve and return the stored representation of a custom database identified by the given database_id from the local API store.

The method looks up the database and returns its contents as a dictionary containing the database's data and metadata.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### list_views

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_views(self, database_id: str) -> list[dict[str, Any]]:
```

#### Description

Return the collection of view definitions associated with a specific custom database.

Given a database identifier, it retrieves and returns each view as a dictionary of properties.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### record_titles

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def record_titles(self, database_id: str) -> list[dict[str, Any]]:
```

#### Description

Retrieve the stored title records for a specific custom database identified by database_id.

The method returns a collection of title entries associated with that database, each represented as a dictionary of fields and values.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### create_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_database(self, body: DatabaseInput) -> dict[str, Any]:
```

#### Description

Create a new custom database using the provided DatabaseInput payload.

The method validates and persists the database definition to the store and returns a representation of the newly created database as a dictionary.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `DatabaseInput` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### rename_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def rename_database(self, database_id: str, body: DatabaseUpdate) -> dict[str, Any]:
```

#### Description

Rename an existing custom database identified by database_id using the data supplied in the DatabaseUpdate body.

The method applies the update (typically a new name) to the stored database entry and returns the result of the operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `DatabaseUpdate` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _unique_name

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _unique_name(definitions: list[dict[str, Any]], name: str, definition_id: str | None) -> None:
```

#### Description

Checks that a proposed name is unique among a list of existing definition dictionaries and enforces uniqueness rules, taking into account an optional current definition identifier so the existing item can be excluded from the check.

definitions is the list of existing definition objects to check against, name is the candidate name to validate, and definition_id (if provided) identifies a definition to ignore during the uniqueness check (typically the item being updated).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `definitions` | `list[dict[str, Any]]` | ✅ | — |
| `name` | `str` | ✅ | — |
| `definition_id` | `str | None` | ✅ | — |

#### Complexity

Not analyzed

---



### write_property

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def write_property(self, database_id: str, body: PropertyInput, property_id: str | None = None) -> dict[str, Any]:
```

#### Description

Create or update a property definition for a custom database identified by database_id.

It sends the provided PropertyInput (body) to the store, optionally targeting an existing property when property_id is supplied, and persists the change.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `PropertyInput` | ✅ | — |
| `property_id` = `None` | `str | None` | ❌ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _preserve_property_values

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _preserve_property_values(self, db: sqlite3.Connection, previous: sqlite3.Row, config: dict[str, Any]) -> None:
```

#### Description

Copy or preserve specific property values from a previously stored database row into a new or updated configuration for a custom database.

It uses the provided sqlite3 connection and the previous row to transfer relevant properties into the given config dict so important values are kept across updates.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `previous` | `sqlite3.Row` | ✅ | — |
| `config` | `dict[str, Any]` | ✅ | — |

#### Complexity

Not analyzed

---



### _property_config

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _property_config(self, db: sqlite3.Connection, database_id: str, kind: str, config: dict[str, Any]) -> dict[str, Any]:
```

#### Description

Builds or retrieves the property-specific configuration for a custom database entry.

It uses the provided SQLite connection and identifiers (database_id and kind) together with an incoming config dictionary to produce the finalized property configuration mapping.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `kind` | `str` | ✅ | — |
| `config` | `dict[str, Any]` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _keys

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _keys(config: dict[str, Any], allowed: set[str]) -> None:
```

#### Description

Private static helper that performs operations related to the keys of a configuration mapping using a provided set of allowed keys.

It accepts a configuration dictionary and an allowed-key set and carries out its intended processing without returning a value.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `dict[str, Any]` | ✅ | — |
| `allowed` | `set[str]` | ✅ | — |

#### Complexity

Not analyzed

---



### write_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def write_view(self, database_id: str, body: ViewInput, view_id: str | None = None) -> dict[str, Any]:
```

#### Description

Create or update a view for a specified custom database.

If view_id is provided the function updates the existing view, otherwise it creates a new view using the provided ViewInput data.


body is a ViewInput object containing the configuration and properties of the view to be created or updated; database_id selects which custom database the view belongs to and view_id, when given, identifies the view to update.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `ViewInput` | ✅ | — |
| `view_id` = `None` | `str | None` | ❌ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _record_view_version

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _record_view_version(self, db: sqlite3.Connection, database_id: str, view_id: str) -> None:
```

#### Description

Record or update the stored version information for a particular view belonging to a custom database using the provided SQLite connection.

It writes metadata associating the given database_id and view_id with the current view version so the system can track view changes.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `view_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### _write_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _write_view(self, db: sqlite3.Connection, database_id: str, body: ViewInput, view_id: str | None) -> dict[str, Any]:
```

#### Description

Create or update a view record for a custom database using the provided SQLite connection.

It accepts the database identifier, the view input data, and an optional view identifier to determine whether to insert a new view or update an existing one, and returns a dictionary representing the stored view or operation result.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `body` | `ViewInput` | ✅ | — |
| `view_id` | `str | None` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### restore_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_view(self, database_id: str, view_id: str, revision: int, body: Revision) -> dict[str, Any]:
```

#### Description

Restore a specific view in a custom database to a given revision.

The method targets the view identified by view_id inside the database identified by database_id and applies the provided revision information to perform the restore operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `view_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |
| `body` | `Revision` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _view_config

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _view_config(self, db: sqlite3.Connection, database_id: str, body: ViewInput) -> dict[str, Any]:
```

#### Description

Builds or retrieves configuration data for a view related to a custom database identified by database_id, using the provided SQLite connection and the ViewInput payload.

It returns that view configuration as a dictionary suitable for further processing or storage.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |
| `body` | `ViewInput` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### add_records

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_records(self, database_id: str, records: list[RecordInput]) -> list[dict[str, Any]]:
```

#### Description

Add multiple records to a custom database identified by database_id.

The method accepts a list of RecordInput objects, stores them in the specified database, and returns information about the added records.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `records` | `list[RecordInput]` | ✅ | — |

#### Returns

**Type:** `list[dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### update_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_record(self, database_id: str, record_id: str, body: RecordUpdate) -> dict[str, Any]:
```

#### Description

Update an existing record in a custom database identified by database_id and record_id using the changes provided in the RecordUpdate body.

The method performs the update operation and returns the resulting record information or operation result as a dictionary.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `body` | `RecordUpdate` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _update_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _update_record(self, db: sqlite3.Connection, database: sqlite3.Row, row: sqlite3.Row, body: RecordInput) -> dict[str, Any]:
```

#### Description

Update an existing record in a custom database row using the provided sqlite3 connection, replacing or merging fields from the provided RecordInput and returning the updated record as a dictionary.

The method applies the update to the given database/row context and returns the record's current representation after the change.


body is a RecordInput containing the new field values to apply to the existing row; db is the active sqlite3.Connection, and database/row are sqlite3.Row objects identifying the custom database and the specific record to update.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database` | `sqlite3.Row` | ✅ | — |
| `row` | `sqlite3.Row` | ✅ | — |
| `body` | `RecordInput` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### restore_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_record(self, database_id: str, record_id: str, revision: int, body: Revision) -> dict[str, Any]:
```

#### Description

Restore a specific record in a custom database to a given revision.

It targets the record identified by database_id and record_id, applying the supplied revision number and Revision payload to perform the restore operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |
| `body` | `Revision` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### delete_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def delete_record(self, database_id: str, record_id: str, body: Revision) -> None:
```

#### Description

Delete a record from a custom database.

The method removes the identified record (record_id) from the specified database (database_id), using the provided Revision object (body) to indicate the revision/condition for the deletion.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `body` | `Revision` | ✅ | — |

#### Complexity

Not analyzed

---



### _record_values

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _record_values(self, db: sqlite3.Connection, properties: list[dict[str, Any]], body: RecordInput) -> tuple[str, str, dict[str, Any]]:
```

#### Description

Take a sqlite3 database connection, a list of property definitions, and a record input and process those values for storage.

The method prepares and records the values from the provided RecordInput according to the supplied properties using the given database connection and returns identification and the processed value set.


properties is a list of dictionaries that describe the schema or property metadata to use when interpreting the record; body is a RecordInput object containing the data to be recorded. The db parameter is the sqlite3.Connection to use for any database operations.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `properties` | `list[dict[str, Any]]` | ✅ | — |
| `body` | `RecordInput` | ✅ | — |

#### Returns

**Type:** `tuple[str, str, dict[str, Any]]`

—

#### Complexity

Not analyzed

---



### _value

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _value(db: sqlite3.Connection, kind: str, config: dict[str, Any], value: Any) -> Any:
```

#### Description

Prepare or transform a provided value for use with a custom database entry according to the given kind and configuration.

The function accepts a sqlite3 connection (for any DB-assisted processing), a kind identifier, and a config mapping, and returns the value after any necessary conversion or normalization.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `kind` | `str` | ✅ | — |
| `config` | `dict[str, Any]` | ✅ | — |
| `value` | `Any` | ✅ | — |

#### Returns

**Type:** `Any`

—

#### Complexity

Not analyzed

---



### _write_links

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _write_links(db: sqlite3.Connection, record_id: str, properties: list[dict[str, Any]], values: dict[str, Any]) -> None:
```

#### Description

Writes link-related data for a specific record into the provided SQLite database connection.

It takes a record identifier, a list of property definitions, and a mapping of property values and persists the link information into the database.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `properties` | `list[dict[str, Any]]` | ✅ | — |
| `values` | `dict[str, Any]` | ✅ | — |

#### Complexity

Not analyzed

---



### _target_values

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _target_values(db: sqlite3.Connection, properties: list[dict[str, Any]], records: list[sqlite3.Row]) -> dict[str, dict[str, Any]]:
```

#### Description

Constructs a mapping of target identifiers to their computed target value dictionaries by processing the provided database rows according to the given property definitions.

It uses the sqlite3 connection and the list of properties to derive per-record target data and returns those results aggregated into a dictionary.


properties is a list of property-definition dictionaries that describe how to compute target values for the records; records is a list of sqlite3.Row objects (database rows) to be processed. The db connection may be used for any lookups or transformations required while computing values.

A dictionary keyed by target identifier strings, each value being a dictionary of computed target attributes for that target.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `properties` | `list[dict[str, Any]]` | ✅ | — |
| `records` | `list[sqlite3.Row]` | ✅ | — |

#### Returns

**Type:** `dict[str, dict[str, Any]]`

A dictionary keyed by target identifier strings, each value being a dictionary of computed target attributes for that target.

#### Complexity

Not analyzed

---



### _snapshot

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _snapshot(self, db: sqlite3.Connection, database_id: str) -> dict[str, Any]:
```

#### Description

Read the current state of a specific custom database from the given SQLite connection and produce a serializable snapshot of its contents and metadata.

The snapshot is returned as a dictionary keyed by descriptive fields so the database state can be inspected, stored, or compared.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db` | `sqlite3.Connection` | ✅ | — |
| `database_id` | `str` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### _record_payload

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def _record_payload(row: sqlite3.Row, properties: list[dict[str, Any]], target_values: dict[str, dict[str, Any]]) -> dict[str, Any]:
```

#### Description

Constructs and returns a dictionary payload for a database record by extracting values from the given sqlite3.Row and combining them with the provided property metadata and any per-target overrides.

It assembles a record representation suitable for downstream use (e.g., API responses or storage) based on the properties list and target_values mapping.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `row` | `sqlite3.Row` | ✅ | — |
| `properties` | `list[dict[str, Any]]` | ✅ | — |
| `target_values` | `dict[str, dict[str, Any]]` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### search

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def search(self, query: str) -> list[dict[str, Any]]:
```

#### Description

Perform a search of the custom database store for items that match the provided query string.

The method uses internal helper functions (matches and values_match) to determine which records satisfy the query and returns those matching records as a list of dictionaries.

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



### matches

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def matches(*values: str) -> bool:
```

#### Description

Determine whether an item satisfies a set of textual criteria provided as string arguments.

The function accepts any number of string values and evaluates whether the target being tested matches those values according to the search/matching logic of the enclosing CustomDatabaseStore.search context.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `values` | `str` | ❌ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### values_match

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def values_match(raw: str) -> bool:
```

#### Description

Determines whether the provided raw string matches the expected values according to the function's internal matching logic.

It evaluates the input and returns a boolean indicating whether the match criteria are satisfied. The function contains a nested helper named 'visible' used as part of that evaluation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `raw` | `str` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### visible

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def visible(value: Any) -> str:
```

#### Description

Convert an arbitrary input value into a string representation suitable for visibility checks or display.

The function takes any Python value and returns a string that represents that value in a consistent, usable form.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `Any` | ✅ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### mount_custom_databases

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def mount_custom_databases(app: FastAPI, store: CustomDatabaseStore) -> None:
```

#### Description

Register a set of HTTP endpoint handlers on the given FastAPI application to manage custom databases using the provided CustomDatabaseStore.

It mounts routes for listing, creating, reading and renaming databases, managing properties, views and view history, and creating, updating, listing history for, restoring and deleting records.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `app` | `FastAPI` | ✅ | — |
| `store` | `CustomDatabaseStore` | ✅ | — |

#### Complexity

Not analyzed

---



### list_databases

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_databases():
```

#### Description

HTTP GET endpoint that returns the available custom databases registered via the mount_custom_databases module.

It provides a way to retrieve a list of the configured custom databases.


Returns a representation (typically JSON) of the list of available custom databases.

#### Complexity

Not analyzed

---



### create_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_database(body: DatabaseInput):
```

#### Description

Expose an HTTP POST endpoint that creates a new custom database using the information provided in the request body.

It accepts a DatabaseInput object, processes that configuration, and registers or mounts the new custom database in the application.


body is a DatabaseInput instance carrying the configuration and connection details required to create and register the custom database (e.g., name, connection parameters, and any metadata).

Returns an HTTP response or created-database representation indicating whether the database was successfully created and mounted, or an error describing why creation failed.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `DatabaseInput` | ✅ | — |

#### Complexity

Not analyzed

---



### read_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def read_database(database_id: str):
```

#### Description

An API GET endpoint that retrieves information for a specific custom database identified by the provided database_id.

It looks up and returns the database resource corresponding to that identifier.


Returns the database details for the given database_id (typically the database record/representation, e.g., as a JSON response) or an appropriate error if the resource is not found.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### rename_database

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def rename_database(database_id: str, body: DatabaseUpdate):
```

#### Description

Updates the name (or other updatable fields) of a mounted custom database resource identified by the given database_id using the data provided in the DatabaseUpdate payload.

This is exposed as an HTTP PUT endpoint (router.put) to perform the rename/update operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `DatabaseUpdate` | ✅ | — |

#### Complexity

Not analyzed

---



### add_property

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_property(database_id: str, body: PropertyInput):
```

#### Description

Defines a POST endpoint that adds a new property to a custom database identified by database_id.

It accepts the property's data in the body as a PropertyInput and registers that property with the specified database.


Returns an HTTP response indicating the result of the operation, typically including confirmation of creation or the created property's details.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `PropertyInput` | ✅ | — |

#### Complexity

Not analyzed

---



### edit_property

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def edit_property(database_id: str, property_id: str, body: PropertyInput):
```

#### Description

Handle an HTTP PUT request to modify an existing property on a custom database identified by database_id and property_id, using the data provided in the PropertyInput body.

It updates the specified property's configuration or metadata in that custom database.


Returns an HTTP response representing the result of the update, typically including the updated property representation or a status indicating success or failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `property_id` | `str` | ✅ | — |
| `body` | `PropertyInput` | ✅ | — |

#### Complexity

Not analyzed

---



### add_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_view(database_id: str, body: ViewInput):
```

#### Description

Exposes an HTTP POST endpoint that adds a new view to a specified custom database.

It accepts the ID of the target database and the view definition payload, then creates or registers that view within the database.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `ViewInput` | ✅ | — |

#### Complexity

Not analyzed

---



### list_views

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_views(database_id: str):
```

#### Description

HTTP GET endpoint that lists the views associated with a specific custom database.

It retrieves and returns the collection of views for the database identified by the provided database_id.


Returns the list of views (likely as a JSON response) for the specified database_id, containing view metadata or definitions.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### edit_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def edit_view(database_id: str, view_id: str, body: ViewInput):
```

#### Description

Handles HTTP PUT requests to edit an existing view for a custom database.

It updates the view identified by view_id within the database identified by database_id using the data provided in the body parameter.


Returns the result of the update operation, typically the updated View representation or an HTTP response indicating success or failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `view_id` | `str` | ✅ | — |
| `body` | `ViewInput` | ✅ | — |

#### Complexity

Not analyzed

---



### view_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def view_history(database_id: str, view_id: str, before_revision: int | None = Query(None, ge=1, le=MAX_REVISION)):
```

#### Description

HTTP GET endpoint that returns the revision history for a specific view within a mounted custom database.

It accepts a database identifier, a view identifier, and an optional before_revision query parameter to limit the returned history to revisions earlier than or equal to that number.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `view_id` | `str` | ✅ | — |
| `before_revision` = `Query(None, ge=1, le=MAX_REVISION)` | `int | None` | ❌ | — |

#### Complexity

Not analyzed

---



### restore_view

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_view(database_id: str, view_id: str, body: Revision, revision: int = Path(ge=1, le=MAX_REVISION)):
```

#### Description

Expose an HTTP POST endpoint that restores a specific view in a custom database to a given revision.

It targets the view identified by view_id within the database identified by database_id and applies the provided Revision payload to perform the restore.


database_id and view_id identify the target database and view; body is a Revision object describing the revision state to restore; revision is a path parameter constrained to be between 1 and MAX_REVISION indicating which revision to restore to.

Returns an HTTP response indicating the outcome of the restore operation (e.g., success or error details).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `view_id` | `str` | ✅ | — |
| `body` | `Revision` | ✅ | — |
| `revision` = `Path(ge=1, le=MAX_REVISION)` | `int` | ❌ | — |

#### Complexity

Not analyzed

---



### add_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_record(database_id: str, body: RecordInput):
```

#### Description

HTTP POST handler that adds a new record to a custom database identified by database_id.

It accepts the record data in the body and persists it to the specified custom database.


Returns the result of the create operation, typically the created record or an HTTP response indicating success or failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `RecordInput` | ✅ | — |

#### Complexity

Not analyzed

---



### record_titles

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def record_titles(database_id: str):
```

#### Description

This function is an HTTP GET endpoint that records or retrieves the titles associated with a custom database identified by the given database_id.

It is intended to be used as part of mounting custom databases in the local API so clients can obtain or update the title entries for that database.


Returns an HTTP response (likely JSON) containing the recorded titles for the specified database_id or a status indicating the result of the recording operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### add_records

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def add_records(database_id: str, body: RecordBatch):
```

#### Description

Expose an HTTP POST endpoint that receives a batch of records and adds them to the specified custom database identified by database_id.

It accepts the incoming RecordBatch payload and persists those records into the database managed by this service.


Returns an HTTP response indicating success or failure of the operation, typically confirming that the records were created/ingested (and may include identifiers or status details) or returning an error description on failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `body` | `RecordBatch` | ✅ | — |

#### Complexity

Not analyzed

---



### update_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_record(database_id: str, record_id: str, body: RecordUpdate):
```

#### Description

Handles an HTTP PUT request to update an existing record in a custom database identified by database_id and record_id, applying the changes provided in the RecordUpdate body.

Returns an HTTP response containing the result of the update operation, typically the updated record representation or a success status.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `body` | `RecordUpdate` | ✅ | — |

#### Complexity

Not analyzed

---



### record_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def record_history(database_id: str, record_id: str, before_revision: int | None = Query(None, ge=1, le=MAX_REVISION)):
```

#### Description

Handles a GET request to retrieve the revision history for a specific record in a mounted custom database.

It fetches the record's historical revisions and can limit which revisions are included based on an optional revision bound.


database_id and record_id identify which database and record to retrieve history for; before_revision is an optional integer that, when provided, acts as a bound to restrict which historical revisions are returned (must be between 1 and MAX_REVISION).

Returns the record's history (the set of historical revisions/entries), optionally limited by the before_revision parameter.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `before_revision` = `Query(None, ge=1, le=MAX_REVISION)` | `int | None` | ❌ | — |

#### Complexity

Not analyzed

---



### restore_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_record(database_id: str, record_id: str, body: Revision, revision: int = Path(ge=1, le=MAX_REVISION)):
```

#### Description

Restore a specific revision of a record in a custom database.

This endpoint accepts a Revision payload and a revision number to restore the specified record version for the given database and record identifiers.


database_id and record_id identify which record to operate on; body is a Revision model containing the revision data to apply; revision is a path parameter constrained to be between 1 and MAX_REVISION that selects which revision to restore.

Returns the result of the restore operation, typically the restored record or a confirmation/status object indicating success or failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `body` | `Revision` | ✅ | — |
| `revision` = `Path(ge=1, le=MAX_REVISION)` | `int` | ❌ | — |

#### Complexity

Not analyzed

---



### delete_record

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def delete_record(database_id: str, record_id: str, body: Revision):
```

#### Description

Handles an HTTP DELETE request to remove a specific record from a mounted custom database.

It identifies the target by database_id and record_id and uses the provided Revision payload to perform the deletion (e.g., for concurrency/version checks).


database_id and record_id identify which database and record to delete; body is a Revision object likely used to validate or match the record's revision before deletion to prevent concurrent modification conflicts.

Returns an HTTP response indicating the outcome of the deletion operation (success or failure), potentially including status codes and any relevant error information.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database_id` | `str` | ✅ | — |
| `record_id` | `str` | ✅ | — |
| `body` | `Revision` | ✅ | — |

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

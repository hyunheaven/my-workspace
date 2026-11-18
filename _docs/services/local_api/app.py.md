<!-- METADATA: {"source_path": "services/local_api/app.py", "source_sha": "03589a538b397d2635ab834dd70810bc1207089f", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:20:15Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "services/local_api/app.py",
  "source_hash": "bf0d85e27660978dad74064707f736ad03b6e5a4c7510c7e58f51820b30d3f16",
  "last_updated": "2026-11-18T03:19:58.826767+00:00",
  "git_sha": "03589a538b397d2635ab834dd70810bc1207089f",
  "tokens_used": 32826,
  "complexity_score": 9,
  "estimated_review_time_minutes": 52,
  "external_dependencies": [
    "__future__",
    "hashlib",
    "json",
    "os.path",
    "re",
    "ipaddress",
    "pathlib",
    "uuid",
    "datetime",
    "urllib.parse",
    "unicodedata",
    "typing",
    "zoneinfo",
    "fastapi",
    "fastapi.responses",
    "pydantic",
    "collections"
  ]
}
```

</details>

[Documentation Home](../../README.md) > [services](../README.md) > [local_api](./README.md) > **app**

---

# app.py

> **File:** `services/local_api/app.py`

![Complexity: High](https://img.shields.io/badge/Complexity-High-red) ![Review Time: 52min](https://img.shields.io/badge/Review_Time-52min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module implements a local-only template editor API using FastAPI and a set of Pydantic models to represent documents, pages, canvas content, projects, tasks and events. It declares numerous data models (CreateDoc, UpdateDoc, BlankPage, PageFromTemplate, CanvasBlock, CanvasContent, CreateProject, UpdateProject, TaskData, EventData, and related update/operation variants) that define the shapes of requests and payloads the application expects. The module also provides a collection of validation and utility functions (for text normalization, date validation, task and event validation, range checks, and value checking) as well as constants that govern file locations and payload size limits.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `__future__` | from __future__ import annotations |
| `hashlib` | from hashlib import sha256 |
| `json` | import json |
| `os.path` | from os.path import normcase |
| `re` | import re |
| `ipaddress` | import ipaddress |
| `pathlib` | from pathlib import Path |
| `uuid` | from uuid import uuid4 |
| `datetime` | from datetime import date, datetime, timedelta, timezone |
| `urllib.parse` | from urllib.parse import urlsplit |
| `unicodedata` | from unicodedata import normalize |
| `typing` | from typing import Any, Literal |
| `zoneinfo` | from zoneinfo import ZoneInfo, ZoneInfoNotFoundError |
| `fastapi` | from fastapi import FastAPI, HTTPException, Query, Request, Response |
| `fastapi.responses` | from fastapi.responses import FileResponse, JSONResponse |
| `pydantic` | from pydantic import BaseModel, ConfigDict, Field, model_validator |
| `collections` |         from collections import Counter |

### Internal Dependencies

| Module | Usage |
| --- | --- |
| `workspace_store` | from .workspace_store import UUID_PATTERN, WorkspaceStore |
| `custom_databases` | from .custom_databases import CustomDatabaseStore, mount_custom_databases |
| `storage` | from .storage import default_db_path |
| `page_templates` | from .page_templates import template_blocks |
| `page_database_views` | from .page_database_views import mount_page_database_views |

## 📁 Directory

This file is part of the **local_api** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Uses Pydantic BaseModel subclasses extensively to define API payload schemas and update/operation variants.
- Builds on FastAPI (create_app returns an app) to expose the local API surface.
- Defines module-level validation and helper functions to centralize input checks and normalization before handling requests.
- Declares typed Literal constants for enumerations (project/task statuses, priority, block types) and module-level constants for resource limits and file paths.

## Maintenance Notes

- Define the domain data contracts for the API using Pydantic models for documents, pages, canvas structures, projects, tasks and events.
- Provide validation utilities (e.g., valid_block_text, clean_text, valid_date_optional, validate_task, validate_event) to enforce input constraints before processing.
- Expose configuration constants and file paths used by the application (catalog paths, public static directory, maximum body sizes, and typed status/value Literals).
- Create and return the FastAPI application instance via the create_app function, wiring the API to use the defined models and validation logic.
- Support page and canvas manipulation semantics through operation models such as PageRevisionOperation, DuplicatePage, MovePage, CanvasUpdate and CanvasImport.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `CATALOG_PATH` | — | `Path(__file__).with_name('catalog.json')` |
| `LIBRARY_CATALOG_PATH` | — | `Path(__file__).with_name('catalog_library.json')` |
| `PUBLIC_DIR` | — | `Path(__file__).resolve().parents[2] / 'apps' / 'local-client' / 'static'` |
| `MAX_BODY` | — | `64 * 1024` |
| `MAX_CANVAS_BODY` | — | `256 * 1024` |
| `PROJECT_STATUS` | — | `Literal['planned', 'active', 'on_hold', 'completed']` |
| `TASK_STATUS` | — | `Literal['todo', 'in_progress', 'blocked', 'done', 'archived']` |
| `PRIORITY` | — | `Literal['low', 'medium', 'high']` |
| `BlockType` | — | `Literal['paragraph', 'heading_1', 'heading_2', 'bullet', 'todo', 'toggle', 'quote', 'code…` |
| `app` | — | `create_app()` |



---

## Functions and Classes


### CreateDoc

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 5](https://img.shields.io/badge/Attributes-5-blue)

#### Description

CreateDoc is a Pydantic model that defines the data structure required to create a document in the local API.

Within the module, CreateDoc acts as the typed input model for operations that create documents, enabling consistent validation and serialization of creation requests. It integrates with the file's logic by representing the structured payload the local API expects when creating a document.

Responsibilities:
- Validate and hold the document creation payload: template_id, title, values, and optional parent_id.
- Enforce types and constraints via Pydantic (string types for template_id and title, a dict of string->string for values, and an optional parent_id).
- Provide a clear schema for consumers and other parts of the application to construct or parse create-document requests.
- Serve as a single source of truth for what data is required to instantiate a new document in the local API.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `template_id` (class) | `str` | 🔓 public | Class attribute template_id<br>**Default:** `Field(min_length=1, max_length=100)` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(min_length=1, max_length=120)` |
| `values` (class) | `dict[str, str]` | 🔓 public | Class attribute values<br>**Default:** `Field(default_factory=dict)` |
| `parent_id` (class) | `str | None` | 🔓 public | Class attribute parent_id<br>**Default:** `None` |

---



### UpdateDoc

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 4](https://img.shields.io/badge/Attributes-4-blue)

#### Description

Represents an update payload for a document in the local API, validating and carrying the fields needed to apply an update.

Acts as the typed request/transfer object within services/local_api/app.py for update operations, ensuring incoming update data conforms to the expected shape and types before being processed by the application.

Responsibilities:
- Declare and validate the expected_revision number to coordinate optimistic concurrency when applying updates.
- Hold the title string that will be applied to the document during an update.
- Contain a mapping of field names to their new string values in the values dictionary.
- Provide pydantic model configuration via model_config to control serialization/validation behavior.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1)` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(min_length=1, max_length=120)` |
| `values` (class) | `dict[str, str]` | 🔓 public | Class attribute values<br>**Default:** `Field(default_factory=dict)` |

---



### BlankPage

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

A small pydantic data model that represents a blank page entity with a required title and an optional parent identifier.

Serves as the canonical data representation of a blank page within the local_api application, enabling typed input/output handling and consistent validation for components that create, transmit, or store page information.

Responsibilities:
- Define and validate the page data structure with a title (str) and an optional parent_id (str or None).
- Provide pydantic model configuration via the model_config attribute to control serialization/validation behavior.
- Serialize and deserialize page instances for use in API request/response cycles or internal data passing.
- Act as a typed container so other parts of the code can rely on a consistent shape for blank page data.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(default='제목 없음', min_length=1, max_length=120)` |
| `parent_id` (class) | `str | None` | 🔓 public | Class attribute parent_id<br>**Default:** `None` |

---



### PageFromTemplate

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 4](https://img.shields.io/badge/Attributes-4-blue)

#### Description

PageFromTemplate is a Pydantic data model that represents the input needed to create or reference a page based on an existing template.

Within services/local_api/app.py, this class serves as the typed input contract for operations that create or reference pages from templates. It centralizes the required identifiers so other components in the module can rely on a consistent, validated payload.

Responsibilities:
- Validate and store the template identifier used to generate or reference the page (template_id).
- Validate and store a request identifier that ties the operation to a higher-level request or workflow (request_id).
- Optionally hold a parent page identifier when the new or referenced page should be placed under an existing parent (parent_id).
- Provide a structured, typed container that other parts of the module can consume to perform template-based page operations.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `template_id` (class) | `str` | 🔓 public | Class attribute template_id<br>**Default:** `Field(min_length=1, max_length=100)` |
| `request_id` (class) | `str` | 🔓 public | Class attribute request_id<br>**Default:** `Field(pattern=UUID_PATTERN)` |
| `parent_id` (class) | `str | None` | 🔓 public | Class attribute parent_id<br>**Default:** `Field(default=None, pattern=UUID_PATTERN)` |

---



### PageRevisionOperation

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 2](https://img.shields.io/badge/Attributes-2-blue)

#### Description

A pydantic data model that represents an operation which carries an expected page revision number and associated model configuration.

Within services/local_api/app.py this class serves as the typed pydantic representation of a page-revision operation, allowing the module to accept, validate, and propagate an expected_revision value according to the model_config settings.

Responsibilities:
- Hold the expected_revision integer that other code can inspect to determine the intended page revision.
- Enforce data validation and serialization behavior as configured by the model_config pydantic settings.
- Act as a typed container for revision-related information passed between components in the application.
- Provide a single source of truth for the expected revision value when performing revision checks or updates.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1, le=2 ** 63 - 1)` |

---



### DuplicatePage

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

DuplicatePage represents a page-revision operation that carries the identifier for a duplicate-page request.

As a subclass of PageRevisionOperation in services/local_api/app.py, DuplicatePage models the specific operation of duplicating a page and supplies the request_id needed by the surrounding local API logic to route and handle that operation.

Responsibilities:
- Carry the request identifier (request_id) for a duplicate-page operation.
- Serve as a specialized variant of PageRevisionOperation representing a duplication action.
- Provide a clear, typed container for passing the duplication request id through the local API stack.
- Differentiate duplicate-page operations from other page-revision operations via its class identity and request_id attribute.

#### Inheritance

**Inherits from:** `PageRevisionOperation`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `request_id` (class) | `str` | 🔓 public | Class attribute request_id<br>**Default:** `Field(pattern=UUID_PATTERN)` |

---



### PagePropertiesUpdate

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Methods: 1](https://img.shields.io/badge/Methods-1-blue) ![Attributes: 6](https://img.shields.io/badge/Attributes-6-blue)

#### Description

PagePropertiesUpdate is a Pydantic model that represents an update payload for a page's configurable properties.

As a typed data container in services/local_api/app.py, this class standardizes incoming or outgoing page property updates for the local API layer, enabling consistent validation and downstream handling of page change requests.

Responsibilities:
- Define and validate the shape and types of page property updates (theme, background, tab_color, tags, and expected_revision) using Pydantic typing and literals.
- Provide a place to store model-level configuration via model_config for Pydantic behavior.
- Hold the canonical list of tags for the page and offer normalization of those tags through the normalize_tags method.
- Ensure background can be explicitly nullable while other properties enforce the allowed literal choices.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid', strict=True)` |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=0, le=2 ** 63 - 1)` |
| `theme` (class) | `Literal['inherit', 'warm', 'sage', 'indigo', 'clay', 'dark', 'ocean', 'lavender', 'rose', 'slate', 'contrast']` | 🔓 public | Class attribute theme<br>**Default:** `'inherit'` |
| `background` (class) | `Literal['plain', 'paper', 'mint', 'mist', 'grid', 'ruled', 'graph', 'margin', 'cream', 'rosepaper'] | None` | 🔓 public | Class attribute background<br>**Default:** `None` |
| `tab_color` (class) | `Literal['none', 'sage', 'ocean', 'indigo', 'lavender', 'rose', 'clay', 'gold', 'slate']` | 🔓 public | Class attribute tab_color<br>**Default:** `'none'` |
| `tags` (class) | `list[str]` | 🔓 public | Class attribute tags<br>**Default:** `Field(default_factory=list, max_length=16)` |

#### Methods

##### Public Methods

| Method | Type | Description |
| --- | --- | --- |
| `normalize_tags` | instance | Method normalize_tags.<br>**Signature:** `def normalize_tags(self):` |

---



### normalize_tags

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def normalize_tags(self):
```

#### Description

Normalize and canonicalize the tag data on the PagePropertiesUpdate model when the model is validated.

It enforces a consistent representation for tags (for example by trimming, deduplicating, or converting formats) so the model always holds tags in a predictable form.


As a model validator, it produces the normalized tag data used to populate the model during validation (i.e., it returns the validated/normalized tag values or otherwise applies them to the instance for the final model state).

#### Complexity

Not analyzed

---



### valid_block_text

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def valid_block_text(value: str) -> bool:
```

#### Description

Checks whether the provided string is a valid block of text according to the module's validation rules.

It accepts a string input and returns a boolean indicating validity.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `str` | ✅ | — |

#### Returns

**Type:** `bool`

—

#### Complexity

Not analyzed

---



### CanvasBlock

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Methods: 2](https://img.shields.io/badge/Methods-2-blue) ![Attributes: 6](https://img.shields.io/badge/Attributes-6-blue)

#### Description

CanvasBlock is a pydantic data model that represents a single block element used by the local API canvas.

Within services/local_api/app.py, CanvasBlock serves as the typed data container for block objects exchanged and persisted by the local API, enabling consistent validation and serialization of block data throughout the module.

Responsibilities:
- Define and validate the shape of a canvas block including id, type, content, checked, and depth fields.
- Enforce content correctness via the validate_content method before persistence or use.
- Provide a stored representation or indicator through the stored method to support persistence workflows.
- Carry model configuration options via model_config inherited from BaseModel.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `id` (class) | `str` | 🔓 public | Class attribute id<br>**Default:** `Field(pattern='^[a-f0-9-]{36}$')` |
| `type` (class) | `BlockType` | 🔓 public | Class attribute type |
| `content` (class) | `str` | 🔓 public | Class attribute content<br>**Default:** `Field(default='', max_length=4000)` |
| `checked` (class) | `bool` | 🔓 public | Class attribute checked<br>**Default:** `False` |
| `depth` (class) | `int` | 🔓 public | Class attribute depth<br>**Default:** `Field(default=0, ge=0, le=6, strict=True)` |

#### Methods

##### Public Methods

| Method | Type | Description |
| --- | --- | --- |
| `stored` | instance | Method stored.<br>**Signature:** `def stored(self) -> dict[str, Any]:` |
| `validate_content` | instance | Method validate_content.<br>**Signature:** `def validate_content(self):` |

---



### stored

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def stored(self) -> dict[str, Any]:
```

#### Description

Return a serializable representation of this CanvasBlock's persisted state.

The method produces a dictionary containing the block's stored data and attributes suitable for saving or inspection.

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### validate_content

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def validate_content(self):
```

#### Description

Run model-level validation for a CanvasBlock instance's content when the model is constructed or updated.

It enforces consistency and correctness of the block's content fields, raising validation errors if required fields are missing or values are invalid.

#### Complexity

Not analyzed

---



### CanvasContent

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Methods: 1](https://img.shields.io/badge/Methods-1-blue) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

CanvasContent is a Pydantic model that represents the top-level content of a canvas, holding a title and an ordered list of CanvasBlock objects.

Within services/local_api/app.py, CanvasContent serves as the primary data container for canvas payloads handled by the module, ensuring the title and blocks conform to expected types and validation rules before further processing.

Responsibilities:
- Store the canvas title as a string in the title attribute.
- Contain an ordered collection of CanvasBlock objects in the blocks attribute.
- Provide model configuration through model_config for Pydantic behavior and serialization.
- Validate the blocks list and enforce any block-level constraints via the validate_blocks method.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(min_length=1, max_length=120)` |
| `blocks` (class) | `list[CanvasBlock]` | 🔓 public | Class attribute blocks<br>**Default:** `Field(default_factory=list, max_length=120)` |

#### Methods

##### Public Methods

| Method | Type | Description |
| --- | --- | --- |
| `validate_blocks` | instance | Method validate_blocks.<br>**Signature:** `def validate_blocks(self):` |

---



### validate_blocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def validate_blocks(self):
```

#### Description

Run model-level validation for a CanvasContent instance to check and enforce correctness of its block data.

As a model_validator-decorated method, it performs any consistency checks or normalization required for the instance's block structure and raises validation errors if the blocks are invalid.

#### Complexity

Not analyzed

---



### CanvasUpdate

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

CanvasUpdate represents an update packet for canvas content that includes an expected revision number.

Within services/local_api/app.py this class functions as the specific form of CanvasContent used for updates that require revision control. It integrates with the module's canvas handling logic to ensure updates are associated with an expected revision.

Responsibilities:
- Carry the expected_revision integer that indicates the revision the update targets.
- Provide a typed representation of a canvas update by inheriting common behavior from CanvasContent.
- Serve as a version-aware container used when applying or validating changes against current canvas state.
- Enable callers to compare or enforce revision expectations before committing updates.

#### Inheritance

**Inherits from:** `CanvasContent`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1)` |

---



### CanvasImport

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

CanvasImport represents an importable piece of canvas content that may be associated with a parent item.

As a subclass of CanvasContent in services/local_api/app.py, CanvasImport provides a focused representation of content used during import-related workflows, specifically handling optional parent relationships within the module's canvas content model.

Responsibilities:
- Carry the parent relationship for a unit of canvas content through the parent_id attribute, allowing callers to determine nesting or ownership.
- Provide a specialized CanvasContent subtype that explicitly supports an optional parent reference.
- Serve as a lightweight data holder for import operations where parent linkage is relevant.
- Convey the presence or absence of parent linkage (using None) so import logic can conditionally attach or treat content as top-level.

#### Inheritance

**Inherits from:** `CanvasContent`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `parent_id` (class) | `str | None` | 🔓 public | Class attribute parent_id<br>**Default:** `Field(default=None, pattern=UUID_PATTERN)` |

---



### MovePage

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 3](https://img.shields.io/badge/Attributes-3-blue)

#### Description

MovePage is a Pydantic data model that represents the payload for a page-move operation, capturing the expected revision number and an optional new parent identifier.

Within services/local_api/app.py, MovePage serves as the schema for incoming or internal move-page requests, ensuring the move operation receives well-formed and validated input data.

Responsibilities:
- Define and validate the shape of data required to perform a page move (expected_revision and optional parent_id).
- Enforce types for expected_revision (int) and parent_id (str or None) through Pydantic's BaseModel behavior.
- Provide model configuration via the model_config attribute to control Pydantic model behavior.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1)` |
| `parent_id` (class) | `str | None` | 🔓 public | Class attribute parent_id<br>**Default:** `None` |

---



### CreateProject

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 4](https://img.shields.io/badge/Attributes-4-blue)

#### Description

CreateProject is a pydantic model that defines the data shape for creating a new project.

Within services/local_api/app.py, CreateProject acts as the input data model for project creation endpoints or functions, ensuring incoming data conforms to the expected schema before further processing.

Responsibilities:
- Declare and validate the required fields for a project creation request: title, description, and status.
- Enforce types and any pydantic model configuration provided in model_config for consistent serialization and validation behavior.
- Serve as a typed contract between API input (or internal callers) and downstream logic that creates project records.
- Provide a single, self-documenting representation of the minimal data needed to create a project.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(min_length=1, max_length=120)` |
| `description` (class) | `str` | 🔓 public | Class attribute description<br>**Default:** `Field(default='', max_length=4000)` |
| `status` (class) | `PROJECT_STATUS` | 🔓 public | Class attribute status<br>**Default:** `'planned'` |

---



### UpdateProject

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

UpdateProject represents an operation that updates an existing project record in the local API.

Within services/local_api/app.py, UpdateProject is the specialized subclass used for update operations, building on CreateProject to handle modification semantics and revision checking. It allows the module to handle create and update flows with shared logic while enforcing revision-based safety for updates.

Responsibilities:
- Reuse or extend creation logic from the CreateProject base class to apply changes to an existing project.
- Hold an expected_revision integer that is used to check and enforce the revision state of the project before applying updates.
- Support optimistic concurrency by ensuring updates are only applied when the current project revision matches expected_revision.
- Provide a focused representation of an update operation so calling code can distinguish between create and update workflows.

#### Inheritance

**Inherits from:** `CreateProject`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1)` |

---



### TaskData

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 12](https://img.shields.io/badge/Attributes-12-blue)

#### Description

TaskData is a pydantic data model that represents the core properties of a task in the local API.

Within services/local_api/app.py, TaskData serves as the typed data contract for tasks used by the application logic and API endpoints. It centralizes task field definitions so other components can rely on a consistent, validated representation.

Responsibilities:
- Hold and validate task fields including title, optional project_id and document_id, status and priority enums, and optional due_on and effort values.
- Represent task metadata such as labels, flagged state, reference_url, and notes in a structured form.
- Provide a single-source schema for task payloads exchanged within the local API to ensure consistent typing and serialization.
- Expose model configuration via model_config to control pydantic behaviors for serialization/validation.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(min_length=1, max_length=120)` |
| `project_id` (class) | `str | None` | 🔓 public | Class attribute project_id<br>**Default:** `None` |
| `document_id` (class) | `str | None` | 🔓 public | Class attribute document_id<br>**Default:** `None` |
| `status` (class) | `TASK_STATUS` | 🔓 public | Class attribute status<br>**Default:** `'todo'` |
| `priority` (class) | `PRIORITY` | 🔓 public | Class attribute priority<br>**Default:** `'medium'` |
| `due_on` (class) | `str | None` | 🔓 public | Class attribute due_on<br>**Default:** `None` |
| `effort` (class) | `float | None` | 🔓 public | Class attribute effort<br>**Default:** `Field(default=None, ge=0, le=1000000, allow_inf_nan=False, strict=True)` |
| `labels` (class) | `list[str]` | 🔓 public | Class attribute labels<br>**Default:** `Field(default_factory=list, max_length=20)` |
| `flagged` (class) | `bool` | 🔓 public | Class attribute flagged<br>**Default:** `Field(default=False, strict=True)` |
| `reference_url` (class) | `str` | 🔓 public | Class attribute reference_url<br>**Default:** `Field(default='', max_length=2048)` |
| `notes` (class) | `str` | 🔓 public | Class attribute notes<br>**Default:** `Field(default='', max_length=8000)` |

---



### UpdateTask

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

UpdateTask represents a unit of work that carries updated task information along with a specific expected revision number.

Within services/local_api/app.py, UpdateTask acts as the revision-aware data model for task update operations, fitting into the module alongside other task data types to standardize how update payloads are represented and validated.

Responsibilities:
- Hold task-related data by extending the TaskData base class.
- Include an expected_revision integer that specifies the revision the update expects to apply to.
- Serve as a typed data container for update operations to ensure callers provide revision-aware updates.

#### Inheritance

**Inherits from:** `TaskData`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1)` |

---



### EventData

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 8](https://img.shields.io/badge/Attributes-8-blue)

#### Description

EventData is a Pydantic data model that represents the core properties of a calendar or schedule event, capturing its title, timing, all-day status, timezone, and optional links to related document or task identifiers.

Within services/local_api/app.py, EventData serves as the canonical schema for event-related payloads and is used wherever structured event information must be passed, validated, or serialized across the local API layer.

Responsibilities:
- Define and store the primary event attributes: title, start and end timestamps, all-day flag, and timezone.
- Enforce typing and validation of event fields through Pydantic model behavior (model_config).
- Expose optional associations to external resources via document_id and task_id when an event is linked to a document or task.
- Provide a serializable representation of event data for use by other parts of the module or for API responses.

#### Inheritance

**Inherits from:** `BaseModel`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `model_config` (class) | `Unknown` | 🔓 public | Class attribute model_config<br>**Default:** `ConfigDict(extra='forbid')` |
| `title` (class) | `str` | 🔓 public | Class attribute title<br>**Default:** `Field(min_length=1, max_length=120)` |
| `start_at` (class) | `str` | 🔓 public | Class attribute start_at<br>**Default:** `Field(min_length=10, max_length=40)` |
| `end_at` (class) | `str` | 🔓 public | Class attribute end_at<br>**Default:** `Field(min_length=10, max_length=40)` |
| `all_day` (class) | `bool` | 🔓 public | Class attribute all_day<br>**Default:** `True` |
| `timezone` (class) | `str` | 🔓 public | Class attribute timezone<br>**Default:** `Field(default='Asia/Seoul', min_length=1, max_length=80)` |
| `document_id` (class) | `str | None` | 🔓 public | Class attribute document_id<br>**Default:** `None` |
| `task_id` (class) | `str | None` | 🔓 public | Class attribute task_id<br>**Default:** `None` |

---



### UpdateEvent

![Type: Concrete](https://img.shields.io/badge/Type-Concrete-green) ![Attributes: 1](https://img.shields.io/badge/Attributes-1-blue)

#### Description

UpdateEvent is a specialized event data container used to represent an update operation.

Within the module, UpdateEvent functions as the concrete event representation for update operations, enabling code that dispatches, processes, or validates events to recognize and handle expected revision semantics. As a subclass of EventData, it integrates with the event handling mechanisms in the file while adding update-specific metadata.

Responsibilities:
- Hold update-specific event information by inheriting the common structure provided by EventData.
- Expose an expected_revision integer that communicates which revision the update expects to apply to.
- Serve as a typed payload for consumers that need to validate or coordinate updates against a particular revision.
- Provide a clear data contract for update events so other parts of the module can rely on the presence of the expected_revision field.

#### Inheritance

**Inherits from:** `EventData`

#### Attributes

| Attribute | Type | Visibility | Description |
| --- | --- | --- | --- |
| `expected_revision` (class) | `int` | 🔓 public | Class attribute expected_revision<br>**Default:** `Field(ge=1)` |

---



### clean_text

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def clean_text(value: str, *, name: str = 'Text') -> str:
```

#### Description

Takes a string input and produces a cleaned or normalized version of that text suitable for further processing.

The function accepts an optional name for the text (defaulting to 'Text'), which can be used to identify the value in messages or logs.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `str` | ✅ | — |
| `name` = `'Text'` | `str` | ❌ | — |

#### Returns

**Type:** `str`

—

#### Complexity

Not analyzed

---



### valid_date_optional

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def valid_date_optional(value: str | None) -> str | None:
```

#### Description

Handles an optional date value: the function accepts either a string or None and returns either a string or None.

It is intended to operate on an optional date input and produce an optional string result.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `str | None` | ✅ | — |

#### Returns

**Type:** `str | None`

—

#### Complexity

Not analyzed

---



### validate_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def validate_task(body: TaskData, *, updating: bool = False) -> dict[str, Any]:
```

#### Description

Validate the provided TaskData payload and produce a normalized/annotated dictionary describing validation results and any transformed or required fields.

The function can operate in a creation mode or an update mode (controlled by the updating flag) to apply different validation rules when modifying an existing task.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `TaskData` | ✅ | — |
| `updating` = `False` | `bool` | ❌ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### validate_event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def validate_event(body: EventData) -> dict[str, Any]:
```

#### Description

Validate an EventData payload provided in the body parameter and produce a dictionary describing the validation outcome.

The returned dictionary typically conveys whether the input passed validation and may include cleaned/normalized values or error details.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `EventData` | ✅ | — |

#### Returns

**Type:** `dict[str, Any]`

—

#### Complexity

Not analyzed

---



### verify_range

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def verify_range(start: str, end: str):
```

#### Description

Check whether the provided start and end string values form a valid range.

It validates the relationship and format of the two inputs to determine if they represent an acceptable range.


Returns a boolean indicating whether the start and end values constitute a valid range (True for valid, False for invalid).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `start` | `str` | ✅ | — |
| `end` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### ref_error

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def ref_error(exc: ValueError):
```

#### Description

Handles a ValueError raised within the local API codebase, converting or formatting that exception into an appropriate error representation for the application.

The function acts as the centralized handler for reference-related ValueError exceptions to produce a consistent error response.


Returns a formatted error result representing the provided ValueError (for example an application error payload or HTTP response) suitable for returning from the API handler.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `exc` | `ValueError` | ✅ | — |

#### Complexity

Not analyzed

---



### valid_values

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def valid_values(template: dict[str, Any], title: str, values: dict[str, str]) -> tuple[str, dict[str, str]]:
```

#### Description

Takes a template definition, a title string, and a mapping of string values and produces a pair consisting of a (possibly adjusted) title and a mapping of validated or normalized string values according to the template.

It encapsulates any logic needed to ensure the provided values conform to the expectations expressed by the template and returns the final title and values together.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `template` | `dict[str, Any]` | ✅ | — |
| `title` | `str` | ✅ | — |
| `values` | `dict[str, str]` | ✅ | — |

#### Returns

**Type:** `tuple[str, dict[str, str]]`

—

#### Complexity

Not analyzed

---



### create_app

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_app(db_path: Path | None = None) -> FastAPI:
```

#### Description

Initializes and returns a FastAPI application wired up with the local API endpoints used by the service.

The created app registers routes and handlers for security, health, templates, documents, pages, projects, tasks, calendar/events, UI and static assets, plus utilities for page history, trash, import/export and other workspace management operations.


db_path is an optional Path pointing to the local database/storage to be used by the application; if omitted, a default storage configuration is used.

Returns a configured FastAPI application instance ready to serve the local API.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `db_path` = `None` | `Path | None` | ❌ | — |

#### Returns

**Type:** `FastAPI`

Returns a configured FastAPI application instance ready to serve the local API.

#### Complexity

Not analyzed

---



### local_security

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```python
async def local_security(request: Request, call_next):
```

#### Description

An asynchronous application middleware named local_security that runs for each incoming Request; it can perform per-request security checks or modifications and then delegates processing to the next handler in the chain.

request is the incoming HTTP Request object; call_next is the downstream callable that the middleware should invoke to continue processing and obtain the response.

Returns the Response produced by calling the downstream handler (call_next) after any middleware processing.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `request` | `Request` | ✅ | — |
| `call_next` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### health

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def health():
```

#### Description

This function defines a GET endpoint named 'health' on the app that serves as a health check for the local API.

It is used to verify that the application is running and responsive.


Returns an HTTP response indicating the service health (typically a simple status or HTTP 200 OK payload) to confirm the API is operational.

#### Complexity

Not analyzed

---



### get_templates

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_templates(department: str = '', job_family: str = '', job_role: str = '', section: str = '', q: str = '', collection: str = ''):
```

#### Description

Handles a GET request to retrieve templates, optionally filtering results by department, job family, job role, section, a free‑text query, or a collection.

It exposes those filters as query parameters so callers can narrow the set of returned templates.


Returns the matching templates (typically as a JSON response containing the list of templates and related metadata) based on the provided filter parameters.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `department` = `''` | `str` | ❌ | — |
| `job_family` = `''` | `str` | ❌ | — |
| `job_role` = `''` | `str` | ❌ | — |
| `section` = `''` | `str` | ❌ | — |
| `q` = `''` | `str` | ❌ | — |
| `collection` = `''` | `str` | ❌ | — |

#### Complexity

Not analyzed

---



### get_template_preview

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_template_preview(template_id: str):
```

#### Description

Handle GET requests to produce a preview for a specific template identified by template_id.

It locates the template and returns a preview representation for that template to the caller.


Returns an HTTP response containing a preview representation of the template identified by template_id (e.g., rendered HTML or JSON preview), or an error response if the template cannot be found.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `template_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### catalog_stats

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def catalog_stats():
```

#### Description

HTTP GET endpoint that returns statistics about the service catalog.

It exposes catalog-related metrics or summary information for clients to inspect via a GET request to the application.


Returns an HTTP response (typically JSON) containing the catalog statistics or summary data.

#### Complexity

Not analyzed

---



### get_documents

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_documents(q: str = ''):
```

#### Description

HTTP GET endpoint that retrieves documents matching an optional text query.

It serves requests to fetch document data based on the provided q string parameter.


Returns an HTTP response (typically JSON) containing the matching document records for the given query.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `q` = `''` | `str` | ❌ | — |

#### Complexity

Not analyzed

---



### search_pages

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def search_pages(q: str = Query(default='', max_length=120), tag: str = Query(default='', max_length=32)):
```

#### Description

HTTP GET endpoint that performs a search over pages using an optional free-text query and an optional tag filter.

It exposes two query parameters, q for the search string and tag for narrowing results by tag.


Returns the search results for pages (likely a JSON response containing matching page records or a list of search hits) based on the provided q and tag parameters.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `q` = `Query(default='', max_length=120)` | `str` | ❌ | — |
| `tag` = `Query(default='', max_length=32)` | `str` | ❌ | — |

#### Complexity

Not analyzed

---



### search_workspace

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def search_workspace(q: str = Query(default='', max_length=120), tag: str = Query(default='', max_length=32)):
```

#### Description

Handles GET requests to search the workspace using a textual query and an optional tag filter.

It accepts a query string and an optional tag and performs a search within the application's workspace data to find matching items.


Returns the search results for the provided query and tag, typically serialized as the HTTP response body (e.g., JSON) containing the matching workspace items.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `q` = `Query(default='', max_length=120)` | `str` | ❌ | — |
| `tag` = `Query(default='', max_length=32)` | `str` | ❌ | — |

#### Complexity

Not analyzed

---



### get_page_tags

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_page_tags():
```

#### Description

HTTP GET route handler that returns tag information for a page.

It serves requests to retrieve the tags associated with a page in the local API.


Produces an HTTP response (typically JSON) containing the page's tag data or an appropriate error status if the tags cannot be retrieved.

#### Complexity

Not analyzed

---



### create_document

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_document(body: CreateDoc):
```

#### Description

HTTP POST endpoint that creates a new document using the provided CreateDoc payload.

It accepts a CreateDoc request body and persists or registers a new document accordingly.


Returns an HTTP response containing the created document or a confirmation of creation (e.g., the created document representation or a creation/status response).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `CreateDoc` | ✅ | — |

#### Complexity

Not analyzed

---



### get_document

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_document(document_id: str):
```

#### Description

An HTTP GET handler that retrieves a document identified by the given document_id, intended to be exposed on a Flask app route via the app.get decorator.

It locates the document using the provided identifier and returns the document data to the caller.


Returns the document data (typically as a JSON response) when found, or an appropriate HTTP response (e.g., 404 or error response) if the document cannot be located.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `document_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### update_document

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_document(document_id: str, body: UpdateDoc):
```

#### Description

Handles an HTTP PUT request that updates an existing document identified by document_id using the data provided in the body (UpdateDoc).

It applies the changes to the specified document and exposes this functionality as an endpoint in the application.


Returns an HTTP response indicating the outcome of the update operation—typically a success/failure status and may include the updated document or an error message.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `document_id` | `str` | ✅ | — |
| `body` | `UpdateDoc` | ✅ | — |

#### Complexity

Not analyzed

---



### create_blank_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_blank_page(body: BlankPage):
```

#### Description

HTTP POST endpoint that creates a new blank page resource using the provided BlankPage data.

It accepts the page representation in the request body and persists or registers a new blank page in the application.


body is a BlankPage object supplied in the request body that contains the data required to create the blank page (fields depend on the BlankPage model).

Returns the result of the create operation, typically the created blank page representation or an HTTP response indicating success or failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `BlankPage` | ✅ | — |

#### Complexity

Not analyzed

---



### create_page_from_template

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_page_from_template(body: PageFromTemplate, response: Response):
```

#### Description

Create a new page using the data supplied in a PageFromTemplate payload, handling the incoming POST request and using the Response object to set HTTP response details.

It triggers the server-side logic that instantiates a page based on a specified template and returns the appropriate HTTP response.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `PageFromTemplate` | ✅ | — |
| `response` | `Response` | ✅ | — |

#### Complexity

Not analyzed

---



### import_local_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def import_local_page(body: CanvasImport):
```

#### Description

Handles an HTTP POST request to import a local Canvas page using the provided CanvasImport payload.

It accepts the import data, processes it, and triggers whatever server-side logic is required to create or update the local page resource.


body is a CanvasImport object containing the data for the Canvas page to be imported (e.g., page content, metadata, and any import options).

Returns an HTTP response indicating the result of the import operation, such as success or failure details.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `CanvasImport` | ✅ | — |

#### Complexity

Not analyzed

---



### get_page_canvas

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_page_canvas(page_id: str):
```

#### Description

HTTP GET route handler that retrieves the canvas representation for a specific page identified by page_id.

It is registered with the app.get decorator and serves the page's canvas data when the endpoint is called.


Returns an HTTP response containing the requested page's canvas representation (typically serialized JSON payload with the canvas data for the given page_id).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### update_page_properties

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_page_properties(page_id: str, body: PagePropertiesUpdate):
```

#### Description

Handles HTTP PATCH requests to update the properties of an existing page.

It applies the changes described in the PagePropertiesUpdate body to the page identified by the given page_id.


Returns an HTTP response indicating the result of the update operation, typically including success/failure status and possibly the updated page representation or confirmation of applied changes.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `PagePropertiesUpdate` | ✅ | — |

#### Complexity

Not analyzed

---



### duplicate_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def duplicate_page(page_id: str, body: DuplicatePage, response: Response):
```

#### Description

Create a duplicate of an existing page identified by page_id using the data provided in the body (DuplicatePage).

It is an HTTP POST endpoint that performs the duplication operation and communicates the outcome via the provided Response object.


page_id is the identifier of the page to duplicate; body is a DuplicatePage model containing the duplication request details; response is a Response object used to set the HTTP response (status, headers, body).

The function communicates the result through the Response object (HTTP response); there is no explicit return type annotation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `DuplicatePage` | ✅ | — |
| `response` | `Response` | ✅ | — |

#### Complexity

Not analyzed

---



### restore_page_revision

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_page_revision(page_id: str, revision: int, body: PageRevisionOperation):
```

#### Description

Endpoint that restores a specific revision of a page.

Given a page_id, a revision number, and a PageRevisionOperation payload, it applies the requested restore operation for that page.


Returns an HTTP response representing the result of the restore operation, typically conveying success or failure and potentially including the restored page data or status details.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |
| `body` | `PageRevisionOperation` | ✅ | — |

#### Complexity

Not analyzed

---



### save_page_canvas

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def save_page_canvas(page_id: str, body: CanvasUpdate):
```

#### Description

Handles an HTTP PUT request to save or update the canvas data for a specific page identified by page_id.

It accepts a CanvasUpdate payload and persists the canvas changes for that page.


page_id is the string identifier of the page whose canvas will be updated. body is a CanvasUpdate payload containing the canvas changes or state to be applied to that page.

Returns an HTTP response (or similar result) indicating the outcome of the save operation, such as success or failure.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `CanvasUpdate` | ✅ | — |

#### Complexity

Not analyzed

---



### list_page_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_page_history(page_id: str, before_revision: int | None = Query(default=None, ge=1, le=2 ** 63 - 1)):
```

#### Description

Handle an HTTP GET that returns the history of a page identified by page_id; it optionally restricts results to revisions earlier than a provided before_revision.

This is an endpoint function registered with the app to list past revisions or events for the specified page.


page_id is the identifier of the page whose history is requested. before_revision is an optional filter that, if provided, limits the returned history to revisions with numbers strictly less than the given integer; it must be between 1 and 2^63-1.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `before_revision` = `Query(default=None, ge=1, le=2 ** 63 - 1)` | `int | None` | ❌ | — |

#### Complexity

Not analyzed

---



### get_page_history

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_page_history(page_id: str, revision: int):
```

#### Description

HTTP GET endpoint that retrieves the history for a specific page.

Given a page identifier and a revision number, it returns the stored history or revision information for that page.


Returns the page history or revision data (typically as a JSON response containing one or more revision entries) for the specified page_id and revision.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `revision` | `int` | ✅ | — |

#### Complexity

Not analyzed

---



### page_tree

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def page_tree():
```

#### Description

HTTP GET route handler (registered with app.get) that serves the application's page tree.

It provides the structured representation of pages for the application, typically used by clients to discover or display site/navigation structure.


Returns a representation of the application's page tree (typically a JSON-compatible structure describing pages and their hierarchy).

#### Complexity

Not analyzed

---



### list_page_trash

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_page_trash():
```

#### Description

HTTP GET endpoint that returns a listing of pages that are in the application's trash.

It's the handler for retrieving trashed pages so clients can view them.


Returns an HTTP response (typically JSON) containing the collection or list of trashed pages for the application.

#### Complexity

Not analyzed

---



### trash_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def trash_page(page_id: str, body: PageRevisionOperation):
```

#### Description

Defines an HTTP POST endpoint that marks a page identified by page_id as trashed.

It accepts a PageRevisionOperation payload to specify the revision-related details of the trash operation and performs the server-side logic to apply that operation to the page.


Returns an HTTP response indicating the outcome of the trash operation, typically including success or error information and any updated page/revision metadata.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `PageRevisionOperation` | ✅ | — |

#### Complexity

Not analyzed

---



### restore_trashed_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def restore_trashed_page(page_id: str, body: PageRevisionOperation):
```

#### Description

HTTP POST endpoint that restores a previously trashed page identified by page_id, using details provided in the PageRevisionOperation body.

It triggers the restoration of the page revision specified in the request so the page is recovered from the trash.


Returns an HTTP response indicating the result of the restore operation (e.g., success or failure and any relevant metadata about the restored page).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `PageRevisionOperation` | ✅ | — |

#### Complexity

Not analyzed

---



### move_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def move_page(page_id: str, body: MovePage):
```

#### Description

Handles an HTTP PUT request to move a page identified by page_id using the information provided in the MovePage request body.

It updates the page's location or ordering according to the supplied move details.


Returns the result of the move operation, typically an HTTP response indicating success or failure and any updated page information.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page_id` | `str` | ✅ | — |
| `body` | `MovePage` | ✅ | — |

#### Complexity

Not analyzed

---



### list_projects

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_projects():
```

#### Description

An HTTP GET endpoint that returns a list of projects.

It is registered with the app.get decorator and exposes project listing functionality from the create_app module.


Returns an HTTP response containing a list of projects (likely serialized as JSON).

#### Complexity

Not analyzed

---



### create_project

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_project(body: CreateProject):
```

#### Description

Handle POST requests to create a new project using the provided CreateProject payload.

This function registers a new project resource based on the data in the body parameter.


Returns an HTTP response exposing the result of the creation operation (typically the created project's representation and/or an appropriate status code).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `CreateProject` | ✅ | — |

#### Complexity

Not analyzed

---



### update_project

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_project(project_id: str, body: UpdateProject):
```

#### Description

HTTP PUT handler that updates an existing project identified by project_id using the data provided in the UpdateProject request body.

It applies the changes from the body to the specified project and persists the updated state.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `str` | ✅ | — |
| `body` | `UpdateProject` | ✅ | — |

#### Complexity

Not analyzed

---



### list_tasks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_tasks(project_id: str = ''):
```

#### Description

HTTP GET endpoint handler that lists tasks, optionally scoped to a specific project.

It serves as the route implementation for retrieving task records associated with the provided project identifier or all tasks when no project_id is given.


project_id is an optional string used to filter the returned tasks to those belonging to the named project; if left empty it returns tasks across projects.

Returns an HTTP response (typically JSON) containing the list of matching task objects.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` = `''` | `str` | ❌ | — |

#### Complexity

Not analyzed

---



### create_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_task(body: TaskData):
```

#### Description

This function is an HTTP POST endpoint that accepts task data and creates a new task in the application.

It handles incoming TaskData payloads and initiates whatever creation logic the service provides for tasks.


Returns an HTTP response containing the created task representation or an appropriate status/result of the creation operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `TaskData` | ✅ | — |

#### Complexity

Not analyzed

---



### get_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_task(task_id: str):
```

#### Description

Handle a GET request that retrieves a task identified by the given task_id.

It serves as an endpoint to look up and return the task corresponding to the provided identifier.


Returns the task representation or response corresponding to the requested task_id (e.g., task data or an HTTP error response if not found).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `task_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### update_task

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_task(task_id: str, body: UpdateTask):
```

#### Description

Handles an HTTP PUT endpoint that updates an existing task identified by task_id using the provided UpdateTask body.

It applies the incoming changes to the specified task and returns the result of that update.


Returns an HTTP response indicating the outcome of the update operation, typically including either the updated task representation or a status/error message.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `task_id` | `str` | ✅ | — |
| `body` | `UpdateTask` | ✅ | — |

#### Complexity

Not analyzed

---



### calendar_feed

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def calendar_feed(start: str, end: str):
```

#### Description

HTTP GET endpoint that produces a calendar feed for a specified time range.

It accepts a start and end boundary and returns the calendar data covering that interval.


Returns an HTTP response containing the calendar feed corresponding to the provided start and end range.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `start` | `str` | ✅ | — |
| `end` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### list_calendar_events

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def list_calendar_events(start: str, end: str):
```

#### Description

Handles an HTTP GET request to list calendar events that fall between the given start and end timestamps.

It returns the events for the requested date/time range.


Returns the calendar events occurring between start and end (likely as a JSON-serializable list or collection of event objects).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `start` | `str` | ✅ | — |
| `end` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### create_event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_event(body: EventData):
```

#### Description

Registers a new event using data provided in the request body and exposes this functionality as an HTTP POST endpoint.

It accepts an EventData payload and processes it to create the corresponding event in the application.


body is an EventData object representing the event payload (fields such as title, time, metadata, etc.) sent by the client to create the event.

Returns an HTTP response (typically a success status and possibly the created event representation or an identifier) indicating the result of the create operation.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `EventData` | ✅ | — |

#### Complexity

Not analyzed

---



### get_calendar_event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def get_calendar_event(event_id: str):
```

#### Description

HTTP GET handler that retrieves a calendar event identified by the given event_id.

It is registered on the app with the app.get decorator and is intended to return the data for a single calendar event corresponding to that identifier.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `event_id` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



### update_event

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def update_event(event_id: str, body: UpdateEvent):
```

#### Description

Handle an HTTP PUT request to update an existing event identified by event_id using the data provided in the body.

It applies the changes from the UpdateEvent payload to the specified event resource.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `event_id` | `str` | ✅ | — |
| `body` | `UpdateEvent` | ✅ | — |

#### Complexity

Not analyzed

---



### ui

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def ui():
```

#### Description

Handle HTTP GET requests for the application's user interface endpoint and return the UI content to the client.

It is a route handler registered with the app.get decorator, intended to serve the frontend UI (typically HTML/JS) for the local API service.


Returns an HTTP response containing the UI content (for example HTML and related assets) to be rendered by the client's browser.

#### Complexity

Not analyzed

---



### assets

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def assets(filename: str):
```

#### Description

HTTP GET route handler that serves a named asset from the application when a client requests it.

It locates the resource identified by the filename parameter and returns it to the requester.


Returns an HTTP response containing the requested asset (e.g., a file or static resource) or an appropriate error response if the asset cannot be found or served.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `filename` | `str` | ✅ | — |

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

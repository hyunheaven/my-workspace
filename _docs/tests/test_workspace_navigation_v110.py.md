<!-- METADATA: {"source_path": "tests/test_workspace_navigation_v110.py", "source_sha": "788f00e586c47a1aab006993454734a61bd54004", "extraction_quality": "full_ast", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:21:27Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "tests/test_workspace_navigation_v110.py",
  "source_hash": "2a38c9f23e36c10b4182f3a84898a4310415845bb056bd35cdc501de19ff4f05",
  "last_updated": "2026-11-18T03:21:12.258590+00:00",
  "git_sha": "788f00e586c47a1aab006993454734a61bd54004",
  "tokens_used": 3489,
  "complexity_score": 1,
  "estimated_review_time_minutes": 5,
  "external_dependencies": [
    "uuid",
    "fastapi.testclient",
    "pytest",
    "services.local_api.app"
  ]
}
```

</details>

[Documentation Home](../README.md) > [tests](./README.md) > **test_workspace_navigation_v110**

---

# test_workspace_navigation_v110.py

> **File:** `tests/test_workspace_navigation_v110.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 5min](https://img.shields.io/badge/Review_Time-5min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This test module contains integration tests that verify workspace navigation behavior around trashing and restoring items and how those operations interact with search, page identifiers, and template tag defaults. It defines a workspace fixture used to create a testing client against a local API application and includes tests that exercise subtree trash behavior (ensuring trashed content is hidden from search and that stale writes are rejected) and template/tag interactions (ensuring default tag settings are independent while tasks share search visibility). The module also provides a constant HEADERS used for making requests as a particular local-template-editor client.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `uuid` | from uuid import uuid4 |
| `fastapi.testclient` | from fastapi.testclient import TestClient |
| `pytest` | import pytest |
| `services.local_api.app` | from services.local_api.app import create_app |

## 📁 Directory

This file is part of the **tests** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- uses FastAPI TestClient for integration testing of the API
- uses pytest for test definitions and fixtures
- organizes tests around workspace operations: trash/restore, search visibility, and template/tag behavior

## Maintenance Notes

- Provide a workspace fixture to set up a TestClient against the local API application for use in tests.
- Test that trashing a subtree hides its pages from search results and that subsequent stale write attempts are rejected.
- Verify that template tag default settings are independent across templates while tasks created from those templates share search behavior.
- Supply a consistent request header (HEADERS) to identify the test client in API requests.


---

## Constants

| Name | Type | Value |
| --- | --- | --- |
| `HEADERS` | — | `{'X-EAW-Request': 'local-template-editor'}` |



---

## Functions and Classes


### workspace

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def workspace(tmp_path):
```

#### Description

A pytest fixture that prepares and yields a temporary workspace for tests related to workspace navigation.

It uses the provided temporary path to create and configure whatever files or directories the tests need to interact with.


Returns the prepared temporary workspace (typically a pathlib.Path or an object representing the workspace) that test functions can use to perform filesystem/navigation assertions.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmp_path` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### test_subtree_trash_hides_search_and_rejects_stale_write

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_subtree_trash_hides_search_and_rejects_stale_write(workspace):
```

#### Description

This test verifies that when a subtree within the workspace is moved to the trash, it is excluded from search results and any attempted writes based on stale state are rejected.

It exercises navigation and mutation of a subtree (using the nested helpers blank, page_path, and change_trash) and asserts correct hiding and conflict behavior after trashing.


workspace is a test fixture providing an isolated workspace instance used to create, search, and modify pages; it supplies the context for performing the trashing and subsequent operations.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `workspace` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### blank

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def blank(title, parent_id=None):
```

#### Description

Create a blank test item identified by a title, optionally placing it under an existing parent.

This helper is intended for use in workspace navigation tests to produce a minimal or placeholder node for further operations.


title is the display name or identifier for the blank item; parent_id, if provided, is the identifier of an existing parent under which the blank item will be placed.

Returns the created blank test item (for example an object or identifier representing the new node) so the caller can reference it in subsequent test actions.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | `Unknown` | ✅ | — |
| `parent_id` = `None` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### page_path

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def page_path(page):
```

#### Description

Compute or retrieve the filesystem or URL-style path for the given page object.

This helper is used in tests to obtain a canonical path representation for a page within the workspace navigation test suite.


Returns the path of the provided page (likely as a string) representing its location in the workspace or site hierarchy.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### change_trash

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def change_trash(page, action, revision=None):
```

#### Description

Perform a change to the trash state of a workspace subtree within a test scenario.

It drives a page interaction to apply the specified trash-related action (e.g., move to trash or restore) and optionally targets a specific revision when making that change.


page is the test page or browser context used to exercise the UI; action specifies the trash operation to perform (such as trash or restore); revision, if provided, indicates the revision to apply the action against or to assert when performing the change.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `action` | `Unknown` | ✅ | — |
| `revision` = `None` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### test_template_tag_defaults_are_independent_and_tasks_share_search

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def test_template_tag_defaults_are_independent_and_tasks_share_search(workspace):
```

#### Description

This test verifies that template tag default values are independent between different templates and that task pages created from those templates share the same search behavior.

It exercises creating template pages (via a nested helper create_template_page), applying defaults and creating tasks, and then checks that defaults do not leak between templates while tasks reflect the shared search context.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `workspace` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### create_template_page

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```python
def create_template_page():
```

#### Description

Creates a template page used in the workspace navigation v110 test suite.

It sets up the necessary page object/state that tests about template tag defaults and task search behavior rely on.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

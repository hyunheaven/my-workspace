<details><summary>Directory Metadata (for smart change detection)</summary>

```json
{
  "doc_type": "directory_index",
  "directory_path": "_docs/services/local_api",
  "directory_hash": "af3af30707db1fed3a49300f1a476e2a5c918cf131650cbb1a8132d5d7970b27",
  "file_count": 5,
  "file_hashes": {
    "app.py": "76d455c756f76325",
    "custom_databases.py": "a59958bd37b670d5",
    "page_database_views.py": "549fb3177e19c717",
    "run.py": "de0bb0152ce18cae",
    "workspace_store.py": "ed770631d904b0a6"
  }
}
```

</details>

[Documentation Home](../../README.md) > [services](../README.md) > [local_api](./README.md) > **local_api**

---

# 📁 local_api

> **Purpose:** Provide a local-only template editor API and supporting local-first persistence layers for pages, databases, and workspace storage used by the application.
> 

![Organization: Feature Based](https://img.shields.io/badge/Organization-Feature_Based-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [All Files](#all-files)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)

---

## Overview

This directory contains the implementation of a local-only template editor API and several supporting local-first persistence components. At the root level, app.py implements the FastAPI-based local API and Pydantic models for documents, pages, canvas content, projects, tasks, and events; custom_databases.py implements a local, user-configurable database layer with properties, views, records and revision history; page_database_views.py contains the components needed to persistently associate personal pages with views stored in a local SQLite database; workspace_store.py implements a local-first workspace storage component for structured data; and run.py provides a small runtime entry point that launches the local application on the loopback interface. These files together provide the API surface, data models, storage backends, and a simple launcher for local development and single-machine usage.

In addition to the documented root files, other artifacts are present in the directory (for example __init__.py, catalog.json, catalog_library.json, page_templates.py, storage.py). These are not described in detail here but are part of the package surface. Conceptually, the directory groups API logic, persistent storage adapters (including a SQLite-backed view association component), and a runtime launcher so that the local editor can operate without external services. The components are designed to work together: app.py exposes the editing and document models, the database modules provide persistence and revision history for customizable data, page_database_views.py binds pages to persisted views, and workspace_store.py provides a local-first structured data store. run.py is the simple entry point used to start the local application on loopback during development or local runs.


### File Organization

Files are organized by feature area: API surface and models (app.py), database/persistence layers (custom_databases.py, page_database_views.py, workspace_store.py), and a small runtime entry (run.py). This keeps API, storage, and launch responsibilities separated so contributors can focus on one concern at a time.

## 📂 All Files

| File | Type |
| --- | --- |
| [app.py](./app.py.md) | 🐍 Python |
| [custom_databases.py](./custom_databases.py.md) | 🐍 Python |
| [page_database_views.py](./page_database_views.py.md) | 🐍 Python |
| [run.py](./run.py.md) | 🐍 Python |
| [workspace_store.py](./workspace_store.py.md) | 🐍 Python |

## Dependencies

### External Dependencies

| Dependency | Usage |
| --- | --- |
| `FastAPI` | Used by app.py to implement the local-only API endpoints and request/response handling. |
| `Pydantic` | Used by app.py for data models representing documents, pages, canvas content, projects, tasks and events. |
| `SQLite (sqlite3)` | Used by page_database_views.py to persistently associate pages with views; provides the local DB backend. |

### Internal Dependencies

| Dependency | Usage |
| --- | --- |
| [Other modules in this directory (e.g., storage.py, page_templates.py)](../Other modules in this directory (e/g/, storage/py, page_templates/py).md) | Supplementary local storage and templates referenced by the API and persistence layers (files present in the directory but not documented in detail here). |

## Architecture Notes

- The directory follows a local-first design: API, database layers, and workspace storage are implemented to operate without external services, enabling offline or single-machine usage.
- Persistence responsibilities are separated: custom_databases.py handles configurable databases and revision history, page_database_views.py handles SQLite-backed page-to-view associations, and workspace_store.py provides structured workspace storage.
- A minimal runtime entry (run.py) is included to keep the development run loop simple and focused on the loopback interface.

---

## Navigation

**↑ Parent Directory:** [Go up](../README.md)

---

*Generated by Woden Docbot*
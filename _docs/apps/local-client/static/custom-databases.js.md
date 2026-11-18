<!-- METADATA: {"source_path": "apps/local-client/static/custom-databases.js", "source_sha": "f4e385cde6f0947ffb678fb489cf7e16c8f9ce7a", "extraction_quality": "structural", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:20:15Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "apps/local-client/static/custom-databases.js",
  "source_hash": "91e4233f33beb303d07b13217bc66fe502e675aceb3856ed894ed6422d66ac4c",
  "last_updated": "2026-11-18T03:19:24.084020+00:00",
  "git_sha": "f4e385cde6f0947ffb678fb489cf7e16c8f9ce7a",
  "tokens_used": 26744,
  "complexity_score": 8,
  "estimated_review_time_minutes": 43,
  "external_dependencies": []
}
```

</details>

[Documentation Home](../../../README.md) > [apps](../../README.md) > [local-client](../README.md) > [static](./README.md) > **custom-databases**

---

# custom-databases.js

> **File:** `apps/local-client/static/custom-databases.js`

![Complexity: High](https://img.shields.io/badge/Complexity-High-red) ![Review Time: 43min](https://img.shields.io/badge/Review_Time-43min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This JavaScript module implements the client-side logic for interacting with custom databases in the application. It provides a large set of helper functions named with the cdb prefix to build and manage database UI elements (buttons, labels, selects, inputs, areas, option rows), to read and write field values, and to compute display and writable state for fields. The module also includes functions for view and record management such as painting views, switching the active view, showing databases, opening databases, and loading or refreshing custom database data from the server.

## Dependencies

No dependencies identified.

## 📁 Directory

This file is part of the **static** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Consistent use of a cdb prefix for related functions providing thematic grouping
- A mix of synchronous helpers and asynchronous operations (several functions declared async for server interaction)
- Separation of concerns between UI element creation, field/value management, and higher-level database/view lifecycle operations

## Maintenance Notes

- Provide UI element factory functions and helpers for custom database fields and controls (cdbButton, cdbLabel, cdbSelect, cdbInput, cdbArea, cdbOptionRows).
- Manage field metadata and values through helpers (cdbField, cdbType, cdbValue, cdbIsComputed, cdbWritable, cdbDisplayValue).
- Handle lifecycle and navigation for custom databases, including loading, refreshing, opening, and showing databases (loadCustomDatabases, refreshCustomDatabase, openCustomDatabase, cdbShowDatabase).
- Support view rendering and interactions, including painting views, switching active views, and managing relations (cdbPaint, cdbActiveView, cdbRelations).
- Provide history and dialog functionality for records and databases (cdbRecordHistoryRows, cdbViewHistoryRows, cdbHistoryChanges, cdbHistoryDialog, cdbDatabaseDialog).


---

## Functions and Classes


### cdbMonthStart

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbMonthStart(date):
```

#### Description

Compute the start of the month for a given date.

The function takes an input date and returns a date representing the beginning of that month.


Returns a Date representing the first day of the month for the supplied date (typically set to the start of that day).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `date` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbDate

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbDate(value):
```

#### Description

Parse or convert the provided value into a date representation used by the custom-databases client.

The function takes a single input and produces a date-related value suitable for use in the app's UI or data layer.


value is the input to be interpreted as a date (e.g., a string, number, or Date) that the function will parse or convert; the exact accepted input formats depend on the function's implementation.

A date representation (such as a JavaScript Date or formatted date value) appropriate for the application's usage.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbRead

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbRead(id):
```

#### Description

Read and return the custom database entry identified by the given id.

The function performs a lookup using the provided id and retrieves the corresponding data from the local custom-databases store.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbWrite

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbWrite(path, method, body):
```

#### Description

Sends a request to perform a write operation on a custom database resource identified by path using the specified HTTP method and request body.

It acts as a helper to issue create/update/delete style operations against the database endpoint.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | `Unknown` | ✅ | — |
| `method` | `Unknown` | ✅ | — |
| `body` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbButton

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbButton(text, action, attributes={}):
```

#### Description

Creates or configures a clickable UI button using the provided label text, attaches the given action to its activation, and applies any optional attributes to the element.

It encapsulates the common pattern of making a button with text, behavior, and HTML attributes in one call.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `text` | `Unknown` | ✅ | — |
| `action` | `Unknown` | ✅ | — |
| `attributes` = `{}` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbLabel

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbLabel(label, control):
```

#### Description

Creates and/or configures a label element associated with a given control.

The function pairs the provided label text or descriptor with the given control so they behave as a labeled UI element.


Returns the created or updated label element (a DOM node) that is associated with the control so it can be inserted into the document or further manipulated.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `label` | `Unknown` | ✅ | — |
| `control` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbSelect

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbSelect(options, value='', placeholder='선택 없음', attributes={}):
```

#### Description

Constructs or configures a selectable control (a dropdown/select) using the provided options, applies a selected value if given, and uses a placeholder label when no value is chosen.

It also accepts an attributes object to add or override HTML/behavioral attributes on the resulting control.


The placeholder parameter defaults to the Korean string '선택 없음' (meaning 'no selection') and will be shown when no value is selected. The attributes parameter is an object of additional attributes to apply to the created control (e.g., classes, data-attributes, or other HTML attributes).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `options` | `Unknown` | ✅ | — |
| `value` = `''` | `Unknown` | ❌ | — |
| `placeholder` = `'선택 없음'` | `Unknown` | ❌ | — |
| `attributes` = `{}` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbInput

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbInput(value='', attributes={}):
```

#### Description

cdbInput is a function that accepts an initial value and an attributes object, intended to produce an input-like result configured by those arguments.

It encapsulates creation or configuration of an input representation using the provided value and attributes.


Returns a result produced by the function implementation (e.g., an input element, HTML string, or configuration object); the exact return type is not specified in the extracted signature.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` = `''` | `Unknown` | ❌ | — |
| `attributes` = `{}` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbArea

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbArea(value='', attributes={}):
```

#### Description

Creates or constructs a 'cdbArea' component using an optional initial value and a set of attributes.

It is intended to produce a configurable area (likely for use in a custom database UI) initialized with the provided value and modified by the attributes object.


Returns a representation of the constructed cdbArea (for example an HTML/DOM node or an HTML string) corresponding to the provided value and attributes.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` = `''` | `Unknown` | ❌ | — |
| `attributes` = `{}` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbOptionRows

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbOptionRows(items):
```

#### Description

Generate a collection of option rows for the custom databases UI by converting the provided items into the appropriate row representations.

It prepares the data needed to render selectable/options entries in the interface.


items is a collection (e.g., an array) of entries that will be transformed into option rows; each element represents one row to be produced.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `items` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbIsComputed

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbIsComputed(property):
```

#### Description

Determines whether the given property represents a computed property.

It inspects the provided property descriptor/value and returns true when it is considered computed and false otherwise.


Returns a boolean: true if the supplied property is a computed property, false if it is not.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `property` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbField

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbField(database, id):
```

#### Description

Locate or build a field representation for a custom database entry identified by id within the provided database.

The function operates on the given database and id to produce the corresponding field object or descriptor.


Returns a field object or descriptor corresponding to the given id from the provided database (e.g., metadata or structure describing that field).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbType

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbType(database, id):
```

#### Description

Determine and return the type of an entry identified by id within the given custom database.

The function looks up the item in the provided database and produces its type representation.


Returns the type of the specified database entry (for example a string or identifier representing the entry's type).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbValue

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbValue(record, id):
```

#### Description

Retrieve or compute a value from a provided record using the given id, typically used to obtain a field or cell value for a custom database entry.

Returns the value associated with the supplied id from the record; the exact type depends on the stored data (e.g., string, number, object).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `record` | `Unknown` | ✅ | — |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbWritable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbWritable(database, values):
```

#### Description

Checks or updates the writable state for a custom database using the provided database descriptor and associated values; it determines whether the given database should be considered writable based on those inputs.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `values` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbDisplayValue

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbDisplayValue(property, value, relations):
```

#### Description

Formats and returns a user-facing representation of a database property value.

It uses the provided property metadata and any relation mappings to produce an appropriate display string or node for the value.


property is the metadata/descriptor for the field being displayed; value is the raw stored value for that property; relations is a lookup or mapping of related records used to resolve foreign-key or relation-type properties into human-readable labels.

Returns a formatted display value (typically a string or HTML-safe representation) appropriate for rendering in the UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `property` | `Unknown` | ✅ | — |
| `value` | `Unknown` | ✅ | — |
| `relations` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### getActiveCustomDatabase

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def getActiveCustomDatabase():
```

#### Description

Retrieve the currently selected custom database for the local client.

It looks up and returns whichever custom database is marked as active in the application's custom-database state.


The active custom database object (or null/undefined if no custom database is currently active).

#### Complexity

Not analyzed

---



### loadCustomDatabases

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def loadCustomDatabases():
```

#### Description

Asynchronously loads custom databases for the application, performing any necessary initialization or fetching of database definitions so they become available to the client code.

It encapsulates the async workflow required to retrieve and register those custom databases.

#### Complexity

Not analyzed

---



### refreshCustomDatabase

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def refreshCustomDatabase():
```

#### Description

Asynchronously refreshes the custom database used by the local client.

The function initiates whatever update or reload logic is implemented in apps/local-client/static/custom-databases.js to bring the custom database state up to date.

#### Complexity

Not analyzed

---



### cdbShowDatabase

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def cdbShowDatabase(id):
```

#### Description

Asynchronously show or display the database identified by the given id, performing whatever client-side actions are needed to present that database's details or view in the local client UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### openCustomDatabase

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def openCustomDatabase(databaseId, recordId):
```

#### Description

Asynchronously opens a custom database identified by databaseId and (optionally) focuses or loads a specific record identified by recordId.

It initiates whatever client-side actions are required to access or display the requested database and record.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `databaseId` | `Unknown` | ✅ | — |
| `recordId` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbActiveView

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbActiveView(database):
```

#### Description

Determine and return the currently active view for the supplied database.

The function selects or computes which view within the given database should be considered active based on the database argument.


Returns the active view for the provided database (typically a view identifier or view object representing the currently selected view).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbRelations

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def cdbRelations(database):
```

#### Description

Asynchronously performs operations related to database relations for the provided database.

The function likely queries, loads, or updates relation information associated with the specified database.


Returns a Promise that resolves when the asynchronous relation operation completes.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbPaint

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def cdbPaint(database, generation):
```

#### Description

Asynchronously updates or renders the UI/state for a custom database view identified by the provided database and generation.

It performs whatever painting or refresh steps are required to reflect the given generation of the database in the client.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `generation` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbModal

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbModal(title, submit, body, extra, showHistory):
```

#### Description

Creates and displays a modal dialog in the application using the provided title, submit button label/handler, main body content, and optional extra content.

It can also optionally show a history section when requested via the showHistory parameter.


title sets the modal header, submit supplies the submit action or label, body is the primary content of the modal, extra is for any additional content or controls to include, and showHistory is a boolean that toggles whether a history section is shown.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | `Unknown` | ✅ | — |
| `submit` | `Unknown` | ✅ | — |
| `body` | `Unknown` | ✅ | — |
| `extra` | `Unknown` | ✅ | — |
| `showHistory` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbRecordHistoryRows

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbRecordHistoryRows(database, snapshot, relations):
```

#### Description

Generate the data rows that represent the change history for a record in a given database using a provided snapshot and relation metadata.

The function collects and formats history entries so they can be displayed or processed elsewhere in the client.


Returns an array of row objects (history entries) derived from the snapshot and relations, suitable for rendering or further processing.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `snapshot` | `Unknown` | ✅ | — |
| `relations` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbViewHistoryRows

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbViewHistoryRows(database, snapshot):
```

#### Description

Show or retrieve the history rows for a given local client database at a particular snapshot.

The function operates on the provided database object and snapshot identifier to produce a view of the historical rows associated with that snapshot.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `snapshot` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbHistoryChanges

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbHistoryChanges(preview, entries, savedEntries):
```

#### Description

Compares a current set of database entries to a saved set and produces or displays the detected history changes; when preview is enabled, it runs in a non-destructive preview mode rather than applying changes.

It is intended to determine what has changed between entries and savedEntries and present those differences for review or further processing.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `preview` | `Unknown` | ✅ | — |
| `entries` | `Unknown` | ✅ | — |
| `savedEntries` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbHistoryDialog

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbHistoryDialog(trigger, {path,kind,expectedRevision,rows,current}):
```

#### Description

Open and manage a change-history dialog for a custom database entry identified by path/kind.

It uses embedded helper functions (load and select) to fetch and display historical rows, and to handle the user selecting a specific revision or row for further actions.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `trigger` | `Unknown` | ✅ | — |
| `{path,kind,expectedRevision,rows,current}` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### load

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def load(before):
```

#### Description

Asynchronously performs a load operation, fetching or initializing data when called.

The function is intended to run asynchronous work (such as retrieving records or resources) possibly constrained by an optional cutoff or pagination marker.


before: an optional parameter (likely a cutoff, cursor, or timestamp) used to limit which items are loaded (for example, to load items occurring before a given value).

Being async, it returns a Promise that resolves when the load operation completes (typically resolving with the loaded data or completion status).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `before` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### select

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def select(item):
```

#### Description

Handles selecting the provided item — e.g., update internal/visual selection state or trigger related selection behavior when a specific item is chosen.

Does not return a value (void); its effect is side-effects such as updating state or UI rather than producing a return value.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `item` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbDatabaseDialog

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbDatabaseDialog(database):
```

#### Description

Creates and/or displays a dialog for interacting with a database identified by the given argument.

The function is intended to build or open a UI dialog related to the provided database object or identifier so the user can view or edit database-related settings.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbPropertyList

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbPropertyList(database):
```

#### Description

Produce and return a list of properties associated with the supplied database.

The function takes a database identifier/object and constructs the corresponding property list for that database.


Returns the list of properties for the provided database.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbPropertyDialog

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def cdbPropertyDialog(database, property):
```

#### Description

Opens and handles a property editing dialog for a custom database entry.

The async function prepares dialog content (using nested helpers readConfig and options), displays UI for viewing or editing the specified property on the given database, and awaits the user's interaction before resolving.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `property` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### readConfig

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def readConfig():
```

#### Description

Reads and returns the current configuration used by the custom-databases module in the local client.

It retrieves the stored configuration for use by other code in apps/local-client/static/custom-databases.js.


Returns the configuration object containing the parsed settings used by the custom-databases code.

#### Complexity

Not analyzed

---



### options

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def options():
```

#### Description

Asynchronously prepares and/or builds the configuration options used by the local-client custom databases UI.

It encapsulates helper subroutines (add and targetOptions) to assemble individual option entries and target-specific option sets before returning or applying the composed options.

#### Complexity

Not analyzed

---



### add

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def add(label, input):
```

#### Description

Adds a new item to the custom databases configuration using the provided label and input.

The function creates or registers an entry identified by the label and populated with the supplied input value.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `label` | `Unknown` | ✅ | — |
| `input` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### targetOptions

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def targetOptions():
```

#### Description

Asynchronously gathers and returns selectable options for a target selection UI or operation.

The function likely fetches or computes available target choices to be used elsewhere in the application, such as populating a dropdown or configuring a target for an action.

#### Complexity

Not analyzed

---



### cdbRecordDialog

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def cdbRecordDialog(database, record):
```

#### Description

Opens and manages an asynchronous dialog related to a custom database record.

It takes a database identifier/object and a specific record and performs the UI and logic needed to display, edit, or interact with that record in a dialog context.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `record` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbValueField

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbValueField(type, value, options):
```

#### Description

Creates or constructs a value field using the provided type, value, and options.

It uses the type to determine how the value should be represented and applies any supplied options to control the field's behavior or appearance.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `Unknown` | ✅ | — |
| `value` | `Unknown` | ✅ | — |
| `options` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbViewDialog

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbViewDialog(database, view):
```

#### Description

Opens and manages a dialog interface for inspecting a specific view within a custom database.

It provides interactive filter handling and UI adjustments via nested helper functions (filterable, adjust, readFilter, changeFilter).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `view` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### filterable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def filterable([id]):
```

#### Description

Initializes or configures a filterable component or behavior for a UI element identified by the optional id argument.

It applies filtering logic or enables filter-related interactions on the target element so it can be used to narrow visible items or data.


id is an optional identifier for the element to make filterable; if omitted the function will operate on a default target (e.g., a predefined element or collection).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `[id]` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### adjust

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def adjust():
```

#### Description

Performs adjustments related to the local client's custom-databases module.

The function name suggests it updates or reconfigures state or presentation for custom databases, but exact behavior is not specified in the extracted data.

#### Complexity

Not analyzed

---



### readFilter

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def readFilter():
```

#### Description

Reads the current filter settings (for example from the UI or internal state) and provides them for use by other code.

The function encapsulates the logic to collect the active filter criteria.


Returns an object (or value) representing the current filter configuration or criteria.

#### Complexity

Not analyzed

---



### changeFilter

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def changeFilter(useExisting=false):
```

#### Description

Updates or switches the active filter used by the client.

When called with useExisting set to true, it will prefer or reuse an existing filter instead of creating or applying a new one.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `useExisting` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbCompare

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbCompare(left, right):
```

#### Description

Compare two values (left and right) to determine their relative ordering, typically used for sorting or equality checks.

A numeric comparison result indicating order: negative if left is less than right, zero if they are equal, and positive if left is greater than right.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `left` | `Unknown` | ✅ | — |
| `right` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbRecords

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbRecords(database, view):
```

#### Description

Provides access to or manipulates records for a given custom database and its view; it is the function that operates on the specified database and view combination in the custom-databases client code.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `view` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbRecordButton

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbRecordButton(record, openRecord, className='secondary-button'):
```

#### Description

Creates a record-related button UI element that is associated with the given record and will invoke the provided openRecord handler when activated.

The function allows specifying a CSS class for the button, defaulting to 'secondary-button'.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `record` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `className` = `'secondary-button'` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbTable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbTable(root, database, records, relations, openRecord):
```

#### Description

Initializes and renders a table view for a custom database into the provided root element using the given database schema, records, and relations.

It wires up interactions so that invoking or selecting a record uses the provided openRecord callback.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `records` | `Unknown` | ✅ | — |
| `relations` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbCard

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbCard(database, record, relations, openRecord, kind):
```

#### Description

Creates or produces a card representation for a specific record in a custom database context.

It takes the database definition, a single record, any related records, a callback to open the record, and a kind to determine how the card should be rendered or behaved.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `database` | `Unknown` | ✅ | — |
| `record` | `Unknown` | ✅ | — |
| `relations` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `kind` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbMarkDraggable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbMarkDraggable(button, database, record):
```

#### Description

Marks a UI element (the provided button) as draggable in the context of a specific custom database and record.

It configures or annotates the button so it can be used for drag-and-drop operations tied to the given database record.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `button` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `record` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbDrop

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbDrop(target, database, property, value):
```

#### Description

Performs a drop operation on a custom database context identified by the provided target and database names, using the given property and value to identify what to drop.

It is intended to remove or clear an entry or association matching the property/value pair within the specified database context.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `property` | `Unknown` | ✅ | — |
| `value` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbBoard

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbBoard(root, database, view, records, relations, openRecord, editable):
```

#### Description

Create and initialize a kanban-style board view for a custom database using the given root element and data.

It uses the provided database, view configuration, records, and relations to render columns and cards and supports opening records and editability based on callbacks/flags.


openRecord is a callback used to open or focus a single record when a card is activated; editable is a boolean flag that enables or disables in-place editing or drag-and-drop reordering of cards. The records and relations parameters supply the board with the items and their relational grouping needed to populate columns.

Returns the constructed board UI component (e.g., a DOM element or framework component) that has been attached to the provided root.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `view` | `Unknown` | ✅ | — |
| `records` | `Unknown` | ✅ | — |
| `relations` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `editable` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbPeriod

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbPeriod(root, render, cursor, hasCalendar):
```

#### Description

cdbPeriod manages period-related behavior for a custom database UI component: it uses the provided root element and render function together with a cursor to control and render the current period state, and it optionally adapts behavior when a calendar is present.

It also defines a nested helper function named shift which adjusts or moves the period cursor.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `render` | `Unknown` | ✅ | — |
| `cursor` | `Unknown` | ✅ | — |
| `hasCalendar` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### shift

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def shift(step):
```

#### Description

Move or rotate an internal index, selection, or window by the given amount.

The function applies a displacement of the provided step to advance or rewind whatever position or buffer the module manages.


step is the amount (typically a number, positive or negative) by which the current position/state should be shifted; its sign and magnitude determine direction and distance of the shift.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `step` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbUnscheduled

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbUnscheduled(root, records, openRecord, label='날짜 미지정'):
```

#### Description

Create and render an “unscheduled” section inside a custom-databases UI.

It takes a container element, a list of records that lack a scheduled date, a callback used to open a record, and an optional label (defaulting to the Korean text '날짜 미지정') to display for the section header.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `records` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `label` = `'날짜 미지정'` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### cdbCalendar

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbCalendar(root, database, view, records, openRecord, editable, cursor):
```

#### Description

Creates or renders a calendar-style view for a custom database using the provided root element and dataset, managing display and interaction for the given records.

It ties the database and view configuration to UI behavior such as opening records and editing state.


openRecord is a callback invoked to open or focus a specific record from the calendar; editable is a boolean that controls whether records in the calendar can be edited; cursor indicates the current selection or navigation position within the calendar UI. The other parameters (root, database, view, records) provide the container element, database metadata, view configuration, and the list of records to display, respectively.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `view` | `Unknown` | ✅ | — |
| `records` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `editable` | `Unknown` | ✅ | — |
| `cursor` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbTimeline

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbTimeline(root, database, view, records, openRecord, cursor):
```

#### Description

Render and manage a timeline-style view of records from a custom database into a given root element.

It takes the database and view configuration, the set of records to display, a callback to open a single record, and an optional cursor for pagination or position, and uses those to build and update the timeline UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `view` | `Unknown` | ✅ | — |
| `records` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `cursor` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### cdbRenderView

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbRenderView(root, database, view, relations, openRecord, editable=false):
```

#### Description

Render a database view into the given DOM root element using the provided database and view metadata.

It uses relation definitions to show linked data, supports opening a specific record via the openRecord handler, and can enable editing when the editable flag is true. The nested render function performs the actual DOM construction/refresh.


relations supplies related-table metadata used to display linked records; openRecord is a callback invoked to open or focus a particular record; editable is an optional boolean (default false) that toggles whether the rendered view allows inline editing. The other parameters (root, database, view) are the target DOM container and the database/view descriptions to render.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `root` | `Unknown` | ✅ | — |
| `database` | `Unknown` | ✅ | — |
| `view` | `Unknown` | ✅ | — |
| `relations` | `Unknown` | ✅ | — |
| `openRecord` | `Unknown` | ✅ | — |
| `editable` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### render

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def render():
```

#### Description

Initializes and updates the visual presentation of the custom databases UI in the local client.

It prepares DOM elements, attaches event handlers, and populates data so the custom-databases view is displayed and interactive.

#### Complexity

Not analyzed

---



### linkedDatabaseOptions

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def linkedDatabaseOptions():
```

#### Description

Asynchronously obtains and provides options related to linked databases.

The function likely performs asynchronous work (e.g., fetching or computing) to produce a set of options for use elsewhere in the application.

#### Complexity

Not analyzed

---



### renderLinkedDatabase

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def renderLinkedDatabase(container, databaseId, viewId):
```

#### Description

Asynchronously renders a linked database view into a given container element.

It fetches or constructs the specified database view (by databaseId and viewId) and inserts the resulting UI into the provided container, managing any internal active state via a nested active function.


container is the DOM element (or similar container) where the linked database view will be rendered; databaseId and viewId are identifiers that select which database and which view of that database to display.

Being async, the function returns a Promise that resolves when the rendering and any setup work (including activating internal state) are complete.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `container` | `Unknown` | ✅ | — |
| `databaseId` | `Unknown` | ✅ | — |
| `viewId` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### active

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def active():
```

#### Description

This is a parameterless function named active defined in apps/local-client/static/custom-databases.js.

The extracted data does not include an implementation or docstring, so the specific behavior is not specified here.

#### Complexity

Not analyzed

---



### cdbRefreshLinked

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def cdbRefreshLinked():
```

#### Description

Refreshes the set of linked/custom database entries managed by the local client UI.

When called, it updates the displayed information for linked databases so the UI reflects the current state.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

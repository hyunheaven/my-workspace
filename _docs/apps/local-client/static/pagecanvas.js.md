<!-- METADATA: {"source_path": "apps/local-client/static/pagecanvas.js", "source_sha": "4c7761186c0e2dc4bce83ddf401e9c14210b760d", "extraction_quality": "structural", "model": "gpt-5-mini", "generated_at": "2026-11-18T03:20:15Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "apps/local-client/static/pagecanvas.js",
  "source_hash": "67cd8edff9d317d3ba21ed474586c6ece29fea40468fb0eb4fda8924d2935428",
  "last_updated": "2026-11-18T03:20:15.463552+00:00",
  "git_sha": "4c7761186c0e2dc4bce83ddf401e9c14210b760d",
  "tokens_used": 32923,
  "complexity_score": 8,
  "estimated_review_time_minutes": 60,
  "external_dependencies": []
}
```

</details>

[Documentation Home](../../../README.md) > [apps](../../README.md) > [local-client](../README.md) > [static](./README.md) > **pagecanvas**

---

# pagecanvas.js

> **File:** `apps/local-client/static/pagecanvas.js`

![Complexity: High](https://img.shields.io/badge/Complexity-High-red) ![Review Time: 60min](https://img.shields.io/badge/Review_Time-60min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module implements a wide set of client-side utilities and handlers for an in-browser page canvas used in a local client application. The functions manage canvas state and metadata (colors, tabs, mastheads, properties), editing workflows (draft persistence, dirty tracking, undo/redo, edit history), keyboard and clipboard interactions (shortcuts, copy/cut/paste), and UI rendering for workspace tabs and tags. Several functions are focused on serializing, persisting and restoring in-progress edits (draft read/write/remove/restore), as well as coordinating saves and scheduled save timers.

The file wires DOM and global event handlers to the canvas element and the document/window to intercept keyboard and clipboard events, handle beforeunload navigation checks, and keep the editing model consistent with user actions. The presence of an async navigation guard indicates navigation may be prevented when unsaved changes exist. Overall, it centralizes the logic for maintaining an editable page canvas, connecting UI rendering, user input handling, and draft persistence mechanisms.

## Dependencies

No dependencies identified.

## 📁 Directory

This file is part of the **static** directory. View the [directory index](./README.md) to see all files in this module.

## Architecture Notes

- Event-driven: registers DOM and global event listeners (copy, cut, paste, focusin, keydown, beforeunload).
- Separation of concerns between UI rendering, state management (dirty/draft), and input handling.
- Persistence-oriented: explicit functions for reading, writing, removing, and restoring drafts.
- Contains both synchronous and asynchronous functions (e.g., an async navigation guard).

## Maintenance Notes

- Render and update canvas-related UI elements such as workspace tabs, page mastheads, and page tags.
- Manage canvas properties and visual state including colors, depth, and shortcut identifiers.
- Track editing state and lifecycle: detect dirty edits, persist and restore drafts, schedule saves, and manage undo/redo history.
- Handle keyboard and clipboard interactions by registering event listeners for copy/cut/paste and keydown events on the canvas and document, and prevent navigation when appropriate.
- Provide utility helpers for canvas structure and navigation (depth, parent index, subtree boundaries) used by editing and rendering functions.


---

## Registered at Module Level

- `canvasBlockRoot.addEventListener('copy')`
- `canvasBlockRoot.addEventListener('cut')`
- `canvasBlockRoot.addEventListener('paste')`
- `canvasBlockRoot.addEventListener('focusin')`
- `canvasBlockRoot.addEventListener('keydown')`
- `window.addEventListener('beforeunload')`
- `document.addEventListener('keydown')`



---

## Functions and Classes


### canvasShortcutIDs

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasShortcutIDs(key):
```

#### Description

Given a key identifier, this function maps that key to the corresponding canvas shortcut element IDs.

It is intended to look up or produce the DOM ID(s) associated with a particular canvas shortcut key.


key: a value (typically a string or identifier) representing the shortcut key whose associated canvas shortcut IDs are being requested.

Returns the canvas shortcut element ID or a collection of IDs corresponding to the provided key.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `key` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSetShortcutIDs

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSetShortcutIDs(key, ids):
```

#### Description

Associates or updates the set of shortcut element IDs for a given shortcut key.

It stores or registers the provided ids under the specified key so the application can look up which elements correspond to that shortcut.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `key` | `Unknown` | ✅ | — |
| `ids` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### pageTabColor

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def pageTabColor(page):
```

#### Description

Determines the color used for a page's tab in the UI.

The function computes or looks up the appropriate color for the given page so the tab can be rendered with a consistent appearance.


page: the page whose tab color is to be determined; typically this will be a page object or identifier used by the application to decide the tab color.

Returns a value representing the color for the page tab, commonly a CSS color string (for example a hex code or rgb/rgba string).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### renderWorkspaceTabs

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def renderWorkspaceTabs(docs=pageDocuments):
```

#### Description

Render the workspace's document tabs in the page canvas UI using the provided list of document objects.

It updates the displayed tabs to reflect the documents passed in, defaulting to the module-level pageDocuments when no argument is provided.


docs is a collection (e.g., array) of document objects to be shown as tabs; when omitted the function uses the default pageDocuments variable from the surrounding module.

This function does not return a meaningful value (returns undefined); its effect is to update the UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `docs` = `pageDocuments` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### showPageTags

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def showPageTags(tags):
```

#### Description

Displays the set of tags associated with the current page in the UI.

It takes the provided tags collection and renders or updates the page tag elements so users can view (and possibly interact with) the page's tags.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tags` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### applyCanvasProperties

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def applyCanvasProperties(pageId, properties):
```

#### Description

Apply the given properties to the canvas associated with the specified pageId.

It updates the canvas configuration or appearance for that page based on the provided properties object.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `pageId` | `Unknown` | ✅ | — |
| `properties` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### changeCanvasProperties

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def changeCanvasProperties(changes):
```

#### Description

Updates one or more properties of the page canvas according to the provided changes object.

It applies the supplied property values to the canvas so the canvas configuration or appearance is modified accordingly.


changes is an object whose keys are canvas property names and whose values are the new values to apply for those properties.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `changes` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasShortcuts

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasShortcuts(docs):
```

#### Description

Initializes or configures keyboard and/or UI shortcuts related to a canvas interface, using provided documentation or metadata.

The function ties the given docs into the canvas shortcut system so the canvas responds to configured shortcut actions.


docs: a documentation or metadata object/list that the function uses to determine which shortcuts to create or how they should behave; it supplies the definitions or descriptions needed to set up the canvas shortcuts.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `docs` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasPageMasthead

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasPageMasthead(page):
```

#### Description

Builds and configures the page masthead area for a given page, creating the header UI (title, controls, and any contextual elements) used at the top of the page canvas.

It prepares and/or inserts the masthead into the page's DOM so the page has a consistent top bar.


Returns the created masthead DOM element (an HTMLElement) representing the header inserted or ready to be inserted into the page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasClearTimer

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasClearTimer():
```

#### Description

Stops and clears any running timer used for canvas-related periodic actions (for example an interval or timeout driving canvas updates), ensuring the timer reference is removed so it won't fire again.

#### Complexity

Not analyzed

---



### canvasStatus

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasStatus(status, failed=false):
```

#### Description

Updates the canvas status display using the provided status message and an optional failure flag.

The function takes a status string and an optional boolean to indicate whether the status represents a failure, and applies that state to the canvas-related UI or internal state.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `status` | `Unknown` | ✅ | — |
| `failed` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasScheduleSave

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasScheduleSave():
```

#### Description

Saves the current canvas schedule state to persistent storage or sends it to the server.

It collects the canvas scheduling data and initiates the save operation so the user's schedule changes are stored.

#### Complexity

Not analyzed

---



### canvasDraftKey

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasDraftKey(id):
```

#### Description

Generate a storage key string for a canvas draft associated with the given identifier.

The function constructs a consistent key (likely for localStorage or similar) that can be used to save or retrieve the draft for the specified canvas id.


id is the identifier for the canvas or page whose draft key is being generated; its name makes its purpose clear so no further detail is required.

Returns the draft storage key as a string.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasDraftRead

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasDraftRead(id):
```

#### Description

Reads or loads a saved canvas draft identified by the given id, retrieving the draft data for use in the page canvas module.

This function is responsible for fetching the stored draft contents so they can be displayed or edited.


id is the identifier of the canvas draft to read; it tells the function which saved draft to retrieve.

Returns the retrieved draft data (for example, an object representing the canvas contents) or null/undefined if no draft is found.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasDraftRemove

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasDraftRemove(id):
```

#### Description

Removes a draft canvas identified by the given id from the application's local state or storage.

This function deletes the draft entry corresponding to the provided identifier so it is no longer available in the draft list.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSameContent

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSameContent(title, blocks, other):
```

#### Description

Determines whether the content described by the given title and blocks matches the content represented by the other argument.

In other words, it checks if two canvas-like content representations are equivalent.


title is the identifier or heading for the content being compared, blocks is the collection (e.g., array) of content blocks that make up that canvas, and other is the other content representation to compare against (likely another title/blocks pair or canvas object).

Returns a boolean indicating whether the provided title/blocks content and the other content are considered the same.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | `Unknown` | ✅ | — |
| `blocks` | `Unknown` | ✅ | — |
| `other` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasPersistDraft

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasPersistDraft():
```

#### Description

Persists the current draft state of the page canvas.

It saves the in-memory canvas draft so it can be recovered later (for example to local storage or a backend).

#### Complexity

Not analyzed

---



### canvasMarkDirty

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasMarkDirty():
```

#### Description

Marks the page canvas as 'dirty' so the rendering system knows it needs to be redrawn.

This signals that something about the canvas state has changed and a subsequent render pass should update the display.

#### Complexity

Not analyzed

---



### canvasResetDirty

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasResetDirty():
```

#### Description

Resets the canvas "dirty" state, marking the page canvas as not modified.

This clears whatever internal flag or indicator is used to track unsaved changes so the application treats the canvas as clean.

#### Complexity

Not analyzed

---



### canvasRestoreDraft

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRestoreDraft(page):
```

#### Description

Restore the saved draft state for a given canvas page, applying previously stored edits or drawing state back onto the page so the user can continue editing where they left off.

This function operates on the provided page object to reinstate its draft content into the canvas UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasMayNavigate

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def canvasMayNavigate(departing=false):
```

#### Description

Asynchronously determines whether the canvas page is allowed to navigate (for example when the user attempts to leave or change views).

It encapsulates any checks or user prompts needed before permitting navigation away from the canvas.


departing (boolean) indicates whether the navigation decision is being made because the current context is departing (true) versus other kinds of navigation checks (false).

Returns a Promise that resolves to a boolean indicating whether navigation is permitted.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `departing` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasEditState

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasEditState():
```

#### Description

Initializes and/or provides the edit-related state for the page canvas.

It encapsulates the current editing mode and associated flags used by the canvas UI to track selection, dragging, and other edit interactions.


Returns an object representing the canvas edit state (the collection of flags and properties that describe the current editing context such as selection, mode, and interaction status).

#### Complexity

Not analyzed

---



### canvasTrackEdit

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasTrackEdit(target=null):
```

#### Description

Enters or initiates edit mode for a canvas track, operating on a specified target track if provided.

The function is intended to begin or manage editing actions for a track displayed on a canvas.


target is an optional parameter (typically a DOM element, track identifier, or null) that indicates which canvas track to edit; if left null the function will operate on the current or default selection.

Does not return a meaningful value (returns undefined / no explicit return).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target` = `null` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasUpdateHistoryButtons

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasUpdateHistoryButtons():
```

#### Description

Updates the enabled/disabled state and visual appearance of the canvas history navigation controls (for example undo/redo or back/forward buttons) to reflect the current history stack and user interaction state.

It synchronizes the UI buttons with the canvas's history so that only valid actions are available to the user.

#### Complexity

Not analyzed

---



### canvasUndoEdit

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasUndoEdit(redo=false):
```

#### Description

Performs an undo operation on the canvas editing history; when the optional parameter is true it performs a redo instead.

This toggles the canvas state to the previous (or next) edit in the edit history.


redo is a boolean flag (default false); when false the function undoes the last edit, when true it reapplies an undone edit (redo).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `redo` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasBindTextInput

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasBindTextInput(input, apply):
```

#### Description

Attaches behavior to a text input element so that edits made by the user are handled and finalized for the canvas.

It wires the provided input element to an apply callback and uses an internal finish function to complete the edit and perform any cleanup or final application of the text change.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `input` | `Unknown` | ✅ | — |
| `apply` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### finish

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def finish():
```

#### Description

Finalizes the current page/canvas state when invoked; intended to perform any end-of-operation cleanup or finalization steps for the page canvas.

#### Complexity

Not analyzed

---



### canvasDepth

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasDepth(block):
```

#### Description

Determines the depth (stacking or hierarchical level) of a given block within a page canvas.

It computes how deep the provided block is positioned relative to other canvas elements or its container.


block is the canvas element or block object whose depth is to be determined; it represents the item within the canvas hierarchy for which the function will compute a depth value.

Returns a numeric value representing the block's depth (its stacking/hierarchical level) within the canvas.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSetDepth

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSetDepth(block, depth):
```

#### Description

Set the drawing or rendering depth (z-order) of the given block within the canvas so that it appears above or below other elements as needed.

It updates the block's depth property and causes the canvas to treat the block at the specified stacking level.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |
| `depth` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSubtreeEnd

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSubtreeEnd(index):
```

#### Description

Marks or finalizes the end of a subtree on the canvas identified by the given index; typically used to close or finish drawing a hierarchical subtree region at that position.

The function updates the canvas state to indicate that the subtree rooted or referenced by index is complete.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasParentIndex

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasParentIndex(index):
```

#### Description

Given a canvas element index, this function determines and returns the index of that element's parent within the canvas structure.

It maps a child canvas index to its parent canvas index.


index is an integer representing the position or identifier of a canvas element whose parent index is being requested.

Returns the numeric index of the parent canvas corresponding to the provided index.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasPreviousSibling

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasPreviousSibling(index):
```

#### Description

Given an index identifying a canvas in the page canvas collection, this function finds and returns the previous sibling (the canvas immediately before it) in that collection.

index is the numeric position of the current canvas within the collection; it identifies which canvas to use when locating its previous sibling.

Returns the previous sibling canvas (or a falsy value such as null/undefined) if there is no previous sibling.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasNextSibling

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasNextSibling(index):
```

#### Description

Given an index identifying a canvas, this function obtains and returns the next sibling element (the DOM node that follows that canvas in its parent).

It is intended to navigate from one canvas element to the next in document order.


Returns the next sibling DOM element that follows the canvas at the provided index, or null if there is no next sibling.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasNewBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasNewBlock(type='paragraph', content='', checked=false, depth=0):
```

#### Description

Create a new block for the page canvas with the specified type, initial content, checkbox state, and nesting depth.

It prepares a block representation suitable for insertion into the canvas or the document model.


type selects the block kind (e.g., 'paragraph'); content is the initial text; checked is a boolean used for checklist/checkbox-style blocks; depth is an integer indicating nesting/indentation level.

Returns the newly created block representation (suitable for insertion into the canvas or document model).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `type` = `'paragraph'` | `Unknown` | ❌ | — |
| `content` = `''` | `Unknown` | ❌ | — |
| `checked` = `false` | `Unknown` | ❌ | — |
| `depth` = `0` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasInsertBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasInsertBlock(index, type='paragraph', content='', depth=0):
```

#### Description

Inserts a new content block into the canvas at the specified position.

The block's type, initial content, and nesting depth can be provided via the optional parameters.


Performs the insertion as a side effect and does not return a meaningful value (implicitly returns undefined).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `type` = `'paragraph'` | `Unknown` | ❌ | — |
| `content` = `''` | `Unknown` | ❌ | — |
| `depth` = `0` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasFocusBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasFocusBlock(index, position=0):
```

#### Description

Set keyboard focus (place the caret/cursor) into a specific block within the canvas identified by its index, optionally positioning the cursor at a given offset inside that block.

The function targets the block at the provided index and moves the insertion point to the given position (default 0).


index is the numeric position of the block within the canvas to focus; position is an optional numeric offset within that block where the caret should be placed (defaults to 0).

Does not return a meaningful value (performs focus/cursor side effects on the canvas).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `position` = `0` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasVisibleSibling

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasVisibleSibling(index, step):
```

#### Description

Locate the visible sibling canvas relative to a given canvas index, using a numeric offset.

The function computes which canvas is the visible neighbor by moving from the provided index by the given step.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `step` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasAddBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasAddBlock(type='paragraph', index=canvasBlocks.length, depth=0):
```

#### Description

Adds a new block element to the page canvas using the given block type, inserting it at the specified position and with the specified nesting depth.

By default it creates a paragraph block appended to the end of the existing canvas blocks with zero depth.


type selects the kind of block to create (default 'paragraph'); index chooses where to insert the new block (default is canvasBlocks.length, i.e., append to the end); depth sets the nesting or indentation level for the new block (default 0).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `type` = `'paragraph'` | `Unknown` | ❌ | — |
| `index` = `canvasBlocks.length` | `Unknown` | ❌ | — |
| `depth` = `0` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasMoveBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasMoveBlock(index, step):
```

#### Description

Moves a block located on a canvas from its current position by a relative amount.

The function adjusts the block at the given index by the specified step, allowing reordering or positional changes on the canvas.


index is the position or identifier of the block to move; step is the relative offset (positive or negative) to apply to that block's position.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `step` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasMoveSubtree

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasMoveSubtree(index, destination, depthDelta=0):
```

#### Description

Move a subtree located at the given index to a new position specified by destination within the canvas data structure, optionally adjusting the depth of all nodes in that subtree by depthDelta.

It performs the relocation and depth adjustment so the moved subtree integrates correctly at its new location.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `destination` | `Unknown` | ✅ | — |
| `depthDelta` = `0` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasCanIndent

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasCanIndent(index):
```

#### Description

Determines whether the item at the given index in the canvas can be indented.

It checks if an indent operation is allowed for that position and returns the result as a boolean.


Returns a boolean indicating whether the canvas element at the specified index can be indented.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasIndentBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasIndentBlock(index, delta):
```

#### Description

Adjusts the indentation level of a block in the canvas at the given index by the specified delta.

It applies an increase or decrease in indent to the block identified by index within the page canvas.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `delta` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasRemoveBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRemoveBlock(index):
```

#### Description

Removes a block from the page canvas at the specified position.

It updates the canvas state to reflect that the block at the given index has been deleted and any related UI or data structures are adjusted accordingly.


index: the numeric position (zero-based) of the block on the canvas to be removed.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSelectionBounds

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSelectionBounds():
```

#### Description

Compute and return the current selection bounds for the page canvas.

The function determines the rectangular area that encloses the active selection on the canvas, useful for layout, rendering, or hit-testing operations.


Returns an object or structure representing the selection bounding rectangle (e.g., coordinates and size) for the canvas.

#### Complexity

Not analyzed

---



### canvasRenderSelection

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRenderSelection():
```

#### Description

Renders the current user selection onto the page canvas.

It updates the visual representation of the selection (such as bounds, handles, or highlight) so that the canvas reflects the latest selection state.

#### Complexity

Not analyzed

---



### canvasFocusSelection

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasFocusSelection(index):
```

#### Description

Sets focus to a particular selection on the canvas identified by the given index.

It brings the specified selection into focus so subsequent input or actions apply to that selection.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSelectBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSelectBlock(index, extend=false):
```

#### Description

Selects a block in the page canvas identified by its numeric index.

If the optional extend flag is true, the selection is extended (e.g., adding to an existing selection) rather than replacing it.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `index` | `Unknown` | ✅ | — |
| `extend` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasRemoveSelection

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRemoveSelection():
```

#### Description

Removes any current selection from the page canvas.

It clears visual selection indicators and resets any internal state related to a selected region or object on the canvas so the canvas is left with no active selection.

#### Complexity

Not analyzed

---



### canvasClipboardPayload

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasClipboardPayload():
```

#### Description

Builds and returns a payload representing the current canvas content suitable for placing on the clipboard (for copy/cut operations).

The payload likely packages image data and related metadata from the page canvas into a single object.


Returns an object containing the canvas clipboard payload (e.g., image data and any associated metadata) to be used when writing to the clipboard.

#### Complexity

Not analyzed

---



### canvasClipboardText

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasClipboardText(block):
```

#### Description

Handles clipboard-related text operations for a canvas block element.

The function performs the work needed to copy, paste, or otherwise process text associated with the given canvas block.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasCopyBlocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasCopyBlocks(event):
```

#### Description

Handle a user event to copy selected blocks on a page canvas.

It processes the provided event (typically a user interaction such as a keyboard or mouse event) and performs the copy action for canvas blocks.


event is the DOM event object that triggered the copy action (e.g., keyboard shortcut or mouse event) and carries context about the user interaction.

No return value; the function performs the copy operation as a side effect.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasValidClipboardBlock

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasValidClipboardBlock(block):
```

#### Description

Checks whether the provided clipboard block is a valid block for use with the canvas.

It performs validation on the given block to determine if it meets the expected shape/requirements for pasting or importing into the canvas.


block: the clipboard block object to validate (expected to be a data structure representing a copied canvas block).

A boolean indicating whether the given block is valid for use on the canvas (true = valid, false = invalid).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasPasteBlocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasPasteBlocks(event):
```

#### Description

Handles paste events on the page canvas to insert one or more blocks when the user pastes content.

It processes the paste event and performs the necessary DOM or application state updates to add the pasted blocks (with an internal helper function named 'added' to manage newly inserted items).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### added

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def added({type,content,checked,depth=0}):
```

#### Description

Handles an added item described by an object with properties type, content, checked, and an optional nesting depth.

It performs whatever creation or processing is needed for a newly added element using those properties.


type identifies the kind of item, content holds the item's payload or text, checked is a boolean flag (e.g., for checkbox state), and depth is a numeric nesting level that defaults to 0.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `{type,content,checked,depth=0}` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasDropDestination

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasDropDestination(event, index):
```

#### Description

Handles a drop action on the page canvas at a specific destination index, using the provided drag/drop event to determine what is being dropped and where.

It updates the canvas state or layout to insert or move the dropped item at the given position.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | `Unknown` | ✅ | — |
| `index` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasChangeBlockType

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasChangeBlockType(block, index, type):
```

#### Description

Changes the type of a block within the page canvas at the given position.

It updates the block identified by the provided index to use the specified type.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |
| `index` | `Unknown` | ✅ | — |
| `type` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasSlashMenu

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSlashMenu(row, block, index, input):
```

#### Description

Implements the canvas slash menu behavior for a given block row and input: it manages rendering the menu and highlighting items through its nested render and highlight helpers.

It ties the menu UI to the specified block and input at a given index so users can pick slash-command options in the canvas editor.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `row` | `Unknown` | ✅ | — |
| `block` | `Unknown` | ✅ | — |
| `index` | `Unknown` | ✅ | — |
| `input` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### highlight

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def highlight():
```

#### Description

Highlights a region or element on the page canvas.

It applies visual highlighting (for example by drawing or changing styles) to indicate selection or focus within the local client page canvas.

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

Render updates to the page canvas in the local client UI.

The function performs the drawing or re-drawing of visual content on the canvas element so the displayed page reflects current application state.

#### Complexity

Not analyzed

---



### canvasReadTable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasReadTable(block):
```

#### Description

Reads a table from a given canvas block and extracts its contents into a JavaScript data representation so the table can be inspected or manipulated programmatically.

It converts the block's table structure into a usable format for further processing.


block is the canvas block (a DOM element or internal block object) that contains the table to be read; the function uses this to locate and extract the table data.

Returns the extracted table data, typically as a structured JavaScript object or array (for example, an array of rows or cell objects) representing the table contents.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasRenderTable

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRenderTable(block, readOnly=false):
```

#### Description

Creates the logic needed to draw or display a table representation for a given content block on a canvas or canvas-like area, with support for producing a non-interactive (readOnly) rendering.

The function organizes rendering behavior and exposes a nested render function to perform the actual drawing.


block is the data or block object that provides the table structure and content to be rendered; readOnly is a boolean flag (default false) that controls whether the rendered table should be produced in a non-interactive, view-only mode.

Returns an object exposing rendering behavior (including the nested render function) that can be invoked to draw or update the table display for the provided block.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |
| `readOnly` = `false` | `Unknown` | ❌ | — |

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

Renders the page canvas content and updates the visual display for the local client.

It performs the necessary drawing and layout work to present the current canvas state to the user.

#### Complexity

Not analyzed

---



### canvasRenderPageLink

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRenderPageLink(block):
```

#### Description

Renders an interactive page link element on the canvas for the given block and manages its dynamic state.

It constructs the visual representation and hooks up an internal update function to refresh the element when the block's data changes.


block is the data object representing the page link to render (its properties are used to build and update the visual element).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `block` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### update

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def update():
```

#### Description

Performs an update of the page canvas state, refreshing visual elements and internal state each time it is called.

It is intended to be invoked on a regular interval or in response to changes so the displayed canvas stays in sync with the underlying data and user interactions.

#### Complexity

Not analyzed

---



### canvasRenderBlocks

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRenderBlocks():
```

#### Description

Renders the page's block elements onto a canvas surface, arranging and drawing individual blocks for the page canvas.

It also contains a nested fit helper to adjust scaling/position so the rendered blocks fit the available canvas area.

#### Complexity

Not analyzed

---



### fit

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def fit():
```

#### Description

Adjusts the canvas or page view to fit its contents or the visible viewport, recalculating scale and/or translation so the content is fully visible.

Typically invoked to reset zoom/position so the drawing or page elements are framed within the canvas area.

#### Complexity

Not analyzed

---



### canvasSidebarTree

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasSidebarTree(docs):
```

#### Description

Builds the sidebar tree UI for a canvas page from a collection of document descriptors.

It organizes documents into groups and entries and uses an internal addGroup helper to create or populate group containers in the tree structure.


docs is the collection (e.g., an array) of document metadata/objects that the function will iterate over to create the grouped sidebar entries; the nested addGroup function handles creating or updating a specific group within the tree.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `docs` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### addGroup

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def addGroup(children, depth):
```

#### Description

Creates and inserts a new group container into the page canvas using the provided children elements and a specified nesting depth.

The function organizes or registers the children under a group at the given depth to manage rendering or z-ordering within the canvas.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `children` | `Unknown` | ✅ | — |
| `depth` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasShowEmpty

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasShowEmpty():
```

#### Description

Updates the page canvas UI to the “empty” state — clears any existing content and renders the placeholder/empty-canvas visuals so the user sees an empty page canvas.

It prepares the canvas for new content or indicates there is nothing to display.

#### Complexity

Not analyzed

---



### canvasTemplateSummary

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasTemplateSummary(page):
```

#### Description

Generate a concise summary of a canvas template based on the provided page object.

It extracts relevant template-related information from the page and formats it into a brief descriptive summary.


Returns a summary string describing the canvas template information derived from the page argument.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasBreadcrumb

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasBreadcrumb(page, docs):
```

#### Description

Create or update a breadcrumb navigation for a documentation page.

It uses the provided page and the overall docs structure to generate the breadcrumb trail that reflects the page's location in the documentation hierarchy.


page is the current documentation page (object or identifier) for which the breadcrumb should be built; docs is the collection or hierarchical structure of all documentation pages used to resolve parent/ancestor relationships.

Returns a DOM element representing the constructed breadcrumb navigation (or attaches it to the page and returns that element).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `docs` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasPageMeta

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasPageMeta(page):
```

#### Description

Produce metadata for a canvas page represented by the given page argument.

The function gathers and returns information about the page that other parts of the application can use when rendering or managing the canvas.


Returns an object containing metadata about the provided page (for example identifiers, sizing, or display-related attributes) that callers can use to render or manage the canvas page.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasDisplayPage

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasDisplayPage(page, docs, created=false):
```

#### Description

Render or update a canvas view for a given page using the provided document data, optionally handling a newly created page.

It takes the page identifier or object and associated document list and updates the UI accordingly.


page is the page to display (identifier or page object), docs is the document data or list used to render that page, and created is a boolean flag (default false) indicating whether the page was just created and may need special handling.

This function does not return a value (returns undefined) and performs its work by updating the canvas/UI.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `docs` | `Unknown` | ✅ | — |
| `created` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasUpdateTree

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasUpdateTree(page, docs):
```

#### Description

Updates the canvas' internal/tree representation for a given page using the provided documents.

It refreshes or rebuilds the visual or data tree structure so the canvas reflects the current state of the specified page and its associated documents.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `docs` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasMergePageIntoTree

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasMergePageIntoTree(page):
```

#### Description

Integrates the provided page object into the existing canvas tree structure used by the application.

It merges the page's nodes and content into the current in-memory document/tree so the canvas reflects the page's data.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### loadCanvas

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def loadCanvas(createdPage):
```

#### Description

Asynchronously initializes or loads the canvas UI for a given page.

It prepares canvas-related state and behaviour for the provided createdPage and includes a nested active function to manage or toggle the active state of the canvas or its controls.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `createdPage` | `Unknown` | ✅ | — |

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

This is a parameterless function named active defined in apps/local-client/static/pagecanvas.js.

Based only on its name and signature, it is intended to access, query, or manage the 'active' state of the page canvas component.

#### Complexity

Not analyzed

---



### openCanvas

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def openCanvas(pageId, createdPage):
```

#### Description

Opens the canvas UI for a given page.

The async function loads or initializes the canvas view associated with the provided page identifier and handles any setup needed when a page has just been created.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `pageId` | `Unknown` | ✅ | — |
| `createdPage` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### createCanvasPage

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def createCanvasPage(parent=null, starter=false):
```

#### Description

Asynchronously creates and initializes a new canvas page element for the application.

If a parent is provided it will attach the new page to that container, and if the starter flag is true it will initialize the page in a starter/template mode.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `parent` = `null` | `Unknown` | ❌ | — |
| `starter` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### canvasWriteSnapshot

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def canvasWriteSnapshot(page, snapshot, silent):
```

#### Description

Asynchronously writes a snapshot for a given page to the application's canvas/storage.

It performs the write operation and optionally suppresses any user-visible notifications or UI updates when the silent flag is set.


page is the target page (object or identifier) to which the snapshot belongs; snapshot is the data or state to be written; silent is a boolean that, when true, suppresses notifications or UI side effects for the write operation.

Returns a Promise that resolves when the snapshot write operation has completed.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | `Unknown` | ✅ | — |
| `snapshot` | `Unknown` | ✅ | — |
| `silent` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### saveCanvas

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def saveCanvas(silent=false):
```

#### Description

Asynchronously saves the current canvas state (persists or uploads the canvas data).

The function performs the save operation and completes when the save has finished.


silent (boolean, default false) controls whether the save should operate without user-facing notifications or prompts (true = suppress notifications, false = allow them).

Being async, it returns a Promise that resolves when the save operation completes (or rejects on error).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `silent` = `false` | `Unknown` | ❌ | — |

#### Complexity

Not analyzed

---



### restoreCanvasRevision

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def restoreCanvasRevision(snapshot, button):
```

#### Description

Asynchronously restores the page canvas to a previous state represented by the given snapshot, likely using the provided button element as the UI trigger or to update its state while the operation runs.

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `snapshot` | `Unknown` | ✅ | — |
| `button` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### canvasRenderHistory

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def canvasRenderHistory(snapshot):
```

#### Description

Render a saved canvas history state onto the page canvas.

It takes a snapshot representing previous drawing data and updates the visual canvas to reflect that recorded history (for example rebuilding or replaying past drawing operations).


snapshot is an object that contains a saved canvas history state (e.g., recorded drawing operations, frames, or other data needed to replay or reconstruct the canvas).

#### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `snapshot` | `Unknown` | ✅ | — |

#### Complexity

Not analyzed

---



### duplicateCanvasPage

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def duplicateCanvasPage():
```

#### Description

Asynchronously creates a duplicate of the current canvas page in the application, performing any necessary state updates and UI refreshes to reflect the newly created page.

It encapsulates the logic for copying page contents and integrating the duplicate into the canvas page list.

#### Complexity

Not analyzed

---



### installCanvasCommands

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

#### Signature

```javascript
def installCanvasCommands():
```

#### Description

Registers or wires up command handlers and shortcuts used by the page canvas UI.

It sets up the canvas-level commands so the rest of the application can invoke canvas actions consistently.

#### Complexity

Not analyzed

---



### canvasShowHistory

![Type: Async](https://img.shields.io/badge/Type-Async-blue)

#### Signature

```javascript
async def canvasShowHistory():
```

#### Description

Asynchronously displays or opens the canvas history UI for the current document or workspace, likely updating the page to show past canvas states and enabling navigation through them.

It contains a nested helper function named 'active' which is used internally to manage the active/history item state.

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

This documents a JavaScript function named active that is defined with no parameters.

The extracted data does not include any implementation details or docstring, so the specific behavior or side effects of the function are not specified here.

#### Complexity

Not analyzed

---



---

## Navigation

**↑ Parent Directory:** [Go up](./README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*

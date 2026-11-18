# ADR-0004 — Page-First Local Workspace

Status: Accepted for **local PoC v0.10** (not security approval or production release)
Date: 2026-11-15

## Context
The earlier v0.9 UI organized each feature (Template Library, Page Tree, Task Database, Calendar, Projects) as a separate screen. The linked Notion `시작하기` page demonstrates the expected **Page is the primary workspace surface** with editable headings, checklists, toggle blocks and embedded subpages. We refer only to behavior and information architecture; no Notion media/text/design assets are copied.

## Decision
- The user's Page Tree appears in the Sidebar; the central Page Canvas is the default landing surface.
- Pages continue using `documents`, preserving template-bound fields, existing document IDs and parent references.
- Add `page_blocks(id, page_id, position, block_type, content, checked)` on local SQLite. Full-page block updates are a single transaction with parent document `revision` concurrency protection.
- A blank page has internal `template_id=__blank_page__`, **not** a new public catalog entry. Original 80 catalog templates remain unchanged.
- Supported blocks: text, heading levels, bullet, checkbox, toggle, quote, code-as-text, divider. No rich HTML/rendered scripts/images/video/voice/remote imports.
- The existing form-based template editor remains available for original template fields, while Page Canvas provides additive blocks.

## Migration and recovery
- `CREATE TABLE IF NOT EXISTS` only. Existing document data/fields are not changed. Backup `workspace.db` with the process stopped before using a previously used DB.
- A new `EAW_DATA_DIR` allows clean PoC validation without mutating the v0.9 test database.
- **Do not roll back a v0.10-edited database to v0.9 for editing without a backup.** v0.9 ignores new blocks, and could create divergent edits if reused.

## Future architecture and trade-offs
- P1: Schema-driven document model, nested blocks, inline child-page blocks, metadata/relations and a unified searchable Page Index.
- P2: Tiptap/ProseMirror rich editor, keyboard shortcuts, safe formatting, undo/redo, autosave, block drag/drop and page history.
- P3: Inline linked Database Views (Table/Board/Calendar) with centralized query and permission enforcement.
- P4: Optional shared Workspace/Teamspace, centralized PostgreSQL, SSO/RBAC/ACL, Yjs collaboration, approved AI.
- Consequence: v0.10 gets closer to Notion interaction with minimal dependencies but is **not** Notion feature parity. The existing v0.9 task/project data remains separate until cross-view integration.

## Acceptance criteria and evidence
- 80 templates unchanged; 24 pytest cases pass; synthetic browser create/modify/save/reopen flow passes; blocked media and external API routes remain blocked.
- Windows 11 manual E2E is pending.

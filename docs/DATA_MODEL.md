> **v0.5 안내:** 아래 문서는 v0.4 Hybrid Target 설계 자료입니다. 실행형 PoC 및 보안 제한의 우선 적용 기준은 [`SECURE_FEATURE_POLICY.md`](SECURE_FEATURE_POLICY.md), [`TEMPLATE_LIBRARY_SPEC.md`](TEMPLATE_LIBRARY_SPEC.md), [`DEVELOPMENT_ROADMAP_v05.md`](DEVELOPMENT_ROADMAP_v05.md)입니다. 모든 첨부·미디어·외부 연동/Export 언급은 현 시점에서 비활성화되며 승인 전 구현하지 않습니다.

# Data Model & Integrity Contracts — v0.4

## 1. Bounded contexts
**Local SQLite**: `local_pages`, `local_page_revisions`, `local_attachments`, `local_settings`, `local_search_fts` and migration manifest. Local user identity is OS context, **not** a central Teamspace identity. Local pages have `scope=local` and never appear in Central search by default.

**Central PostgreSQL**: `users`, `teams`, `team_memberships`, `workspaces`, `workspace_memberships`, `pages`, `page_revisions`, `page_acl`, `attachments`, `attachment_links`, `search_documents`, `search_outbox`, `audit_events`, `publish_requests`; P1 adds `collab_documents` and `collab_snapshots`.

## 2. Conceptual schema (draft, migrations not executed)
| Entity | Minimum fields / important constraints | Notes |
|---|---|---|
| users | `id UUID PK`, `oidc_subject UNIQUE`, `status`, `created_at` | never trust caller-supplied principal ID |
| teams | `id`, `name`, `lifecycle_status` | [VERIFY] ownership mapping |
| team_memberships | `team_id,user_id,role,status`, UNIQUE(team_id,user_id) | SSO group reconciliation rules TBD |
| workspaces | `id`, `team_id`, `owner_id`, `name`, `visibility`, `created_at` | shared only; private local is elsewhere |
| workspace_memberships | `workspace_id,user_id,role,status`, UNIQUE pair | effective rights derive from membership + ACL |
| pages | `id`, `workspace_id`, `parent_page_id`, `title`, `status`, `current_revision`, `acl_version`, `created_by` | prevent parent cycles and cross-workspace children |
| page_revisions | `id`, `page_id`, `revision_no`, `editor_schema_version`, `content_json`, `created_by`, `created_at` | immutable; UNIQUE(page_id,revision_no) |
| page_acl | `id`, `page_id`, `principal_type`, `principal_id`, `role`, `effect`, `inheritance_mode`, `acl_version` | explicit DENY wins; safe inheritance semantics |
| attachments | `id`, `storage_key`, `sha256`, `size`, `mime`, `status`, `scan_status` | random internal key, never caller-controlled path |
| attachment_links | `page_id`, `attachment_id` | authorization via page and attachment linkage |
| search_documents | `page_id`, `indexed_revision`, `search_vector/text`, `updated_at` | metadata and snippets filtered by page ACL |
| search_outbox | `event_id`, `aggregate_id`, `revision`, `event_type`, `status` | DB transaction with page mutation |
| audit_events | `id`, `actor_id`, `action`, `resource_kind`, `resource_id`, `timestamp`, `outcome` | append-only operational policy; exclude content |
| publish_requests | `idempotency_key`, `actor_id`, `source_fingerprint`, `destination_id`, `target_page_id`, `state` | prevent duplicate publish on retries |
| collab_documents (P1) | `page_id`, `ydoc_binary`, `schema_version`, `store_generation` | Yjs binary is canonical during collaboration |
| collab_snapshots (P1) | `page_id`, `seq`, `snapshot_binary`, `created_at` | revision/checkpoint policy to be validated |

## 3. Integrity rules
- IDs are opaque UUIDs generated server-side; never use sequential IDs as a security boundary.
- Each shared page belongs to exactly one Workspace. Parent cannot cross Workspace or form cycles.
- Soft-delete tombstone must revoke search, attachment and collaboration access before asynchronous purge.
- P0 page body: immutable editor JSON revisions + `current_revision` CAS; only server increments revision in transaction.
- P1 collaborative document: **Yjs binary** canonical for merged state; derived editor JSON/plain text is a versioned projection for display/search/export. Do not rebuild a new Y.Doc from JSON on every load.
- Publish request: central commit + revision + audit + outbox transaction; attachment staging/rollback/reconciliation separated from DB atomicity.
- ACL version bump on grant/revoke/role change; invalidate sessions, WS capabilities, search caches and AI retrieval authorization caches.
- Index operation idempotent keyed by `(page_id, revision)`; rebuild process handles stale/reordered events and deletion.
- Backups include DB, attachments and cryptographic integrity manifest with tested restore (RPO/RTO [VERIFY]).

## 4. Search and Korean PoC
PostgreSQL FTS uses parser/dictionaries; Korean morphological behavior cannot be presumed. Compare `tsvector`, `pg_trgm` (subject to approved extension), and approved Korean analyzer using a synthetic Korean/English corpus. Evaluate 1/2/3+ syllable queries, ranking, updates, zero unauthorized leak and p95 latency. Do not commit to a particular analyzer without test data.

## 5. Cross-store boundaries
- No Local SQLite DB files mounted or written by Central.
- No direct shared SQLite file over SMB/NAS.
- `local_page_id` and `shared_page_id` are separate; publish provenance is non-sensitive opaque information.
- `local` data never included in shared backup, search index or audit event contents.

## 6. Evolution
Every migration has version, expected before/after schema, backup/restore, online rollout/rollback strategy, tests and owner review. Shared collab schema activates only after P1 gate.

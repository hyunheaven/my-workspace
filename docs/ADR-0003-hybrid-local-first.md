# ADR-0003 — Local Workspace and Optional Shared Deployment

**Date**: 2026-11-15
**Status**: Accepted product direction; detailed infrastructure is proposed and requires validation.

## Decision
Run Personal Workspace independently on Windows PC, with Local FastAPI/SQLite/files and no network requirement. Support an approved Shared Web interface and shared workspace through Central FastAPI/PostgreSQL/storage/SSO. The central server is authoritative for all shared content. Add Yjs/Hocuspocus for real-time co-editing only after secure shared CRUD is stable; AI after separate approved model gateway.

## Benefits
- Offline personal productivity, centralized organization knowledge and auditable delegated access.
- A shared editor/UI/domain contract, limiting duplicate development.
- Explicit boundary between private and shared, with managed Publish workflow.

## Costs / risks
- A shared deployment requires hosting, SSO, backups and an operator.
- RBAC/ACL/revocation across REST/WS/Search/AI add complexity.
- P1 Yjs binary persistence, schema migration and collision/recovery require focused testing.
- No shared offline cache in P0 limits offline collaboration but reduces permission/remanence risk.

## Alternatives
- Always local: rejected for team sharing.
- Single NAS-based SQLite file: rejected for concurrent writes/integrity.
- Full microservice mesh: rejected until scale warrants.
- Pure web-only: rejected because personal offline requirement must remain.

## Follow-ups
Approve threat model, source of truth, identity model and permission inheritance; resolve deployment/licensing and offline packaging in Phase 0.

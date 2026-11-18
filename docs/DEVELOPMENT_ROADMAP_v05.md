# Roadmap v0.5 / Execution Gates

| Gate | Priority | Deliverables | Test / Go-No-Go |
|---|---|---|---|
| Phase 0 — Compliance | P0 | Windows 11 software allowlist, GHES/GHEC, infra, license, data classification | IT+Security approval [확인 필요] |
| Phase 1A — Template PoC | P0 | Static catalog, local SQLite, form editor, safe local API | pytest passing with synthetic data; media & external API absent |
| Phase 1B — Core Workspace | P0 | React/Vite/Tiptap OSS after approval, page tree, typed blocks, history, recovery | Editor schema validation, backup restore, offline tests |
| Phase 2 — Central Shared MVP | P0 | Central FastAPI/PostgreSQL, SSO, Teamspace, ACL, Publish, search, audit | cross-user authorization negative tests and index leak tests |
| Phase 3 — Collaboration | P1 | Yjs/Hocuspocus, comments/mentions, versions | simultaneous edit / revocation / reconnect consistency |
| Phase 4 — Enterprise Templates | P1-P2 | Catalog admin workflow, role-linked suggestion, shared templates, advanced views | approval logs, version migration, team permission tests |
| Phase 5 — Approved AI | P2-P3 | Local/on-prem model adapter, RAG evaluation, automation approval | ACL retrieval, faithfulness, citation evaluation, no egress |

Current executable code covers **Phase 1A only**. All P0 central components remain planned/unimplemented.

## Phase 1A acceptance checklist
- ≥15 original templates with department/job family/job role metadata
- Template filter and fields visible in offline Local UI
- Save/open/update Local SQLite; revision mismatch returns HTTP 409
- Host/Origin and JSON constraints; no upload/media/AI/Publish endpoints
- No external JavaScript/CSS/CDN dependencies
- All tests use fake data; no sensitive fixtures or credentials

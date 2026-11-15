# Starter GitHub Issue Definitions — Phase 0 v0.4

**No GitHub issues have been created; use the approved internal corporate repository and human review.**

## GOV-001 — Corporate security and environment constraints
**Owner** Security/TPM; **Reviewer** corporate IT/security.
**Scope** [VERIFY] GitHub host, allowed software/AI tools, endpoint packaging, approved intranet servers/SSO, licenses, artifact classification and permitted data storage.
**AC** Record approvals or blockers with dates and responsible roles; never invent internal endpoints.
**Gate** G0.

## ARCH-001 — Hybrid trust boundaries and ADR
**Owner** Architect; **Review** Security/Product.
**Scope** Map Local, Publish and Shared data flow, identify canonical stores, draw service interfaces, choose P0 versioning vs P1 CRDT boundary.
**AC** ADR-0003 approved; no automatic local-to-shared sync; failure/rollback flow explicit.
**Gate** G1.

## ACL-001 — Permission policy specification and negative tests
**Owner** Identity/Permission; **Review** Security/QA.
**Scope** Role matrix, workspace membership, page inheritance, explicit DENY, revocation, 404 existence concealment, Search/Attachment/WS/AI enforcement points.
**AC** ACL vectors reviewed and mapped to API test harness; cross-team denial demonstrated with synthetic fixtures.
**Gate** G1/G3.

## DAT-001 — Domain model and evolution contracts
**Owner** Data; **Review** Backend/Security.
**Scope** Local SQLite and central PostgreSQL schemas, revision immutability, search outbox, publish idempotency, migration/backup.
**AC** Unique constraints/indexing/migration strategy reviewed; binary Yjs future compatibility recorded.
**Gate** G1.

## API-001 — Contract and concurrency spec
**Owner** Backend; **Review** Frontend/QA.
**Scope** API v1 schemas, standard errors, ETag conflicts, paginated search, Publish copy, ACL audit, WS capability future route.
**AC** Machine-checkable OpenAPI design planned and 409/401/403/404 failure semantics agreed.
**Gate** G1.

## SRCH-POC-001 — Korean Search feasibility
**Owner** Search; **Review** QA/Security.
**Scope** native FTS vs approved analyzer, permission filter, 1/2/3+ syllables, mixed English/Korean terms.
**AC** synthetic corpus and Precision@k/Recall@k plus p95 results documented; ACL query filter tested.
**Gate** before G3.

## LIC-001 — Dependency, license, packages and code transfer
**Owner** Release/Security; **Review** corporate IT/Legal.
**Scope** Hocuspocus4/Tiptap OSS/Yjs and optional extensions, internal mirror, license matrix, SBOM and CI runner isolation.
**AC** allowlist and official version requirements captured; unapproved components blocked.
**Gate** G0/G1.

# Decision Register — v0.4

| ID | Decision | Status | Rationale / revisit |
|---|---|---|---|
| DEC-001 | Local workspace for a personal PC | Active | Shared deployment is a separate proposal |
| DEC-002 | Source and synthetic tests in Git | Active | Keep app data outside Git |
| DEC-003 | Personal SQLite, Shared PostgreSQL | PROPOSED tech | low-maintenance local + central concurrency |
| DEC-004 | Explicit Publish central COPY | PROPOSED behavior | user control; no implicit sync |
| DEC-005 | No shared offline cache P0 | PROPOSED security | revocation/remanence risk; revisit later |
| DEC-006 | Tiptap OSS + custom comments/version features | PROPOSED | separate paid license terms |
| DEC-007 | Yjs/Hocuspocus from P1 | PROPOSED | protect P0 data integrity before CRDT |
| DEC-008 | SSO/OIDC + server RBAC/ACL | REQUIRED principle | provider and permissions [VERIFY] |
| DEC-009 | Local/approved internal AI only | CONFIRMED boundary | model use [BLOCKED until approval] |
| DEC-010 | Modular monolith central API, separate WS P1 | PROPOSED | limit operational complexity |
| DEC-011 | PostgreSQL search initially | PROPOSED | Korean search PoC before selection |
| DEC-012 | Private repo then Internal if policy permits | PROPOSED governance | broad inner-source only after review |

**Contradiction resolved**: `ADR-0001` single-PC-only goal is superseded; local-only *mode* stays supported but does not limit whole product.

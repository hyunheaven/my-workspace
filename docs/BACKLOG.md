# P0-First Prioritized Development Backlog v0.4

Use ticket IDs with unique acceptance, test and human reviewer. Priority ≠ effort/lead time.

| ID | Phase | Priority | Owner + reviewer | Acceptance / negative evidence |
|---|---|---|---|---|
| GOV-001 | 0 | P0 | TPM/Security | company scope, internal GitHub, AI tool and server policy recorded |
| ARCH-001 | 0 | P0 | Architect/Security | ADR-0003 and local/shared trust boundaries signed off |
| ACL-001 | 0 | P0 | Security+Identity/QA | role matrix and deny-precedence test vectors approved |
| DAT-001 | 0 | P0 | Data/Backend | SQLite/PostgreSQL schema, owner ID and immutable revision semantics reviewed |
| API-001 | 0 | P0 | Backend/Frontend | typed API/ETag/error/idempotency contracts approved |
| SRCH-POC-001 | 0 | P0 | Search/QA | Korean FTS alternatives measured with synthetic data |
| LIC-001 | 0 | P0 | Security/Release | library/Tiptap/Hocuspocus license, SBOM allowlist and offline packaging review |
| LOC-001 | 1 | P0 | Backend/QA | loopback launcher and no unauthorized network listeners |
| EDT-001 | 1 | P0 | Frontend/QA | Tiptap core editor JSON roundtrip and a11y |
| LOC-002 | 1 | P0 | Data/QA | SQLite atomic autosave, crash recovery, backup restore |
| IDN-001 | 2 | P0 | Identity/Security | corporate SSO integration and forbidden principal tests |
| SHR-001 | 2 | P0 | Backend/Security | teamspace CRUD & least privilege resource ACL |
| SHR-002 | 2 | P0 | Backend/QA | shared page CRUD, revision conflict and audit |
| PUB-001 | 2 | P0 | Local+Backend/Security | publish preview, idempotent central copy; original untouched |
| SRCH-001 | 2 | P0 | Search/Security | only authorized results, snippets, counts and links |
| REL-001 | 2 | P0 | Ops/QA | internal deployment+backup+restore rehearsal |
| WS-001 | 3 | P1 | Collaboration/Security | WS connect/write/read-only/revoke after ACL change |
| WS-002 | 3 | P1 | Data/QA | Yjs binary persistence, schema upgrade, restart recovery |
| COM-001 | 3 | P1 | Product/Backend | scoped comments/mentions, no notification leakage |
| DBV-001 | 4 | P2 | Data/Product | table, board, calendar and permission tests |
| AI-001 | 5 | P2 (blocked) | AI/Security | approved internal/local runtime, no outside calls |
| RAG-001 | 5 | P2 (blocked) | AI/Security | pre/post ACL checks, correct citations, hallucination evaluation |
| AUTO-001 | 5 | P3 (blocked) | Agent/Security | scoped tools, human approval, audit/rollback |

## First issue sequence
`GOV-001 → ARCH-001 + ACL-001 → DAT-001 + API-001 → SRCH-POC-001 + LIC-001 → LOC-001`.
Build branch work only after relevant gate and approval. No automatic GitHub Issue creation performed by this packet.

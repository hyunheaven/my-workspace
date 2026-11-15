# Requirements → Architecture → API → Test Traceability (v0.4)

| Requirement | Architecture contract | Data / API | Acceptance tests | Priority |
|---|---|---|---|---|
| Offline Personal Page | local loopback + SQLite | local_pages, /local/pages | LOC-01/02/03 | P0 |
| Explicit Publish | Copy-on-publish, idempotency | publish_requests, POST /publishes | PUB-01/02 | P0 |
| SSO Workspace membership | Central Identity & Permission boundary | users/memberships, /me /workspaces | SSO-01 ACL-01 | P0 |
| Team-page ACL inheritance | Server RBAC + ACL | page_acl, /pages/{id}/acl | ACL-02/03/04 | P0 |
| Shared CRUD | PostgreSQL canonical page JSON rev | pages/revisions, PATCH If-Match | DAT-01 | P0 |
| Shared Search | permission filtered query + index outbox | search_documents/outbox, /search | SRCH-01/02 ACL-01 | P0 |
| Files/Audit | linked authorization and append audit | attachments/audit, download /audit | SEC-01 REL-01 | P0 |
| Realtime editor | short-lived WS scope + Yjs binary | collab_documents, /collab/capability | P1 WS test suite | P1 |
| Comment/Mention | permission-aware notification | deferred schema/API | P1 scenario tests | P1 |
| Advanced DB views | record-scoped schema and views | deferred contract | Phase4 integration | P2 |
| AI RAG and Writing | approved Model Gateway + ACL double-check | deferred AI contract | P2 retrieval/source tests | P2 |
| Automation | restricted tools and approval queue | deferred | P3 audit/approval | P3 |

Missing API/test design is **not** silently implemented. New feature PRs must update this mapping.

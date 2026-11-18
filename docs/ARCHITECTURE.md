> **이전 설계안** · 현재 앱은 [개인 PC용 로컬 작업 공간](../README.md)입니다. 이 문서의 공유 기능은 별도 서버를 전제로 한 설계안입니다.

# System Architecture — v0.4

## 1. Logical context
```mermaid
flowchart TB
  LC[Windows Local Client
React/Vite/Tiptap] --> LA[Local FastAPI
127.0.0.1]
  LA --> LDB[(SQLite Local
Private)]
  LA --> LFS[(Local Files)]
  IW[Shared Web
React/Vite/Tiptap] --> GW[Internal HTTPS Reverse Proxy]
  LC -. Shared online mode .-> GW
  GW --> API[Central FastAPI
Policy Enforcement]
  API --> PG[(Central PostgreSQL
Shared Source of Truth)]
  API --> AFS[(Approved Internal Attachments)]
  API --> IDX[(Authorized Search Index)]
  API --> SSO[SSO/OIDC]
  GW -. P1 only .-> WS[Yjs/Hocuspocus]
  WS --> API
  WS --> PG
  API -. P2 approval only .-> AI[Internal Approved AI/RAG]
```

## 2. Boundaries
- **Local trust zone**: process scoped to Windows login; local UI via loopback; SQLite DB and local files. No inbound LAN listener; no default cloud, automatic remote sync or data telemetry.
- **Shared deployment zone**: central HTTPS endpoint, user-authenticated and policy-enforced CRUD, storage, search and audited administration. Shared web UI can be accessed by approved staff without installing a local app.
- **P1 collaboration zone**: Hocuspocus must not become a backdoor to central documents. Authenticate at connection, authorize read/write action, revoke active connections if ACL changes, rate-limit/revalidate and persist Yjs binary state.
- **P2 AI zone**: retrieval only after ACL filter; permission check repeated before content is returned and prompt constructed.

## 3. Module map (Modular Monolith + isolated WS service)
Central FastAPI module boundaries: `identity`, `workspaces`, `pages`, `blocks`, `permissions`, `files`, `revisions`, `search`, `audit`, `publishing`, `health`. Shared repository/type packages describe contracts, **not** security source of truth. `collaboration` Node/Hocuspocus process becomes separate only at P1. Search starts as an API module + PostgreSQL index; no independent search service in MVP unless PoC proves a need.

## 4. Publishing data flow
1. User chooses explicit Publish in local app, previewing complete page and linked attachment list.
2. Local UI obtains approved identity provider session, selects target workspace, checks current destination rights and classification.
3. Local app serializes a **copy** and submits HTTPS API with opaque idempotency key; validate payload and attachments; server rechecks membership and destination rights.
4. Server writes central page, immutable initial revision, provenance without leaking private paths, audit event and search-outbox in transaction; binaries staged/committed with cleanup rules.
5. Server returns new central page ID; local original remains local. Errors/timeout require idempotent status resolution, never blind retry duplication.
6. Sharing is not bidirectional sync; subsequent edits on the two copies diverge intentionally until a later approved import/merge feature.

## 5. Shared write/read flows
- **P0 edit**: GET -> `revision`/ETag -> PATCH with `If-Match` -> optimistic transaction; 409 conflicts shown to user. Every read and write checks central ACL server-side.
- **P0 search**: query user-visible doc set; SQL/FTS filters by authorized resource IDs; materialized snippets built only after filter; no unauthorized result counts or titles.
- **P1 collaborative**: Hocuspocus WS token scoped to document and role; central ACL service authoritative; raw Yjs binary persisted with versioned snapshots; side effect queue triggers content projection/reindex.
- **P2 RAG**: index chunks tagged by source doc + ACL/version; retrieval filtered by current permissions at query time, revalidated before model context and answer. Deny tombstoned/revoked resources.

## 6. Architectural risks and alternatives
| Option | Why selected / excluded | Gate |
|---|---|---|
| React/Vite shared UI | lean local and shared clients and common editor | Vite/CSP/offline build PoC |
| SQLite local + PostgreSQL central | local low-maintenance and central concurrency | migration, backup and authorization tests |
| Hocuspocus/Yjs P1 | mature CRDT real-time framework; separate process/operational cost | concurrency/licensing PoC |
| Dedicated microservices now | reject until scaling/coupling evidence | defer |
| Shared SQLite via NAS | reject concurrent network DB access | SQLite official guidance |
| Shared offline support in P0 | reject due to revocation and cache data-remanence risk | later Security ADR |

## 7. Deployment topology (proposed)
Local: Windows package (launcher + UI bundle + FastAPI/SQLite). Shared deployment: reverse proxy/TLS, central API, PostgreSQL backups, approved file storage, SSO, logging. Web assets/self-hosted fonts bundled; outbound network deny except configured services. Central runtime may listen on an approved interface **behind** network controls; local runtime remains loopback-only.

## 8. Open questions
Endpoint ownership, HA/DR, TLS certificate handling, SSO provider/identity groups, security labels/retention, operational owners, mobile/browser policy, network proxies [확인 필요].

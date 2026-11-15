> **v0.5 안내:** 아래 문서는 v0.4 Hybrid Target 설계 자료입니다. 실행형 PoC 및 보안 제한의 우선 적용 기준은 [`SECURE_FEATURE_POLICY.md`](SECURE_FEATURE_POLICY.md), [`TEMPLATE_LIBRARY_SPEC.md`](TEMPLATE_LIBRARY_SPEC.md), [`DEVELOPMENT_ROADMAP_v05.md`](DEVELOPMENT_ROADMAP_v05.md)입니다. 모든 첨부·미디어·외부 연동/Export 언급은 현 시점에서 비활성화되며 승인 전 구현하지 않습니다.

# Development Roadmap — v0.4 (phase-gated, no calendar promise)

## Phase 0 — Requirements, policy, risks, contracts
**P0 needed:** corporate host/network/security/AI policy, PRD, threat model, ADR-0003, local/shared ownership, ID mapping, API, ACL decision table, Korean search baseline, OSS/license/SBOM. **Exit G0/G1:** recorded architecture and approval boundaries, synthetic negative test fixtures and backlog with owners.

## Phase 1 — Common Platform + Local Workspace (P0)
React/Vite/Tiptap shared packages, typed client contracts, local launcher, FastAPI loopback, SQLite revisioned pages/tree/autosave, local search, backup/restore, local vs shared UI context. **Exit G2:** works offline, no egress, no lost saves, migration/restore pass.

## Phase 2 — Central Knowledge MVP (P0)
Approved central FastAPI/PostgreSQL/SSO, Teams/Workspaces, membership/ACL, Shared page CRUD+optimistic revisions, explicit Publish copy, central search/filter, audit and backup, intranet web. **Exit G3:** every cross-team negative authorization test passes; permission revoke/search consistency and restore proven.

## Phase 3 — Real-time Collaboration (P1)
Yjs/Hocuspocus, presence, read-only/active revocation, comment/mention service, document history and recovery; binary persistence and disruption tests. **Exit G4:** concurrent edits, server restart, network flap, cursor presence isolation, no cross-team leakage.

## Phase 4 — Advanced Workspace (P2)
Database table and view types (Board/Calendar), formula/relation/rollup, project/task links, templates/import-export, keyboard improvements. Exit: schema and data permissions validated, UX reviewed.

## Phase 5 — Approved Enterprise AI + Automation (P2/P3)
ModelGateway abstraction, local/internal LLM, ACL-filtered Hybrid Search + RAG, citation and AI edit diff/approval, scoped tool use, approval workflows. **Exit G5:** model/license approved, RAG evaluation and prompt-injection negative tests, monitoring+human approval.

## Dependencies / priority
`Identity + ACL + shared data model` precedes `Shared Search` and `Real-time WS`. `Local publish` depends on `shared workspace create`, `ACL`, `idempotency`. `Collab Yjs` depends on durable revisions & snapshot policy. `AI` depends on robust permission filtering, retrieval metrics and approved model. Distinguish **feature priority P0-P3** from **Phase number 0-5**.

## Measures (targets only after baseline)
- P0: unauthorized access test pass count / total; save integrity; search index lag; backup recovery success.
- P1: concurrent doc convergence, lost update count, post-revocation WS write prevention, crash recovery.
- P2/AI: Retrieval Recall@k, citation accuracy, faithfulness, refusal on insufficient evidence, latency, egress audit.
- Establish actual p50/p95 thresholds after user count, page count, file size, workstation and server specs known.

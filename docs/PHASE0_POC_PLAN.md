# Phase 0 Technical Proof-of-Concept Plan — v0.4

The following are **synthetic-data PoCs**, not production deployment. All executables, downloads, runners and network configurations must follow corporate policy; work in an authorized sandbox or with public components only until approved.

## POC-01: Local offline editor persistence
- Goal: one React/Tiptap JSON page roundtrip via Local FastAPI/SQLite with crash/restore and zero unauthorized egress.
- Compare: local loopback API vs native IPC if endpoint policy blocks loopback.
- Evidence: startup network listing, 20+ create/save/restart test cases, checksum validation, migration rollback.
- Exit: no lost acknowledged saves, no external request, no LAN listening.

## POC-02: Shared central ACL and search
- Goal: 2 synthetic teams x 3 roles x 20 documents plus explicit deny descendants; PostgreSQL/FastAPI test harness.
- Evidence: `tests/spec/permission_vectors.example.json` plus property-based cross-team tests, result-count/snippet/link leak check, role revocation without re-login, search index lag test.
- Exit: every forbidden action and metadata exposure denied; auditable results.

## POC-03: Korean search quality
- Goal: compare PostgreSQL native FTS, approved trigram extension and optional Korean analyzer on controlled Korean/English documents.
- Evidence: Precision@k, Recall@k and p95 latency; simple one/two syllable queries, compound technical terms, typo cases and mixed-language queries.
- Exit: qualitative/quantitative fit documented; approved extension footprint and safe migration path.

## POC-04: Publish copy and idempotency
- Goal: local page with 2 attachments, user preview → SSO -> central copy, timeout/retry, failure rollback.
- Evidence: original local ID unchanged, exactly one central document on retry, no leaked local filesystem path, no orphan attachment on reject.
- Exit: DB transaction+outbox consistency and reproducible rollback.

## POC-05: Realtime feasibility (P1 design only)
- Goal: Hocuspocus/Yjs concurrent edits, canonical binary persistence, active WS revocation, process restart and editor schema drift.
- Evidence: separate Node runtime/license/dependency assessment, 2/5/N-client convergence logs, restart and storage failure cases.
- Exit: correctness/security/operation trade-off recorded; *does not* unblock deployment without P1 gate.

## POC-06: Software supply chain & packaging
- Goal: license/SBOM for Tiptap OSS/paid extensions/Yjs/Hocuspocus/SQLite/PostgreSQL; company dependency mirror readiness.
- Evidence: version manifest, license obligations, approved OS/runtime/Node/Python executables, scanned packages, internal GitHub runner model.
- Exit: security+legal/IT signoff fields populated, or BLOCKED clearly documented.

## Evidence template per PoC
`PoC ID | environment classification | target versions | synthetic dataset seed | command/test method | metric/threshold | observed result | limitations | owner | reviewer | policy signoff/status`.

## Decision logic
Any failure in POC-02 ACL is a **hard blocker** for Shared MVP. Unapproved software is not installed as a workaround. If Hocuspocus is blocked, P0 optimistic concurrency remains available; reassess P1 alternative via an ADR. If Korean FTS is poor, choose an approved analyzer before indexing production shared pages.

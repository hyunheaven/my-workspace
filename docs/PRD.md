> **v0.5 안내:** 아래 문서는 v0.4 Hybrid Target 설계 자료입니다. 실행형 PoC 및 보안 제한의 우선 적용 기준은 [`SECURE_FEATURE_POLICY.md`](SECURE_FEATURE_POLICY.md), [`TEMPLATE_LIBRARY_SPEC.md`](TEMPLATE_LIBRARY_SPEC.md), [`DEVELOPMENT_ROADMAP_v05.md`](DEVELOPMENT_ROADMAP_v05.md)입니다. 모든 첨부·미디어·외부 연동/Export 언급은 현 시점에서 비활성화되며 승인 전 구현하지 않습니다.

# Product Requirements Document — v0.4

## 1. Problem / success
Personal notes, team project documents and technical knowledge are fragmented. Product should enable local-first authoring, deliberate publication, controlled organization-wide discovery and eventual collaboration without sending company content to external systems. This is a goal; no current deployment measurements exist.

### Personas
- **Personal author**: edits local/private notes offline; no central sync unless explicitly publishes.
- **Team contributor**: creates/edits shared team pages with granted permissions; uses central search.
- **Knowledge consumer**: read-only access to permitted pages and citations.
- **Team admin/owner**: manages membership, ACL and audit within delegated scope.
- **Security/IT operator**: enforces corporate SSO, system controls, backups, retention.

## 2. P0 workflows (required)
**P0-U1 Personal**: launch local app → create page/tree/block document → autosave → restart and read offline → backup/restore verified. Local DB remains on device.

**P0-U2 Share a local page**: explicit `Publish to Shared` → choose teamspace/destination and preview content/attachments → show destination ACL and data classification → confirm → new shared document ID/revision created centrally → personal original unchanged. Retry with idempotency key; on failure no misleading success state.

**P0-U3 Team knowledge**: user signs in via approved SSO → choose authorized teamspace → create/read/edit pages within policy → shared search returns only authorized titles/snippets → audit events tracked.

**P0-U4 Controlled access**: owner adds member/editor/viewer; effective roles inherited unless explicit narrower override; non-members cannot discover titles, attachments, presence or search hits. Test revocation without requiring a new login.

**P0-U5 Shared edit without Yjs**: edit while online with revision/ETag checks; when another user updates concurrently, return 409 and offer reload / compare / manual merge; never overwrite silently.

## 3. Prioritization
| Item | Priority | Acceptance |
|---|---|---|
| Local editor/tree/save/search/backup | P0 | offline deterministic E2E roundtrip |
| Teamspaces/members/SSO/ACL | P0 | all cross-tenant and role-negative tests pass |
| Central page CRUD/version/search/audit | P0 | index and ACL revocation correct; recoverable revisions |
| Publish copy/preview/confirm | P0 | local original unchanged; no implicit sync |
| Shared Web view | P0 | central-only pages, no offline editing |
| Yjs/Hocuspocus realtime + presence | P1 | concurrent simulation & revocation/restart passes |
| Comments/mentions/version diff | P1 | reviewer/workflow and retention verified |
| Project database views/relation/rollup | P2 | typed field validation and migration tests |
| AI Writing/RAG | P2 (approved only) | permission and citation eval pass |
| Agent workflows | P3 (approved only) | least privilege, dry-run, human approval, audit |

## 4. Explicit nonfunctional requirements
- Authentication: SSO/OIDC only for Central. Local mode uses permitted OS identity/data protections; do **not** claim this protects against local admin compromise.
- Isolation: `Private ≠ Shared`; no shared offline persistent cache in P0. Browser cache behavior to be verified at packaging time.
- Authorization: deny-by-default, consistent across API/index/attachments/WS/AI and tenant boundaries.
- Integrity: atomic versions, ETag conflict handling, confirmed backup/restore and migration rollback.
- Accessibility: keyboard navigation, screen-reader labels, visible sync/failure states.
- Operational: audit trail for ACL, publish, deletion, restores; metrics must not contain content or secrets.
- Localization: Korean UI and Korean/English search benchmark; performance targets after scale/PC profile confirmed.

## 5. Release-specific acceptance
**Local release**: no network dependency; create/edit/reopen/restore; tested backup; no outside listener.
**Shared P0 release**: SSO/ACL mandatory; signed-off cross-team negative tests; authorized central search; revocation and log audit; server backup/restore rehearsal.
**Collab P1 release**: no data loss with two clients/reconnect; no stale write after revoked access.

## 6. Assumptions / open issues
Deployment count, company SSO, endpoint policies, license allowlist, data classes, retention/backup ownership and concurrency are **[확인 필요]**. No actual corporate approval has been granted in this document.

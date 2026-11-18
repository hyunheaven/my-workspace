## v0.8 — Marketplace intake guardrail
- Treat third-party *free* as a price label, not as a license to republish or bulk export.
- Never scrape/copy Marketplace template bodies, media, unique page design, paid content or creator assets into repository.
- Author differentiated original templates from general business processes; prefer reusable fields, acceptance criteria and relevance to department/role.
- For any proposed third-party template require an attributable source, explicit grant to redistribute in a separate application, legal/security review, and a PR. No automatic Marketplace sync or remote template fetch.
- Static catalog remains immutable at runtime, without remote download, uploads or external redirects. Original template text never contains secrets.

# AGENTS.md — My Workspace

## Mission
Personal workspace for organizing documents, tasks and schedules on a local Windows 11 PC. Prioritize original, reusable templates. Any future shared workspace is a separate deployment.

## Non-negotiable requirements
1. Use **synthetic and public test data only** in fixtures and tests. Keep private documents, credentials and other sensitive data out of source control and shared development tools.
2. Default deny: audio, video, recording, media capture, camera/microphone, file uploads, external URLs/embeds, arbitrary scripts/macros, external AI, telemetry and download/export/remote connectors. New capabilities need security analysis and explicit human approval.
   - v1.2 local transfers: explicit UTF-8 Markdown and CSV text import/export. Read files in the browser, validate structured payloads over loopback, and keep imported markup inert. Export only after a user action. Arbitrary attachments and remote transfer stay out of scope.
3. Never advertise **zero exfiltration risk**: same-user local file read, clipboard, screenshots, browsers, malware and GitHub activity require device and operating-system controls.
4. Local private docs in local SQLite; server-mode Shared docs are centrally authoritative only, never automatically published. Explicit preview/target/classification/ACL/confirmation required before Publish copy. Shared offline cache/edit excluded in P0.
5. Backend permission enforcement on Shared API, search, titles/snippets, attachment when approved, collaboration, AI/worker. All central features are unimplemented as of v0.5.
6. Templates are original, pre-reviewed, versioned. No unapproved third-party/proprietary Notion paid templates or plugin marketplace. Templates contain no private data.
7. GitHub for code, docs, synthetic fixtures, PR/Issues only, not operational Workspace data. No unapproved GitHub Actions or deployment. Verify repository visibility before publishing.
8. Orchestrator routes Architecture/Product/Security/Backend/Frontend/Data/QA/AI work; independent Security & QA reviews mandatory. AI agents do not self-approve, merge or deploy.
9. Security checks are in API, not only in UI. Host/Origin/size/schema validation; content displayed as plain text; all HTTP responses no-store, no camera/mic permissions, no media CSP. Do not claim these are complete DLP.

## Agent issue/PR workflow
`Requirement → Data Classification → Threat Model/Feature Allowlist → ADR/API/Schema → Implementation → Independent Negative Tests → Security Review → Human Approval`.

## Role handoffs
- Product Agent: template taxonomy, UX, prohibited features, acceptance.
- Security Agent: threat model, egress restrictions, data classification, review gate.
- Architect Agent: local/shared boundaries, future permission model, package provenance.
- Data Agent: versioned template fields, SQLite, migrations/recovery (later).
- Frontend Agent: text-only safe input, no media, accessibility.
- Backend Agent: strict schema and no unapproved outbound interfaces.
- QA Agent: 409 concurrency, negative paths, no external assets, test evidence.
- AI Agent: design-only for future features.

## Skills
Existing `skills/` are design playbooks, not live agents. Add `skills/template-safety/SKILL.md` for new template reviews.

## Release definition
Scope and tests documented; synthetic fixtures; zero unapproved media/network/AI routes; human PR review; Windows 11 verification for releases.

## 저장소 작업
- 원격 주소와 공개 범위를 확인하고 사용자가 요청한 저장소 작업만 진행한다.
- `git add` 후 `python scripts/check_before_commit.py`, `git diff --cached --check`, 수동 diff 리뷰를 통과해야 Commit한다.
- PR은 AI Agent가 제안하고 승인된 사람이 검토한다. `main` 직접 수정은 최초 초기화 외 금지한다.
- GitHub Issue, PR, 로그, Artifacts와 Test Fixtures에는 합성·공개 가능한 정보만 사용한다.

## v0.9 Integrated Core Implementation Gate
- Running local implementation now includes Dashboard, Page Tree, Project, Task Table/Board and Personal Calendar. Maintain invariant: **shared data still has no endpoint**.
- `services/local_api/workspace_store.py` owns SQLite schema, migration and transactional revision guards. Test old DB upgrades and cyclic moves; never add implicit remote sync.
- Task due dates appear as projection in Calendar feed. Do **not** create duplicate calendar events for them.
- Calendar all-day ranges are end-exclusive in API/DB; UI end date inclusive. Timed events must have explicit offsets, canonical UTC storage, local date projection.
- Display user-authored titles and descriptions with textContent, never innerHTML; no media/file/script fields without approved policy revision.
- Multi-Agent review: Data Agent checks foreign keys and schema; API Agent checks request/response contracts and 409; Frontend Agent checks accessibility and state transitions; Security Agent confirms network/feature denylist; QA Agent runs 19+ tests + approved browser E2E; Human Owner approves PR.
- Known limits: local single-user only, not a Notion clone, generic database properties and collaborative live editing deferred, Windows browser end-to-end testing outstanding.


## v0.11 Page-First Architecture Guardrails
- Build around Page/Block/Linked View primitives; keep Projects/Tasks/Calendar as reusable datasets, not independent UI-only concepts.
- SQLite migration must be additive and preserve all v0.9 documents, template fields, tasks, events and revisions. No implicit cloud sync.
- `page_blocks` uses an allowed list of text-only block types. No raw HTML, executable Markdown, SVG, media, embeds or file blocks.
- Canvas writes are atomic, `expected_revision` guarded, and reject duplicate block IDs, control characters, unsupported types and oversized payloads.
- Render document content with `textContent` or text inputs only; never set user text as `innerHTML`.
- Start Page is an original local onboarding page, not a reproduction of proprietary Notion text/tutorials/media.
- v0.11 is a Page Canvas proof of concept; **do not claim** production-grade rich editing, true nested blocks or inline database views, reliable multi-user synchronization, Yjs, SSO, AI, or shared deployment are implemented. A best-effort local debounce save is present and must be tested for errors and conflicts.
- QA gates: legacy SQLite migration, all prior tests, API negative tests, browser creation/save/reopen, offline asset policy, Windows 11 human test before GitHub publication.

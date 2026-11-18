> **이전 설계안** · 현재 앱은 [개인 PC용 로컬 작업 공간](../README.md)입니다. 이 문서의 공유 기능은 별도 서버를 전제로 한 설계안입니다.

# Security, Threat Model & Governance v0.4

## 1. Scope assumptions
Personal workspace data stays on the local PC. Any future shared deployment has its own storage, access and backup controls. Keep private documents and credentials out of Git and test fixtures.

## 2. Primary threats
| Threat | Impact | Control / validation |
|---|---|---|
| Insecure Direct Object Reference / ACL gap | cross-team disclosure | server authorization each endpoint; negative tenant tests |
| Search index/title/snippet leakage | metadata/content exfiltration | apply ACL before ranking/snippets/counts; cache key & ACL version |
| Unauthorized WS access or stale session | continuous post-revocation editing | central capability tokens, origin, read-only, active room eviction |
| Prompt injection / RAG privilege bypass | unapproved content exposure/tool misuse | retrieval filter, untrusted content, second authorization gate, no auto tool access |
| Attachment traversal, upload malware | endpoint/server compromise | opaque keys, path normalization, approved scan, MIME/size/format validation |
| Local loopback attack / CSRF | local data compromise | Host/Origin/CSRF, ephemeral local session, bind loopback only |
| Unauthorized egress/dependency updates | external data leak | configured network access, bundled assets, SBOM/signature, no CDN/telemetry |
| Inconsistent backups, lost updates | data loss | transactional revision, idempotency, outbox, restore rehearsal |
| Unauthorized GitHub/AI assistant access | proprietary source disclosure | private repo initially, least privilege, permitted AI tools only, synthetic fixtures |

## 3. Technical policy
- Central: OIDC/SSO, session expiration, service-to-service identity, secret vault, TLS; CSRF, CORS, CSP, HTTPS only.
- Authorization: RBAC + ACL + hierarchical inheritance defined in `ACCESS_CONTROL.md`; every worker, attachment download, websocket, search and model call checked.
- Shared response: no offline cache in MVP, no service worker cache of shared bodies; `Cache-Control: no-store`, browser/client behavior tested. No design can guarantee already-viewed content is erased from memory/screenshots.
- Data at rest: operating-system disk encryption, file ACL, backups and retention policy; app-level encryption only if approved/key managed.
- Logging: request/actor/resource IDs, decision, timing, policy version. No document payload, tokens, prompts or plaintext PII.
- AI: feature disabled until model, ingestion, embedding, RAG index, runtime and egress approved; red-team prompt injection and ACL leakage tests.
- GitHub: code only, secrets + dependency scanning within approved environment, protected main and human review. Self-hosted runners isolated and authorized.

## 4. Required approvals [확인 필요]
Future shared deployment: server infrastructure, firewall/DNS, OIDC/SSO, endpoint installation, internal model, Tiptap/Hocuspocus/library licenses, third-party dependency transfer, storage/data retention, backup/DR, threat review, audit access.

## 5. Security gates
G0 policy approval record → G1 threat model and ACL spec → G2 local offline control → G3 cross-team no-leak, revocation and backup tests → G4 WS resilience → G5 AI RAG grounding/evaluation.

## 6. Standards for review
OWASP Authorization Cheat Sheet, OWASP ASVS, NIST AI RMF GenAI profile, OpenID Connect Core, PostgreSQL RLS guide. See `REFERENCES.md`.

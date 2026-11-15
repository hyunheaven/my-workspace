> **v0.5 안내:** 아래 문서는 v0.4 Hybrid Target 설계 자료입니다. 실행형 PoC 및 보안 제한의 우선 적용 기준은 [`SECURE_FEATURE_POLICY.md`](SECURE_FEATURE_POLICY.md), [`TEMPLATE_LIBRARY_SPEC.md`](TEMPLATE_LIBRARY_SPEC.md), [`DEVELOPMENT_ROADMAP_v05.md`](DEVELOPMENT_ROADMAP_v05.md)입니다. 모든 첨부·미디어·외부 연동/Export 언급은 현 시점에서 비활성화되며 승인 전 구현하지 않습니다.

# Security, Threat Model & Governance v0.4

## 1. Scope assumptions
Local personal data stays on company Windows endpoints; shared data stays on approved company network/infrastructure. Company information-security and software intake approval are prerequisites. No confidential/proprietary material in external AI, public Git, personal cloud or unapproved runners.

## 2. Primary threats
| Threat | Impact | Control / validation |
|---|---|---|
| Insecure Direct Object Reference / ACL gap | cross-team disclosure | server authorization each endpoint; negative tenant tests |
| Search index/title/snippet leakage | metadata/content exfiltration | apply ACL before ranking/snippets/counts; cache key & ACL version |
| Unauthorized WS access or stale session | continuous post-revocation editing | central capability tokens, origin, read-only, active room eviction |
| Prompt injection / RAG privilege bypass | unapproved content exposure/tool misuse | retrieval filter, untrusted content, second authorization gate, no auto tool access |
| Attachment traversal, upload malware | endpoint/server compromise | opaque keys, path normalization, approved scan, MIME/size/format validation |
| Local loopback attack / CSRF | local data compromise | Host/Origin/CSRF, ephemeral local session, bind loopback only |
| Unauthorized egress/dependency updates | external data leak | allowlisted intranet, bundled assets, SBOM/signature, no CDN/telemetry |
| Inconsistent backups, lost updates | data loss | transactional revision, idempotency, outbox, restore rehearsal |
| Unauthorized GitHub/AI assistant access | proprietary source disclosure | private repo initially, least privilege, permitted AI tools only, synthetic fixtures |

## 3. Technical policy
- Central: OIDC/SSO, session expiration, service-to-service identity, secret vault, TLS; CSRF, CORS, CSP, HTTPS only.
- Authorization: RBAC + ACL + hierarchical inheritance defined in `ACCESS_CONTROL.md`; every worker, attachment download, websocket, search and model call checked.
- Shared response: no offline cache in MVP, no service worker cache of shared bodies; `Cache-Control: no-store`, browser/client behavior tested. No design can guarantee already-viewed content is erased from memory/screenshots.
- Data at rest: company-managed disk encryption, file ACL, backups and retention policy; app-level encryption only if approved/key managed.
- Logging: request/actor/resource IDs, decision, timing, policy version. No document payload, tokens, prompts or plaintext PII.
- AI: feature disabled until model, ingestion, embedding, RAG index, runtime and egress approved; red-team prompt injection and ACL leakage tests.
- GitHub: code only, secrets + dependency scanning within approved environment, protected main and human review. Self-hosted runners isolated and authorized.

## 4. Required approvals [확인 필요]
Corporate: Internal GitHub type/organization, server infrastructure, firewall/DNS, OIDC/SSO, endpoint installation, internal model, Tiptap/Hocuspocus/library licenses, third-party dependency transfer, storage/data retention, backup/DR, threat review, audit access.

## 5. Security gates
G0 policy approval record → G1 threat model and ACL spec → G2 local offline control → G3 cross-team no-leak, revocation and backup tests → G4 WS resilience → G5 AI RAG grounding/evaluation. No claims of corporate compliance until verified by authorized personnel.

## 6. Standards for review
OWASP Authorization Cheat Sheet, OWASP ASVS, NIST AI RMF GenAI profile, OpenID Connect Core, PostgreSQL RLS guide. See `REFERENCES.md`.

> **이전 설계안** · 현재 앱은 [개인 PC용 로컬 작업 공간](../README.md)입니다. 이 문서의 공유 기능은 별도 서버를 전제로 한 설계안입니다.

# Test Matrix / Definition of Done — v0.4

## P0 acceptance test matrix
| ID | Scenario | Passing criterion |
|---|---|---|
| LOC-01 | Windows local app offline | create/edit/reopen/recover without network/unauthorized egress |
| LOC-02 | loopback surface | no LAN listener; Host/Origin/CSRF attacks blocked |
| LOC-03 | backup/migration crash | restored content hashes match, no partially committed revision |
| DAT-01 | concurrent P0 edits | stale ETag rejected, manual merge offered, zero silent lost updates |
| PUB-01 | publish page with attachments | review + explicit confirmation, one central copy on retry, local original unchanged |
| PUB-02 | publish rejected | no central partial metadata/ghost page, no false success |
| SSO-01 | invalid/stale principal | blocked, no fallback login bypass |
| ACL-01 | team A → team B | no titles/search/snippets/attachments/resource existence leaked |
| ACL-02 | viewer/commenter/editor matrix | forbidden update, ACL change, delete rejected via API and WS where applicable |
| ACL-03 | inheritance/explicit deny | nearest override and deny precedence match spec |
| ACL-04 | revocation | REST/search access blocked immediately; cache invalidated; WS tested P1 |
| SRCH-01 | create/update/delete/restore | no stale inaccessible result; index rebuild deterministic |
| SRCH-02 | Korean/English corpus | record recall/precision/latency and known query failure modes |
| REL-01 | server backup | PostgreSQL + attachments restore to isolated environment and integrity verify |
| SEC-01 | upload/XSS/CSRF/path traversal | all malicious synthetic payloads rejected/neutralized |
| SEC-02 | supply chain | SBOM, dependency licenses, no secrets or unapproved egress |

## P1 collaboration tests
- 2, 5, N clients edit same page concurrently: converge to equivalent Yjs state; editor schema valid after merge.
- Server process restart during edit: persistence state and replay behavior observed; documented loss window within approved RPO.
- Reconnect with stale capability/ACL revoked: denied; no post-revocation write.
- Viewer sends handcrafted update via WS: rejected.
- Deletion while 2 users active: room invalidation and search/attachment revocation.
- Upgrade of editor schema and Yjs binary restore from backup.
- Presence metadata is scoped to authorized viewers only.

## P2 AI tests
Synthetic corpus with deliberately overlapping access: denied-source retrieval 0; unauthorized citations/snippets 0; record Recall@k, faithfulness and citation accuracy. Test prompt injection as hostile source content, unsafe tool calls, and rejected AI edits leaving originals untouched.

## Review rubric
For every PR: unit + integration + representative E2E, negative permission tests if data touched, failure and rollback demonstration, license/dependency review, clean diff, independent human code review, updated docs/ADR. Never self-certify as security approved.

## Baselines / targets
p95 API latency, search latency, average document size, concurrent users, retention, backup RPO/RTO not set until [확인 필요] capacity and business requirements. Security correctness is release blocker, not optional performance tradeoff.

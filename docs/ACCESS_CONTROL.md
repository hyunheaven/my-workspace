> **이전 설계안** · 현재 앱은 [개인 PC용 로컬 작업 공간](../README.md)입니다. 이 문서의 공유 기능은 별도 서버를 전제로 한 설계안입니다.

# Access Control Specification — v0.4 (draft)

## 1. Scope and trust boundaries
Local PC: OS account and local filesystem controls (not a replacement for device security). Shared: SSO/OIDC authentication, server-side RBAC + resource ACL + explicit deny; cross-team isolation. PostgreSQL RLS may be added as defense in depth but cannot replace application checks.

## 2. Roles and matrix
| Role | read | edit | comment | share/manage ACL | delete/restore | administer workspace |
|---|---:|---:|---:|---:|---:|---:|
| Owner | Y | Y | Y | Y | Y | Y |
| Admin | Y | Y | Y | delegated only | delegated only | delegated only |
| Editor | Y | Y | Y | N | N by default | N |
| Commenter | Y | N | Y | N | N | N |
| Viewer | Y | N | N | N | N | N |
| No Access | N | N | N | N | N | N |

`Owner`, `Admin` operations are constrained by policy/data classification; do not allow arbitrary privilege escalation. Commenter exists as P1 workflow but action policy is specified early. A service account has no implicit human user permissions.

## 3. Effective permission policy (MVP proposal)
1. Validate SSO principal/session, account status, tenant/workspace identity, resource existence and classification.
2. Check user/group Workspace membership. **No membership → deny**, even if page ID guessed. Owner/delegated Admin within scope has inherited rights; policy denies may override.
3. Inherit closest parent grant within the same Workspace; apply page-specific explicit **DENY over ALLOW**. For v0.4 P0, narrower page overrides may *reduce* effective rights; capability to grant broader rights than workspace membership is disabled.
4. Resolve effective action rights from role matrix and explicit ACL, always with least privilege. Undefined states or invalid groups deny.
5. Re-evaluate on every read and mutation; attachments, search snippets, websocket tokens, presence and RAG do not get separate blanket permissions.

This is a **normative proposed algorithm**; final exception semantics need human security signoff before implementation.

## 4. Enforcement points
- REST: shared middleware authenticates, resource loader resolves scoped IDs and policy service authorizes per action; UI hiding is convenience, not access control.
- Search: filter authorized page IDs at data-query level **before** computing ranks/snippets/counts; verify results again before returning.
- Attachments: issue short-lived authorized download after checking linked page; no guessable raw storage URLs.
- WebSocket: authorize handshake and each requested document/write capability; read-only for Viewer; revoke active session on ACL or account change, avoid relying solely on token TTL.
- Background workers: identity-bearing jobs with authorization snapshot/version **and fresh revalidation** before exposing content or sending a notification.
- AI: retrieve only authorized chunks, recheck live ACL and document revision before context assembly and citation output; no hidden title leakage.

## 5. SQL defense in depth
RLS enabled where feasible; app DB role must lack SUPERUSER/BYPASSRLS and not be the owning role. Consider `FORCE ROW LEVEL SECURITY` for owning roles where appropriate. Review SECURITY DEFINER functions, migration privilege, connection pooling identity propagation, and administrative exception paths separately.

## 6. Test vectors (required)
- User in Team A cannot guess/read/list/search/get snippets/attachments/collab-presence of Team B pages.
- Viewer cannot PATCH nor send WS writes; Commenter cannot edit document content.
- Editor cannot change ACL or share document outside their approved workspace.
- Direct child explicit deny overrides inherited read grant; parent permission changes propagate to descendants.
- Revocation immediately blocks new REST/search requests and terminates/restricts existing WS; still-open screen must cease further writes and clear in-memory content as practical.
- ACL changes invalidate stale search/AI cache outputs; no residual titles or counts in other tenants.
- Deleted/restricted pages and attached files not accessible via old URL.
- Unexpected claims/groups, stale tokens and missing resource IDs fail closed without exposing sensitive metadata.

## 7. Auditing
Record actor ID, action, target opaque ID, decision allow/deny, policy version and timestamp; do not store document body, snippets, model prompts or credentials in audit trail. Security audit retention [VERIFY].

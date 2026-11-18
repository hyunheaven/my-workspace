> **이전 설계안** · 현재 앱은 [개인 PC용 로컬 작업 공간](../README.md)입니다. 이 문서의 공유 기능은 별도 서버를 전제로 한 설계안입니다.

# REST/WS API Contract — v0.4 preliminary

API is **proposed**, not implemented. Base path shared: `/api/v1`. Local service uses separate loopback base URL with no shared identity assumptions; shared frontend uses shared deployment HTTPS origin.

## Central endpoints
| Method/path | Action | Authorization | Idempotency/concurrency |
|---|---|---|---|
| GET `/me` | current principal | authenticated | no sensitive claims exposed |
| GET `/workspaces` | authorized workspace list | membership | filtered server-side |
| POST `/workspaces/{id}/members` | add member | Owner/Admin delegated | audit, request validation |
| GET `/workspaces/{id}/pages` | page tree/list | read, resource filter | cursor pagination |
| POST `/workspaces/{id}/pages` | create page | Editor+ or explicit create | idempotency key |
| GET `/pages/{page_id}` | read page | read | revision/ETag |
| PATCH `/pages/{page_id}` | update content | edit | `If-Match` required; 409/412 on stale |
| GET `/pages/{id}/revisions` | list revisions | read | immutable metadata |
| POST `/pages/{id}/restore` | restore revision | Owner/delegated | creates next revision + audit |
| POST `/pages/{id}/acl` | update ACL | delegated admin | require current `acl_version` |
| POST `/publishes` | Publish local copy | target create + confirmation | unique `Idempotency-Key` |
| GET `/publishes/{key}` | resolve timeout state | original actor only | safe retry |
| GET `/search?q=...` | knowledge search | read & field-level policy | filtered before snippets |
| POST `/attachments/init` | staged upload | target edit/create | size/type/scanner policy |
| GET `/attachments/{id}/download` | protected download | linked page read | short-lived response |
| GET `/audit` | delegated audit view | admin + compliance | redaction |
| POST `/collab/{id}/capability` | P1 WS capability | read or edit | short-lived, revocable |

## Local endpoints
`GET /local/pages`, `POST /local/pages`, `GET /local/pages/{id}`, `PATCH /local/pages/{id}`, `POST /local/backup/preview`, `POST /local/backup/commit`, `POST /local/restore/preview`, `POST /local/restore/commit`. Local requests require Host/Origin protection and a per-process/session CSRF token if HTTP; loopback alone is insufficient.

## Response and failure semantics
Standard JSON: `{"code":"PERMISSION_DENIED","message":"Access denied","request_id":"opaque"}`. Use `401` for unauthenticated, `403` for authenticated unauthorized where safe, `404` to avoid resource enumeration where required, `409`/`412` revision precondition conflicts, `422` validation, `429` limits and `503` service unavailable. Never return hidden titles/paths in errors.

## Page representation
```json
{
  "id":"uuid",
  "workspace_id":"uuid",
  "title":"Synthetic Test Document",
  "revision":3,
  "content_schema_version":1,
  "content":{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"Example"}]}]},
  "permissions":{"read":true,"edit":false,"share":false}
}
```
The `permissions` field is informational for UI; it never substitutes for server check.

## P0 vs P1
P0 shared edit uses full document revision + optimistic concurrency. P1 WS uses separate Yjs state and explicit migration/initialization rules; do not allow P0 PATCH to overwrite live Yjs collaborative content. Capability scopes and revocation depend on a central policy service.

## Privacy headers/protocol
Central HTTPS only with session-cookie `Secure/HttpOnly/SameSite` as permitted, CSRF defense for mutations, CORS locked to configured HTTPS origins, validation and size limits. WS over WSS behind approved proxy with Origin check, auth & per-resource permission. Shared responses `Cache-Control: no-store` where required, and offline service workers must not cache shared bodies (verify browser behavior). No direct database access from browser.

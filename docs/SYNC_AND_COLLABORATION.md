> **이전 설계안** · 현재 앱은 [개인 PC용 로컬 작업 공간](../README.md)입니다. 이 문서의 공유 기능은 별도 서버를 전제로 한 설계안입니다.

# Publish, Synchronization & Collaboration Design — v0.4

## Three distinct states
- **Local**: owned on PC. No network required. Edit and backup local only.
- **Shared P0**: new central document created by explicit publish or shared UI; online transactions and optimistic revision conflicts; no offline edit queue or shared persistent cache.
- **Collaborative P1**: a shared page is temporarily operated as Yjs document via approved Hocuspocus service; server state is authoritative with persisted binary.

## Publish as copy, not bidirectional sync
`LOCAL_DRAFT → PREVIEW_AND_DESTINATION_SELECTION → SERVER_AUTHORIZE → STAGE_ATTACHMENTS → COMMIT_CENTRAL_PAGE_AND_AUDIT → CONFIRM`. If upload fails or acknowledgment is lost, query by idempotency key. Central never reads local SQLite directly. Keep source local; explicit future republish or approved change import would be separately designed, never auto-sync.

## P0 concurrent write policy
`GET page rev=7` → `PATCH If-Match rev=7`; server atomically checks current revision. One writer succeeds rev=8, second gets `409/412` with safe conflict metadata, can reload/compare before retry. Never last-writer-wins silently.

## P1 Yjs/Hocuspocus constraints
- One Y.Doc per shared Page/Document domain. Serialize and persist actual Yjs update bytes, not reconstructed JSON.
- Track `document_name = opaque page UUID` internally; validate and bind to workspace ID and ACL before loading.
- Authenticate WS with a short-lived scoped token minted by central API, read-only for Viewers, reject unauthorized writes, validate Origin and rate/payload limits.
- On ACL revocation, disconnect or downgrade active sessions, prevent new updates, and purge ephemeral room access as policy allows. Test across server nodes.
- Persist canonical Yjs state with durable snapshots/checkpoints; `onStoreDocument` is debounced, so crash resilience requires explicit test, cadence policy and possibly durable update log. Hocuspocus hook alone is not a guarantee of zero data loss.
- Search projection jobs extract only after durable snapshot; index newest stable version. Deleted/ACL-revoked pages leave search immediately inaccessible even if index cleanup lags.
- Presence/awareness is transient and must not expose unauthorized collaborators.
- Backups restore binary state along with metadata; test multi-client rejoin and schema upgrade.

## Storage migration at P1 activation
Existing P0 page JSON revision is transformed into a **single initial Yjs state** once. Record migration generation; stop legacy full-document PATCH on active collaboration pages. Never repeatedly derive fresh Yjs state from JSON on reconnect.

## Out of scope until additional ADR
- Shared document offline content cache with transparent sync
- Cross-device personal document sync
- Filesystem/NAS shared SQLite database
- Public/cross-enterprise sharing

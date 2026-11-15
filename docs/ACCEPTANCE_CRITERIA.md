# Release Gate Checklist v0.4

## G0/G1 — Planning
- [ ] Product charter and P0 scope approved by product owner.
- [ ] Approved company GitHub, network/server/SSO/software/licensing policy recorded.
- [ ] ADR-0003, data owners, Publish semantics, no shared offline mode signed off.
- [ ] RBAC/ACL matrix + cross-team negative vectors reviewed.
- [ ] Korean search PoC and data sizing plan agreed.

## G2 — Local
- [ ] Local offline E2E and backup/restore.
- [ ] Loopback Host/Origin/CSRF and unauthorized egress tested.
- [ ] Page revision integrity across crashes.

## G3 — Shared
- [ ] SSO, explicit membership, page ACL, resource visibility.
- [ ] Search/snippets and attachments permission isolated.
- [ ] Publish copy idempotent; local source unchanged.
- [ ] Operational backup, logs and recovery tests.

## G4 — P1 Collaboration
- [ ] WS read/write/revocation tests.
- [ ] Yjs state convergence, persistence and recovery.
- [ ] Room presence scoped by authorization.

## G5 — AI
- [ ] Approved model endpoint/weights and licenses.
- [ ] ACL-filtered RAG, citation/faithfulness and injection tests.
- [ ] Explicit review/approval for AI changes.

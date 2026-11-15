---
name: permission-audit
description: Generate and review RBAC/ACL and cross-team negative permission test vectors for all content paths.
---
# Permission Audit
Input: role matrix, principal, team/workspace/page tree, action, ACL effect and policy version. Compute expected allow/deny using `docs/ACCESS_CONTROL.md` and verify REST/list/search/snippets/attachments/WS/AI/worker behavior. Include inherited DENY, revocation, stale session and ACL cache races. Raise any bypass as release-blocking. Use synthetic identities/documents only.

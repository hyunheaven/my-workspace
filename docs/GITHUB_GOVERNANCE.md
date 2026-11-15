# Internal GitHub Governance — v0.4

- Company GitHub only; type/host [VERIFY]. The connected consumer GitHub plugin is not automatically the approved enterprise endpoint.
- Repository `enterprise-ai-workspace`, Private at start; broad `Internal` visibility only after security/license/source classification approval.
- Monorepo and short-lived `feat/`, `fix/`, `docs/` branches; protected `main`; PR with approved reviewers. Independent Security review for ACL/WS/SSO/data/AI and network changes.
- Never commit SQLite DB, PostgreSQL dumps, local/shared attachments, real usage data, secrets, model weights, internal network diagrams or customer data.
- CODEOWNERS requires approved real teams; no fake accounts. GitHub Issues must use synthetic reproductions. Audit PR/Actions artifacts and logs.
- CI on approved isolated runner only. No workflow marketplace actions nor dependency download without company policy check.
- Version tags/releases deliver source artifacts and approved offline/install packages only. Deployment never auto-granted by a merged PR.

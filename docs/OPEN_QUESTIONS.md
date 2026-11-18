# Open Questions and Approval Dependencies — v0.4

| Question | Reason | Suggested owner | Blocks |
|---|---|---|---|
| GHES, managed enterprise cloud or other? repo permission/visibility, CI/runner? | source data boundary | IT/GitHub admin | real repo operations |
| Server hosting, firewall, DB backup and object storage approved? | data hosting/network feasibility | IT/Security | Phase 2 |
| SSO OIDC available, groups/claims, deprovision SLA? | identity correctness | IAM/Security | Phase 2 |
| What Windows versions and Python/Node packages should be supported? | local runtime | Endpoint Security | Phase 1 deployment |
| Allowed libraries/licenses: Tiptap OSS, Hocuspocus, Yjs, PostgreSQL extension? | legal/supply-chain | Legal/Security | dependency import |
| Team/workspace scale, attachments, retention, restricted data classes? | data design/capacity | Product/IT | sizing/retention |
| Shared view in browser or packaged local client required? | endpoint and UI needs | Product/IT | UX/build packaging |
| Korean tokenizer/extensions availability? | search viability | DB/QA | indexing design |
| Users may publish attachments/embedded data? classification requirements? | accidental data leaks | Data owner/Security | Publish feature |
| Internal models and model weights permitted and hosted where? | AI legal/security feasibility | AI/IT | Phase 5 |
| Shared offline policy may ever be allowed? | revocation/remanence | Security | future sync ADR |
| Performance, RTO/RPO, uptime and audit retention target? | testing/ops capacity | Operations/Product | release gates |

Update the ADR and PRD when these design questions are resolved.

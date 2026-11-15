# Approved Company GitHub Setup Checklist — v0.4

**This package does not create or modify a GitHub repository.**

- [ ] Corporate IT confirms GHES/Enterprise Cloud and approved Organization, repository classification, creation permissions and AI tool access.
- [ ] Select Private initially; confirm whether Internal is allowed and whether distribution has legal/licensing requirements.
- [ ] Import sanitized v0.4 docs/skills/Issue templates into company repo; inspect staged diff, `.gitignore` and generated artifacts first.
- [ ] Protect `main`, require PR/human review, prevent force pushes/deletion, configure code owners only for real teams, require status checks once approved.
- [ ] Disable unapproved Actions/plugins/webhooks; approve internal runner/data retention before CI.
- [ ] Create first G0/G1 Issues (`GOV-001`, `ARCH-001`, `ACL-001`, `DAT-001`, `API-001`).
- [ ] Record issue-specific data classification and link independent reviewers; no actual corporate data in external tools.
- [ ] Keep product personal SQLite and central PostgreSQL outside repository.

**Acceptance**: a reviewed docs PR in the authorized repo, no secrets/sensitive files, branch rules enabled, no unauthorized external transfer.

# Initial GitHub Issue Backlog — v0.5

| ID | Priority | Lead Agent | Task | Blocking gate |
|---|---|---|---|---|
| GOV-002 | P0 | Security/TPM | GitHub Enterprise Server/Cloud, policies and approvals verify | G0 |
| SEC-010 | P0 | Security | Sensitive capability denylist and DLP threat model | G0 |
| TMP-001 | P0 | Product/UX | Dept/job family/role ontology & user journeys | — |
| TMP-002 | P0 | Backend | Versioned approved template schema & validation | TMP-001 |
| TMP-003 | P0 | Frontend | Template catalog UI; role filters; authoring | TMP-002 |
| LOC-010 | P0 | Backend/Data | Local SQLite CRUD, revisions, backup/restore | TMP-002; backup TBD |
| SEC-011 | P0 | QA/Security | Negative tests for media/upload/egress and template injections | SEC-010 |
| UI-010 | P0 | Frontend | React/Tiptap migration after package approval | GOV-002 |
| SHR-010 | P0 | Architecture/Identity | Central SSO/ACL and Publish copy specification | GOV-002 |
| TMP-020 | P1 | Product/Security | Admin approval workflow for template publication | SHR-010 |
| AI-020 | P2 | AI/Security | Approved on-prem AI template guidance, offline eval | GOV-002, SEC-010 |

Phase 1A PoC covers TMP-002/003 and core LOC-010 partially, not an approved enterprise deployment.

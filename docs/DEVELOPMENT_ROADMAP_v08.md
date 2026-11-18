# v0.8 Roadmap — Enterprise Template Library

## Done in executable PoC (synthetic data)
- Onboarding/Getting Started page; original catalog 80; metadata taxonomy 15 areas; keyword + department/job-family/job-role/section filters.
- Local SQLite document create/read/update, revision validation; restricted HTTP endpoints.

## Not yet done
- Formal review of all template structures and terminology by department owners.
- Multi-select tags, favorites, template-based full Page Tree, rich blocks, user-customizable template management.
- P0 Windows 11 security, installer, EDR/DLP, license and threat model review.
- Notion Calendar implementation (v0.7 design, separate epic).
- Shared workspace, SSO/ACL, on-prem PostgreSQL, team collaboration and AI.

## Implementation sequence
1. **TMP-101:** Product/Legal/Security approval of original 80-template catalog; verify organization terminology.
2. **TMP-102:** Template usage analytics **local-only** and favorite/sort without network egress; opt-in.
3. **TMP-103:** Page Tree + rich text Editor integration; data migration planning.
4. **CAL-001/002:** Local calendar persistence and CRUD per existing v0.7 spec (not part of this release).
5. **SHR-001:** Central SSO/ACL foundation after shared hosting design.
6. **TMP-104:** Authorized enterprise template publishing workflow and versioned approvals.

## Acceptance
- Catalog exact unique count 80. All templates text/date/select only, fields validated.
- Search/facets stable; Getting Started always accessible.
- Existing doc ID and template IDs stable across upgrade.
- No copyrighted Marketplace template bodies or third-party assets copied.
- No external cloud, upload, media, embed, export or AI endpoints exposed.

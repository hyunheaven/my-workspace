# Skill: template-safety

Input: proposed enterprise template fields, departments, roles and intended uses.

1. Confirm original content, no replication of paid Notion template copy/design.
2. Verify every field type on allowlist (`text`, `multiline`, `select`, `date`) and document version; no HTML/scripts/attachments/URL previews/remote loaders.
3. Check synthetic placeholders only; no private data, passwords, personal identifiers, URLs to external resources or real customer names.
4. Identify data classification and clarify local-private vs approved shared scope; no automatic publication.
5. Map required fields to validation and unit tests. Client labels are convenience only; API remains authoritative.
6. Require Product and Security human approval before template becomes generally available.

Output: PASS / FAIL with issues, tests and responsible reviewers. A skill document is not an installed autonomous agent.

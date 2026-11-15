---
name: spec-to-task
description: Convert reviewed PRD requirements into gated GitHub Issues with acceptance cases and permission tests.
---
# Spec to Task
Input: PRD requirement, target phase and data classification.
1. Identify Local/Shared/Publish trust zone and owner.
2. Identify dependency on security approval, identity, schema and external software licenses.
3. Break into small testable tasks with positive/negative acceptance.
4. Identify API contract, data migration, rollback and audit impact.
5. Send to Architecture+Security reviewer before implementation; propose Issues but do not create in GitHub without authorized user approval.
Output: issue IDs, scope, acceptance, dependencies, reviewers, unresolved policy blockers.

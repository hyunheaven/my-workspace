# Multi-Agent One Team Orchestration v0.4

## Roles
Human Product Owner approves scope and all privileged deployment/release. **Lead Orchestrator** decomposes milestones; Product/UX, Architect, Security, Identity, Data, Backend, Frontend, Collaboration, Search/AI, QA/DevOps are role-specialized AI assistance tracks, not automatically provisioned independent agents.

## Sequence
`User goal → PRD acceptance cases → trust zone classification → architecture/ADR review → ACL/API schema definition → independent security review → coding branch → QA/negative cases → human review/merge → gated release`.

## Work product exchange
- Product → Architect: user scenarios, out-of-scope, acceptance.
- Architect → Identity/Data/Backend: ownership, domain API, trust boundary, migration plan.
- Security → all: threat checklist, egress/license constraints, non-bypass authorization cases.
- Backend/Data → Frontend: versioned contract, error cases, schemas.
- Collaboration → Security/Data: websocket life cycle, binary persistence, revocation plan.
- QA → Owner: reproducible tests, remaining risks, rollback steps.

## Review independence
An implementing agent does not verify itself. Every high-risk PR must receive Security + QA review and a designated human approval; a message from another AI role is a proposed review, not a company signoff.

## Tool governance
Tools/connectors are not assumed to have corporate permission. Internal GitHub actions require authorized access to a company-managed repo and explicit user approval. No AI agent is allowed to push unpublished internal code to an external GitHub or use external model on confidential documents.

## Collaboration
Track GitHub Issue → branch → PR → tests and reviewer evidence; refer to `docs/BACKLOG.md`, `docs/ACCESS_CONTROL.md` and `AGENTS.md`. Code development starts only after technical and security prerequisites.

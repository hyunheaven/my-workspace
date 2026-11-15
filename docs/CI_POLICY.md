# CI / Release Policy — v0.4

- CI is opt-in only after corporate approval of self-hosted runner location, egress, service accounts, dependency mirror and artifact retention. Never assume consumer GitHub Actions is company approved.
- Unit/static type checks and synthetic test fixtures can run offline. Integration tests with PostgreSQL and SSO use approved isolated test environment and synthetic identities.
- Every PR gate: format/lint/type/unit; tests for affected trust zone; secret/SBOM/license scanner; negative ACL tests when relevant; manual security approval for auth, WS, storage and AI changes.
- No actual business documents, production database snapshots or bearer tokens in CI logs/artifacts. Artifact signatures, provenance and release ownership policy [VERIFY].
- Deployment to central servers and endpoint installers remain separate human-controlled release actions; PR merge does not deploy automatically until explicit corporate governance says otherwise.

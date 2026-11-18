# CI / Release Policy — v0.4

- Enable CI after reviewing runner isolation, network access, service accounts, dependency sources and artifact retention.
- Unit/static type checks and synthetic test fixtures can run offline. Integration tests with PostgreSQL and SSO use approved isolated test environment and synthetic identities.
- Every PR gate: format/lint/type/unit; tests for affected trust zone; secret/SBOM/license scanner; negative ACL tests when relevant; manual security approval for auth, WS, storage and AI changes.
- No actual business documents, production database snapshots or bearer tokens in CI logs/artifacts. Artifact signatures, provenance and release ownership policy [VERIFY].
- Deployment to central servers and endpoint installers remain separate human-controlled release actions; PR merge does not deploy automatically without an explicit release step.

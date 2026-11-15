# ADR-0002 — Internal GitHub for Source Collaboration

**Date**: 2026-11-15
**Status**: Accepted product governance direction; actual host and policy [VERIFY].

Company-managed GitHub is used exclusively for application source, docs, tests with **synthetic fixtures** and PR/Issues/release tracking. User pages, attachments, local SQLite databases, shared PostgreSQL data dumps, credentials, AI prompts/outputs and model weights do not belong in Git repositories. Initialize Private, consider Internal visibility only if ownership, code/data classification and policy permit. Protected main, human PR review and approved isolated CI runner are recommended.

Before any connector-based GitHub action, verify that connected account/host are the **approved corporate** environment and the user authorized the specific operation. External GitHub.com accounts are not interchangeable with internal corporate GitHub.

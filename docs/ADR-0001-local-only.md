# ADR-0001 — Local-Only Single-PC App (SUPERSEDED)

**Date**: 2026-11-15
**Status**: **Superseded by ADR-0003**

Earlier scope constrained the entire product to a single PC without team collaboration. User later explicitly reinstated organization-level shared knowledge and Multi-user Collaboration.

**Retained constraints**: Personal/Local mode must work standalone offline, keep local data on device, and expose local backend via loopback only. Internal GitHub is the source-management system; it never stores runtime user content.

**No longer applies globally**: "No central server", "no shared workspace", "no user collaboration". See `ADR-0003-hybrid-local-first.md`.

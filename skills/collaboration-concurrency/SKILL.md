---
name: collaboration-concurrency
description: Verify P0 optimistic revisions and P1 Yjs/Hocuspocus persistence/convergence under failures.
---
# Collaboration Concurrency Review
P0: two writers using stale ETag must cause explicit conflict, no silent overwrite. P1: verify Yjs raw binary persistence, restart recovery, reconnect, schema upgrade, concurrency convergence, debounced store loss window, ACL revoke active WS and read-only enforcement. Compare durable canonical state and indexed projection separately. Return trace and reproducible tests; never claim zero data loss without durability evidence.

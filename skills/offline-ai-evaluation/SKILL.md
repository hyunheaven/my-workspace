---
name: offline-ai-evaluation
description: Evaluate only approved local/internal AI adapters on synthetic authorization-labeled documents.
---
# Approved AI Evaluation
Use a synthetic corpus and identities in an isolated evaluation environment. Measure authorization leakage (must be zero), Retrieval Recall@k, faithfulness, citation accuracy, latency, prompt injection resistance, edit preview+reject integrity and disabled-model fallback. Do not process private documents with external models; never bypass user approval for edit or high-risk agent tool.

---
id: FE-05
file: 005_manifests.md
title: "Vanguard v4.0 — Manifest Consumption in Clients"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  Client-side display, validation, and execution rules for harness manifest packs.
supersedes: none
superseded_by: none
budget_words: 2000
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Manifest Consumption in Clients

> **Who this is for.** Engineers presenting harness configurations and capabilities to users.

---

## 1. Schema Shape & Requirements

Schema owner: `vanguard/packages/domain/artifacts/manifest.py`. The client must not fork the schema.

Required keys:
```json
{
  "harness": "string",
  "components": {},
  "capabilities": [{ "verb": "string", "sink": "string", "selector": {}, "risk": "string" }],
  "evaluators": {},
  "budgetPolicy": {}
}
```

`sink` $\in$ `{pure, observation, privileged}`.

---

## 2. Discovery & Selection

- The client displays user-supplied manifest files passed via `--manifest` or workspace configuration.
- The client does not crawl backend source trees directly.
- Missing manifest paths trigger an explicit `invalid_request` error.

# Sprint 6B — Two-Senior Beta Closure

**Status:** RELEASE NO-GO until R0–R10 pass at one candidate SHA  
**Team:** two Senior Developers, each delegated Tech Lead and Project Lead decision rights within the scope below  
**Goal:** finish Sprints 1–6 and ship one modular Vanguard framework, one `vg-code-default` coding harness, and one trustworthy `vg` CLI Beta

## Execution package

1. [Closure review and ordered TODOs](sprint_6B_review_overview_and_next_tasks.md)
2. [Authoritative detailed backlog](backlog.md)
3. [Lane A — Control Plane, Client and Release](lane-a-senior-control-plane.md)
4. [Lane B — Workload, Evidence and Platform](lane-b-senior-workload-evidence.md)
5. [Sprint 6B close development guidelines](../../development_guides/guidelines_sprint_6B_close.md)
6. [Master Task Matrix & Implementation Tracker (todo_list.md)](../../../todo_list.md)
7. [Invalidated Sprint 6 receipts](INVALIDATED-sprint6-receipts.md)
8. [Gate receipt schema](gate-receipt.schema.json)

## One product path

```text
installed vg CLI
  → authenticated durable RuntimeService
  → ContextCompiler / canonical ModelInvocation
  → explicit LAM, Ollama or OpenRouter ModelPort
  → strict typed ModelProposal
  → Kernel S0–S12
  → rootless worker for read/search/patch/test
  → externally signed exact approval
  → ledger-only exactly-once recovery
  → persisted terminal event
  → exterior UID 10002 evaluator
  → signed verdict in ledger
  → terminal CLI event and stable exit code
```

No alternate path may claim Beta evidence. Replay, cassette, scenario and fixtures are explicit, visibly labelled and unable to mutate production state.

## Decision and review model

| Area | Decision DRI | Required reviewer |
|---|---|---|
| RuntimeService, lifecycle, CLI protocol, contract gates, candidate assembly | Lane A | Lane B |
| Model contract, providers, context, worker/sandbox, evaluator and platform images | Lane B | Lane A |
| Shared schema, port or trust-boundary change | Both lanes | Both must approve and record compatibility impact |
| R3–R8 control evidence | Non-authoring lane | External reviewer when both lanes authored the control |
| R9 dogfood and R10 GO/NO-GO | Both lanes recommend | Repository owner or named independent release reviewer countersigns |
| Credential rotation/history rewrite, remote force-update, tag or publication | Neither lane acts implicitly | Separate explicit repository-owner authorization |

## Integration order

1. Jointly freeze decisions, schemas, golden vectors and acceptance tests.
2. Lane A builds service/client/governance against the frozen ports while Lane B builds model/worker/evaluator adapters against them.
3. Integrate first with LAM and no network dependency.
4. Prove approval, sandbox, evaluator and kill/restart behavior adversarially.
5. Add Ollama and protected OpenRouter modes without changing the loop.
6. Build and install release artifacts on clean Linux.
7. Freeze one candidate, complete three dogfood runs, validate R0–R10 and only then seek release authorization.


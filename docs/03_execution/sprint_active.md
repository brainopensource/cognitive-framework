---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.7.0"
last_verified: 2026-08-25
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Sprint Board — M-4 and Parallel Lanes

Authority order: [`VISION.md`](../../VISION.md) (Law Zero) → [`SPEC.md`](../SPEC.md) +
[`01_law/`](../01_law/) → accepted ADRs → [`milestones.md`](milestones.md) sequencing → **this board**,
the only document that authorizes current work. `README.md` communicates; it does not decide.

## 1. Current Decision

`ADR-0095` locks [`VISION.md`](../../VISION.md) as the constitutional authority and reconciles the
roadmap to **M-4 → M-5a → M-5b → M-6 → M-6.5 → M-7 → M-8 → M-9**. `ADR-0094` remains in force:
M-4 is the RF-95 product proof and RF-85 is optional assurance claiming zero rows.

- **M-4 is active** and now includes scientific trajectory capture, not only the coding loop.
- **Nothing is blocked by a milestone.** Only named technical dependencies block work.
- **M-5a preparation may start now** — the ontology (`Operation`, `Lineage`, `Scope`, `AgentView`)
  can be designed against M-4's emerging telemetry vocabulary.
- **M7-01 continues in parallel** as a named measurement lane and must not add scheduling.

## 2. Architectural Boundary

```text
clients/products -> runtime -> agency -> kernel
                         |          |
                    adapters <- ports <- domain
```

- Clients own UX, commands, streaming display, approvals, session selection.
- Packs own domain prompts, tools, policies, and semantics.
- Runtime owns composition, bootstrap, profiles, lifecycle, sessions, persistence, replay —
  **and no domain behavior**.
- Agency owns the domain-neutral turn mechanism and context lifecycle.
- Kernel owns generic effect authority, budgets, selectors, provenance only.
- Adapters implement models, tools, stores, evaluators, indexes, sandboxing, protocols.
- Ledger and artifacts are canonical; indexes, caches, maps, summaries are rebuildable projections.

Assurance may vary by profile, but no profile may disguise its assurance level in `D_R`.

## 3. Lane A — M-4 product proof (serializing lane)

### M4-01 — Product execution profile and durable bootstrap — **IMPLEMENTED**

`product` profile (in-place host workspace, explicit approvals, SQLite-WAL, optional evaluator,
non-promotional assurance), file-backed store by default, generic entrypoint defaulting to `product`.
RF-95 guards that product use requires no containment/evaluator and never silently falls back to
memory persistence.

### M4-02 — Make the coding CLI operable

1. Install Node dependencies; qualify CLI typecheck and tests.
2. Expose provider/model, workspace, run id, event-store path, turn/effect/token budgets, and
   approval mode through the existing client request contract.
3. Stream model/tool/receipt/terminal events from the existing runtime fan-out.
4. Present reviewable diffs and approval prompts; do not duplicate authority logic in TypeScript.
5. Add `vg resume <run-id>` over the existing WAL/reconstruction path.

**Exit:** a developer can start, observe, approve, interrupt, and resume a product coding session from
the CLI without constructing Python objects by hand.

### M4-03 — Close tool-loop gaps

Exercise `vg-code-default` against a small real repository and fix only defects the run exposes. The
minimum tool surface is `fs.read`, `fs.search`, `patch.apply`, and allowlisted `proc.exec`. Improve
prompts, schemas, receipts, diff ergonomics, and compaction in the pack, clients, or adapters — never
the kernel.

**Exit:** the agent inspects before editing, applies a valid change, runs the preregistered
verification command, reacts to failure, and stops after success within declared budgets.

### M4-04 — Scientific trajectory capture *(new; parallel with M4-02/03)*

Implement the provenance rule from [`../01_law/EVIDENCE.md`](../01_law/EVIDENCE.md): every variable
that can materially affect a result gets observable identity and provenance.

- Emit context-selection, compaction, and cache events carrying policy identity, parameters, input
  digest, and output digest — **digests and references, not inlined blobs**.
- Store large content (full prompts, raw model outputs, snapshots, patches) in the artifact store,
  content-addressed.
- Add retention as an `ExecutionProfile` axis; the reproducibility class MUST enter `D_R`.
- Provide a trajectory reader good enough to compare two runs.

**Exit:** two runs of the same task can be diffed on the variables that differed. Without this,
M-6.5, M-7, and M-8 cannot be measured.

### M4-05 — Execute RF-95 *(serializing; depends on M4-02, M4-03, M4-04)*

Freeze a non-trivial coding task and verifier before the run. Execute exactly one candidate with a
live non-fake provider through canonical compose/activate/`Runtime.run_composed`, the `product`
profile in `D_R`, at least one observation, one mutation, one verification effect, a non-empty diff,
a passing verifier receipt, file-backed WAL, a complete terminal trajectory, and fresh-process
reconstruction. An independent reviewer confirms the evidence; the Engineering Director closes M-4.
RF-85 is not implicitly satisfied.

## 4. Lane B — M-5a preparation *(may start now)*

Design only; implementation opens when M-4's telemetry vocabulary stabilizes.

- **M5a-P1** — define `Operation`, `Lineage`, `Scope`, `AgentView` as contracts.
- **M5a-P2** — decide which facts are semantically necessary for reconstruction. Criterion: *does
  this change the history we must reconstruct or analyze?* — never "it happened internally".
- **M5a-P3** — RED tests: a fresh process must rebuild goal, plan, prior attempts, settled effects,
  budget, strategy, and terminal status from the ledger alone.
- **M5a-P4** — plan the runtime domain-decoupling migration named in
  [`../01_law/EXTENSIBILITY.md`](../01_law/EXTENSIBILITY.md): `runtime/entrypoint.py`,
  `runtime/scoring.py`, `runtime/autonomous_grant.py`.

Prohibited before the ADR: adding event kinds, changing the reducer, or re-tagging `M-5-BASE`.

## 5. Lane C — M7-01 measurement *(non-blocking, named historical lane)*

`ADR-0092` authorizes sequential effect-log measurement in parallel. Build `EffectRef` from actual
`EffectStarted` records with resolved resources — not static manifests. Capture selector, sink,
idempotency key, wall/model/tool timing, and cache-hit rate over a fixed-seed workload.

Allowed: capture, analysis, deterministic fixtures, reproducible runner. **Forbidden:** scheduler,
concurrency, claim TTL, leasing, worker pool, topology engine. Terminates in an explicit Director
decision — implement, simplify, or cancel — recorded as a successor ADR.

## 6. Always-parallel lanes

Open now; each blocks only on its own named interface. Every charter MUST name the RF-86 frozen paths
(`vanguard/packages/{domain, ports, kernel, runtime, agency/episode}`) as prohibited scope.

| Lane | Home | Blocks on |
|---|---|---|
| Model & tool adapters | `vanguard/packages/adapters/` | `ports/` |
| UI / CLI | `vanguard/clients/cli/` | client request contract |
| Indexing & retrieval | adapters | `IndexPort` |
| Context management | `agency/context/` | nothing |
| Coding pack tool loop | `packs/code-default/` | existing SPI |
| Tooling, linters, docs | `tools/`, `docs/` | nothing |

## 7. Explicit Non-Scope

- Do not implement `agent.spawn` before M-5b closes.
- Do not implement concurrency, scheduling, or topologies from M7-01 data without a successor ADR.
- Do not build memory, broad MCP support, swarms, learned skills, or metacognition now.
- Do not delete RF-85 assurance code; it remains an optional profile.
- Do not add a second execution authority, a conceptual mirror package, or kernel domain semantics.
- Do not weaken RF-86 or move `M-5-BASE` outside an ADR-authorized substrate change.

## 8. Verification

```bash
python3 -m unittest discover -s test -t .
bash ci/rf86_gate.sh M-5-BASE
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/scan_secrets.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_event_coverage.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
npm ci
npm run typecheck --workspaces --if-present
npm test --workspaces --if-present
```


# TODO list

+-----------+------------------------------------------------------+---------------------------+------
| Milestone | Task                                                 | Objetivo                  |
+-----------+------------------------------------------------------+---------------------------+------
| GOV       | Tornar VISION.md autoridade arquitetural superior    | Eliminar ambiguidade      |  OK 
| GOV       | Criar ADR-0095 de transição e remapeamento           | Fixar nova governança     |  OK
| GOV       | Reconciliar SPEC, LAW, README, milestones e sprints  | Uma única verdade ativa   |  OK
| GOV       | Remover locks cerimoniais; usar dependências técnicas| Desbloquear equipes       |  OK
+-----------+------------------------------------------------------+---------------------------+------
| M-4       | Finalizar vg code útil                               | Produto funcional         |
| M-4       | Streaming, tools, diff, tests, resume, WAL            | Loop agentic completo    |
| M-4       | Telemetria e trajectory capture desde o início        | Base científica          |
| M-4       | Executar RF-95 real                                  | Validar caminho do produto|
+-----------+------------------------------------------------------+---------------------------+------
| M-5a      | Definir Operation, Lineage, Scope e AgentView         | Nova ontologia do agente |
| M-5a      | Tornar estado necessário reconstruível por eventos    | Agent event-derived      |
| M-5a      | Separar ledger reducer de projections                 | Evitar acoplamento       |
| M-5a      | Registrar provenance de context/cache/compaction      | Reprodutibilidade        |
| M-5a      | Congelar e re-tag novo M-5-BASE                       | Baseline estável         |
+-----------+------------------------------------------------------+---------------------------+------
| M-5b      | Criar formal-default + checker determinístico         | Provar generalidade      |
| M-5b      | Executar RF-86 contra novo baseline                   | Zero domain leakage      |
+-----------+------------------------------------------------------+---------------------------+------
| M-6       | Implementar spawn como nested lineage                 | Delegação recursiva      |
| M-6       | Child scopes, budget/capability attenuation           | Limites claros           |
| M-6       | Join, cancelamento e recovery                         | Recursão durável         |
+-----------+------------------------------------------------------+---------------------------+------
| M-6.5     | Criar ProgressProjection + meta-controller            | Estratégia adaptativa    |
| M-6.5     | Medir runs com/sem meta-controller                    | Validar metacognição     |
+-----------+------------------------------------------------------+---------------------------+------
| M-7       | Definir topology como artifact/config versionado      | Grafos agentic           |
| M-7       | Formalizar causal partial order / branch / join       | Execução não linear      |
| M-7       | Adicionar paralelismo observacional simples           | Ganho imediato           |
| M-7       | Scheduler avançado apenas se medições justificarem    | Evitar complexidade inúti|
+-----------+------------------------------------------------------+---------------------------+------
| M-8       | Memory e retrieval como projections/plugins           | Memória reutilizável     |
| M-8       | Skills versionadas derivadas de trajetórias           | Aprendizagem operacional |
| M-8       | Held-out evaluation + promotion + rollback            | Aprender com rigor       |
+-----------+------------------------------------------------------+---------------------------+------
| M-9       | Integrar coding + formal + research                   | General Agent Framework  |
| M-9       | Testar adaptação, transferência e long-horizon        | Validar v1.0             |
| M-9       | Release AETHER v1.0                                   | Framework geral integrado|
+-----------+------------------------------------------------------+---------------------------+------
| PARALELO  | Adapters, UI/CLI, indexing, context, tooling, docs    | Não bloquear 20 devs     |
| PARALELO  | Concurrency measurement histórica                    | Decidir scheduler por dado|
+-----------+------------------------------------------------------+---------------------------+------
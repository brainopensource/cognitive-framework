# Project Alignment — Formalização e abertura da v0.6.1 "Substrate AETHER VANGUARD"**

Act as the same collective leadership body as before — **Principal Staff Engineer, Senior Software Architect / Specialist, Tech Lead, and Project/Engineering Director** — for AETHER / Vanguard.

**Context you must load before doing anything else:** an independent Substrate Generality Review was already conducted against the live `v0.6.0` Concept Lock (`SPEC.md`, ADRs `0069`–`0076`, GAMMA, the `002` gap register, `sprint_active.md`, and all four wave plans). That review's verdict: the foundation is genuinely building a general substrate, not a coding harness with a kernel attached — but it identified a specific, bounded set of corrections that must be formalized **before** Wave 3 implementation proceeds, plus a longer-horizon roadmap extension (M-5 through M-10) that must exist in the backlog now, even if most of it stays `DEFERRED`, so nothing forces a later migration.

**Your task is not to re-review the architecture. The review is done. Your task is to make the documentation and planning artifacts say what the review already concluded, so developers can execute against it.**

---

### 1. What you are producing

A version bump from `v0.6.0` Concept Lock to **`v0.6.1` — Substrate Correction Lock**, expressed as:

1. One or more new **append-only ADRs** (numbered `0077+`) that formalize each accepted correction below. Do not silently edit `0069`–`0076`. Where a correction narrows or extends a prior ADR, cite it and say so explicitly, exactly as `0076` did to `0069`–`0075`.
2. An updated **`SPEC.md`** version anchor and the specific sections the new ADRs touch (manifest shape in §2.3, the deferred list in §9 if scope changes, invariants if any are added).
3. An updated **`002` gap register** — new falsifiers added to §4.2 in the same table format, existing wave exit gates amended where the correction changes them.
4. An updated **`backlog.md`**, **`milestones.md`**, and **`sprint_active.md`** reflecting the corrected Wave 3 (rebalanced, not just re-labeled) and a new, intentionally lighter **post-foundation macro-roadmap section** (M-5 through M-10) — outcomes and gates only, not sprint-level detail, since detailing unstarted future work is waste per the engineering posture already established for this project.
5. Updated wave plan files (`wave3_extensibility.md` at minimum) with the new/changed tasks.

---

### 2. The corrections to formalize (do not reopen; adapt around them)

These come directly from the Substrate Generality Review's decision register. Treat them as the input, not as something to re-litigate:

- **Manifest as component graph, not fixed slots.** `harness.yaml`'s five fixed keys (`planner`, `context`, `memory`, `evaluation`, `toolkits`) must become a named component graph. Slot names survive only as a pack convention. `D_H` computation extends to cover the graph. This is a **Wave 3 (3.1-B) change**, ADR required, `code-default` migrates mechanically.
- **Guardrails: absent-vs-forged, not always-on-vs-optional.** A composition may declare an absent evaluator, sandbox tier, or approval policy. The system must accept the declaration, bake it into `D_H`, and mark resulting trajectories non-attributable for promotion. An unsigned verdict remains categorically illegal regardless of any other declaration. ADR required.
- **`agent.spawn` as a capability-mediated kernel verb — design only, not implementation.** Today only the engine can spawn; planners cannot. Write the design note and the falsifier sketch now. Do **not** touch the kernel before Wave 4 closes. Record the implementation decision as explicitly deferred to post-M-4, owner Director.
- **Falsifier hardening, cheap and immediate:** F-12 must assert non-zero per-turn cost, populated turns, model fingerprint, and embedded-or-explicitly-null verdict — not just schema validity. A new falsifier for suspend-mid-turn → cold-reconstruct-from-WAL-in-a-fresh-process → resume-to-completion must be added; this is the single test that determines whether future concurrency is a scheduling refactor or a rewrite.
- **Wave 3 rebalancing.** Wave 3 currently carries the entire extensibility claim on far fewer falsifiers than Wave 1 carried for the trust spine, and it builds on `layer0/registry/` and `layer0/compose/`, which have never run on the canonical path. Add the negative-test set named in the review (unknown-ref-fails-at-compose, empty-ceiling-denies, registry-exclusive-write, faulted-cell-cannot-stay-active, `in_process`-requires-explicit-grant, frozen-composition-immutable) as first-class Wave 3 falsifiers, not implied behavior.
- **Pack #2 as a gate, not an aspiration.** A second, non-coding domain pack with zero diffs under `domain/` and `kernel/` becomes an explicit exit condition for claiming I-7 (domain-blindness) is proven, not just declared. Place it in the post-foundation macro-roadmap (M-5), not before Wave 4.
- **Documentation consolidation, scheduled, not immediate.** The governance corpus (SPEC + GAMMA + `002` + `000` + wave plans + sprint board) should collapse to SPEC + ADR log + one living board once Wave 4 closes. Do not touch this now — record it as a scheduled post-M-4 task so it doesn't get lost, but do not let it distract from Wave 3.
- **Macro-roadmap M-5 through M-10 must exist in the backlog now, at outcome level only:** post-foundation consolidation and Pack #2 (M-5) → concurrency enablement gated on the suspend/resume falsifier (M-5/M-7) → `agent.spawn` implementation and validation cases: hierarchical decomposition, tree search (M-6) → controlled concurrency at scale (M-7) → framework-builder abstraction proven via debate, critic-loop, evolutionary-search, multi-agent delegation compositions (M-8) → high-performance orchestration of many logical agents (M-9) → the meta-cognitive substrate: outer-loop planner, manifest mutation, skill synthesis, DPO harvest, continuous promotion loop (M-10, final). Each milestone gets a one-paragraph outcome and its entry/exit gate — nothing more granular than that until the milestone before it is entered.

---

### 3. Operating constraints (unchanged from the original lock — do not relitigate)

- ADRs are append-only. `0069`–`0076` stand. Any new ADR that narrows them must name which one and why, with evidence — preference or aesthetics is not sufficient grounds.
- No third runtime tree, no Rust TCB rewrite, no evaluator-as-plugin, no mid-run hot-swap, no swarm engine, no workflow DAG, no graph database. These remain refused; nothing in this correction pass reopens them.
- Wave 4's stop condition is not negotiable. `agent.spawn`, concurrency, Pack #2, and all of M-5 through M-10 are explicitly **out of scope for implementation** until Wave 4's nine-row gate is green on one real run.
- The kernel gains nothing in Waves 1–4 except tests; the TCB LOC ceiling stands.
- Sequential scheduling (I-11) stands until its own named measurement gate fires — the suspend/resume falsifier is that gate's precondition, not its satisfaction.
- Distinguish explicitly, for every item you touch: **lock now / strengthen now / generalize now / design-only-implement-later / revisit after Wave 4 / reject**. Do not implement anything marked design-only or revisit-after-Wave-4.

---

### 4. Required output

For each document you touch, produce the actual edited content (not a description of what should change), plus a short changelog entry stating: what changed, which ADR authorizes it, and which wave it lands in. Close with:

1. A one-paragraph statement of what `v0.6.1` now locks that `v0.6.0` did not.
2. Confirmation that Wave 4's stop condition and scope are unchanged.
3. Explicit confirmation that M-5 through M-10 exist in the backlog as outcomes/gates only, with no sprint-level detail authorized yet.
4. A short "what a developer reads first" pointer, updated if the reading order changed.

# Roadmap completo — Wave 2 (atual) até Wave final (Meta-Cognição)

**Convenção de status:** `CONCLUÍDA` · `EM ANDAMENTO` · `PRONTA` (pode começar) · `TECH-LEAD` (precisa decisão) · `DIRECTOR` (precisa aprovação) · `BLOQUEADA` (aguarda milestone anterior) · `DESIGN` (só especificação, sem código)

*(M-0 CI-truth e M-1 Trust-Spine já estão `CONCLUÍDAS` — não repetidas aqui, você pediu a partir de onde paramos.)*

| Milestone | Sprint | ID | Tarefa / Subtarefa | Status |
|---|---|---|---|---|
| **M-2 — Convergência (runtime único)** | 2.2 | 2.2-B | Deletar superfícies KILL do `layer0/` (kernel, scheduler, events duplicados) | EM ANDAMENTO (Dev A) |
| M-2 | 2.2 | 2.2-C | Split de `root.py` no lugar | EM ANDAMENTO (Dev B) |
| M-2 | 2.2 | ↳ 2.2-C.1 | Extrair `compose.py` | PRONTA |
| M-2 | 2.2 | ↳ 2.2-C.2 | Extrair `session.py` | PRONTA |
| M-2 | 2.2 | ↳ 2.2-C.3 | Extrair `wiring.py` | PRONTA |
| M-2 | 2.2 | 2.2-D | Estender linter de domain-blindness + boundary checker para os módulos splitados | PRONTA |
| M-2 | 2.2 | **NOVA-1** | Fortalecer F-12: trajetória deve carregar custo por turno não-zero, fingerprint do modelo, veredito embutido (hoje passa vazia) | PRONTA |
| M-2 | 2.2 | **NOVA-2** | Falsificador de suspend/resume: suspender episódio no meio do turno → reconstruir a frio em processo novo → retomar até concluir | PRONTA |
| M-2 | 2.2 | **NOVA-3** | Corrigir `_PROC_PATTERN` para ler do ceiling compilado em vez de restatement literal | PRONTA |
| M-2 | — | **GATE M-2** | Detector de duplicação verde; zero imports `layer0.*`; testes de runtime verdes sem mudança de comportamento | BLOQUEADA (aguarda 2.2-B/C/D) |
| **M-3 — Extensibilidade + Correção Conceitual** | 3.1 | 3.1-A | FSM do registry de plugins absorvida em `runtime/registry/`, toda transição ledgerada | PRONTA (entry: M-2) |
| M-3 | 3.1 | 3.1-B | Compose v2 ligado ao registry: discovery → resolve → verify → freeze | PRONTA |
| M-3 | 3.1 | 3.1-C | Plugin echo: lifecycle completo DISCOVERED→RETIRED sobre UDS + injeção de falha | PRONTA |
| M-3 | 3.1 | 3.1-D | Isolation broker: rlimits do tier subprocess | TECH-LEAD |
| M-3 | 3.1 | **NOVA-4** | Suite de negativos do lifecycle: ref desconhecida falha no compose (nunca no runtime); ceiling vazio nega; só o registry pode escrever eventos `Plugin*`; cell com falha não pode ficar "ativa"; `in_process` exige grant explícito de política; nenhum caminho muta composição congelada | PRONTA |
| M-3 | 3.2 | 3.2-A | Toolkits do `code-default` carregando via lifecycle real (não import direto) | PRONTA |
| M-3 | 3.2 | 3.2-B | Varredura de tokens de codificação para fora de `domain/`/`kernel/` | PRONTA |
| M-3 | 3.2 | 3.2-C | Convergência do parser de manifesto (um único caminho YAML→harness) | PRONTA |
| M-3 | **3.3 (nova)** | 3.3-A | **Correção de conceito/spec:** desenhar manifesto como grafo nomeado de componentes (substitui os 5 slots fixos) | DESIGN |
| M-3 | 3.3 | 3.3-B | Decidir: nomes de slot viram convenção de pack, não restrição de schema — registrar em ADR | DIRECTOR |
| M-3 | 3.3 | 3.3-C | Atualizar definição de `D_H` para cobrir o grafo de componentes | DESIGN |
| M-3 | 3.3 | 3.3-D | Migrar `code-default` mecanicamente para o novo formato de manifesto | BLOQUEADA (aguarda 3.3-B) |
| M-3 | **3.4 (nova)** | 3.4-A | **Correção de conceito/spec:** formalizar a regra "ausência declarada vs. falsificação" para guardrails opcionais — ADR | DESIGN |
| M-3 | 3.4 | 3.4-B | Schema: `evaluation: none`, sandbox tier opcional, approval policy opcional por composição | PRONTA (após 3.4-A) |
| M-3 | 3.4 | 3.4-C | Marcação de trajetória "não-atribuível para promoção" quando guardrail está ausente | PRONTA |
| M-3 | 3.4 | 3.4-D | Falsificador: veredito não assinado continua inaceitável mesmo com `evaluation: none` declarado em outro componente | PRONTA |
| M-3 | **3.5 (nova)** | 3.5-A | **Correção de conceito/spec, apenas design:** nota de design para `agent.spawn` como verbo mediado pelo kernel (não implementar ainda) | DESIGN |
| M-3 | 3.5 | 3.5-B | Esboçar falsificador: planner sem grant de spawn não pode delegar; atenuação do filho permanece intacta | DESIGN |
| M-3 | 3.5 | 3.5-C | Registrar decisão formal: implementação fica bloqueada até pós-M-4 | DIRECTOR |
| M-3 | — | **GATE M-3** | Echo plugin percorre lifecycle completo; `code-default` carrega pelo mesmo caminho; I-7 vale em todo lugar | BLOQUEADA |
| **M-4 — Foundation E2E (STOP)** | 4.1 | 4.1-A | Repositório fixture + oráculo pré-registrado | PRONTA (entry: M-1+M-2+M-3) |
| M-4 | 4.1 | 4.1-B | Teste E2E das nove linhas em uma execução única | PRONTA |
| M-4 | 4.1 | 4.1-C | Cassette da execução verde para CI por PR | PRONTA |
| M-4 | 4.1 | 4.1-D | Relatório de evidência (ledger digest, `D_H`/`D_R`, trajetória, containment) | PRONTA |
| M-4 | 4.1 | **NOVA-5** | Confirmar que a trajetória da execução real carrega custo/turno não-zero (valida NOVA-1) | PRONTA |
| M-4 | — | **GATE M-4 — PARE** | Modelo real, efeito autorizado, filesystem, sandbox, avaliação assinada, WAL, replay a frio, trajetória, runtime único — tudo em uma execução | BLOQUEADA |
| **M-5 — Consolidação Pós-Fundação + Prova de Generalidade** | 5.1 | 5.1-A | **Organizar/reescrever:** colapsar corpus de governança em SPEC + log de ADRs + um único board vivo | BLOQUEADA (entry: M-4) |
| M-5 | 5.1 | 5.1-B | Aposentar GAMMA e o registro `002` como autoridades permanentes uma vez absorvidos | BLOQUEADA |
| M-5 | 5.1 | 5.1-C | Caminho de leitura único para novo desenvolvedor (3 documentos, não 7) | BLOQUEADA |
| M-5 | **5.2** | 5.2-A | **Teste de premissa básica:** escolher Pack #2 fora de codificação (ex.: análise de dados ou math) | BLOQUEADA |
| M-5 | 5.2 | 5.2-B | Implementar toolkit(s) + suite de oráculos + defaults de manifesto + vocabulário de seletor do Pack #2 | BLOQUEADA |
| M-5 | 5.2 | 5.2-C | Verificar zero diffs sob `domain/` e `kernel/` (falsificador I-7) | BLOQUEADA |
| M-5 | 5.2 | **GATE 5.2** | Generalidade deixa de ser tese e vira fato demonstrado | — |
| M-5 | **5.3** | 5.3-A | **Testar premissa básica:** medir solidez dos seletores para grupos de independência | BLOQUEADA |
| M-5 | 5.3 | 5.3-B | Confirmar NOVA-2 (suspend/resume) passa em escala com múltiplos episódios | BLOQUEADA |
| M-5 | 5.3 | 5.3-C | Nomear e registrar o gate de medição para I-11 (decisão documentada, concorrência ainda não ligada) | TECH-LEAD |
| **M-6 — Delegação Mediada (agent.spawn)** | 6.1 | 6.1-A | **Feature nova:** implementar `agent.spawn` como efeito no dispatch S0–S12 | BLOQUEADA (entry: M-5, decisão 3.5-C) |
| M-6 | 6.1 | 6.1-B | Grant de capacidade de spawn por composição | BLOQUEADA |
| M-6 | 6.1 | 6.1-C | Reaproveitar atenuação/orçamento existentes de `spawn()` para o novo verbo | BLOQUEADA |
| M-6 | 6.1 | 6.1-D | Falsificadores: planner sem grant não spawna; filho continua atenuado; ledger registra spawn como efeito com receipt | BLOQUEADA |
| M-6 | **6.2** | 6.2-A | **Caso de validação:** composição de referência — decomposição hierárquica via planner recursivo | BLOQUEADA |
| M-6 | 6.2 | 6.2-B | **Caso de validação:** composição de referência — busca em árvore (expansão/avaliação/seleção como componentes separados) | BLOQUEADA |
| M-6 | 6.2 | 6.2-C | Validar ambos contra o manifesto em grafo de componentes (M-3.3) | BLOQUEADA |
| **M-7 — Concorrência Controlada (gated por medição)** | 7.1 | 7.1-A | Ativar grupos de independência para seletores não-intersectantes | BLOQUEADA (entry: gate 5.3-C atingido) |
| M-7 | 7.1 | 7.1-B | Backpressure, cancelamento cooperativo, contabilização de recursos | BLOQUEADA |
| M-7 | **7.2** | 7.2-A | Separação lógica agente-vs-worker (`K ≪ N`) | BLOQUEADA |
| M-7 | 7.2 | 7.2-B | Protótipo de scheduler assíncrono/orientado a eventos | BLOQUEADA |
| M-7 | 7.2 | 7.2-C | Validar via NOVA-2 em escala real | BLOQUEADA |
| **M-8 — Framework Builder Abstraction + Casos de Validação** | 8.1 | 8.1-A | **Caso de validação:** composição de debate (N proponentes + agregador) | BLOQUEADA (entry: M-6) |
| M-8 | 8.1 | 8.1-B | **Caso de validação:** loop crítico/revisor (dois componentes de avaliação distintos) | BLOQUEADA |
| M-8 | 8.1 | 8.1-C | **Caso de validação:** busca evolutiva (operador de população + binding de fitness) | BLOQUEADA |
| M-8 | 8.1 | 8.1-D | **Caso de validação (exploratório):** delegação econômica multi-agente | BLOQUEADA |
| M-8 | **8.2** | 8.2-A | SDK/CLI para compor novos harnesses declarativamente | BLOQUEADA |
| M-8 | 8.2 | 8.2-B | Ferramenta de validação de composição (dry-run compose, preview de ceiling) | BLOQUEADA |
| M-8 | 8.2 | 8.2-C | Guia do desenvolvedor: "como construir um novo agente" | BLOQUEADA |
| M-8 | **8.3** | 8.3-A | Rodar pack de codificação + Pack #2 + um terceiro pack lado a lado | BLOQUEADA |
| M-8 | 8.3 | 8.3-B | Confirmar runtime único, zero diffs de core entre os três | BLOQUEADA |
| M-8 | 8.3 | **GATE M-8** | Framework comprovadamente builder de algoritmos agênticos sem novo engine | — |
| **M-9 — Alta Performance / Orquestração em Escala** | 9.1 | 9.1-A | Teste de carga: muitos agentes lógicos sobre pool de workers limitado | BLOQUEADA (entry: M-7 + M-8) |
| M-9 | 9.1 | 9.1-B | Medir overhead de IPC, serialização, chamada de plugin | BLOQUEADA |
| M-9 | 9.1 | 9.1-C | Medir pressão de ledger e custo de isolamento em escala | BLOQUEADA |
| M-9 | **9.2** | 9.2-A | Otimizações pontuais apenas onde a medição 9.1 apontar gargalo real | BLOQUEADA |
| M-9 | 9.2 | 9.2-B | Revisar congelamento de 5 SPIs à luz do grafo de componentes maduro | TECH-LEAD |
| **M-10 — Substrato Meta-Cognitivo (WAVE FINAL)** | 10.1 | 10.1-A | Endurecer exhaust de dados em produção: custo/turno, fingerprint, veredito sempre presentes em todos os packs | BLOQUEADA (entry: M-8 + M-9) |
| M-10 | 10.1 | 10.1-B | Validar telemetria de atribuição (prefix hits, escalações) entre packs | BLOQUEADA |
| M-10 | **10.2** | 10.2-A | Implementar loop externo (`outer`) como segundo `IPlanner` registrado, invocado no `reflect()` | BLOQUEADA |
| M-10 | 10.2 | 10.2-B | Restringir capacidade do loop externo a: propostas de mutação de manifesto, escrita de skill, pré-registro de oráculo — nunca workspace | BLOQUEADA |
| M-10 | **10.3** | 10.3-A | Operadores de mutação evolutiva sobre campos JCS-diferenciáveis do manifesto | BLOQUEADA |
| M-10 | 10.3 | 10.3-B | Runs pareados contra baseline não-deletável como função de seleção | BLOQUEADA |
| M-10 | 10.3 | 10.3-C | Evento assinado de promoção que troca o ponteiro default do registry | BLOQUEADA |
| M-10 | **10.4** | 10.4-A | Harvester minerando trajetórias por n-gramas de efeito de alto lift condicionado a veredito | BLOQUEADA |
| M-10 | 10.4 | 10.4-B | Skill cards candidatos só entram no manifesto pelo pipeline de seleção 10.3 | BLOQUEADA |
| M-10 | **10.5** | 10.5-A | Pipeline de harvest DPO: pares (chosen, rejected) por `(task_digest, harness_digest, prefix)` | BLOQUEADA |
| M-10 | 10.5 | 10.5-B | Filtro anti-cheat + validade de assinatura de veredito | BLOQUEADA |
| M-10 | 10.5 | 10.5-C | Fine-tune de modelos tier-1/2 + regressão via cassette-replay no lab + ponteiro de promoção | BLOQUEADA |
| M-10 | **10.6** | 10.6-A | Loop contínuo em produção: telemetria → harvest → fine-tune → regressão → promoção, como processo permanente | BLOQUEADA |
| M-10 | 10.6 | 10.6-B | Gate de decisão calibrado (estilo active-inference) usando histórico de veredito por harness digest | BLOQUEADA |
| M-10 | 10.6 | 10.6-C | **Protótipo multi-dimensional:** loop externo raciocinando simultaneamente sobre seleção de planner, seleção de plugin e roteamento adaptativo | BLOQUEADA |
| M-10 | **10.7** | 10.7-A | **Validação final:** sistema propõe, testa e promove uma versão melhorada de sua própria composição | BLOQUEADA |
| M-10 | 10.7 | 10.7-B | Toda a cadeia permanece atribuível via `D_H`/`D_R`/`D_X` e veredito assinado, do primeiro ao último passo | BLOQUEADA |
| M-10 | — | **GATE FINAL** | Meta-Harness prototype comprovado: self-improvement e aprendizado contínuo funcionando sobre um substrato cuja evidência nunca pôde ser forjada | — |
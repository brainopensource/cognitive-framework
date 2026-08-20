# AETHER v1 — Roadmap de Desenvolvimento por Waves

**Status:** plano executivo de replatformização e desenvolvimento
**Substitui:** `vanguard-roadmap-waves.md` como sequência recomendada para o produto v1
**Base técnica:** review do código atual, `SPEC.md`, documentos de Tech Lead e validação dos caminhos reais de produção
**Objetivo:** entregar um Harness Builder world-class e usá-lo para construir o primeiro Autonomous Coding Project, preservando o kernel semântico e substituindo o runtime provisório.

---

## 0. Decisão executiva sobre o roadmap anterior

O roadmap anterior contém princípios que devem ser preservados, mas sua ordem de execução e algumas premissas não são compatíveis com o estado real do código.

### Preservar

- Hierarquia `Subtask → Task → Sprint → Wave → Milestone`.
- Toda task com verificação executável.
- Telemetria, causalidade, custo e atribuição capturados desde o primeiro runtime.
- Exterior evaluator separado e com verdicts assinados.
- Replay como propriedade provada em CI.
- Plugins untrusted by default.
- Harness como composição declarativa content-addressed.
- Promoção de self-improvement apenas com avaliação pareada e rollback.

### Reescrever

| Premissa anterior | Correção para AETHER v1 |
|---|---|
| Wave documental na cadeia crítica | Documentação e higiene deixam de ser milestones de produto. Só entram quando desbloqueiam código ou gates. |
| Deletar `vanguard/packages/` em data fixa | Congelar como referência; retirar somente após paridade diferencial, rollback validado e nenhum consumer de produção. |
| Telemetria completa depois do coding pack | Event Envelope v2, attribution e trajectory começam na primeira wave. |
| JSON-RPC/UDS atual já é seam polyglot | O worker atual é fixture. Criar contrato tipado e supervisor genérico antes de portar plugins reais. |
| Orquestrador central como consumer posterior de ledgers | O orquestrador é Control Plane autoritativo: agenda, concede leases, registra comandos e supervisiona runs. Analytics é consumer. |
| Um `seq` global resolve concorrência | Sequenciamento autoritativo por projeto/run, mais causalidade entre agentes; sem gargalo global artificial. |
| Stores e sandbox como plugins comuns | Stores têm adapters substituíveis, mas commit/ordering pertencem ao core confiável. O supervisor de isolamento também pertence ao TCB. |
| SDK polyglot depois do coding pack | Protocolos e SDKs gerados precedem qualquer plugin real. |
| 200 tarefas e `p < 0.05` como gate universal | O tamanho da suíte vem de power analysis; promoção exige efeito mínimo, incerteza, correção de múltiplos testes e piso A/A. |

**Conclusão:** o arquivo anterior deve ser arquivado como planejamento histórico. Corrigi-lo incrementalmente manteria dependências e numeração enganosas. Este documento o substitui.

---

## 1. Princípios de execução

### 1.1 Hierarquia

```text
Subtask → Task → Sprint → Wave → Milestone
```

- **Subtask:** mudança atômica, owner único.
- **Task:** entrega verificável por comando ou teste automatizado.
- **Sprint:** incremento coerente que torna uma sentença verdadeira.
- **Wave:** conjunto de sprints que termina em gate de arquitetura/produto.
- **Milestone:** capacidade demonstrável e utilizável, com release candidate.

### 1.2 Regras de entrada

Nenhuma task entra no plano sem:

1. output de código ou teste claramente identificado;
2. dependências explícitas;
3. critério de aceite executável;
4. eventos e métricas produzidos;
5. comportamento de falha e rollback;
6. owner do estado autoritativo.

### 1.3 Sequenciamento inegociável

1. Contratos antes de implementações multilíngues.
2. Ledger durável antes de autonomia.
3. Supervisor genérico antes de plugins reais.
4. Single-node correto antes de distribuição.
5. Um coding agent real antes de multi-agent.
6. Autonomous Project observável antes de self-improvement.
7. Experimentos com poder estatístico antes de promoção automática.
8. Novo domínio deve entrar sem diff no core.

### 1.4 Estratégia de migração

O projeto seguirá um **strangler rewrite**:

- O Python atual é congelado como implementação de referência.
- Golden vectors, kernel S0–S12, JCS, evaluator e lab permanecem ativos.
- O core de produção nasce em Rust ao lado do sistema atual.
- Cada semântica portada passa por teste diferencial Python × Rust.
- Nenhum diretório legado é removido antes de existir substituto aceito.
- Após paridade, consumers migram por feature flag e cohort.
- A remoção final exige uma janela de rollback já concluída.

---

## 2. Arquitetura-alvo e ownership

| Plane | Responsabilidade | Autoridade |
|---|---|---|
| **Control Plane** | Orchestrator, scheduler, project state, capability/budget kernel, plugin supervision | Autoritativo |
| **Execution Plane** | Harness instances, agent runtimes, plugins e workspaces isolados | Executa leases; não escreve estado autoritativo diretamente |
| **Evidence Plane** | Oracles, evaluation requests, signed verdicts | Identidade exterior independente |
| **Data Plane** | Ledger, transactional outbox, CAS blobs, event stream e projections | Ledger é source of truth |
| **Learning Plane** | Dataset, experiments, attribution, variant proposals e promotion analysis | Read-only sobre histórico; promoção mediada |

### 2.1 Stack

- **Rust/Tokio:** kernel de produção, ledger, orchestrator, scheduler e plugin supervisor.
- **Python:** planners, context, memory, model adapters, evaluation clients e learning plugins.
- **TypeScript:** SDK, CLI/UI e clientes de consulta.
- **Protobuf/gRPC:** serviços e transporte tipado.
- **JSON Schema + JCS:** manifests, identidade, hashing, assinatura e golden vectors.
- **OCI:** empacotamento content-addressed de plugins.
- **SQLite WAL + filesystem CAS:** primeiro deployment single-node.
- **PostgreSQL + S3/MinIO + NATS JetStream:** adapters do deployment distribuído.
- **OpenTelemetry:** export operacional; nunca substitui o ledger semântico.

### 2.2 Estrutura de destino

```text
crates/
  aether-protocol/
  aether-canonical/
  aether-kernel/
  aether-ledger/
  aether-orchestrator/
  aether-plugin-host/
  aether-harness-compiler/
proto/aether/v1/
schemas/aether/v1/
sdk/python/
sdk/typescript/
plugins/coding/
packs/coding/
conformance/
```

---

# MILESTONE A — Contract-Locked Executable Foundation

**Waves 1–2**  
**Entrega:** core single-node durável, com contratos polyglot, replay real e paridade semântica com a referência Python.

## WAVE 1 — Protocol & Conformance Lock

**Sentence:** *Todas as fronteiras do sistema têm contrato versionado, SDK gerado e compatibilidade verificável.*

### Sprint 1.1 — Protocolos canônicos

**Task 1.1.1 — Event Envelope v2**

- Definir `project_id`, `run_id`, `agent_id`, `harness_digest` e `plugin_digest`.
- Adicionar `project_seq`, `agent_seq`, `causation_id`, `correlation_id` e `idempotency_key`.
- Separar metadata do conteúdo: eventos carregam `payload_digest`/`blob_ref` por padrão.
- Manter JCS como representação de identidade e assinatura.

**Task 1.1.2 — Command e lifecycle contracts**

- Project, run, harness e agent commands.
- Plugin lifecycle: `Describe`, `Init`, `Health`, `Checkpoint`, `Quiesce`, `Shutdown`.
- Serviços tipados: Planner, Context, Memory, Model, Tool, Evaluation Gateway e Project Policy.
- Deadlines, cancellation e structured errors obrigatórios.

**Task 1.1.3 — Manifests v2**

- `PluginManifest`, `HarnessManifest` e `ProjectManifest`.
- Protocol version, artifact digest, capabilities, isolation, resource requirements e config schema.
- Refs sempre resolvidas para digest imutável na composição.

### Sprint 1.2 — Toolchain polyglot

- Introduzir Buf lint, generation e breaking-change detection.
- Gerar SDKs Rust, Python e TypeScript.
- Proibir tipos de domínio duplicados escritos à mão.
- Importar golden vectors JCS e kernel para `conformance/`.
- Criar compatibility matrix por SPI major/minor.

### Sprint 1.3 — Data contract para aprendizagem

- Definir trajectory v2 como projeção determinística dos eventos.
- Taxonomia fechada de failure causes com extensão versionada.
- Usage/cost multidimensional em model calls, tool calls e project totals.
- Políticas de redaction, encryption, content capture e retention.

### Gate G-W1

```bash
buf lint
buf breaking --against '.git#branch=main'
cargo test -p aether-protocol -p aether-canonical
python -m pytest conformance/python
```

- SDKs gerados sem diff após nova geração.
- Golden vectors idênticos em Rust, Python e TypeScript.
- Nenhum digest depende dos bytes de serialização Protobuf.
- Todo command possui idempotency key, deadline e resposta terminal.

## WAVE 2 — Durable Core & Authoritative Orchestrator

**Sentence:** *Um projeto executa e recupera seu estado exclusivamente a partir de eventos duráveis.*

### Sprint 2.1 — Ledger e blobs

- Implementar append-only ledger em SQLite WAL.
- Commit atômico de command state, event e outbox.
- Filesystem CAS com `write → fsync → event(blob_ref)`.
- Fold/reducers puros para project, run, budget, grants, approvals e plugin lifecycle.
- Cold replay e time-travel branch.

### Sprint 2.2 — Kernel Rust com paridade diferencial

- Portar S0–S12, selectors, attenuation, grants e budget reservation.
- Reutilizar todos os golden vectors existentes.
- Executar referência Python e Rust sobre os mesmos inputs.
- Bloquear merge em divergência de decision, digest, receipt ou event sequence.

### Sprint 2.3 — Orchestrator single-node

- State machine de Project/Run/Agent.
- Um owner/lease autoritativo por projeto.
- Command deduplication e retry seguro.
- Scheduler inicialmente concorrente entre agents, mas serializa decisões conflitantes por projeto.
- Heartbeat, cancellation, recovery e terminal state obrigatórios.

### Gate G-W2 · G-MILESTONE A

- Kill/restart entre qualquer command e event sem perda ou duplicação lógica.
- Replay cold-start reconstrói 100% do estado observável.
- Paridade Python × Rust em toda a suíte de conformidade.
- Nenhum verdict, claim ou checkpoint sintético.
- Benchmark baseline salvo para append latency, replay throughput, memória e startup.

---

# MILESTONE B — Real Harness Builder

**Waves 3–4**  
**Entrega:** plugins realmente substituíveis e isolados, harnesses compilados por digest e experiência completa de construção.

## WAVE 3 — Generic Plugin Runtime

**Sentence:** *Qualquer plugin compatível pode ser verificado, iniciado, chamado, interrompido e substituído sem import no core.*

### Sprint 3.1 — Registry e supply chain

- Resolver artifacts OCI por digest, nunca por tag mutável em runtime.
- Verificar signature, attestation, SBOM e protocol compatibility.
- Calcular plugin identity a partir de artifact, config, assets, prompts e policies resolvidas.
- Lifecycle ledgerado: discovered → verified → activated → quiesced → retired/faulted.

### Sprint 3.2 — Supervisor de isolamento

- `in_process` restrito a componentes compilados do TCB.
- `subprocess` com identity, rlimits, no-new-privileges e filesystem policy.
- `container` rootless para tool execution e código produzido por modelos.
- Network default-deny com grants explícitos.
- stdout/stderr sempre capturados por blob ref e associados à chamada.
- WASI permanece spike não bloqueante; não é requisito de release.

### Sprint 3.3 — Runtime semantics

- Deadlines e cooperative cancellation.
- Backpressure e bounded queues.
- Health/readiness separados.
- Crash-loop backoff e circuit breaker.
- Hot-swap somente em boundary registrada; runs podem optar por version pinning integral.
- Plugin nunca recebe grants brutos: apenas work leases já autorizadas.

### Gate G-W3

- Plugin de referência Rust e plugin de referência Python passam a mesma suíte.
- Core não importa nenhum módulo de plugin.
- Fault injection não derruba orchestrator nem corrompe ledger.
- Capability ceiling falha fechado.
- Todas as transições de lifecycle são replayáveis.

## WAVE 4 — Harness Compiler & Builder Experience

**Sentence:** *Um terceiro compõe, valida, compara e executa um harness sem alterar o core.*

### Sprint 4.1 — Compiler v2

- Resolver todos os plugin refs para digests.
- Validar compatibility, dependency graph, capability intersection e budgets.
- Produzir `FrozenHarness` byte-stable.
- Explicar conflicts de composição com path e remediation.

### Sprint 4.2 — Builder CLI/SDK

- `aether plugin validate`
- `aether harness scaffold`
- `aether harness validate`
- `aether harness compose`
- `aether harness diff`
- `aether run inspect/replay`

### Sprint 4.3 — Migração segura dos assets atuais

- Reempacotar apenas plugins necessários ao primeiro coding harness.
- Não portar wrappers e abstrações sem call-site de produção.
- Registrar no migration ledger cada comportamento preservado, substituído ou recusado.
- Começar migração de consumers por feature flag; legado continua reference-only.

### Gate G-W4 · G-MILESTONE B

- Mesmo manifest + artifacts produz mesmo harness digest em ambientes limpos.
- Troca de planner ou memory exige zero diff em crates do core.
- Plugin externo não-Python executa em isolamento real.
- Builder detecta incompatibilidade antes de iniciar um run.

---

# MILESTONE C — Autonomous Coding Project

**Waves 5–6**  
**Entrega:** primeiro coding agent real e, em seguida, múltiplos harness agents coordenados como um projeto autônomo.

## WAVE 5 — Coding Agent Vertical Slice

**Sentence:** *Um harness resolve uma tarefa de código real, com efeitos autorizados, evidência exterior e trajetória completa.*

### Sprint 5.1 — Coding plugins mínimos

- Model Gateway com streaming, usage e provider-independent errors.
- Filesystem e terminal toolkits.
- Repo index/context plugin com símbolos, imports e token budget.
- Patch plugin inicialmente textual/anchored; AST edits entram somente com benchmark favorável.
- Short-term memory e compaction plugin.
- Evaluation Gateway que apenas solicita e valida signed verdicts.

### Sprint 5.2 — Workspace execution

- Workspace isolado por run.
- Snapshot/checkpoint e rollback.
- Tool effects passam exclusivamente pelo kernel.
- Patch/test loop com causa de falha estruturada.
- Secrets e network separados da workspace do agent.

### Sprint 5.3 — Acceptance corpus

- Corpus pequeno, determinístico e pré-registrado para walking skeleton.
- Cassettes apenas para regression; release gate inclui modelo vivo.
- Baseline shell-only e A/A para medir ruído da infraestrutura.
- Registrar pass rate, custo, latency, turns e failure attribution.

### Gate G-W5

- Tarefa real termina com diff não vazio e signed verdict não-mockado.
- Toda model/tool call rastreável até plugin, versão, harness e causal parent.
- Nenhum coding concept aparece no core.
- Abort/restart preserva workspace e trajetória conforme policy.

## WAVE 6 — Multi-Agent Autonomous Project

**Sentence:** *Um ProjectManifest coordena múltiplos harnesses em paralelo, com workspaces isolados, artifacts tipados e decisão central auditável.*

### Sprint 6.1 — Project model

- `ProjectManifest`: roles, harness refs, budgets, acceptance gates e artifact contracts.
- Project planner/policy plugin propõe task graph; o core valida e agenda.
- Task leases atenuadas por agent.
- Project budget agrega reservas e commits de todos os filhos.

### Sprint 6.2 — Parallel agent execution

- Agentes executam em worktrees/workspaces independentes.
- Event ordering por `project_seq` e `agent_seq`, preservando causalidade.
- Nenhum total-order global entre projetos.
- Cancellation, timeout e reassignment por task.
- Comunicação apenas por events/artifacts tipados; sem chat invisível.

### Sprint 6.3 — Integration workflow

- Planner/executor/reviewer como primeira composição, sem hard-code desses papéis no core.
- Artifact handoff e provenance.
- Merge/conflict policy como plugin controlado.
- Exterior evaluator decide aceitação final.
- Failed reviewer ou executor pode ser substituído sem perder project state.

### Gate G-W6 · G-MILESTONE C

- Coordinator + pelo menos dois coding harnesses executam trabalho útil concorrente.
- Cada agent pode usar tecnologia/model/provider diferente.
- Kill de qualquer agent produz recovery ou reassignment determinístico.
- Project replay reconstrói task graph, artifacts, budgets, approvals e verdicts.
- Toda mudança aceita possui causal chain até command e evidence.

---

# MILESTONE D — Scale, Measurement & Meta-Harness

**Waves 7–9**  
**Entrega:** deployment distribuído, experimentação estatística e promoção auditável de melhorias.

## WAVE 7 — Distributed Control & Data Plane

**Sentence:** *O mesmo protocolo single-node escala por adapters, sem mudar semântica ou manifests.*

### Sprint 7.1 — Distributed stores

- PostgreSQL event/command store.
- S3/MinIO CAS.
- Transactional outbox para NATS JetStream.
- Consumers idempotentes e projection rebuild.

### Sprint 7.2 — Sharding e availability

- Shard por `project_id`.
- Ownership leases com fencing tokens.
- Orchestrator stateless fora do project lease.
- Backpressure, admission control e bounded resource pools.

### Sprint 7.3 — Operational observability

- OpenTelemetry exporter para traces, metrics e logs operacionais.
- Ledger continua source of truth semântico.
- Dashboards de queue depth, saturation, cost, failures e recovery.
- Chaos tests de partition, duplicate delivery e slow consumers.

### Gate G-W7

- Mesmo conformance suite passa em SQLite/local e PostgreSQL/distributed.
- Redelivery não duplica efeitos.
- Perda do project leader faz failover com fencing correto.
- Nenhum conteúdo sensível é exportado sem opt-in/policy.

## WAVE 8 — Experiment & Learning Plane

**Sentence:** *Toda mudança de harness pode ser avaliada contra controle com poder estatístico e atribuição causal.*

### Sprint 8.1 — Dataset e projections

- Trajectory materialization para Parquet/analytics.
- Views por project, harness, plugin, model, tool e failure cause.
- Data-quality gates: completeness, attribution e signature validity.
- Dataset versions content-addressed.

### Sprint 8.2 — Experiment service

- Preregistration de hipótese, métrica, population e stopping rule.
- Paired assignment e deterministic seeds/cassettes quando aplicável.
- A/A floor, power analysis, minimum detectable effect e confidence intervals.
- Multiple-testing correction e registro de todas as tentativas.

### Sprint 8.3 — Attribution

- Backward attribution sobre causal graph.
- Separar falha de model, context, tool, memory, policy, provider e infrastructure.
- Gerar candidate improvements; nenhuma mutação de produção ainda.

### Gate G-W8

- Um experimento completo pode ser reproduzido a partir de dataset + manifests + artifact digests.
- A/A respeita o false-positive budget pré-registrado.
- Nenhuma trajectory sem attribution entra no corpus de treino/promoção.

## WAVE 9 — Governed Meta-Harness

**Sentence:** *O sistema propõe, testa, promove e reverte melhorias sem autoridade para modificar diretamente produção.*

### Sprint 9.1 — Variant proposer

- Variantes limitadas inicialmente a manifest, skill, prompt asset e policy parameters.
- Mutation budget, forbidden fields e similarity/loop guard.
- Toda variante imutável, content-addressed e assinável.

### Sprint 9.2 — Promotion controller

- Promotion policy usa efeito mínimo, incerteza, custo e safety regressions.
- Aprovação humana configurável por classe de mudança.
- Canary por project cohort.
- Rollback por registry pointer; artifacts nunca são sobrescritos.

### Sprint 9.3 — Skill/model learning

- Harvest somente de episodes com evidence válido.
- Skill synthesis antes de fine-tuning por custo e reversibilidade.
- DPO/SFT export versionado.
- Model candidates passam pelos mesmos experiment gates antes de routing.

### Gate G-W9 · G-MILESTONE D

- Uma variante é proposta, avaliada, promovida em canary e revertida em exercício controlado.
- Meta-Harness não possui workspace write, evaluator key ou registry write direto.
- Promotion Controller é o único writer do production pointer.
- Histórico completo permite explicar por que a versão foi promovida.

---

# MILESTONE E — General Task Solver Falsification

**Wave 10**  
**Entrega:** prova de que AETHER é framework geral e não um coding runtime disfarçado.

## WAVE 10 — New Domain, Zero Core Diff

**Sentence:** *Um domínio estruturalmente diferente de coding é entregue apenas com novos plugins, manifests e evaluators.*

### Sprint 10.1 — Seleção do domínio

- Escolher tarefa com ferramentas, memória e critérios de sucesso diferentes de coding.
- Recomendados: data investigation, structured research ou operations planning.
- Pré-registrar corpus e exterior evaluator.

### Sprint 10.2 — Domain pack

- Implementar plugins necessários sem adicionar SPI específica ao domínio.
- Reusar orchestrator, scheduler, ledger, budgets e project model.
- Caso falte capacidade, primeiro provar que é extensão universal antes de alterar contrato.

### Sprint 10.3 — Generality test

- Rodar single-agent e multi-agent.
- Comparar trajectory, custo e recovery com coding project.
- Validar Builder UX com um integrador que não participou do core.

### Gate G-W10 · G-MILESTONE E

- `git diff` dos crates de core é vazio durante a criação do pack.
- Novo domínio executa end-to-end com signed evidence.
- Pelo menos um plugin é reutilizado sem modificação entre coding e o novo domínio.
- Nenhuma taxonomy ou role de coding virou conceito universal do core.

---

## 3. Gates transversais permanentes

### Correctness

- State = fold(events), provado em CI.
- Nenhum command sem terminal outcome ou reconciliation state.
- Nenhum controle mergeia sem production call-site test.
- Event schema, manifest schema e SDK generation sem drift.

### Security

- Plugins untrusted por default.
- Capability e isolation são autoridades independentes.
- Judge e signing keys exteriores.
- Network e secrets default-deny.
- Artifact digest + signature antes de activation.

### Performance

- Benchmarks desde W2: append p50/p95/p99, replay throughput, RPC overhead, memory/cell, scheduling latency e saturation.
- Regressão superior ao budget configurado bloqueia merge ou exige ADR com trade-off medido.
- Batching e async projection nunca podem relaxar durability do ledger.
- Otimização só entra com profile reproduzível.

### Data quality

- Todo evento tem attribution suficiente para explicar executor e versão.
- Conteúdo completo é blob protegido; envelope mantém digest/ref.
- Falhas possuem cause estruturada.
- Costs reconciliam por call, agent, run e project.

---

## 4. Política de desativação do legado

`vanguard/packages/` e o runtime Python não possuem data de deleção antecipada. Possuem condições de saída:

1. todas as semânticas preservadas possuem teste diferencial;
2. todos os consumers de produção usam AETHER v1;
3. rollback para v1 foi exercitado sem depender do runtime antigo;
4. nenhum artifact ou migration tool importa o legado;
5. duas releases completas ocorreram sem fallback;
6. Tech Lead aprova o relatório final de parity e intentionally-not-ported.

Depois dessas condições, o legado pode ser removido em uma task isolada e reversível por tag, sem misturar a remoção com feature work.

---

## 5. Resumo executivo

| Milestone | Waves | Entrega demonstrável |
|---|---:|---|
| **A — Foundation** | 1–2 | Protocolos, core Rust, ledger durável e replay/paridade |
| **B — Harness Builder** | 3–4 | Runtime real de plugins e composição polyglot |
| **C — Autonomous Coding Project** | 5–6 | Coding agent real e projeto multi-agent coordenado |
| **D — Scale & Meta-Harness** | 7–9 | Distribuição, experimentação e promoção governada |
| **E — Generality** | 10 | Novo domínio sem alteração no core |

### Caminho crítico

```text
Protocol Lock
  → Durable Core
  → Generic Plugin Runtime
  → Harness Builder
  → Coding Agent
  → Autonomous Coding Project
  → Distributed Runtime
  → Experiment Plane
  → Governed Meta-Harness
  → Generality Falsification
```

### Primeiro incremento a executar

Começar pela Wave 1. O primeiro PR deve criar os contratos `EventEnvelope v2`, `PluginManifest v2`, `HarnessManifest v2` e `ProjectManifest v1`, o pipeline Buf e a suíte de golden vectors cross-language. Nenhum plugin de produto deve ser portado antes desse gate.


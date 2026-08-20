# Vanguard Substrate 0.6.0 — Plano Final de Execução

**Documento:** `vanguard-substrate-060-execution-plan.md`
**Companheiro operacional de:** `Vanguard-substrate-060-full-refactor-v3.md` (relatório técnico e decisão)
**Relação:** o v3 responde *por quê*; este documento responde *o quê, em que ordem, com qual critério de aceite*.
**Decisão de stack incorporada:** **Python-first, Rust diferido.** O argumento do Rust é correção de concorrência, não performance; a mesma correção se obtém em Python redesenhando o ledger. O port fica atrás de um portão de decisão explícito (§ Gate de Decisão Rust, após M4), quando houver medição real. Estimativa de destino final: ~15–20% do backend (apenas o TCB) em Rust; ~80% permanece Python.

---

# PARTE 0 — GUIDELINES

## 0.1 Hierarquia de planejamento

```
Subtask  →  Task  →  Sprint  →  Wave  →  Milestone
```

| Nível | Definição | Duração típica |
|---|---|---|
| **Subtask** | Mudança atômica, owner único, reversível isoladamente | < 1 dia |
| **Task** | Entrega verificável por comando ou teste automatizado | 1–3 dias |
| **Sprint** | Incremento coerente que torna uma sentença verdadeira | 1–2 semanas |
| **Wave** | Conjunto de sprints terminando em gate de arquitetura | 2–6 semanas |
| **Milestone** | Capacidade demonstrável e utilizável, com release candidate | 1–3 meses |

## 0.2 Regras de entrada (Definition of Ready)

Nenhuma task entra no board sem os seis campos:

1. **Output** — arquivo, módulo ou teste identificado.
2. **Dependências** — explícitas, com IDs.
3. **Critério de aceite** — comando executável que retorna 0/1.
4. **Eventos e métricas produzidos** — o que passa a ser registrado.
5. **Comportamento de falha e rollback** — o que acontece quando quebra.
6. **Owner do estado autoritativo** — quem escreve, quem só lê.

## 0.3 Definition of Done

Uma task só fecha com todos:

- [ ] Critério de aceite executável passa em ambiente limpo.
- [ ] O controle merge **junto** com seu call-site de produção — nunca antes (regra de ativação; corrige AP-5).
- [ ] Nenhum valor emitido é constante quando deveria depender do input.
- [ ] Teste adversarial: existe teste que **falha** se a implementação for a preguiçosa.
- [ ] Eventos novos têm emissor real e payload derivado de estado observado.
- [ ] ADR registrado se houve decisão de arquitetura ou mudança de invariante.

## 0.4 Disciplina de gates (a lição central do v3)

> **Todo gate deve ser satisfeito apenas por comportamento observado em execução, nunca por presença lexical.**

**Procedimento obrigatório de criação de gate:**

1. Enuncie a propriedade desejada em uma frase.
2. Escreva o **código mais preguiçoso** que satisfaria o gate proposto.
3. Se esse código passa, o gate está errado — volte a (1).
4. Comite o código preguiçoso como **teste negativo permanente** (`test_planted_*_fails_closed`).

Isto falhou duas vezes no projeto (TCB-LOC, E-COV). Não pode falhar uma terceira.

| Propriedade | Gate errado | Gate correto |
|---|---|---|
| Emissão real | grep do nome do kind | Property test: payload varia com input; falha se constante |
| Veredito exterior | existe chamada ao gate | Injetar `fail` ⇒ run falha; assinatura inválida ⇒ rejeição |
| Replay | teste existe | Fold frio vs. estado vivo, diff estrutural, todo run de CI |
| TCB mínimo | contagem de LOC | Mutation score ≥ limiar em kernel + reducers |
| Controle ativo | teste unitário verde | Cobertura de call-site de produção |
| Domain-blindness | grep de tokens | grep **+** pack de outro domínio compila com core diff vazio |
| Isolamento | manifesto declara tier | Fault injection: escape deve falhar |
| Identidade de plugin | manifesto tem versão | 1 byte alterado ⇒ digest muda ⇒ harness digest muda |
| Determinismo | cassettes existem | Duas execuções ⇒ ledger byte-idêntico |
| Qualidade de dado | schema valida | Trajetória sem atribuição não entra no corpus |

## 0.5 Invariantes do substrato

Substituem I-1…I-11. Mudança exige ADR com condição de reversão — **nunca edição silenciosa**.

| ID | Invariante |
|---|---|
| **S-1** | Um único `EffectRequest`, gerado de schema, usado no dispatch, na wire e nos adapters. |
| **S-2** | Emitido = declarado **e semanticamente real**. Emissão constante é defeito. |
| **S-3** | Um controle merge com seu call-site de produção. |
| **S-4** | `state = fold(events)`, provado por replay-parity em todo CI. |
| **S-5** | O juiz é exterior, assinado e **sua resposta é lida e determina o resultado**. |
| **S-6** | Plugins são não-confiáveis por padrão; `in_process` é privilégio, não default. |
| **S-7** | O core é domain-blind. |
| **S-8** | Especificações são geradas **ou** normativas — nunca ambas. |
| **S-9** | Telemetria é dataset: toda trajetória é linha válida de harvest, sem transformação. |
| **S-10** | Metáforas vão em comentários, nunca em arquitetura. |
| **S-11** | Unidade de consistência é `project_id`. Não há ordem total global. |
| **S-12** | Identidade e digest em JCS; Protobuf é transporte, nunca identidade. |
| **S-13** | Nenhum gate é satisfeito por presença lexical. |
| **S-14** | Promoção do Learning Plane exige avaliação pareada, correção de múltiplos testes e rollback exercitado. |

## 0.6 Trilha transversal de cognição (C-1…C-5)

Obrigação de **toda** wave. Dado não capturado no momento do evento é irrecuperável.

| ID | Princípio | Consequência prática |
|---|---|---|
| **C-1** | Toda trajetória é linha válida de harvest | Gate de CI valida contra schema de treino |
| **C-2** | Todo evento carrega atribuição | `harness_digest` + `plugin_digests` + `model_route` |
| **C-3** | Todo insucesso carrega causa nomeada | Taxonomia fechada; proibido `failed` sem `cause` |
| **C-4** | Todo custo é 6-dimensional | `{usd_micros, millis, tokens, bytes, turns, depth}` |
| **C-5** | Nenhum aprendizado sem pré-registro | Hipótese, métrica, população e regra de parada antes de rodar |

**Checklist de fim de wave:** *"Se ligássemos o Learning Plane hoje, que perguntas os dados desta wave responderiam?"* A resposta deve crescer a cada wave.

## 0.7 Convenções de desenvolvimento

- **Python 3.12+**, type hints obrigatórios em fronteiras, `from __future__ import annotations`.
- **Stdlib-only no core**; dependências apenas em adapters/plugins.
- **pytest** (migração de `unittest` na Wave 0).
- Nomes: `snake_case` para módulos/funções, `PascalCase` para classes, SPIs prefixadas com `I`.
- Commits: `feat(escopo):`, `fix(escopo):`, `docs:`, `chore:`; corpo cita ADR ou task ID.
- PR: descreve comportamento, cita comando de verificação, lista eventos novos.
- **Proibido**: tipo de domínio escrito à mão quando existe schema; comparação de seletor fora do módulo canônico; import de plugin pelo core.

## 0.8 Política do legado

`vanguard/packages/` **não tem data de deleção** — tem condições de saída:

1. Toda semântica preservada tem teste diferencial.
2. Todos os consumidores de produção usam o substrato novo.
3. Rollback exercitado sem depender do runtime antigo.
4. Nenhum artifact ou ferramenta de migração importa o legado.
5. Duas releases completas sem fallback.
6. Relatório de paridade e de *intentionally-not-ported* aprovado.

Satisfeitas: remoção em task isolada, reversível por tag, sem misturar com feature work.

---

# PARTE 1 — CONJUNTO DOCUMENTAL

## 1.1 Estrutura de destino

```
docs/
├── SPEC.md                          # NORMATIVO — único
├── 00_guidelines/
│   ├── DEVELOPMENT.md               # §0.7 expandido
│   ├── GATES.md                     # §0.4 — disciplina anti-Goodhart
│   ├── ADR_PROCESS.md               # como se decide e como se reverte
│   ├── DEFINITION_OF_DONE.md        # §0.2–0.3
│   └── COGNITION_TRACK.md           # C-1…C-5
├── 01_concepts/
│   ├── CONCEPT_LOCK.md              # vocabulário congelado
│   ├── INVARIANTS.md                # S-1…S-14
│   └── GLOSSARY.md                  # termo → definição → onde vive no código
├── 02_roadmap/
│   ├── milestones.md                # M0–M7 (este documento, resumido)
│   └── backlog.md                   # itens fora de milestone, com disposição
├── 03_sprints/
│   ├── sprint_active.md             # board único, sempre atual
│   ├── plans/                       # waves futuras, staged
│   └── evidence/                    # digest-referenced, nunca conteúdo bruto
├── 04_annex/
│   ├── KERNEL.md                    # NORMATIVO — dispatch, grants, atenuação
│   ├── MEASUREMENT.md               # NORMATIVO — power, McNemar, A/A, FDR
│   ├── LEDGER.md                    # NORMATIVO (novo) — envelope, ordem, durabilidade
│   └── THREAT_MODEL.md              # NORMATIVO (novo) — tiers, ameaças, não-garantias
├── 05_adr/                          # append-only, cada um com condição de reversão
└── 06_references/                   # evidência, não lei
```

## 1.2 Documentos a criar na Wave 0

| Documento | Conteúdo | Substitui |
|---|---|---|
| `00_guidelines/GATES.md` | Disciplina anti-Goodhart, tabela de gates, procedimento de criação | — (novo, crítico) |
| `00_guidelines/DEVELOPMENT.md` | Convenções, setup (incl. `bwrap`), comandos, estrutura | AGENTS.md disperso |
| `00_guidelines/ADR_PROCESS.md` | Formato, numeração, condição de reversão, quem assina | implícito |
| `00_guidelines/DEFINITION_OF_DONE.md` | DoR + DoD | — |
| `00_guidelines/COGNITION_TRACK.md` | C-1…C-5 com exemplos e gates | — |
| `01_concepts/CONCEPT_LOCK.md` | Vocabulário congelado: plane, harness, pack, plugin, cell, lease, grant, verdict, trajectory | dispersão atual |
| `01_concepts/INVARIANTS.md` | S-1…S-14 com rationale e teste que os prova | I-1…I-11 |
| `01_concepts/GLOSSARY.md` | Termo → definição → módulo | — |
| `04_annex/LEDGER.md` | Envelope v2, ordem parcial, durabilidade, outbox, recuperação | — (novo) |
| `04_annex/THREAT_MODEL.md` | Tiers, ameaças cobertas e **explicitamente não cobertas** | — (novo) |

## 1.3 Documentos a reescrever

| Documento | Ação |
|---|---|
| `README.md` | Reduzir a ponteiro: tese em 1 parágrafo, tabela de camadas reais, links. Remover árvore obsoleta, roadmap morto, six-plane, config de modelos em prosa |
| `docs/SPEC.md` | Reescrever refletindo o substrato: 5 planos, envelope v2, S-1…S-14. Remover descrição do `layer0` como "destino M1" |
| `CLAUDE.md` / `AGENTS.md` | Apontar para `00_guidelines/`; documentar `bwrap`; explicitar o que CI roda e o que não roda |
| `docs/02_roadmap/milestones.md` | Substituir M0–M6 antigos por M0–M7 deste plano |
| `docs/03_sprints/sprint_active.md` | Board da Wave 0, formato novo |

## 1.4 Documentos a arquivar ou remover

| Item | Ação | Motivo |
|---|---|---|
| `vanguard_body_detailed.md` | Remover | Cosmologia órfã; ADR-M0-10 |
| `workflow_visualizer.html` | Remover | Órfão, 48K |
| `benchmark_results.json` | Mover para evidência por digest | Artefato de execução |
| `wave_6A/6B/7_project_lead.md` | Arquivar com nota de revogação | Briefs de meta-cognição prematuros |
| `tools/002_LLM_API_MOCK/lam.sqlite` | `git rm --cached` + gitignore | Banco versionado |
| Suítes de benchmark duplicadas | Consolidar em uma árvore | `zero_hint_v1`, `tasks_phase2`, `tasks_phase2_LAM`, `lab/tasks` |
| `vanguard-gui/`, `vanguard-ide/` | Repositórios separados | Fora de escopo backend |

## 1.5 ADRs da Wave 0

| ADR | Título | Conteúdo |
|---|---|---|
| **ADR-060-01** | Substrato 0.6.0: replatformização com Python-first | Decisão central; `layer0` reclassificado; Python de referência vira produção evoluída |
| **ADR-060-02** | Rust diferido atrás de portão de decisão | Justificativa é correção de concorrência, não performance; contra-argumento registrado; gate após M4 |
| **ADR-060-03** | Gates comportamentais; proibição de gate lexical | S-13; procedimento §0.4; retirada do E-COV atual |
| **ADR-060-04** | Ordem parcial: `project_id` como unidade de consistência | S-11; substitui I-11 (scheduler sequencial) com condições C1–C6 |
| **ADR-060-05** | Identidade em JCS; Protobuf apenas transporte | S-12 |
| **ADR-060-06** | Álgebra de seletores única | Delegação obrigatória; corrige F4/F5 |
| **ADR-060-07** | Hierarquia de planejamento e trilha de cognição | §0.1, C-1…C-5 |
| **ADR-060-08** | Condições de saída do legado (sem data de deleção) | §0.8 |
| **ADR-060-09** | Corpus pré-substrato descartado | Vereditos sintéticos contaminam harvest (risco K-9) |
| **ADR-060-10** | Escopo anti-metafísica estendido a todo o repositório | Amplia ADR-M0-10 |

---

# PARTE 2 — MILESTONES, WAVES, SPRINTS E TASKS

## Visão geral

| Milestone | Waves | Entrega demonstrável |
|---|---|---|
| **M0 — Concept Lock & Base Limpa** | 0 | Documentação verdadeira, conceitos travados, bloat removido |
| **M1 — Núcleo Verdadeiro** | 1–2 | Fatia vertical real, contratos derivados de evidência, ledger durável |
| **M2 — Runtime Real de Plugins** | 3–4 | Plugins isolados e substituíveis, builder funcional |
| **M3 — Coding Agent** | 5 | Um harness resolve tarefa real com veredito assinado |
| **M4 — Projeto Autônomo** | 6–7 | N harnesses em paralelo sob orquestrador autoritativo |
| **⟐ Gate de Decisão Rust** | — | Medição decide se o TCB migra |
| **M5 — Escala e Experimentação** | 8–9 | Distribuído + plano de experimentos com poder estatístico |
| **M6 — Meta-Harness Governado** | 10 | Variante promovida e revertida sob controle |
| **M7 — Falsificação de Generalidade** | 11 | Novo domínio com core diff vazio |

---

# MILESTONE M0 — Concept Lock & Base Limpa

**Wave 0** · *Entrega: a documentação descreve o sistema que existe; o vocabulário está travado; o repositório carrega código e schemas.*

## WAVE 0 — Verdade, Conceito e Higiene

### Sprint 0.1 — Guidelines e conceito

**Sentence:** *Existe um conjunto único de regras de desenvolvimento, e nenhum gate pode ser satisfeito por string.*

**Task 0.1.1 — `GATES.md` e retirada do E-COV lexical**
- 0.1.1.a — Escrever `00_guidelines/GATES.md` com §0.4 completo.
- 0.1.1.b — Auditar os 10 gates existentes; classificar lexical vs. comportamental.
- 0.1.1.c — Para cada gate lexical, escrever o código preguiçoso que o satisfaz e comitá-lo como teste negativo.
- 0.1.1.d — Marcar `check_event_coverage.py` como **não-normativo** até substituição comportamental (M1).
- ✅ `pytest test/gates/test_planted_failures.py` — todos os plantados falham fechado.

**Task 0.1.2 — Concept Lock**
- 0.1.2.a — `01_concepts/CONCEPT_LOCK.md`: definir plane, harness, pack, plugin, cell, lease, grant, verdict, trajectory, project, run, agent, episode, turn.
- 0.1.2.b — `01_concepts/GLOSSARY.md`: termo → definição → módulo onde vive.
- 0.1.2.c — `01_concepts/INVARIANTS.md`: S-1…S-14 com rationale e teste que prova cada um.
- 0.1.2.d — Gate: termo usado no código sem entrada no glossário falha o lint de documentação.
- ✅ `python3 tools/check_glossary.py`

**Task 0.1.3 — Guidelines operacionais**
- 0.1.3.a — `DEVELOPMENT.md`: convenções, setup (**incluindo `bwrap` e requisito de user namespaces**), comandos, o que CI roda e o que não roda.
- 0.1.3.b — `ADR_PROCESS.md`: formato, numeração, condição de reversão obrigatória, quem assina.
- 0.1.3.c — `DEFINITION_OF_DONE.md`: DoR (6 campos) + DoD (6 checkboxes).
- 0.1.3.d — `COGNITION_TRACK.md`: C-1…C-5 com exemplo por princípio.

### Sprint 0.2 — Documentação verdadeira

**Sentence:** *Nenhum documento descreve um sistema que não existe.*

**Task 0.2.1 — README como ponteiro**
- 0.2.1.a — Remover árvore de diretórios obsoleta.
- 0.2.1.b — Remover roadmap "PHASE 1/2/3 · Sprint 7–10".
- 0.2.1.c — Remover §2/§3 (taxonomia aposentada e six-plane).
- 0.2.1.d — Escrever: tese em 1 parágrafo + tabela de camadas reais + links normativos.
- 0.2.1.e — Mover config de modelos para `config/model-routes.yaml` schema-validado.

**Task 0.2.2 — SPEC.md v2**
- 0.2.2.a — Reescrever §1 refletindo os 5 planos.
- 0.2.2.b — Substituir I-1…I-11 por S-1…S-14 com ponteiro para `INVARIANTS.md`.
- 0.2.2.c — Varredura de TBD/TODO/contradições.
- 0.2.2.d — Registrar F1–F9 como **estado conhecido**, não como resolvido.

**Task 0.2.3 — Annexes novos**
- 0.2.3.a — `04_annex/LEDGER.md`: envelope v2, ordem parcial, durabilidade, outbox, recuperação.
- 0.2.3.b — `04_annex/THREAT_MODEL.md`: tiers, ameaças cobertas e **explicitamente não cobertas** (timing, cache, esgotamento de kernel).
- 0.2.3.c — Atualizar `MEASUREMENT.md`: power analysis, FDR, MDE, regra de parada.

**Task 0.2.4 — CLAUDE.md / AGENTS.md**
- 0.2.4.a — Apontar para `00_guidelines/`.
- 0.2.4.b — Documentar dependência `bwrap` e por que o dogfood fica `undeterminable` em container aninhado.
- 0.2.4.c — Explicitar cobertura real da CI.

### Sprint 0.3 — Higiene e ADRs

**Sentence:** *O repositório carrega código, schemas e vetores — nada mais.*

**Task 0.3.1 — Purga**
- 0.3.1.a — Remover `vanguard_body_detailed.md`, `workflow_visualizer.html`.
- 0.3.1.b — `git rm --cached tools/002_LLM_API_MOCK/lam.sqlite`; gitignore `*.sqlite`, `runs/`, `outputs/`.
- 0.3.1.c — Corrigir linha placeholder do `.gitignore`.
- 0.3.1.d — Consolidar suítes de benchmark duplicadas.
- 0.3.1.e — Arquivar `wave_6A/6B/7_project_lead.md` com nota de revogação.
- 0.3.1.f — Extrair `vanguard-gui/` e `vanguard-ide/` para repositórios próprios.
- 0.3.1.g — `tools/check_metaphysics.py` — gate estendido a todo o repositório.

**Task 0.3.2 — Higiene de testes**
- 0.3.2.a — Migrar `unittest` → `pytest`; mapa de portabilidade comitado.
- 0.3.2.b — Skip guard para testes dependentes de Ollama.
- 0.3.2.c — Corrigir poluição de ordem (`test_evaluator_daemon`, `test_plugin_isolation`).
- 0.3.2.d — Marcar testes que exigem `bwrap` com marker `requires_sandbox`.
- ✅ `pytest -q` determinístico em máquina limpa.

**Task 0.3.3 — ADRs 01–10**
- 0.3.3.a–j — Redigir e assinar os dez ADRs de §1.5.

### 🚪 Gate G-W0 (= **G-M0**)

```bash
pytest -q                                    # determinístico
python3 tools/check_glossary.py
python3 tools/check_metaphysics.py
python3 tools/check_markdown_links.py
python3 tools/check_stale_paths.py
python3 tools/scan_secrets.py
pytest test/gates/test_planted_failures.py   # todos plantados falham fechado
```

- [ ] Todo gate classificado; nenhum gate lexical é normativo.
- [ ] Todo termo do código tem entrada no glossário.
- [ ] Zero arquivo órfão; zero binário versionado.
- [ ] 10 ADRs assinados.

**📊 Cognição W0:** taxonomia de causa de falha (C-3) definida e schema-validada.

---

# MILESTONE M1 — Núcleo Verdadeiro

**Waves 1–2** · *Entrega: um caminho real ponta a ponta, contratos derivados dele, e um ledger que sobrevive a crash.*

## WAVE 1 — Fatia Vertical + Contract Lock

**Sentence:** *Uma tarefa real é resolvida com veredito exterior assinado, e os contratos descrevem esse comportamento observado.*

⚠️ **A ordem dos sprints 1.1 e 1.2 é inegociável.** Congelar contratos antes de observar comportamento é o erro que produziu `verdict: "pass"`.

### Sprint 1.1 — Fatia vertical real

**Task 1.1.1 — Remover semântica sintética**
- 1.1.1.a — Eliminar `verdict: "pass"` literal do scheduler; ler resposta do gate.
- 1.1.1.b — Eliminar `InvalidationChecked{ok: True}` literal.
- 1.1.1.c — Eliminar `TrajectoryRef(digest="sha256:000…")`; computar digest real.
- 1.1.1.d — `CLAIM_RECORDED` com payload derivado de evidência, não de `len(receipts)`.
- ✅ Teste: injetar veredito `fail` ⇒ run **falha**; assinatura inválida ⇒ rejeição.

**Task 1.1.2 — Caminho ponta a ponta**
- 1.1.2.a — Tarefa de código real, repositório de fixture, bug determinístico.
- 1.1.2.b — Todo efeito pelo dispatch do kernel; zero segundo caminho.
- 1.1.2.c — Avaliador exterior em processo separado, Ed25519, resposta lida pelo chamador.
- 1.1.2.d — Trajetória completa com atribuição (C-2) e custo 6-dim (C-4).
- ✅ Diff não-vazio no disco + veredito assinado não-mockado.

**Task 1.1.3 — Observação para derivar contratos**
- 1.1.3.a — Registrar o ledger real produzido pela fatia como fixture normativa.
- 1.1.3.b — Documentar cada campo efetivamente usado vs. presumido.
- 1.1.3.c — Lista de campos que se mostraram desnecessários (candidatos a corte).

### Sprint 1.2 — Contratos canônicos

**Task 1.2.1 — Event Envelope v2**
- 1.2.1.a — `project_id`, `run_id`, `agent_id`, `harness_digest`, `plugin_digest`.
- 1.2.1.b — `project_seq`, `agent_seq`, `prev_digest`, relógio lógico híbrido.
- 1.2.1.c — `causation_id`, `correlation_id`, `command_id`, `idempotency_key`.
- 1.2.1.d — `payload_digest` / `blob_ref` — conteúdo fora do envelope por padrão.
- 1.2.1.e — JCS como representação de identidade e assinatura (S-12).

**Task 1.2.2 — Manifests v2**
- 1.2.2.a — `PluginManifest v2`: protocol version, artifact digest, capabilities, isolation, resource requirements, config schema.
- 1.2.2.b — `HarnessManifest v2`.
- 1.2.2.c — `ProjectManifest v1`: roles, harness refs, budgets, acceptance gates, contratos de artifact.
- 1.2.2.d — Refs sempre resolvidas para digest imutável na composição.

**Task 1.2.3 — Lifecycle e serviços tipados**
- 1.2.3.a — `Describe · Init · Health · Invoke · Checkpoint · Quiesce · Shutdown`.
- 1.2.3.b — Serviços: Planner, Context, Memory, Model Gateway, Tool/Effect Adapter, Evaluation Gateway, Project Policy.
- 1.2.3.c — Deadlines, cancelamento e erros estruturados obrigatórios em toda chamada.

**Task 1.2.4 — Toolchain de schema**
- 1.2.4.a — JSON Schema como fonte; dataclasses Python **geradas**.
- 1.2.4.b — Golden vectors importados para `conformance/`.
- 1.2.4.c — Detecção de breaking change entre versões de schema.
- 1.2.4.d — Proibir tipo de domínio escrito à mão (gate).

### Sprint 1.3 — Contrato de dados de aprendizagem

**Task 1.3.1 — Trajectory v2** — projeção determinística de eventos; linha válida de harvest sem transformação (C-1/S-9).
**Task 1.3.2 — Taxonomia fechada de causas** — versionada, extensível; proibido `failed` sem `cause` (C-3).
**Task 1.3.3 — Custo multidimensional** — em model calls, tool calls e totais de projeto (C-4).
**Task 1.3.4 — Políticas de dado** — redação, criptografia, captura de conteúdo, retenção.

### 🚪 Gate G-W1

- [ ] Fatia vertical roda com veredito exterior **real**; injeção de `fail` faz o run falhar.
- [ ] Schemas geram tipos sem diff após regeneração.
- [ ] Golden vectors idênticos entre implementações.
- [ ] Nenhum digest depende de bytes de serialização não-canônica.
- [ ] Todo command tem idempotency key, deadline e resposta terminal.
- [ ] Contratos rastreáveis a campo observado na fatia (task 1.1.3).

## WAVE 2 — Ledger Durável e Orquestrador Autoritativo

**Sentence:** *Um projeto executa e recupera seu estado exclusivamente a partir de eventos duráveis.*

### Sprint 2.1 — Ledger e blobs

**Task 2.1.1 — Append-only durável** — SQLite WAL, `synchronous=FULL`; premissas de durabilidade documentadas.
**Task 2.1.2 — Commit atômico** — command state + event + outbox numa transação.
**Task 2.1.3 — CAS** — `write → fsync → event(blob_ref)`; evento nunca referencia blob não-durável.
**Task 2.1.4 — Reducers puros** — project, run, budget, grants, approvals, plugin lifecycle.
**Task 2.1.5 — Replay** — cold start reconstrói 100% do estado observável; branch de time-travel.

### Sprint 2.2 — Kernel e ordem parcial

**Task 2.2.1 — Redesenho do ledger para ordem parcial** — `project_seq` autoritativo por projeto, `agent_seq` local; sem ordem total global (S-11). Corrige **F3**.
**Task 2.2.2 — Sincronização explícita** — append serializado por projeto com lock; corrida impossível por construção.
**Task 2.2.3 — Álgebra de seletores única** — `ceiling` delega para o módulo canônico; gate proíbe comparação fora dele. Corrige **F4**.
**Task 2.2.4 — Fail-closed em ceiling vazio** — schema torna `capabilities` obrigatório. Corrige **F5**.
**Task 2.2.5 — Provenance viva** — spans acumulam; remover confiança hard-coded; `revoke` com chamador real (D-05/D-06/D-07/D-15).

### Sprint 2.3 — Orquestrador single-node

**Task 2.3.1 — State machines** — Project / Run / Agent, puras.
**Task 2.3.2 — Ownership** — um lease autoritativo por projeto.
**Task 2.3.3 — Comandos** — deduplicação, retry seguro, resposta terminal obrigatória.
**Task 2.3.4 — Ciclo operacional** — heartbeat, cancelamento, recuperação, estado terminal.
**Task 2.3.5 — Benchmarks baseline** — append p50/p95/p99, replay throughput, memória, startup. **Regression budget desde aqui.**

### 🚪 Gate G-W2 (= **G-M1**)

- [ ] Kill/restart entre qualquer command e event: sem perda nem duplicação lógica.
- [ ] Replay cold-start reconstrói 100% do estado observável.
- [ ] **Nenhum verdict, claim ou checkpoint sintético** (gate comportamental).
- [ ] Mutation score ≥ 80% em kernel + reducers.
- [ ] Baseline de performance salvo e versionado.

---

# MILESTONE M2 — Runtime Real de Plugins

**Waves 3–4** · *Entrega: plugins realmente substituíveis e isolados; harnesses compilados por digest.*

## WAVE 3 — Supervisor Genérico

**Sentence:** *Qualquer plugin compatível pode ser verificado, iniciado, chamado, interrompido e substituído sem import no core.*

### Sprint 3.1 — Registry e supply chain
- **3.1.1** — Artifacts resolvidos por digest, nunca por tag mutável.
- **3.1.2** — Verificação de assinatura, attestation, SBOM, compatibilidade de protocolo.
- **3.1.3** — **Identidade sobre bytes**: `H(JCS(manifest) ‖ H(artifact) ‖ H(assets) ‖ H(prompts) ‖ H(policies))`. Corrige **F8**.
- **3.1.4** — Lifecycle ledgerado: discovered → verified → activated → quiesced → retired/faulted.

### Sprint 3.2 — Isolamento
- **3.2.1** — `in_process` restrito a TCB auditado, por política de registry.
- **3.2.2** — `subprocess` com identity, rlimits **aplicados**, no-new-privs, FS policy. Fecha D-31.
- **3.2.3** — `container` rootless para execução de ferramentas e código de modelo. Corrige **F9**.
- **3.2.4** — Rede default-deny com grants explícitos.
- **3.2.5** — stdout/stderr sempre em blob ref, associados à chamada.
- **3.2.6** — Teste: chave do avaliador inalcançável de qualquer cela.

### Sprint 3.3 — Semântica de runtime
- **3.3.1** — Deadlines e cancelamento cooperativo.
- **3.3.2** — Backpressure e filas limitadas.
- **3.3.3** — Health e readiness separados.
- **3.3.4** — Crash-loop backoff e circuit breaker.
- **3.3.5** — Hot-swap só em fronteira registrada, com atribuição no ledger; version pinning opcional.
- **3.3.6** — Plugin recebe **work lease**, nunca grant bruto.
- **3.3.7** — Substituir o worker fixture por runtime genérico. Corrige **F7**.

### 🚪 Gate G-W3
- [ ] Dois plugins de referência (linguagens diferentes) passam a mesma suíte.
- [ ] Core não importa nenhum módulo de plugin (gate estático + runtime).
- [ ] Fault injection não derruba orquestrador nem corrompe ledger.
- [ ] Capability ceiling falha fechado.
- [ ] Todas as transições de lifecycle replayáveis.
- [ ] 1 byte alterado no artifact ⇒ digest muda ⇒ harness digest muda.

## WAVE 4 — Compiler e Builder

**Sentence:** *Um terceiro compõe, valida, compara e executa um harness sem alterar o core.*

### Sprint 4.1 — Compiler v2
- **4.1.1** — Resolver todos os refs para digests.
- **4.1.2** — Validar compatibilidade, grafo de dependências, interseção de capabilities e budgets.
- **4.1.3** — `FrozenHarness` byte-stable.
- **4.1.4** — Explicar conflitos com path e remediação.

### Sprint 4.2 — Builder CLI
- **4.2.1** — `plugin validate`
- **4.2.2** — `harness scaffold | validate | compose | diff`
- **4.2.3** — `run inspect | replay`
- **4.2.4** — Catálogo de plugins e documentação **gerada** dos schemas.

### Sprint 4.3 — Migração seletiva
- **4.3.1** — Reempacotar apenas plugins necessários ao primeiro coding harness.
- **4.3.2** — Não portar wrapper sem call-site de produção.
- **4.3.3** — Migration ledger: preservado / substituído / **recusado**, com motivo.
- **4.3.4** — Migrar consumidores por feature flag; legado reference-only.

### 🚪 Gate G-W4 (= **G-M2**)
- [ ] Mesmo manifest + artifacts ⇒ mesmo harness digest em ambiente limpo.
- [ ] Trocar planner ou memory ⇒ **zero diff** no core.
- [ ] Plugin não-Python executa em isolamento real.
- [ ] Builder detecta incompatibilidade antes de iniciar run.

---

# MILESTONE M3 — Coding Agent

**Wave 5** · *Entrega: um harness resolve tarefa de código real com evidência exterior.*

### Sprint 5.1 — Plugins mínimos
- **5.1.1** — Model Gateway: streaming, usage, erros provider-independent.
- **5.1.2** — Filesystem e terminal toolkits (primeira falha estruturada, p95 < 300ms).
- **5.1.3** — Repo index/context: símbolos, imports, orçamento de tokens.
- **5.1.4** — Patch **textual/anchored**; AST edits só entram com benchmark favorável.
- **5.1.5** — Memória de curto prazo e compaction.
- **5.1.6** — Evaluation Gateway: apenas solicita e valida verdicts assinados.

### Sprint 5.2 — Execução em workspace
- **5.2.1** — Workspace isolado por run.
- **5.2.2** — Snapshot/checkpoint e rollback.
- **5.2.3** — Efeitos exclusivamente pelo kernel.
- **5.2.4** — Loop patch/test com causa de falha estruturada (C-3).
- **5.2.5** — Secrets e rede separados do workspace do agente.

### Sprint 5.3 — Corpus de aceitação
- **5.3.1** — Corpus pequeno, determinístico, pré-registrado.
- **5.3.2** — Cassettes para regressão; **modelo vivo no gate de release**.
- **5.3.3** — Baseline shell-only e piso A/A para medir ruído da infraestrutura.
- **5.3.4** — Registrar pass rate, custo, latência, turns e atribuição de falha.

### 🚪 Gate G-W5 (= **G-M3**)
- [ ] Tarefa real termina com diff não-vazio e **verdict assinado não-mockado**.
- [ ] Toda model/tool call rastreável até plugin, versão, harness e pai causal.
- [ ] Nenhum conceito de coding no core (grep + pack de outro domínio compila).
- [ ] Abort/restart preserva workspace e trajetória conforme policy.

**📊 Cognição M3:** primeira massa de trajetórias **válidas**. O corpus começa aqui (ADR-060-09).

---

# MILESTONE M4 — Projeto Autônomo

**Waves 6–7** · *Entrega: N harnesses em paralelo sob orquestrador autoritativo.*

## WAVE 6 — Paralelismo Seguro

### Sprint 6.1 — Condições de concorrência
- **6.1.1** — Implementar C1: disjunção de recursos via álgebra única.
- **6.1.2** — C2: resolução de aliasing (realpath/inode) ou proibição de symlink por mount policy.
- **6.1.3** — C3: isolamento de canal lateral (container + net default-deny).
- **6.1.4** — C4: migrar `fs.*` para semântica de handle (`openat`/`*at()`) — elimina TOCTOU.
- **6.1.5** — C5: regra de merge determinística por `(project_seq, agent_id, agent_seq)`.
- **6.1.6** — C6: idempotência/compensação sob recuperação parcial.

### Sprint 6.2 — Scheduler concorrente
- **6.2.1** — Grupos de independência com prova de não-interseção antes do dispatch.
- **6.2.2** — Tokens de cancelamento cooperativo.
- **6.2.3** — Admission control por **pior caso simultâneo**, não soma esperada.
- **6.2.4** — `spawn()` real: executa filho, spans de provenance preenchidos. Fecha D-06.
- **6.2.5** — `depth` como dimensão de reserva enforçada; orçamento do filho atenuado do pai.

### 🚪 Gate G-W6
- [ ] **Replay-parity verde sob concorrência** (duas execuções ⇒ ledger byte-idêntico).
- [ ] Zero corrida em stress test.
- [ ] Ganho de latência medido vs. sequencial.
- [ ] Revogação de capability interrompe trabalho em andamento.

## WAVE 7 — Projeto Multi-Agente

### Sprint 7.1 — Modelo de projeto
- **7.1.1** — `ProjectManifest`: roles, harness refs, budgets, acceptance gates, contratos de artifact.
- **7.1.2** — Project planner/policy propõe task graph; **o core valida e agenda**.
- **7.1.3** — Task leases atenuadas por agente.
- **7.1.4** — Budget de projeto agrega reservas e commits dos filhos.

### Sprint 7.2 — Execução paralela
- **7.2.1** — Worktrees/workspaces independentes por agente.
- **7.2.2** — Comunicação apenas por eventos e artifacts tipados — **sem chat invisível**.
- **7.2.3** — Cancelamento, timeout e reassignment por task.

### Sprint 7.3 — Workflow de integração
- **7.3.1** — Planner/executor/reviewer como composição, **sem hard-code no core**.
- **7.3.2** — Artifact handoff e proveniência.
- **7.3.3** — Merge/conflict policy como plugin.
- **7.3.4** — Avaliador exterior decide aceitação final.
- **7.3.5** — Agente falho substituível sem perder estado do projeto.

### 🚪 Gate G-W7 (= **G-M4**)
- [ ] Coordinator + ≥2 harnesses fazem trabalho concorrente útil.
- [ ] Cada agente pode usar modelo/provider diferente.
- [ ] Kill de qualquer agente ⇒ recovery ou reassignment determinístico.
- [ ] Project replay reconstrói task graph, artifacts, budgets, approvals e verdicts.
- [ ] Toda mudança aceita tem cadeia causal até command e evidence.

---

# ⟐ GATE DE DECISÃO RUST

**Após G-M4.** Neste ponto existe concorrência real, medida, com benchmarks de duas waves.

**Decidir migrar o TCB para Rust se e somente se:**

| Critério | Limiar |
|---|---|
| Contenção no append do ledger | > 15% do tempo de parede sob carga alvo |
| Defeitos de concorrência escapados para main | ≥ 2 no período |
| Capacidade da equipe | ≥ 1 engenheiro com Rust em produção, sustentável |
| Horizonte do produto | ≥ 24 meses |

**Escopo se aprovado:** ledger/append, kernel de capabilities e budget, scheduler, plugin supervisor. **~15–20% do backend.** Os ~80% restantes — planners, context, memória, model gateways, toolkits, evaluation clients, learning plane — permanecem Python permanentemente.

**Método:** strangler com teste diferencial. Python vira oráculo; divergência em decisão, digest, receipt ou sequência de eventos **bloqueia merge**.

**Se reprovado:** manter Python; revisitar após M5. Registrar em ADR com os números medidos.

---

# MILESTONE M5 — Escala e Experimentação

## WAVE 8 — Plano Distribuído
- **Sprint 8.1** — PostgreSQL event/command store; S3/MinIO CAS; outbox → NATS JetStream; consumidores idempotentes; rebuild de projeções.
- **Sprint 8.2** — Shard por `project_id`; leases com **fencing tokens**; orquestrador stateless fora do lease; backpressure e pools limitados.
- **Sprint 8.3** — OpenTelemetry como **exporter** (ledger continua fonte da verdade); dashboards; chaos (partição, entrega duplicada, consumidor lento).

**🚪 G-W8:** mesma suíte passa em SQLite/local e Postgres/distribuído · redelivery não duplica efeito · failover com fencing correto · nada sensível exportado sem opt-in.

## WAVE 9 — Plano de Experimentos
- **Sprint 9.1** — Materialização de trajetórias (Parquet); views por project/harness/plugin/model/tool/cause; datasets content-addressed; data-quality gates.
- **Sprint 9.2** — Experiment service: pré-registro de hipótese, métrica, população e **regra de parada**; assignment pareado; piso A/A; power analysis; MDE; IC; correção de múltiplos testes; **registro de todas as tentativas**.
- **Sprint 9.3** — Atribuição regressiva sobre grafo causal: separar falha de model / context / tool / memory / policy / provider / infra. Gera candidatos; **nenhuma mutação em produção**.

**🚪 G-W9 (= G-M5):** experimento reproduzível de dataset + manifests + digests · A/A respeita orçamento de falso positivo · nenhuma trajetória sem atribuição entra no corpus · tamanho do corpus derivado de **power analysis**, não de número arbitrário.

---

# MILESTONE M6 — Meta-Harness Governado

## WAVE 10
- **Sprint 10.1 — Variant proposer** — variantes limitadas a manifest, skill, prompt asset e parâmetros de policy; mutation budget; campos proibidos; guard de similaridade/loop; variantes imutáveis e content-addressed.
- **Sprint 10.2 — Promotion controller** — efeito mínimo, incerteza, custo e regressões de segurança; aprovação humana por classe; canary por cohort; **rollback por ponteiro — artifacts nunca sobrescritos**.
- **Sprint 10.3 — Skill/model learning** — harvest só de episódios com evidence válido; **skill synthesis antes de fine-tuning** (mais barato e reversível); export DPO/SFT versionado com harness constante (validade causal); candidatos passam pelos mesmos gates.

**🚪 G-W10 (= G-M6):** variante proposta, avaliada, promovida em canary **e revertida em exercício controlado** · Meta-Harness sem workspace write, evaluator key ou registry write direto · Promotion Controller é o único writer do ponteiro de produção · histórico explica por que a versão foi promovida.

---

# MILESTONE M7 — Falsificação de Generalidade

## WAVE 11
- **Sprint 11.1 — Seleção de domínio** — estruturalmente diferente de coding (data investigation, structured research ou operations planning); corpus e evaluator pré-registrados.
- **Sprint 11.2 — Domain pack** — plugins novos **sem** SPI específica de domínio; se faltar capacidade, provar primeiro que é extensão universal.
- **Sprint 11.3 — Teste de generalidade** — single-agent e multi-agent; comparar trajetória, custo e recovery com coding; validar builder UX com integrador externo ao core.

**🚪 G-W11 (= G-M7):** `git diff` do core **vazio** durante criação do pack · novo domínio end-to-end com signed evidence · ≥1 plugin reutilizado sem modificação entre domínios · nenhuma taxonomia de coding virou conceito universal.

---

# PARTE 3 — GATES TRANSVERSAIS PERMANENTES

## Correctness
- `state = fold(events)` provado em CI.
- Nenhum command sem outcome terminal ou estado de reconciliação.
- Nenhum controle merge sem teste de call-site de produção.
- Schema, manifest e geração de tipos sem drift.

## Security
- Plugins não-confiáveis por padrão.
- Capability e isolation como autoridades independentes.
- Juiz e chaves de assinatura exteriores; inalcançáveis de qualquer cela.
- Rede e secrets default-deny.
- Digest + assinatura de artifact antes de ativação.

## Performance
- Benchmarks desde W2: append p50/p95/p99, replay throughput, RPC overhead, memória/cela, latência de scheduling, saturação.
- Regressão acima do budget bloqueia merge ou exige ADR com trade-off **medido**.
- Batching e projeção assíncrona nunca relaxam durabilidade do ledger.
- Otimização só entra com profile reproduzível.

## Data quality
- Todo evento tem atribuição suficiente para explicar executor e versão.
- Conteúdo completo em blob protegido; envelope guarda digest/ref.
- Falhas têm causa estruturada.
- Custos reconciliam por call, agent, run e project.

---

# PARTE 4 — RISCOS

| ID | Risco | Mitigação |
|---|---|---|
| K-1 | Goodhart recorre em gate novo | §0.4 + teste plantado obrigatório + revisão adversarial |
| K-2 | Contract lock congela ficção | Sprint 1.1 **antes** de 1.2, inegociável |
| K-3 | Time-to-value longo | M3 é o marco de valor; não deixar M1–M2 incharem |
| K-4 | Legado nunca morre | Condições de saída §0.8 + revisão trimestral |
| K-5 | Promoção por ruído | FDR + MDE + A/A + holdout + pré-registro (M5 antes de M6) |
| K-6 | Corpus contaminado | ADR-060-09: descartar dados pré-M3 |
| K-7 | Concorrência sem as 6 condições | Sprint 6.1 completo antes de 6.2 |
| K-8 | Rust adotado por motivo errado | Gate de decisão com limiares numéricos |

---

# PARTE 5 — PRIMEIRO INCREMENTO

**O primeiro PR do substrato 0.6.0 deve conter:**

1. `docs/00_guidelines/GATES.md`
2. `test/gates/test_planted_failures.py` — o código preguiçoso que passaria em cada gate atual, comitado como teste negativo
3. `ADR-060-03` — gates comportamentais, proibição de gate lexical
4. Marcação de `check_event_coverage.py` como não-normativo

**Racional:** antes de construir qualquer coisa, instalar a disciplina que teria detectado `verdict: "pass"`. Todo o resto depende de os gates serem confiáveis.

---

## Sequenciamento inegociável

1. Disciplina de gates **antes** de qualquer construção.
2. Fatia vertical **antes** de contract lock.
3. Ledger durável **antes** de autonomia.
4. Supervisor genérico **antes** de plugins reais.
5. Single-node correto **antes** de distribuição.
6. Um coding agent real **antes** de multi-agent.
7. As seis condições **antes** de concorrência.
8. Poder estatístico **antes** de promoção automática.
9. Medição **antes** da decisão sobre Rust.
10. Domínio novo entra **sem** diff no core.

# Principal Staff Engineer Review: Concept Lock Index & Task Breakdown

## 1. Important Files List

| ID | Nome / Alias | Caminho do Arquivo (Filepath) | Descrição e Foco |
|:---|:---|:---|:---|
| 02 | `milestones` | `docs/03_execution/milestones.md` | Escada macro de marcos e sequenciamento (M-0 a M-10) |
| 03 | `higgs_concepts` | `docs/_archive/reviews/Higgs_update_concepts.md` | Plano diretor, auditoria forense e convergência M-3C |
| 04 | `higgs_todo` | `docs/_archive/reviews/Higgs_update_todo_list.md` | Checklist operacional e backlog detalhado de tarefas |
| 05 | `spec_normative` | `docs/SPEC.md` | Especificação normativa central, axiomas e invariantes |
| 06 | `law_runtime` | `docs/01_law/RUNTIME.md` | Regras de composição, ActivationPlan e execução |
| 07 | `law_dispatch` | `docs/01_law/DISPATCH.md` | Pipeline S0-S12, monitor TCB e leases tipados 6D |
| 08 | `law_extensibility` | `docs/01_law/EXTENSIBILITY.md` | Regras de manifestos v2, SPIs e domínios desacoplados |
| 09 | `law_evidence` | `docs/01_law/EVIDENCE.md` | Avaliador exterior UID 10002 e vereditos assinados |
| 10 | `law_measurement` | `docs/01_law/MEASUREMENT.md` | Validação estatística McNemar e identidades D_H/D_R/D_X |
| 11 | `law_security` | `docs/01_law/SECURITY.md` | Isolamento Bubblewrap, namespaces e teto TCB |
| 12 | `adr_index` | `docs/02_decisions/INDEX.md` | Índice mestre de decisões arquiteturais aceitas |
| 13 | `adr_0077_manifest` | `docs/02_decisions/0077-named-component-graph-manifest.md` | Grafo de componentes nomeados (mhf.manifest/2) |
| 14 | `adr_0078_trajectory` | `docs/02_decisions/0078-trajectory-un-hollowing-cost-accounting.md` | Trajetórias ricas e contabilidade real de custo |
| 15 | `adr_0081_lifecycle` | `docs/02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md` | Ciclo de vida de plugins no runtime |
| 16 | `adr_0082_loop` | `docs/02_decisions/0082-universal-turn-loop-m10-compatibility-contract.md` | Protocolo universal de efeitos e evidências |
| 17 | `arch_overview` | `docs/04_architecture/overview.md` | Visão geral da malha hexagonal e fluxo de camadas |
| 18 | `arch_components` | `docs/04_architecture/c4_component.md` | Diagrama C4 de componentes e fronteiras de isolamento |
| 19 | `arch_state_machines` | `docs/04_architecture/state_machines.md` | FSMs de plugins, episódios e sessões |
| 20 | `contract_manifests` | `docs/05_contracts/manifests.md` | Esquema canônico de manifestos (mhf.manifest/2) |
| 21 | `contract_trajectories` | `docs/05_contracts/trajectories.md` | Esquema canônico de trajetórias (mhf.trajectory/1) |
| 22 | `contract_verdicts` | `docs/05_contracts/verdicts.md` | Contrato de vereditos assinados com Ed25519 |
| 23 | `contract_selectors` | `docs/05_contracts/selectors_and_budgets.md` | Contrato de seletores e leases tipados em 6D |
| 24 | `proto_evaluator` | `docs/06_protocols/evaluator.md` | Protocolo do daemon avaliador exterior UID 10002 |
| 25 | `proto_stores` | `docs/06_protocols/stores.md` | Protocolo de persistência SQLite WAL e cold recovery |
| 26 | `proto_sandbox` | `docs/06_protocols/sandbox.md` | Protocolo de sandbox Bubblewrap rootless |
| 27 | `eng_testing` | `docs/07_engineering/testing_and_falsifiers.md` | Guia de testes herméticos e falsificadores red-first |
| 28 | `eng_security_tcb` | `docs/07_engineering/security_and_tcb.md` | Guia do orçamento TCB (<= 1438 LOC) e linters |
| 29 | `eng_adding_pack` | `docs/07_engineering/adding_a_pack.md` | Procedimento para adição de packs desacoplados (Pack #2) |
| 30 | `root_readme` | `README.md` | Mapa de navegação primário do repositório |
| 31 | `root_agents` | `AGENTS.md` | Contrato de governança operacional e anti-sprawl |

---

## 2. Leadership Documentation Matrix

| ID | Caminho Relativo (Filepath) | Categoria | Foco / Importância para a Liderança |
|:---|:---|:---|:---|
| 01 | `docs/_archive/reviews/Higgs_update_concepts.md` | Executivo / Auditoria | Plano diretor, auditoria forense e convergência M-3C |
| 02 | `docs/_archive/reviews/Higgs_update_todo_list.md` | Executivo / Backlog | Backlog operacional e tarefas detalhadas da convergência |
| 03 | `docs/03_execution/milestones.md` | Macro-Roadmap | Escada de marcos do projeto (M-0 ao M-10) |
| 04 | `docs/03_execution/sprint_active.md` | Execução Viva | Quadro de tarefas da sprint atual e gates imediatos |
| 05 | `docs/SPEC.md` | Lei Normativa Central | Axiomas A-1..A-6, invariantes I-1..I-11 e precedência |
| 06 | `docs/_archive/reviews/concepts_review_prompt.md` | Diretiva Executiva | Mandato de auditoria forense e re-fundação do substrate |
| 07 | `docs/_archive/references/RESEARCH_2308B_gm.md` | Pesquisa SOTA / Teoria | Paper de 7 planos, genomas e taxonomia de mutação (M0-M8) |
| 08 | `docs/_archive/references/RESEARCH_META_COGNITIVE_ENGINEERING.md` | Visão Futura pós-v1.0 | Meta-Engenharia Cognitiva, Noesis, Genesis e Ecosphere |
| 09 | `docs/_archive/references/RESEARCH_META_COGNITIVE_ENGINEERING_briefing.md` | Briefing Executivo | Síntese executiva da visão pós-v1.0 para Diretores |
| 10 | `docs/_archive/references/RESEARCH_higgs_2308.md` | Pesquisa 2026 | Implicações técnicas das pesquisas recentes de harnesses |
| 11 | `docs/_archive/references/RESEARCH_Harness_Builder_Framework.md` | Arquitetura / Plugins | Design de compilação de plugins e manifestos declarativos |
| 12 | `docs/_archive/references/proposal_glm_harness_BETA.md` | Auditoria Histórica | Diagnóstico de trajetórias e falsificadores do System 1 |
| 13 | `docs/01_law/RUNTIME.md` | Lei / Runtime | Composição, ActivationPlan e autoridade de execução |
| 14 | `docs/01_law/DISPATCH.md` | Lei / Kernel | Pipeline S0-S12, monitor TCB e leases tipados 6D |
| 15 | `docs/01_law/EXTENSIBILITY.md` | Lei / Extensibilidade | Regras de manifestos v2, SPIs e domínios desacoplados |
| 16 | `docs/01_law/EVIDENCE.md` | Lei / Evidência | Avaliador exterior UID 10002 e vereditos assinados |
| 17 | `docs/01_law/MEASUREMENT.md` | Lei / Métricas | Protocolo estatístico McNemar e identidades D_H/D_R/D_X |
| 18 | `docs/01_law/SECURITY.md` | Lei / Segurança | Isolamento Bubblewrap, namespaces e teto de LOC do TCB |
| 19 | `docs/02_decisions/INDEX.md` | Decisões / ADRs | Registro cronológico de todas as decisões arquiteturais |
| 20 | `docs/02_decisions/0069-runtime-convergence-python-first-packages-canonical.md` | Decisões / ADRs | Convergência em pacotes Python e malha hexagonal |
| 21 | `docs/02_decisions/0071-authority-state-ledger-identity-trinity.md` | Decisões / ADRs | Trindade autoridade/estado/ledger e separação de identidades |
| 22 | `docs/02_decisions/0072-plugin-boundary-wire-first-evaluator-exterior.md` | Decisões / ADRs | Fronteira de plugins e isolamento do avaliador |
| 23 | `docs/02_decisions/0077-named-component-graph-manifest.md` | Decisões / ADRs | Decisão do grafo de componentes nomeados (mhf.manifest/2) |
| 24 | `docs/02_decisions/0078-trajectory-un-hollowing-cost-accounting.md` | Decisões / ADRs | Contabilidade real de custos e trajetórias ricas |
| 25 | `docs/02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md` | Decisões / ADRs | Ciclo de vida de plugins e remoção do layer0 |
| 26 | `docs/02_decisions/0082-universal-turn-loop-m10-compatibility-contract.md` | Decisões / ADRs | O protocolo universal de turn loop (efeitos/evidências) |
| 27 | `docs/02_decisions/0085-reversibility-radius-decide-shape-defer-implementation.md` | Decisões / ADRs | Raio de reversibilidade e estratégia de deferral |
| 28 | `docs/04_architecture/overview.md` | Arquitetura / Sistema | Visão geral da malha hexagonal de dependências |
| 29 | `docs/04_architecture/c4_component.md` | Arquitetura / C4 | Diagrama C4 de componentes e fronteiras de isolamento |
| 30 | `docs/04_architecture/state_machines.md` | Arquitetura / FSM | Máquinas de estado de plugins, episódios e sessões |
| 31 | `docs/05_contracts/manifests.md` | Contratos / Dados | Esquema canônico de manifestos (mhf.manifest/2) |
| 32 | `docs/05_contracts/trajectories.md` | Contratos / Dados | Esquema canônico de trajetórias ricas (mhf.trajectory/1) |
| 33 | `docs/05_contracts/verdicts.md` | Contratos / Dados | Esquema de vereditos assinados com Ed25519 |
| 34 | `docs/05_contracts/selectors_and_budgets.md` | Contratos / Dados | Álgebra de leases tipados em 6 dimensões |
| 35 | `docs/06_protocols/evaluator.md` | Protocolos / Portas | Protocolo do daemon avaliador exterior UID 10002 |
| 36 | `docs/06_protocols/stores.md` | Protocolos / Portas | Protocolo de persistência SQLite WAL e cold recovery |
| 37 | `docs/06_protocols/sandbox.md` | Protocolos / Portas | Protocolo de sandbox Bubblewrap rootless |
| 38 | `docs/07_engineering/security_and_tcb.md` | Engenharia / Governança | Teto de LOC do TCB (<= 1438) e linters de segurança |
| 39 | `docs/07_engineering/testing_and_falsifiers.md` | Engenharia / Testes | Disciplina de testes herméticos e falsificadores red-first |
| 40 | `docs/08_theory/active_inference.md` | Teoria Científica | Fundamentos de Active Inference e minimização de EFE |
| 41 | `README.md` | Raiz do Projeto | Mapa de navegação primário do repositório |
| 42 | `AGENTS.md` | Raiz do Projeto | Contrato de governança para agentes e regras de anti-sprawl |

---

## 3. Granular Action Plan (Notes & Subtasks)

| SubID | Subtarefa Granular | Arquivo / Módulo Afetado | Responsável |
|:---|:---|:---|:---|
| **01.A** | Auditar estado das sprints e congelar M-4 temporariamente | `docs/03_execution/sprint_active.md` | Liderança |
| **01.B** | Redefinir backlog da sprint ativa para M-3C (v0.6.2) | `docs/03_execution/sprint_active.md` | Liderança / Docs |
| **01.C** | Atualizar escada macro inserindo M-3C antes de M-4 | `docs/03_execution/milestones.md` | Liderança / Docs |
| **02.A** | Atualizar SPEC.md vinculando ActivationPlan e manifest v2 | `docs/SPEC.md` & `docs/01_law/` | AI PhD / Architect |
| **02.B** | Redigir ADR sucessor para formalizar a convergência M-3C | `docs/02_decisions/` | Principal Arch |
| **02.C** | Sincronizar versões e metadados na tríade documental | `README.md`, `AGENTS.md`, `pyproject.toml` | Doc Architect |
| **03.A** | Escrever teste vermelho: vg-code-default via manifest v2 | `test/contracts/test_runtime_v2.py` | Tech Lead |
| **03.B** | Escrever teste vermelho: vg-table-default sem erro de verbo | `test/contracts/test_table_probe.py` | Tech Lead |
| **04.A** | Definir tipos de dados imutáveis ActivationPlan & RunPlan | `vanguard/packages/runtime/plan.py` | Staff / Principal |
| **04.B** | Refatorar Runtime.compose para produzir ActivationPlan | `vanguard/packages/runtime/compose.py` | Staff / Principal |
| **04.C** | Adaptar HarnessSession para consumir ActivationPlan | `vanguard/packages/runtime/session.py` | Staff / Principal |
| **05.A** | Mover verbos de DEFAULT_BINDINGS para provedores de domínio | `vanguard/packages/runtime/wiring.py` | Senior Dev |
| **05.B** | Integrar ciclo de vida do registry no compose/session | `vanguard/packages/runtime/registry/` | Senior Dev |
| **05.C** | Garantir encerramento reverso de plugins em falhas/exit | `vanguard/packages/runtime/registry/` | Senior Dev |
| **06.A** | Converter manifesto do vg-code-default para mhf.manifest/2 | `vanguard/packages/agency/manifests/` | Senior / Mid Dev |
| **06.B** | Ativar probe vg-table-default no runtime unificado | `packs/table-default/` | Senior / Mid Dev |
| **06.C** | Consolidar superfícies de packs duplicadas | `packs/code-default/` | Senior / Mid Dev |
| **07.A** | Configurar SqliteEventStore file-backed como default de E2E | `vanguard/packages/runtime/root.py` | Senior Dev |
| **07.B** | Validar teste de cold restart a partir do arquivo WAL | `test/runtime/test_ledger_truth.py` | Senior Dev |
| **08.A** | Executar testes diferenciais de paridade (legado vs v2) | `test/contracts/test_parity.py` | Senior Dev |
| **08.B** | Deletar parser e tipos legados (HarnessManifest, load_pack) | `domain/artifacts/`, `agency/manifests/` | Senior Dev |
| **08.C** | Rodar linters de duplicação e fronteiras arquiteturais | `tools/linters/` | Senior Dev |
| **09.A** | Executar suíte completa de linters (TCB, boundaries, links) | `tools/linters/*.py` | Tech Lead |
| **09.B** | Homologar clean clone e autorizar fechamento da v0.6.2 | `CI / GitHub Workflows` | Liderança |
| **10.A** | Provisionar chaves e daemon avaliador exterior (UID 10002) | `containers/evaluator/` | Release Engineer |
| **10.B** | Executar E2E real e derivar 9 linhas de evidência com hash | `vanguard/packages/apps/` | Dev Team |
| **10.C** | Validar auditoria de evidência criptográfica | `domain/evidence/audit.py` | Evidence Lead |
| **11.A** | Modelar contrato de oráculo formal e witness do Pack #2 | `packs/math-formal/` | Formal Lead |
| **11.B** | Provar execução do Pack #2 com zero diffs no kernel/domain | `test/packs/test_formal_pack.py` | Dev Team |
| **12.A** | Implementar verbo agent.spawn com atenuação de grants no TCB | `vanguard/packages/kernel/` | Principal / Staff |
| **12.B** | Construir scheduler com leases, claims e backpressure | `vanguard/packages/runtime/sched/` | Principal / Staff |
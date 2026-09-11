# AETHER/Vanguard — Relatório de Revisão e Guia de Implementação para Liderança

> [!NOTE]
> **Status de Governança e Classificação de Implementação (Atualizado: 2026-09-11 | HEAD: `1e257e76` | Sujeito Qualificado: `2989d57d`)**
> - **Autoridade:** Informativo / Orientação Estratégica (a autoridade normativa e de execução reside estritamente em [`docs/execution/`](../docs/execution)).
> - **CONCLUÍDO / ACEITO PELA LIDERANÇA (`DONE`):**
>   - Bloco NT-1 completo ([T-98](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/tasks.md#L95) a [T-111](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/tasks.md#L255)).
>   - Marco [**`MS-BASELINE`**](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/milestones.md#L138) **`FECHADO`** (3.121 testes verdes, 0 falhas, `just check` & `just verify` aprovados).
>   - Marco [**`MS-CONTEXT`**](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/milestones.md#L83) **`FECHADO`** (T-110 qualificado com 104 turnos determinísticos em 4 interpretadores novos).
>   - Invariantes preservados: TCB em 1.386 LOC ($\le 1.438$), 0 imports de `subprocess` no runtime, presets públicos inalterados.
> - **PRÓXIMO PASSO ATIVO (`TODO`):**
>   - Marco [**`MS-CONTROL`**](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/milestones.md#L143): Auditoria e congelamento de pré-registro de controle em [T-26](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/tasks.md#L605) (0 chamadas pagas) $\to$ Avaliação do canário single-agent em [T-27](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/tasks.md#L611) ($n \ge 30$, Wilson LB $\ge 0.40$, 0 falsas conclusões).
> - **PROTÓTIPOS / EXPERIMENTAL / HORIZONTE POST-CONTROL (`FH-1 PROPOSAL`):**
>   - Estritamente bloqueados até o aceite formal de `MS-CONTROL`: CAS workspace (`MS-CAS`), delegação de subagentes (`MS-DELEGATION`), tratamentos especialistas (`MS-SPECIALIST`), diretor de campanha (`MS-CAMPAIGN`), memória governada (`MS-MEMORY` / `M-8`) e benchmark oficial (`MS-OFFICIAL`).

**Data da revisão original:** 2026-09-10 (Atualizado: 2026-09-11)  
**Repositório:** `brainopensource/cognitive-framework`  
**Branch:** `feat/aether-framework-electroweak-canonical-agents`  
**Escopo:** backend Vanguard, substrato de criação de agentes e Coding Max para projetos Greenfield/Brownfield, múltiplos arquivos, contexto longo, recuperação e execução autônoma.  

---

## 1. Resumo executivo

O AETHER/Vanguard já possui uma fundação arquitetural avançada para computação agêntica governada: event sourcing, ledger SQLite-WAL, autoridade de execução separada do modelo, kernel fail-closed, budgets tipados, grants atenuados, composição declarativa, sandbox, verificação externa, retomada durável, contexto estratificado e mecanismos de edição multi-file. O projeto não precisa de uma reescrita arquitetural.

O caminho de produto canônico consolidado é:

```text
CodingMaxFacade
    → ApplicationService
    → Runtime
    → HarnessSession
    → EpisodeEngine
    → Kernel
```

O risco central histórico era a diferença entre mecanismo existente e capacidade aceita. Esse risco foi superado no bloco Near-Term: `MS-BASELINE` e `MS-CONTEXT` foram auditados, integrados e formalmente aceitos pela Liderança no commit `2989d57d`.

A ordem de entrega canônica em execução é:

```text
verdade operacional & isolamento (MS-BASELINE) [FECHADO]
→ contexto, cache & recuperação determinística (MS-CONTEXT) [FECHADO]
→ controle single-agent congelado e canário (MS-CONTROL) [ATIVO AGORA: T-26 / T-27]
→ [Pós-Controle FH-1 PROPOSAL]:
    ├─ CAS imutável e promoção atômica (MS-CAS / T-112–T-116)
    ├─ Delegação atenuada de subagentes (MS-DELEGATION / T-117–T-118)
    ├─ Tratamentos especialistas e estudos pareados (MS-SPECIALIST / T-119)
    ├─ Campanhas multiagente em worktrees paralelos (MS-CAMPAIGN / T-120)
    ├─ Memória governada com held-out lift (MS-MEMORY / M-8 / T-121)
    └─ Qualificação de release (M-9 Beta -> M-10 Release)
```

CAS completo, especialistas, campanhas multiagente, meta-controlador e benchmark oficial permanecem propostas condicionais posteriores a `MS-CONTROL`. Eles não contaminam o controle inicial nem são tratados como dependências universais de M-8.

---

## 2. Autoridade documental e ordem obrigatória de leitura

Para cada implementação, revisão ou correção, a equipe deve seguir esta ordem:

1. `AGENTS.md` — regras operacionais, arquitetura, anti-sprawl e protocolo de navegação.
2. `README.md` — mapa inicial do repositório.
3. `docs/execution/tasks.md` — trabalho autorizado, dependências, streams, arquivos e falsificadores.
4. `docs/execution/spec.md` — contratos normativos, schemas, invariantes e matriz de falhas.
5. `docs/execution/technical.md` — algoritmos, integração e receitas de engenharia.
6. `docs/execution/milestones.md` — gates e critérios de aceite.
7. `docs/execution/backlog.md` — inventário e lifecycle dos packages; não é uma fila de execução.
8. Código e testes diretamente associados à tarefa.

O princípio de autoridade é:

```text
índices roteiam;
documentos canônicos restringem;
código implementa;
testes falsificam;
ledger e evidências demonstram comportamento observado.
```

LDA deve ser usado como mecanismo de navegação e blast-radius, nunca como autoridade arquitetural. Antes de confiar no índice, a equipe deve verificar que ele está saudável e vinculado ao HEAD atual. Depois de mudanças de código, deve executar indexação delta e inspeção de drift.

---

## 3. Arquitetura que deve ser preservada

```text
domain ← ports ← kernel ← agency ← runtime → adapters
                                    ↓
                              apps / packs
                                    ↓
                         CLI / TUI / Desktop / Lab
```

### 3.1 Domain

Responsável por valores puros, contratos wire, canonicalização RFC 8785/JCS, selectors, evidência, estados semânticos e reducers puros. Deve permanecer sem I/O, rede, subprocessos ou dependência das camadas superiores.

### 3.2 Ports

Define protocolos pequenos e estáveis para kernel, modelos, sandbox, evaluator, event store, blob store, environment, determinismo, indexação e SPIs. Não deve absorver interfaces provider-shaped nem crescer apenas para acomodar implementações específicas.

### 3.3 Kernel

É a Trusted Computing Base: dispatch S0–S12, capability attenuation, grants, policy fail-closed, budgets e proveniência. Deve permanecer domain-blind e abaixo do teto de 1438 LOC. O headroom não é orçamento de feature.

### 3.4 Agency

Contém `EpisodeEngine`, estado de episódio, admission, context compiler, compactação e recuperação de protocolo. Não deve ganhar um segundo loop para context, retry, planning ou especialistas.

### 3.5 Runtime

É responsável por composição, lifecycle, sessão, ledger emitter, checkpoints, resume, governança, projections e integração das portas. Não deve executar subprocessos diretamente. Toda execução concreta pertence a adapters ou tooling exterior.

### 3.6 Adapters

Implementam filesystem, Git, transações, sandbox, providers, evaluators e stores. Não podem importar kernel ou agency. O 2PC e os efeitos concretos de ambiente devem permanecer nessa camada.

### 3.7 Apps e packs

`apps/` deve permanecer fino, chamando o runtime canônico. `packs/` contém semântica específica do domínio de código: planejamento, contexto de repositório, completion policy, verificação, greenfield, implicated files e toolkits. Packs podem definir comportamento; não recebem autoridade para contornar o kernel.

---

## 4. Estado de evidência e limitações

Foi reportada uma execução com 2839 testes, 24 failures, 30 errors e 27 skips. Esse resultado é útil como diagnóstico, mas não é receipt de aceite porque não foi produzido pelo runner independente especificado em T-98 e não demonstra todos os predicados de isolamento, identidade e não mutação.

O fato de `git status --porcelain` permanecer vazio após uma suíte é positivo, mas não fecha T-98. O contrato exige, entre outros elementos:

- repositório descartável com metadados Git independentes;
- redirecionamento dos corpora e diretórios graváveis;
- credenciais removidas do ambiente;
- rede negada no boundary apropriado;
- digests de source, index e corpus antes/depois;
- inventário completo dos módulos coletados;
- preservação de import errors, failures, errors e skips;
- associação da evidência ao SHA e ambiente exatos.

Dependências obrigatórias ausentes, como sandbox, daemon, runtime ou ferramenta declarada por um gate, devem produzir `BLOCKED` ou `not_run` com causa tipada. Não devem ser convertidas automaticamente em skip ou sucesso. Skip somente é aceitável quando o contrato da capacidade declara explicitamente que ela é opcional.

Um import de módulo inexistente deve ser tratado por T-101: portar a asserção para uma API suportada ou registrar formalmente a retirada do claim e seu sucessor. Não se deve restaurar código obsoleto apenas para reduzir a contagem de erros.

---

## 5. Vocabulário operacional

O repositório contém referências históricas a Waves e Phases, mas o vocabulário normativo atual é:

```text
Stream + Task ID + Milestone Gate
```

As relações `requires:` são a única fonte de ordenação. Termos como “Wave 2” podem permanecer em histórico ou em mapas de compatibilidade, mas não devem ser usados em commits, handoffs ou status atuais sem o Task ID e o gate correspondente.

Formato obrigatório para status:

```text
Stream A — T-99 → MS-BASELINE — IN_PROGRESS
Stream B — T-100 → MS-CONTEXT — READY
Stream C — T-98 → MS-BASELINE — BLOCKED_DEPENDENCY
```

---

## 6. Plano near-term autorizado: NT-1

Os desenvolvedores seniores podem avançar autonomamente em T-98–T-111, incluindo as dependências ativas T-77 e T-97, desde que respeitem as arestas `requires:` e a propriedade exclusiva de arquivos.

### 6.1 Quadro operacional

| Ordem causal | Task | Stream | Resultado | Principais arquivos | Pronto para implementação |
|---|---|---:|---|---|---|
| 1 | T-98 | C | Runner independente, isolamento e não mutação | `test/`, `tools/linters/check_test_hygiene.py`, `justfile` | Sim |
| 1 | T-99 | A | Projeção terminal sem perda | `runtime/entrypoint.py`, `app_service.py`, `child_runtime.py` | Sim |
| 1 | T-100 | B | Valores canônicos de working memory/recovery | `domain/task_state.py`, `agency/episode/protocol_recovery.py` | Sim |
| 1 | T-97 | A | Superfície CLI correta | `vanguard/clients/cli/` | Sim, observando T-84 |
| 2 | T-101 | C | Collection e failure inventory completos | `test/lab/`, fixtures e meta-test de collection | Sim após T-98 |
| 2 | T-103 | C | Integridade de presets e evidência | `packs/code-default/presets.json`, `load.py`, manifests | Sim após T-98 |
| 2 | T-104 | B | Context selection limitada no compilador existente | `agency/context/` | Sim após T-100 |
| 3 | T-102 | A | Facade fina e caminho único | `apps/coding_max/`, runtime CLI/API | Sim após T-99 e T-103 |
| 3 | T-106 | B | Stall recovery determinístico e limitado | `agency/episode/` | Sim após T-100 e T-104 |
| 3 | T-108 | B | Patch exato, rollback e consolidação | `ast_patch.py`, `adapters/environment/` | Sim após T-98 e T-101 |
| 4 | T-105 | A | PromptCodec e contagem na fronteira provider | `adapters/models/` | Sim após T-102 e T-104 |
| 5 | T-77 | B/A | Stable prefix, receipts limitados e cache observável | `agency/context/`; serializer em A | Sim após T-104 e T-105 |
| 5 | T-109 | C | Aceite integrado de MS-BASELINE | tooling, receipts e gates | Sim após seus predecessores |
| 6 | T-107 | A | Binding de state/context/recovery no ledger | `runtime/session.py`, `task_state.py`, `checkpoints.py`, `ledger_emitter.py` | Sim após T-109 e contexto |
| 7 | T-110 | A | Qualificação de 100+ turnos e cold restart | runtime tests e fixtures | Sim após T-107 e T-77 |
| 8 | T-111 | C | Reconciliação MS-BASELINE/MS-CONTEXT | cinco execution docs e pré-registro | Sim após T-109 e T-110 |

### 6.2 Stream A — Runtime, produto e providers

**Responsabilidades:**

- manter uma única projeção de término e disposição;
- impedir `abstained → completed`;
- convergir facade, CLI, API e presets;
- separar budget declarado de atenuação solicitada;
- contar a requisição realmente serializada para o provider;
- observar cache como valor medido ou `null`;
- persistir fatos de selection/recovery antes de chamadas externas;
- preservar resume, counters, epochs e pending effects.

**Arquivos sob propriedade predominante:**

```text
vanguard/packages/runtime/entrypoint.py
vanguard/packages/runtime/app_service.py
vanguard/packages/runtime/child_runtime.py
vanguard/packages/runtime/session.py
vanguard/packages/runtime/task_state.py
vanguard/packages/runtime/checkpoints.py
vanguard/packages/runtime/ledger_emitter.py
vanguard/packages/apps/coding_max/
vanguard/packages/adapters/models/
vanguard/clients/cli/
```

### 6.3 Stream B — Estado, contexto, recovery e patch

**Responsabilidades:**

- snapshots imutáveis e versionados;
- JCS e digests canônicos;
- um único `ContextCompiler`;
- preservação obrigatória de objetivo, restrições, plano, efeitos e verificação;
- compaction por unidade completa de interação;
- omissions explicitamente registradas;
- detecção de loops e stalls por fingerprints normalizados;
- reground/replan/stop com budgets persistentes;
- patch com preimage exato e rollback byte-identical;
- 2PC nos adapters, nunca no kernel.

**Arquivos sob propriedade predominante:**

```text
vanguard/packages/domain/task_state.py
vanguard/packages/agency/context/
vanguard/packages/agency/episode/
vanguard/packages/adapters/environment/
packs/code-default/middleware/
packs/code-default/toolkits/
```

### 6.4 Stream C — Qualificação, configuração e integração

**Responsabilidades:**

- runner independente;
- collection integrity;
- classificação de failures e bloqueios;
- integridade de manifests e presets;
- ferramentas de gate e CI;
- pré-registro e benchmark protocols;
- evidence receipts exact-subject;
- merge queue e atualização dos cinco execution docs.

**Arquivos sob propriedade predominante:**

```text
test/
benchmarks/
tools/linters/
ci/
justfile
packs/code-default/presets.json
packs/code-default/load.py
vanguard/packages/agency/manifests/
docs/execution/
```

---

## 7. Regras de concorrência e integração

1. Cada task deve operar em branch isolada criada a partir do mesmo baseline acordado.
2. Nenhum arquivo pode estar sob lease simultâneo de duas streams.
3. Alterações em arquivos compartilhados devem ser entregues ao proprietário antes da integração.
4. `main` é o único alvo serial de integração.
5. Uma task só entra na fila quando seus `requires:` estão satisfeitos por commits aceitos, não apenas por branches locais.
6. Após cada alteração de código, executar `lda index --delta` e verificar o drift aplicável.
7. Mudanças de contratos, eventos, schemas, APIs, configuração ou comportamento exigem sincronização do documento canônico proprietário.
8. Artefatos gerados não podem ser editados manualmente.
9. Um teste não executado nunca recebe PASS.
10. Falhas introduzidas pela task devem ser corrigidas antes do handoff.

### Handoff mínimo por task

Cada entrega deve informar:

- Task ID e gate;
- baseline e commit resultante;
- arquivos modificados;
- contratos e eventos afetados;
- comandos efetivamente executados;
- resultados, skips, bloqueios e missingness;
- digests de artefatos relevantes;
- riscos ou limitações restantes;
- próxima task desbloqueada.

---

## 8. Gates e definição de pronto

### 8.1 MS-BASELINE

Requer T-98, T-99, T-101, T-102, T-103, T-108, T-97 e T-109 no mesmo sujeito integrado.

Só pode fechar quando houver:

- suíte Python completa e coletada;
- gates TypeScript requeridos;
- recipes completas de `just check` e `just verify`;
- zero failure/error não contabilizado;
- nenhuma perda silenciosa de módulo ou falsificador;
- terminal/disposition preservados separadamente;
- patch semantics fail-closed;
- source/index/corpus não modificados pela qualificação;
- receipt associado ao SHA e ambiente exatos.

### 8.2 MS-CONTEXT

Requer MS-BASELINE, T-100, T-104, T-105, T-106, T-107, T-77, T-110 e T-111.

Só pode fechar quando uma execução determinística de 100+ turnos, incluindo compactação e fresh-process restart, preservar:

- intenção e restrições completas;
- grants e budgets;
- plano e próxima ação;
- efeitos concluídos e pendentes;
- recovery counters e deadlines;
- interação mais recente;
- verificação fresca;
- prefix e policy identities;
- omissions e epoch coerentes.

### 8.3 MS-CONTROL

Depois de MS-BASELINE e MS-CONTEXT:

1. reconciliar T-51 e T-52;
2. completar dependências do controle;
3. congelar T-26 antes da primeira chamada paga;
4. executar T-27 com o braço single-worker `vg-code-balanced` via `entrypoint.execute`;
5. usar SHA limpo e exato;
6. preservar todos os resultados e missingness;
7. exigir `n ≥ 30`, Wilson lower bound `≥ 0.40` e zero false-completions observadas para aceite positivo.

T-27 pode terminar como `POSITIVE`, `NEGATIVE`, `UNDETERMINABLE` ou `INVALID`. Todos os resultados devem ser publicados. Somente uma disposição que satisfaça o predicado positivo aceita `MS-CONTROL`; negativo ou indeterminável conclui a medição, mas mantém o gate aberto.

---

## 9. Cronograma recomendado

O cronograma abaixo é uma estimativa de capacidade para três desenvolvedores seniores com integração serial. As dependências continuam sendo autoridade superior ao calendário.

| Período | Stream A | Stream B | Stream C | Gate esperado |
|---|---|---|---|---|
| Semanas 1–2 | T-99, T-97 | T-100 | T-98 | Base segura iniciada |
| Semanas 2–3 | preparar T-102 | T-104 | T-101, T-103 | Inventário e contratos |
| Semanas 3–4 | T-102, iniciar T-105 | T-106, T-108 | integração contínua | Produto e patch convergentes |
| Semanas 5–6 | T-105 | T-77 | T-109 | MS-BASELINE candidato |
| Semanas 6–7 | T-107, T-110 | suporte de context/recovery | T-111 | MS-CONTEXT candidato |
| Semanas 8–9 | suporte ao controle | correções apenas se falsificadas | T-51/T-52/T-26/T-27 | MS-CONTROL medido |
| Semanas 10–12 | planejamento dos ramos aceitos | contratos puros dos ramos aceitos | protocolos/gates | FH-1 refinado seletivamente |
| Semanas 13+ | implementação conforme perfil | implementação conforme perfil | qualificação e release | M-8/M-9/M-10 |

Datas não devem ser usadas para declarar fechamento. Um gate somente fecha por evidência exact-subject aceita.

---

## 10. Correções às recomendações anteriores

### 10.1 Não transformar dependência ausente em skip automático

Probes de ambiente são recomendados, mas devem produzir uma classificação verdadeira, como:

```text
READY
BLOCKED_DEPENDENCY
BLOCKED_PLATFORM
NOT_RUN
FAILED
PASSED
```

O probe melhora a observabilidade; não reduz o contrato de aceitação.

### 10.2 Não declarar T-98 concluído apenas porque o Git permaneceu limpo

Árvore limpa é apenas um predicado. T-98 também exige isolamento de Git, rede, credenciais, corpora e identidade de runner.

### 10.3 Não recriar mecanismos existentes

O código atual já contém transaction manager, tamper shield, greenfield policy, implicated-file logic e multi-file completeness. A implementação deve integrar, consolidar e qualificar esses mecanismos. Novos módulos concorrentes são proibidos.

### 10.4 Não podar manifests antes de T-101/T-108

A redução da fauna experimental é recomendável, mas somente depois de identificar callers, aliases, registros, recursos, testes, claims e sucessores. A retirada deve preservar falsificadores e produzir migração explícita.

### 10.5 Não impor quota arbitrária a documentação

Documentação normativa pode preceder código. A regra correta é exigir que alterações em `docs/execution` tenham Task ID, proprietário semântico, delta de contrato verificável e impacto identificável. Depois do detalhamento suficiente, o planejamento deve congelar até surgir nova evidência.

### 10.6 Não exigir todos os ramos FH-1 para M-8

CAS, delegação, campaign e avaliação oficial são condicionais ao perfil que será entregue. M-8 exige memória governada e seus predicados vigentes; outros ramos só se tornam obrigatórios se a release anunciar essas capacidades.

---

## 11. Planejamento pós-controle: T-112–T-128

T-112–T-128 permanecem `[PROPOSAL]`. A liderança deve selecionar ramos após medir o controle, não aprovar todo o horizonte simultaneamente.

| Ramo | Tasks | Gate | Quando autorizar |
|---|---|---|---|
| CAS workspace | T-112–T-116 | MS-CAS | Quando o produto exigir candidatos imutáveis e promoção transacional |
| Delegação | T-117–T-118 | MS-DELEGATION | Quando especialistas/subagentes entrarem no perfil |
| Tratamentos | T-119 | MS-META / MS-SPECIALIST | Somente por estudo pareado pré-registrado |
| Campaign | T-120 | MS-CAMPAIGN | Quando houver DAG durável multiagente |
| Memória | T-121 | MS-MEMORY / M-8 | Para memória governada e lift held-out |
| Avaliação | T-122–T-125 | MS-EVAL | Para protocolos externos e corpus greenfield qualificados |
| Oficial/SOTA | T-126–T-127 | MS-OFFICIAL / MS-SOTA | Mediante orçamento e autorização explícitos |
| Release | T-128 | M-8/M-9/M-10 | Apenas com os ramos realmente enviados aceitos |

### 11.1 Ordem de detalhamento pela liderança

Para cada ramo selecionado:

1. Atualizar `spec.md` com tipos, schemas, invariantes e failure matrix.
2. Atualizar `technical.md` com algoritmos, transações, recovery e integração.
3. Decompor `tasks.md` em folhas pequenas e executáveis.
4. Atualizar `backlog.md` apenas para lifecycle e escopo de packages.
5. Atualizar `milestones.md` com acceptance predicates mensuráveis.
6. Promover arquitetura para `docs/architecture/` ou `docs/backend/` somente após aceite do gate correspondente.

### 11.2 Definition of Ready obrigatória

Nenhuma task pós-controle pode mudar de `[PROPOSAL]` para trabalho autorizado sem:

- objetivo comportamental observável;
- `requires:` completos;
- proprietário e stream;
- arquivos exatos e leases sem overlap;
- contratos, tipos, schemas e versões;
- eventos e reducers afetados;
- limites de CPU, tempo, tokens, custo, armazenamento e tentativas;
- política de idempotência;
- crash points e reconciliation;
- migração e rollback;
- falsificador executável;
- testes adversariais;
- evidence receipt esperado;
- gate de destino;
- non-goals e stop conditions.

### 11.3 Refusals arquiteturais para o pós-controle

A liderança deve proibir explicitamente:

- segundo runtime;
- segundo ledger ou event store autoritativo;
- segundo tool broker;
- segundo `EpisodeEngine`;
- segundo context compiler;
- retry loop paralelo;
- campaign engine que bypassa `ApplicationService` ou runtime;
- director com verbos mutantes;
- especialista capaz de admitir conclusão;
- veredicto produzido pelo próprio modelo como evidência exterior;
- promoção de memória pelo mesmo componente que a gerou;
- write compartilhado por agentes no mesmo checkout;
- score oficial inferido de fixture local;
- mudança de prompt, modelo, budget ou ferramenta após congelamento sem invalidar o braço.

---

## 12. Recomendações de engenharia

### 12.1 Priorizar o controle single-agent

O `vg-code-balanced` deve ser o primeiro produto tecnicamente defensável: single-agent, multi-file, resumível, bounded, capaz de trabalhar por sessões longas e incapaz de declarar conclusão sem verificação atual.

### 12.2 Separar complexidade útil de multiplicação de agentes

Antes de adicionar especialistas, melhorar:

- requirement decomposition;
- repository intelligence;
- implicated-file closure;
- context selection;
- exact editing;
- verification planning;
- recovery;
- completion admission.

Um inner loop fraco multiplicado por um director produz mais custo e mais falsas conclusões, não mais capacidade.

### 12.3 Tooling poliglota como extensão de pack

Após `MS-CONTROL`, a expansão para Node/Bun, TypeScript, Rust, Java e outros ecossistemas deve ocorrer por toolkits e policies declarativas, mantendo o kernel neutro. Cada ecossistema precisa declarar comandos, workspaces, timeouts, parser de resultados e critérios de collection/execution.

### 12.4 Skills e MCP sob grants

Skills, techniques, proficiencies e MCPs devem ser capacidades selecionáveis pela composição, com:

- identidade e versão;
- capability grants;
- selectors;
- timeouts;
- budgets;
- provenance;
- output schema;
- rollback/compensation quando aplicável;
- admissão independente.

Uma skill nunca deve possuir autoridade implícita apenas porque está presente no catálogo.

### 12.5 Preservar resultado negativo

Falha experimental não deve ser apagada nem reinterpretada. Resultado negativo ou inconclusivo é evidência para manter uma feature desligada, revisar a hipótese ou interromper investimento.

---

## 13. Riscos prioritários

| Risco | Consequência | Controle |
|---|---|---|
| False completion | Código incompleto tratado como sucesso | Separar termination/disposition; admission por evidência fresca |
| Collection loss | Suite aparentemente verde por ausência de módulos | T-101 e inventory digest |
| Mutação de testes | Agente fabrica o próprio sucesso | TestTamperShield e oracle set congelado |
| Contexto stale | Conclusão baseada em preimage antiga | WorkspaceEpoch, index refresh e stale rejection |
| Perda após restart | Repetição de efeitos ou abandono de obrigações | Ledger fold, recovery state versionado e cold-resume |
| Overflow no provider | Prompt local cabe, request real excede janela | PromptCodec e contagem pós-serialização |
| Patch parcial | Estado multi-file inconsistente | Preflight e transaction manager all-or-nothing |
| Preset divergence | CLI/API/facade executam políticas diferentes | Catálogo único e composition identity |
| Manifest sprawl | Braços incomparáveis e routing inconsistente | Quarentena após inventário e registro separado |
| Benchmark contamination | Score sem validade | Pré-registro, corpus congelado e evaluator exterior |
| Multi-agent cost explosion | Mais custo sem lift | Controle single-agent e estudo pareado |
| Memory leakage | Contaminação de holdout ou cross-project | Grants de retrieval, promoção independente e rollback |

---

## 14. Critério recomendado para Beta MVP

O Beta MVP deve ser inicialmente definido como um perfil `vg-code-balanced` que:

- executa pelo caminho canônico único;
- diferencia término de disposição;
- lê e modifica múltiplos arquivos atomicamente;
- executa verificações targeted e broad;
- preserva estado e budgets após restart;
- compacta contexto sem perder obrigações;
- rejeita completion stale, vazia ou sem testes aplicáveis;
- registra eventos, receipts, custos e missingness;
- termina honestamente quando bloqueado;
- possui controle empírico congelado e auditável.

Se a governança mantiver M-8 como predecessor obrigatório de M-9, a versão beta também deverá fechar memória governada, held-out lift, rollback e separação de promoção antes da autorização. Caso a liderança deseje um beta sem aprendizagem/memória adaptativa, isso exige uma mudança normativa explícita nos gates; não pode ser obtido por interpretação informal.

---

## 15. Decisões requeridas da liderança

Após T-111, a liderança deve deliberar formalmente:

1. Qual corpus, modelo, orçamento e stop rule serão congelados em T-26?
2. Quais tarefas Greenfield/Brownfield compõem T-51?
3. Qual tratamento estatístico e função de custo T-52 usará?
4. Qual resultado mínimo aceita `MS-CONTROL` sem alterar o threshold após observar dados?
5. O Beta MVP incluirá memória governada e aprendizagem, conforme o gate M-8 atual?
6. CAS, delegação ou campaign fazem parte do produto beta ou permanecem experimentais?
7. Quais linguagens e build systems serão oficialmente suportados?
8. Quais manifests continuam produto, experimento, controle ou deprecated?
9. Qual autoridade assina evidência, aceita gates e autoriza spend externo?
10. Qual é o procedimento de rollback e retirada de uma capability já lançada?

---

## 16. Conclusão

O AETHER/Vanguard possui arquitetura suficiente para sustentar agentes de software avançados. O caminho crítico agora é provar o que já existe: uma única execução, uma única verdade de estado, uma única semântica de conclusão e uma qualificação reproduzível.

A equipe deve concluir NT-1 até T-111, congelar e medir o controle, e somente então selecionar os ramos posteriores. O projeto não precisa de mais arquitetura paralela; precisa transformar mecanismos presentes em capacidades aceitas, com evidência exact-subject e ausência de false-completion.

Essa disciplina permitirá evoluir do atual substrato sofisticado para um Beta MVP defensável e, depois, para agentes Greenfield/Brownfield de longa duração com delegação, memória e campanhas governadas.

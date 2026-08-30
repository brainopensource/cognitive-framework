---
id: research.coding-harness-agentic-coding-builder-framework-b
kind: research
status: reference
authority: non-canonical
summary: "SOTA research on harness agentic coding builder architecture and meta-cognition framework."
topic:
  - coding-harness
---
# Harness Agentic Coding Builder — Research & Framework B

## Estado da arte, arquitetura de Harness Builder e aplicação ao AETHER/Vanguard para meta-cognição, Meta-Harness e evolução autoaperfeiçoável de alta ordem

**Data de referência:** 21 de agosto de 2026  
**Classificação:** Research / Principal Staff Engineering synthesis  
**Status:** Documento de pesquisa e direção arquitetural; **não normativo**.  
**Escopo:** Agentic coding harnesses, general agentic algorithms, harness composition, execution substrates, context engineering, memory, plugins, evaluation, observability, experimentation, meta-cognition, adaptive systems, harness-native learning e self-improvement governado.

---

## Nota de autoridade e leitura

Este documento tem duas funções e não deve ser confundido com a `SPEC.md`.

1. **Capítulo I — Pesquisa:** consolida evidência externa, padrões arquiteturais, papers, benchmarks e princípios de engenharia que explicam por que o *harness* é parte material da capacidade observada de um sistema agêntico.
2. **Capítulo II — Aplicação ao AETHER/Vanguard:** transforma esse aprendizado em uma arquitetura de Harness Builder e em uma trajetória de evolução para meta-cognição, Meta-Harness e self-improvement de ordem superior, explicitando onde a arquitetura atual deve ser preservada, fortalecida, simplificada ou formalmente reavaliada.

A fonte normativa atual do projeto continua sendo `SPEC.md`, ADRs e annexes. Quando este relatório propõe algo que contradiz uma decisão vigente — por exemplo, tratar o loop reativo atual como um controller de primeira classe em vez de universalizar o `EpisodeEngine`, ou reavaliar a ideia de “exatamente cinco SPIs” — isso é marcado como **PROPOSTA DE EMENDA / ADR**, não como fato já aprovado.

A revisão independente mais recente do código concluiu que o AETHER possui um trust/effect substrate genuinamente forte, mas que o execution/strategy plane ainda carrega hipóteses de um coding agent reativo. A conclusão operacional deste documento é a mesma: **não reescrever o trust substrate; completar a generalização do plano de execução e composição antes de congelá-lo como API pública.**

---

# Síntese executiva

A principal conclusão da pesquisa é:

> **A unidade de engenharia de um sistema agêntico moderno não é o modelo e nem uma classe `Agent`; é o harness executável que compõe modelo, contexto, estratégia, ferramentas, ambiente, políticas, estado, avaliação e mecanismos de execução.**

Benchmarks recentes reforçam empiricamente esse ponto. No Terminal-Bench 2.1 verificado, Claude Code + Fable 5 aparece com 83,8% e Codex + GPT-5.5 com 83,1%, enquanto outras combinações de harness/model apresentam diferentes trade-offs de qualidade e custo. Isso não permite atribuir cada delta exclusivamente ao harness, mas demonstra que **modelo-base sozinho não prediz a capacidade operacional do sistema**.

Em 18 de agosto de 2026, o LEGO-RL mostrou um ponto ainda mais importante: quando o treinamento acontece **dentro do harness nativo**, preservando compaction, serialização, tool loop e comportamento real do runtime, Qwen3.5-35B-A3B melhorou em três harnesses diferentes no SWE-bench Verified: OpenHands SDK 64,0→70,4%, Claude Code 62,4→68,2% e OpenCode 57,2→66,6%. Agent Lightning v1.0 formaliza uma direção semelhante: o harness de deploy mantém o loop e o trainer observa/intervém por um seam separado.

O aprendizado combinado sugere que uma arquitetura SOTA precisa separar pelo menos quatro planos:

```text
TRUST / EXECUTION PLANE
    identity, authority, resources, effect mediation,
    durable state, plugin containment, exterior evidence

STRATEGY / COGNITION PLANE
    controllers, planning, search, reflection,
    context, memory selection, routing, delegation policy

COMPOSITION / HARNESS PLANE
    declarative composition, plugin resolution,
    model/environment bindings, policy selection, D_H

EXPERIMENT / EVOLUTION PLANE
    trajectories, D_R / D_X, evaluation, ablation,
    candidate generation, search, promotion, rollback
```

Esse desenho permite que o AETHER evolua de:

```text
Coding Agent
  ↓
Harness Builder
  ↓
General Agentic Algorithm Framework
  ↓
Experiment Plane
  ↓
Meta-Harness
  ↓
Governed Self-Improving Harness Ecosystem
```

sem transformar cada estágio em uma nova engine.

A tese de produto deste relatório é:

> **AETHER deve ser uma máquina de compilar e executar composições agênticas sob uma pequena base confiável. Coding, research, debate, tree search, evolutionary search, critic loops, multi-agent coordination e meta-cognição devem aparecer como controllers, policies, plugins e compositions — não como novas ontologias do core.**

A tese de evolução é:

> **Self-improvement não deve significar “um agente altera a si mesmo e torna-se automaticamente produção”. Deve significar geração de candidatos imutáveis, nova identidade `D_H`, execução sob `D_R`, comparação sob `D_X`, julgamento exterior, promoção separada e rollback explícito.**

A tese científica associada é falsificável:

\[
Capability_{new} \Rightarrow Composition/Strategy/Plugin
\]

deve permanecer verdadeiro na maioria das novas capacidades.

Quando a evolução passa repetidamente a exigir:

\[
Capability_{new} \Rightarrow NewCorePrimitive/NewEngine
\]

o substrate deixou de ser suficientemente geral.

---

# CAPÍTULO I — PESQUISA: HARNESSES, AGENTIC ALGORITHMS, META-COGNIÇÃO E SISTEMAS AUTOEVOLUTIVOS

## 1. Modelo, agente, controller e harness são objetos diferentes

### 1.1 Modelo

O modelo é o mecanismo probabilístico de inferência. Ele transforma contexto em saídas: texto, tool calls, código, classificações, planos ou outras estruturas.

Ele não é, por si só:

- um scheduler;
- um sistema de autoridade;
- um memory store;
- uma policy de execução;
- um sandbox;
- um experiment runner;
- uma fonte confiável de avaliação;
- um mecanismo de replay.

### 1.2 Agentic controller

Um controller define **como o sistema decide o próximo passo**.

Um controller pode ser:

- um loop reativo ReAct;
- plan-and-execute;
- planner/editor/verifier;
- tree search;
- best-first search;
- debate;
- critic/refine;
- deterministic workflow;
- portfolio/race;
- evolutionary search;
- hybrid symbolic/LLM logic.

A principal distinção é que o controller descreve a **política de computação**, enquanto o substrate implementa o que precisa ser confiável ao executar diretivas.

### 1.3 Agent

Uma formulação operacional útil é:

```text
AgentExecution = Principal / identity
               + FrozenHarness
               + execution state
```

A classe ou objeto “Agent” não precisa conter toda a arquitetura. Em um substrate recursivo, “subagent” é apenas outra execução sob uma identidade descendente e autoridade atenuada.

### 1.4 Harness

O harness é a composição que transforma capacidade cognitiva em execução operacional:

```text
Harness =
    controller / strategy
  + model routes
  + context policy
  + memory policy
  + tools
  + environment
  + permissions / policies
  + verification / evaluation policy
  + execution substrate bindings
```

Em termos de produto, é o harness que deve ser compilável, comparável e versionável.

---

## 2. Evidência empírica: harness engineering muda desempenho

### 2.1 Terminal-Bench

O Terminal-Bench mede agentes em tarefas de terminal dentro de ambientes reproduzíveis. No leaderboard 2.1 verificado, em 21/08/2026:

| Agent / harness | Model | Accuracy | Custo reportado |
|---|---|---:|---:|
| Claude Code | Fable 5 | 83,8% ± 1,2% | US$ 552,67 |
| Codex | GPT-5.5 | 83,1% ± 1,1% | US$ 2.059,19 |
| Terminus 2 | Fable 5 | 80,4% ± 1,2% | US$ 438,64 |

O benchmark não é um experimento causal perfeito sobre “harness isolado”: prompts, effort, adapters e configurações também variam. Mesmo assim, a evidência operacional é forte o suficiente para rejeitar a ideia de que “o modelo define o desempenho”.

A variável a ser otimizada passa a ser:

\[
Y = F(Model, Harness, Context, Tools, Environment, Policy, Verification)
\]

e não simplesmente:

\[
Y = F(Model)
\]

### 2.2 Harbor como infraestrutura de experimentação

Harbor formaliza o benchmark como:

```text
Task = instruction + container environment + test script
Dataset = collection(Task)
Agent = executable system under test
```

Essa separação é importante porque permite manter constantes:

- dataset;
- task;
- ambiente;
- oracle;
- modelo;

e modificar apenas:

- controller;
- prompt;
- context strategy;
- tool protocol;
- memory;
- routing;
- verification;
- delegation.

O resultado é uma base para **harness ablation**, não apenas benchmark de modelos.

---

## 3. Codex: loop, persistência, compaction e cache como engenharia de harness

A descrição pública do Codex trata explicitamente o *agent loop* como uma peça de software que orquestra usuário, modelo e tools.

Lições relevantes:

### 3.1 Agent loop é mecanismo operacional

O harness:

1. constrói instruções;
2. invoca o modelo;
3. interpreta tool calls;
4. executa tools;
5. injeta observações;
6. repete;
7. termina.

Isso parece simples, mas o comportamento real depende de:

- ordem de mensagens;
- ferramentas disponíveis;
- sandbox;
- approval mode;
- contexto;
- compaction;
- persistência;
- retry;
- caching.

### 3.2 Instruções possuem hierarquia

Codex agrega instruções globais e específicas do projeto. Isso sugere que “prompt” não deve ser um blob; deve ser uma composição ordenada e atribuível.

### 3.3 Prefix stability e prompt caching são arquitetura

Cache depende de prefixos idênticos. Alterar ordem de tools, model, sandbox configuration ou instruções pode invalidar cache.

Logo, um Context/Prompt Engine deveria distinguir:

```text
static prefix
semi-static project context
dynamic task context
ephemeral observations
```

### 3.4 Compaction é checkpoint semântico

A conversa não pode crescer indefinidamente. Compaction preserva informação suficiente para continuar a tarefa sob um novo contexto reduzido.

Conclusão:

> **Compaction deve produzir um objeto observável e atribuível, não uma mutação invisível do histórico.**

---

## 4. Claude Code: isolamento, permissions e capacidades progressivamente materializadas

A documentação e os padrões operacionais do Claude Code fornecem três ideias relevantes para um Harness Builder.

### 4.1 Permissions são uma camada de runtime

Ferramentas podem ser permitidas, negadas ou sujeitas a confirmação. O modelo não é a autoridade final.

### 4.2 MCP é seam de integração, não necessariamente a ontologia do sistema

MCP resolve interoperabilidade de tools/context providers. Um framework mais amplo pode tratá-lo como adapter.

### 4.3 Context isolation e especialização

A prática de separar agentes/subagentes especializados reduz interferência entre:

- pesquisa;
- edição;
- verificação;
- exploração.

O princípio mais geral não é “tenha muitos agentes”, mas:

> **ownership de contexto deve seguir ownership de responsabilidade.**

---

## 5. OpenHands: events, statelessness e components

O OpenHands Software Agent SDK trata events como log append-only e integração entre components. Seu `Agent` é stateless entre steps e reconstrói o que precisa a partir do event history.

Lições:

- typed events são úteis;
- append-only history facilita pause/resume;
- condensers devem ser components substituíveis;
- tools podem seguir Action/Observation;
- security analysis pode mediar ações;
- Conversation pode ser lifecycle owner enquanto Agent permanece stateless.

O ponto mais útil é a separação:

```text
state/lifecycle owner
≠
reasoning component
```

AETHER pode ir além dessa abordagem ao tornar também **authority, signed evidence e resource conservation** propriedades do substrate.

---

## 6. Aider: estrutura de código e protocolos específicos por modelo

Aider continua valioso porque várias de suas decisões são altamente pragmáticas.

### 6.1 Repo map

Seu repository map fornece ao modelo:

- arquivos importantes;
- classes/funções;
- signatures;
- símbolos relevantes.

Isso reduz a necessidade de despejar o repositório inteiro no contexto.

### 6.2 Structural retrieval

Para código, a ordem recomendada de retrieval é aproximadamente:

```text
exact path / current files
  ↓
symbols / definitions
  ↓
references / dependency graph
  ↓
lexical search
  ↓
semantic search
  ↓
agentic exploration
```

Isso é superior a iniciar por embeddings para todo problema.

### 6.3 Model-specific edit protocols

Aider usa formatos diferentes porque modelos diferentes apresentam confiabilidade diferente com `diff`, `whole`, `udiff`, architect/editor etc.

Lição:

> **Provider/API compatibility não implica behavioral equivalence.**

### 6.4 Architect/editor

Separar raciocínio de edição pode melhorar resultados para certos modelos.

Generalização:

```text
reasoning strategy
≠
mutation protocol
```

O Harness Builder deve permitir combiná-los.

---

## 7. Context Engineering como sistema de seleção

Contexto é um recurso escasso e afeta simultaneamente:

- qualidade;
- custo;
- latência;
- cache;
- atenção;
- reliability.

### 7.1 Pirâmide de contexto

Para coding:

```text
L0 task + exact files
L1 symbols / AST
L2 dependency / reference graph
L3 lexical retrieval
L4 semantic retrieval
L5 episodic/project memory
L6 agentic exploration
L7 external research
```

A regra deveria ser:

> **usar o mecanismo mais barato e determinístico que atinge recall suficiente; escalar somente quando necessário.**

### 7.2 Context ownership

Main, researcher, editor e verifier não precisam compartilhar transcript completo.

Melhor:

```text
Research execution
    ↓
ResearchArtifact
    ↓
Consumer execution
```

onde o artifact contém:

- evidence refs;
- relevant files;
- symbols;
- hypotheses;
- uncertainties;
- provenance.

### 7.3 Context compaction

Um checkpoint operacional pode preservar:

```json
{
  "goal": "...",
  "constraints": [],
  "accepted_decisions": [],
  "completed": [],
  "pending": [],
  "critical_refs": [],
  "uncertainties": []
}
```

Compaction deve ter:

- input digest;
- output digest;
- strategy identity;
- token delta;
- provenance.

---

## 8. Memory não é “um vector database”

Um agente pode precisar de quatro horizontes conceituais.

### 8.1 Working memory

Estado necessário para a execução corrente:

- plano;
- hipóteses;
- changed artifacts;
- pending checks.

### 8.2 Checkpoint memory

Resumo retomável após compaction/pause/crash.

### 8.3 Episodic memory

Experiência anterior:

- problema;
- tentativas;
- falhas;
- resolução;
- evidência;
- lesson candidate.

### 8.4 Semantic/procedural memory

Conhecimento estável:

- arquitetura;
- convenções;
- procedimentos;
- pitfalls;
- domain rules.

A melhor arquitetura inicial não precisa de quatro stores. Pode usar:

```text
one memory contract
+ record classes
+ retention policies
+ consolidation strategies
+ retrieval policies
```

O segredo é **consolidation**.

---

## 9. Skills e progressive materialization

Uma skill não precisa ser primitive do substrate.

Pode ser:

```text
SkillDescriptor
    id
    description
    activation hints
        ↓ activate
SkillBundle
    instructions
    references
    schemas
    scripts
    tool refs
    policies
```

O princípio é:

```text
discovery context ≠ execution context
```

Isto escala melhor que inserir todas as instruções no prompt inicial.

---

## 10. Tool execution: proposta probabilística, execução determinística

Um princípio recorrente em sistemas confiáveis é:

```text
LLM/controller
     ↓
untrusted intent
     ↓
schema / semantic validation
     ↓
policy + capability + resource authorization
     ↓
sandbox / environment
     ↓
effect
     ↓
receipt
```

A tool não deve ser a autoridade sobre o próprio risco.

Uma descrição de ferramenta pode declarar:

- side effects;
- selector footprint;
- network needs;
- required secrets;
- determinism;
- idempotency;
- expected cost;
- cacheability.

Mas o runtime decide se o efeito é autorizado.

---

## 11. Effect semantics devem representar fases de confiança

Uma única classe universal `EffectRequest` pode parecer DRY, mas pode misturar:

- intent não confiável;
- authority metadata;
- leased execution;
- adapter invocation.

Uma separação mais robusta é:

```text
EffectIntent
    ↓ authorize
AuthorizedEffect / DispatchCommand
    ↓ adapt
EnvironmentCommand
    ↓ execute
Receipt
```

O identificador/digest causal permanece estável entre traduções.

Essa modelagem torna explícito **onde autoridade entra**.

---

## 12. Verification, evaluation e stopping

“Agent says done” é um sinal fraco.

Conclusão deveria significar:

```text
acceptance evidence satisfied
```

### 12.1 AcceptanceContract

Em vez de uma engine chamada `VerificationGraph`, usar data:

```yaml
acceptance:
  require:
    - syntax
    - typecheck
    - targeted-tests
    - regression
    - exterior-oracle
```

Cada criterion resolve para um verifier/evaluator/tool.

### 12.2 Verification ≠ exterior judgment

Verification pode ser:

- compiler;
- tests;
- static analysis;
- semantic checks;
- simulation.

Exterior evaluation é a autoridade que autentica um verdict conforme um oracle.

Separar essas camadas evita que o agente “autocertifique” sucesso.

---

## 13. Observability e Event Sourcing

Há duas necessidades diferentes:

### 13.1 Authoritative record

Eventos que precisam existir para o sistema ser correto:

- execution identity;
- grants;
- leases;
- effect intent/started/completed;
- spawn;
- evaluation binding;
- terminal state.

Falha de persistência aqui é falha do transition.

### 13.2 Telemetry

Informação útil, mas potencialmente best-effort:

- token chunks;
- verbose model traces;
- performance samples;
- UI heartbeat;
- debug logging.

Misturar ambos sob a mesma política leva a dois extremos ruins:

- tudo bloqueia execução;
- ou eventos essenciais podem ser perdidos silenciosamente.

A arquitetura recomendada é:

```text
one causal namespace
two durability classes
```

---

## 14. Agentic algorithm families

O ponto decisivo para um framework geral é não assumir que “agent” significa um único loop.

### 14.1 Reactive tool agent

```text
observe → infer → act → observe
```

### 14.2 Plan-and-execute

```text
plan
  ↓
execute subgoal
  ↓
update plan
```

### 14.3 Critic / refine

```text
produce
  ↓
critique
  ↓
revise
```

Self-Refine mostra que feedback e refinement iterativos podem melhorar outputs sem treinamento.

### 14.4 Reflexion

Reflexion armazena feedback linguístico em episodic memory e reutiliza essa reflexão em tentativas posteriores.

Lição para o substrate:

> reflection é uma strategy/memory pattern, não uma fase obrigatória do kernel.

### 14.5 Tree of Thoughts

ToT explora múltiplos caminhos, avalia branches e pode backtrack.

Isso demonstra que um loop linear `proposal → effect` não representa naturalmente toda computação agêntica observável.

### 14.6 Debate

Vários participantes produzem argumentos/soluções e um agregador/judge seleciona.

### 14.7 Portfolio / race

Executar vários solvers e cancelar os perdedores.

### 14.8 Evolutionary search

Gerar população de candidatos, medir fitness, selecionar/mutar.

### 14.9 Deterministic + LLM hybrid

Controle determinístico pode decidir **quando** invocar modelos e effects.

Conclusão:

> o substrate precisa representar executions, directives, joins/waits, artifacts, effects, evaluation e cancellation — não conhecer “debate”, “tree search” ou “evolution” como engines.

---

## 15. Por que um controller/directive seam é mais geral que um universal agent loop

Uma abstração mínima possível:

```text
ExecutionCoordinator
        │
        ▼
Controller.next(view)
        │
        ▼
Directive
```

Exemplos de diretivas:

```text
InvokeModel
InvokeEffect
SpawnExecution
RequestEvaluation
Wait / Suspend
EmitArtifact
Complete
```

Essas diretivas **não carregam autoridade**. O coordinator interpreta a diretiva usando services confiáveis.

Benefícios:

- reactive coding agent vira um controller;
- tree search vira outro;
- deterministic algorithm vira outro;
- debate vira composição de executions;
- evolutionary search vira controller/meta-controller;
- o kernel não muda.

Esse seam deve ser pequeno. Não deve virar um workflow language obrigatório.

---

## 16. Multi-agent: delegation must pay rent

Multi-agent aumenta:

- tokens;
- coordination overhead;
- state;
- failure modes;
- evaluation complexity.

Use quando traz:

- isolamento de contexto;
- especialização;
- paralelismo verdadeiro;
- independência de verificação;
- competição/diversidade de soluções.

Patterns úteis:

```text
Main + Researcher
Planner + Editor
Planner + Editor + Verifier
Parallel workers
Debate
Hierarchical delegation
```

Mas `Swarm` não precisa ser primitive.

---

## 17. Logical agents versus workers

Para escala, deve ser falso que:

```text
1 logical agent = 1 OS process
```

O target é:

\[
K_{workers} \ll N_{logical\ executions}
\]

A scheduler pode mapear executions para:

- in-process workers;
- subprocess pools;
- container pools;
- remote workers;

sem alterar identity semantics.

---

## 18. Concurrency: preservar opção, não pagar custo agora

Concorrência exige:

- selector soundness;
- cancellation;
- backpressure;
- resource accounting;
- scheduling fairness;
- conflict detection;
- reconciliation;
- order semantics.

O substrate deve preservar a possibilidade de async/event-driven placement, mas a semântica inicial pode permanecer sequencial.

Uma distinction importante:

> **event-sourced não significa event-bus assíncrono em toda parte.**

---

## 19. Model-aware harness

OpenAI-compatible APIs não tornam modelos operacionalmente equivalentes.

Um `ModelProfile` futuro pode combinar:

### Static capability

- context window;
- structured output;
- native tools;
- caching;
- parallel calls;
- reasoning controls.

### Measured profile

- tool-call reliability;
- edit reliability;
- latency p50/p95;
- cost distribution;
- instruction adherence;
- long-context degradation;
- protocol-specific success.

A route pode então selecionar:

```text
model
+ prompt strategy
+ edit protocol
+ tool encoding
+ reasoning budget
+ cache strategy
```

---

## 20. Harness-native learning: LEGO-RL

LEGO-RL parte do problema de que o harness real altera:

- compaction;
- serialization;
- tool feedback;
- model requests;
- trajectory shape.

Treinar uma política fora desse ambiente causa mismatch.

A contribuição conceitual mais relevante é:

> **o deploy harness participa da policy observada; treinamento que o remove pode otimizar um sistema diferente daquele que será executado.**

Para um Harness Builder, a consequência imediata não é “implementar RL”, mas:

- preservar raw model request/response attribution;
- registrar compaction;
- registrar route/model identity;
- registrar context digests;
- manter effects/receipts;
- manter reward/verdict binding;
- permitir que trainer/evaluator observe sem possuir o loop.

---

## 21. Agent Lightning: execution/training disaggregation

Agent Lightning propõe separar:

```text
agent/harness execution
        ≠
trainer
```

e transformar trajectories em uma interface de aprendizagem.

Isso combina bem com uma arquitetura onde:

- `D_H` identifica a composição;
- `D_R` identifica a execução;
- `D_X` identifica o experimento;
- training é consumidor do dataset.

---

## 22. Meta-cognição: níveis diferentes não devem ser confundidos

“Meta-cognição” pode significar objetos diferentes.

### Nível 1 — introspecção intra-execution

- uncertainty;
- critique;
- reflection;
- plan revision.

### Nível 2 — adaptação inter-episode

- episodic lessons;
- memory consolidation;
- strategy selection baseada em experiência.

### Nível 3 — harness adaptation

- trocar prompt;
- route;
- controller;
- context strategy;
- skill activation;
- tool configuration.

### Nível 4 — experiment design

- escolher quais variantes comparar;
- alocar budget experimental;
- detectar regressões;
- gerar hipóteses.

### Nível 5 — meta-search

- otimizar os próprios mutation operators;
- escolher search strategies;
- evoluir a forma de gerar harness candidates.

Esses níveis têm riscos e requisitos de evidência diferentes.

---

## 23. Automated Design of Agentic Systems (ADAS)

ADAS formula explicitamente o problema de **automatizar o design de sistemas agênticos**.

A ideia do Meta Agent Search é manter um archive de designs e usar um meta-agent para propor novos agentes em código.

A lição relevante para AETHER:

- agente pode ser representado como programa/composição;
- o espaço de search pode incluir prompts, control flow e components;
- um archive de candidatos pode acumular stepping stones.

Mas um framework de produção precisa adicionar:

- immutable candidate identity;
- evaluation isolation;
- holdout;
- rollback;
- promotion authority.

---

## 24. Darwin Gödel Machine: evolução aberta de coding agents

DGM modifica agentes, avalia cada versão em benchmarks e mantém um archive/árvore de candidatos.

Resultados publicados reportam melhora em SWE-bench e Polyglot.

O insight mais importante não é “self-modification irrestrita”, mas:

```text
candidate
  ↓ mutate
new candidate
  ↓ evaluate
archive / selection
```

Isso é muito diferente de:

```text
running production agent edits itself in place
```

AETHER deveria escolher o primeiro modelo.

---

## 25. AlphaEvolve: generate → measure → select → evolve

AlphaEvolve usa:

- seed program;
- evaluator definido;
- candidate generation;
- evolutionary selection;
- repeated improvement.

Esse padrão é diretamente generalizável para Harness Builder:

```text
FrozenHarness seed
   ↓
mutation operators
   ↓
Candidate FrozenHarnesses
   ↓
Evaluation protocol
   ↓
Pareto/frontier selection
   ↓
new generation
```

A diferença é que nosso objeto evoluído pode ser um harness, não apenas código algorítmico.

---

## 26. Reflexion, Voyager e skill accumulation

Voyager combina:

- automatic curriculum;
- iterative feedback;
- skill library.

Isso mostra um caminho de lifelong capability accumulation sem necessariamente alterar pesos.

Para um Harness Builder:

```text
successful trajectory
   ↓
candidate procedure/skill
   ↓
validation
   ↓
skill library
   ↓
lazy reuse
```

A fase crítica é **candidate validation**. Uma skill não deve ganhar autoridade por ter sido gerada pelo próprio agente.

---

## 27. Self-improvement precisa de um Experiment Plane

Sem um Experiment Plane, “melhorou” vira narrativa.

O mínimo:

```text
Candidate identity
Task/dataset identity
Environment identity
Model identity
Oracle identity
Protocol identity
Metrics
Statistical comparison
Promotion decision
```

Isso é a base da ciência do harness.

---

## 28. Multi-objective optimization e Pareto frontier

O objetivo não é apenas pass rate.

Um harness pode ser avaliado por:

\[
Q = quality
\]
\[
C = cost
\]
\[
L = latency
\]
\[
R = risk
\]
\[
S = stability
\]

A seleção pode manter uma Pareto frontier, em vez de colapsar tudo prematuramente em um único scalar.

Uma policy posterior pode escolher conforme o domínio.

---

## 29. Anti-Goodhart para Meta-Harness

Quanto mais poderosa a otimização, mais perigoso otimizar um proxy.

Medidas:

- exterior evaluator;
- hidden tests;
- holdout datasets;
- multiple oracles;
- anti-cheat checks;
- mutation testing dos gates;
- canary;
- regression suites;
- human promotion para mudanças de alto impacto.

A regra fundamental é:

> **o sistema que propõe a mudança não pode ser a única autoridade que mede e promove essa mudança.**

---

## 30. Síntese do estado da arte

A pesquisa converge para os seguintes princípios:

1. **Harness is part of capability.**
2. **Context management is a first-class system.**
3. **Agent loop is one algorithm, not the definition of agency.**
4. **Effects require deterministic mediation.**
5. **Memory needs consolidation, not indiscriminate persistence.**
6. **Skills should materialize lazily.**
7. **Typed artifacts are better coordination objects than transcript sharing.**
8. **Verification should drive stopping.**
9. **Exterior evaluation is stronger than self-judgment.**
10. **Events and trajectories make optimization measurable.**
11. **Model behavior requires model-specific protocols.**
12. **Multi-agent should be justified by measurable benefit.**
13. **Logical agents should be cheaper than workers.**
14. **Concurrency should be enabled after correctness, not before it.**
15. **Learning must preserve native harness behavior.**
16. **Self-improvement should generate new immutable candidates, not mutate production invisibly.**
17. **Experimentation should precede large-scale distribution.**
18. **The ultimate object of optimization can be the harness composition itself.**

---

# CAPÍTULO II — APLICAÇÃO AO AETHER/VANGUARD: HARNESS BUILDER, META-HARNESS E EVOLUÇÃO DE ALTA ORDEM

## 31. O ponto de partida real do AETHER

A arquitetura vigente já contém várias decisões alinhadas ao estado da arte:

```text
Agent = Principal + HarnessInstance
Harness = f(manifest, plugins)
State = fold(Events)
D_H = composition identity
D_R = execution identity
D_X = experiment identity
spawn = recursive delegation
kernel = effect authority
evaluator = exterior judge
```

Isso é mais forte que a maioria dos frameworks leves porque identidade, autoridade e evidence não são deixados implícitos.

A revisão independente do código, porém, mostrou que a implementação ainda possui uma assimetria:

```text
TRUST / EFFECT substrate      strong and relatively general
STRATEGY / EXECUTION runtime  still coding/reactive shaped
MHF composition path          partially integrated
```

Portanto, o objetivo não é substituir a base. É completar a separação.

---

## 32. O que preservar como substrate permanente

### 32.1 Typed identity

- Project;
- Principal;
- Execution;
- Episode;
- causal lineage.

### 32.2 Canonical composition identity

Um harness compilado precisa ter uma identidade completa:

\[
D_H = H(
manifest,
resolved\ plugins,
controller,
prompts,
policies,
capability\ ceiling,
model\ routes,
behavioral\ assets
)
\]

### 32.3 Execution identity

\[
D_R = H(
D_H,
runtime\ build,
environment,
model\ identity,
oracle\ identity,
execution\ relevant\ configuration
)
\]

### 32.4 Experiment identity

\[
D_X = H(
D_R,
dataset,
protocol,
experimental\ controls
)
\]

### 32.5 Capability / selector / grant / lease machinery

Esses mecanismos são TCB.

### 32.6 Effect mediation

Todo external side effect relevante atravessa o substrate.

### 32.7 Resource accounting

Budget settlement não pertence ao planner/plugin.

### 32.8 Authoritative durable history

O state plane é durable record + reducers, não memória do controller.

### 32.9 Plugin containment enforcement

Loader/broker controla **plugin code authority** de forma separada das capabilities do agente.

### 32.10 Exterior evaluation authenticity

Plugins podem solicitar julgamento; não podem assinar o próprio verdict.

---

## 33. O que precisa tornar-se efetivamente composable

O AETHER não ganha liberdade por declarar plugins; ganha quando o production execution realmente depende deles.

As superfícies prioritárias:

- controller / decision strategy;
- planning/search;
- context selection;
- context compaction;
- memory retrieval/consolidation;
- model routing;
- toolkits;
- evidence request construction;
- retry/escalate policy;
- reflection;
- delegation policy;
- domain adapters;
- acceptance contracts.

---

## 34. PROPOSTA DE EMENDA A — `EpisodeEngine` como controller reativo, não engine universal

### Problema

O loop atual é adequado para coding reativo:

```text
model → proposal → effect → observation → repeat
```

Mas algoritmos futuros precisam de:

- branching;
- multiple model calls before effect;
- wait/join;
- heterogeneous spawn;
- race;
- cancellation;
- branch evaluation;
- deterministic subroutines.

Esconder tudo dentro de `IPlanner.plan()` torna:

- trajectory opaca;
- budget attribution difícil;
- child execution invisível;
- scheduler incapaz de otimizar.

### Direção

Criar um pequeno `ExecutionCoordinator` first-party.

```text
ExecutionCoordinator
    │
    ├── owns lifecycle
    ├── owns identity
    ├── owns scheduling
    ├── owns cancellation
    ├── owns trusted service dispatch
    │
    ▼
Controller
    │
    ▼
Directive
```

O atual loop vira:

```text
ReactiveAgentController
```

### Diretivas candidatas

```text
InvokeModel
InvokeEffect
SpawnExecution
RequestEvaluation
Wait / Suspend
EmitArtifact
Complete
```

A lista **não deve ser congelada sem dois witnesses**: Coding + um domínio não-coding.

### Constraint

Directives são intents; não carregam authority.

**Status:** requer ADR se alterar a semântica normative do scheduler/turn machine.

---

## 35. PROPOSTA DE EMENDA B — recursive effective scope deve ser TCB

Se child authority é uma invariante:

\[
C_{child} \subseteq C_{parent}
\]

ela não pode depender de o controller atual lembrar de checar antes de dispatch.

O kernel/trusted authorization boundary deve receber uma prova/handle de effective scope que não possa ser alargado pelo plugin.

### Regra

```text
controller validation  = early convenience
kernel enforcement     = security truth
```

**Status:** fortalecer antes de tornar heterogenous spawn público.

---

## 36. PROPOSTA DE EMENDA C — substituir “one EffectRequest class” por one effect algebra

Não precisamos de uma kitchen-sink class.

Target:

```text
EffectIntent
    ↓
AuthorizedEffect
    ↓
EnvironmentCommand
    ↓
Receipt
```

Propriedades invariantes:

- causal digest;
- attribution;
- selector;
- cost/reservation relation;
- receipt binding.

**Status:** alteração de contract; requer versionamento/ADR.

---

## 37. PROPOSTA DE EMENDA D — exatamente cinco SPIs não deve virar objetivo em si

A SPEC vigente congela cinco SPIs. A revisão independente encontrou motivos para separar “semantic role stable” de “exact count stable”.

Exemplos:

- `reflect()` não precisa estar em todo planner;
- EvaluationGate mistura request, verified verdict consumption e post-verdict policy;
- toolkit compensation não é universal;
- model provider e routing têm diferentes trust profiles.

Recomendação:

> congelar contracts pelo papel semântico comprovado, não para preservar um número.

Possível resultado ainda pode ter cinco interfaces. O ponto é que **“cinco” não deve ser a invariante arquitetural**.

**Status:** proposta explícita de ADR; não é law atual.

---

## 38. PROPOSTA DE EMENDA E — authoritative events e telemetry possuem durability diferente

Criar semantic classes:

```text
AuthoritativeRecord
TelemetryRecord
```

### Authoritative

- identity;
- grants;
- leases;
- accepted effect intents;
- effect terminal states;
- child lifecycle;
- evaluation binding;
- terminal execution state.

Persist failure → transition falha/faulta.

### Telemetry

- token stream;
- verbose traces;
- performance samples;
- UI events.

Pode ser buffered/sampled/dropped com loss accounting.

---

## 39. PROPOSTA DE EMENDA F — per-project sequencing deve ser atomic antes de concorrência

Hoje a arquitetura já escolhe `project_id` como consistency unit.

Antes de múltiplos writers concorrentes:

```text
append(expected_head, event)
```

deve ser atomic, ou:

```text
one sequencer/mailbox per Project
```

Um conflict nunca pode silenciosamente produzir duas chains.

Isso é pré-requisito de concurrency, não de Wave 4 single-thread.

---

## 40. A equação de produto do Harness Builder

O produto deve aproximar-se de:

```text
Executable Harness =
    Frozen Composition
  + Controller
  + Strategy Plugins
  + Policies
  + Model Routes
  + Environment Bindings
  + Trusted Execution Substrate
```

e não:

```text
class Agent(BaseAgent):
    ...
```

---

## 41. HarnessManifest como programa declarativo de composição

Um manifesto futuro pode expressar:

```yaml
api: mhf.harness/2

controller:
  plugin: mhf.controller.reactive-coding@1

strategies:
  context:
    plugin: mhf.context.repo-structural@2
  memory:
    plugin: mhf.memory.hybrid@1
  post_verdict:
    plugin: mhf.policy.retry-escalate@1

models:
  primary:
    route: frontier-reasoner
  editor:
    route: fast-editor
  verifier:
    route: independent-verifier

tools:
  - mhf.toolkit.fs@2
  - mhf.toolkit.patch@3
  - mhf.toolkit.terminal@2

environment:
  adapter: mhf.env.code-workspace@1

policy:
  filesystem: workspace
  network: approval
  destructive: deny

acceptance:
  require:
    - tests
    - typecheck
    - exterior_oracle

budget:
  tokens: 200000
  usd_micros: 10000000
  turns: 80
  max_depth: 4
```

Esse documento é **data**, não uma nova workflow language.

---

## 42. Harness Compiler

Pipeline:

```text
Manifest
   ↓ parse
Schema-valid AST
   ↓ resolve
Plugin/model/environment refs
   ↓ verify
signatures / compatibility / ceilings
   ↓ intersect
effective policy + capability ceiling
   ↓ freeze
FrozenHarness
   ↓ canonicalize
D_H
```

Regras:

- unknown refs falham no compose;
- behavior-affecting input entra em `D_H`;
- plugins não mudam mid-run;
- changing composition produz novo `D_H`.

---

## 43. Controller Host e managed services

Plugins cognitivos não deveriam abrir provider APIs diretamente.

O host deve oferecer:

```text
ModelClient
ContextView
MemoryView
ArtifactClient
SpawnClient
EvaluationClient
```

Esses clients são capabilities limitadas.

### ModelClient

Responsabilidades do host:

- credentials;
- model identity;
- cost;
- retry;
- cassette;
- request/response trace;
- rate limits.

Routing policy pode ser plugin, mas invocation continua managed.

---

## 44. Context subsystem aplicado ao Coding Pack

Coding Pack deve possuir:

```text
repo discovery
symbol graph
AST
reference graph
lexical retrieval
semantic retrieval
repo-map rendering
```

O runtime genérico só conhece:

```text
ContextManager.compile(view, budget)
```

ou o contract que sucedê-lo.

Falsifier:

> novo domínio não precisa importar conceitos de repository no substrate.

---

## 45. Typed artifacts como linguagem de coordenação

### ResearchArtifact

```yaml
relevant_artifacts: [...]
evidence_refs: [...]
hypotheses: [...]
uncertainties: [...]
```

### PlanArtifact

```yaml
goal: ...
steps: [...]
constraints: [...]
acceptance_refs: [...]
```

### ChangeArtifact

```yaml
patch_ref: ...
affected_entities: [...]
assumptions: [...]
```

### VerificationArtifact

```yaml
criteria: [...]
results: [...]
evidence: [...]
```

Artifacts precisam ser:

- content-addressed;
- typed;
- provenance-bound;
- shareable entre executions.

Isso permite multi-agent sem transcript flooding.

---

## 46. Meta-cognição no AETHER

A meta-cognição não deve aparecer como um `MetaAgent` privilegiado.

Ela pode ser uma execução normal com capabilities específicas.

```text
Meta execution =
Principal
+ MetaHarness
+ meta-capabilities
```

### Capabilities possíveis

- read trajectories;
- create candidate manifests;
- create candidate skills;
- request experiments;
- preregister oracles;
- write hypothesis artifacts.

### Capabilities que não deve possuir automaticamente

- mutate active production harness;
- overwrite trusted evaluator;
- mint grants;
- promote itself;
- edit substrate TCB;
- alter holdout dataset.

Isso torna:

> **meta-cognition capability-shaped, não trust-shaped.**

---

## 47. Nível 1 — Reflection intra-execution

Uma strategy pode observar:

- receipts;
- failures;
- uncertainty;
- current plan.

e produzir:

- plan revision;
- reground request;
- retry;
- escalate;
- abandon.

Sem nova engine.

---

## 48. Nível 2 — Post-episode Meta-Reflection

Uma execution separada recebe:

```text
TrajectoryRef
Outcome
Cost
Verdict
```

e produz:

```text
ReflectionArtifact
LessonCandidate
HarnessMutationProposal
SkillCandidate
```

Ela não promove nada.

---

## 49. Nível 3 — Harness Optimization

Objeto de otimização:

```text
FrozenHarness candidate
```

Mutation space inicial:

- system prompt fragments;
- controller parameters;
- context budget;
- retrieval sequence;
- compaction strategy;
- model routes;
- tool descriptions;
- skill activation rules;
- retry thresholds;
- delegation thresholds.

Trusted core fica fora do mutation space.

---

## 50. Nível 4 — Population / Evolution

Manter archive:

```text
HarnessArchive
 ├── D_H A
 ├── D_H B
 ├── D_H C
 └── lineage edges
```

Cada candidate é imutável.

O search pode ser:

- evolutionary;
- Bayesian;
- bandit;
- hill-climbing;
- beam;
- novelty search;
- LLM meta-search.

O Experiment Plane não precisa conhecer a search strategy.

---

## 51. Nível 5 — Meta-search de alta ordem

Aqui o sistema não otimiza apenas harnesses. Ele otimiza **como procura novos harnesses**.

Exemplos:

- qual mutation operator usar;
- qual archive parent selecionar;
- qual benchmark slice executar;
- quanto budget alocar;
- qual surrogate metric confiar;
- quando explorar versus explorar menos.

Formalmente:

```text
Level 0: task solution
Level 1: strategy adaptation
Level 2: harness adaptation
Level 3: population search
Level 4: search-strategy adaptation
Level 5: learner/model adaptation
```

Esse é o ponto em que “meta high-order evolution” ganha um significado operacional e mensurável.

---

## 52. O Meta-Harness

Meta-Harness é uma **composição**, não uma engine.

```text
MetaHarness
    controller: experiment-designer
    tools:
      - trajectory.query
      - harness.mutate
      - experiment.submit
      - archive.read
    context:
      - previous experiments
      - frontier
      - failures
    policy:
      no-production-write
      no-evaluator-write
      no-holdout-read
```

Saída:

```text
ExperimentProposal
CandidateHarness[]
```

O scheduler normal executa isso sob budget.

---

## 53. Experiment Plane

O Experiment Plane é o coração do self-improvement governado.

### 53.1 ExperimentSpec

```yaml
baseline: D_H_A
candidates:
  - D_H_B
  - D_H_C

dataset: benchmark@version
protocol: paired-v1

controls:
  model_identity: fixed
  environment: fixed
  oracle: fixed

metrics:
  - pass_rate
  - cost
  - latency
  - failure_rate
```

### 53.2 Result

```text
ExperimentResult
  D_X
  cells
  metrics
  confidence intervals
  safety failures
  artifacts
```

### 53.3 Promotion

```text
candidate wins experiment
       ≠
candidate becomes production
```

Promotion é uma ação separada.

---

## 54. Scientific comparison

Para tasks pareadas binárias, McNemar é adequado em muitos casos.

Outras análises:

- bootstrap confidence intervals;
- paired cost delta;
- latency distributions;
- failure mode stratification;
- calibration/Brier score;
- Pareto frontier.

Nenhuma estatística única deve ser tratada como universal.

---

## 55. Holdout e anti-overfitting do Meta-Harness

O Meta-Harness pode acessar:

```text
training/evolution set
development set
```

mas não necessariamente:

```text
sealed holdout
```

Promotion exige:

- hidden evaluation;
- external evaluator;
- regression gates;
- no policy violations.

Isso reduz benchmark hacking.

---

## 56. Self-improvement governado

Fluxo recomendado:

```text
Production trajectories
      ↓
analysis / hypothesis
      ↓
candidate generation
      ↓
new D_H
      ↓
experiment runs (new D_R)
      ↓
D_X comparison
      ↓
exterior evaluation
      ↓
promotion decision
      ↓
canary
      ↓
default pointer update
```

Nunca:

```text
running harness edits itself
→ silently becomes production
```

---

## 57. Rollback é parte da arquitetura de evolução

Toda promotion deve registrar:

- previous default;
- candidate;
- evidence;
- promoter identity;
- rollback target.

Rollback precisa ser simples:

```text
default pointer
D_H_new → D_H_previous
```

Não reverter history.

---

## 58. Evolução de skills

Pipeline:

```text
successful trajectories
     ↓ mine repeated procedure
SkillCandidate
     ↓ validation
     ↓ ablation
     ↓ external evaluation
SkillArtifact
     ↓ optional harness inclusion
new D_H
```

A skill não é “memory text copiado do agente”.

É um artefato versionado.

---

## 59. Evolução de context strategies

O sistema pode experimentar:

- repo map budgets;
- symbol ranking;
- semantic thresholds;
- exploration triggers;
- compaction timing;
- retrieval ordering.

Métrica:

\[
Utility =
quality
- \lambda_1 cost
- \lambda_2 latency
- \lambda_3 context\ waste
\]

---

## 60. Evolução de model routing

Um router pode aprender:

\[
P(success \mid task, model, harness, state)
\]

Mas o route decision precisa deixar provenance.

O resultado de aprendizado pode ser:

- table;
- calibrated classifier;
- bandit policy;
- learned model.

Ele continua sendo policy acima do provider host.

---

## 61. Multi-agent pós-foundation

Sequência recomendada:

### 61.1 Sequential heterogeneous delegation

Primeiro provar:

```text
Main harness
  ↓ spawn
Research harness
  ↓ artifact
Main resumes
```

### 61.2 Independent verifier

```text
Editor harness
    ↓
ChangeArtifact
    ↓
Verifier harness
```

### 61.3 Parallel workers

Só depois de:

- selector soundness;
- budget conservation;
- cancellation;
- race tests.

### 61.4 Portfolio

Executar várias estratégias e selecionar.

Isso aproxima AETHER de um substrate de algorithms, não de “um swarm framework”.

---

## 62. Worker pool e escala

Target:

```text
Logical Execution Registry
        ↓
Scheduler
        ↓
bounded worker pool
        ↓
plugin/model/environment hosts
```

State não vive no worker.

Worker é placement.

Isso permite:

- local sequential;
- local async;
- process pools;
- remote workers;

sem alterar execution identity.

---

## 63. Backpressure

Futuro scheduler precisa controlar:

- model concurrency;
- tool concurrency;
- sandbox pool;
- ledger append capacity;
- evaluator capacity;
- token budget;
- per-project quotas.

Backpressure deve ser explícito, não emergir como timeouts aleatórios.

---

## 64. Cancellation

Todo long-running operation deve possuir:

- cancellation token;
- causal owner;
- deadline;
- reconciliation semantics.

Cancelar um effect externo pode produzir `undeterminable`, não “failed” por conveniência.

---

## 65. O papel do Coding Agent

Coding continua sendo o melhor laboratório inicial porque oferece:

- tests;
- compilers;
- static analysis;
- precise artifacts;
- reproducible environments;
- objective partial oracles;
- rich failures.

Mas coding não prova generalidade.

---

## 66. Generality witness

Logo após o foundation MVP, construir um domínio propositalmente pequeno e diferente.

Exemplos:

- TableWorld;
- structured data transformation;
- document evidence task;
- simple planning environment.

Gate:

```text
new pack added
AND
core/kernel diff == 0
AND
trusted event semantics diff == 0
AND
new engine == 0
```

Esse é um falsifier de generalidade.

---

## 67. Harness Builder API mental model

Usuário deveria poder pensar:

```python
h = Harness(
    controller="search.best_first",
    context="domain.context.v2",
    memory="episodic+semantic",
    tools=["domain.read", "domain.act"],
    model_routes={"reasoner": "frontier"},
    acceptance="domain.oracle.v3",
)
```

O builder compila isso em uma composição congelada.

A API real pode ser declarativa, Python SDK ou ambos.

---

## 68. Não criar inheritance zoo

Evitar:

```text
CodingAgent
ResearchAgent
MetaAgent
SwarmAgent
DebateAgent
TreeSearchAgent
```

Preferir:

```text
Principal + FrozenHarness + Controller
```

As diferenças são composition.

---

## 69. Guardrails como infraestrutura, não produto rígido

### Sempre enforced

- identity integrity;
- no authority widening;
- lease/budget conservation;
- writer authority;
- effect mediation;
- plugin digest/containment;
- evaluator signature authenticity.

### Policy/composition

- approvals;
- allowed network;
- risk threshold;
- evaluation criteria;
- memory retention;
- sandbox tier;
- human-in-loop;
- retry policy.

Assim um harness experimental pode ser permissivo sem poder falsificar história ou autoridade.

---

## 70. Trusted versus replaceable

| Concern | Status target |
|---|---|
| Identity issuance | Trusted |
| JCS / digest semantics | Trusted |
| Project sequencer | Trusted |
| Capability / grant | Trusted |
| Budget settlement | Trusted |
| Effect authorization | Trusted |
| Sandbox enforcement | Trusted host |
| Evaluator verification | Trusted exterior/host |
| Controller | Replaceable |
| Planner/search | Replaceable |
| Context | Replaceable |
| Memory selection | Replaceable |
| Tool implementation | Replaceable behind mediation |
| Model routing | Replaceable policy |
| Model provider | Host adapter |
| Acceptance criteria | Composition |
| Reflection | Composition |
| Delegation policy | Composition |
| Meta-Harness | Composition |

---

## 71. Data contract necessário para self-improvement

Uma trajectory realmente científica precisa bindar:

```text
project_id
execution_id
episode_id
principal_id
parent_principal_id
D_H
D_R
controller digest
plugin digests
model routes used
model fingerprints
environment digest
oracle identity
context digests
compaction records
model requests/responses refs
directives / effect intents
receipts
actual settled costs
artifacts
verdict
terminal reason
completeness markers
```

Sem isso, o sistema acumula “logs”, não dataset confiável.

---

## 72. Materialized trajectory versus ledger

O ledger não precisa carregar todos os bytes.

Melhor:

```text
authoritative ledger
    ↓ refs
CAS / trace store
    ↓
versioned trajectory materializer
```

`mhf.trajectory/1` pode ser uma view/materialization com versão explícita.

O importante é não perder causal data no momento da execução.

---

## 73. Learning Plane

Depois de dataset suficiente:

### 73.1 Offline analysis

- failure clustering;
- route comparison;
- context ablations;
- cost analysis.

### 73.2 Prompt/harness optimization

Sem weight updates.

### 73.3 SFT / preference learning

A partir de evidence-valid trajectories.

### 73.4 Harness-native RL

Usando execution harness real via proxy/adapter.

### 73.5 Learned scheduling/routing

Quando houver volume e causal attribution suficientes.

O trainer não vira authority.

---

## 74. Meta-productivity: otimizar capacidade de melhorar

Um sistema de ordem superior pode otimizar não apenas benchmark atual, mas sua capacidade de gerar bons descendentes.

Isso sugere métricas futuras como:

```text
direct task quality
+
descendant quality
+
diversity / novelty
+
cost of improvement
```

Essa ideia aparece em trabalhos posteriores à DGM que distinguem performance imediata de *metaproductivity*.

É uma pesquisa avançada e não deve entrar no MVP.

---

## 75. Fronteiras do mutation space

### Permitido inicialmente

- prompts;
- controller config;
- context config;
- retrieval;
- model routes;
- skill selection;
- tool metadata;
- retry thresholds;
- budgets dentro de ceiling;
- acceptance composition.

### Permitido depois com revisão

- controller code;
- plugin code;
- mutation operators;
- experiment policies.

### Fora do self-mutation automático

- kernel authority semantics;
- evaluator signing keys;
- project writer rules;
- holdout secrecy;
- promotion authority;
- root capability ceiling.

Essas áreas podem evoluir por engenharia humana/ADR, não por automatic self-promotion.

---

## 76. Harness Genome

Se quisermos usar a metáfora de “genome”, ela deve ser operacional:

```text
Genome = canonical behavior-affecting composition fields
```

Ou seja:

\[
Genome \equiv D_H\ input
\]

Não há necessidade de uma segunda representação biológica.

Mutation = transformação sobre manifest AST.

---

## 77. Harness lineage

Cada candidate pode registrar:

```text
parent_D_H
mutation_operator
mutation_parameters
generation
experiment_refs
```

Isso cria uma árvore/graph como **projection** sobre records, não como nova source of truth.

---

## 78. Meta-Harness search policy

Um Meta-Harness pode escolher entre:

- exploit frontier;
- novelty;
- repair failures;
- specialize per task cluster;
- compress cost;
- reduce latency;
- improve robustness.

Isso é policy.

O Experiment Plane continua constante.

---

## 79. Cross-domain transfer

Uma pergunta científica importante:

> uma estratégia descoberta em coding melhora outros domínios?

Testar:

```text
controller discovered on coding
       ↓
freeze
       ↓
evaluate on research/math/data witness
```

Transfer positivo sugere abstrações mais gerais.

---

## 80. Harness portfolio

Em vez de buscar um único “melhor harness”, manter:

```text
HarnessPortfolio
  coding-small
  coding-large
  research
  high-risk
  low-cost
  long-context
```

Um router seleciona conforme task.

Isso evita overfitting a um único aggregate score.

---

## 81. Adaptive selection

Depois de dados suficientes:

\[
h^* = \arg\max_h E[
Q - \lambda C - \mu L - \rho R
\mid task,state
]
\]

A seleção é explicável porque candidates possuem identities e historical evidence.

---

## 82. Experiment-before-distribution

A ordem recomendada:

```text
single-node correctness
  ↓
one real harness
  ↓
generality witness
  ↓
measurement
  ↓
experiment plane
  ↓
multi-agent
  ↓
controlled concurrency
  ↓
prove bottleneck
  ↓
distribution
```

Distribuição aumenta throughput.

Experimentação aumenta conhecimento.

---

## 83. Roadmap aplicado

### Gate A — Foundation correction before public API freeze

Resolver somente seams que podem fossilizar o produto:

1. child/effective authority enforcement no TCB;
2. controller/directive seam;
3. one composition compiler/truth;
4. plugin authority boundary;
5. effect phase algebra;
6. authoritative durability/atomic sequencing;
7. trajectory attribution suficiente.

### Gate B — Foundation E2E

Um real coding run:

- model;
- authorized effects;
- sandbox;
- durable WAL;
- cold replay;
- signed verdict;
- complete `D_H/D_R`;
- real cost;
- trajectory.

### Gate C — Generality witness

Segundo domínio, core diff zero.

### Stage D — Harness Builder 1.0

- stable controller contract;
- stable composition compiler;
- context/memory/tool plugin maturity;
- typed artifacts;
- acceptance contracts;
- ablation lab.

### Stage E — Sequential multi-agent

- heterogeneous spawn;
- artifacts;
- verifier;
- portfolio.

### Stage F — Controlled concurrency

- worker pools;
- cancellation;
- backpressure;
- selector soundness.

### Stage G — Experiment Plane / Meta-Harness

- candidate archive;
- mutation;
- paired evaluation;
- promotion pipeline.

### Stage H — Learning

- routing;
- prompt optimization;
- SFT/preference;
- harness-native RL.

### Stage I — Higher-order evolution

- meta-search;
- learned mutation;
- metaproductivity;
- cross-domain transfer.

---

## 84. O que explicitamente não implementar no foundation MVP

- distributed scheduler;
- NATS/Kubernetes control plane;
- WASM default;
- graph database;
- swarm engine;
- workflow DAG engine;
- competence graph como core;
- automatic self-promotion;
- arbitrary self-edit do TCB;
- universal vector DB;
- learned scheduler;
- RL trainer;
- Meta-Harness runtime especial.

---

## 85. Matriz de decisões

| Tema | Disposição |
|---|---|
| Python-first substrate | KEEP |
| `vanguard/packages` canonical | KEEP |
| Capability kernel | KEEP |
| Exterior evaluator | KEEP |
| Project-scoped event truth | KEEP + strengthen atomic head |
| `D_H/D_R/D_X` | KEEP + complete |
| JSON Schema + JCS | KEEP |
| Wire-first plugins | KEEP |
| Freeze-at-compose | KEEP |
| Sequential foundation | KEEP |
| `Agent = Principal + HarnessInstance` | KEEP |
| Swarm as policy | KEEP |
| Coding as first pack | KEEP |
| Universal `EpisodeEngine` semantics | **REVISIT / amend** |
| Exactly five SPIs as invariant | **REVISIT / amend** |
| One universal EffectRequest type | **REVISIT / phase algebra** |
| Agency-only child-scope enforcement | **STRENGTHEN into TCB** |
| Dual composition paths | **ELIMINATE** |
| Plugin access to Governor/kernel | **REJECT** |
| Reflection mandatory on all planners | **SIMPLIFY** |
| Trajectory = schema only | **STRENGTHEN scientifically** |
| Model/sandbox untrusted plugins now | DEFER |
| Multi-agent now | DEFER until E2E + witness |
| Concurrency now | DEFER |
| Meta-Harness now | DEFER |
| Self-improvement now | DEFER |
| Experiment data capture now | **YES — irreversible** |

---

## 86. Falsifiers arquiteturais adicionais sugeridos

Estes são candidatos de research/engineering; precisam de ADR/plan antes de virarem gates oficiais.

### H-01 — Controller substitution

Trocar apenas controller muda o algoritmo sem diff no kernel/runtime trust mechanisms.

### H-02 — Context substitution

Trocar context strategy não muda session/kernel.

### H-03 — One composition truth

Dois manifests semanticamente equivalentes compilam para o mesmo resolved representation e `D_H`.

### H-04 — No plugin authority import

Plugin não importa kernel Governor, event store implementation, signing keys ou generic writer.

### H-05 — Heterogeneous spawn

Parent pode spawnar um `FrozenHarness` diferente sob authority/budget atenuados.

### H-06 — Generality witness

Adicionar domínio #2 não altera trusted core.

### H-07 — Trajectory attribution completeness

Toda execution de benchmark tem os campos necessários para comparar causalmente harnesses.

### H-08 — Promotion separation

Meta-Harness não consegue alterar production default sem promotion authority separada.

### H-09 — Holdout secrecy

Search process não consegue ler sealed evaluation data.

### H-10 — Rollback

Toda promotion consegue retornar ao predecessor sem mutar history.

---

## 87. Métricas principais do Harness Builder

### Outcome

- success / pass;
- robustness;
- regression rate.

### Economic

- tokens;
- provider cost;
- sandbox cost;
- wall time;
- compute time.

### Process

- tool failures;
- invalid proposals;
- compactions;
- retries;
- escalations;
- context churn;
- cache hits.

### Safety / trust

- denied effects;
- authority violations;
- sandbox violations;
- unsigned verdict attempts;
- incomplete trajectories.

### Evolution

- candidate win rate;
- transfer;
- diversity;
- improvement cost;
- regression frequency;
- descendant potential.

---

## 88. Métrica de sucesso arquitetural

A métrica de arquitetura mais importante não é número de plugins.

É:

\[
CoreDiff(new\ capability)
\]

Idealmente:

```text
new capability
    → new composition/controller/plugin
    → core diff ≈ 0
```

O segundo sinal:

\[
AttributionCompleteness \rightarrow 1
\]

Se o sistema não consegue explicar qual composição, modelo, contexto, tool strategy e environment produziram um resultado, não consegue melhorar cientificamente.

---

## 89. O que impediria AETHER de tornar-se SOTA

1. Congelar um ReAct coding loop como “a arquitetura universal”.
2. Ter dois compilers/composition truths.
3. Permitir que plugins controlem budgets/authority.
4. Confundir event history com best-effort logs.
5. Prometer replay a partir de identities incompletas.
6. Acumular abstrações antes de um vertical path real.
7. Introduzir multi-agent antes de demonstrar single-agent harness quality.
8. Introduzir concurrency antes de cancellation/backpressure/resource correctness.
9. Fazer RL sobre trajectories incompletas.
10. Permitir self-improvement sem exterior evaluation/holdout.
11. Otimizar um benchmark único até Goodhart.
12. Confundir maior número de components com maior generalidade.

---

## 90. O diferencial possível do AETHER

Frameworks leves conseguem alta composability.

Frameworks de produção conseguem sandboxing e tool use.

Frameworks de RL conseguem otimizar agents.

O diferencial plausível do AETHER é combinar:

```text
high composability
+
strong identity
+
capability authority
+
resource conservation
+
exterior evidence
+
replay / causal history
+
experiment identity
+
harness-level optimization
```

A pergunta de design não é:

> “como competir em número de integrations?”

É:

> **“como tornar a composição inteira um objeto reproduzível, mensurável e evoluível sem dar ao sistema que está sendo otimizado autoridade para falsificar sua própria evidência?”**

Essa é uma tese mais forte.

---

# Conclusão

O aprendizado de agentic coding em 2026 sugere que a próxima camada de progresso não virá apenas de modelos melhores. Virá da engenharia do sistema que decide:

- qual contexto mostrar;
- qual estratégia usar;
- quais tools executar;
- como verificar;
- quando delegar;
- quanto gastar;
- como registrar;
- como comparar;
- como aprender com execuções anteriores.

AETHER já possui uma fundação incomum porque colocou cedo no design:

- authority;
- provenance;
- event-derived state;
- content identity;
- exterior evaluation;
- recursive delegation;
- experiment identity.

O passo decisivo é garantir que **essas propriedades fiquem abaixo da linha de extensão**, enquanto a maior parte da inteligência fica acima.

A arquitetura target pode ser resumida assim:

```text
                         EXPERIMENT / EVOLUTION
                  candidate generation · ablation
                 archive · selection · promotion
                              │
                              ▼
                         HARNESS BUILDER
                 manifest → resolve → verify → freeze
                              │ D_H
                              ▼
                     EXECUTION COORDINATOR
                lifecycle · scheduling · cancellation
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
                 CONTROLLERS        STRATEGIES
             reactive/search/...  context/memory/routing
                     │                 │
                     └────────┬────────┘
                              ▼
                      TRUSTED SUBSTRATE
               identity · grants · leases · effects
                  ledger · containment · evidence
                              │
                              ▼
                     MODELS / ENVIRONMENTS
```

Meta-cognição é uma composição nesse sistema.

Multi-agent é uma composição nesse sistema.

Tree search é um controller nesse sistema.

Evolution é uma search policy sobre FrozenHarnesses.

Self-improvement é um pipeline de candidatos e experimentos.

O kernel não precisa “tornar-se inteligente”.

A hipótese final é:

> **AETHER pode tornar-se um framework de evolução de inteligência agêntica se mantiver o trusted substrate pequeno, tornar o control/strategy plane realmente substituível, tratar harnesses como artefatos imutáveis e construir self-improvement sobre evidência exterior e experimentação reproduzível.**

O teste da hipótese não é uma declaração de generalidade.

É construir, medir e tentar falsificá-la repetidamente:

```text
new domain?
new algorithm?
new coordination pattern?
new memory?
new meta strategy?

Did trusted core need a new engine?
```

Enquanto a resposta continuar sendo “não; foi composição”, o substrate está funcionando.

---

# Fontes de pesquisa

## Benchmarks e harness engineering

- Terminal-Bench 2.1 verified leaderboard — https://www.tbench.ai/leaderboard/terminal-bench/2.1?verified=true
- Harbor documentation — https://www.harborframework.com/docs
- Harbor Terminal-Bench tutorial — https://www.harborframework.com/docs/tutorials/running-terminal-bench
- OpenAI, *Unrolling the Codex agent loop* — https://openai.com/index/unrolling-the-codex-agent-loop/
- OpenAI, *Unlocking the Codex harness: how we built the App Server* — https://openai.com/index/unlocking-the-codex-harness/
- OpenAI, *Harness engineering: leveraging Codex in an agent-first world* — https://openai.com/index/harness-engineering/
- OpenAI, *Running Codex safely at OpenAI* — https://openai.com/index/running-codex-safely/

## Agent frameworks / context

- OpenHands Software Agent SDK architecture — https://docs.openhands.dev/sdk/arch/overview
- OpenHands Agent architecture — https://docs.openhands.dev/sdk/arch/agent
- OpenHands Events — https://docs.openhands.dev/sdk/arch/events
- OpenHands Conversation — https://docs.openhands.dev/sdk/arch/conversation
- Aider repository map — https://aider.chat/docs/repomap.html
- Aider edit formats — https://aider.chat/docs/more/edit-formats.html
- Aider prompt caching — https://aider.chat/docs/usage/caching.html
- Anthropic, *Building Effective Agents* — https://www.anthropic.com/engineering/building-effective-agents

## Agentic reasoning / meta-cognition

- Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning* — https://arxiv.org/abs/2303.11366
- Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback* — https://arxiv.org/abs/2303.17651
- Yao et al., *Tree of Thoughts: Deliberate Problem Solving with Large Language Models* — https://arxiv.org/abs/2305.10601
- Wang et al., *VOYAGER: An Open-Ended Embodied Agent* — https://openreview.net/forum?id=ehfRiF0R3a
- Ma et al., *Eureka: Human-Level Reward Design via Coding Large Language Models* — https://arxiv.org/abs/2310.12931

## Automated agent design / evolution

- Hu, Lu, Clune, *Automated Design of Agentic Systems* — https://arxiv.org/abs/2408.08435
- Zhang et al., *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents* — https://arxiv.org/abs/2505.22954
- Google DeepMind / Google Cloud, AlphaEvolve overview — https://docs.cloud.google.com/gemini/enterprise/docs/alphaevolve/developer-guide/overview
- Google Cloud, AlphaEvolve GA — https://cloud.google.com/blog/products/ai-machine-learning/alphaevolve-is-available-for-everyone

## Harness-native training

- Du et al., *LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents* — https://arxiv.org/abs/2608.17393
- He et al., *Agent Lightning v1.0: Towards Harnessed Agentic RL* — https://arxiv.org/abs/2608.17528
- Luo et al., *Agent Lightning: Train ANY AI Agents with Reinforcement Learning* — https://arxiv.org/abs/2508.03680

---

# Fontes internas do AETHER/Vanguard usadas nesta aplicação

- `SPEC.md`
- `0069-runtime-convergence-python-first-packages-canonical.md`
- `0070-recursive-substrate-agent-spawn-swarm-as-policy.md`
- `0071-authority-state-ledger-identity-trinity.md`
- `0072-plugin-boundary-wire-first-evaluator-exterior.md`
- `0073-v060-lock-vs-defer.md`
- `0074-gamma-lock-amendments-proof-budget-writer-identity.md`
- `0075-director-review-v060-approved-wave0-authorized.md`
- `0076-foundation-execution-decisions-canonical-artifacts.md`
- `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`
- `000_CANONICAL_EXECUTION_PATH.md`
- `wave1_trust_spine.md`
- `wave2_convergence.md`
- `wave3_extensibility.md`
- `wave4_foundation_e2e.md`
- `AETHER_VANGUARD_INDEPENDENT_ENGINEERING_REVIEW_2026-08-20.md`
- `harness_agentic_coding_builder_research_and_framework.md`

---

# Apêndice A — Princípios operacionais

1. **Mechanism below; intelligence above.**
2. **Authority is never inferred from model confidence.**
3. **No hidden composition mutation.**
4. **No self-signed success.**
5. **No new engine without failed composition evidence.**
6. **No optimization without identity.**
7. **No learning without trajectory completeness.**
8. **No promotion without independent evaluation.**
9. **No concurrency without cancellation/resource proofs.**
10. **No distribution before a measured bottleneck.**
11. **No memory persistence without consolidation/invalidation policy.**
12. **No multi-agent without measured coordination benefit.**
13. **No “generality” claim without a second-domain falsifier.**
14. **No SOTA claim from architecture alone; prove through controlled experiments.**

---

# Apêndice B — Perguntas que o projeto deve ser capaz de responder depois do Foundation MVP

### Composição

- Quais inputs determinam exatamente `D_H`?
- Consigo reproduzir a mesma composição byte-identicamente?
- Consigo trocar controller sem tocar no trusted substrate?

### Execução

- Qual `D_R` produziu este artifact?
- Qual modelo e route foram realmente usados?
- Qual environment executou cada effect?
- Qual Principal possuía qual authority?

### Evidência

- Quem emitiu o verdict?
- O verdict está bound ao subject certo?
- O agente poderia ter lido/modificado o oracle?
- Consigo reconstruir o terminal state a partir do durable record?

### Generalidade

- Um Tree Search controller cabe sem nova engine?
- Um research pack cabe sem `repo_path` no core?
- Um deterministic solver cabe sem fingir ser “LLM turn”?
- Um child pode usar um harness heterogêneo com authority atenuada?

### Evolução

- Uma mudança cria novo `D_H`?
- O experimento que a justificou possui `D_X`?
- Há holdout?
- Há rollback?
- O mesmo sistema que propôs a mudança pode promovê-la sozinho? A resposta deve ser **não**.

---

# Apêndice C — North Star

A forma final desejada não é “um agente cada vez maior”.

É:

```text
small trusted substrate
        +
composable cognitive/control strategies
        +
versioned harness compositions
        +
domain packs
        +
scientific experiment plane
        +
governed evolutionary search
```

O substrate estabiliza.

O espaço de composição cresce.

A capacidade ativa é selecionada.

A evidência acumula.

A evolução acontece acima da linha de confiança.

Essa assimetria é a propriedade arquitetural que permite ao AETHER crescer por várias gerações sem transformar o core em uma coleção de exceções históricas.

# Harness Agentic Coding Builder
## Pesquisa de Estado da Arte e Aplicação Arquitetural para CLIs Autônomas de Engenharia de Software

**Data de referência:** 20 de agosto de 2026  
**Tipo de documento:** Relatório técnico de pesquisa e especificação arquitetural preliminar  
**Escopo:** Agentic Coding Harnesses, autonomous task solvers, coding CLIs, context engineering, memória, tool use, segurança, verificação, observabilidade, benchmarking e aplicação em um framework abstrato de construção de agentes.

---

## Resumo executivo

A pesquisa indica uma mudança importante na engenharia de sistemas agentic: **o modelo de linguagem deixou de ser a unidade suficiente de análise**. Em tarefas autônomas de software, o desempenho observado depende fortemente do *harness* que envolve o modelo — isto é, do sistema responsável por montar contexto, persistir estado, selecionar ferramentas, controlar permissões, executar ações, interpretar observações, delegar trabalho, compactar histórico e verificar resultados.

A tese central deste relatório é:

> **Modelo é capacidade cognitiva; agente é uma política iterativa de decisão; harness é o sistema operacional que transforma essa política em comportamento autônomo verificável.**

Os resultados recentes de Terminal-Bench reforçam empiricamente que o harness é uma variável independente relevante. No Terminal-Bench 2.0, utilizando o mesmo modelo GPT-5.3-Codex, diferentes agentes/harnesses apresentam resultados significativamente distintos: SageAgent 78,4%, Droid 77,3%, CodeBrain-1.5 75,8%, Simple Codex 75,1% e Terminus 2 64,7%. A diferença entre 78,4% e 64,7% ocorre sem troca do modelo-base, mostrando que orchestration, context management, tool execution e recovery possuem impacto material.

No Terminal-Bench 2.1 verificado, Claude Code com Fable 5 alcança 83,8% ± 1,2%, Codex com GPT-5.5 alcança 83,1% ± 1,1%, enquanto Terminus 2 com Fable 5 alcança 80,4% ± 1,2%. O custo reportado também varia substancialmente, reforçando que qualidade, custo e latência precisam ser tratados como objetivos distintos de otimização.

Outro resultado importante é o trabalho **LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents**, publicado em 18 de agosto de 2026. O estudo argumenta que treinar modelos fora do harness real cria *train–inference mismatch*. Ao preservar o controle nativo de harnesses como OpenHands SDK, Claude Code e OpenCode durante reinforcement learning, os autores reportam melhora de Qwen3.5-35B-A3B de 64,0% para 70,4% no OpenHands SDK, 62,4% para 68,2% no Claude Code e 57,2% para 66,6% no OpenCode em SWE-bench Verified.

A implicação para nosso framework é direta: **o Harness Builder não deve ser um wrapper de modelo com tools**. Ele deve ser um runtime modular capaz de compor:

- modelos;
- agentes;
- contexto;
- retrieval;
- memória;
- skills;
- tools;
- políticas;
- sandbox;
- verificação;
- observabilidade;
- avaliação;
- schedulers e estratégias multi-agent.

O segundo grande resultado desta pesquisa é que **context engineering deve ser tratado como sistema de seleção e compressão, não como simples vector RAG**. Em código, mecanismos determinísticos e estruturais — paths, símbolos, AST, call graphs, referências, dependências e busca lexical — devem preceder retrieval semântico e exploração agentic sempre que possível.

O terceiro resultado é que **multi-agent não deve ser o modo padrão**. Subagentes são mais valiosos quando introduzem isolamento de contexto, paralelismo verdadeiro, especialização ou verificação independente. Caso contrário, podem apenas multiplicar tokens, latência e superfície de falha.

O quarto resultado é que **segurança e conclusão não podem depender da autoconfiança do LLM**. Ações precisam atravessar uma camada determinística de schema, policy, risk, approval e sandbox. Da mesma forma, “done” deve significar que um contrato de aceitação foi satisfeito por evidência externa — testes, compilação, análise estática, validação semântica ou outro verificador apropriado.

O framework proposto neste documento, portanto, adota como núcleo:

1. **runtime orientado a eventos**;
2. **context engine hierárquico e multi-estratégia**;
3. **agentes isolados que trocam artefatos tipados**;
4. **tool runtime com capability contracts**;
5. **policy plane determinístico**;
6. **verification graph**;
7. **memória em múltiplos horizontes**;
8. **model-aware adapters**;
9. **scheduler adaptativo e cost-aware**;
10. **telemetria de trajetória para avaliação e aprendizado futuro**.

---

# CAPÍTULO I — PESQUISA DETALHADA: ESTADO DA ARTE EM AGENTIC CODING HARNESSES

## 1. Definições fundamentais

### 1.1 Modelo de linguagem

Um Large Language Model é o componente probabilístico que recebe uma sequência de contexto e produz uma continuação. Em sistemas modernos, essa continuação pode representar:

- linguagem natural;
- uma estrutura JSON;
- uma chamada de ferramenta;
- um patch;
- um plano;
- uma classificação;
- uma sequência de ações.

O modelo, isoladamente, não possui necessariamente estado persistente entre sessões, acesso direto ao filesystem, ferramentas, política de segurança, capacidade de verificar consequências, memória de longo prazo ou orchestration multi-agent. Por isso, **LLM e agente são categorias diferentes**.

## 2. O que caracteriza um agente

Um agente existe quando o modelo é colocado em um ciclo onde sua saída pode alterar o ambiente e gerar novas observações.

```text
objetivo
  ↓
observar estado
  ↓
decidir ação
  ↓
executar
  ↓
observar consequência
  ↓
repetir ou finalizar
```

Esse loop é uma extensão prática do paradigma ReAct — *Reasoning and Acting* — no qual raciocínio e ação são intercalados.

Em um coding agent, exemplos de ações incluem buscar símbolos, ler arquivos, editar, executar shell, rodar testes, navegar documentação, consultar APIs, delegar a um subagente, solicitar aprovação e finalizar.

A diferença fundamental em relação a um chatbot é que **o agente fecha um ciclo causal com o ambiente**.

## 3. O que é um harness

O harness é a infraestrutura que envolve o modelo e implementa as regras operacionais do agente.

Ele normalmente contém:

- prompt/system instruction assembly;
- gerenciamento do histórico;
- context window accounting;
- retrieval;
- tool registry;
- tool execution;
- parsing de structured output;
- approval e permissions;
- sandbox;
- loops de retry;
- delegação;
- compaction;
- memória;
- logging;
- métricas;
- verification;
- stopping criteria.

Uma forma útil de raciocinar é:

> **capacidade observada ≈ capacidade do modelo × qualidade do harness × qualidade do ambiente × qualidade da verificação**

A expressão não pretende ser uma equação científica formal. Ela enfatiza que performance final é resultado de interação entre componentes.

## 4. Evidência empírica de que o harness importa

### 4.1 Terminal-Bench

Terminal-Bench mede desempenho em tarefas realistas executadas em ambientes de terminal.

No Terminal-Bench 2.0, GPT-5.3-Codex aparece em combinações diferentes:

| Harness / agente | Modelo | Accuracy |
|---|---|---:|
| SageAgent | GPT-5.3-Codex | 78,4% ± 2,2 |
| Droid | GPT-5.3-Codex | 77,3% ± 2,2 |
| CodeBrain-1.5 | GPT-5.3-Codex | 75,8% ± 2,0 |
| Simple Codex | GPT-5.3-Codex | 75,1% ± 2,4 |
| Terminus 2 | GPT-5.3-Codex | 64,7% ± 2,7 |

A amplitude é de aproximadamente 13,7 pontos percentuais entre SageAgent e Terminus 2.

Isso não prova que todo ganho seja exclusivamente de harness — configurações, prompts e detalhes operacionais podem variar —, mas mostra com força que **modelo sozinho não prediz a performance do sistema**.

No Terminal-Bench 2.1 verificado:

| Harness / agente | Modelo | Accuracy | Custo reportado |
|---|---|---:|---:|
| Claude Code | Fable 5 | 83,8% ± 1,2 | US$ 552,67 |
| Codex | GPT-5.5 | 83,1% ± 1,1 | US$ 2.059,19 |
| Terminus 2 | Fable 5 | 80,4% ± 1,2 | US$ 438,64 |

Esse quadro introduz outra dimensão importante: **Pareto entre qualidade, custo e latência**.

### Implicação

Nosso Harness Builder precisa medir o harness de forma independente.

Métricas mínimas:

- taxa de resolução;
- custo por tarefa;
- custo por tarefa resolvida;
- latência;
- número de tool calls;
- número de tool failures;
- retries;
- quantidade de contexto lido;
- contexto efetivamente utilizado;
- cobertura de verificação;
- número de delegações;
- número de compactions.

## 5. Claude Code

### 5.1 Arquitetura conceitual

Claude Code representa uma das arquiteturas de produção mais maduras em termos de subagentes, context isolation, memória persistente, hooks, skills, MCP, permissões e agent teams.

A documentação oficial descreve subagentes como assistentes especializados executados em **janelas de contexto próprias**, com system prompt específico, ferramentas específicas, permissões independentes, modelo configurável e escopo de memória opcional.

O resultado do subagente retorna ao contexto principal, evitando transferir toda a trajetória exploratória.

### 5.2 Context isolation

Considere uma investigação de bug com dezenas de buscas, arquivos e hipóteses. Manter tudo no contexto principal aumenta custo, distração e risco de contradições.

Com um subagente, a exploração acontece separadamente. O agente principal recebe somente arquivos relevantes, símbolos, evidências, conclusão e incertezas.

Assim, **subagente funciona também como mecanismo de compressão semântica**.

### 5.3 Especialização

Claude Code inclui padrões como Explore, Plan, general-purpose e subagentes customizados.

Um agente pode ter ferramentas read-only, write access, modelo mais barato, esforço diferente, skills específicas e hooks específicos.

Isso permite model routing por função.

### 5.4 Agent teams

Agent teams executam sessões independentes que podem compartilhar tarefas, comunicar-se e coordenar trabalho.

A própria documentação destaca trade-offs: maior custo de tokens, complexidade de coordenação e limitações experimentais.

Isso apoia a conclusão de que **multi-agent deve ser seletivo**.

### 5.5 Memória

Claude Code separa dois mecanismos importantes.

#### CLAUDE.md

Memória/instrução explícita escrita por humanos: standards, workflows, arquitetura, regras e convenções.

#### Auto memory

Memória criada pelo agente: comandos, debugging insights, padrões, preferências e observações úteis para sessões futuras.

A documentação indica que `MEMORY.md` funciona como índice conciso. As primeiras 200 linhas ou 25 KB são carregadas no início da sessão; arquivos temáticos detalhados podem ser lidos sob demanda.

O padrão é conceitualmente importante:

> **índice pequeno sempre disponível + detalhes recuperados sob demanda**

### 5.6 Hooks

Hooks permitem lógica determinística em eventos do ciclo de vida, como antes e depois de tool use, stop, inicialização e prompt submission.

A principal lição é:

> **comportamentos críticos podem e devem ser implementados fora do prompt.**

### 5.7 SWOT — Claude Code

**Strengths**

- isolamento de contexto maduro;
- subagentes especializados;
- model routing;
- skills;
- memory hierárquica;
- hooks;
- permissões e integração de ferramentas.

**Weaknesses**

- implementação central menos auditável que projetos totalmente open source;
- multi-agent amplia custo;
- memória/instruções continuam sendo contexto probabilístico, não enforcement;
- resumos de subagente são necessariamente lossy.

**Opportunities**

- copiar o padrão de context isolation;
- usar subagentes principalmente para pesquisa e verificação;
- separar human policy de learned memory;
- usar hooks como policy/verifier interfaces.

**Threats**

- coordenação excessiva;
- prompt injection via ferramentas;
- dependência de heurísticas proprietárias;
- expansão da trusted computing base por plugins/MCP.

## 6. OpenAI Codex CLI

### 6.1 Por que é relevante

Codex CLI é importante para pesquisa porque oferece uma implementação de produção amplamente inspecionável, com arquitetura modular em Rust.

Elementos observáveis incluem sessions/threads, message history, sandbox, approvals, hooks, MCP, file search, memories, compaction e model management.

### 6.2 Instruções hierárquicas

O ecossistema Codex utiliza `AGENTS.md` como forma de instrução contextual do repositório.

O padrão importante é conceitual:

```text
organização
  ↓
repositório
  ↓
subárvore
  ↓
tarefa
```

Isto permite especializar contexto sem criar um system prompt global monolítico.

### 6.3 Context checkpoint compaction

O prompt de compaction público do Codex pede que o checkpoint preserve progresso, decisões, contexto crítico, restrições, próximos passos e dados necessários para continuação.

Portanto, compaction é melhor entendida como:

> **transferência de estado operacional para uma futura instância de raciocínio**

### 6.4 Memória em duas fases

A documentação do pipeline de memories descreve um processo de startup para sessões elegíveis.

O pipeline encontra rollouts recentes, extrai memória estruturada por rollout, consolida mudanças e mantém memória reutilizável.

```text
trajetória
  ↓
extração episódica
  ↓
delta de conhecimento
  ↓
consolidação
  ↓
memória reutilizável
```

Esse é um dos melhores padrões encontrados na pesquisa.

### 6.5 MCP bidirecional

Codex funciona como MCP client e MCP server experimental.

A lição para nosso framework é que a arquitetura deve permitir **composição hierárquica de agentes**.

### 6.6 Sandbox e approval policy

A configuração de Codex expõe separadamente sandbox mode e approval policy.

Esse desacoplamento é importante: permissão e execução não devem ser confundidas.

### 6.7 SWOT — Codex

**Strengths**

- arquitetura inspecionável;
- isolamento entre sandbox e approval;
- threads persistentes;
- memória estruturada;
- compaction explícita;
- MCP cliente/servidor;
- grande modularidade.

**Weaknesses**

- complexidade crescente;
- composição entre hooks, plugins, MCP e sandbox pode introduzir interações difíceis;
- state persistence amplia superfície de bugs.

**Opportunities**

- event/thread log como base do runtime;
- memória em duas fases;
- compaction como checkpoint;
- agent-as-tool;
- policy/sandbox independentes.

**Threats**

- múltiplos canais de execução podem introduzir inconsistência de policy;
- crescimento da trusted computing base;
- regressões emergentes em sistemas altamente configuráveis.

## 7. OpenHands Software Agent SDK

### 7.1 Arquitetura stateless e event-driven

OpenHands descreve o Agent como um executor de loop de raciocínio-ação **stateless e event-driven**.

```text
Event History
  ↓
Condenser
  ↓
LLM
  ↓
Security Analyzer
  ↓
Tool Executor
  ↓
Observation Event
  ↓
Event History
```

Essa é provavelmente a melhor referência para o core do nosso Harness Runtime.

### 7.2 Stateless agent

Em vez de manter estado interno obscuro, cada `step()` lê eventos, constrói contexto, consulta o modelo, produz eventos, executa ações e registra observações.

Consequências:

- replay;
- resume;
- debugging;
- auditoria;
- branch/fork;
- treinamento sobre trajetória.

### 7.3 Condensers

OpenHands trata condensação de contexto como componente substituível.

Isso sugere que compaction deve ser uma interface capaz de suportar truncation, summary, hierarchical summary, checkpoint, task-aware compression e model-aware compression.

### 7.4 Security Analyzer

OpenHands separa análise de risco e confirmação. Esse é um bom boundary arquitetural, embora qualquer segurança baseada exclusivamente em classificação do próprio ator continue sujeita a circularidade.

### 7.5 Composability

A documentação do V1 enfatiza separação entre SDK, tools, workspace e agent server.

Isso é relevante para um framework que possa servir CLI, servidor, avaliação, IDE e automações.

### 7.6 SWOT — OpenHands

**Strengths**

- design explicitamente modular;
- loop event-driven;
- stateless agent;
- condenser plugável;
- security interface;
- excelente base para experimentação.

**Weaknesses**

- generalidade pode introduzir mais abstração do que CLIs simples precisam;
- security analyzer depende da qualidade da classificação disponível;
- retrieval de código não é automaticamente resolvido pelo runtime.

**Opportunities**

- usar o mesmo runtime para pesquisa e produção;
- realizar ablations trocando apenas componentes;
- integrar telemetry nativa;
- usar event trajectories para aprendizado.

**Threats**

- abstrações muito genéricas podem perder performance frente a harnesses altamente especializados;
- flexibilidade excessiva cria configuração difícil de validar.

## 8. Aider

### 8.1 Por que continua relevante

Aider é menos focado em grandes orquestrações multi-agent, mas contém alguns dos padrões mais limpos para repository mapping, prompt caching, edit protocols e separação architect/editor.

### 8.2 Repository map

Aider utiliza uma representação compacta da estrutura do repositório, priorizando definições, símbolos, relações, referências e código estruturalmente central.

O principal aprendizado é:

> **código não deve ser tratado como coleção arbitrária de chunks textuais.**

Código possui estrutura formal.

### 8.3 Structural retrieval

Podemos distinguir:

1. path retrieval;
2. symbol retrieval;
3. AST;
4. dependency graph;
5. reference graph;
6. lexical retrieval;
7. semantic retrieval.

Essa ordem é útil porque os primeiros mecanismos são baratos, determinísticos e auditáveis.

### 8.4 Architect/editor

Aider popularizou uma separação prática entre modelo que raciocina sobre solução e modelo que converte solução em edição concreta.

### 8.5 Model-specific edit formats

Aider ajusta mecanismos de edição conforme o modelo.

Isso leva a uma tese importante:

> **uma interface de API uniforme não implica que modelos devam receber o mesmo protocolo.**

O harness deve ser model-aware.

### 8.6 Prompt caching

Aider expõe configurações explícitas para prompt caching e keepalive. O aprendizado é que stable prefix design precisa ser considerado durante prompt assembly.

### 8.7 SWOT — Aider

**Strengths**

- retrieval estrutural;
- simplicidade;
- caching explícito;
- model adaptation;
- separação architect/editor.

**Weaknesses**

- menor foco em autonomia ampla;
- memória episódica menos sofisticada;
- menos orchestration nativa.

**Opportunities**

- incorporar repo map ao Context Engine;
- model-specific editors;
- prefix-cache-aware prompt assembly.

**Threats**

- modelos de contextos muito grandes podem reduzir parte do benefício;
- search nativo de provedores pode substituir algumas estratégias locais.

## 9. Context engineering

### 9.1 Contexto é recurso escasso

Mesmo com context windows grandes, há quatro custos: tokens, latência, dinheiro e degradação de atenção.

A pergunta correta não é “quanto contexto cabe?”, mas:

> **“Qual contexto aumenta a probabilidade da próxima ação correta?”**

### 9.2 Pipeline recomendado

```text
1. exact/path
2. symbol
3. AST/reference/dependency graph
4. lexical search
5. semantic retrieval
6. agentic exploration
7. external search
```

Nem toda tarefa precisa atravessar todos os níveis.

### 9.3 Recall versus precision

ContextBench fornece evidência de que coding agents tendem a priorizar recall em detrimento de precision.

O benchmark contém 1.136 tarefas, 66 repositórios e 8 linguagens, com gold contexts anotados por humanos.

O estudo relata ganhos marginais de retrieval com scaffolding mais sofisticado, tendência dos LLMs a buscar contexto em excesso e diferença entre contexto explorado e contexto efetivamente utilizado.

### Implicação

**Retrieval excessivo é um problema mensurável.**

Nosso framework deve medir context recall, context precision, bytes/tokens lidos, arquivos explorados, arquivos utilizados e distância entre contexto encontrado e aplicado.

## 10. Parsing e structured output

Agentes dependem de tradução confiável entre intenção e execução.

### 10.1 Tool calling nativo

Modelo produz chamadas estruturadas validadas por schema.

Vantagens: parsing robusto, validação e menor ambiguidade.

Desvantagens: comportamento varia por modelo e esquemas grandes consomem contexto.

### 10.2 Structured text

JSON, XML, tags ou outros contratos podem ser úteis quando tool calling nativo é insuficiente.

### 10.3 Protocolos específicos de edição

Diffs, patches, full-file rewrite e search/replace.

Conclusão: **o protocolo de saída deve ser escolhido por perfil de modelo e classe de tarefa**.

## 11. Prompt engineering moderno

Prompt engineering para agentes deve ser visto menos como “escrever um prompt perfeito” e mais como **distribuir instruções ao longo do sistema**.

Camadas possíveis:

- system-level invariants;
- developer policies;
- repository instructions;
- path-scoped instructions;
- skill instructions;
- agent-role instructions;
- task prompt;
- verification prompt.

A tendência é sair de um prompt monolítico para **prompt composition hierárquico e lazy-loaded**.

## 12. Skills e progressive disclosure

Uma skill representa uma capability modular com descrição, activation hints, instruções, ferramentas, referências, scripts, schemas e policies.

No momento de discovery, o agente precisa conhecer apenas nome, objetivo e condições de uso. O conteúdo completo entra no contexto somente quando a skill é ativada.

Princípio:

> **discovery context ≠ execution context**

## 13. Memória

### 13.1 Working memory

Estado da tarefa atual: objetivo, plano, hipóteses, arquivos ativos, ações pendentes e resultados recentes.

### 13.2 Checkpoint memory

Estado comprimido utilizado para compaction, resume e handoff. Deve preservar progress, decisions, constraints, pending e critical data.

### 13.3 Episodic memory

Representação de experiências anteriores: problema, tentativas, erros, resultado, evidência e lição.

### 13.4 Semantic/procedural memory

Conhecimento reutilizável: arquitetura, conventions, build procedures, test strategies e debugging patterns.

### 13.5 Consolidation

```text
trajectory
  ↓
episode extraction
  ↓
salience filtering
  ↓
conflict detection
  ↓
consolidation
  ↓
durable memory
```

O problema principal de memória não é armazenamento, mas seleção, atualização, conflito, validade e retrieval.

## 14. Caching

Caching deve existir em múltiplas camadas.

### 14.1 Provider prompt cache

Prefixos estáveis: system prompt, políticas e instruções de projeto.

### 14.2 Structural cache

AST, symbol index, reference graph e dependency graph, chaveados por hash/versão.

### 14.3 Retrieval cache

`repo_version + query → candidates`

### 14.4 Tool-result cache

Para operações read-only, determinísticas e com dependências conhecidas.

### 14.5 Sandbox cache

Imagens, environments e dependency layers.

### 14.6 Memory consolidation cache

Evita reprocessar trajetórias imutáveis.

## 15. Multi-agent patterns

### 15.1 Planner–worker

Planner cria estratégia; worker executa.

### 15.2 Researcher–editor

Researcher explora sem contaminar contexto de edição.

### 15.3 Planner–editor–verifier

Separa intenção, mutação e evidência.

### 15.4 Parallel workers

Útil quando subtarefas são independentes.

### 15.5 Debate

Dois agentes desafiam hipóteses. Pode ser útil em problemas ambíguos, mas é caro e não é universalmente superior.

### 15.6 Hierarchical delegation

Agentes podem spawnar outros agentes, exigindo budgets, depth limits, attribution, cancellation e observabilidade.

### Regra

> **Delegation must pay rent.**

Um novo agente deve existir somente quando justificado por paralelismo, especialização, isolamento ou independência de verificação.

## 16. Reflexion e reflection loops

Reflection introduz revisão explícita de uma tentativa.

```text
attempt
  ↓
external feedback
  ↓
failure analysis
  ↓
revised hypothesis
  ↓
new attempt
```

O ponto crítico é **external feedback**. Reflection sem sinais externos pode apenas gerar uma segunda narrativa plausível.

Sinais preferidos: compiler, tests, static analyzer, benchmark judge e external verifier.

## 17. Plan-and-Execute

Separar planejamento e execução melhora coerência em tarefas longas, mas planos rígidos falham quando novas informações emergem.

O padrão preferível é adaptativo:

```text
plan
→ act
→ observe
→ update plan
→ act
```

O plano deve ser um **estado revisável**, não uma verdade fixa.

## 18. Tree-of-Thoughts e search over trajectories

Uma tarefa agentic pode ser tratada como busca em espaço de trajetórias. Cada estado permite ações como search, read, edit, test, delegate, rollback e finish.

Tree-of-Thoughts, beam-like search, debate e self-consistency são formas de explorar múltiplos caminhos.

O problema é econômico: maior branching aumenta cobertura, mas também custo. O scheduler precisa controlar branching factor, budget, pruning e early stopping.

## 19. Segurança: stochastic plane versus deterministic plane

Uma arquitetura robusta separa dois planos.

### Probabilistic plane

Reasoning, planning, hypothesis e tool proposal.

### Deterministic plane

Validation, permissions, quotas, capability enforcement, sandbox, secret isolation e network rules.

```text
LLM
 ↓
Action Proposal
 ↓
Schema Validation
 ↓
Policy
 ↓
Risk
 ↓
Approval
 ↓
Sandbox
 ↓
Execution
```

Princípio:

> **o modelo pode recomendar uma ação; não deve ser a autoridade final que concede a si próprio a permissão de executá-la.**

## 20. Verification

### 20.1 Por que é central

LLMs podem produzir uma solução plausível e declarar sucesso sem evidência suficiente.

> **done deve ser uma propriedade verificável, não uma afirmação do agente.**

### 20.2 Verification graph

```text
change
 ↓
syntax
 ↓
format
 ↓
typecheck
 ↓
unit tests
 ↓
integration tests
 ↓
security
 ↓
acceptance
```

Nem todo nó é obrigatório para toda tarefa.

### 20.3 Acceptance contract

Cada tarefa deveria possuir critérios como compilação, testes específicos, ausência de regressão, API behavior, performance threshold e security requirement.

O runtime só conclui quando critérios requeridos estão satisfeitos.

## 21. Event-driven runtime

Uma das conclusões mais fortes da pesquisa é que a trajetória deve ser modelada explicitamente como eventos.

Tipos conceituais:

```text
UserMessage
ModelRequested
ModelResponded
ToolProposed
ToolApproved
ToolRejected
ToolStarted
ToolCompleted
ToolFailed
AgentSpawned
AgentCompleted
ContextCompacted
VerificationCompleted
MemoryWritten
TaskCompleted
```

O estado atual passa a ser:

> **state = projection(event log)**

Benefícios: replay, audit, resume, branching, debugging, analytics e training datasets.

## 22. Model-aware harness

Modelos diferentes apresentam perfis diferentes de context window, reasoning, tool calling, edit reliability, structured output, parallel tool use, prompt caching, custo e latência.

Nosso sistema não deve assumir que “OpenAI-compatible API” significa comportamento equivalente.

Precisamos de `ModelProfile` e `ModelAdapter`.

## 23. Harness-native reinforcement learning — LEGO-RL

### 23.1 Problema

Treinar uma policy fora do harness e executar dentro dele cria mismatch. O harness pode compactar, reserializar, transformar tool calls, recuperar falhas, truncar contexto e introduzir observações.

### 23.2 Proposta

LEGO-RL preserva o fluxo nativo e captura streams de geração com proxy in-process. Também adiciona sandbox orchestration, image caching, reward-hacking defenses e trajectory observability.

### 23.3 Resultados reportados

Qwen3.5-35B-A3B em SWE-bench Verified:

| Harness | Baseline | LEGO-RL |
|---|---:|---:|
| OpenHands SDK | 64,0% | 70,4% |
| Claude Code | 62,4% | 68,2% |
| OpenCode | 57,2% | 66,6% |

Correlação rollout-training reportada: > 0,99.

### 23.4 Implicação

No futuro, não basta model optimization. Precisaremos de **model–harness co-optimization**.

## 24. Síntese comparativa

| Sistema | Principal contribuição reutilizável |
|---|---|
| Claude Code | context isolation, subagents, hooks, skills, memory hierarchy |
| Codex | threads, checkpoint compaction, hierarchical instructions, memory pipeline, sandbox/policy |
| OpenHands | stateless event-driven agent core, condensers, composability |
| Aider | structural retrieval, model-specific editing, prompt caching |
| LEGO-RL | harness-native training |
| ContextBench | process metrics para retrieval |
| Terminal-Bench | benchmark operacional de harness + model |

## 25. Conclusões do Capítulo I

### 25.1 O harness é parte da inteligência do sistema

Não apenas infraestrutura.

### 25.2 Context precision é tão importante quanto context capacity

Mais tokens não substituem seleção.

### 25.3 Estrutura de código deve ser explorada explicitamente

AST/symbol graphs devem preceder embedding-only RAG.

### 25.4 Subagentes são primariamente uma ferramenta de isolamento

Paralelismo é apenas um dos benefícios.

### 25.5 Memória precisa de consolidação

Persistência bruta não é suficiente.

### 25.6 Segurança deve existir fora do LLM

Política e sandbox são enforcement.

### 25.7 Verification deve comandar stopping

O agente não decide sozinho que terminou.

### 25.8 O runtime deve registrar trajetórias

Eventos são base para observabilidade, benchmarks e aprendizado.

---

# CAPÍTULO II — APLICAÇÃO DA PESQUISA: FRAMEWORK HARNESS BUILDER PARA AGENTIC CODING CLIs

## 26. Objetivo do framework

O objetivo não é criar mais um coding agent específico.

O objetivo é criar uma **abstração geral para construir harnesses agentic**.

Um mesmo runtime deve poder sustentar coding agent, research agent, debugging agent, DevOps agent, security-review agent, autonomous project agent e scientific agent.

A diferença entre esses sistemas deve ser majoritariamente configuracional e componível.

## 27. Princípio arquitetural central

Não modelar o sistema como:

```text
Agent
 ├─ model
 ├─ tools
 └─ prompt
```

Modelar como:

```text
Harness
 ├─ Runtime
 ├─ Scheduler
 ├─ Model Layer
 ├─ Agent Layer
 ├─ Context Engine
 ├─ Retrieval
 ├─ Memory
 ├─ Skills
 ├─ Tool Runtime
 ├─ Policy Engine
 ├─ Sandbox
 ├─ Verification
 ├─ Observability
 └─ Evaluation
```

O Agent é uma entidade dentro do Harness.

## 28. Arquitetura de alto nível

```text
                    USER TASK
                        │
                        ▼
              Task Classification
                        │
                        ▼
                Harness Scheduler
                        │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
 Research Agent      Planner          Worker/Editor
      └─────────────────┼─────────────────┘
                        ▼
                 Typed Artifacts
                        ▼
                  Context Engine
     ┌──────────────────┼──────────────────┐
     ▼                  ▼                  ▼
 Instructions       Retrieval           Memory
                        │
                        ▼
                   Agent Loop
                        │
                        ▼
                   Tool Intent
                        │
                        ▼
              Deterministic Policy
                        │
                        ▼
                     Sandbox
                        │
                        ▼
                    Execution
                        │
                        ▼
                   Verification
                        │
                        ▼
                    Event Store
              ┌─────────┴─────────┐
              ▼                   ▼
          Checkpoints          Memory
```

## 29. Harness Runtime

### 29.1 Responsabilidades

O runtime deve receber tasks, criar sessions, manter event log, executar steps, coordenar agentes, controlar budgets, processar tool lifecycle, calcular stopping e emitir telemetry.

### 29.2 Event sourcing

Categorias recomendadas:

**Conversation events**

- `UserMessage`
- `AgentMessage`
- `SystemInstructionLoaded`

**Model events**

- `ModelRequestStarted`
- `ModelResponseReceived`
- `ModelError`

**Tool events**

- `ToolProposed`
- `ToolPolicyChecked`
- `ToolApproved`
- `ToolRejected`
- `ToolStarted`
- `ToolCompleted`
- `ToolFailed`

**Agent events**

- `AgentSpawned`
- `AgentDelegated`
- `AgentCompleted`
- `AgentCancelled`

**Context events**

- `ContextBuilt`
- `ContextCompacted`
- `MemoryRetrieved`

**Verification events**

- `VerificationStarted`
- `VerificationPassed`
- `VerificationFailed`

**Lifecycle events**

- `TaskStarted`
- `TaskPaused`
- `TaskResumed`
- `TaskCompleted`
- `TaskFailed`

## 30. Session e state projection

O estado de uma sessão não precisa ser armazenado apenas como objeto mutável. Pode ser reconstruído a partir dos eventos.

Projeções úteis:

- CurrentPlan;
- WorkingSet;
- PendingTools;
- AgentTree;
- BudgetUsage;
- VerificationStatus;
- MemoryCandidates.

Isso permite criar diferentes views do mesmo event log.

## 31. Scheduler

O Scheduler será um componente estratégico do framework.

Responsabilidades:

- decidir single versus multi-agent;
- selecionar modelo;
- alocar budgets;
- escolher strategy;
- controlar paralelismo;
- escalonar para modelos mais fortes;
- cancelar branches improdutivos.

### 31.1 Estratégias iniciais

**Direct:** uma única instância resolve.

**Research-Then-Act:** researcher explora; main agent executa.

**Plan-and-Execute:** planner cria plano revisável.

**Planner–Editor–Verifier:** para mudanças relevantes.

**Parallel Research:** vários pesquisadores independentes.

**Independent Verification:** outro agente verifica solução.

## 32. Task classifier

Antes de gastar recursos, classificar complexidade, domínio, risco, necessidade de escrita, necessidade de rede, necessidade de pesquisa, grau de paralelização e verificabilidade.

Exemplos:

- trivial → single agent;
- investigativa → researcher isolado;
- implementação ampla → planner + worker + verifier;
- alto risco → policy estrita + approval + independent verifier.

## 33. Agent abstraction

Um agente não deve possuir toda a infraestrutura.

Ele deveria declarar:

- role;
- model profile;
- tools;
- skills;
- context policy;
- memory scope;
- permission scope;
- output contract;
- budget;
- stopping policy.

Tipos possíveis:

- `OrchestratorAgent`
- `ResearchAgent`
- `PlanningAgent`
- `EditingAgent`
- `VerificationAgent`
- `ReviewAgent`

## 34. Typed artifacts

Agentes devem trocar informação estruturada.

### 34.1 ResearchArtifact

- relevant files;
- symbols;
- evidence;
- observations;
- hypotheses;
- uncertainty;
- recommended next actions.

### 34.2 PlanArtifact

- objective;
- steps;
- dependencies;
- risks;
- verification criteria.

### 34.3 ChangeArtifact

- changed files;
- semantic changes;
- assumptions;
- tests affected.

### 34.4 VerificationArtifact

- criterion;
- evidence;
- pass/fail;
- logs;
- residual risk.

Typed artifacts reduzem transcript pollution, ambiguity, token usage e coupling entre agentes.

## 35. Context Engine

### 35.1 Responsabilidades

O Context Engine decide o que o modelo vê.

Entradas:

- task;
- current state;
- agent role;
- model profile;
- repository version;
- memory;
- tool results.

Saída:

- ordenação de mensagens;
- instructions;
- relevant artifacts;
- code context;
- memory snippets;
- tool schemas.

### 35.2 Context budgets

Context budget deve ser particionado. Uma configuração inicial poderia reservar faixas para instructions, working code, retrieval, memory, event history e headroom. Os percentuais devem ser configuráveis, não universais.

## 36. Retrieval Engine

Arquitetura sugerida:

### Stage A — deterministic

- explicit paths;
- changed files;
- symbols;
- references.

### Stage B — structural

- AST;
- dependency graph;
- call graph.

### Stage C — lexical

- grep;
- BM25.

### Stage D — semantic

- embedding retrieval;
- reranking.

### Stage E — agentic

- research agent.

### Stage F — external

- docs;
- web;
- issue trackers.

A engine deve poder terminar cedo quando confiança suficiente é alcançada.

## 37. Repository Intelligence

O framework deve representar código como mais que texto.

Entidades:

- File;
- Module;
- Symbol;
- Class;
- Function;
- Type;
- Import;
- Reference;
- Dependency;
- Test;
- Build target.

Relações:

- defines;
- calls;
- imports;
- inherits;
- implements;
- tests;
- depends_on.

Com isso, retrieval pode usar graph expansion.

## 38. Index lifecycle

Índice deve ser incremental e chaveado por repository identity, commit/hash e file hash.

Ao editar:

1. detectar arquivos alterados;
2. invalidar nodes afetados;
3. reparse;
4. atualizar relações.

## 39. Memory Store

Interface conceitual:

```text
remember()
retrieve()
consolidate()
invalidate()
forget()
```

Stores separados por tipo:

- Working store;
- Checkpoint store;
- Episodic store;
- Semantic/procedural store.

## 40. Memory retrieval

A recuperação deve considerar semantic similarity, project scope, recency, success/failure, confidence e task type.

Memórias devem carregar metadados como source session, timestamp, evidence, validity e confidence.

## 41. Memory consolidation pipeline

```text
Raw Events
 ↓
Episode Extractor
 ↓
Salience Filter
 ↓
Conflict Detector
 ↓
Consolidator
 ↓
Durable Memory
```

Não consolidar detalhes triviais, fatos temporários ou hipóteses não verificadas.

Consolidar comandos recorrentes, arquitetura estável, resolução confirmada, failure patterns e decisões permanentes.

## 42. Skill system

Estrutura conceitual:

```text
SkillDescriptor
 ├─ id
 ├─ description
 ├─ activation
 └─ version
```

Quando ativada:

```text
Skill
 ├─ instructions
 ├─ tools
 ├─ references
 ├─ policies
 ├─ scripts
 └─ output schemas
```

Activation pode ser explicit, classifier, semantic matching ou agent decision.

## 43. Tool abstraction

Uma tool deve possuir metadata operacional:

- input schema;
- output schema;
- capabilities;
- side effects;
- risk;
- filesystem scope;
- network scope;
- secrets requirement;
- idempotency;
- determinism;
- cost;
- latency;
- cache policy;
- verification strategy.

Isso transforma tools em **capability contracts**.

## 44. Tool lifecycle

```text
Proposed
  ↓
Parsed
  ↓
Validated
  ↓
Policy Checked
  ↓
Risk Classified
  ↓
Approved/Rejected
  ↓
Executed
  ↓
Observed
  ↓
Verified
```

Cada estágio gera evento.

## 45. MCP adapter

MCP deve ser suportado, porém tratado como adapter.

```text
Harness Tool Interface
     ↑
 ┌───┼──────────────┐
 │   │              │
MCP Native Tool   Remote API
```

Assim, nosso domínio interno não depende integralmente de MCP.

## 46. Policy Engine

Policy deve trabalhar com regras determinísticas.

### Filesystem

- read;
- workspace-write;
- restricted paths;
- immutable paths.

### Network

- deny;
- allowlist;
- approval;
- unrestricted.

### Secrets

- unavailable;
- scoped;
- masked;
- approval required.

### Commands

- safe allowlist;
- risky;
- destructive deny.

## 47. Risk Engine

Classificar ações por propriedades objetivas:

- writes filesystem;
- deletes;
- changes permissions;
- executes network;
- installs dependencies;
- modifies git history;
- uses credentials;
- deploys.

O modelo pode contribuir com interpretação semântica, mas não deve ser a única fonte.

## 48. Sandbox

Sandboxes possíveis:

- process-level;
- filesystem;
- container;
- VM;
- remote workspace.

O framework deve permitir seleção por task risk.

## 49. Model layer

### 49.1 ModelProfile

Representa provider, model, context size, reasoning modes, tool support, structured output, parallel tools, prompt caching, edit preferences, latency e cost.

### 49.2 ModelAdapter

Responsável por message serialization, tool schema encoding, reasoning configuration, edit protocol, cache hints e usage telemetry.

## 50. Model routing

O scheduler pode escolher fast model para classification/search/summarization, strong reasoner para architecture e debugging complexo, editor para patches/refactor e verifier para independent review.

Objetivo:

> **não pagar capacidade máxima quando uma função mais barata é suficiente.**

## 51. Edit protocols

Suportar patch/diff, search-replace, full file, AST transformations e language-server actions.

Seleção por modelo, tamanho do arquivo, risco e linguagem.

## 52. Verification Engine

### 52.1 Verifier abstraction

Um verifier recebe task, change, environment e criterion e produz status, evidence, logs, confidence e residual risk.

### 52.2 Verification graph

```text
compile
 ├─ unit tests
 │   └─ integration
 └─ static analysis
     └─ security
```

Se compile falha, testes posteriores podem ser cancelados.

## 53. Acceptance contract

O task pode gerar ou receber critérios como endpoint behavior, teste específico, ausência de regressão, limite de latência e requisitos de segurança.

`TaskCompleted` só deve ocorrer quando required criteria forem satisfeitos.

## 54. Observability

Cada run deve produzir métricas.

### Model

- prompt tokens;
- output tokens;
- cache hit;
- latency;
- retries.

### Tools

- count;
- duration;
- failures;
- approval rate.

### Context

- tokens;
- files;
- retrieval candidates;
- precision/recall quando gold disponível.

### Agents

- spawns;
- depth;
- messages;
- artifacts.

### Verification

- criteria passed;
- failed;
- retries.

### Economics

- total cost;
- cost/resolved task.

## 55. Tracing

Cada Task deve possuir trace id, session id, agent id, parent agent id, tool span e model span.

Assim podemos visualizar árvore causal.

## 56. Replay

Replay modes:

- Full replay;
- Model replay;
- Tool replay;
- Offline evaluation.

Isso é extremamente valioso para pesquisa.

## 57. Evaluation framework

Precisamos de três níveis.

### Outcome evaluation

A tarefa foi resolvida?

### Process evaluation

Como foi resolvida?

### Economic evaluation

Quanto custou?

Benchmarks externos incluem SWE-bench, Terminal-Bench, HumanEval, AgentBench e GAIA.

Benchmarks internos devem incluir repo-specific tasks, regression tasks, security tasks e latency/cost tasks.

## 58. Harness ablation testing

Experimento inicial recomendado:

Mesmo modelo, task e environment; variar somente harness.

- A: Minimal ReAct.
- B: ReAct + structural retrieval.
- C: Planner + structural retrieval.
- D: Researcher + editor + verifier.

Medir success, tokens, latency, cost, retrieval precision e tool failures.

## 59. Context ablation

Comparar:

1. grep;
2. symbol index;
3. AST graph;
4. BM25;
5. embeddings;
6. graph + lexical;
7. graph + semantic reranking;
8. research agent.

Objetivo: identificar quando cada técnica compensa seu custo.

## 60. Memory ablation

Comparar sem memória, checkpoint, episodic, semantic e episodic + consolidation.

Métricas: repetição de erros, tempo de resolução, token cost e false memory rate.

## 61. Delegation ablation

Comparar single-agent, researcher, planner, verifier e full multi-agent.

O objetivo não é provar que multi-agent é melhor, mas encontrar **fronteiras onde delegação produz ROI positivo**.

## 62. DSL do Harness Builder

O usuário do framework deve poder descrever harnesses declarativamente.

```yaml
harness: coding-agent

models:
  primary: frontier
  researcher: fast
  verifier: independent

agents:
  main:
    role: orchestrator

  researcher:
    context: isolated
    permissions: read-only

  editor:
    permissions: workspace-write

  verifier:
    context: isolated

retrieval:
  pipeline:
    - exact
    - symbols
    - graph
    - lexical
    - semantic

memory:
  checkpoint: true
  episodic: true
  consolidation: true

policy:
  filesystem: workspace
  network: approval
  destructive: deny

verification:
  required:
    - tests
    - typecheck
```

O DSL é compilado para componentes de runtime.

## 63. Harness Compiler / Resolver

A configuração declarativa precisa ser validada.

Etapas:

1. parse;
2. schema validation;
3. dependency resolution;
4. capability resolution;
5. policy consistency;
6. model compatibility;
7. runtime graph construction.

Erros detectáveis antes de executar:

- agent requer tool não instalada;
- verifier requer rede negada;
- model não suporta structured tool call;
- skill exige capability ausente.

## 64. Plugin architecture

Plugins podem fornecer tools, skills, verifiers, model adapters, retrievers, memory stores e policies.

Plugin deve declarar versão, capabilities, permissions e dependencies.

A carga deve ser explicitamente controlada.

## 65. Segurança de plugins

Nunca assumir que plugin é confiável.

Recomendações:

- manifest;
- signatures;
- permission review;
- isolated execution;
- dependency audit;
- version pinning.

## 66. Error recovery

Falhas são parte normal de autonomia.

Categorias:

- model failure;
- parser failure;
- tool failure;
- timeout;
- sandbox failure;
- verification failure;
- agent deadlock.

Recovery policies:

- retry;
- retry with repair;
- fallback model;
- alternate tool;
- replan;
- escalate;
- abort.

## 67. Loop detection

Detectar padrões como mesma tool + mesmos args, mesmos arquivos relidos, mesma hipótese ou zero progress em N steps.

Ações: reflection, replan, alternate agent ou stop.

## 68. Budgeting

Budgets:

- tokens;
- dollars;
- wall-clock;
- tool calls;
- agent spawns;
- search depth.

O scheduler deve tratar budget como restrição real.

## 69. Cost-aware scheduling

Política conceitual:

```text
start cheap
  ↓
measure uncertainty
  ↓
escalate only if necessary
```

Exemplo: fast search agent; se confiança insuficiente, strong reasoner; se alteração ampla, verifier independente.

## 70. Deterministic versus agentic orchestration

Nem toda decisão deve passar por LLM.

Determinístico:

- schema validation;
- permissions;
- retry threshold;
- test execution order;
- hash invalidation.

Agentic:

- hypothesis;
- search strategy;
- decomposition;
- semantic interpretation.

Boa arquitetura maximiza determinismo onde regras podem ser explicitadas.

## 71. CLI UX

Uma Agentic Coding CLI deve expor task state, active agent, current plan, tool operation, approvals, verification, cost e context use.

O usuário precisa manter controle do sistema.

## 72. Human-in-the-loop

Approval levels:

- Auto — operações de baixo risco;
- Ask — operações moderadas;
- Deny — ações proibidas;
- Escalate — requer política externa/administrador.

## 73. Proposta de interfaces conceituais

- **Harness** — composição.
- **Runtime** — execução de eventos.
- **Scheduler** — seleção de estratégia.
- **Agent** — decisão de ações.
- **ContextEngine** — montagem da visão do mundo.
- **Retriever** — busca informação.
- **MemoryStore** — persiste experiências.
- **Skill** — adiciona capacidade.
- **Tool** — executa efeito.
- **PolicyEngine** — autoriza.
- **Sandbox** — isola.
- **Verifier** — produz evidência.
- **EventStore** — persiste trajetória.
- **Evaluator** — mede resultado.

## 74. Roadmap de implementação

### Fase 1 — Runtime mínimo

Implementar EventStore, Session, model adapter, tool abstraction, policy, executor e telemetry.

Meta: executar um single-agent ReAct reproduzível.

### Fase 2 — Context e verification

Adicionar repository index, structural retrieval, ContextEngine e verification contracts.

Meta: coding agent robusto sem multi-agent.

### Fase 3 — Isolation e artifacts

Adicionar subagents, typed artifacts, role-specific context e budgets.

Meta: researcher + editor + verifier.

### Fase 4 — Memory e skills

Adicionar checkpoints, episodic store, consolidation, skills e progressive disclosure.

### Fase 5 — Adaptive Scheduler

Adicionar model routing, dynamic delegation, parallelism e cost-aware strategy.

### Fase 6 — Optimization

Adicionar trajectory dataset, offline evaluation, preference optimization e harness-native RL.

## 75. MVP recomendado

O MVP deve provar cinco ideias:

1. event-driven runtime;
2. deterministic tool policy;
3. structural context;
4. verification-based completion;
5. reproducible telemetry.

Configuração inicial:

- 1 primary agent;
- 1 optional research subagent;
- filesystem;
- shell;
- symbol search;
- tests;
- sem long-term memory inicialmente.

## 76. O que não construir primeiro

### Não começar por swarm

Complexidade prematura.

### Não começar por vector database

Retrieval estrutural pode resolver grande parte das tarefas.

### Não começar por memória infinita

Persistência pode introduzir mais ruído que valor.

### Não começar por RL

Primeiro estabilizar harness.

### Não começar por 30 adapters

Provar interfaces com poucos modelos.

## 77. Hipóteses de diferenciação competitiva

### 77.1 Harness composability

Construir múltiplos agentes com o mesmo runtime.

### 77.2 Evidence-driven execution

Verification como requisito estrutural.

### 77.3 Process observability

Métricas de trajetória de primeira classe.

### 77.4 Model independence sem model blindness

Provider-agnostic, mas model-aware.

### 77.5 Experimental reproducibility

A/B testing de harnesses nativo.

## 78. Métrica principal

Não otimizar apenas pass rate.

O objetivo deve ser:

> **resolved tasks por unidade de custo e tempo, sob restrições de segurança e qualidade.**

Métricas complementares: success rate, cost, latency, verification confidence, risk incidents e token efficiency.

## 79. Princípios finais de design

1. **Harness > wrapper** — a arquitetura é parte da capacidade.
2. **Context > volume** — mais contexto não é sempre melhor.
3. **Structure > embedding-only** — código possui relações formais.
4. **Events > hidden mutable state** — trajetórias devem ser reproduzíveis.
5. **Artifacts > transcripts** — agentes devem trocar contratos informacionais.
6. **Policy > prompt** — segurança precisa de enforcement.
7. **Evidence > confidence** — verificação externa define sucesso.
8. **Adaptation > uniformity** — modelos diferentes precisam de protocolos diferentes.
9. **Selective multi-agent > swarm-by-default** — delegação só quando justificada.
10. **Measurement > intuition** — toda decisão arquitetural importante precisa de ablation.

---

# CONCLUSÃO GERAL

O estado atual dos Agentic Coding Harnesses demonstra que estamos entrando em uma fase na qual **engenharia de agentes passa a ser engenharia de sistemas distribuídos cognitivos**.

O modelo fornece generalização e raciocínio probabilístico. O harness fornece estrutura, estado, instrumentos, segurança, memória, feedback e critérios de conclusão.

A fronteira prática não está apenas em aumentar parâmetros ou context windows. Está em controlar melhor o ciclo:

> **perceber → selecionar contexto → decidir → agir → observar → verificar → aprender**

Claude Code mostra o valor de context isolation, subagentes, skills, hooks e memória hierárquica.

Codex mostra o valor de threads, compaction como checkpoint, memória consolidada, instruções hierárquicas e separação entre sandbox e approval.

OpenHands oferece uma arquitetura particularmente limpa para um runtime stateless, event-driven e componível.

Aider demonstra que retrieval estrutural, model-specific protocols e prompt caching continuam sendo altamente relevantes.

ContextBench alerta que retrieval continua longe de resolvido e que agentes frequentemente exploram mais contexto do que realmente utilizam.

Terminal-Bench mostra que harnesses diferentes conseguem extrair performance substancialmente distinta do mesmo modelo.

LEGO-RL sugere uma próxima etapa: treinar modelos dentro do próprio harness, transformando model e runtime em um sistema co-otimizado.

A aplicação correta desses aprendizados é criar um **Harness Builder**, não um único “super agente”.

O framework deve permitir configurar e compor diferentes sistemas sobre os mesmos primitives:

- Runtime;
- ContextEngine;
- Agent;
- ModelAdapter;
- Retriever;
- MemoryStore;
- Skill;
- Tool;
- PolicyEngine;
- Sandbox;
- Verifier;
- Scheduler;
- EventStore;
- Evaluator.

A partir desse núcleo, coding agents, research agents e autonomous task solvers tornam-se variações arquiteturais em vez de produtos completamente distintos.

A tese de engenharia final é:

> **O melhor agente não é o que raciocina mais. É o sistema que entrega ao modelo o contexto certo, oferece apenas as ações corretas, registra o estado necessário, verifica consequências de forma independente e aprende seletivamente com experiências anteriores.**

---

# Próximos experimentos recomendados

1. **Harness ablation** — mesmo modelo, diferentes loops.
2. **Retrieval ablation** — structural vs lexical vs semantic vs agentic.
3. **Context-isolated researcher** — medir qualidade, custo e redução de contexto.
4. **Verification graph** — comparar self-declared completion com evidence-based completion.
5. **Episodic memory** — medir redução de erros repetidos.
6. **Adaptive model routing** — medir custo/resolução.
7. **Harness-native optimization** — somente após estabilização do runtime.

---

# Referências primárias e bibliografia

## Claude Code

- **Subagents:** https://code.claude.com/docs/en/sub-agents
- **Agent teams:** https://code.claude.com/docs/en/agent-teams
- **Memory:** https://code.claude.com/docs/en/memory
- **Commands / permissions / MCP:** https://code.claude.com/docs/en/commands
- **Features overview:** https://code.claude.com/docs/en/features-overview

## OpenAI Codex

- **Repository:** https://github.com/openai/codex
- **AGENTS.md example / repository instructions:** https://github.com/openai/codex/blob/main/AGENTS.md
- **Memory pipeline:** https://github.com/openai/codex/blob/main/codex-rs/memories/README.md
- **Core memories pipeline:** https://github.com/openai/codex/blob/main/codex-rs/core/src/memories/README.md
- **Compaction prompt:** https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/compact/prompt.md
- **MCP client/server:** https://github.com/openai/codex/blob/main/codex-rs/README.md

## OpenHands

- **Agent architecture:** https://github.com/OpenHands/docs/blob/main/sdk/arch/agent.mdx
- **Security architecture:** https://github.com/OpenHands/docs/blob/main/sdk/arch/security.mdx
- **Design principles:** https://github.com/OpenHands/docs/blob/main/sdk/arch/design.mdx
- **Condenser base:** https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/context/condenser/base.py
- **Software Agent SDK:** https://github.com/OpenHands/software-agent-sdk

## Aider

- **Documentation:** https://aider.chat/docs/
- **Repository map:** https://aider.chat/docs/repomap.html
- **Configuration / prompt caching:** https://aider.chat/docs/config/options.html
- **Usage modes:** https://aider.chat/docs/usage/modes.html

## Benchmarks e research

- **Terminal-Bench 2.1 leaderboard:** https://www.tbench.ai/leaderboard/terminal-bench/2.1
- **Terminal-Bench 2.0 — GPT-5.3-Codex comparisons:** https://www.tbench.ai/leaderboard/terminal-bench/2.0?models=GPT-5.3-Codex
- **ContextBench:** https://arxiv.org/abs/2602.05892
- **LEGO-RL:** https://arxiv.org/abs/2608.17393
- **SWE-bench:** https://www.swebench.com/

---

# Apêndice A — Glossário

**Agent** — entidade que seleciona ações iterativamente para atingir um objetivo.

**Harness** — infraestrutura que operacionaliza agente e modelo.

**Context Engine** — sistema que seleciona e monta o contexto efetivamente enviado ao modelo.

**Condenser / Compaction** — componente responsável por reduzir histórico preservando estado útil.

**Artifact** — estrutura tipada produzida por um agente para consumo de outro componente.

**Skill** — capability modular carregada sob demanda.

**Tool** — interface que permite ao agente observar ou alterar ambiente.

**Policy Engine** — camada determinística que decide se uma ação é permitida.

**Sandbox** — ambiente de execução restrito.

**Verifier** — componente que produz evidência sobre critérios de aceitação.

**Event Store** — persistência da trajetória de execução.

**Episodic Memory** — memória de experiências anteriores.

**Semantic/Procedural Memory** — conhecimento durável sobre domínio, arquitetura ou workflow.

**Model Adapter** — camada que adapta protocolo do harness às características do modelo.

**Scheduler** — componente responsável por estratégia, delegação, routing e budgets.

---

# Apêndice B — Checklist arquitetural do Harness Builder

## Runtime

- [ ] Event sourcing
- [ ] Sessions
- [ ] Resume
- [ ] Replay
- [ ] Fork
- [ ] Cancellation
- [ ] Budgets

## Models

- [ ] Provider adapters
- [ ] Model profiles
- [ ] Cost metadata
- [ ] Tool capability
- [ ] Prompt caching
- [ ] Reasoning settings

## Context

- [ ] Hierarchical instructions
- [ ] Token budgets
- [ ] Structural code context
- [ ] Context compaction
- [ ] Role-specific views

## Retrieval

- [ ] Exact/path
- [ ] Symbols
- [ ] AST
- [ ] Graph
- [ ] Lexical
- [ ] Semantic
- [ ] Agentic exploration

## Agents

- [ ] Main/orchestrator
- [ ] Researcher
- [ ] Planner
- [ ] Editor
- [ ] Verifier
- [ ] Parallel execution
- [ ] Typed artifacts

## Memory

- [ ] Working
- [ ] Checkpoint
- [ ] Episodic
- [ ] Semantic
- [ ] Consolidation
- [ ] Invalidation

## Tools

- [ ] Schemas
- [ ] Capability metadata
- [ ] Side-effect metadata
- [ ] Risk metadata
- [ ] Cache policy
- [ ] MCP adapter

## Security

- [ ] Policy engine
- [ ] Risk classification
- [ ] Approval
- [ ] Filesystem control
- [ ] Network control
- [ ] Secret isolation
- [ ] Sandbox

## Verification

- [ ] Verifier interface
- [ ] Verification graph
- [ ] Acceptance contracts
- [ ] Independent verification
- [ ] Evidence persistence

## Observability

- [ ] Tracing
- [ ] Token metrics
- [ ] Cost metrics
- [ ] Tool metrics
- [ ] Retrieval metrics
- [ ] Agent metrics
- [ ] Verification metrics

## Evaluation

- [ ] Outcome benchmarks
- [ ] Process benchmarks
- [ ] Harness ablations
- [ ] Cost-aware metrics
- [ ] Regression suite

---

# Apêndice C — Hipótese de arquitetura de referência v0.1

```text
Task
 │
 ▼
TaskClassifier
 │
 ▼
Scheduler
 │
 ├── MainAgent
 ├── ResearchAgent
 ├── PlannerAgent
 ├── EditorAgent
 └── VerifierAgent
 │
 ▼
ContextEngine
 ├── Instructions
 ├── RepositoryIntelligence
 ├── Retrieval
 ├── WorkingMemory
 ├── EpisodicMemory
 └── Skills
 │
 ▼
ModelAdapter
 │
 ▼
AgentLoop
 │
 ▼
ToolRuntime
 │
 ▼
PolicyEngine
 │
 ▼
Sandbox
 │
 ▼
Execution
 │
 ▼
VerificationEngine
 │
 ▼
EventStore
 │
 ├── Replay
 ├── Checkpoint
 ├── Telemetry
 └── MemoryConsolidation
```

---

# Apêndice D — Perguntas de pesquisa em aberto

1. Em quais classes de tarefa multi-agent oferece ganho estatisticamente significativo após normalizar por custo?
2. Qual combinação de structural + lexical + semantic retrieval maximiza contexto útil por token?
3. Como medir corretamente *context utilization*, e não somente recall?
4. Qual política de compaction preserva melhor estado operacional?
5. Como detectar memórias obsoletas antes que prejudiquem decisões?
6. Qual é a melhor forma de compor policies entre tool, MCP, plugin e remote executor?
7. Como medir independência real de um verifier que usa modelo da mesma família?
8. Quando adaptar edit protocol por modelo traz ganho suficiente para justificar complexidade?
9. Quanto do ganho de harness-native RL permanece após troca de harness?
10. É possível aprender políticas de scheduler a partir de event trajectories?
11. Como otimizar simultaneamente success, latency, cost e risk?
12. Qual é a abstração mínima de Harness DSL que mantém poder sem virar configuração excessiva?

---

**Fim do relatório.**

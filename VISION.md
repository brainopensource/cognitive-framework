---
id: repo-root-vision
class: charter
authority: constitutional
canonical_for:
  - architectural-identity
  - agentic-ontology
  - product-principles
  - long-term-direction
status: locked
owner: principal-systems-architect
version: "0.9.0b1"
last_verified: 2026-08-26
locked_by: ADR-0095+ADR-0096+ADR-0097+ADR-0100+ADR-0101+ADR-0102
read_when:
  - resolving-any-architectural-authority-conflict
  - proposing-a-new-milestone-or-roadmap-change
  - deciding-where-a-capability-belongs-in-the-layer-stack
do_not_read_when:
  - looking-up-a-current-implementation-detail
supersedes: []
superseded_by: null
---

# AETHER — Vision (Law Zero, v0.7+)

The frontmatter `version` is this constitutional document's revision, not the software package
version. The package version is owned exclusively by `pyproject.toml`.

## Authority of this document

This is **Law Zero**: the binding architectural and product authority for v0.7+, locked by
[`ADR-0095`](docs/02_decisions/0095-vision-as-law-zero-and-roadmap-reconciliation.md). It defines
*what AETHER is and where it is going*. Every other active document exists to specify, implement,
measure, or schedule this Vision.

**Precedence ladder — highest first. In a conflict, the higher document wins.**

| # | Layer | Documents | Owns |
|---|---|---|---|
| 0 | **Vision (constitutional)** | `VISION.md` | Architectural identity, ontology, product principles, non-negotiable direction |
| 1 | **Law (normative)** | [`docs/SPEC.md`](docs/SPEC.md) | Current system requirements, invariants, RFC-2119 obligations that realize the Vision |
| 2 | **Decisions (binding)** | [`docs/decisions.md`](docs/decisions.md) | Local architectural decisions; may refine implementation, may **not** contradict locked Vision |
| 3 | **Architecture & product** | [`docs/architecture/`](docs/architecture/), [`docs/backend/`](docs/backend/), [`docs/frontend/`](docs/frontend/), [`docs/product/`](docs/product/), `schemas/` | Wire-level and component realization of the law |
| 4 | **Sequencing** | [`docs/execution/milestones.md`](docs/execution/milestones.md), [`backlog.md`](docs/execution/backlog.md) | Delivery gates and stable work packages |
| 5 | **Authorization** | [`docs/execution/active.md`](docs/execution/active.md) | The only board that authorizes current work; `sprint_upcoming.md` is staging only |
| 6 | **Communication** | `README.md`, [`docs/theory/`](docs/theory/), [`docs/research/`](docs/research/), [`docs/reports/`](docs/reports/) | Current state and orientation; introduces **no** independent architecture |

Three rules follow from this ladder:

1. **A lower document may not be used to reject a Vision concept.** If law, an ADR, a protocol, or
   the README still describes the previous architecture, that text is stale and MUST be reconciled —
   it is not a counter-authority.
2. **The Vision is changed only by an explicit Vision-superseding ADR**, ratified by Engineering
   Leadership and reflected here atomically. Sustained material reproducible counter-evidence MUST
   trigger Vision review, but evidence never amends the constitution implicitly.
3. Divergence is classified explicitly. **Implementation non-conformance** is a documented gap and
   has no constitutional effect. **Reproducible material counter-evidence** triggers mandatory
   architectural review and may change the Vision only through a ratified successor ADR.

Historical ADRs remain immutable provenance. They are superseded, never rewritten.

## Ratified constitutional clarifications (v0.7.1)

ADR-0096 and ADR-0097 bind the following interpretations throughout this Vision:

- Event sourcing is the v0.7 reference realization of durable causal history, attributable
  artifacts, reconstructable projections, committed outcomes, authority, cold replay, and
  process-independent continuation. A replacement requires equivalent invariants and falsifiers.
- Runtime Agent objects are permitted conveniences; authoritative persistent in-memory Agent state
  is prohibited.
- The causal record is authoritative; telemetry is correlated operational evidence and never a
  second truth.
- Reproducibility is computed, multidimensional, time-aware, and proof-honest. Capability or
  prerequisite presence is not executed verification.
- Settlement belongs to the substrate; Kernel owns admissibility, authority, and generic resource
  invariants. The Trusted Core is its transitive executable import closure, not a directory count.
- Memory, topology, scheduling, learning, delegation, and metacognition are derived capability
  families. They do not become mandatory independent layers or Kernel semantics.
- Composition-level promotion requires regression decomposition and distinct generator, evaluator,
  and promoter authority.
- Authority provenance and capture/privacy policy are first-class protocol data. Retention never
  grants permission to capture content.
- Milestone acceptance is monotonic and receipt-backed; mechanism, integration, experiment,
  independent attestation, and accepted closure are distinct states.
- Durable memory and promotion remain subordinate capabilities: authorization precedes retrieval,
  and an immutable composition is promoted or rolled back only by separated authorities.

---

# AETHER v0.7+ — Event-Sourced General Agent Framework

## Capítulo 1 — Tese central: de Agent Framework para Substrate de Computação Agentic

AETHER deve ser definido a partir de uma tese mais fundamental do que “framework para criar agentes”. O objetivo é construir um **substrate geral de computação agentic**, no qual comportamento inteligente complexo emerge da composição reiterada de primitivas simples, observáveis, substituíveis e reutilizáveis. Coding agents, pesquisadores, planners, critics, equipes, sistemas de debate, memória de longo prazo e mecanismos metacognitivos não devem constituir arquiteturas independentes. Devem ser diferentes organizações sobre a mesma base operacional.

A unidade fundamental do sistema, portanto, não é uma classe `Agent`, um workflow pré-programado ou uma máquina de estados específica de domínio. A unidade fundamental é uma **operação causal tipada**, executada dentro de determinado contexto, produzindo eventos, artefatos e alterações observáveis. Uma execução inteira é formada pela composição dessas operações.

Essa formulação muda a direção do desenvolvimento. Não devemos tentar prever todos os tipos de agentes que existirão e criar abstrações específicas para cada um. Devemos construir um conjunto pequeno de primitivas suficientemente gerais e contratos suficientemente estáveis para que novas estruturas agentic possam emergir pela composição.

A arquitetura já existente fornece boa parte dessa fundação: kernel domain-blind, ports tipados, runtime de composição, agency genérica, adapters, domain packs e ledger persistente. Os documentos recentes já reconhecem que comportamento de coding, research e outros domínios deve permanecer fora do kernel e ser implementado por packs, plugins, adapters e policies.

A filosofia da v0.7+ deve ser, portanto, **product-first, composition-first, evidence-first e experiment-first**, sem abandonar a disciplina arquitetural conquistada. O sistema precisa se tornar útil rapidamente, mas sua utilidade deve surgir pela mesma arquitetura que permitirá generalização futura. Não queremos um produto temporário que posteriormente será substituído pelo Meta-Framework; queremos que o produto seja a primeira manifestação prática do Meta-Framework.

---

## Capítulo 2 — Event Sourcing como ontologia operacional

Event sourcing deve ser entendido em AETHER não apenas como uma técnica de persistência, mas como uma escolha de **ontologia operacional**. Em vez de considerar o estado atual como a verdade primária e os logs como informação secundária, consideramos a sequência causal de fatos como a verdade, enquanto o estado atual é uma projeção derivada dessa história.

Se um objetivo foi declarado, um arquivo observado, uma hipótese criada, uma tool chamada, uma edição aplicada, um teste falhou, um plano foi revisado e posteriormente uma tarefa terminou, esses acontecimentos constituem a execução. O estado “atual” do sistema é apenas o resultado da redução dessa história.

Essa arquitetura produz propriedades particularmente importantes para sistemas agentic. Ela permite reconstrução após crash, análise retrospectiva, comparação de estratégias, auditoria de decisões observáveis, geração de datasets de trajetória, bifurcação de execuções, criação de simulations contrafactuais e estudo científico da influência de diferentes políticas.

A truth model deve permanecer simples: **eventos registram fatos causais pequenos e permanentes; artifacts preservam conteúdos maiores; projections materializam estados derivados**. O documento arquitetural atual já converge para essa distinção ao definir o append-only event log e content-addressed artifacts como verdade central, enquanto indexes, caches e measurements são derivados.

Event sourcing não significa registrar indiscriminadamente qualquer variável interna do programa. O ledger não deve virar um dump de memória. A questão relevante é causalidade: se determinado elemento participou materialmente da geração de um resultado e é necessário para explicá-lo, reconstruí-lo ou compará-lo cientificamente, sua identidade precisa permanecer observável.

Isso torna o AETHER potencialmente mais valioso como infraestrutura de pesquisa do que frameworks que guardam apenas a mensagem final. Um resultado deixa de ser apenas uma resposta. Ele passa a possuir uma trajetória experimental completa.

---

## Capítulo 3 — Replay, reconstrução e re-execução probabilística

É necessário estabelecer uma distinção normativa entre **replay** e **re-execução**.

Replay significa aplicar novamente os eventos persistidos a reducers compatíveis e reconstruir o estado semanticamente equivalente que existia em determinado ponto da execução. Nesse processo, uma resposta anterior da LLM não é calculada novamente; ela já é um fato registrado. Sob schemas, reducer versions e artifacts corretamente identificados, esse processo pode ser deterministicamente reproduzível.

Re-execução significa executar novamente modelos, tools ou policies com os mesmos inputs. Isso não possui a mesma garantia. Mesmo modelos executados com temperatura zero podem variar por mudanças de backend, floating-point behavior, batching, model routing, provider revisions ou diferenças de infraestrutura. Baixa temperatura reduz variância estatística, mas não transforma inferência de modelos modernos em computação puramente determinística.

AETHER deve explorar ambos os conceitos, mas nunca confundi-los. O replay responde: **“qual estado resulta da história que efetivamente ocorreu?”**. A re-execução responde: **“o que aconteceria se submetêssemos novamente condições equivalentes ao sistema?”**

A segunda pergunta é particularmente importante para investigação científica. Uma trajectory registrada pode ser utilizada como baseline para executar variantes de modelo, prompt, topology, compaction policy, retrieval depth, recursion depth, budget, tool selection ou strategy controller.

Isso cria uma plataforma para **re-simulation**. Podemos preservar determinada parte de uma trajetória e substituir outra. Podemos perguntar o que teria ocorrido usando um modelo diferente apenas no passo onze, utilizando outra compactação no passo vinte ou alterando a quantidade de evidence retrieval disponível a um critic.

O objetivo científico não é fingir determinismo onde ele não existe. É identificar precisamente quais variáveis permaneceram constantes, quais foram modificadas e quais resultados emergiram.

---

## Capítulo 4 — O agente como projeção, não como objeto físico

A principal mudança conceitual da v0.7+ deve ser abandonar a necessidade de tratar o agente como uma entidade mutável permanente.

Em vez de uma classe `Agent` que carrega dentro de si memória, plano, estado, ferramentas e objetivos, podemos definir conceitualmente:

**Agent = Identity + Policy + Event-Derived Projection + Execution Boundary.**

A identidade permite correlacionar uma lineage. A policy influencia quais operações serão escolhidas. A projection resume o estado semanticamente relevante derivado do ledger. A execution boundary determina recursos, contexto, budget e outros limites daquela execução.

Nenhum desses elementos exige que exista permanentemente um objeto Python “vivo”. O processo pode terminar. Outro processo pode abrir o ledger, reconstruir a lineage e continuar.

Um `AgentView` pode derivar goal atual, plano, observações importantes, artifacts conhecidos, ações anteriores, failures, budget consumido, contexto relevante, estratégia corrente e terminal state. A projeção pode mudar radicalmente ao longo do tempo sem destruir provenance.

Isso permite agentes **metamórficos**. Um mesmo identificador de lineage pode começar explorando um problema, adotar posteriormente uma estratégia de planning, entrar em comportamento de debugging, solicitar delegação, abandonar uma hipótese e terminar como synthesizer. Não precisamos decidir antecipadamente a “natureza” ontológica desse agente.

O agente passa a ser uma conveniência cognitiva e operacional para designar uma região coerente do grafo causal, e não a unidade fundamental da arquitetura.

Esse modelo também simplifica recovery. Não recuperamos objetos mortos. Reconstruímos projeções a partir daquilo que ocorreu.

---

## Capítulo 5 — Primitivas: os átomos da computação agentic

O segundo elemento fundamental são as primitivas. Operações como `list`, `search`, `read`, `model.invoke`, `write`, `patch`, `bash`, `test`, `fetch`, `retrieve`, `evaluate`, `spawn` ou `publish` podem ser entendidas como átomos de uma linguagem geral de ação agentic.

Cada primitiva deve possuir pelo menos identidade, contrato de input, contrato de output, semantics observáveis, requisitos de capability quando aplicável, accounting de custo, possíveis side effects e representação de erro.

Um fluxo para explicar uma codebase poderia surgir como listagem, seleção por LLM, leitura, nova seleção, pesquisa externa, síntese e geração de documento. Um bug fixer utiliza muitos dos mesmos átomos, mas reorganizados: search, read, reason, patch, execute tests, inspect logs, revise e patch novamente. Um researcher substitui parte das tools por search, fetch, parse, citation e synthesis.

A generalidade não vem de uma primitiva chamada `research()` ou `fix_bug()`. Ela emerge da capacidade de compor operações menores.

Isso também explica por que devemos evitar grandes quantidades de branches específicas de domínio dentro do runtime. Decisões continuam existindo, mas podem ser realizadas por model policies, deterministic policies, graph transitions, plugin configurations ou control logic externa.

A mesma arquitetura suporta computação probabilística e determinística. Uma “caixa” pode ser uma chamada de LLM, mas outra pode ser um SMT solver, compiler, linter ou algoritmo convencional cheio de loops e `if/else`. A abstração não exige que todo processamento seja generativo; exige apenas contratos coerentes entre transformações.

---

## Capítulo 6 — Separação entre Kernel, Event Substrate, Runtime e Extensibility

O kernel deve permanecer pequeno e cognitivamente simples. Seu papel não é produzir inteligência. Seu papel é preservar invariantes mínimos associados à execução genérica: autoridade, budgets, admissibilidade de efeitos e regras fundamentais que não devem depender de coding, research ou qualquer ontology específica.

Essa separação já é uma força da arquitetura atual. Os documentos recentes descrevem uma estrutura `domain → ports → kernel → agency → runtime → adapters`, com kernel domain-blind e runtime responsável por composition e lifecycle.

A v0.7+ deve explicitar uma decomposição conceitual ainda mais clara.

O **Kernel** contém invariantes mínimos.

O **Event/Artifact Substrate** contém fatos persistentes, lineage, reducers, identities e artifacts.

O **Runtime** executa composition, sessions, lifecycle, effects e reconstruction.

A **Agency Layer** implementa mecanismos gerais de interação entre observations, proposals e operations, mas não agentes específicos.

A **Extensibility Layer** contém tools, model adapters, plugins, indexes, context providers, evaluators, MCP adapters e outras capacidades substituíveis.

Os **Packs e Policies** definem como essas capacidades são organizadas para tarefas concretas.

As futuras famílias de capacidade de **Topology, Scheduler, Memory, Learning e Meta-Control** devem ser derivadas acima dessa fundação e utilizar as mesmas primitivas; elas não são camadas obrigatórias nem runtimes independentes.

Essa separação é importante porque permite aumentar drasticamente a complexidade comportamental sem aumentar proporcionalmente o Trusted Core. Inteligência pode crescer nas bordas enquanto o substrate permanece estável.

---

## Capítulo 7 — Composição estática versus trajetória emergente

Devemos distinguir claramente duas espécies de grafo.

A primeira é a **composição**, que representa quais capacidades, providers, plugins, limits, schemas e policies existem para determinada execução. Ela é principalmente uma declaração do espaço de possibilidades.

A segunda é a **trajectory**, que representa quais possibilidades foram efetivamente utilizadas, em que ordem causal, com quais inputs, outputs e resultados.

Essa distinção evita transformar AETHER prematuramente em um workflow engine rígido.

Uma composição pode dizer que existem `fs.read`, `fs.search`, `model.invoke`, `patch.apply` e `proc.exec`. Ela não precisa dizer antecipadamente que a execução obrigatoriamente fará read, depois LLM, depois patch, depois test.

A sequência concreta pode emergir durante a execução.

Isso significa que o “fluxograma orgânico” que descrevemos é principalmente **observado depois de acontecer**, embora portions da estrutura possam ser condicionadas por policies ou topologies.

Com o avanço do framework, trajectories podem deixar de ser puramente lineares e assumir uma estrutura de causalidade parcialmente ordenada. A composição define as capacidades disponíveis. Policies decidem entre possibilidades. Topologies podem estabelecer relações estruturais. Scheduler pode organizar execução temporal. O ledger registra a história resultante.

Dessa forma evitamos dois extremos: um sistema completamente hard-coded como um workflow tradicional e um sistema completamente amorfo em que qualquer coisa pode acontecer sem contratos.

---

## Capítulo 8 — M-4: produto real como laboratório arquitetural

O novo M-4 deve ser a primeira manifestação concreta da filosofia inteira: um coding agent realmente utilizável.

O objetivo não é provar uma arquitetura no papel. É executar tarefas reais por um loop suficientemente competente para expor falhas do substrate, das tools, do context management e das policies.

O produto precisa inspecionar um repositório, pesquisar símbolos e arquivos, construir contexto, editar, executar testes, diagnosticar failures, reparar e terminar com resultado verificável. Deve persistir sua trajetória e suportar `resume`.

Esse milestone deve também instalar desde o início observabilidade suficiente para sustentar todo o programa científico posterior. Devemos registrar model invocations, selected context, tool calls, effects, failures, retries, latências, tokens, custos, artifacts e outcomes.

A experiência anterior mostrou que execução real encontra problemas que revisão abstrata não encontra. O próprio estado recente do projeto registrou diversas correções de runtime, composition e profiles encontradas durante convergência e qualificação.

A filosofia deve ser simples: **melhorar o framework utilizando tarefas reais como falsifiers**.

Assurance avançada continua podendo existir como profile adicional, mas não define o produto nem controla o ritmo normal da construção agentic.

---

## Capítulo 9 — Observabilidade científica como parte do produto, não pós-processamento

Observabilidade não deve ser tratada como feature de debugging adicionada depois. Ela é a infraestrutura que permitirá AETHER aprender sobre o próprio comportamento.

Uma trajectory útil para ciência precisa preservar muito mais que mensagens de chat. Deve ser possível correlacionar inputs, selected context, model outputs, tool invocations, transformations, costs, latency, errors, compaction operations, cache behavior, strategy changes e terminal outcome.

Os documentos anteriores já defendem granular scientific telemetry, incluindo tokens, latency, exact cost, context dynamics e statistical A/B benchmarking.

A v0.7+ deve ampliar essa ideia: cada execução é potencialmente uma observação experimental.

Isso permite construir datasets em que o target não é apenas “texto bom versus texto ruim”, mas **qual trajetória levou a determinado resultado sob determinada configuração**.

Sem essa infraestrutura, futuras afirmações como “metacognition melhorou performance”, “esta skill é superior” ou “esta topology funciona melhor” serão opiniões.

Com ela, podemos executar paired trials, fixed task sets, held-out workloads, ablation studies e factorial experiments. Podemos isolar modelos, prompts, tools, context depth, compaction, retrieval, recursion e topology.

Esse é um elemento central da visão: AETHER deve ser simultaneamente framework de execução e **laboratório de agentic systems**.

---

## Capítulo 10 — M-5a: estado agentic derivado do ledger

Depois do produto funcional, o próximo passo é formalizar o agente como projeção.

M-5a deve definir quais fatos são semanticamente necessários para reconstruir uma execução agentic. Eventos candidatos incluem declaração de objetivo, criação ou revisão de plano, observação, proposal, effect settlement, avaliação de progresso, mudança de estratégia, compactação de contexto, avaliação externa ou interna e conclusão.

O critério para introduzir um event kind não deve ser “isso aconteceu internamente”. Deve ser: **esse acontecimento altera semanticamente a história que precisamos reconstruir ou analisar?**

O AgentView deve ser uma projection, não um segundo banco de verdade.

Também não devemos exigir que diferentes domínios compartilhem exatamente o mesmo reducer final. Um coding solver e um formal solver podem possuir projections específicas. O que deve permanecer estável são os contratos fundamentais de event identity, lineage, persistence, effects e composition.

M-5a modifica o substrate de forma consciente e deve, portanto, acontecer antes de congelarmos o baseline usado para provar generalidade. Essa é uma correção importante ao roadmap anterior: seria contraditório provar “zero semantic diff” e simultaneamente alterar a semântica fundamental do agente.

Depois de M-5a, o substrate pode ser novamente congelado e utilizado como baseline do próximo experimento.

---

## Capítulo 11 — M-5b: generalidade como falsificação, não como declaração

M-5b possui uma função extremamente específica: verificar se aquilo que construímos é realmente generalizável.

A melhor maneira de fazer isso é utilizar um domínio materialmente diferente de coding. Formal reasoning, structured reasoning ou problemas com witness determinístico são excelentes candidatos porque oferecem oracle forte e reduzem ambiguidades de avaliação.

O objetivo não é construir imediatamente um grande produto formal. O objetivo é tentar quebrar a abstração.

Se para executar uma tarefa formal precisarmos inserir conhecimento matemático no kernel, alterar o generic episode mechanism ou criar um segundo runtime, então encontramos uma falha arquitetural.

Se for suficiente fornecer novas tools, policies, prompts, context providers e domain-specific projections, a generalidade foi fortalecida empiricamente.

Os documentos anteriores já definiam o segundo domínio como falsifier do substrate e RF-86 como mecanismo para impedir mudanças semânticas durante essa prova.

A diferença no novo roadmap é que esse baseline deve ser criado **depois** da consolidação do AgentView event-derived.

M-5b, portanto, não cria a generalidade. Ele tenta falsificá-la.

---

## Capítulo 12 — Recursividade como nested execution lineages

Se agentes não são objetos físicos, `spawn` também precisa de uma nova interpretação.

Spawn não deve significar “instanciar outra classe Agent”. Deve significar **criar uma nova execution lineage subordinada à lineage atual**.

Essa subexecução recebe identidade, parent reference, objetivo, selected context, budget, capabilities, depth boundary e terminal conditions. A partir daí ela produz sua própria sequência de eventos e artifacts.

Quando termina, seu resultado pode ser incorporado pela lineage pai.

A recursividade agentic passa então a ser o **aninhamento de regiões causais delimitadas**.

Essa formulação é particularmente poderosa para crash recovery. O parent ou child não precisa sobreviver como processo. Basta reconstruir o ledger e identificar quais lineages estão completas, interrompidas, waiting ou ainda executáveis.

Uma tool normal não equivale exatamente a spawn. Uma tool é uma transformação encapsulada, ainda que internamente muito sofisticada. Uma child lineage possui seu próprio ciclo agentic, context evolution e budget.

Essa diferença justifica `agent.spawn` como operação distinta, embora continue atravessando os mesmos mecanismos gerais de effects e accounting.

O projeto anterior já prevê `ChildSpawned` e `ChildReturned`, mas a implementação completa de delegation ainda estava pendente.

---

## Capítulo 13 — Fronteiras espaço-temporais e scopes de execução

A ausência de um Agent object rígido não elimina a necessidade de boundaries. Pelo contrário: torna necessário definir boundaries explicitamente como parte do protocolo.

Cada lineage deve possuir um **execution scope**.

Esse scope pode limitar tempo, wall-clock, tokens, cost, number of turns, tool invocations, recursion depth, accessible resources e capabilities.

Podemos pensar nesse scope como uma região espaço-temporal dentro do causal graph. Ela possui um início identificável, ancestry, condições de continuidade e condições terminais.

Isso oferece uma definição mais rigorosa de “agente” do que muitas frameworks convencionais: não uma entidade antropomorfizada, mas uma computação orientada a objetivo dentro de uma fronteira observável.

Esses scopes também permitem nested execution, teams e simulations sem perder accounting. Um parent pode possuir budget global e distribuir sub-budgets entre children. Cada child permanece identificável, mas o consumo pode ser agregado ao ancestor.

Essa arquitetura será importante para experimentos de busca em árvore, debate, populations e simulations, porque cada branch pode existir como lineage separada enquanto compartilha uma raiz causal comum.

---

## Capítulo 14 — M-6.5: Adaptive Strategy como início operacional da metacognição

Metacognição não deve ser introduzida como uma entidade mágica capaz de controlar o restante do sistema. Ela deve surgir como **controle de ordem superior baseado nas mesmas observações e operações disponíveis ao restante da arquitetura**.

Um meta-controller observa projections de progresso, failures, repetition, uncertainty, budget consumption ou missing knowledge. Com base nessas observações, uma policy pode selecionar uma nova estratégia.

Ela pode decidir revisar um plano, solicitar contexto adicional, abandonar uma hipótese, alterar uma verification strategy, delegar um problema ou encerrar a execução.

Nenhuma dessas decisões reescreve a história. Eventos anteriores continuam existindo. Um `PlanRevised`, por exemplo, não apaga o plano anterior; ele modifica a projeção atual e preserva o caminho pelo qual a mudança aconteceu.

Isso é precisamente o que torna essa abordagem útil para ciência: posteriormente conseguimos observar quando o sistema percebeu uma falha e se a alteração estratégica melhorou ou piorou o resultado.

A frase normativa deve permanecer:

**Metacognition is policy/reducer/plugin, never a kernel primitive.**

Seu benefício deve ser medido experimentalmente comparando paired runs com e sem meta-controller. Success rate, wasted loops, tool calls, cost, latency, recovery de failures e final quality são exemplos de métricas.

---

## Capítulo 15 — Concorrência, paralelismo e partial-order event graphs

A execução inicial pode ser sequencial sem que a arquitetura conceitual seja eternamente sequencial.

Precisamos diferenciar concorrência de paralelismo. Concorrência significa várias operações em progresso ou intercaladas. Paralelismo significa execução física simultânea.

Duas leituras independentes de arquivos são um caso trivial em que paralelismo deve ser possível. Duas chamadas independentes de search ou fetch também. O desafio surge quando operações compartilham recursos mutáveis ou budgets.

Duas edições sobre o mesmo arquivo, dois effects disputando determinado budget, dois children produzindo uma mesma output binding ou uma interrupção durante settlement introduzem problemas de conflict detection, reservation, idempotency, ordering e recovery.

A arquitetura deve, portanto, caminhar para um **causal partial order**. O event store pode possuir sequence numbers físicos para persistência, mas sequence number não deve ser confundido com dependência lógica.

A pode anteceder C e B também pode anteceder C sem que A anteceda B.

Essa interpretação aproxima AETHER de um dynamic dataflow system persistido por event sourcing.

A lane de concurrency measurement já proposta continua útil: medir effect independence e contention antes de construir scheduling sofisticado. Entretanto, isso não deve impedir paralelismo simples e obviamente seguro quando os contratos permitirem.

---

## Capítulo 16 — Topology e Scheduler: estrutura espacial e política temporal

Topology e Scheduler precisam permanecer conceitualmente separados.

A **Topology** define estrutura: quais roles ou lineages existem, quais relações causais são permitidas, quem pode solicitar trabalho a quem, quais artifacts conectam determinadas etapas e quais condições estruturais limitam a execução.

O **Scheduler** decide temporalidade: dentre as operações atualmente ready, quais executar primeiro, onde executá-las, quais paralelizar, quais suspender e quais priorizar.

Uma analogia útil é considerar topology como parte das boundary conditions estruturais e scheduler como política de evolução temporal dentro desse espaço permitido.

O **Kernel** permanece separado de ambos: ele decide se uma operação é autorizável segundo seus invariants genéricos.

O **Ledger** também permanece separado: ele registra o que realmente ocorreu.

Assim temos quatro responsabilidades diferentes: topology define possibilidades estruturais, scheduler organiza readiness no tempo, kernel preserva admissibilidade e ledger registra fatos.

Essa separação funciona particularmente bem com agentes não físicos. Um role em uma topology não precisa ser uma nova classe. Pode simplesmente significar uma lineage criada com determinada policy, context configuration, capabilities e goal.

Direct agent, planner/executor, critic/reviser, debate, research fan-out e tree search tornam-se diferentes configurações de uma mesma linguagem operacional.

---

## Capítulo 17 — Memória, contexto, cache e artefatos: persistência causal seletiva

Nem tudo deve ser um evento, mas “efêmero” não deve significar “irrelevante e descartável”.

Devemos distinguir pelo menos três categorias.

O **ledger** preserva fatos causais pequenos e duráveis.

O **artifact store** preserva conteúdos potencialmente grandes, como prompts completos, outputs, source snapshots, compressed contexts, patches, reports e datasets.

As **projections** incluem indexes, embeddings, caches, semantic memory, repo maps e outras estruturas derivadas.

Essa arquitetura já está parcialmente refletida no desenho atual, que recomenda artifacts grandes fora do ledger e indexes/caches como projections rebuildable.

Mas precisamos acrescentar uma regra científica: **qualquer variável que possa afetar materialmente o resultado deve possuir identidade e provenance observáveis**, mesmo que seu conteúdo completo seja armazenado fora do ledger ou sujeito a retention policy.

Se uma compaction alterou o contexto, registre source range, compactor identity, relevant parameters, input digest e output digest. Se houve cache hit, registre cache identity, key, source artifact e validation result.

Isso permite estudar posteriormente se determinada optimization foi responsável por grande parcela do desempenho.

Retention também deve ser configurável, mas não autoriza captura. Experiment profiles podem reter quase todos os artifacts autorizados; interactive profiles podem manter apenas digests e alguns blobs essenciais. A reproducibilidade da execução deve ser um vetor computado e temporal que separa capacidade de verificação executada; WAL e pins isoladamente não provam replay ou reconstrução.

---

## Capítulo 18 — Skills, aprendizagem e transformação de trajetórias em conhecimento

Skills não representam uma nova fundação. Elas são estruturas reutilizáveis construídas sobre a fundação existente.

Uma skill pode ser uma prompt policy, um pequeno programa, uma sequência parametrizada de operações, um topology fragment, uma heuristic ou uma strategy policy.

O aspecto importante é lifecycle.

Runs produzem trajectories. Trajectories produzem dados. Análise identifica padrões de sucesso e failure. Desses padrões podem surgir candidate skills ou policies. Essas candidates são avaliadas em workloads independentes. Versões que melhoram performance são promovidas explicitamente. Versões ruins podem ser revertidas.

Assim, aprendizagem deixa de significar necessariamente modificar weights de uma rede neural. O framework pode aprender em diversos níveis: retrieval policy, tool selection, prompts, context strategy, topology, budget allocation, delegation policy e reusable skills.

O princípio de segurança epistemológica aqui é importante: o agente pode **propor** uma skill, mas não deve declarar unilateralmente que ela é melhor. Promotion precisa utilizar avaliação explícita, provenance e rollback.

Os documentos anteriores já colocavam learned skills, retrieval e adaptation em fases futuras; a nova visão mantém esses elementos, mas os conecta diretamente às trajectories coletadas desde M-4.

AETHER começa assim a formar um ciclo de melhoria: execução produz dados, dados produzem abstrações, abstrações alteram futuras execuções, e os resultados dessas alterações voltam ao dataset.

---

## Capítulo 19 — Protocolo universal e evolução para uma linguagem de agentic computation

A ambição arquitetural mais profunda é que as diferentes camadas possam se comunicar através de um conjunto pequeno de protocolos universais.

Cada operation deve possuir identidade, input references, output references, causal parentage, execution scope, resource requirements, status e observability metadata.

Cada artifact deve possuir identity, schema/type, provenance e lifecycle.

Cada lineage deve possuir identity, ancestry, policy references, budget scope e projection semantics.

Cada event deve possuir stable schema, causation, correlation e ordering information.

Cada plugin deve declarar capabilities, dependencies, schemas e lifecycle hooks.

Cada topology deve ser representável como configuração ou artifact versionado, não como uma segunda runtime authority.

Com essas propriedades, AETHER começa a parecer menos uma coleção de agentes e mais uma **linguagem operacional para computação cognitiva distribuída**.

Um coding agent é um programa nessa linguagem. Um researcher é outro programa. Uma equipe de agentes é uma composição de programas. Uma skill é um fragmento reutilizável. Uma metacognitive policy modifica dinamicamente qual fragmento executar. Um scheduler determina temporalidade. Memory e indexes fornecem projections que influenciam as próximas decisões.

A inteligência observada não precisa estar localizada em nenhum componente individual. Ela pode emergir do comportamento global produzido pela interação entre primitives, policies, memory, models, evaluators e topology.

Essa é a principal justificativa para manter o kernel mínimo: quanto menos comportamento específico ele codificar, maior será o espaço de sistemas que podem emergir acima dele.

---

## Capítulo 20 — Roadmap, documentação e nova identidade da v0.7+

A documentação da v0.7+ deve refletir essa tese de maneira inequívoca.

O roadmap recomendado começa por **M-4**, com um coding agent útil e observabilidade de trajetória desde o primeiro dia. Depois vem **M-5a**, formalizando AgentView e agent state como projections event-sourced e estabilizando um baseline experimental imutável, revisado e verificável. **ADR-0102 registra que o ref histórico `M-5A-BASE-v2` não é esse controle e exige `CONVERGENCE-BASE-v1` como sucessor.** A partir do baseline válido, **M-5b** tenta falsificar a generalidade em um segundo domínio enquanto **M-6** implementa recursive delegation por nested lineages em uma lane independente. **M-6.5** introduz adaptive strategy e meta-control como policy/reducer/plugin. **M-7** introduz declarative topologies. **M-8** consolida memory, retrieval, skills e learning. **M-9/M-10** permanecem horizontes de compatibilidade até o aceite independente de M-8. A antiga lane de concurrency measurement deve permanecer identificável historicamente e terminar em uma decisão explícita de implementação, simplificação ou cancelamento.

Essa reorganização deve ser refletida em `README`, Product Vision, `SPEC.md`, architecture documentation, protocols, milestone definitions, sprint boards e novos ADRs. ADRs antigos permanecem como provenance histórica; novas decisões supersedem apenas aquilo que realmente mudou.

Locks genéricos de milestone devem ser substituídos por **technical dependencies explícitas**. Uma equipe deve ficar bloqueada apenas quando sua tarefa depende efetivamente de interface, schema ou semantics ainda instáveis. Coding UX, research tooling, adapters, indexing, context, telemetry e outras lanes devem avançar paralelamente sempre que seus contratos permitirem.

A identidade estratégica do projeto também precisa mudar. AETHER não deve ser apresentado prioritariamente como security architecture, certification framework, coding harness ou multi-agent framework. Essas são manifestações ou capacidades secundárias.

A definição central deveria ser:

**AETHER é um event-sourced general agent framework e experimental substrate no qual operações causais tipadas, artifacts, lineages, policies e plugins formam uma linguagem comum para construir, observar, reproduzir e evoluir sistemas inteligentes. Agentes não são entidades fundamentais: são projections dinâmicas sobre regiões do causal event graph. Memória, skills, delegation, metacognition e topologies não criam novos cores; emergem da composição das mesmas primitivas. O objetivo é permitir que inteligência cada vez mais complexa surja de iterações, feedback, experimentação, seleção e recomposição, mantendo uma fundação pequena e estável.**
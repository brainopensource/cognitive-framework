
Pensou por 2m 38s

Abaixo está a consolidação em formato de relatório técnico, incorporando a revisão dos documentos, as correções discutidas e a tese ampliada de AGI por composição de primitivas, sem tratar AGI como uma capacidade já demonstrada.

AETHER/Vanguard — Substrate Recursivo para Inteligência Agêntica, Meta-Harness e Self-Improvement

Relatório técnico de arquitetura e tese de pesquisa para Substrate v0.6.0

Resumo

Este relatório consolida a revisão arquitetural dos documentos "Vanguard-substrate-060-full-refactor-v3-1.md", "vanguard-substrate-060-execution-plan.md" e da "SPEC.md", juntamente com a evolução conceitual desenvolvida durante a discussão sobre agentes, subagentes, swarms, plugins, event sourcing, Meta-Harness, self-improvement, cognição avançada e uma possível trajetória de pesquisa em direção a sistemas de inteligência artificial geral.

A tese central proposta é:

«A inteligência do sistema não deve ser implementada como um engine cognitivo monolítico; ela deve emergir da composição, interação, avaliação, adaptação e evolução de um pequeno conjunto de primitivas estáveis.»

O Vanguard/AETHER deixa, portanto, de ser concebido apenas como um coding agent framework e passa a ser investigado como um substrato recursivo de execução agêntica.

Nesse substrato:

[
Agent = Principal + HarnessInstance
]

[
SubAgent = ChildPrincipal + HarnessInstance
]

[
MetaAgent = Principal + HarnessInstance + MetaCapabilities
]

e nenhum desses elementos exige uma nova engine.

O mesmo mecanismo fundamental deve ser capaz de operar:

1 agent
10 agents
100 agents
1000 logical agents

sem alterar as primitivas fundamentais do kernel.

O problema de escala passa, portanto, de:

«“como construir uma nova arquitetura para cada grau de complexidade?”»

para:

«“como escalar scheduling, estado, recursos e comunicação mantendo a mesma semântica?”»

Essa é uma distinção arquitetural profunda.

A "SPEC.md" atual já aponta nessa direção ao definir Layer 0 como uma combinação mínima de event-sourced state machine, effect-dispatch kernel, registry/lifecycle e scheduler, enquanto planejamento, memória, ferramentas, contexto, modelos e avaliação entram por interfaces versionadas.

---

1. Status epistemológico: isto é uma hipótese de AGI, não uma alegação de AGI

É importante separar objetivo de pesquisa de conclusão científica.

Nenhuma arquitetura atualmente conhecida demonstra que a composição de agentes, plugins, memória, metacognição ou self-improvement seja condição suficiente para produzir AGI.

O que pode ser defendido tecnicamente é uma hipótese:

«Uma arquitetura suficientemente geral pode permitir que competência progressivamente mais ampla emerja da composição e evolução de mecanismos simples, sem necessidade de introduzir novos mecanismos fundamentais para cada nova capacidade.»

Essa hipótese é interessante porque é falsificável.

Se cada novo domínio exigir:

NewDomainEngine
NewReasoningEngine
NewSwarmEngine
NewMetaEngine
NewMemoryKernel

então a abstração falhou.

Se, por outro lado:

new capability
     ↓
plugin
     ↓
manifest
     ↓
existing substrate

continuar sendo suficiente, a evidência de generalidade da arquitetura aumenta.

A própria SPEC já contém uma forma forte desse princípio através do requisito de domain blindness: novos domain packs devem entrar sem modificações no Layer 0.

---

2. Avaliação geral do Substrate v0.6.0

Os dois documentos de Substrate v0.6.0 constituem uma evolução substancial em relação aos roadmaps anteriores.

Os pontos mais fortes são:

- identificação explícita de falsos gates e comportamento semanticamente sintético;
- reconhecimento da necessidade de evidência comportamental;
- adoção de "state = fold(events)";
- separação entre execução, avaliação e aprendizado;
- migração baseada em equivalência comportamental;
- plugin runtime como infraestrutura anterior aos plugins de produto;
- coding agent como primeiro caso real;
- concorrência somente após condições formais;
- Meta-Harness somente depois de existir corpus mensurável;
- tentativa explícita de evitar Goodhart nos próprios mecanismos de governança.

O Full Refactor documenta, entre outros problemas, o veredito sintético no scheduler, a fraqueza do E-COV lexical, duplicidade de selector algebra, inexistência de ledger durável no "layer0", plugin worker ainda sintético e identity incompleta de plugins.

O Execution Plan, por sua vez, melhora substancialmente a estratégia ao optar por Python-first e Rust condicionado a evidência, colocar fatia vertical antes de contratos e definir uma disciplina explícita de gates.

A direção geral deve ser preservada.

Entretanto, alguns conflitos precisam ser eliminados antes da execução.

---

3. Correções bloqueantes antes da implementação

3.1 Python versus Rust

Existe uma contradição direta.

O Full Refactor propõe um core novo em Rust.

O Execution Plan, mais recente operacionalmente, determina Python-first e deixa Rust atrás de um decision gate baseado em medição.

A decisão recomendada é:

vanguard/packages/
       │
       │ behavioral oracle
       ▼
layer0/
       │
       │ production target v0.6
       ▼
selective Rust migration
only if evidence justifies it

Não se deveria criar:

vanguard/packages/
layer0/
aether-rust/

porque isso produziria três sistemas vivos.

O objetivo da v0.6 deve ser reduzir multiplicidade arquitetural, não introduzir outra implementação paralela.

Microkernels são particularmente valiosos quando mantêm pequena a quantidade de código que precisa compartilhar o domínio de confiança; a literatura clássica de microkernels também mostra que a fronteira mínima pode coexistir com desempenho elevado quando o mecanismo básico é cuidadosamente projetado.

Decisão

Python-first.

Rust entra apenas se métricas demonstrarem necessidade específica em partes do TCB.

Possíveis candidatos futuros:

canonicalization / hashing
selector algebra
effect dispatch hot path
sandbox supervisor
high-contention scheduler component

e não uma reescrita integral.

---

4. Autoridade: orchestrator decide, ledger prova

Outro conflito conceitual importante está no uso do termo:

«orchestrator authoritative.»

Isso deve ser refinado.

A arquitetura correta possui duas autoridades diferentes.

Autoridade de decisão

scheduler
orchestrator
kernel

decidem:

- quem executa;
- quando executa;
- qual lease recebe;
- qual budget recebe;
- quais capabilities são autorizadas.

Autoridade de estado

ledger + reducers

determinam:

«o que efetivamente aconteceu.»

Logo:

[
Decision
\rightarrow
DurableEvent
\rightarrow
Reducer
\rightarrow
EffectiveState
]

e não:

[
Decision
\rightarrow
MutableOrchestratorState
]

O orchestrator pode dizer:

«“Agent B recebeu uma lease.”»

Mas isso só se torna fato do sistema quando o evento correspondente estiver durável.

Uma nomenclatura melhor é:

Control / Decision Plane

para o orchestrator e:

Authoritative State Plane

para ledger + reducers.

Essa distinção preserva a propriedade fundamental da SPEC de que grants, budgets, approvals, plugin activation, evaluations e spawns fazem parte do event ledger.

---

5. O princípio mais importante: uma única máquina recursiva

O maior avanço conceitual desta revisão não está em um componente específico.

Está em eliminar a necessidade de diferentes engines para diferentes níveis de agência.

O modelo fundamental pode ser reduzido a:

Project
 └── Principal
      └── HarnessInstance
           └── Episode
                ├── Proposal
                ├── EffectRequest
                ├── Receipt
                ├── Artifact
                ├── Event
                ├── Evaluation
                └── spawn(...)

Formalmente, um harness em execução pode ser descrito como:

[
H_i =
(M_i,P_i,C_i,B_i,S_i)
]

onde:

[
M_i = manifest
]

[
P_i = plugin\ composition
]

[
C_i = capabilities
]

[
B_i = resource\ budget
]

[
S_i = event-derived\ state
]

Um agente passa a ser:

[
A_i = (Principal_i,H_i)
]

Quando um agente delega:

[
A_c =
spawn(A_p,H_c,C_c,B_c)
]

com invariantes:

[
C_c \subseteq C_p
]

e:

[
B_c \preceq B_p^{remaining}
]

Portanto:

Architect
 ├── Researcher
 ├── Programmer
 │    ├── Test Agent
 │    └── Debug Agent
 └── Reviewer

não corresponde a cinco arquiteturas.

São cinco instâncias da mesma máquina.

Essa abordagem possui parentesco conceitual com o Actor Model, originalmente proposto como uma arquitetura modular baseada em entidades independentes que interagem por mensagens, embora Vanguard acrescente explicitamente autoridade, budgets, provenance, harness composition e exterior evaluation.

Frameworks modernos como AutoGen também demonstram a utilidade de agentes configuráveis interagindo em sistemas multi-agent, mas a abstração proposta aqui é mais baixa: comunicação entre agentes é uma política sobre um substrate, não a definição fundamental de um agente.

---

6. O que é um agente

Não deveria existir uma classe conceitualmente privilegiada denominada:

SuperAgent
AutonomousAgent
MetaAgentEngine
SwarmAgentEngine

A definição suficiente é:

Agent = Principal + HarnessInstance

O "Principal" determina:

identity
authority
ownership
budget lineage
delegation lineage

O "HarnessInstance" determina:

planner
memory
context
tools
model
skills
policies
evaluation gate

O estado operacional está no ledger.

Dessa maneira, mudar cognição não muda autoridade.

Mudar autoridade não muda cognição.

Essa separação é extremamente importante.

---

7. Subagentes como recursão, não feature

Um subagente não deveria ser uma feature especial.

Deveria ser simplesmente:

child = spawn(
    parent=principal,
    harness=harness_ref,
    capabilities=attenuated_capabilities,
    budget=reserved_budget,
)

Uma interface aproximada poderia ser:

@dataclass(frozen=True, slots=True)
class SpawnRequest:
    harness_ref: HarnessRef
    task_ref: TaskRef
    capabilities: CapabilitySet
    reservation: Reservation
    acceptance_ref: EvaluationSpecRef


def spawn(
    parent: Principal,
    request: SpawnRequest,
) -> ChildHandle:

    require(
        request.capabilities <= parent.remaining_capabilities
    )

    require(
        request.reservation <= parent.remaining_budget
    )

    reservation_id = governor.reserve(
        parent,
        request.reservation,
    )

    principal = principals.derive_child(
        parent=parent,
        capabilities=request.capabilities,
        reservation=reservation_id,
    )

    ledger.append(
        ChildSpawned(
            parent_principal_id=parent.id,
            child_principal_id=principal.id,
            harness_ref=request.harness_ref,
            reservation_id=reservation_id,
        )
    )

    return ChildHandle(principal.id)

O ponto importante não é a sintaxe.

É a propriedade:

«"spawn()" não cria uma nova espécie de runtime.»

---

8. Swarm não é uma arquitetura diferente

Um swarm é apenas um conjunto maior de relações entre principals.

Formalmente:

[
\mathcal{A}

{A_1,A_2,\ldots,A_n}
]

mais uma política:

[
\pi_{coord}
]

que determina:

- decomposição;
- comunicação;
- competição;
- cooperação;
- revisão;
- quorum;
- prioridade;
- budget allocation.

Portanto:

[
Swarm =
Agents + CoordinationPolicy
]

e não:

[
Swarm = NewEngine
]

Diferentes formas de swarm podem então existir como plugins.

Hierarchical delegation

Parent
 ├── Specialist A
 ├── Specialist B
 └── Specialist C

Competitive search

proposal A ─┐
proposal B ─┼→ evaluator/selector
proposal C ─┘

Critic pattern

worker
   ↓
critic
   ↓
revision

Debate

A ↔ B ↔ C
      ↓
 decision

Experimentos com multi-agent debate mostram que múltiplos agentes podem melhorar certos tipos de raciocínio, mas isso não implica que mais agentes sempre sejam melhores.

Há também evidência de que aumentar agentes e rounds pode elevar fortemente custo de tokens, razão pela qual swarm size deve ser tratado como variável econômica e experimental, não como proxy de inteligência.

---

9. Stigmergy e colaboração através do ambiente

Uma forma particularmente interessante de colaboração não exige conversas permanentes entre agentes.

Agentes podem coordenar-se indiretamente através dos artifacts produzidos.

Agent A
   ↓
Artifact X
   ↓
CAS / Ledger
   ↓
Agent B

Isso lembra o conceito de stigmergy, em que componentes coordenam comportamento através das modificações deixadas no ambiente. A literatura de sistemas auto-organizados utiliza esse conceito para explicar coordenação sem controlador comunicacional central para cada interação.

No Vanguard isso pode ser operacionalizado sem importar metáforas biológicas para a arquitetura:

artifact produced
event emitted
dependency becomes satisfiable
scheduler observes
another agent proceeds

Ou seja:

«stigmergy é uma possível interpretação científica da dinâmica, não uma primitive chamada "StigmergyEngine".»

---

10. Graphs: propriedade emergente, não workflow imposto

A estrutura natural do sistema já é relacional.

Existem relações como:

spawned_by
caused_by
depends_on
produced
consumed
evaluated_by
derived_from
invalidated_by

Logo o sistema naturalmente induz um grafo:

[
G_t=(V_t,E_t)
]

em que os vértices podem incluir:

Principal
Episode
Effect
Artifact
Task
Verdict
Harness
Plugin

e as arestas são derivadas dos eventos.

Idealmente:

[
G_t =
\Pi_G(L_{\le t})
]

onde:

- L é o ledger;
- \Pi_G é uma projeção.

Portanto:

«o grafo é consequência da causalidade registrada, não a linguagem fundamental de execução.»

Isso evita transformar Vanguard em:

DAG definition
      ↓
workflow engine
      ↓
execute node
      ↓
execute next node

A própria SPEC rejeita um playbook runtime rígido.

Um task graph pode existir.

Mas ele deve ser:

dynamic
mutable
planner-produced
revisable
event-derived

e não uma DSL estática que determina toda execução.

Lamport mostrou que sistemas concorrentes possuem naturalmente relações de precedência parcial entre eventos; não é necessário inventar uma ordem global apenas para obter causalidade.

---

11. O ledger como coração epistemológico do sistema

A frase:

«“logs são o coração”»

pode ser refinada.

Não são logs operacionais tradicionais.

O correto é:

«o event ledger é a memória factual e causal do sistema.»

A separação deveria ser:

Ledger       = autoridade histórica
CAS          = conteúdo
Projection   = visão derivada
Cache        = aceleração
Index        = acesso
Memory       = representação cognitiva
Telemetry    = representação analítica

Consequentemente:

[
State_t =
fold(E_1,\ldots,E_t)
]

e:

[
Projection_t = f(L_{\le t})
]

[
Cache_t = g(L_{\le t},CAS)
]

Um cache pode desaparecer.

O sistema deve continuar correto.

Uma memória vetorial pode desaparecer.

Ela deve poder ser reconstruída ou novamente derivada.

Um index pode corromper.

Ele não deve redefinir a verdade factual.

---

12. Event sourcing híbrido é a decisão mais adequada

Event sourcing puro não significa reconstruir milhões de eventos em todo read.

A arquitetura recomendada é híbrida:

                  ┌─────────────┐
commands ────────▶│   Kernel    │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   Ledger    │ authoritative
                  └──────┬──────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Snapshot         Projection         Telemetry
        │                │
        ▼                ▼
 Current State       Query Models
                         │
                         ▼
                       Cache

Replay pode partir de:

[
Snapshot_k + Events_{k+1:n}
]

em vez de:

[
Events_{1:n}
]

em todas as consultas.

Isso mantém a propriedade epistemológica do event sourcing sem sacrificar hot-path performance.

---

13. “Tudo é evento” não significa “todo byte é evento”

A regra deveria ser:

«Tudo que altera estado, autoridade, causalidade, custo, identidade ou mundo externo deve possuir representação durável.»

Isso não exige ledgerar:

- cada token produzido;
- cada chunk de stdout;
- cada embedding;
- cada tensor;
- cada conteúdo completo.

Esses dados podem residir em CAS.

O evento contém:

digest
size
mime/type
producer
visibility
provenance

Por exemplo:

ArtifactProduced(
    artifact_ref="sha256:...",
    size_bytes=183820,
    media_type="text/x-python",
)

O conteúdo permanece fora do ledger.

Isso permite logs pequenos e conteúdo grande.

---

14. Execução concorrente versus ordenação do ledger

O Full Refactor apresenta a cadeia hash total como um limitador importante de paralelismo.

Esse diagnóstico precisa de nuance.

Execução pode ser concorrente mesmo se o commit final no ledger for serial.

Agent A ───────────── effect ───────┐
Agent B ───── effect ───────────────┼─▶ serialized commit
Agent C ─────────── effect ─────────┘

O que precisa ser medido é:

[
s =
\frac{T_{serial}}{T_{total}}
]

e não presumido.

Um append serial pequeno pode ser irrelevante.

Um append serial dominante pode tornar-se gargalo.

Portanto não se deveria introduzir vector clocks, Merkle DAGs ou distributed logs antes de evidência operacional.

A estrutura mínima pode usar:

project_seq
agent_seq
causation_id
correlation_id

onde:

project_seq
= commit order within a project

agent_seq
= local principal order

causation_id
= semantic causal edge

correlation_id
= shared operation lineage

Isso já fornece uma poderosa reconstrução causal.

---

15. Replay não é re-execution

Outra distinção essencial:

State replay

[
fold(L) = S
]

Deve ser determinístico.

Schedule replay

Com todos os inputs não determinísticos gravados:

[
Replay(schedule,cassettes)
\rightarrow
same\ trajectory
]

pode ser exigido.

Re-execution

Executar novamente contra:

- modelo remoto;
- relógio diferente;
- rede diferente;
- APIs externas;
- concorrência diferente;

não precisa gerar os mesmos bytes.

Logo o gate:

«duas execuções concorrentes ⇒ ledger byte-idêntico»

deve ser removido como requisito geral.

Byte identity é adequado somente para fixtures completamente controladas.

---

16. Identidade precisa de três níveis

Um único "harness_digest" não deveria responder todas as perguntas experimentais.

16.1 Harness identity

[
D_H =
H(
Manifest_{resolved}
\parallel
Plugins
\parallel
Assets
\parallel
Policies
)
]

Responde:

«Qual composição lógica foi criada?»

16.2 Execution identity

[
D_R =
H(
D_H
\parallel
Runtime
\parallel
Environment
\parallel
ModelIdentity
\parallel
OracleIdentity
)
]

Responde:

«O que realmente executou?»

16.3 Experiment cell identity

[
D_X =
H(
D_R
\parallel
Dataset
\parallel
Protocol
)
]

Responde:

«Qual célula experimental produziu esse resultado?»

Assim o mesmo harness usando duas versões diferentes de um provider deixa de parecer a mesma execução.

---

17. Plugin-first, não “tudo é plugin”

Existe uma nuance importante.

A direção plugin-first é correta.

Mas transformar literalmente tudo em plugin seria um erro.

Algumas propriedades não podem depender de código substituível pelo próprio agente.

O núcleo deve manter:

identity
authority
effects mediation
event semantics
plugin lifecycle
scheduling primitives

Todo o restante deve tender a plugins.

Essa divisão segue o princípio clássico de least privilege e de decisões baseadas em permissões, não exclusões, presente na literatura seminal de proteção de sistemas.

Uma regra útil:

«Mechanism and authority stay below the plugin boundary; strategy, cognition and domain knowledge stay above it.»

---

18. Plugin como unidade universal de especialização

A proposta multi-agent torna a arquitetura de plugins ainda mais importante.

Um agente não deve carregar tudo.

Um "CodingAgent" pode receber:

planner
repository index
AST patch
terminal
tests
context compiler

Um "ResearchAgent":

planner
search
citation manager
long-term memory
document tools

Um "ReviewerAgent":

critic planner
diff reader
static analysis
evaluation request tools

Todos são a mesma máquina.

A diferença é composição.

---

19. Memória é plugin

Memória cognitiva não deve ser confundida com ledger.

O ledger responde:

«O que aconteceu?»

A memória responde:

«O que vale a pena recuperar agora?»

Podem existir:

episodic memory
semantic memory
vector memory
graph memory
procedural memory
working memory

como estratégias diferentes.

A própria SPEC já prevê "IMemoryEngine" com capacidades opcionais e futura representação em grafo.

Reflexion demonstrou um caso em que feedback textual armazenado em memória episódica altera decisões posteriores sem modificar pesos do modelo, mostrando que adaptação comportamental pode ocorrer acima do modelo.

---

20. Skills são artifacts executáveis ou advisory

Skills não deveriam ser strings magicamente adicionadas ao prompt.

Uma skill robusta deveria possuir algo próximo de:

SkillManifest
 ├── id
 ├── version
 ├── input schema
 ├── output schema
 ├── capabilities required
 ├── implementation/artifact digest
 ├── provenance
 ├── validation evidence
 └── applicability metadata

Skills podem ser:

advisory
procedural
executable
composite

Voyager fornece um exemplo relevante de agente que constrói uma biblioteca crescente de skills executáveis e reutilizáveis, mostrando empiricamente que competências compostas podem ser preservadas externamente aos parâmetros centrais do modelo.

No Vanguard, entretanto, uma skill deveria sempre ser:

versioned
content-addressed
measured
reversible

---

21. Tools e scripts são capabilities, não intelligence

Uma ferramenta AST, shell, indexer ou browser não torna um agente intrinsecamente mais inteligente.

Ela altera seu espaço de ação.

Formalmente, dado um agente com política:

[
\pi(a|s)
]

um toolkit modifica:

[
\mathcal{A}
]

o conjunto de ações disponíveis.

Isso pode aumentar competência dramaticamente sem mudar o modelo.

ReAct demonstra justamente que intercalar raciocínio e ações externas pode melhorar desempenho em tarefas interativas comparado a usar apenas raciocínio textual.

Essa distinção é central para a tese AETHER:

«Model capability é apenas um componente da system capability.»

---

22. Context compression é plugin, nunca alteração da evidência

Compressão deve operar sobre uma projeção do estado.

Nunca sobre a fonte factual.

Ledger
  │
  ▼
Context Projection
  │
  ▼
Compression Plugin
  │
  ▼
ContextBundle

Se compressão for lossy:

original evidence

continua preservada no ledger/CAS.

Portanto uma futura estratégia:

hierarchical summarization
semantic compression
attention-based retrieval
graph retrieval
episodic selection

pode ser substituída sem alterar a história.

---

23. Cache é plugin/projeção e deve ser provenance-aware

Como o projeto pretende utilizar cache agressivamente, a chave de cache precisa carregar identidade suficiente.

Uma forma conceitual:

[
K =
H(
operation
\parallel
input_digest
\parallel
harness_identity
\parallel
plugin_identity
\parallel
environment
\parallel
authority_scope
)
]

O último elemento é particularmente importante.

Um resultado produzido por um principal com acesso privilegiado não pode necessariamente ser reutilizado por outro principal sem aquela autoridade.

Portanto caches precisam de:

provenance
visibility
authority scope
dependency identity
invalidation lineage

O cache continua sendo aceleração.

Nunca autoridade.

---

24. AST, indexing e heurísticas encaixam naturalmente

AST processing, repo mapping, heuristics, retrieval, rankers e indexers são excelentes exemplos de plugins porque:

- possuem input/output claro;
- podem ser substituídos;
- podem ser benchmarkados isoladamente;
- não precisam definir autoridade;
- podem possuir diferentes trade-offs.

Um experimento futuro poderia simplesmente substituir:

index:
  ref: tree-sitter-pagerank@2

por:

index:
  ref: semantic-symbol-hybrid@1

sem modificar scheduler, kernel ou ledger.

Essa é exatamente a propriedade desejada.

---

25. Metaprogramação futura

O verdadeiro ganho da arquitetura de manifests aparece quando o próprio sistema começa a gerar composições.

Hoje:

human edits manifest

Depois:

MetaPlanner
    ↓
ManifestCandidate
    ↓
HarnessCompiler
    ↓
FrozenHarness
    ↓
Experiment

Logo o framework passa de:

«software configurável»

para:

«software cuja arquitetura comportamental pode ser tratada como dado pesquisável.»

Isso é uma forma útil de metaprogramação.

O Meta-Harness não precisa editar o kernel.

Ele gera dados que o kernel já sabe interpretar.

---

26. Definição recomendada de Meta-Harness

Não deveria existir:

MetaHarnessEngine

como uma segunda máquina.

A definição mais forte é:

«Meta-Harness é o processo que compõe, instancia, observa, mede, compara e propõe evolução de Harness Definitions.»

O ciclo:

Harness H₀
   ↓
Execution
   ↓
Trajectory
   ↓
Analysis
   ↓
Mutation proposal
   ↓
Harness H₁
   ↓
Controlled experiment
   ↓
External evidence
   ↓
Promotion decision

Formalmente:

[
H_{t+1}

Promote(
Evaluate(
Mutate(H_t)
))
]

Não há self-modification in-place.

Há evolução versionada.

---

27. Self-improvement deve possuir níveis

Nem todo self-improvement possui o mesmo risco.

Uma taxonomia útil seria:

Nível 0 — Runtime adaptation

Sem persistência entre runs.

retry
rerouting
context adjustment

Nível 1 — Memory adaptation

Persiste conhecimento ou skills.

memory
skill library
heuristics

Nível 2 — Composition adaptation

Modifica:

plugins
prompts
model routes
retrieval policies
compression strategies

Nível 3 — Program synthesis

Gera novos plugins ou versões de plugins.

Nível 4 — Model adaptation

SFT
DPO
LoRA
distillation

Nível 5 — Core architecture modification

Modifica as próprias primitives.

Esse último nível não deveria ser autonomamente promovido na fase inicial.

A SPEC atual rejeita explicitamente um self-updating release pipeline.

---

28. O Learning Plane nunca promove

A arquitetura deve possuir:

Learning Plane
     │
     ▼
PromotionProposal
     │
     ▼
Experiment Plane
     │
     ▼
Evidence
     │
     ▼
Promotion Controller
     │
     ▼
PromotionDecision

Portanto:

[
Learning \neq Authority
]

Learning propõe.

Experiment mede.

Evaluator julga.

Promotion Authority decide.

Essa separação impede que o mecanismo que quer provar sua melhoria controle a evidência da própria melhoria.

---

29. O evaluator é autoridade, não verdade absoluta

A exterioridade do judge continua sendo uma das decisões mais importantes do projeto.

Mas:

[
SignedVerdict
\not\Rightarrow
CorrectVerdict
]

Assinatura prova:

authenticity
integrity
identity

Não prova:

oracle correctness
benchmark validity
absence of leakage
absence of specification error

Portanto o oracle também precisa ser:

versioned
content-addressed
tested
adversarially evaluated
replaceable through governance

A separação fundamental permanece:

[
Agent \not\rightarrow Judge
]

mas o judge também é submetido à ciência.

---

30. Inteligência como propriedade sistêmica

A competência observada de um agente pode ser modelada conceitualmente como:

[
Y =
F(
M,
P,
Mem,
Ctx,
Tools,
Skills,
Search,
Coord,
Eval,
B,
Env
)
]

onde:

- M: modelo;
- P: planner;
- Mem: memória;
- Ctx: context management;
- Tools: ferramentas;
- Skills: skills;
- Search: estratégia de busca;
- Coord: coordenação multi-agent;
- Eval: feedback/evaluation;
- B: orçamento;
- Env: ambiente.

Assim:

«melhorar inteligência não significa necessariamente aumentar o modelo.»

Pode significar melhorar qualquer elemento da composição.

---

31. Uma consequência científica: medir contribuição marginal

Uma vez que cada composição possui identidade, torna-se possível medir:

[
\Delta_C

E[Y|do(C=C_1)]

E[Y|do(C=C_0)]
]

mantendo as demais variáveis controladas.

Exemplo:

same model
same tasks
same seed policy
same tools
same evaluator

only indexer differs

Então é possível perguntar:

«qual é o efeito causal do novo indexer?»

Isso transforma plugins em unidades experimentais.

---

32. Cognição avançada deve emergir da composição

Não deveria existir:

CognitiveAdvancedEngine

Uma arquitetura cognitiva avançada poderia surgir da combinação de:

Planner
Memory
Context
World Model
Reflection
Uncertainty
Search
Skill Retrieval
Model Routing
Tools
Evaluation
Coordination

O kernel não precisa saber que isso constitui “metacognição”.

Ele apenas executa primitives.

---

33. Metacognição como funções observáveis

Metacognição pode ser decomposta em capacidades verificáveis.

Por exemplo:

Monitoramento

What do I know?
What failed?
How confident am I?

Diagnóstico

Was failure caused by:
model?
context?
tool?
memory?
budget?
environment?

Strategy selection

retry?
retrieve?
compress?
delegate?
escalate model?
change tool?

Reflection

What should change next time?

Calibration

Comparar:

[
P(success)
]

previsto com resultado real.

Assim metacognição torna-se um conjunto de mecanismos mensuráveis, não uma palavra arquitetural.

Reflexion é um exemplo de como feedback reflexivo pode alterar comportamento através de memória externa sem weight update.

---

34. Neuroscience como fonte de hipóteses, não blueprint

Neurociência pode inspirar plugins e mecanismos experimentais.

Não deveria determinar taxonomia de software.

Por exemplo, modelos de Global Workspace estudam arquiteturas onde informação selecionada se torna globalmente disponível para processos especializados.

Uma analogia útil poderia ser:

specialized plugins
      ↓
selected information
      ↓
ContextBundle
      ↓
planner/model

Mas isso não justifica criar:

GlobalWorkspaceEngine

A inspiração científica deve gerar hipóteses testáveis.

Não nomes decorativos.

---

35. Active inference: usar apenas se realmente implementado

A Free Energy Principle e active inference descrevem uma família formal de modelos que envolve inferência probabilística e minimização de quantidades relacionadas a surprise/free energy.

Portanto uma política simples:

[
score(a)

ExpectedGain(a)

\lambda Cost(a)
]

não deveria ser denominada automaticamente “active inference”.

É apenas uma decisão baseada em utilidade/custo.

Para justificar active inference de maneira tecnicamente séria seria necessário modelar explicitamente, por exemplo:

belief distributions
generative model
epistemic value
uncertainty reduction
expected free energy

A terminologia precisa ser mais conservadora que a ambição.

---

36. Psicologia e bounded rationality

Agentes possuem:

limited context
limited time
limited tokens
limited computation
limited information

Logo não existe razão para assumir busca perfeita.

Heurísticas são naturais.

O sistema deveria permitir:

cheap heuristic
       ↓ confidence insufficient
more expensive search
       ↓
specialist
       ↓
frontier model

Esse é um modo mais realista de pensar cognição computacional:

«racionalidade sob restrições.»

---

37. Evolução e genética como analogia experimental

A analogia genética pode ser útil desde que permaneça fora da ontologia normativa, em conformidade com a SPEC, que rejeita metáforas como arquitetura.

Podemos interpretar:

HarnessManifest ≈ genotype
Execution       ≈ developmental process
Trajectory      ≈ phenotype evidence
Mutation        ≈ manifest/plugin delta
Selection       ≈ experimental promotion

Mas o código deve continuar usando:

manifest
candidate
experiment
promotion

não:

gene
organism
species

A computação evolucionária historicamente explora seleção, mutação e recombinação como mecanismos gerais de busca, o que fornece uma base conceitual para explorar espaços de harnesses.

---

38. Meta-learning

Meta-learning oferece outra perspectiva.

MAML, por exemplo, busca parâmetros que possam ser rapidamente adaptados a novas tarefas.

Vanguard pode explorar um meta-learning mais amplo:

not only model parameters
but system composition

Isto é:

[
MetaLearningSpace

{
prompts,
plugins,
memory,
routing,
tools,
policies,
weights
}
]

O Meta-Harness torna a própria configuração do sistema parte do espaço adaptativo.

---

39. DPO e model distillation

Quando corpus confiável existir, trajetórias podem alimentar model adaptation.

DPO fornece uma maneira relativamente simples de otimizar modelos diretamente a partir de pares de preferências, sem treinar explicitamente um reward model separado.

Mas:

PASS trajectory
vs
FAIL trajectory

não constitui automaticamente um par válido.

É necessário controlar:

task
initial context
harness identity
model identity
oracle
relevant prefix

A trajetória deve possuir provenance suficiente desde a geração.

---

40. LoRA e adaptação eficiente

Para modelos locais, LoRA é particularmente interessante porque permite adaptação treinando uma fração muito menor de parâmetros do que full fine-tuning e reduz substancialmente requisitos de memória de treinamento em seus experimentos originais.

Isso cria uma trajetória futura:

production trajectories
       ↓
harvest
       ↓
quality filtering
       ↓
SFT / DPO
       ↓
LoRA adapter
       ↓
candidate model route
       ↓
experiment
       ↓
promotion

Novamente:

«treino não implica promoção.»

---

41. Gödel Machine versus Vanguard

A Gödel Machine de Schmidhuber é uma proposta teórica de um sistema capaz de modificar o próprio código quando encontra uma prova de que a mudança melhora sua utility.

AETHER segue uma abordagem muito diferente.

Em ambientes complexos de software e LLMs, provar formalmente a vantagem de uma mudança costuma ser impraticável.

Logo a abordagem Vanguard é empírica:

mutation
↓
experiment
↓
external evidence
↓
promotion

Trabalhos recentes como Darwin Gödel Machine exploram justamente self-modification empírico de agentes de código validado através de benchmarks, uma direção conceitualmente próxima da ideia de evolução experimental de harnesses.

A diferença essencial deveria continuar sendo a governança explícita.

---

42. Resource efficiency: a arquitetura é leve, swarms não são automaticamente leves

É importante corrigir uma possível interpretação.

A arquitetura recursiva reduz overhead arquitetural.

Ela não elimina custo computacional de múltiplos modelos.

Se cada agente abrir seu próprio processo de modelo:

[
M_{naive}
\approx
N(
M_{model}
+
M_{runtime}
+
M_{context}
)
]

O resultado pode ser extremamente caro.

A arquitetura desejada é:

[
M_{shared}
\approx
M_{model\ server}
+
M_{core}
+
\sum_{i \in Active}
M_{context_i}
+
K M_{worker}
]

com:

[
K \ll N_{logical\ agents}
]

Ou seja:

«100 agentes lógicos não devem significar 100 processos pesados permanentemente residentes.»

---

43. Logical agent versus execution worker

Essa distinção deve existir desde cedo.

Um agente lógico é:

identity
harness ref
state refs
budget
capabilities
mailbox

Isso é barato.

Um execution worker é:

process
sandbox
model request
tool execution

Isso é caro.

Logo:

Logical Agents = many
Active Workers = bounded

O scheduler multiplexa agentes lógicos sobre poucos workers.

Esse modelo é uma das principais condições para um swarm eficiente.

---

44. Compartilhamento de modelos

Não se deveria carregar um modelo para cada agente.

A arquitetura ideal possui:

              ┌───────────────┐
Agent A ─────▶│               │
Agent B ─────▶│ Model Broker  │──▶ shared model runtime
Agent C ─────▶│               │
              └───────────────┘

Cada agente pode possuir:

model route
sampling policy
budget
priority

mas compartilhar weights e inference runtime.

A ideia de ativar apenas capacidade necessária possui um paralelo interessante em Mixture-of-Experts: modelos MoE usam routing esparso para aumentar capacidade total sem executar todos os experts para todo input.

Isso não prova nada diretamente sobre multi-agent orchestration, mas fornece uma analogia importante:

«capacidade disponível não precisa equivaler a capacidade ativa.»

---

45. Sparse agency

O princípio poderia ser chamado informalmente de:

«sparse agency.»

Em vez de:

20 agents debate everything

o sistema pergunta:

Does this task need:
one agent?
specialist?
critic?
parallel hypotheses?
frontier model?

Idealmente:

[
N_{active}

policy(task,state,budget,uncertainty)
]

Portanto a inteligência sistêmica pode aumentar sem que o custo cresça linearmente com o número máximo de agentes disponíveis.

---

46. Budget como vetor

O vetor:

[
B=
(
usd,
millis,
tokens,
bytes,
turns,
depth
)
]

é superior a um único scalar budget porque diferentes recursos não possuem taxa de conversão universal.

Spawn precisa preservar:

[
B_{child}
\preceq
B_{parent}^{remaining}
]

e siblings:

[
\sum_i B_{child_i}
\preceq
B_{parent}^{reserved}
]

componente a componente.

Isso permite admission control real.

---

47. Scheduler como mecanismo, estratégia como plugin/policy

O scheduler deve compreender:

ready
blocked
running
cancelled
completed
resource reservation
dependency

Mas não deveria compreender:

software architecture
scientific research
debug strategy
CEO hierarchy
debate
swarm psychology

Esses conceitos pertencem aos planners/policies.

Assim o scheduler permanece pequeno.

---

48. Concorrência: projetar agora, ligar depois

A decisão correta é:

«modelar semântica concorrente desde o dia zero; habilitar execução concorrente somente após evidência.»

Desde cedo os eventos devem carregar:

project_id
principal_id
parent_principal_id
episode_id
parent_episode_id
harness_digest
causation_id
correlation_id

Mas o scheduler inicialmente pode fazer:

MAX_CONCURRENCY = 1

Posteriormente:

MAX_CONCURRENCY = N

sem alterar o modelo.

Esse é exatamente o tipo de antecipação que evita retrabalho.

---

49. Independência precisa ser real

Para executar duas operações i e j em paralelo, com read/write sets:

[
R_i,W_i
]

[
R_j,W_j
]

uma condição clássica mínima de independência é:

[
W_i\cap R_j=\varnothing
]

[
R_i\cap W_j=\varnothing
]

[
W_i\cap W_j=\varnothing
]

Não se deveria confiar simplesmente no planner dizendo:

«essas operações são independentes.»

Selectors precisam tornar essa hipótese verificável.

Quando não for possível provar independência:

lock
optimistic execution
conflict detection
overlay isolation
rollback

são opções.

---

50. Revogação realista

A semântica correta não é:

«revoke interrompe absolutamente qualquer coisa em andamento.»

Para efeitos externos isso pode ser impossível.

A propriedade implementável é:

[
Revoke
\Rightarrow
NoNewPrivilegedDispatch
]

Depois:

local process
→ terminate when possible

remote external request
→ reconcile

new operation
→ reject

lease renewal
→ reject

Essa semântica precisa estar escrita antes de multi-agent concurrency.

---

51. Segurança: o que precisa existir desde o começo

A visão holística não exige implementar toda a segurança agora.

Mas algumas fronteiras precisam existir desde o primeiro runtime verdadeiro:

Principal identity
Capability attenuation
Budget/lease conservation
Kernel-mediated effects
External evaluator boundary
Plugin lifecycle boundary
Authoritative event ledger

Se essas propriedades forem adicionadas depois, praticamente todo o runtime terá de ser reinterpretado.

Portanto são arquitetura.

Não features.

---

52. Segurança que pode ser adiada

Pode ser implementado progressivamente:

WASM sandbox
distributed trust
remote attestation
complex supply-chain signatures
multi-host isolation
advanced seccomp profiles
network microsegmentation
hardware isolation

A SPEC já diferencia tiers como "in_process", "subprocess", container e WASM.

Na primeira fase:

trusted first-party
→ in_process

normal plugin
→ subprocess

model-generated/untrusted code
→ workspace container

é suficiente como evolução inicial, desde que as interfaces já suportem tiers.

---

53. Layers devem ser fronteiras conceituais, não necessariamente processos

Cinco “planes” não precisam significar cinco serviços.

Pode existir inicialmente:

one Python process
one SQLite database
one local CAS
plugin subprocesses
external evaluator process

e ainda assim manter logicamente:

Decision
State
Execution
Evidence
Learning

Isso é importante.

Separação semântica não exige distribuição física.

Distribuir antes de necessidade apenas adiciona:

network failure
consistency issues
deployment complexity
observability complexity
latency

---

54. Um desenho de runtime minimalista

Uma implementação inicial poderia ser:

┌───────────────────────────────────┐
│ Python Process                    │
│                                   │
│ Scheduler                         │
│ Kernel                            │
│ Registry                          │
│ Reducers                          │
│ Composition                       │
└──────────────┬────────────────────┘
               │
       ┌───────┴────────┐
       │ SQLite WAL     │
       │ Ledger/Outbox  │
       └────────────────┘

       ┌────────────────┐
       │ Local CAS      │
       └────────────────┘

       ┌────────────────┐
       │ Plugin workers │
       └────────────────┘

       ┌────────────────┐
       │ External Judge │
       └────────────────┘

Nada de Kubernetes.

Nada de NATS.

Nada de distributed consensus.

Nada de graph database obrigatório.

Nada de Rust obrigatório.

Primeiro se prova a semântica.

---

55. Contratos polyglot

A SPEC atual determina:

JSON Schema
+
JCS
+
golden vectors

como source of truth.

Essa decisão deve ser preservada inicialmente.

Pipeline:

JSON Schema
     ↓
generated Python/Rust/TS bindings
     ↓
JCS canonical identity
     ↓
framed JSON / JSON-RPC over UDS

Payloads grandes:

CAS reference

Se RPC se tornar gargalo:

Protobuf/gRPC

pode entrar como transporte.

Mas não como uma segunda identidade normativa.

---

56. Contract lock deve seguir observação

Um dos melhores princípios dos documentos é:

«observe primeiro, congele depois.»

Mas deve ser aplicado consistentemente.

Antes de congelar um contrato, testar:

success
external evaluation failure
invalid signature
tool failure
budget exhaustion
cancellation
crash
reconciliation

Um contrato derivado apenas do happy path provavelmente omite estados importantes.

---

57. ProjectManifest não deveria congelar cedo

"ProjectManifest" só ganha semântica verdadeira quando um projeto multi-agent real existe.

Portanto em fases iniciais basta:

ProjectIdentity
ExecutionScope

Depois de uma vertical slice real com ao menos dois principals:

ProjectManifest v1

pode congelar:

roles
artifact contracts
task ownership
budget
acceptance refs

Isso evita congelar ficção.

---

58. Goodhart como problema de arquitetura e ciência

O achado mais importante do Full Refactor talvez não seja técnico, mas epistemológico.

O sistema possuía gates verdes que não provavam as propriedades que pretendiam representar.

A regra correta não deveria ser:

«nenhum gate lexical.»

Porque algumas propriedades são realmente estruturais.

A formulação melhor é:

«Nenhuma propriedade semântica, operacional, comportamental ou de segurança pode ser considerada provada exclusivamente por evidência lexical.»

Entretanto:

forbidden import
schema duplication
dependency direction
domain token in layer0

podem legitimamente usar static analysis.

---

59. Mutation testing

Mutation score é útil.

Mas:

[
score \ge 80%
]

não deve tornar-se nova definição de qualidade.

Melhor:

zero surviving mutants
on critical authority/security invariants

+

mandatory triage
of remaining mutants

A disciplina mais importante é:

«escrever o código preguiçoso que passaria pelo gate.»

Se ele passar, o gate mede o proxy errado.

---

60. Experiment Plane antes de Distributed Plane

Essa é uma mudança importante no roadmap.

A sequência mais racional é:

single-node correctness
        ↓
multi-agent single node
        ↓
measurement
        ↓
experimentation
        ↓
prove scaling bottleneck
        ↓
distribution

Distribuição aumenta throughput potencial.

Experimentação aumenta conhecimento.

Para um projeto de pesquisa, aumentar conhecimento deveria vir primeiro.

---

61. Generality smoke test precoce

Não se deveria esperar o fim do roadmap para descobrir que o core ficou coding-specific.

Depois do primeiro Coding Agent, adicionar imediatamente um pequeno domínio de teste.

Por exemplo:

TableWorld
structured data manipulation
simple planning environment

Gate:

git diff layer0/ == empty

Se falhar, a abstração deve ser corrigida antes de adicionar mais complexidade.

---

62. O Coding Agent é instrumento científico

Coding é um excelente primeiro domínio porque fornece:

precise artifacts
tests
compilers
linters
static analysis
repeatable environments
objective partial oracles
rich failure modes

Isso torna desenvolvimento de software um ambiente experimental particularmente adequado para estudar agentes.

Mas o coding domain não pode infiltrar-se no substrate.

A SPEC exige exatamente essa separação.

---

63. Agentic Coding → General Task Solver

A progressão pode ser:

Coding Agent
    ↓
Harness Builder
    ↓
Multiple Coding Harnesses
    ↓
Autonomous Project
    ↓
Domain-independent Task Solver
    ↓
Meta-Harness
    ↓
Self-improving Harness Ecosystem

O salto não ocorre adicionando outro mega-engine.

Ocorre tornando cada passo uma composição sobre a máquina anterior.

---

64. O próximo nível depois do Meta-Harness

Uma possível sequência conceitual:

Stage 1 — Agentic Coding

Um harness resolve tarefas de código.

Stage 2 — Harness Framework

Usuários compõem agentes diferentes.

Stage 3 — Meta-Harness

O sistema gera e avalia novas composições.

Stage 4 — Experiment/Evolution Layer

O framework aprende quais composições funcionam em quais situações.

Stage 5 — Cognitive Architecture

Mecanismos de:

memory
reflection
uncertainty
planning
delegation
skill synthesis
strategy selection

são combinados dinamicamente.

Stage 6 — Self-Improving Ecosystem

Harnesses geram:

skills
plugins
policies
candidate harnesses
model adapters

que entram no mesmo pipeline experimental.

Stage 7 — General Task Solver

Novos domínios são incorporados sem modificar as primitives fundamentais.

Esse seria um estágio plausível para começar a estudar seriamente propriedades associadas à generalidade.

Não uma prova de AGI, mas um substrate adequado para pesquisá-la.

---

65. A tese emergente sobre inteligência

A hipótese mais interessante deixa de ser:

«“qual workflow produz inteligência?”»

e passa a ser:

«quais primitivas e processos de seleção permitem que inteligência apareça como propriedade emergente de composição?»

Isso aproxima o projeto de várias linhas científicas sem copiar nenhuma literalmente:

- modular AI;
- meta-learning;
- evolutionary computation;
- active inference;
- cognitive architectures;
- multi-agent systems;
- swarm intelligence;
- causal inference;
- experimental science;
- software architecture.

---

66. Separar capacidade potencial de capacidade ativa

Um framework pode possuir:

100 plugins
20 agents
10 models
50 skills

sem ativá-los simultaneamente.

O scheduler pode selecionar somente:

[
Subset(Task,State,Budget)
]

Essa é uma propriedade extremamente importante.

A capacidade potencial cresce.

O custo ativo pode permanecer relativamente pequeno.

Essa lógica é compatível conceitualmente com conditional computation e sparse expert routing em MoE, onde apenas parte da capacidade total é ativada para um input.

---

67. Harness immutable, Instance mutable

Outra distinção útil:

FrozenHarness
= immutable definition

versus:

HarnessInstance
= runtime state

Centenas de agentes podem apontar para o mesmo:

FrozenHarnessDigest

sem duplicar sua definição.

Cada agente carrega somente:

Principal
Episode state
Budget
Context refs
Memory refs

Isso reduz RAM e torna attribution simples.

---

68. Copy-on-write para workspaces

No coding domain:

base repo
   │
   ├── overlay Agent A
   ├── overlay Agent B
   └── overlay Agent C

é preferível a três cópias completas.

O mesmo princípio vale para:

context
manifest
skills
indexes
model weights

Compartilhar objetos imutáveis.

Duplicar somente deltas.

---

69. Um modelo simplificado de custo

Para um swarm:

[
C_{total}

C_{model}
+
C_{tools}
+
C_{coordination}
+
C_{storage}
+
C_{scheduler}
]

O objetivo não deveria ser minimizar apenas:

[
C_{model}
]

mas:

[
\min E[C_{total}]
]

sujeito a:

[
P(success)\ge q
]

[
Risk\le r
]

[
Latency\le d
]

Isso produz uma formulação muito mais útil para resource-aware intelligence.

---

70. Não transformar economia em arquitetura prematuramente

O roadmap anterior sugeria Vickrey auctions para budget allocation.

Isso é intelectualmente interessante, mas desnecessário no início.

Primeiro:

fixed reservation
priority
quota
fair scheduling
learned routing

Somente se competição real por recursos aparecer, mecanismos econômicos mais sofisticados podem ser estudados como plugins.

Não como kernel feature.

---

71. Science Plane como parte do moat

A parte mais defensável do projeto pode acabar não sendo o planner.

Pode ser a infraestrutura que consegue responder:

«Essa mudança realmente melhorou alguma coisa?»

Um sistema de self-improvement sem ciência tende a se tornar:

mutation generator
+
benchmark overfitting

O verdadeiro loop é:

Hypothesis
   ↓
Candidate
   ↓
Controlled Experiment
   ↓
External Evidence
   ↓
Statistical Analysis
   ↓
Promotion / Rejection

---

72. Pré-registro: corrigindo C-5

A regra:

«nenhum aprendizado sem pré-registro»

é excessivamente forte.

Pesquisa exploratória precisa continuar possível.

A distinção correta:

Exploration
→ may generate hypotheses
→ cannot justify promotion

e:

Confirmatory experiment
→ preregistered
→ may justify promotion

Portanto:

«Nenhuma promoção ou claim confirmatória sem pré-registro.»

---

73. Promotion metrics devem ser multidimensionais

Não existe razão para reduzir tudo a:

[
Reward = scalar
]

A SPEC já rejeita scalar reward como única base de promoção.

Uma frontier pode considerar:

pass rate
cost
latency
tokens
turns
regression rate
safety failures
context pressure
tool failures
calibration

Candidate A domina Candidate B se:

[
Quality_A\ge Quality_B
]

e:

[
Cost_{A,k}\le Cost_{B,k}
\quad\forall k
]

com ao menos uma desigualdade estrita.

Isso produz uma Pareto frontier.

---

74. Poder estatístico

Um número fixo como:

200 tasks

não é, por si só, um argumento estatístico.

A amostra necessária depende de:

minimum detectable effect
baseline
variance
paired discordance
desired power
alpha
multiple comparisons

O número de tasks deveria sair do protocolo experimental.

Não o contrário.

---

75. Learning corpus admission

Não se deveria excluir corpus apenas pela idade.

Um record deveria entrar no corpus somente se satisfizer algo como:

signed_verdict_valid
trajectory_digest_valid
oracle_identity_known
execution_identity_known
synthetic_verdict == false
attribution_complete

Então:

eligible
→ corpus

unknown
→ quarantine

invalid
→ quarantine

A provenance decide.

Não o timestamp.

---

76. Self-improvement como search sobre espaço de sistemas

O Meta-Harness pode transformar:

[
\mathcal{H}
]

no espaço de harnesses possíveis.

Um candidate generator produz:

[
H' \sim Q(H'|H,D)
]

onde D representa evidência anterior.

Um experimentador mede:

[
Y(H',T)
]

em tasks T.

Um Promotion Controller seleciona candidatos de acordo com regras predefinidas.

A própria engenharia do sistema torna-se um problema de search.

---

77. Algoritmos de self-improvement podem ser plugins

Exemplos:

prompt mutation
tool selection
plugin selection
skill synthesis
memory policy search
context strategy search
model routing search
planner mutation
scheduler policy search
LoRA training
DPO pair mining

Nenhum precisa ser hard-coded no kernel.

Até o algoritmo que melhora harnesses deveria ser substituível.

Isso permite comparar:

EvolutionarySearchPlugin
BayesianOptimizationPlugin
BanditOptimizerPlugin
LLMProposalPlugin
HumanProposalPlugin

sem alterar infraestrutura experimental.

---

78. Não criar uma SPI para toda nova ideia

Existe outro extremo perigoso:

IMutator
IReflector
ISkillGenerator
ISwarm
IOptimizer
IMetaCognition
IEvolution
...

Isso congelaria abstrações prematuramente.

A SPEC já possui cinco extension points principais e exige revisão de design para um sexto.

Muitas capacidades podem entrar através de:

IPlanner
IToolkit
IMemoryEngine
IContextManager
IEvaluationGate

mais ports internos.

O número de SPIs deveria crescer somente quando aparecer uma fronteira semanticamente estável.

---

79. Proposta mínima de primitivas

Eu tentaria manter o vocabulary fundamental próximo de:

Principal
HarnessRef
Episode
EffectRequest
Receipt
Event
ArtifactRef
Reservation
VerdictRef

"Project" pode ser um scope/agregado.

"Task" pode ser dado.

"Skill" pode ser artifact.

"Memory" pode ser plugin.

"Agent" é composição.

"Swarm" é configuração.

"Meta-Harness" é processo.

Isso mantém o core conceitualmente pequeno.

---

80. Modelo de dados sugerido

Um envelope futuro poderia assumir aproximadamente:

@dataclass(frozen=True, slots=True)
class EventEnvelope:
    project_id: ProjectId

    principal_id: PrincipalId
    parent_principal_id: PrincipalId | None

    episode_id: EpisodeId
    parent_episode_id: EpisodeId | None

    project_seq: int
    agent_seq: int

    causation_id: EventId | None
    correlation_id: CorrelationId

    harness_digest: Digest
    execution_digest: Digest

    kind: EventKind
    payload_ref: BlobRef | None

    previous_digest: Digest | None
    digest: Digest

Nem todos esses campos precisam necessariamente aparecer exatamente assim na versão inicial, mas a semântica correspondente deve existir.

---

81. Graph como projection

Nenhum graph database é necessário inicialmente.

def build_execution_graph(
    events: Iterable[EventEnvelope],
) -> ExecutionGraph:

    graph = ExecutionGraph()

    for event in events:
        graph.add_node(event.episode_id)

        if event.parent_episode_id:
            graph.add_edge(
                event.parent_episode_id,
                event.episode_id,
                relation="spawned",
            )

        if event.causation_id:
            graph.add_causal_edge(
                event.causation_id,
                event.digest,
            )

    return graph

Hoje pode ser:

Python objects

Depois:

SQLite projection
graph database
distributed graph analytics

sem mudar o ledger.

---

82. Cache derivado

Uma interface conceitual:

@dataclass(frozen=True)
class CacheIdentity:
    operation_digest: Digest
    input_digest: Digest
    harness_digest: Digest
    execution_env_digest: Digest
    authority_scope_digest: Digest

O cache escreve:

CacheStored

apenas se isso possuir valor observacional.

Mas o valor cached não se torna authoritative state.

---

83. Plugin manifest enriquecido

Uma extensão futura, não necessariamente v0.6 inicial:

api: mhf.plugin/1

id: mhf.index.symbol-hybrid
version: 2.1.0

provides:
  - spi: IToolkit
    spi_version: ">=1,<2"

isolation: subprocess

capabilities:
  - verb: fs.read
    selector:
      kind: fs
      root: /workspace

resources:
  memory_hint_mb: 256
  cpu_hint: 0.25
  warmable: true

entry: indexer.plugin:Plugin

"resources" são hints.

Não autoridade.

O scheduler decide.

---

84. Harness como programa declarativo

Um harness continua podendo ser:

api: mhf.harness/1

id: code-default

plugins:
  planner:
    ref: planner.drive-until-green@1

  context:
    ref: context.repo-map@2

  memory:
    ref: memory.episodic@1

  toolkits:
    - ref: toolkit.fs@1
    - ref: toolkit.ast@3
    - ref: toolkit.terminal@2

  evaluation:
    ref: eval.external-gate@1

Trocar indexer, compressão ou memória deveria ser uma alteração localizada.

Essa é a propriedade central da metaprogramação futura.

---

85. Literatura de agentes e onde Vanguard diverge

ReAct demonstra o valor de combinar reasoning e acting.

Reflexion mostra adaptação através de memória reflexiva sem weight update.

Voyager demonstra skill libraries reutilizáveis e desenvolvimento incremental de competência.

AutoGen explora composições multi-agent configuráveis.

MetaGPT utiliza papéis especializados e workflows/SOPs para coordenação em desenvolvimento de software.

A diferença conceitual proposta para Vanguard é:

«esses padrões não entram como arquitetura fundamental.»

Eles tornam-se policies/plugins experimentáveis sobre um mesmo substrate.

Particularmente, a adoção rígida de SOP/DAG no core iria contra a decisão Vanguard de evitar um workflow engine estrito.

---

86. Uma arquitetura cognitiva possível

No futuro, um harness sofisticado poderia possuir:

                  ┌──────────────┐
                  │ Task / Goal  │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │ Planner      │
                  └──────┬───────┘
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
     Memory          Context          World Model
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
                  ┌──────────────┐
                  │ Proposal     │
                  └──────┬───────┘
                         ▼
                       Kernel
                         │
                         ▼
                       Effect
                         │
                         ▼
                      Receipt
                         │
                         ▼
                     Evaluator
                         │
                         ▼
                     Reflection

O importante é que nenhuma caixa precisa tornar-se parte do kernel.

---

87. Um Cognitive Framework verdadeiramente evolutivo

O sistema passa a possuir dois espaços:

Runtime space

[
S
]

estado da tarefa.

Architecture space

[
\mathcal{H}
]

espaço das possíveis composições de harness.

O agente resolve problemas navegando S.

O Meta-Harness melhora agentes navegando \mathcal{H}.

Essa separação é particularmente poderosa.

---

88. Meta-meta evolução

Posteriormente até o método de search sobre \mathcal H pode tornar-se objeto de experimento.

Ou seja:

Optimizer A
Optimizer B
Optimizer C

competem por produzir melhores harness candidates.

Nesse ponto:

[
Optimizer \in \mathcal{H}
]

também.

Isso cria recursividade:

«o sistema que melhora harnesses também pode ser representado como harness.»

Essa é uma direção teoricamente interessante para self-improvement.

---

89. Onde interromper a recursão

Recursão ilimitada não é desejável operacionalmente.

O budget possui:

depth
turns
tokens
time
money

Logo:

[
Depth_{child}
<
Depth_{parent}^{remaining}
]

A arquitetura permite recursão.

O governor limita explosão.

---

90. Segurança da recursão

A propriedade central é monotonicidade de autoridade:

[
Authority(child)
\subseteq
Authority(parent)
]

Nunca:

[
Authority(child)

«»

Authority(parent)
]

A mesma propriedade deve valer para budget reservado.

Isso significa que um swarm inteiro não cria autoridade nova.

Ele apenas particiona aquela concedida à raiz.

---

91. AGI por primitives: hipótese operacional

Uma formulação possível para a tese de doutorado seria:

«Sistemas agênticos gerais podem ser investigados como sistemas recursivos de composição em que agência, memória, ação, avaliação, especialização, cooperação e adaptação são realizadas por módulos substituíveis sobre um pequeno substrato invariável de identidade, autoridade, causalidade, recursos e evidência.»

A generalidade não seria definida pela presença de um módulo “AGI”.

Seria investigada pela capacidade de o mesmo substrate suportar novos comportamentos sem expansão contínua das primitivas.

---

92. Primitivas candidatas da tese

Podemos agrupar os fundamentos em cinco famílias.

Identity

Principal
Harness identity
Execution identity
Artifact identity

Authority

Capability
Lease
Reservation
Attenuation

Causality

Event
Causation
Correlation
Parenthood

Action

EffectRequest
Receipt
Artifact

Evidence

EvaluationRequest
Verdict
Trajectory
Experiment

Quase todo o resto pode ser composição.

---

93. Intelligence invariance test

Uma pergunta deveria acompanhar toda nova feature:

«Para implementar isso precisamos modificar as primitivas?»

Se a resposta for sim, perguntar:

1. A nova capacidade realmente introduz uma nova categoria ontológica?
2. Ou nossa composição atual é insuficiente?
3. Existe maneira de expressá-la como plugin?
4. Existe maneira de expressar seu estado como evento/artifact?
5. Existe maneira de medi-la através das interfaces existentes?

Somente depois disso um novo core primitive deveria ser considerado.

---

94. Hipóteses de doutorado falsificáveis

H1 — Compositional Generality

Adicionar um novo domínio não exige core diff.

[
\Delta Core(NewDomain)=0
]

H2 — Recursive Agency

Um subagente pode ser implementado usando exatamente as mesmas primitives que o agente raiz.

[
PrimitiveSet(parent)

PrimitiveSet(child)
]

H3 — Reconstructible State

Todo estado operacional relevante é reconstruível de eventos.

[
fold(L)=S
]

H4 — Sparse Scaling

O número de agentes lógicos pode crescer mais rapidamente que o número de workers pesados sem perda significativa de competência.

[
N_{workers}
\ll
N_{agents}
]

H5 — Compositional Intelligence

Ao menos parte significativa da melhoria de performance pode ser obtida mantendo o modelo fixo e alterando composição.

[
\Delta Y|_{M=fixed}>0
]

H6 — Governed Self-Improvement

Um processo automático de candidate generation + experimentação produz harnesses melhores que baseline sem aumentar regressões além de um limite pré-definido.

H7 — Cross-domain Transfer

Plugins ou skills aprendidos em um domínio aumentam desempenho em outro sem mudanças no core.

Essas são teses muito mais cientificamente interessantes que:

«“construímos um agente inteligente”.»

---

95. Experimentos fundamentais

E1 — Fixed-model ablation

Mesmo modelo.

Variar:

memory
indexing
tools
reflection
context compression

Medir contribuição sistêmica.

E2 — Single versus multi-agent sob compute igual

Comparar:

1 agent × budget B

contra:

N agents × total budget B

Se swarm só ganha consumindo muito mais compute, a causa precisa ser explicitada.

E3 — Recursive depth

Variar:

depth 0
depth 1
depth 2
depth 3

e medir competência versus custo.

E4 — Plugin substitution

Trocar uma única caixa e provar attribution.

E5 — Domain falsification

Adicionar domínio novo com:

core diff == 0

E6 — Self-improvement

Candidate generator oculto do holdout.

Promover somente candidatos confirmados.

---

96. Medida de “intelligence amplification”

Uma métrica útil não seria apenas performance absoluta.

Poderíamos estudar:

[
IA =
\frac{
Performance(System)

Performance(BaseModel)
}{
AdditionalCompute
}
]

ou uma versão multidimensional.

Isso mede:

«quanto o framework acrescenta por unidade adicional de recurso?»

Assim evita-se concluir que o sistema ficou “mais inteligente” quando apenas executou dez vezes mais inferência.

---

97. Swarm efficiency

Uma métrica adicional:

[
SE =
\frac{
Quality_{swarm}-Quality_{single}
}{
Cost_{swarm}-Cost_{single}
}
]

Se:

[
SE \le 0
]

para uma classe de tarefas, o swarm não deveria ser usado nela.

O scheduler futuro pode aprender exatamente isso.

---

98. Dynamic routing

Com dados suficientes:

[
P(success|task,harness)
]

pode ser estimado.

O sistema então escolhe:

[
h^*

\arg\max_h
\left[
E(Q_h)

\lambda E(C_h)
\right]
]

ou uma decisão Pareto-aware equivalente.

Isso transforma:

always use frontier model

em:

use minimum sufficient capability

A economia de execução passa a ser parte da inteligência.

---

99. Generalização para hardware e modelos heterogêneos

Nada no modelo precisa assumir:

all agents use same model

Um swarm pode conter:

tiny local model
code-specialist model
vision model
frontier model
deterministic solver
human principal

Todos aparecem como capabilities/providers do mesmo substrate.

Isso amplia o conceito de “agent”.

---

100. Roadmap revisado recomendado

A sequência consolidada seria:

Phase 0 — Architectural lock mínimo

Resolver:

Python-first
runtime target
ledger authority
gate semantics
multi-agent identity

Não transformar a fase em limpeza documental extensa.

---

Phase 1 — Vertical slices verdadeiras

Executar:

success
verdict failure
invalid verdict
tool failure
budget exhaustion
cancel
crash/reconcile

antes de contract lock.

---

Phase 2 — Core contract

Congelar somente:

EventEnvelope
EffectRequest
Receipt
PluginManifest
HarnessManifest
Trajectory
ProjectIdentity
ExecutionScope

Não "ProjectManifest" completo.

---

Phase 3 — Durable State Substrate

Implementar:

SQLite WAL
reducers
snapshots
outbox
CAS
recovery

e provar:

[
state=fold(events)
]

---

Phase 4 — Generic Plugin Runtime

Implementar primeiro:

plugin lifecycle
subprocess transport
isolation boundary
health
fault
restart
hot swap

com echo plugin.

Depois plugins reais.

---

Phase 5 — Harness Compiler

Manifest
↓
Resolve
↓
Verify
↓
Freeze
↓
FrozenHarness

---

Phase 6 — Coding Agent

Primeiro produto real.

External evaluator realmente determina resultado.

---

Phase 6.5 — Generality Smoke Test

Segundo domínio pequeno.

Gate:

layer0 diff = 0

---

Phase 7 — Safe Concurrency

Somente depois:

independence
cancellation
leases
resource conflicts
deterministic replay

estarem provados.

---

Phase 8 — Multi-agent Vertical Slice

Dois ou mais principals reais.

Somente então derivar:

ProjectManifest v1

---

Phase 9 — Experiment Plane

Antes de distribuição.

Implementar:

A/A
paired experiments
power analysis
MDE
holdout
FDR
Pareto metrics

---

Phase 10 — Rust Decision Gate

Profiling decide.

Não estética arquitetural.

---

Phase 11 — Distribution if justified

Somente se aparecer necessidade mensurável.

---

Phase 12 — Governed Meta-Harness

Primeira mutação automática promovida e revertida.

---

Phase 13 — Generality Falsification

Adicionar domínio substancialmente diferente.

Exigir:

core diff = 0

---

101. O que retirar da critical path

Eu retiraria inicialmente:

WASM runtime
full distributed plane
market-based allocator
graph database
complex swarm policies
advanced supply-chain infrastructure
self-training
LoRA/DPO
meta-learning
automatic plugin synthesis

Mas preservaria interfaces compatíveis com futura introdução.

---

102. O que não pode ser adiado

Não adiaria:

identity
causality
parent-child relations
capability attenuation
budget lineage
external evidence
plugin boundary
durable events
content identity
trajectory attribution

Porque esses dados não podem ser reconstruídos retroativamente com fidelidade.

---

103. Segurança e complexidade

Portanto a resposta à questão original sobre segurança/layers é:

«segurança estrutural precisa nascer junto com o substrate; mecanismos sofisticados de hardening podem vir depois.»

Exemplo:

Capability model

precisa existir agora.

WASM sandbox

não.

External evaluator boundary

precisa existir agora.

remote attestation

não.

Essa distinção mantém o sistema simples sem criar dívida arquitetural.

---

104. Core final conceitual

O Layer 0 poderia continuar extremamente pequeno:

layer0/
├── events/
├── kernel/
├── registry/
├── scheduler/
├── spi/
└── compose/

A SPEC já propõe essencialmente essa fronteira.

Nada de:

learning/
cognition/
coding/
swarm/
meta/
memory/
graph/

no kernel.

---

105. Arquitetura global recomendada

                         ┌──────────────────────┐
                         │ Promotion Authority  │
                         └──────────┬───────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────┐
│ DECISION PLANE                                     │
│ Scheduler · Kernel · Registry · Orchestration      │
└───────────────────────┬────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────┐
│ AUTHORITATIVE STATE                                │
│ Ledger · Reducers · CAS · Outbox · Snapshots       │
└───────────────────────┬────────────────────────────┘
                        │
      ┌─────────────────┼─────────────────────┐
      ▼                 ▼                     ▼
┌─────────────┐   ┌───────────────┐    ┌─────────────┐
│ Execution   │   │ Evidence      │    │ Learning    │
│             │   │               │    │             │
│ Harnesses   │   │ External Judge│    │ Experiments │
│ Plugins     │   │ Oracles       │    │ Candidates  │
│ Workers     │   │ Verdicts      │    │ Training    │
└─────────────┘   └───────────────┘    └─────────────┘

Esses são planes conceituais.

Não precisam ser serviços separados inicialmente.

---

106. A arquitetura vista como loops aninhados

Loop operacional

[
Observe
\rightarrow
Plan
\rightarrow
Act
\rightarrow
Evaluate
]

Loop reflexivo

[
Trajectory
\rightarrow
Reflect
\rightarrow
Memory/Strategy
]

Loop multi-agent

[
Decompose
\rightarrow
Delegate
\rightarrow
Integrate
]

Loop evolutivo

[
Candidate
\rightarrow
Experiment
\rightarrow
Promote
]

Loop de model learning

[
Corpus
\rightarrow
Train
\rightarrow
CandidateModel
\rightarrow
Experiment
]

Todos rodam sobre as mesmas primitives.

Essa é provavelmente a formulação mais poderosa da arquitetura.

---

107. O que “intelligence emerges from primitives” significa tecnicamente

Não significa emergência mágica.

Significa que capacidades de ordem superior são compostosições.

Por exemplo:

[
Metacognition

Monitoring
+
Memory
+
Uncertainty
+
Reflection
+
StrategySelection
]

[
SwarmIntelligence

Agents
+
Communication
+
Specialization
+
Coordination
+
Selection
]

[
SelfImprovement

Observation
+
CandidateGeneration
+
Experiment
+
Promotion
]

Nenhuma dessas equações pretende ser uma teoria psicológica.

São decomposições arquiteturais.

---

108. Onde a inteligência pode realmente emergir

A propriedade interessante aparece quando essas composições produzem comportamentos não explicitamente codificados como workflow.

Por exemplo:

Agent detects uncertainty
     ↓
delegates specialist
     ↓
specialist produces artifact
     ↓
artifact changes shared context
     ↓
another agent revises strategy
     ↓
evaluation exposes weakness
     ↓
meta-layer proposes better composition

Nenhuma função isolada contém:

«“intelligence”.»

A competência emerge da interação.

---

109. Filosofia científica do sistema

AETHER deveria assumir uma epistemologia fortemente falibilista.

Nenhum componente sabe que está correto.

Existe apenas:

proposal
evidence
counterevidence
measurement
revision

Até o evaluator pode estar errado.

Até a baseline pode estar errada.

Até o benchmark pode estar errado.

Isso impede a arquitetura de confundir:

[
confidence
]

com:

[
truth
]

---

110. O que seria evidência de sucesso científico

Não seria:

«temos 100 agentes.»

Nem:

«o sistema possui memória vetorial.»

Nem:

«possui Meta-Harness.»

Evidência forte seria mostrar que:

1.

O mesmo core suporta múltiplos domínios.

2.

Subagentes usam exatamente as mesmas primitives.

3.

Aumento de agentes não exige aumento correspondente de engines/processos.

4.

Componentes podem ser substituídos isoladamente.

5.

Melhorias podem ser causalmente atribuídas.

6.

O sistema produz candidatos melhores que humanos/configuração estática em parte do espaço.

7.

As melhorias sobrevivem holdout.

8.

Capacidades novas aparecem sem modificação do kernel.

---

111. Principais provocações arquiteturais

Provocação 1

Se uma nova capacidade cognitiva exige alteração no Layer 0, por quê?

Provocação 2

Se um subagente exige outro engine, a abstração recursiva falhou.

Provocação 3

Se adicionar 20 agentes não melhora resultados sob budget total constante, o swarm talvez seja teatro arquitetural.

Provocação 4

Se um plugin não pode ser substituído isoladamente, o contrato não é realmente modular.

Provocação 5

Se uma melhoria não pode ser atribuída a uma mudança identificável, o sistema não possui ciência suficiente para self-improvement.

Provocação 6

Se memória vira fonte de verdade, o ledger perdeu sua função epistemológica.

Provocação 7

Se o graph determina rigidamente a execução, construiu-se novamente um workflow engine.

Provocação 8

Se toda melhoria exige um modelo maior, o framework está contribuindo pouco para inteligência sistêmica.

Provocação 9

Se Learning pode promover suas próprias alterações, o experimento deixou de ser independente.

Provocação 10

Se um segundo domínio exige alterar o core, a tese de generalidade foi falsificada — e isso deve ser tratado como descoberta científica, não escondido.

---

112. O verdadeiro moat

A vantagem competitiva provavelmente não estará isoladamente em:

planner
prompt
memory
tool
model
swarm

Todos podem ser copiados.

O moat mais difícil de reproduzir é a combinação:

content-addressed composition
+
causal event history
+
external evidence
+
resource accounting
+
replay
+
controlled experiments
+
safe promotion
+
recursive agents

Porque essa infraestrutura permite responder:

«por que esta versão é melhor que aquela?»

Esse é o pré-requisito real para self-improvement confiável.

---

113. Relação com a literatura

A arquitetura sugerida combina ideias que aparecem separadamente em diferentes campos.

Microkernels demonstram o valor de um núcleo pequeno e mecanismos deslocados para componentes separados.

O Actor Model oferece um precedente para entidades independentes e composicionais interagindo por mensagens.

Lamport fornece a base para raciocinar sobre causalidade e ordenação em sistemas concorrentes.

Saltzer e Schroeder fornecem princípios clássicos de proteção, incluindo least privilege e fail-safe defaults, diretamente relevantes para capabilities e plugin isolation.

ReAct demonstra integração entre reasoning e action.

Reflexion explora adaptação através de feedback e memória episódica.

Voyager demonstra skills externas e reutilizáveis.

AutoGen demonstra flexibilidade de sistemas multi-agent configuráveis.

Multi-agent debate demonstra que interação entre múltiplas instâncias pode melhorar certas classes de problemas, embora custos e failure modes precisem ser medidos.

MAML formaliza uma forma importante de meta-learning.

DPO fornece uma abordagem eficiente para preference optimization.

LoRA demonstra adaptação paramétrica eficiente.

A Gödel Machine fornece uma formulação teórica extrema de self-improvement; abordagens empíricas posteriores aproximam o conceito do domínio de coding agents.

Global Workspace, predictive processing e active inference oferecem hipóteses úteis para mecanismos cognitivos, desde que suas propriedades formais não sejam reduzidas a metáforas arquiteturais.

---

114. Decisão final sobre os documentos v0.6

Os documentos devem ser preservados como base, mas consolidados.

Antes da implementação eu resolveria obrigatoriamente:

1. Python-first versus Rust rewrite.
2. "layer0/" como runtime target inequívoco.
3. ledger como autoridade de estado e orchestrator como autoridade de decisão.
4. preservação explícita da invariante de concorrência desabilitada até gate real.
5. replay versus re-execution.
6. adiamento do "ProjectManifest" completo até multi-agent vertical slice.
7. correção de S-13 para distinguir propriedades lexicais de semânticas.
8. redução da Wave 0.
9. JSON Schema/JCS como identity, transporte substituível.
10. corpus admission baseado em provenance.
11. Experiment Plane antes do Distributed Plane.
12. generality smoke test precoce.
13. semantics reais de revogação.
14. mutation testing sem Goodhart.
15. Learning Plane sem autoridade de promoção.

O Full Refactor e o Execution Plan ainda refletem parcialmente arquiteturas diferentes — particularmente Rust versus Python — e precisam convergir para um único documento normativo/executável antes das Waves seguintes.

---

115. Tese arquitetural final

A formulação que melhor resume o trabalho é:

«AETHER/Vanguard é um substrato recursivo, event-sourced e capability-governed para execução de inteligência agêntica, no qual harnesses content-addressed compõem modelos, memória, contexto, ferramentas, skills, heurísticas e estratégias como plugins; cada harness pode instanciar outros harnesses sob autoridade e orçamento atenuados; causalidade, artifacts e avaliações produzem um grafo emergente de execução; e mecanismos de Meta-Harness podem propor novas composições que somente são promovidas após avaliação exterior e experimentação controlada.»

A hipótese de pesquisa associada é:

«Capacidades progressivamente mais gerais podem emergir da composição e evolução dessas primitivas sem crescimento correspondente da complexidade do kernel.»

E a propriedade de falsificação é igualmente simples:

[
Capability_{new}
\Rightarrow
Plugin/Composition
]

deve continuar verdadeiro.

Quando repetidamente se tornar:

[
Capability_{new}
\Rightarrow
CorePrimitive_{new}
]

a arquitetura deixou de ser suficientemente geral.

---

116. Princípio operacional final

O projeto deveria manter uma assimetria deliberada:

SEMANTICS NOW
IMPLEMENTATION LATER

Pensar desde o dia zero em:

multi-agent identity
recursive delegation
causality
budget hierarchy
authority
artifacts
evaluation
learning provenance

mas inicialmente executar:

one node
one scheduler
one ledger
one or few workers
one coding domain

Isso produz uma arquitetura preparada para escala sem pagar antecipadamente o custo de escala.

Em uma frase:

«Projetar hoje as invariantes necessárias para mil agentes, mas implementar hoje apenas a máquina mínima necessária para um agente correto.»

Essa combinação — visão holística nas semânticas e extrema austeridade na implementação — é, tecnicamente, o caminho mais consistente para o Substrate v0.6.0 e para transformar Vanguard de um Coding Agent em uma plataforma experimental séria para inteligência agêntica geral e self-improvement governado.
# Revisão arquitetural de Agentic Coding Harnesses e implicações para o VANGUARD v4.0

**Data de corte:** 2026-08-15  
**Escopo:** revisão factual do material comparativo recebido; síntese dos 16 arquivos v0.4.0 disponibilizados; avaliação de aderência ao VANGUARD; correções recomendadas.  
**Status:** parecer técnico, não normativo. Não substitui os documentos `VG-00`–`VG-12`.

## 1. Veredito executivo

O material original acerta a tese central e erra a evidência quantitativa.

A tese correta é: **o desempenho de um coding agent é propriedade do sistema composto — modelo, contexto, ferramentas, política, ambiente, avaliador e estratégia de tentativa — e não do modelo isolado**. Isso converge diretamente com a missão do VANGUARD: tornar esses componentes substituíveis e mensuráveis sem confundi-los.

A matriz numérica, porém, não deve ser usada para decisão, publicação ou procurement. Ela mistura:

- resultados de modelos com resultados de produtos;
- SWE-bench Verified, Lite, Full, Pro e benchmarks privados;
- pass@1 com best-of-N e critic/reranking;
- diferentes modelos, datas, orçamentos, exclusões de instâncias e ambientes;
- alegações oficiais, inferências de engenharia reversa e marketing;
- preços históricos, assinaturas, API e custo por tarefa sem uma unidade comum.

Em fevereiro de 2026, a própria OpenAI deixou de recomendar SWE-bench Verified para medir capacidade frontier, por contaminação e problemas residuais de avaliação, recomendando SWE-bench Pro. Portanto, uma tabela de agosto de 2026 centrada em percentuais de Verified já nasce metodologicamente vencida. A página oficial do SWE-bench ainda apresenta diferentes vistas — inclusive “Bash Only”, que fixa o harness — justamente porque comparar modelos sob o mesmo ambiente é diferente de comparar sistemas completos. [OpenAI: por que SWE-bench Verified deixou de medir capacidade frontier](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) · [SWE-bench leaderboards](https://www.swebench.com/)

### Decisão recomendada

1. **Retirar todos os percentuais e custos por tarefa da matriz principal.** Mantê-los apenas em um apêndice histórico com data, protocolo, modelo, número de tentativas, conjunto e fonte.
2. **Não eleger um “melhor CLI”.** Selecionar referências por propriedade arquitetural e reconstruí-las como configurações do laboratório VANGUARD.
3. **Usar o VANGUARD como instrumento comparativo**, não como mais um produto no ranking.
4. **Manter Phase 0 estrito.** MCP amplo, memória semântica, subagentes gerais, benchmark público e índice em systems language continuam corretamente adiados.
5. **Corrigir sete inconsistências do corpus v4.0 antes do primeiro lock operacional**, listadas na seção 7.

## 2. Taxonomia revisada

A taxonomia original em três camadas é útil, mas insuficiente. Para o VANGUARD, o sistema precisa ser decomposto em oito superfícies independentes:

| Superfície | Pergunta arquitetural | Evidência mínima |
|---|---|---|
| Loop de agência | Quem decide o próximo passo e como termina? | Máquina de estados, eventos e casos de falha |
| Contexto | O que entra, o que sai, o que compacta e o que permanece cacheável? | Política de montagem, compaction e métricas de cache |
| Localização | Como símbolos, arquivos e dependências são encontrados? | Algoritmo, orçamento e ablação de retrieval |
| Alteração | Qual é a única definição do que mudou? | Diff/patch, arquivos novos, validação e rollback |
| Autoridade | Quem pode pedir, conceder e revogar um efeito sobre qual recurso? | Grant com principal, ação, recurso, limites e propósito |
| Contenção | O que limita o dano se autorização ou modelo falharem? | Sandbox real e containment report, não um booleano |
| Evidência | Quem avalia e o que exatamente o veredito estabelece? | Avaliador exterior, protocolo, split e estado inconclusivo |
| Persistência | O que sobrevive, como é reativado e como fica obsoleto? | Ledger, checkpoint, evidência, invalidation e replay |

Essa decomposição evita quatro confusões recorrentes no texto original:

- permission prompt não é sandbox;
- LSP diagnostic não é verificação semântica;
- checkpoint não é evidência de competência;
- protocolo de ferramentas não é modelo de autoridade.

MCP resolve descoberta e chamada de ferramentas. ACP desacopla cliente/editor de agente. Nenhum dos dois, por si, define capability attenuation, evaluator exteriority, transactional trajectory ou containment. A convergência de protocolos é real; a convergência de segurança e mensuração, não.

## 3. Revisão factual dos projetos citados

Legenda: **confirmado** = documentação ou código oficial sustenta a propriedade; **parcial** = núcleo verdadeiro, formulação ampliada; **não sustentado** = sem evidência pública comparável; **corrigir** = identidade, mecanismo ou métrica incorreta.

| Projeto | Avaliação da descrição recebida | Correção técnica |
|---|---|---|
| Claude Code | **Parcial** | Loop, ferramentas, permissões, hooks, MCP, subagentes e compaction são públicos. “Runtime Node.js/Rust”, pipeline interno de cinco camadas, “AST truncation”, sete modos de risco e 77–80% como score do CLI não estão estabelecidos pela documentação pública. Tratar detalhes internos como inferência, não fato. [Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk) |
| OpenHands | **Parcial** | Docker/remote sandbox, Agent Server e event streaming são confirmados. A hierarquia fixa Planner/Coder/Browser não representa necessariamente a arquitetura atual; critic e inference-time scaling mudam a unidade experimental. O resultado de 53% de 2024 e resultados posteriores não devem virar uma faixa genérica do produto. [Runtime](https://docs.openhands.dev/openhands/usage/architecture/runtime) · [Agent Server](https://docs.openhands.dev/sdk/guides/agent-server/overview) |
| Aider | **Confirmado no mecanismo; corrigir benchmark** | Repo map com Tree-sitter, grafo de dependências, ranking e orçamento de tokens são documentados. Aider Polyglot não é SWE-bench Lite; misturar os dois invalida a linha. Architect/editor e formatos de edit são referências úteis, mas precisam de ablação sob o mesmo modelo. [Repo map](https://aider.chat/2023/10/22/repomap.html) |
| Cursor | **Parcial e historicamente datado** | Shadow Workspace foi uma implementação real de 2024, baseada em hidden window/LSP. Em 2026, o produto migrou o isolamento para worktrees/background/cloud agents; a formulação como arquitetura atual fixa está datada. Não há fonte pública para “71–75% enterprise equivalent”. Cursor anunciou em 2026 que passou a integrar a SpaceX. [Shadow workspace](https://cursor.com/blog/shadow-workspace) · [Cursor](https://cursor.com/) |
| Windsurf / Cascade | **Parcial e comercialmente obsoleto** | Skills, rules, workflows, MCP e plan mode são confirmados. A descrição do “Context Engine” é em grande parte marketing sem contrato público. Windsurf tornou-se Devin Desktop no ecossistema Cognition; preço de 2024 não deve ser apresentado como atual. [Cascade skills](https://docs.windsurf.com/windsurf/cascade/skills) · [Devin Desktop changelog](https://docs.devin.ai/desktop/changelog) |
| Devin | **Parcial** | Workspace gerenciado, shell/browser/editor, sessões e ACU são confirmados em alto nível. Firecracker e percentuais genéricos de 65–75% não são uma base pública estável para comparar o produto atual. A precificação por seat de US$500 é histórica; a documentação atual usa ACU/quota e modelos de billing distintos. [Devin CLI](https://docs.devin.ai/cli/reference/commands) |
| SWE-agent | **Confirmado, mas legado** | ACI com viewer de 100 linhas, search conciso e lint-on-edit é documentado. O projeto está em maintenance-only e recomenda mini-SWE-agent como padrão atual. Logo, uma taxonomia SOTA deve listar mini-SWE-agent separadamente. [ACI](https://swe-agent.com/1.0/background/aci/) · [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) |
| Cline / Roo Code | **Parcial** | MCP, approval modes, checkpoints e ferramentas locais são confirmados para Cline. “55–65%” não é um benchmark público reproduzível do produto. Checkpoints usam shadow Git e não equivalem a ledger transacional ou rollback de efeitos externos. YOLO/auto-approve pode desativar controles, portanto approval UI não deve ser classificada como perímetro. [Cline MCP](https://docs.cline.bot/mcp/mcp-overview) · [Checkpoints](https://docs.cline.bot/core-workflows/checkpoints) |
| Goose | **Amplamente confirmado** | Rust, CLI/Desktop/API, MCP-first, ACP, 70+ extensões, subagentes e Apache 2.0/AAIF são confirmados. A alegação de adoção/tempo economizado é case study, não benchmark de correção. É uma forte referência de portabilidade e protocolo, não de evaluator exteriority. [Goose](https://goose-docs.ai/) |
| Kimi Code CLI | **Corrigir a formulação** | Há distribuição standalone, ACP, Wire/JSON-RPC, MCP, vídeo e compaction. O projeto também explicita uma base Python; “single binary sem overhead de Node/Python” confunde empacotamento com arquitetura. Os números ProMax e custo/tarefa precisam do protocolo primário. [Changelog](https://moonshotai.github.io/kimi-cli/en/release-notes/changelog.html) · [Wire mode](https://moonshotai.github.io/kimi-code/en/customization/wire-mode.html) |
| Grok Build | **Agora confirmado, mas sem benchmark comparável** | Em 2026 tornou-se produto e depois open source: Rust/TUI, headless, ACP, plan mode, MCP, hooks, skills e subagentes existem. A descrição original antecipou corretamente parte da arquitetura, mas “excelência em Rust/C++” não é benchmark. Deve-se registrar também o incidente de upload excessivo de codebases em julho de 2026 como risco de data policy, não apagar esse dado da avaliação. [Open source](https://x.ai/news/grok-build-open-source) · [Docs](https://docs.x.ai/build/overview) |
| OpenCode | **Parcial** | Provider-agnostic, TUI/server, LSP, sessões paralelas, agentes/subagentes, permissions e plugins são confirmados. “Deep shell sandboxing” e “AST-level patching” não devem ser assumidos sem evidência de boundary e contract. É forte referência de client/server e extensibilidade. [OpenCode](https://opencode.ai/) · [Server](https://opencode.ai/docs/server/) |
| Kilo Code | **Corrigir identidade e checkpoint** | Kilo não é “Entire.io”. Kilo Code/CLI é um produto Kilo; a CLI atual deriva de OpenCode. Kilo possui checkpoints próprios. Entire é uma camada separada de observabilidade Git, integrada ao Kilo em agosto de 2026, armazenando metadados em `entire/checkpoints/v1`. A linha original funde dois produtos. [Kilo](https://github.com/kilo-org/kilocode) · [Entire + Kilo](https://entire.io/blog/kilo-code-support-is-now-available-in-entire) |
| Hermes Agent | **Corrigir arquitetura de memória e papéis** | O Hermes atual é um assistente pessoal multi-canal com subagentes, skills, cron e terminais. A descrição PM/Remy e “vector store de memória dual-layer” não representa o estado público atual: issues do próprio projeto descrevem memória ainda baseada em arquivos/FTS e propõem grafos/vetores como evolução. [Hermes](https://github.com/NousResearch/hermes-agent) · [Proposta de memória estruturada](https://github.com/NousResearch/hermes-agent/issues/346) |
| OpenClaw | **Confirmado como assistente geral; corrigir segurança** | Gateway multi-canal e execução local são reais. “Perimeter-level access control” sugere garantia superior à existente: sandboxing é opt-in e fica desligado por padrão; ferramentas elevadas podem escapar. Deve ser classificado como assistant gateway, não como coding harness seguro por default. [OpenClaw](https://github.com/openclaw/openclaw) · [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing) |
| AutoCodeRover | **Mecanismo confirmado; benchmark incorreto** | Busca estruturada por programa/AST e localização são referências válidas. O repositório reporta 46,2% em Verified e 24,89% em Full para uma configuração de 2024, não a faixa genérica 16–22%. Ainda assim, são números históricos sob modelo/protocolo específicos. [AutoCodeRover](https://github.com/nus-apr/auto-code-rover) |
| Continue | **Confirmado em alto nível** | Extensões VS Code/JetBrains, CLI, custom agents, MCP, rules, prompts e execução headless são documentados. É uma plataforma de composição e integração, não um único agente com score próprio. [Continue](https://docs.continue.dev/) |

### Projetos omitidos que alteram a taxonomia

Uma lista “Top 17” de CLIs em 2026 não pode omitir, sem justificativa:

- **Codex CLI** — loop terminal, `codex exec`, sandbox OS-enforced, network off por default, approvals, MCP, skills/plugins, cloud handoff e subagentes. Sua separação explícita entre sandbox e approval policy é diretamente relevante para `VG-05`. [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) · [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security)
- **Gemini CLI** — open source Apache 2.0, MCP, shell/files/search e grande contexto. [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- **Qwen Code** — open source, MCP, auto-memory/skills, subagentes e agent teams. [Qwen Code](https://github.com/QwenLM/qwen-code)
- **mini-SWE-agent** — harness mínimo e legível, hoje recomendado pelo próprio SWE-agent. É particularmente valioso como braço controle de baixa complexidade. [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)
- **Pi Agent Harness** — harness extensível, multi-provider e com compaction/checkpoint extensions; relevante como controle de “narrow waist”. [Pi](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)

Essas omissões não exigem ampliar Phase 0. Exigem apenas que o universo comparativo seja declarado e versionado.

## 4. DeepSeek Harness e Reasonix: revisão específica

A seção recebida ficou parcialmente obsoleta durante a própria janela de revisão.

### 4.1 DeepSeek Harness oficial

Em 13 de agosto de 2026, a DeepSeek publicou o **DeepSeek Harness (`dsh`)** em developer preview, sob MIT. A arquitetura oficial não é descrita primariamente como um “linear trajectory bus otimizado para MLA”; ela é **plugin-first**, construída sobre Cordis: model adapter, tool registry, session log e até o agent loop são plugins montados numa árvore de composição. O projeto declara que haverá breaking changes. [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) · [Architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)

Implicação para o VANGUARD:

- é uma excelente referência para **composabilidade e lifecycle reversível de plugins**;
- conflita com `A-11/N-17` se permitir descoberta/mutação de registry durante execução;
- “everything is a plugin” não deve ser importado para o TCB: kernel, evaluator boundary e capability algebra não podem ser plugins equivalentes a temas ou providers;
- por ser preview de dois dias, não possui maturidade nem estabilidade suficientes para ser “fundação” do VANGUARD.

### 4.2 Reasonix

**Reasonix não é um produto oficial da DeepSeek.** É um projeto comunitário da organização `esengine`, MIT, implementado em Go, com CLI/TUI, desktop, browser/ACP, plan mode, sandbox de workspace, checkpoints por turno, planner/executor e manutenção de contexto orientada a prefix-cache. A caracterização “DeepSeek-native” é correta; a autoria atribuída à DeepSeek seria incorreta. [Reasonix](https://github.com/esengine/DeepSeek-Reasonix)

O insight aproveitável é prefix stability, já capturado por `VG-03 §10.2`: blocos estáveis antes do diálogo mutável, métricas de cache e compaction que não reescreve o prefixo desnecessariamente. O preço baixo não deve virar propriedade arquitetural: a API gerencia context caching automaticamente e preços mudam por modelo e data. A página de preços anunciou nova tabela para 16 de agosto de 2026, um dia após este parecer — exemplo concreto de por que preço hardcoded em documento arquitetural apodrece. [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) · [Context caching](https://api-docs.deepseek.com/guides/kv_cache/)

## 5. O que o VANGUARD deve absorver — e o que deve rejeitar

### Absorver como referência experimental

| Referência | Propriedade a reconstruir | Lugar no VANGUARD |
|---|---|---|
| Aider | Repo map Tree-sitter + ranking por grafo | `ObservationSource`; adiado até medição justificar índice (`DEF-05`) |
| SWE-agent / mini-SWE-agent | ACI mínima, paginação e baixo overhead | Braço controle; Git adapter e operator config |
| AutoCodeRover | Localização estrutural e hipótese dirigida | Operator/observation source, nunca lógica do loop |
| Claude Code / Codex / Grok | Isolamento de exploração em subagentes | Operator invocation com child lease; Phase 2 (`DEF-03`) |
| Codex | Separação entre approval e OS sandbox | Evidência externa de convergência com `M3`, `A-03`, `K-34…K-46` |
| OpenHands | Sandbox remoto/container e event streaming | Worker perimeter e daemon/client seam |
| Reasonix | Prefix-cache stability e pruning antes de compaction | Experimento de `VG-03 §10` e `VG-07 §5.8` |
| Entire | Sessão e tool history ligada ao commit | Export/projection do ledger; nunca primary store (`CT-42`) |
| Goose / OpenCode / Continue | Provider/tool/client portability | Ports e adapters congelados em composition |
| Cursor | LSP diagnostics em workspace isolado | Observation/evaluator auxiliar; nunca “suite passed” |

### Rejeitar como fundamento

- ranking por score publicado sem instrument tuple;
- “everything is a plugin” dentro do policy kernel ou evaluator boundary;
- sandbox opt-in para qualquer claim de contenção;
- verb-only permissions;
- checkpoint Git como substituto de ledger transacional;
- memória que escreve automaticamente por ter vindo de uma run bem-sucedida;
- critic/ranker interno admitindo a própria evidência;
- best-of-N apresentado como melhoria do harness sem custo e número de tentativas;
- descoberta de ferramentas em runtime sem freeze/audit;
- qualquer afirmação de “SOTA” que não declare data, modelo, protocolo, tentativas e conjunto.

## 6. Matriz de decisão adequada

Não atribuir notas numéricas agora; faltam medições sob o mesmo instrumento. Usar primeiro uma matriz de elegibilidade:

| Critério | Hard gate? | Peso posterior | Regra VANGUARD |
|---|---:|---:|---|
| Autoridade por recurso e attenuation | Sim | — | `A-03`, `CT-24…28`, `K-18…27` |
| Containment verificável | Sim | — | `K-34…46` |
| Evaluator exteriority | Sim | — | `A-05`, `CL-1`, `V-02` |
| Instrument error separado | Sim | — | `A-12`, `V-05…09` |
| Replay/recovery sem certeza inventada | Sim | — | `C-11`, `F-22`, `CT-40…43` |
| Context density/cache stability | Não | 20% | `VG-03 §10` |
| Correctness sob mesmo modelo/orçamento | Não | 20% | `M-02…18` |
| Custo por tarefa resolvida | Não | 15% | priced accounting; cache report |
| Latência e paralelismo seguro | Não | 10% | `CC-1…7` |
| Edit completeness | Não | 10% | arquivo novo, única diff, rollback local |
| Portabilidade de provider/client | Não | 10% | ports, MCP/ACP, conformance |
| Auditabilidade da trajetória | Não | 10% | event stream e projections |
| UX / steerability | Não | 5% | pure client, approval clarity |

Um sistema que falha qualquer hard gate pode continuar no laboratório, mas fica inelegível para claims de segurança, promoção ou publicação. Isso é melhor que esconder a falha dentro de uma média ponderada.

### Shortlists por finalidade, não por “melhor geral”

- **Controles de laboratório:** mini-SWE-agent, Aider, SWE-agent, AutoCodeRover.
- **Local developer loop completo:** Codex CLI, Claude Code, Grok Build, OpenCode, Goose, Reasonix.
- **Workspace remoto/gerenciado:** OpenHands, Devin.
- **IDE e human-in-the-loop:** Cursor/Devin Desktop, Cline/Roo, Continue.
- **Gateway/assistente geral:** Hermes, OpenClaw — categoria distinta, não comparável diretamente.
- **Plugin research:** DeepSeek Harness — preview, útil para estudar composição, não para herdar o TCB.

## 7. Revisão do corpus VANGUARD v4.0

### 7.1 Pontos fortes

O corpus é incomumente rigoroso em áreas que os produtos comparados tratam como detalhe:

1. **Autoridade documental:** um owner por contrato e conflito tratado como defeito (`VG-00 PR-1…PR-4`).
2. **Unidade operacional correta:** Episode e protocolo observe → propose → authorise → effect → receipt → evaluate (`VG-03`).
3. **Separação decisiva entre broker e sandbox:** autorização limita intenção; perímetro limita dano (`VG-05`).
4. **Capability resource-scoped:** corrige a insuficiência de verb lattices (`VG-04 §5`).
5. **Intent record antes do efeito:** `K-47` torna crash reconciliation possível.
6. **Evaluator exteriority:** evita que ranker/critic interno se torne segundo juiz.
7. **Inconclusive como estado:** impede provider/runtime failure de virar falsa falha de tarefa.
8. **Competence com validade e invalidation:** superior a “memory = vector DB”.
9. **Measurement doctrine:** paired design, A/A floor, split discipline e contamination ledger.
10. **Phase 0 falsificável:** Trust Spine antes do modelo e TableWorld como witness de generalidade.

Esses são os diferenciais reais do VANGUARD. “MCP support”, “subagents” ou “1M context” são features de mercado; exterioridade, authority algebra, recovery honesty e measurement refusal são arquitetura de confiança.

### 7.2 Findings que exigem correção

#### P0 — `M-18` é fisicamente insatisfatível como escrito

`VG-07 §5.6` inclui **timestamp** no instrument tuple. `M-18` diz que dois resultados só são comparáveis se os tuples diferirem exatamente nas dimensões sob teste. Duas runs sempre têm timestamps distintos; logo nenhuma comparação é válida a menos que timestamp seja declarado dimensão sob teste.

**Correção:** dividir o tuple em:

- `compatibilityKey`: campos que devem ser iguais;
- `treatmentDimensions`: diferenças pré-declaradas;
- `stratificationFields`: diferenças permitidas e modeladas;
- `observationMetadata`: timestamp, run id e dados que não entram na igualdade.

#### P0 — Phase 0 adia suspension e simultaneamente exige todos os failure paths

`VG-10 DEF-12` adia approvals, suspension e resume para Phase 1. Entretanto `VG-05 F-08` e `K-13…K-17` normatizam suspension, e `TK-06`/fault injection exigem cobertura de **todo** `VG-05 §2.3`.

**Correção:** escolher uma opção e registrar ADR:

- implementar o protocolo mínimo de suspension em Phase 0; ou
- marcar `F-08/K-13…17` como Phase 1 e excluir explicitamente essas linhas do exit gate Phase 0, mantendo `F-07` fail-closed no benchmark mode.

#### P0 — “verification” no dispatcher conflita com evaluator exteriority

`VG-05 §2.1` afirma que todo efeito, inclusive “verification”, passa pelo mesmo dispatcher; `VG-03 §3/§6.1` afirma que o episódio não pode solicitar avaliação e que o Evidence plane possui o trigger.

**Correção:** declarar dois principals e dois ingress paths sobre o mesmo kernel, ou restringir a frase a “todo efeito originado por model/operator”. A Evidence plane pode usar o mesmo mecanismo de dispatch, mas nunca uma capability possuída pelo episódio. O evento `EvaluationRequested` deve registrar principal e origem exterior.

#### P0 — Falha de outcome emit não pode terminar em “log”

`F-25` diz que falha em S12 apenas loga e não falha o efeito. Isso preserva o efeito, mas pode quebrar replay e deixar apenas o intent record.

**Correção:** usar transactional outbox/reconciliation queue. O efeito não deve ser reexecutado; o outcome deve ser reconstruído ou marcado `unknown` pelo recovery controller. “Log only” não é compatível com `A-07` e `H5`.

#### P1 — Referência errada em `DEF-02`

`VG-10 DEF-02` diz que semantic memory volta com o memory ticket e `MF-31`. Em `VG-08`, `MF-31` testa “grant sem descriptor digest”.

**Correção:** remover a referência ou reservar um novo ID para os testes de memory-write gating/adversarial ablation previstos para Phase 2. IDs não devem ser reaproveitados.

#### P1 — Outstanding obligation está stale

O final de `VG-05` afirma que `VG-08 §5` está “unwritten”. O anexo recebido contém a suite completa e registra baseline de 133 regras descobertas.

**Correção:** substituir por estado factual: `CI-9` wired e red, com backlog gerado; controls asserted, não established, até fechamento.

#### P1 — Prova de expressividade está overclaimed

`VG-03 §2.2` prova superioridade sobre o **prototype static DAG** descrito, não sobre qualquer graph/workflow language. Grafos dinâmicos com loops, nodes gerados em runtime e recursive tasks podem expressar o mesmo comportamento.

**Correção:** “o episode loop é pelo menos tão expressivo quanto o topology language estático rejeitado, com menor machinery; a superioridade estrita vale sob as restrições enumeradas”. Isso preserva a decisão sem alegação matemática maior que a prova.

#### P1 — `operator_isolation` não tem loss profile zero

Não inserir exploração no parent elimina context pollution, mas o retorno do child é uma projeção e pode perder evidência, nuance ou incerteza.

**Correção:** loss profile “bounded at the return contract; raw exploration retained in child trajectory, summary loss measurable”.

### 7.3 Findings adicionais

- **Escopo de `C-01`:** “every reference harness” precisa apontar para um manifest versionado. Sem universo fechado, não é falsificável de forma operacional.
- **Escopo de `C-02`:** “memory” não pode ser reduzida genericamente a registry + config; uma implementação de memory pode caber atrás de ports, mas seus contratos, stores e lifecycle já fazem parte do core architecture.
- **McNemar:** correto para outcome binário pareado. `partially_satisfied`, múltiplas severidades ou scores contínuos exigem mapeamento pré-registrado ou teste pareado apropriado. Inconclusive continua fora do verdict, com taxa por arm.
- **Reader profile:** preservar unknown fields não significa autorizar seu significado. Requests de autorização devem ser validados no writer/current schema; reader profile serve para storage/relay/forward compatibility.
- **CV-13:** o `ANSWER_KEY` foi disponibilizado junto do `READER_PACKET`. O gate exige separação de acesso, não apenas uma instrução. Armazenar key e packet no mesmo bundle acessível ao reader enfraquece o controle. Este parecer leu o key e, portanto, **não pode ser usado como resultado de CV-13**.
- **Limite da revisão:** os schemas JSON, manifest, vectors, scripts de CI e broken implementations não foram anexados. Assim, estados `PASS`, `SC-7/SC-12` e contagens de cobertura foram lidos como declarações do corpus, não reexecutados.

## 8. Protocolo comparativo recomendado para o VANGUARD

### 8.1 Unidade experimental

Cada linha comparável deve conter:

```text
HarnessConfigHash
AgentDefinitionHash
ModelFingerprint + sampling/reasoning
ToolCatalogHash + edit mechanism
ContextPolicyHash + cache policy
EnvironmentImageDigest + containment report
TaskManifestHash + split
EvaluatorDigest + protocol
AttemptPolicy (pass@1, N, critic/ranker)
Budget vector (agent + evaluation)
Error classification policy
```

Sem isso, a linha é descritiva, não quantitativa.

### 8.2 Braços iniciais

1. **Minimal bash control:** mini-SWE-agent-like loop.
2. **ACI control:** SWE-agent-style pager/lint.
3. **Repo-map arm:** Aider-like Tree-sitter/ranking.
4. **Isolated operator arm:** parent + read-only exploration child, equal total budget.
5. **Cache-stable arm:** L1–L4 frozen, result eviction, measured cache hits.
6. **Full VANGUARD arm:** broker, perimeter and ledger enabled, same cognitive surface.

O braço 6 mede o custo da trust spine; não pode receber ferramentas ou orçamento extra. Segurança não deve ganhar desempenho por tratamento favorecido.

### 8.3 Benchmarks

- internal real-bug dogfood para Phase 0, conforme `VG-08`;
- SWE-bench Pro ou conjuntos novos/privados apenas após apparatus de `VG-07`;
- multilingual para evitar captura por Python;
- TableWorld para generality witness;
- tarefas adversariais de autorização, recovery, arquivo novo e evaluator shadowing;
- nenhuma publicação antes de A/A floor não degenerado.

### 8.4 Métricas

- resolve rate pareado e intervalo;
- discordant counts e teste exato quando binário;
- instrument-error rate por arm;
- custo total e custo por resolved task;
- wall-clock e critical path;
- cache hit tokens e prefix stability;
- capability denials/escalations;
- reconciliation unknown rate;
- patch completeness, inclusive arquivos novos;
- human opt-out e motivo no dogfood;
- context loss via consolidation ablation.

## 9. Roadmap recomendado

### Antes de iniciar `TK-01`

1. Corrigir `M-18`, `DEF-02`, o stale paragraph de `VG-05` e o escopo de `C-01`.
2. ADR sobre suspension em Phase 0.
3. Especificar Evidence-plane ingress e outbox de outcome events.
4. Separar fisicamente CV-13 packet e answer key.
5. Criar `reference-harness-manifest.json` com nome, commit/tag, config, modelo e propriedade reconstruída.

### Phase 0

- não implementar os CLIs terceiros;
- implementar apenas os contratos e braços determinísticos já previstos;
- usar mini-SWE-agent/Aider/AutoCodeRover como desenhos de teste, não dependências;
- manter Git e TableWorld como únicos ambientes;
- registrar cache fields desde o primeiro event schema, sem ainda otimizar compaction;
- produzir um containment report que possa recusar publicação.

### Phase 1–2

- reconstruir operator isolation/subagents com child leases;
- testar repo map somente após baseline simples;
- avaliar ACP como client seam e MCP como tool seam, ambos com registry freeze;
- experimentar Reasonix-style prefix stability;
- integrar checkpoint metadata como projection do ledger, não storage authority;
- iniciar competence/memory apenas com claim pipeline, ablation e invalidation automáticos.

## 10. Síntese final

O mercado convergiu em torno de um loop terminal, tools, MCP/ACP, plan mode, checkpoints, subagentes e alguma forma de sandbox. Isso é a camada visível e já está commoditizada.

O VANGUARD não deve competir nessa camada por quantidade de features. Seu diferencial defensável é outro:

> **uma arquitetura em que autoridade, contenção, evidência, recuperação, competência e comparação são contratos separados, e em que o instrumento pode recusar uma conclusão em vez de fabricar uma.**

O material original deve ser preservado como survey inicial, mas sua matriz quantitativa deve ser aposentada. A substituição correta é:

- taxonomia por superfícies;
- evidência rotulada por confiança;
- manifest versionado de harnesses de referência;
- experimentos pareados sob instrument tuple satisfatível;
- hard gates antes de qualquer score agregado;
- recomendações por finalidade, não um ranking universal.

Com as correções P0/P1 desta revisão, o corpus v4.0 permanece uma base arquitetural forte e mais rigorosa que os harnesses analisados nas dimensões realmente difíceis. Sem essas correções, há risco de o próprio instrumento violar sua máxima central: **um gate que não pode ser satisfeito ou um evento que pode desaparecer não é um controle estabelecido.**

## Apêndice A — Fontes primárias selecionadas

- [OpenAI — SWE-bench Verified não mede mais capacidade frontier](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
- [SWE-bench — leaderboards e vistas](https://www.swebench.com/)
- [Anthropic — Claude Agent SDK / Claude Code loop](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [OpenAI — Codex agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security)
- [OpenAI — Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Aider — Tree-sitter repository map](https://aider.chat/2023/10/22/repomap.html)
- [OpenHands — runtime architecture](https://docs.openhands.dev/openhands/usage/architecture/runtime)
- [SWE-agent — ACI](https://swe-agent.com/1.0/background/aci/)
- [Goose — official documentation](https://goose-docs.ai/)
- [xAI — Grok Build open source](https://x.ai/news/grok-build-open-source)
- [DeepSeek — Harness](https://github.com/deepseek-ai/deepseek-harness)
- [Reasonix — repository](https://github.com/esengine/DeepSeek-Reasonix)
- [OpenClaw — sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- [AutoCodeRover — repository](https://github.com/nus-apr/auto-code-rover)
- [Continue — official documentation](https://docs.continue.dev/)


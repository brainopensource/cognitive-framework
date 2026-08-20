> **Non-normative.** Advisory evidence only. Law is `docs/SPEC.md` + `docs/05_adr/0069`–`0074` + annexes.
> Operational sequence: `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`. Do not cite this file as a requirement.
> In particular, do not treat “replatform into `layer0/`” as the v0.6 destination.

# Vanguard Substrate 0.6.0 — Full Refactor Report (v3)

**Documento:** `Vanguard-substrate-060-full-refactor-v3.md`
**Status:** Relatório técnico final e decisão de arquitetura
**Supersede:** `vanguard-repo-review.md`, `vanguard-estrategia-evolucao.md` (v1), `vanguard-estrategia-evolucao-v2.md`, `vanguard-roadmap-waves.md`
**Incorpora:** `aether-v1-roadmap-waves.md` (plano do Tech Lead) e a decisão executiva de replatformização
**Base de evidência:** commit `99d1e0b`, verificação por execução (1106 testes, 10 gates de CI) e leitura de fonte
**Data:** 2026-08-19

---

## Sumário executivo

**Decisão: replatformizar para AETHER v1 (Substrate 0.6.0), com um ajuste de sequenciamento.**

O runtime Python atual (`vanguard/packages/`, 21.296 LOC) torna-se **implementação de referência e oráculo de conformidade**. O `layer0/` (4.556 LOC) é reclassificado de "microkernel novo" para **walking skeleton com semântica parcialmente sintética**. O core de produção nasce ao lado, em Rust, sob contratos gerados e testes diferenciais.

O ajuste que este documento acrescenta ao plano do Tech Lead: **uma fatia vertical real precede o congelamento de contratos** (R0). A justificativa está em §3 e é consequência direta do achado F1.

O que se preserva é a propriedade intelectual, não o código: kernel semântico S0–S12, canonicalização RFC 8785 com golden vectors, exterioridade do juiz, harness-como-dado e o laboratório de medição pareada. Esses cinco itens são o fosso competitivo e nenhum deles é jogado fora.

---

## 1. Nota epistêmica: por que as avaliações anteriores erraram

Esta seção existe porque o modo de falha metodológico que produziu os erros é o **mesmo** que produziu os defeitos no código. Documentá-lo é parte da correção.

### 1.1 O erro

Nos relatórios v1 e v2 eu afirmei que o E-COV a 100% resolvia "o defeito mais grave do audit" (o ledger não-replayável, AP-10). Verifiquei que o gate passava. **Não verifiquei se as emissões eram semanticamente reais.**

O Tech Lead verificou. E não eram.

### 1.2 A generalização

Um gate é um **proxy** de uma propriedade. A propriedade desejada era *"todo kind declarado é emitido em produção com semântica correta"*. O proxy implementado é:

```python
needles = (f'"{kind}"', f"'{kind}'", f"EventKind.{member}")
for path in directory.rglob("*.py"):
    if any(needle in text for needle in needles):
        found = True
```

— **busca lexical de string num diretório**. Qualquer linha que mencione o nome do evento satisfaz o gate, independentemente de o payload ser real, condicional, ou uma constante inventada.

Isto é a Lei de Goodhart em forma pura: *"When a measure becomes a target, it ceases to be a good measure"* (Goodhart, 1975; formalização de variantes em Manheim & Garrabrant, *Categorizing Variants of Goodhart's Law*, 2018). Na taxonomia deles, é **Regressional + Extremal Goodhart**: otimizar o proxy até a região onde sua correlação com o alvo colapsa.

O audit original já havia nomeado exatamente este padrão — AP-8, *"Goodharted governance metrics"*, sobre o badge de TCB-LOC e contagem de testes. A correção proposta foi substituir por "cobertura de emissão de event kinds". **A correção reproduziu o defeito que corrigia**, um nível acima.

### 1.3 Regra derivada (vinculante para o novo substrato)

> **Nenhum gate pode ser satisfeito por presença lexical.** Todo gate deve ser satisfeito apenas por **comportamento observado em execução**: um teste que falha se o valor emitido for constante, um teste diferencial contra oráculo, ou um property test sobre o resultado.

Corolário operacional: para cada gate novo, escreva primeiro o **falso positivo** — o código mais preguiçoso que passaria. Se ele passa, o gate está errado. Isto é a disciplina de *mutation testing* (DeMillo, Lipton & Sayward, 1978; Jia & Harman, survey 2011) aplicada a gates de governança em vez de a testes unitários.

---

## 2. Achados verificados

Todos os itens abaixo foram confirmados por execução ou leitura direta de fonte no commit `99d1e0b`.

### F1 — O scheduler fabrica o próprio veredito
**Severidade: crítica. Invalida a tese central do projeto.**

`layer0/scheduler/driver.py:133-152`:

```python
subject = EvaluationSubject(run_id=run_id, episode_id=episode_id)
eval_id = self._gate.request(subject)
if isinstance(eval_id, Ok):
    emit(EventKind.EVALUATION_REQUESTED, ..., payload={"id": eval_id.value})
emit(EventKind.VERDICT_RECORDED, ..., payload={"verdict": "pass"})     # ← literal
emit(EventKind.CLAIM_RECORDED,   ..., payload={"n": len(receipts)})
emit(EventKind.INVALIDATION_CHECKED, ..., payload={"ok": True})        # ← literal
...
TrajectoryRef(digest="sha256:" + "0" * 64)                             # ← digest nulo
```

O gate é **chamado** e sua resposta é **descartada**. O veredito é a string `"pass"`, emitida incondicionalmente. A trajetória — que o I-9 exige ser linha válida de dataset de treino — carrega digest nulo.

A ironia técnica: `packs/code-default/oracles/gate.py` implementa verificação Ed25519 **de verdade** (`sign_verdict` / `verify_verdict`, com `test_unsigned_verdicts_cannot_pass_the_gate` verde). A capacidade existe uma camada acima. O scheduler simplesmente não a usa.

Consequência: a proposição de valor — *"what solved it must be separable, and the judge must be unreachable from the judged"* — está, no caminho do `layer0`, **não implementada**. O juiz não é inalcançável; ele é irrelevante, porque o julgado escreve o veredito.

Isto é AP-5 do audit ("controles que existem como bibliotecas com testes verdes mas não estão no caminho de produção") recorrendo dentro do código escrito para corrigir AP-5.

### F2 — E-COV é satisfeito por grep
**Severidade: crítica (é o gate que deveria ter detectado F1).**

Ver §1.2. O gate que atesta "emitted = declared" não distingue emissão real de emissão sintética. Foi este gate que me levou a declarar o problema resolvido.

### F3 — Cadeia de hash totalmente ordenada
**Severidade: alta. Bloqueia paralelismo.**

`layer0/events/envelope.py`: `EnvelopeFactory` mantém `self._seq` e `self._prev` como estado mutável único, sem sincronização. `layer0/events/fold.py:48` rejeita `seq` não-monotônico.

Três consequências formais:

1. **Corrida não detectada.** Duas threads emitindo concorrentemente podem encadear ao mesmo `prev_digest`, bifurcando silenciosamente. Não há CAS nem lock.
2. **Serialização obrigatória.** A cadeia `H_n = SHA256(H_{n-1} \| \mathrm{JCS}(e_n))` é intrinsecamente sequencial — o evento *n* não pode ser selado antes do *n−1* existir.
3. **Replay quebra por construção sob concorrência**, não por defeito.

O custo de (2) é quantificável pela Lei de Amdahl (Amdahl, 1967). Se *s* é a fração serial (append no ledger) e *p = 1−s* a paralelizável:

$$S(n) = \frac{1}{s + \frac{1-s}{n}}, \qquad \lim_{n\to\infty} S(n) = \frac{1}{s}$$

Com A-3 ("everything is an event or it didn't happen"), *todo* trabalho atravessa o ponto serial. Mesmo *s* modesto — digamos 5% — limita o ganho assintótico a 20×, e o *throughput* de append vira teto global do sistema, independentemente de quantos agentes rodem.

### F4 — Duas álgebras de seletores, a mais nova incorreta
**Severidade: alta (defesa em profundidade comprometida).**

`layer0/events/selectors.py` (450 LOC) implementa álgebra rigorosa: normalização de path com rejeição de travessia (`if segment == "..": _require(bool(segments), "traversal", ...)`), NFC em hosts, fail-closed em par indefinido (`Decision(False, "unparsable")`).

`layer0/spi/ceiling.py` (55 LOC) reimplementa por prefixo lexical. Verificado empiricamente:

```
/workspace/../etc  ⊆ /workspace  →  True    ← travessia aceita
/workspace-evil    ⊆ /workspace  →  False   ← caso tratado
```

É a recorrência de AP-3/D-21 (os três `EffectRequest` homônimos): duas implementações do mesmo conceito semântico, a mais recente mais fraca. Viola A-2, que exige que as duas autoridades **não confiem nos sujeitos uma da outra** — logo o ceiling não pode presumir que o kernel corrige o que ele deixa passar.

### F5 — Fail-open em ceiling vazio
**Severidade: média (contradiz I-6).**

```python
if not capabilities:
    return True
```

`plugin.yaml` sem chave `capabilities:` recebe teto irrestrito. Ausência de declaração lida como "sem restrição" em vez de "sem permissão" — inversão do princípio de *fail-safe defaults* (Saltzer & Schroeder, 1975, princípio 3: *"base access decisions on permission rather than exclusion"*).

### F6 — Sem durabilidade no `layer0`
`grep -rn "sqlite3" layer0/` → vazio. O sink é `InMemorySink` (lista Python). Não há WAL, fsync, nem outbox. A propriedade "state = fold(events)" é verdadeira apenas dentro do processo vivo; crash perde tudo.

### F7 — Worker de plugin é fixture
`layer0/registry/worker.py:114-123` responde `echo` e `fs.read` com eco literal. Não é runtime genérico; é *stub* de protocolo.

### F8 — Digest de plugin não cobre bytes
`layer0/registry/validator.py` não contém a substring `digest`. A identidade de plugin não é derivada de artefato, assets, prompts e políticas — logo `FrozenHarness` não é content-addressed sobre o que de fato executa, e a atribuição A/B perde o denominador.

### F9 — Isolamento é apenas `subprocess`
Tiers `container` e `wasm` são configuração declarativa sem rota de execução. Nenhum plugin não-Python roda hoje.

### F10 — Achados operacionais (menores)
Travessia lexical em `ceiling` já em F4; `lam.sqlite` versionado; `.gitignore` com placeholder; `vanguard_body_detailed.md` órfão contradizendo ADR-M0-10; 4 testes frágeis (2 por ausência de Ollama, 2 por poluição de ordem); dependência de `bwrap` indocumentada.

### Síntese dos achados

| ID | Achado | Severidade | Destino |
|---|---|---|---|
| F1 | Veredito sintético no scheduler | Crítica | Reescrito no novo core |
| F2 | E-COV satisfeito por grep | Crítica | Gate substituído (§8) |
| F3 | Cadeia de hash total-order | Alta | Envelope v2, `project_seq`/`agent_seq` |
| F4 | Álgebra de seletores duplicada | Alta | Delegação única; gate de CI |
| F5 | Fail-open em ceiling vazio | Média | Inversão de default + schema |
| F6 | Sem durabilidade | Alta | Ledger R1 |
| F7 | Worker fixture | Alta | Supervisor genérico R2 |
| F8 | Digest não cobre bytes | Alta | Identidade OCI R2 |
| F9 | Só `subprocess` | Média | Container R2 |
| F10 | Higiene | Baixa | Tarefas avulsas |

**Padrão comum:** F1, F2, F7, F8 são todos a mesma patologia — **a forma do contrato foi implementada e a semântica foi adiada**, com um gate lexical atestando conclusão. Não é desleixo; é a consequência previsível de medir estrutura em vez de comportamento.

---

## 3. A decisão e sua lógica

### 3.1 Reavaliação do custo afundado

Meu argumento anterior contra reescrever era: *"o `layer0` está ~70% pronto; jogar fora é caro."* Os achados F1/F6/F7/F8 refutam a premissa. O que existe é:

- **Forma de contrato correta** (os 5 SPIs, a taxonomia de 40 kinds, o FSM de ciclo de vida) — isso é *design*, transferível para qualquer linguagem.
- **Semântica de produção largamente ausente** (veredito, durabilidade, isolamento real, identidade de artefato).

Portanto o custo de replatformizar o `layer0` é **muito menor** do que estimei, porque grande parte dele é andaime. O argumento de preservação se desloca inteiro para (a) `vanguard/packages/`, que é real e funciona, e (b) os golden vectors e o kernel semântico. É exatamente o que a decisão do Tech Lead preserva.

**Correção formal do meu parecer anterior:** "não reescrever" continua correto quanto ao *kernel semântico*; estava errado quanto ao *runtime*. A distinção entre as duas coisas é o núcleo desta decisão.

### 3.2 Por que não continuar expandindo o runtime atual

Construir a Wave de paralelismo sobre F3, e o Milestone de cognição sobre F1, produziria:
- Corrupção silenciosa de ledger sob concorrência (o pior modo de falha para um sistema de auditoria).
- Um corpus de treino contaminado por vereditos fabricados — e, por §6.3, **irrecuperável**, porque atribuição ausente no momento do evento não é reconstruível.

Cada feature adicionada consolida abstrações provisórias. Isto é dívida técnica no sentido estrito de Cunningham (1992): juros pagos em toda entrega futura.

### 3.3 Por que não um rewrite cego

O kernel S0–S12 codifica ~47 regras de ordenação (`K-04`…`K-47`), cada uma documentando um defeito já sofrido em produção — por exemplo `K-47`/S8a: *append durável do intent com fsync **antes** do dispatch*, de modo que um crash entre dispatch e emit deixe o efeito **indeterminável** em vez de **invisível**. Reescrever sem oráculo redescobriria todos.

A resposta é **strangler fig** (Fowler, 2004) com **teste diferencial** (Feathers, *Working Effectively with Legacy Code*, 2004; McKeeman, *Differential Testing for Software*, 1998): o Python vira oráculo executável; nenhum merge passa se Rust e Python divergirem em decisão, digest, receipt ou sequência de eventos.

$$\forall x \in \mathcal{X}_{\text{conformance}}: \quad f_{\text{Rust}}(x) \equiv f_{\text{Python}}(x)$$

onde `≡` é igualdade byte-a-byte sobre a projeção canônica JCS. Isto converte "reescrita" — atividade de alto risco — em "port verificado", atividade de risco controlado.

### 3.4 O ajuste: fatia vertical antes do contract lock

**Esta é a única alteração material que proponho ao plano do Tech Lead.**

R0 congela `EventEnvelope v2`, `PluginManifest v2`, `HarnessManifest v2`, `ProjectManifest v1` e ativa `buf breaking`. Mas os contratos seriam derivados de um sistema cujo caminho end-to-end é sintético (F1): o fluxo de veredito, o payload de claim, o digest de trajetória — nada disso tem semântica observada.

Congelar contratos sobre comportamento presumido, e depois protegê-los com detecção de breaking change, **encapsula a ficção e torna caro removê-la**. É precisamente o modo de falha que produziu `verdict: "pass"`: especificar a partir de intenção em vez de evidência.

**Mitigação (barata, ~1 sprint):** antes do lock, executar **um** caminho vertical real ponta a ponta — pode ser no Python de referência, pode ser feio, não precisa escalar. Requisito mínimo: uma tarefa de código real, efeito autorizado pelo kernel, veredito Ed25519 **assinado por processo exterior e lido pelo chamador**, trajetória com digest verdadeiro. Serve para derivar os contratos de comportamento observado.

Custo: um sprint. Benefício: os contratos v2 descrevem o sistema que existe, não o que se imaginou. Dado que o projeto acaba de descobrir que sua camada nova tinha o veredito hard-coded por meses, essa validação é barata.

---

## 4. Fundamentação teórica

### 4.1 Event sourcing e a obrigação de replay

O contrato é `state = fold(events)` — um catamorfismo sobre o log:

$$\sigma_n = \mathrm{fold}(\delta, \sigma_0, [e_1..e_n]), \qquad \delta: \Sigma \times E \to \Sigma \text{ puro}$$

Replay-parity é a propriedade $\mathrm{fold}(\delta,\sigma_0,L) \equiv \sigma_{\text{live}}$. Ela só é significativa se $\delta$ for total e determinística e se **todo** efeito de estado passar pelo log (Young, CQRS/ES; Vernon, *Implementing DDD*, 2013; Kleppmann, *DDIA*, 2017, cap. 11).

F1 quebra isso semanticamente mesmo com o gate verde: o evento existe, o fold reconstrói — mas reconstrói uma ficção. **Replay fiel de dados falsos é indistinguível de replay fiel de dados verdadeiros.** Daí a necessidade de gates comportamentais (§8).

### 4.2 Ordem parcial, causalidade e o custo da ordem total

Ordem total é mais forte do que o domínio exige. O necessário é a relação *happens-before* de Lamport (1978):

$$e_1 \to e_2 \iff \text{(mesmo agente e } e_1 \text{ precede)} \lor \text{(causação)} \lor \exists e_3: e_1 \to e_3 \to e_2$$

Eventos concorrentes ($e_1 \parallel e_2$: nem $e_1 \to e_2$ nem $e_2 \to e_1$) **não precisam** de ordem. Relógios vetoriais (Fidge, 1988; Mattern, 1988) capturam exatamente essa ordem parcial; relógios híbridos (Kulkarni et al., HLC, 2014) acrescentam proximidade com tempo físico para depuração.

O CALM theorem (Hellerstein & Alvaro, *Keeping CALM*, CACM 2020) dá o critério: **um programa tem implementação coordenação-livre se e somente se for monotônico**. A atenuação de capacidades é monotônica por construção — o escopo só estreita:

$$\mathrm{attenuate}(S_{\text{parent}}, S_{\text{req}}) = S \implies S \sqsubseteq S_{\text{parent}}$$

Isto é um semi-reticulado; a operação nunca cresce. Já a reserva de orçamento **não** é monotônica (débito é decremento com limite inferior), logo exige coordenação — mas apenas dentro da unidade de consistência.

**Conclusão de projeto:** a unidade de consistência correta é `project_id`, com `project_seq` autoritativo por projeto e `agent_seq` local por agente, e causalidade explícita cruzando os dois. Nenhuma ordem global entre projetos. É exatamente a proposta do Tech Lead, e ela é a resposta certa a F3 — melhor do que minha sugestão anterior de reciclar `branch_id`, porque deriva a unidade de consistência do **domínio** (o projeto) e não de um artefato de depuração.

### 4.3 Segurança de capacidades

O modelo é object-capability (Dennis & Van Horn, 1966; Miller, *Robust Composition*, 2006). Propriedades relevantes:

- **Fail-safe defaults** (Saltzer & Schroeder, 1975): F5 viola.
- **Confused deputy** (Hardy, 1988): evitado se o plugin nunca recebe grants brutos, só *work leases* já autorizadas. O `IToolkit` está correto neste ponto ("toolkits NEVER see grants").
- **TOCTOU** (Bishop & Dilger, 1996): validar nome em S5 e operar sobre nome em S8 é a janela clássica. A correção estrutural é operar sobre **handles**, não nomes: `openat` + família `*at()` sob descritor aberto no grant. Elimina a classe inteira, incluindo aliasing por symlink.
- **Aliasing:** não-intersecção lexical não implica disjunção física. Necessário resolver identidade real (`realpath`, `st_dev`/`st_ino`) ou proibir symlinks por política de montagem.

### 4.4 Condições para concorrência segura

Não-intersecção de seletores é **necessária, não suficiente**. Condições completas:

| # | Condição | Formalização | Mecanismo |
|---|---|---|---|
| C1 | Disjunção de recursos | $\mathrm{sel}(e_i) \cap \mathrm{sel}(e_j) = \emptyset$ | Álgebra de seletores única (F4) |
| C2 | Ausência de aliasing | $\mathrm{inode}(\mathrm{sel}_i) \cap \mathrm{inode}(\mathrm{sel}_j) = \emptyset$ | realpath/inode ou mount policy |
| C3 | Ausência de canal lateral | Isolamento de namespace | container + net default-deny |
| C4 | Ausência de TOCTOU | Handle-based | `openat`/`*at()` |
| C5 | Merge determinístico | $\mathrm{merge}$ é função pura de $\to$ | Ordem canônica por `(project_seq, agent_id, agent_seq)` |
| C6 | Recuperação parcial | Idempotência ou compensação | Outbox + `compensate()` |

**C5 é a condição crítica e a mais fácil de violar.** Uma regra de merge do tipo "ordem em que os ramos terminaram" é determinística *no papel* e não-determinística *na prática* — e destrói a atribuição A/B, porque a diferença medida passa a poder vir do escalonador em vez do harness.

### 4.5 Validade estatística do self-improvement

Este é o ponto onde projetos de "agente que se melhora" falham silenciosamente.

**Comparações múltiplas.** Com *k* variantes testadas a nível α, a taxa de erro familiar é

$$\mathrm{FWER} = 1 - (1-\alpha)^k$$

Para $k=20, \alpha=0{,}05$: **64%** de chance de ao menos um falso positivo. Promover "a que ganhou" entre 20 é selecionar ruído. Correções: Holm (1979) para *k* pequeno; Benjamini–Hochberg (1995) com controle de FDR para *k* grande.

**Composição do erro.** O sistema **acumula**: variante promovida por ruído vira baseline, e a rodada seguinte mede contra baseline inflado. O erro não se dilui — compõe. É o mecanismo de Ioannidis (*Why Most Published Research Findings Are False*, PLoS Med 2005) aplicado a um laço automatizado que roda milhares de vezes mais que a ciência humana.

**McNemar** (1947) para desenho pareado, com correção de continuidade:

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad \mathrm{df}=1$$

onde *b* e *c* são os pares discordantes. Note que o poder depende **apenas dos discordantes** — pares em que ambos os braços acertam ou ambos erram não contribuem. Logo o *n* necessário cresce com a concordância: se a taxa de discordância é $\pi_d$, então $n \approx n_{\text{disc}}/\pi_d$. Com $\pi_d = 0{,}2$ e necessidade de ~200 discordantes, o corpus precisa de ~1000 tarefas — **não 200**. Daí a regra correta ser *power analysis define o N*, não um número fixo. Meu "200 tarefas" anterior era arbitrário; a formulação do Tech Lead é a certa.

**Efeito mínimo detectável.** Reportar MDE e intervalo de confiança, não apenas *p*. Um sistema que promove por *p* < 0,05 sem limiar de efeito promove preferencialmente variantes de **alta variância** — exatamente as piores.

**Piso A/A.** Rodar o mesmo harness contra si mesmo estabelece a taxa empírica de falso positivo do instrumento. É o ativo mais subestimado do projeto e deve ser gate permanente.

**Pré-registro.** Hipótese, métrica, população e regra de parada fixadas antes de rodar (Nosek et al., *The preregistration revolution*, PNAS 2018). Sem regra de parada, *optional stopping* infla α arbitrariamente.

### 4.6 Reward hacking e o limite do juiz exterior

O juiz exterior assinado previne **adulteração** do veredito, não **gaming** do oráculo. Agente que faz `pytest` passar deletando o teste obtém veredito verde legítimo de juiz honesto.

Literatura: Krakovna et al., *Specification gaming: the flip side of AI ingenuity* (DeepMind, 2020); Skalse et al., *Defining and Characterizing Reward Hacking* (NeurIPS 2022); Amodei et al., *Concrete Problems in AI Safety* (2016), §"reward hacking". Campbell (1979) é o ancestral sociológico: *"the more any quantitative social indicator is used for social decision-making, the more subject it will be to corruption pressures"*.

Defesas complementares: oráculos pré-registrados; **mutation testing sobre a própria suíte do oráculo** (se a suíte sobrevive a mutantes, ela discrimina); invariantes sobre o diff (proibir modificação de arquivos de teste sem aprovação; medir cobertura antes/depois); `InvalidationChecked` com semântica real — hoje é literal `{"ok": True}` (F1).

### 4.7 Destilação e confundimento

Pares DPO (Rafailov et al., *Direct Preference Optimization*, NeurIPS 2023) colhidos de trajetórias com harnesses diferentes ensinam o modelo a imitar o **harness** vencedor, não a política melhor. O sinal fica confundido com prompt, ferramentas, orçamento e política de contexto.

Validade causal exige manter constante tudo exceto a variável de interesse:

$$(\tau_w, \tau_l) \text{ válido} \iff \text{harness\_digest}_w = \text{harness\_digest}_l \land \text{task}_w = \text{task}_l \land \text{seed}_w = \text{seed}_l$$

Isto é o *ceteris paribus* de Rubin (modelo de resultados potenciais, 1974) aplicado ao harness. **É por isso que a atribuição precisa ser gravada no momento do evento, não depois:** trajetória sem `harness_digest` e `plugin_digests` é inutilizável para harvest, e a lacuna é irreparável.

### 4.8 Economia de execução

O vetor de reserva $R = \{ \text{usd\_micros}, \text{millis}, \text{tokens}, \text{bytes}, \text{turns}, \text{depth} \}$ é decisão forte e incomum.

**Admission control sob concorrência.** Com *n* ramos, a condição segura é sobre o **pior caso simultâneo**, não a soma esperada:

$$\sum_{i=1}^{n} R^{\max}_i \preceq R_{\text{disponível}} \quad \text{(componente a componente)}$$

Caso contrário *n* ramos individualmente conformes estouram coletivamente.

**Escalada de tier é um bandit contextual, não uma cascata.** A política atual (`tier1 → tier2 → tier3` ao falhar) é heurística estática. Com causa nomeada (C-3) e custo 6-dim (C-4), a escolha vira decisão aprendível: `CONTEXT_OVERFLOW` não se resolve com modelo maior — resolve-se com compactação melhor. Escalar sempre para o tier caro desperdiça orçamento nas falhas que capacidade não resolve. Formalmente, minimizar arrependimento

$$\mathcal{R}(T) = \sum_{t=1}^{T} \left[ c(a_t) - c(a^*_t) \right]$$

com $a_t$ condicionado ao contexto (causa da falha anterior, orçamento restante, dificuldade estimada). LinUCB (Li et al., 2010) ou Thompson sampling contextual são baselines adequados. **Isto é trabalho de Milestone D, mas os dados precisam ser capturados desde o primeiro runtime.**

### 4.9 Durabilidade e a fronteira transacional

F6 (sem durabilidade) e a necessidade de publicar eventos exigem escrita atômica de estado + evento + outbox. Sem transação única, dois modos de falha: evento publicado sem estado (fantasma) ou estado sem evento (invisível).

Padrão: **transactional outbox** (Richardson, *Microservices Patterns*, 2018; ancestral em Helland, *Life beyond Distributed Transactions*, CIDR 2007). Com JetStream em entrega *at-least-once*, todo consumidor deve ser idempotente — chave de idempotência no envelope, dedupe por `(command_id, idempotency_key)`.

Ordenação de blob: `write → fsync → emit(event with blob_ref)`. Nunca o inverso (fecha D-19). Note que fsync não é garantia universal em todos os sistemas de arquivo/hardware; para o nível de garantia pretendido, documentar as premissas de durabilidade do storage é obrigatório.

**Identidade nunca deriva de bytes Protobuf.** A documentação oficial do Protobuf afirma que a serialização determinística **não** é canônica nem estável entre versões e linguagens. Identidade, digest e assinatura permanecem em JCS/RFC 8785 (Rundgren et al.). Protobuf é **transporte**; JCS é **identidade**. Esta separação está correta no plano do Tech Lead e é um erro comum em sistemas assinados.

---

## 5. Arquitetura-alvo

### 5.1 Cinco planos

```
┌──────────────────────────────────────────────────────────┐
│ CONTROL PLANE            (autoritativo)                  │
│ Orchestrator · Scheduler · Capability/Budget Kernel       │
│ Plugin Supervision · Project State · Leases               │
└───────────┬──────────────────────────────┬───────────────┘
            │ work leases                  │ commands+events
            ▼                              ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│ EXECUTION PLANE           │  │ DATA PLANE               │
│ Harness instances         │──▶ Ledger (source of truth) │
│ Isolated plugin cells     │  │ CAS blobs · Outbox        │
│ Workspaces / worktrees    │  │ Projections               │
└───────────┬───────────────┘  └───────────┬──────────────┘
            │ evaluation requests           │ read-only
            ▼                               ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│ EVIDENCE PLANE            │  │ LEARNING PLANE           │
│ Exterior evaluators       │  │ Dataset · Experiments     │
│ Signed verdicts (Ed25519) │  │ Attribution · Variants    │
│ Identidade independente   │  │ Promotion proposals       │
└───────────────────────────┘  └───────────┬──────────────┘
                                            │ signed promotion
                                            └──▶ Control Plane
```

**Correção de projeto que incorporo do Tech Lead:** o orquestrador é **autoritativo**, não consumidor de ledgers. Meu plano anterior o colocava como *consumer* — errado: quem concede leases, agenda e supervisiona **é** fonte de autoridade. Analytics é que é consumidor.

**Unidade de consistência = `project_id`.** Um líder por projeto, sharding entre projetos. Central logicamente, não singleton global.

### 5.2 Event Envelope v2

```
project_id · run_id · agent_id · harness_digest · plugin_digest
project_seq · agent_seq · prev_digest
causation_id · correlation_id · command_id · idempotency_key
hybrid_logical_clock
payload_digest | blob_ref        ← conteúdo fora do envelope por padrão
kind · occurred_at · principal · alertable
```

Separar metadados de conteúdo resolve três problemas de uma vez: tamanho do ledger, redação/criptografia de conteúdo sensível, e a possibilidade de reter identidade após expurgo de conteúdo (GDPR-like).

### 5.3 Modelo de plugin

Lifecycle comum: `Describe · Init · Health · Invoke · Checkpoint · Quiesce · Shutdown`.

Serviços tipados sobre ele: Planner · Context · Memory · Model Gateway · Tool/Effect Adapter · Evaluation Gateway · Project Policy.

**Disciplina anti-proliferação de SPI** (do Tech Lead, correta): cache é *decorator*; skills são *assets/providers*; prompt engineering e compressão pertencem a Context/Planner; self-improvement pertence ao Learning Plane. Cada SPI nova é superfície congelada para sempre — o custo marginal de uma SPI é permanente.

Identidade de plugin (corrige F8):

$$\mathrm{id} = H\big(\mathrm{JCS}(\text{manifest}) \,\|\, H(\text{artifact bytes}) \,\|\, H(\text{assets}) \,\|\, H(\text{prompts}) \,\|\, H(\text{policies resolvidas})\big)$$

Sem isso, `FrozenHarness` não é content-addressed sobre o que executa, e A/B perde denominador.

### 5.4 Tiers de isolamento

| Tier | Contém | Não contém | Uso |
|---|---|---|---|
| `in_process` | nada | tudo | somente TCB compilado e auditado |
| `subprocess` | memória, rlimits, no-new-privs | rede, canais de timing | plugins confiáveis de baixa autoridade |
| `container` (OCI rootless) | + namespaces mount/PID/net, UID | canais de cache/CPU | **default** para tools e código de modelo |
| `wasm` (WASI) | + capacidades explícitas | timing | spike não-bloqueante |

**Nota sobre WASI/Component Model:** WIT é adequado para contratos de componentes, mas o Component Model segue em ciclos de Developer Preview. Não deve ser ABI inicial única. Posição correta: spike, não requisito de release.

**MCP** entra apenas como *adapter* de ferramentas externas — nunca como protocolo de autoridade, lifecycle ou ledger interno. Confundir protocolo de integração com protocolo de autoridade é erro estrutural comum.

**Chave de assinatura do avaliador jamais entra em célula de plugin.** Deve haver teste que falha se a chave for alcançável de qualquer cela.

### 5.5 Tech stack

| Camada | Escolha | Justificativa |
|---|---|---|
| Core (orchestrator, kernel, ledger, supervisor) | **Rust + Tokio** | Ver §5.6 |
| Planners, context, memory, model adapters, learning | **Python** | Ecossistema de ML; iteração rápida; é onde a pesquisa acontece |
| SDK, CLI/UI, consumidores de telemetria | **TypeScript** | Superfície de cliente |
| Transporte runtime | **Protobuf + gRPC**, lint/breaking via **Buf** | Tipado, streaming, multilíngue |
| **Identidade / digest / assinatura** | **JSON Schema + JCS (RFC 8785)** | Protobuf não é canônico entre versões/linguagens |
| Empacotamento de plugin | **OCI** content-addressed | Fixação por digest, não por tag |
| Supply chain | **Sigstore/Cosign + SBOM + in-toto/SLSA** | Assinatura e proveniência de artefato |
| Persistência single-node | **SQLite WAL + filesystem CAS** | Simples, durável, transacional |
| Persistência distribuída | **PostgreSQL + S3/MinIO + NATS JetStream** | Adapters atrás da mesma interface |
| Analytics | **Parquet/Iceberg ou ClickHouse** | Export assíncrono |
| Observabilidade operacional | **OpenTelemetry** | Exporter do ledger, **nunca** substituto |

### 5.6 Justificativa honesta do Rust

**O argumento não é performance.** O gargalo de um agente é latência de modelo e I/O de sandbox; reescrever o kernel para ganhar CPU otimizaria ~1% do tempo de parede.

**O argumento é correção sob concorrência.** F3 é uma corrida de dados numa estrutura compartilhada sem sincronização — precisamente a classe que o sistema de tipos e o modelo de ownership do Rust tornam **inexprimível** em código seguro. Dado que:

1. o Milestone de paralelismo é central ao produto,
2. o modo de falha de uma corrida no ledger é corrupção silenciosa de auditoria,
3. o projeto já demonstrou (F1, F3) que a disciplina de revisão não pegou defeitos dessa classe,

mover o TCB para uma linguagem onde a classe é impedida por construção é decisão defensável — mas **deve ser registrada em ADR com esta justificativa**, não com justificativa de performance. Justificar por performance seria falso e criaria expectativa errada, além de convidar a métricas Goodhartáveis.

**Contra-argumento que deve constar do ADR:** a mesma correção é alcançável em Python com locks explícitos e uma estrutura de dados redesenhada, a custo muito menor. A escolha do Rust só se justifica se a equipe tiver capacidade real de sustentá-lo e se o horizonte do produto for longo. Se a resposta a qualquer uma dessas for negativa, a decisão correta é redesenhar o ledger em Python e adiar o Rust.

---

## 6. Sequência de execução

Hierarquia: `Subtask → Task → Sprint → Wave → Milestone`.

### R0 — Vertical Slice + Contract Lock
**Wave 0 (novo, meu ajuste) + Wave 1**

**Sprint 0.1 — Fatia vertical real** *(pré-requisito do lock)*
- Uma tarefa de código real, ponta a ponta, no Python de referência.
- Efeito autorizado pelo kernel; nada fora do dispatch.
- Veredito Ed25519 assinado por **processo exterior**, lido pelo chamador e determinando o resultado. Remover `verdict: "pass"` literal.
- Trajetória com digest real (não `sha256:000…`).
- **Objetivo: observar o comportamento que os contratos vão descrever.**

**Sprint 1.1 — Contratos canônicos**
- `EventEnvelope v2` (§5.2), `PluginManifest v2`, `HarnessManifest v2`, `ProjectManifest v1`.
- Lifecycle e serviços tipados; deadlines, cancellation, erros estruturados obrigatórios.
- Refs sempre resolvidas para digest imutável.

**Sprint 1.2 — Toolchain polyglot**
- Buf lint / generate / breaking.
- SDKs Rust, Python, TS gerados. Proibido tipo de domínio escrito à mão.
- Golden vectors importados para `conformance/`.

**Sprint 1.3 — Contrato de dados de aprendizagem**
- Trajectory v2 como projeção determinística de eventos.
- Taxonomia fechada de causas de falha, versionada.
- Custo multidimensional em model calls, tool calls, totais de projeto.
- Políticas de redação, criptografia, captura e retenção.

**Gate G-R0:** `buf lint && buf breaking && cargo test -p aether-protocol -p aether-canonical && pytest conformance/` · SDKs regeneram sem diff · golden vectors idênticos nas 3 linguagens · nenhum digest depende de bytes Protobuf · **a fatia vertical roda com veredito exterior real**.

### R1 — Durable Core & Authoritative Orchestrator
- Ledger append-only SQLite WAL; commit atômico de command + event + outbox.
- CAS: `write → fsync → event(blob_ref)`.
- Reducers puros: project, run, budget, grants, approvals, plugin lifecycle.
- Cold replay + time-travel branch.
- Kernel Rust portado com **paridade diferencial** contra Python em todos os golden vectors.
- Orchestrator single-node: state machines, um lease por projeto, dedupe de comando, heartbeat, cancelamento, recuperação.
- **Benchmarks e regression budgets desde aqui** (append p50/p95/p99, replay throughput, RPC overhead, memória/cela, latência de scheduling).

**Gate G-R1 (= Milestone A):** kill/restart entre qualquer command e event sem perda ou duplicação lógica · replay reconstrói 100% do estado observável · paridade Python×Rust total · **nenhum verdict, claim ou checkpoint sintético** · baseline de performance salvo.

### R2 — Generic Plugin Runtime
- Registry OCI por digest; verificação de assinatura, attestation, SBOM, compatibilidade de protocolo.
- Identidade de plugin sobre bytes+assets+prompts+policies (corrige F8).
- Supervisor: `subprocess` com identity/rlimits/no-new-privs/FS policy; `container` rootless para execução de ferramentas; rede default-deny.
- Lifecycle ledgerado; deadlines, cancelamento cooperativo, backpressure, bounded queues, crash-loop backoff, circuit breaker.
- Hot-swap somente em fronteira registrada, com atribuição no ledger.
- Plugin nunca recebe grant bruto — apenas work lease autorizada.
- **`ceiling` delega para a álgebra única de seletores** (corrige F4); default fail-closed (corrige F5); gate de CI proibindo comparação de seletor fora do módulo canônico.

**Gate G-R2:** plugin de referência Rust **e** Python passam a mesma suíte · core não importa módulo de plugin · fault injection não derruba orchestrator nem corrompe ledger · capability ceiling falha fechado · todas as transições replayáveis.

### R3 — Harness Compiler & Builder Experience
- Compiler v2: resolve refs para digest, valida compatibilidade, grafo de dependências, interseção de capabilities e budgets; produz `FrozenHarness` byte-stable; explica conflitos com path e remediação.
- CLI: `plugin validate` · `harness scaffold|validate|compose|diff` · `run inspect|replay`.
- Migração seletiva dos assets atuais; migration ledger registrando preservado / substituído / **recusado**.

**Gate G-R3 (= Milestone B):** mesmo manifest + artifacts ⇒ mesmo digest em ambiente limpo · trocar planner ou memory ⇒ zero diff no core · plugin não-Python executa em isolamento real · builder detecta incompatibilidade antes do run.

### R4 — Coding Agent Vertical Slice
- Model Gateway com streaming, usage e erros provider-independent.
- Filesystem e terminal toolkits; repo index/context com símbolos, imports e orçamento de tokens.
- Patch inicialmente textual/anchored; **AST edits só entram com benchmark favorável** (evita complexidade não justificada).
- Memória de curto prazo e compaction.
- Evaluation Gateway que **apenas solicita e valida** verdicts assinados.
- Workspace isolado por run; snapshot/checkpoint/rollback; secrets e rede separados.
- Corpus de aceitação pequeno, determinístico, pré-registrado; cassettes para regressão, modelo vivo no gate de release; baseline shell-only e piso A/A.

**Gate G-R4:** tarefa real termina com diff não-vazio e **verdict assinado não-mockado** · toda model/tool call rastreável até plugin, versão, harness e pai causal · nenhum conceito de coding no core · abort/restart preserva workspace e trajetória.

### R5 — Autonomous Coding Project (multi-agente)
- `ProjectManifest`: roles, harness refs, budgets, acceptance gates, contratos de artifact.
- Project planner/policy propõe task graph; o **core valida e agenda**.
- Task leases atenuadas por agente; budget de projeto agrega reservas e commits dos filhos.
- Execução paralela em worktrees independentes; ordenação por `project_seq`/`agent_seq` preservando causalidade; sem ordem total global.
- Comunicação apenas por eventos e artifacts tipados — **sem chat invisível**.
- Planner/executor/reviewer como primeira composição, **sem hard-code desses papéis no core**.
- Merge/conflict policy como plugin; avaliador exterior decide aceitação final.

**Gate G-R5 (= Milestone C):** coordinator + ≥2 harnesses fazem trabalho concorrente útil · cada agente pode usar modelo/provider diferente · kill de qualquer agente ⇒ recovery ou reassignment determinístico · project replay reconstrói task graph, artifacts, budgets, approvals e verdicts · toda mudança aceita tem cadeia causal até command e evidence.

### R6 — Distributed Control & Data Plane
- PostgreSQL event/command store; S3/MinIO CAS; outbox → NATS JetStream; consumidores idempotentes; rebuild de projeções.
- Shard por `project_id`; ownership leases com **fencing tokens**; orchestrator stateless fora do lease.
- Backpressure, admission control, bounded pools.
- OTel para traces/metrics/logs operacionais; ledger segue fonte da verdade semântica.
- Chaos: partição, entrega duplicada, consumidor lento.

**Gate G-R6:** mesma suíte de conformidade passa em SQLite/local e Postgres/distribuído · redelivery não duplica efeito · perda do líder faz failover com fencing correto · nada sensível exportado sem opt-in.

### R7 — Experiment & Learning Plane
- Materialização de trajetórias para Parquet; views por project/harness/plugin/model/tool/failure cause; datasets content-addressed.
- Data-quality gates: completude, atribuição, validade de assinatura.
- Experiment service: pré-registro de hipótese, métrica, população e **regra de parada**; assignment pareado; seeds/cassettes determinísticos; piso A/A; power analysis; MDE; intervalos de confiança; correção de múltiplos testes; **registro de todas as tentativas**.
- Atribuição regressiva sobre o grafo causal, separando falha de model / context / tool / memory / policy / provider / infraestrutura.
- Gera candidatos; **nenhuma mutação em produção ainda**.

**Gate G-R7:** experimento reproduzível a partir de dataset + manifests + artifact digests · A/A respeita o orçamento de falso positivo pré-registrado · nenhuma trajetória sem atribuição entra no corpus.

### R8 — Governed Meta-Harness
- Variantes limitadas a manifest, skill, prompt asset e parâmetros de policy. Mutation budget, campos proibidos, guard de similaridade/loop. Toda variante imutável, content-addressed, assinável.
- Promotion policy com efeito mínimo, incerteza, custo e regressões de segurança; aprovação humana configurável por classe; canary por cohort; **rollback por ponteiro de registry — artifacts nunca sobrescritos**.
- Harvest só de episódios com evidence válido; skill synthesis **antes** de fine-tuning (mais barato e reversível); export DPO/SFT versionado; candidatos de modelo passam pelos mesmos gates de experimento.

**Gate G-R8 (= Milestone D):** uma variante é proposta, avaliada, promovida em canary e **revertida em exercício controlado** · Meta-Harness não possui workspace write, evaluator key nem registry write direto · Promotion Controller é o único writer do ponteiro de produção · histórico explica por que a versão foi promovida.

### R9 — Generality Falsification
- Domínio estruturalmente diferente de coding (data investigation, structured research ou operations planning), com corpus e evaluator pré-registrados.
- Plugins novos **sem** adicionar SPI específica de domínio. Se faltar capacidade, primeiro provar que é extensão universal.
- Rodar single-agent e multi-agent; comparar trajetória, custo e recovery com o projeto de coding; validar UX do builder com integrador externo ao core.

**Gate G-R9 (= Milestone E):** `git diff` dos crates de core **vazio** durante a criação do pack · novo domínio end-to-end com signed evidence · ≥1 plugin reutilizado sem modificação entre domínios · nenhuma taxonomia de coding virou conceito universal.

---

## 7. Política de desativação do legado

`vanguard/packages/` **não tem data de deleção**. Tem condições de saída — correção que incorporo do Tech Lead sobre meu plano anterior, que fixava deleção na Wave 7 (imprudente):

1. Toda semântica preservada possui teste diferencial.
2. Todos os consumidores de produção usam AETHER v1.
3. Rollback foi exercitado sem depender do runtime antigo.
4. Nenhum artifact ou ferramenta de migração importa o legado.
5. Duas releases completas sem fallback.
6. Tech Lead aprova relatório de paridade e de *intentionally-not-ported*.

Satisfeitas, a remoção ocorre em task isolada, reversível por tag, **sem misturar com feature work**.

---

## 8. Gates que resistem a Goodhart

Consequência direta de §1. Cada gate abaixo é comportamental, não lexical.

| Propriedade | Gate errado (lexical) | Gate correto (comportamental) |
|---|---|---|
| Emissão real | grep do nome do kind | Property test: payload varia com o input; **teste que falha se o valor for constante** |
| Veredito exterior | existe chamada ao gate | Injetar veredito `fail` e exigir que o run **falhe**; injetar assinatura inválida e exigir rejeição |
| Replay | teste de replay existe | Fold frio vs. estado vivo, diff estrutural, **em todo run de CI** |
| TCB mínimo | contagem de LOC | **Mutation score** ≥ limiar em kernel + reducers |
| Controle ativo | teste unitário verde | Cobertura de **call-site de produção**: controle sem chamador falha o build |
| Domain-blindness | grep de `coding\|pytest\|ast` | grep **+** compilação de pack de outro domínio com `git diff` core vazio |
| Isolamento | manifesto declara tier | Fault injection: plugin tenta escapar e **deve falhar**; probe de containment verificado |
| Identidade de plugin | manifesto tem versão | Alterar 1 byte do artifact ⇒ **digest muda** ⇒ harness digest muda |
| Determinismo | cassettes existem | Duas execuções ⇒ **ledger byte-idêntico** |
| Qualidade de dado | schema valida | Nenhuma trajetória sem atribuição entra no corpus; **gate de completude** |

**Regra de construção de gate:** escreva primeiro o código mais preguiçoso que passaria. Se ele passa, o gate está errado.

---

## 9. Registro de riscos

| ID | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| K-1 | Equipe não sustenta Rust | Média | Crítico | ADR honesto (§5.6); fallback = redesenhar ledger em Python |
| K-2 | Contract lock congela ficção | **Alta se R0 pular a fatia vertical** | Alto | Sprint 0.1 obrigatório |
| K-3 | Superfície de stack grande demais | Média | Alto | R6 (distribuído) só depois de R5; adapters atrás de interface desde R1 |
| K-4 | Time-to-value longo demais | Média | Alto | R4 (coding agent) é o marco de valor; não deixar R1–R3 incharem |
| K-5 | Paridade diferencial incompleta | Média | Crítico | Golden vectors como gate de merge; divergência bloqueia |
| K-6 | Goodhart recorre em gate novo | **Alta** (já ocorreu 2×) | Alto | §8 + revisão adversarial de todo gate |
| K-7 | Promoção por ruído no Meta-Harness | Alta se sem correção | Crítico | FDR + MDE + A/A + holdout + pré-registro |
| K-8 | Legado nunca morre | Média | Médio | Condições de saída §7 + revisão trimestral |
| K-9 | Corpus contaminado por verdicts sintéticos | **Certa para dados atuais** | Alto | Descartar corpus pré-R0; harvest só de evidence válido |

**K-9 merece destaque:** todo dado gerado pelo caminho do `layer0` até hoje carrega vereditos fabricados. Ele **não pode** alimentar o Learning Plane. O corpus começa do zero em R4.

---

## 10. Referências

**Medição e incentivos**
Goodhart (1975), *Problems of Monetary Management*. · Campbell (1979), *Assessing the impact of planned social change*. · Manheim & Garrabrant (2018), *Categorizing Variants of Goodhart's Law*. · Muller (2018), *The Tyranny of Metrics*.

**Sistemas distribuídos**
Lamport (1978), *Time, Clocks, and the Ordering of Events in a Distributed System*, CACM. · Fidge (1988) / Mattern (1988), vector clocks. · Kulkarni et al. (2014), *Logical Physical Clocks (HLC)*. · Hellerstein & Alvaro (2020), *Keeping CALM: When Distributed Consistency is Easy*, CACM. · Herlihy & Wing (1990), *Linearizability*. · Helland (2007), *Life beyond Distributed Transactions*, CIDR. · Kleppmann (2017), *Designing Data-Intensive Applications*. · Amdahl (1967), *Validity of the single processor approach*.

**Event sourcing e arquitetura**
Young, CQRS/Event Sourcing. · Vernon (2013), *Implementing Domain-Driven Design*. · Evans (2003), *Domain-Driven Design*. · Richardson (2018), *Microservices Patterns* (transactional outbox). · Fowler, *StranglerFigApplication*. · Feathers (2004), *Working Effectively with Legacy Code*. · Nygard (2007), *Release It!* (circuit breaker, bulkhead). · Cunningham (1992), *The WyCash Portfolio Management System* (technical debt).

**Segurança de capacidades**
Dennis & Van Horn (1966), *Programming Semantics for Multiprogrammed Computations*. · Lampson (1971), *Protection*. · Saltzer & Schroeder (1975), *The Protection of Information in Computer Systems*. · Hardy (1988), *The Confused Deputy*. · Miller (2006), *Robust Composition* (tese, object-capability). · Bishop & Dilger (1996), *Checking for Race Conditions in File Accesses* (TOCTOU).

**Teste e verificação**
DeMillo, Lipton & Sayward (1978), *Hints on Test Data Selection* (mutation testing). · Jia & Harman (2011), *An Analysis and Survey of the Development of Mutation Testing*. · McKeeman (1998), *Differential Testing for Software*. · Claessen & Hughes (2000), *QuickCheck* (property-based testing).

**Estatística e validade**
McNemar (1947), *Note on the sampling error of the difference between correlated proportions*. · Holm (1979), *A simple sequentially rejective multiple test procedure*. · Benjamini & Hochberg (1995), *Controlling the False Discovery Rate*, JRSS-B. · Ioannidis (2005), *Why Most Published Research Findings Are False*, PLoS Medicine. · Nosek et al. (2018), *The preregistration revolution*, PNAS. · Rubin (1974), potential outcomes.

**IA, alinhamento e aprendizagem**
Amodei et al. (2016), *Concrete Problems in AI Safety*. · Krakovna et al. (2020), *Specification gaming: the flip side of AI ingenuity*, DeepMind. · Skalse et al. (2022), *Defining and Characterizing Reward Hacking*, NeurIPS. · Rafailov et al. (2023), *Direct Preference Optimization*, NeurIPS. · Li et al. (2010), *A Contextual-Bandit Approach to Personalized News Article Recommendation* (LinUCB).

**Padrões e especificações**
RFC 8785 — *JSON Canonicalization Scheme (JCS)*. · RFC 8032 — *EdDSA (Ed25519)*. · OCI Image Format Specification. · Sigstore/Cosign; in-toto attestation; SLSA framework. · OpenTelemetry Semantic Conventions (GenAI). · WebAssembly Component Model / WIT. · NATS JetStream (at-least-once delivery). · Protocol Buffers — nota oficial sobre não-canonicidade da serialização determinística.

---

## 11. Conclusão

O projeto possui um fosso competitivo real — determinismo por construção, segurança de capacidades com álgebra formal, juiz exterior assinado, economia multidimensional e medição pareada com piso A/A — e **nenhum concorrente tem esse conjunto**. Esse fosso está nas ideias, nos golden vectors e no runtime Python que funciona, não no `layer0`.

O `layer0` foi diagnosticado corretamente pelo Tech Lead: forma de contrato certa, semântica de produção largamente sintética, atestada por um gate que media presença de string. A descoberta de que o veredito é a constante `"pass"` num sistema cuja tese é *"o juiz deve ser inalcançável para o julgado"* é o achado mais importante deste ciclo, e a decisão de replatformizar decorre dele logicamente — não de preferência estética por Rust.

Duas lições estruturais devem sobreviver a este documento:

1. **Gate lexical mede sintaxe; propriedade é semântica.** Todo gate deve ser adversarialmente testado contra a implementação mais preguiçosa que o satisfaria. Isto falhou duas vezes (TCB-LOC, E-COV); não pode falhar uma terceira.

2. **Especificar a partir de intenção produz ficção; especificar a partir de evidência produz contrato.** É por isso que a fatia vertical precede o contract lock — a única alteração material que este relatório faz ao plano do Tech Lead, e ela custa um sprint.

O caminho é: fatia vertical real → contratos derivados de comportamento observado → core durável com paridade diferencial → runtime genérico de plugins → builder → coding agent → projeto autônomo → escala → experimentação → meta-harness governado → falsificação de generalidade.

Nada nesse caminho exige acreditar em nada. Cada passo tem gate que pode falhar — que é, afinal, a única propriedade que distinguia este projeto desde o início.

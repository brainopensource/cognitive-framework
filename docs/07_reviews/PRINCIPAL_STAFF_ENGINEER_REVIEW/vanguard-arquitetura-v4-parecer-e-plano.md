> **Non-normative.** Advisory evidence only. Law is `docs/SPEC.md` + `docs/05_adr/0069`–`0074` + annexes.
> Operational sequence: `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`. Do not cite this file as a requirement.
> The `core/` tree proposed here is **rejected** (ADR-0069).

# Vanguard — Parecer de Arquitetura e Plano de Construção (v4)

**Documento:** `vanguard-arquitetura-v4-parecer-e-plano.md`
**Papel:** Senior Tech Lead / Principal Architect — parecer independente
**Base de evidência:** clone de `brainopensource/cognitive-framework` no commit `99d1e0b`, leitura de fonte, execução da suíte completa e dos gates
**Avalia:** `Vanguard-substrate-060-full-refactor-v3.md` e `vanguard-substrate-060-execution-plan.md`
**Data:** 2026-08-19

---

## 0. Veredito em cinco linhas

O diagnóstico dos dois documentos anexos está **correto quanto ao sintoma** (`verdict: "pass"` hard-coded, gates lexicais, Goodhart) e **errado quanto à causa** — e por isso o plano proposto é o remédio errado.

Os documentos afirmam que a semântica de produção do `layer0/` "foi adiada". **Não foi adiada. Foi deixada para trás num fork por cópia.** Verifiquei: `layer0/events/selectors.py` difere de `vanguard/packages/domain/selectors/resource_selector.py` em **2 linhas** — só o caminho de import. O kernel é fork com 70% de similaridade. O `layer0/` não é um microkernel novo: é uma cópia do runtime existente **sem** a durabilidade, **sem** o avaliador exterior, **sem** o sandbox e **sem** o model gateway que o original já tinha e ainda tem.

Consequência: o plano 0.6.0 agenda Waves 1–3 (meses) para reconstruir SQLite WAL, avaliador Ed25519 em processo separado e sandbox rootless — **tudo isso já existe, testado, no mesmo repositório**. E propõe construir um terceiro sistema ao lado dos dois que já competem, que é exatamente a condição que produziu o defeito.

**Recomendação: não replatformizar. Convergir as duas látices, inverter a direção da migração, e gastar o esforço no que de fato não existe — a fronteira de plugin fora de processo e o orquestrador.**

---

## 1. Evidência de execução

Tudo abaixo é reproduzível a partir do clone limpo do commit `99d1e0b`.

### 1.1 O fork por cópia

```
layer0/events/selectors.py   vs  vanguard/packages/domain/selectors/resource_selector.py
  → 18.498 vs 18.510 chars · 28 defs compartilhados · 0 defs exclusivos de cada lado
  → diff completo = 2 linhas:
      -from ..canonicalisation.jcs import canonicalise, utf16_sort_key
      +from .canonical import canonicalise, utf16_sort_key

layer0/kernel/dispatch.py    vs  vanguard/packages/kernel/dispatch.py     similaridade 0,700
layer0/kernel/grants.py      vs  vanguard/packages/kernel/grants.py       similaridade 0,731
layer0/events/canonical.py   vs  .../canonicalisation/jcs.py              similaridade 0,928
```

O relatório v3 chama o F4 de "duas álgebras de seletores, a mais nova incorreta". A realidade é pior e mais simples: **é a mesma álgebra, copiada**, e a divergência (F4/F5) está em `spi/ceiling.py`, uma reimplementação de 55 LOC feita *ao lado* da cópia de 450 LOC correta. Alguém copiou o módulo certo e depois escreveu um segundo comparador em vez de chamá-lo.

Kernel e canonicalização estão em 70–93% de similaridade — isto é pior que cópia pura: são **forks já em divergência**, com correções aplicadas de um lado só.

### 1.2 O que o fork deixou para trás

| Capacidade | `vanguard/packages/` (legado) | `layer0/` (o "novo") | O plano 0.6.0 agenda para |
|---|---|---|---|
| Durabilidade | `SqliteEventStore`: WAL, `synchronous=FULL`, `BEGIN IMMEDIATE`, `RLock`, append atômico com validação de monotonicidade | `InMemorySink` (lista Python) | **Wave 2, Sprint 2.1** |
| Juiz exterior | `EvaluatorDaemon`: processo separado, UID 10002, UDS com `SO_PEERCRED`, `VerdictSigner` Ed25519 real, digest de imagem no handshake | `verdict: "pass"` literal | **Wave 1, Sprint 1.1** |
| Sandbox | `RootlessSandboxRunner` + bwrap, falha **fechada** se ausente | `subprocess` + rlimits | **Wave 3, Sprint 3.2** |
| Model gateway | `openrouter.py` (896 LOC): SSE streaming incremental, custo em micros, estimativa de tokens, redaction, cassettes, roteamento multi-provider | inexistente | **Wave 5, Sprint 5.1** |
| Loop de agente real | `HarnessSession.run()` + `lab_driver` com modelos mock/ollama/openrouter/deepseek | `SequentialTurnDriver` que encerra no primeiro turno bem-sucedido | **Wave 5** |
| Ledger/projeções | reducer 478 LOC + projections 339 LOC | `fold.py` 151 LOC | **Wave 2** |

**Aproximadamente 60–70% do plano 0.6.0 é reconstrução de código que já está no repositório e passa em teste.**

### 1.3 O bug F1 já tinha sido corrigido uma vez

Docstring de `vanguard/packages/runtime/lab_driver.py`, no repositório, hoje:

> *"This driver used to fabricate its result. It read the manifest, never composed anything, never ran a turn, and returned `{"status": "completed", "turnCount": 1}` regardless of what the task was or whether any work happened. A harness that reports completion for work it did not do is worse than one that reports nothing."*

O F1 (`verdict: "pass"` incondicional no `layer0/scheduler/driver.py`) **é a mesma patologia, recorrendo no fork**, porque o fork copiou a estrutura e não a correção. Isto não é Goodhart — Goodhart explica por que o gate não pegou. A causa raiz é **fork sem gate de convergência**.

### 1.4 O CI protege o código errado

```yaml
# .github/workflows/ci.yml — o que roda:
test.test_repo_paths · test/layer0 · test/packs · 8 gates lexicais
```

```
test/layer0/     545 LOC de teste  → 25 testes, 0,014 s   ← ÚNICO gate de CI
test/runtime/   6016 LOC de teste  → não roda em CI
test/contracts/ 2720 LOC           → não roda em CI
test/agency/    2358 LOC           → não roda em CI
test/adapters/  2171 LOC           → não roda em CI
test/kernel/    1523 LOC           → não roda em CI
```

O `layer0/` (4.556 LOC) é gateado por **25 testes que rodam em 14 milissegundos** — nada toca disco, processo ou modelo. Os ~15.000 LOC de teste que exercitam o runtime real **nunca rodam**. Este é, isolado, o defeito mais grave do repositório: *a verdade de execução não é medida onde o código é load-bearing.* Explica mecanicamente como o `verdict: "pass"` sobreviveu meses.

### 1.5 Estado real da suíte

```
python3 -m pytest test/ --ignore=test/broken --ignore=test/runtime/fixtures
→ 1062 passed · 52 failed · 8 skipped · 39.079 subtests passed · 25,8 s
```

Não são "4 testes frágeis de 1106" como o v3 registra. São **52**, dominadas por ausência de `bwrap` neste container — e a falha é **correta**: o runtime recusa compor efeitos de produção sem sandbox rootless (`CompositionError`). Isso é fail-closed exemplar. Mas significa que o caminho real do agente é **não testável sem bubblewrap** e **não testado em CI**.

### 1.6 O gargalo real de modularidade

`vanguard/packages/runtime/root.py` — **1.418 LOC** contendo `Harness`, `HarnessSession`, `Runtime`, `LedgerBridge`, `_LayeredOperator`, `SessionPorts`, `_SwappablePolicy` e as funções de binding. É o composition root **e** o runtime de sessão **e** a ponte de ledger **e** o operador em camadas, tudo num módulo. Nenhum dos dois documentos anexos menciona este arquivo.

É aqui que a modularidade morre na prática — não no `layer0/`.

---

## 2. Por que o plano 0.6.0 falha

O plano é intelectualmente sólido (§4 do v3 é excelente: CALM, Lamport, McNemar, FDR, outbox transacional, JCS vs Protobuf — tudo correto e bem fundamentado). O problema não é o raciocínio; é a premissa factual sobre a qual ele opera.

**Premissa do plano:** *"a semântica de produção foi adiada; portanto construa-a corretamente num substrato novo."*
**Realidade verificada:** *"a semântica existe e foi abandonada num fork; portanto convirja, não construa."*

Três consequências:

**(a) Terceira reescrita = terceiro fork.** O próprio v3 diagnostica que dois sistemas em paralelo é "o estado de custo máximo e benefício zero" — e então propõe um terceiro. O modo de falha do projeto é reescrever ao lado em vez de convergir. Um substrato 0.6.0 construído ao lado reproduz exatamente as condições de F1: forma nova, semântica pendente, gate verde.

**(b) A disciplina anti-Goodhart não impede fork-drift.** §0.4 do plano de execução é ótima e deve ser mantida integralmente. Mas nenhum dos gates propostos teria detectado que `selectors.py` existe duas vezes. Falta um gate de **unicidade de implementação**, não só de comportamento.

**(c) O sequenciamento inverte prioridade e risco.** M0 é higiene documental (semanas). M1–M2 reconstroem o que existe (meses). O usuário pediu explicitamente para não focar em documentos e lixo — e está certo. Mas o corolário não é "reescreva o core"; é "vá direto ao que não existe".

**O que o plano acerta e deve ser preservado integralmente:**

- §0.4 disciplina de gates comportamentais + teste plantado permanente (`test_planted_*_fails_closed`)
- C-1…C-5 (trilha de cognição): atribuição no envelope, causa nomeada, custo 6-dim, pré-registro. **Isto é a coisa mais valiosa dos dois documentos** — dado não capturado no momento do evento é irrecuperável, e isto precisa entrar antes de qualquer massa de dados.
- §0.8 condições de saída do legado sem data de deleção
- Diferimento do Rust atrás de portão numérico (§Gate de Decisão Rust) — correto e honesto
- JCS para identidade, Protobuf só transporte (S-12)
- Ordem parcial com `project_id` como unidade de consistência (S-11) e as condições C1–C6
- Descarte do corpus contaminado (ADR-060-09)

---

## 3. As cinco lacunas que nenhum dos documentos endereça

Estas são as coisas que realmente separam o repositório de hoje do produto descrito ("framework Harness builder + projeto autônomo agêntico, plugins trocáveis em qualquer tecnologia").

### G1 — A SPI é in-process; o produto exige que seja wire

Este é **o achado arquitetural mais importante para o objetivo declarado**.

`layer0/spi/interfaces.py` define `IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`, `IEvaluationGate` como `typing.Protocol` do Python. Um `Protocol` é verificado em tempo de import, no mesmo processo, no mesmo interpretador.

> "poderemos depois trocar caixas independentes… o plugin de memória de curto prazo, ou de longo prazo, compressão, self improvement etc. Usando protocolos padronizados e universais"

**Isso é impossível atrás de um `Protocol` Python.** Não se pluga um plugin de memória em TypeScript, Rust ou Go num `typing.Protocol`. A fronteira de substituição e a fronteira de processo precisam ser **a mesma fronteira**.

O repositório tem a semente certa e não a usou: `layer0/spi/jsonrpc.py` (JSON-RPC 2.0 line-delimited) + `layer0/registry/broker.py` (308 LOC: FSM de célula, UDS, rlimits, contenção de crash). **Esta é a única coisa genuinamente nova que o `layer0/` construiu.** Mas `registry/worker.py` é fixture (`echo`/`fs.read` com eco literal — F7), então a fronteira nunca foi exercitada por um plugin real.

**Correção:** o contrato de plugin passa a ser **wire-first**. As 5 SPIs viram métodos JSON-RPC sobre UDS, com handshake (versão de protocolo + digest de artefato), deadline, cancelamento, erro estruturado e streaming. O `Protocol` Python vira um *cliente conveniente* do protocolo, não o protocolo.

### G2 — Não existe orquestrador

O objetivo declarado: *"orquestrador central registrando todos os eventos dos diferentes harnesses agents sendo executados em paralelo"*.

Hoje existe `Runtime.compose()` (constrói um harness) e `HarnessSession.run()` (roda **uma** sessão, in-process, sequencial). Não existe nenhum componente que: conceda leases, agende N harnesses, mantenha máquina de estados de projeto, detecte agente morto, reatribua trabalho, ou agregue orçamento entre filhos. O `spawn()` do `layer0` emite `CHILD_SPAWNED` e `CHILD_RETURNED` imediatamente com `spans: []` — não cria nada.

Isto é **construção nova legítima**. É onde o esforço deve ir.

### G3 — `root.py` é o gargalo de modularidade

1.418 LOC misturando composição, execução de sessão, bridge de ledger e operador. Enquanto isso não for quebrado, "trocar o plugin de contexto" continua sendo uma edição no composition root.

### G4 — O CI não mede o que é load-bearing

§1.4. Correção de um dia, maior alavancagem do repositório inteiro. Sem isso, todo gate comportamental proposto no plano 0.6.0 é teatro, porque roda sobre 4.556 LOC de andaime enquanto 21.298 LOC reais ficam sem rede.

### G5 — Concorrência determinística

O legado também é single-session. As seis condições C1–C6 do v3 estão corretas e são construção nova. C5 (merge determinístico) e C4 (TOCTOU via `openat`) são as mais fáceis de errar.

---

## 4. Arquitetura-alvo

### 4.1 Quatro anéis, uma fronteira de processo

```
┌─ ANEL 3 — CLIENTES E APRENDIZAGEM ────────────────────────────┐
│  CLI · GUI · IDE · Analytics · Experiment Service              │
│  Meta-Harness (propõe variantes) · Promotion Controller        │
│  → leitores do ledger; único writer é o ponteiro de promoção   │
└──────────────────────────┬────────────────────────────────────┘
                           │ ledger read-only / promotion signed
┌─ ANEL 1 — CORE / TCB ────▼────────────────────────────────────┐
│  Orchestrator  ·  Ledger  ·  Capability & Budget Kernel        │
│  Plugin Supervisor  ·  Project State Machine  ·  Leases        │
│  domain-blind · nunca importa plugin · alvo ≤ 5k LOC           │
└──────────────────────────┬────────────────────────────────────┘
                           │  ═══ FRONTEIRA DE PROCESSO ═══
                           │  work lease + JSON-RPC/UDS (nunca grant bruto)
┌─ ANEL 2 — PLUGINS (qualquer linguagem) ──▼────────────────────┐
│  Planner · Context · Memory · Model Gateway · Toolkit          │
│  Evaluator · Cache · Compressor · Skills · Merge Policy        │
│  cada um: digest próprio · versão própria · cela isolada       │
└───────────────────────────────────────────────────────────────┘
┌─ ANEL 0 — CONTRATO (schemas, zero código) ────────────────────┐
│  JSON Schema → tipos gerados Py/TS/Rust · golden vectors       │
│  Envelope v2 · EffectRequest · Receipt · Verdict · Manifest     │
│  identidade em JCS (RFC 8785) · única coisa congelada          │
└───────────────────────────────────────────────────────────────┘
```

**Duas regras que o código de hoje viola e que definem o produto:**

1. **A fronteira de substituição é a fronteira de processo.** Se um componente é trocável, ele fala wire. Se ele fala `import`, ele é core. Não há terceira categoria. Isto elimina a discussão de "qual linguagem" — o core é uma implementação, os plugins são outras.

2. **O orquestrador é dono do tempo; o harness é dono do turno.** Hoje `HarnessSession.run()` é dono do loop inteiro, o que torna N harnesses em paralelo estruturalmente impossível. Inverter: orquestrador emite lease → harness executa turno → reporta → orquestrador decide.

### 4.2 Contrato de plugin v1 (concreto)

Framing: line-delimited JSON-RPC 2.0 sobre UDS (já existe em `layer0/spi/jsonrpc.py` — manter). O que falta:

```
handshake     → { protocol: "vg.plugin/1", artifact_digest, spi: "planner|context|memory|model|toolkit|evaluator", capabilities[] }
describe      → schema de verbos, requisitos de recurso, config schema
init          → config resolvida + work lease (NUNCA grant bruto)
invoke        → { method, params, deadline_ms, idempotency_key, cancel_token }
invoke_stream → frames incrementais (obrigatório para model gateway)
checkpoint    → estado serializável para hot-swap
quiesce/shutdown
health/ready  → separados (readiness ≠ liveness)
```

Toda resposta carrega `{ cost: {usd_micros, millis, tokens, bytes, turns, depth}, cause?: <taxonomia fechada> }` — C-3 e C-4 são obrigatórios **no protocolo**, não numa convenção. É a única forma de garantir que a trajetória seja linha válida de harvest (C-1) sem transformação posterior.

**Gate que define sucesso:** um plugin de memória escrito em **TypeScript** passa a mesma suíte de conformidade que o de Python, com `git diff` do core vazio. Enquanto isso não rodar, o produto "framework de harness" não existe — existe uma aplicação Python bem organizada.

### 4.3 Envelope v2 — atribuição desde o primeiro evento

Adotar integralmente §5.2 do v3, com ênfase no que é irreversível:

```
project_id · run_id · agent_id · harness_digest · plugin_digests[] · model_route
project_seq · agent_seq · prev_digest · hybrid_logical_clock
causation_id · correlation_id · command_id · idempotency_key
payload_digest | blob_ref            ← conteúdo fora do envelope
cost{6-dim} · cause? · kind · occurred_at · principal
```

`harness_digest` + `plugin_digests` + `model_route` no envelope são **não-negociáveis desde o primeiro commit do orquestrador**. Sem eles, todo par DPO colhido depois é confundido com o harness (v3 §4.7, e está certo) e a lacuna é irreparável retroativamente.

---

## 5. Plano de construção

Sequência por risco e por valor, não por camada. Cada fase tem gate comportamental — o código mais preguiçoso que passaria deve ser escrito primeiro e comitado como teste negativo (§0.4 do plano de execução, mantida).

### P0 — Verdade de execução · 3–5 dias

Maior alavancagem do repositório. Nada mais é verificável antes disto.

- CI roda a suíte inteira. Runner com `bubblewrap` instalado; marker `requires_sandbox` para separar ambiente de defeito.
- `check_event_coverage.py` sai de normativo (é grep — F2). Substituído por property test: payload varia com input, **falha se constante**.
- `test/gates/test_planted_failures.py`: para cada gate atual, o código preguiçoso que o satisfaz, comitado como teste que **deve** falhar.
- Baseline de performance registrado: append p50/p95/p99, spawn de cela, turno completo com cassette.

**Gate P0:** CI cobre ≥ 95% do LOC executável · todo gate lexical retirado ou substituído · plantados falham fechado · baseline versionado.

### P1 — Convergência de látice · 2–3 semanas

Matar o fork. Não construir nada novo.

- Extrair o núcleo canônico compartilhado para um pacote único (`core/`): álgebra de seletores, canonicalização JCS, kernel de capabilities/budget, taxonomia de eventos, tipos gerados. **Uma implementação, um dono.**
- `layer0/` deixa de existir como látice. Três coisas são promovidas para o core, o resto é deletado:
  - `spi/interfaces.py` — as 5 SPIs (design correto, vira base do contrato wire)
  - `spi/jsonrpc.py` + `registry/broker.py` + `registry/sandbox.py` — a célula de plugin fora de processo (**a única capacidade genuinamente nova**)
  - `spi/types_gen.py` — disciplina de tipos gerados de schema
- Deletar: `events/selectors.py` (cópia), `kernel/*` (fork divergente), `events/envelope.py` (regressão sem durabilidade), `spi/ceiling.py` (duplicata mais fraca — passa a delegar), `scheduler/driver.py` (sintético), `registry/worker.py` (fixture).
- **Novo gate de CI:** `tools/check_duplication.py` — nenhum módulo com similaridade > 0,85 contra outro módulo do repo. Falha o build. *Este é o gate que teria impedido o defeito raiz e não existe em nenhum dos dois planos.*
- Corrigir F5 no ato: `capabilities` obrigatório em schema; ausência = fail-closed.

**Gate P1:** zero par de módulos com similaridade > 0,85 · uma única álgebra de seletores no repo (verificado por AST, não grep) · suíte inteira verde · `git diff --stat` mostra deleção líquida ≥ 3.000 LOC.

### P2 — Fronteira de plugin real · 4–6 semanas

**A fase que define o produto.**

- Contrato de plugin v1 (§4.2) em JSON Schema; SDK cliente gerado para Python **e** TypeScript.
- Migrar o **Model Gateway** para fora de processo primeiro — é I/O-bound (custo de IPC irrelevante), tem streaming (exercita o caso difícil), e já existe pronto em `adapters/models/openrouter.py`.
- Substituir `registry/worker.py` (fixture) por supervisor genérico: deadline, cancelamento cooperativo, backpressure, fila limitada, crash-loop backoff, circuit breaker.
- Identidade de plugin sobre bytes: `H(JCS(manifest) ‖ H(artifact) ‖ H(assets) ‖ H(prompts) ‖ H(policies))` — corrige F8.
- `container` rootless como tier default para toolkits e código de modelo; rede default-deny.
- Teste que falha se a chave do avaliador for alcançável de qualquer cela.

**Gate P2:** um plugin de memória em **TypeScript** e um em Python passam a mesma suíte de conformidade · `git diff` do core vazio ao trocar · 1 byte alterado no artefato ⇒ digest do plugin muda ⇒ digest do harness muda · fault injection na cela não derruba o supervisor · plugin nunca recebe grant bruto (verificado em runtime).

### P3 — Orquestrador e ledger de projeto · 4–6 semanas

- Quebrar `root.py` em: `composition/` (resolve manifest → digest), `session/` (executa turno), `ledger/bridge.py`, `operator/`. Nenhum módulo > 400 LOC.
- Processo orquestrador: máquina de estados de Project/Run/Agent (puras), um lease autoritativo por projeto, dedupe de comando por `(command_id, idempotency_key)`, heartbeat, cancelamento, recuperação.
- Envelope v2 com `project_seq`/`agent_seq` (corrige F3) e atribuição completa (C-2).
- Append serializado **por projeto** com lock explícito — a corrida do F3 vira impossível por construção, em Python, sem Rust.
- Outbox transacional: estado + evento + outbox em uma transação. CAS com `write → fsync → emit(blob_ref)`.

**Gate P3:** `kill -9` entre qualquer command e event ⇒ sem perda nem duplicação lógica · replay cold-start reconstrói 100% do estado observável · dois harnesses sob um orquestrador, eventos intercalados, replay determinístico · mutation score ≥ 80% em kernel + reducers.

### P4 — Coding agent com evidência real · 4 semanas

Aqui F1 morre na origem, não por patch.

- O veredito assinado é **lido e determina o resultado**. Injetar `fail` ⇒ o run falha. Assinatura inválida ⇒ rejeição. (O `EvaluatorDaemon` já existe — é wiring, não construção.)
- Trajetória com digest real sobre o conteúdo, não `sha256:000…`.
- `InvalidationChecked` com semântica; `CLAIM_RECORDED` derivado de evidência.
- Corpus pequeno, determinístico, pré-registrado. Cassettes para regressão, modelo vivo no gate de release. **Piso A/A obrigatório** desde o primeiro dia — é o ativo mais subestimado do projeto.

**Gate P4:** tarefa real ⇒ diff não-vazio em disco + verdict assinado não-mockado · toda model/tool call rastreável até plugin, versão, harness e pai causal · nenhum conceito de coding no core (grep + pack de outro domínio compila) · A/A dentro do orçamento de falso positivo pré-registrado.

### P5 — Paralelismo seguro · 4–6 semanas

As seis condições do v3 §4.4, na ordem: C1 (disjunção via álgebra única, já garantida em P1) → C2 (aliasing: realpath/inode ou proibição de symlink) → C3 (canal lateral: container + net deny) → C4 (TOCTOU: migrar `fs.*` para `openat`/`*at()`) → C5 (merge determinístico por `(project_seq, agent_id, agent_seq)`) → C6 (idempotência/compensação).

Admission control por **pior caso simultâneo**, não soma esperada.

**Gate P5:** duas execuções ⇒ ledger byte-idêntico sob concorrência · zero corrida em stress · revogação de capability interrompe trabalho em andamento · ganho de latência **medido** contra sequencial.

### P6 — Plano de aprendizagem e meta-harness

Adotar R7–R8 do v3 e Waves 9–10 do plano de execução sem alteração — estão corretos. Ênfase: pré-registro com regra de parada, correção de múltiplos testes (Holm para *k* pequeno, BH/FDR para *k* grande), MDE e IC reportados, tamanho do corpus derivado de power analysis (não de número arbitrário), rollback por ponteiro de registry, artefatos nunca sobrescritos, e harvest apenas de episódios com evidence válido.

---

## 6. O que aproveitar, o que reescrever, o que deletar

| Ativo | Situação verificada | Decisão |
|---|---|---|
| `packages/domain/` (canonicalização, seletores, ledger, evidence, primitives) | Real, testado, é o fosso | **Manter** — vira `core/` |
| `packages/kernel/` (dispatch, grants, atenuação) | Real, sólido, gates passam | **Manter** |
| `packages/adapters/stores/` (SQLite WAL, blob, memory) | Durabilidade real já implementada | **Manter** — economiza a Wave 2 inteira |
| `packages/adapters/evaluators/` (daemon, signing, client, isolated) | Juiz exterior Ed25519 real, UID separado, SO_PEERCRED | **Manter** — economiza a Wave 1 |
| `packages/adapters/models/` (openrouter, ollama, cassette, routing) | SSE streaming, custo micros, redaction | **Manter** → primeiro plugin fora de processo (P2) |
| `packages/adapters/sandbox/` (rootless bwrap) | Real, falha fechado | **Manter** → base do tier `container` |
| `packages/ports/` | Contratos hexagonais bem separados | **Manter** → viram schemas do Anel 0 |
| `packages/agency/` (episode, context, manifests) | Real | **Manter**, refatorar para plugin |
| `packages/runtime/root.py` | God module de 1.418 LOC | **Refatorar** (P3) — 4 módulos |
| `packages/runtime/service/` | asyncio, inbox | **Avaliar** como base do orquestrador |
| `layer0/spi/interfaces.py` | Design correto das 5 SPIs | **Promover** → base do contrato wire |
| `layer0/spi/jsonrpc.py` + `registry/broker.py` + `registry/sandbox.py` | Única capacidade genuinamente nova | **Promover e endurecer** (P2) |
| `layer0/spi/types_gen.py` + `schemas/` (388 JSON) | Disciplina de geração | **Promover** → Anel 0 |
| `layer0/events/selectors.py` | Cópia (diff = 2 linhas) | **Deletar** |
| `layer0/kernel/*` | Fork divergente (sim. 0,70) | **Deletar** |
| `layer0/events/envelope.py` | Regressão: sem durabilidade, sem project_seq | **Deletar** → Envelope v2 no core |
| `layer0/spi/ceiling.py` | Duplicata mais fraca, aceita travessia | **Deletar** → delega à álgebra única |
| `layer0/scheduler/driver.py` | Veredito sintético (F1) | **Deletar** → orquestrador em P3 |
| `layer0/registry/worker.py` | Fixture de eco (F7) | **Deletar** → supervisor genérico em P2 |
| `check_event_coverage.py` | Grep (F2) | **Deletar** → property test |
| Corpus/trajetórias existentes | Contaminados por veredito fabricado | **Descartar** (ADR-060-09 está certo) |
| `vanguard-gui/`, `vanguard-ide/` | Fora do escopo de backend | Repositórios próprios consumindo contrato gerado |

**Balanço:** ~2.900 LOC deletados do `layer0/`, ~1.100 LOC promovidos, ~21.000 LOC preservados e reorganizados. Contra o plano 0.6.0, que preserva ~1.100 e reconstrói o resto.

---

## 7. Performance — onde o custo realmente está

Advertência necessária, porque a pergunta "deixar mais performático" tem uma resposta contraintuitiva neste domínio.

Perfil de latência de um turno de agente, por ordem de grandeza:

| Componente | Ordem | Observação |
|---|---|---|
| Chamada de modelo | 10⁰–10¹ s | domina tudo, 90–99% do tempo de parede |
| Spawn de sandbox (bwrap fork/exec) | 10–200 ms | **por efeito**, se não houver pool |
| `fsync` no append do ledger | 1–10 ms | agrupável |
| IPC JSON-RPC sobre UDS | 0,1–1 ms | irrelevante |
| Overhead do interpretador Python | µs | irrelevante |

Conclusões operacionais:

1. **Trocar Python por Rust otimiza a linha que menos importa.** O v3 já diz isso em §5.6 e está certo; o plano de execução acerta ao diferir atrás de portão numérico. Mantenha.
2. **Célula de plugin de vida longa, não fork por efeito.** Se cada `fs.read` faz spawn de bwrap, o overhead de sandbox vira o segundo maior custo do sistema. A célula deve nascer uma vez por sessão e receber invocações — o `PluginCell` FSM do broker já está estruturado para isso.
3. **Group commit no ledger.** Agrupar appends numa transação por janela curta corta fsync por ordem de grandeza sem relaxar durabilidade — o commit continua atômico, só é compartilhado.
4. **Paralelismo de agentes é ganho real; paralelismo dentro do agente não é.** O agente é sequencialmente dependente (observar → planejar → agir). O ganho vem de N projetos/agentes concorrentes, que é exatamente o que P3/P5 destravam.
5. **Nada disso entra sem profile reproduzível.** Baseline em P0, regression budget desde P3.

---

## 8. Riscos

| ID | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| R-1 | **Terceiro fork** — o time constrói o substrato ao lado em vez de convergir | **Alta** (padrão já ocorreu 2×) | Crítico | P1 antes de tudo; `check_duplication.py` como gate de merge |
| R-2 | CI continua medindo andaime | Alta se P0 pular | Crítico | P0 é pré-requisito de todo o resto |
| R-3 | Fronteira de plugin fica in-process "por enquanto" | Alta | Crítico ao produto | Gate P2 exige plugin TS rodando; sem ele não há framework |
| R-4 | Goodhart recorre em gate novo | Alta | Alto | Teste plantado obrigatório por gate (§0.4 do plano — manter) |
| R-5 | Deleção do `layer0` perde algo não mapeado | Média | Médio | P1 promove antes de deletar; teste diferencial contra a suíte atual |
| R-6 | `root.py` resiste ao corte por acoplamento | Média | Alto | Caracterizar com testes antes (Feathers); um módulo por PR |
| R-7 | Promoção por ruído no meta-harness | Alta sem correção | Crítico | FDR + MDE + A/A + holdout + pré-registro (v3 §4.5 está correto) |
| R-8 | Corpus contaminado alimenta treino | Certa para dados atuais | Alto | Descartar tudo pré-P4 |

---

## 9. Primeiro incremento

O plano de execução propõe começar por `GATES.md` + testes plantados. **Concordo com o espírito e discordo do primeiro PR** — a disciplina de gate é necessária mas insuficiente, porque nenhum gate comportamental detecta um fork.

**PR #1 (1 dia):**
1. `.github/workflows/ci.yml` — roda a suíte inteira; `bubblewrap` no runner; marker `requires_sandbox`.
2. `tools/check_duplication.py` — falha se dois módulos têm similaridade > 0,85. Roda como gate.
3. `test/gates/test_planted_failures.py` — o código preguiçoso de cada gate atual, comitado como teste negativo.
4. `check_event_coverage.py` marcado não-normativo.
5. `docs/00_guidelines/GATES.md` com §0.4 do plano de execução, acrescida de: *"nenhum gate detecta código duplicado; unicidade de implementação é gate estrutural separado."*

**Racional:** o PR #1 instala simultaneamente a disciplina que teria detectado `verdict: "pass"` **e** a que teria detectado o fork. O plano anexo instala só a primeira.

**PR #2–#5 (2–3 semanas):** P1 completo — convergência de látice, deleção líquida do `layer0`, promoção das três peças que valem.

---

## 10. Conclusão

O projeto tem um fosso real e ele é maior do que os documentos anexos reconhecem — porque eles subestimam o próprio legado. Existem, funcionando e testados neste repositório: canonicalização JCS com golden vectors, álgebra de seletores formal, kernel de capabilities com atenuação, ledger SQLite WAL transacional, avaliador exterior com Ed25519 e identidade de processo separada, sandbox rootless que falha fechado, model gateway com streaming e contabilidade de custo em seis dimensões. Nenhum concorrente tem esse conjunto.

O que aconteceu não foi degradação de qualidade — foi **um fork sem gate de convergência**. Alguém copiou o núcleo para uma pasta nova, deixou a semântica para trás, e um gate lexical atestou conclusão. O `verdict: "pass"` é o sintoma; o fork é a doença. E a doença tem uma propriedade que a torna especialmente perigosa: **ela se apresenta como progresso**, porque a látice nova sempre parece mais limpa que a antiga — ela é mais limpa exatamente na proporção do que deixou de fazer.

A decisão correta não é uma terceira reescrita. É:

**convergir a látice → restaurar a verdade de CI → empurrar a fronteira de plugin para fora do processo → construir o orquestrador que nunca existiu → ligar o veredito real que já está pronto → paralelizar sob as seis condições → só então aprender com os dados.**

Rust, se entrar, entra depois de P5 com números medidos — e provavelmente só no append do ledger e no kernel, ~15% do backend, como o plano de execução já concluiu corretamente.

Duas regras devem sobreviver a este documento:

1. **Gate lexical mede sintaxe; gate comportamental mede semântica; nenhum dos dois mede unicidade.** O terceiro eixo precisa de gate próprio, e é o que faltava.
2. **Se um componente é trocável, ele fala wire. Se ele fala `import`, ele é core.** Não há terceira categoria — e é essa regra, mais que qualquer escolha de linguagem, que decide se isto vira um framework ou continua sendo uma aplicação Python bem organizada.

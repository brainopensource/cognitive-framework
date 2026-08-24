# TODO W-3D Final — Rebaselining the AETHER Product Runtime

| ID | Estado | Entrega | Arquivos principais | Gate objetivo |
|---|---|---|---|---|
| W3D-00 | TODO | Autorizar W-3D e separar produto, contenção e certificação | `docs/SPEC.md`, `docs/01_law/{RUNTIME,SECURITY,DISPATCH,EXTENSIBILITY,EVIDENCE}.md`, novo ADR-0089, `docs/03_execution/{sprint_active,milestones}.md` | Lei, ADR e board concordam antes do código |
| W3D-01 | TODO | Congelar baseline e criar falsificadores RF-87…RF-94 | `test/falsifiers/`, `tools/linters/check_falsifier_ids.py`, board | RED reproduz cada acoplamento atual |
| W3D-02 | TODO | Introduzir `ExecutionProfile` ortogonal e identity-bearing | novo schema de profile, `domain/artifacts/manifest.py`, `runtime/profiles.py`, `runtime/run_plan.py` | perfil efetivo entra em `D_R`, nunca altera silenciosamente `D_H` |
| W3D-03 | TODO | Tornar `Runtime` fino e injetar dependências concretas fora do loop | `runtime/{root,bootstrap,session,compose,wiring}.py` | nenhuma seleção de provider/store/sandbox dentro do mecanismo de execução |
| W3D-04 | TODO | Segurança portátil, explícita e capability-based | `ports/sandbox.py`, `adapters/sandbox/{rootless,platform}.py`, `adapters/environment/{git,sandboxed}.py`, `runtime/profiles.py` | WSL2 não é negado por nome; sandbox solicitado nunca cai silenciosamente para host |
| W3D-05 | TODO | Separar filesystem rápido de subprocesso confinado | `runtime/wiring.py`, adapters de environment/sandbox, packs de tools | `fs.read/search/write` não pagam bwrap; `proc.exec` usa backend do perfil |
| W3D-06 | TODO | Fazer plugins/componentes realmente ativarem serviços | `runtime/activation.py`, `runtime/registry/`, `runtime/compose.py`, `packs/code-default/` | produção não ativa componentes com `cell=None`; teardown é reversível |
| W3D-07 | TODO | Convergir pack canônico e criar `code-explain` por reutilização | `packs/code-default/`, novo `packs/code-explain/`, `agency/manifests/`, schemas | coding e explain usam os mesmos plugins/tools sem duplicar implementação |
| W3D-08 | TODO | Criar entrypoint genérico e unir CLI, daemon e one-shot | novo `runtime/entrypoint.py`, `runtime/service/`, `clients/client-core/`, `clients/cli/` | `vg code` e `vg explain` executam pelo mesmo `Runtime.run_composed` |
| W3D-09 | TODO | Unificar persistência e streaming sem criar segunda verdade | `runtime/ledger_emitter.py`, novo `runtime/event_stream.py`, `runtime/service/`, `ports/event_store.py` | store durável é verdade; live stream é fan-out/replay, não outro ledger |
| W3D-10 | DONE | Tornar evidência e evaluator políticas de assurance | `runtime/assurance.py`, `runtime/foundation_evidence.py`, profiles | local é executável e não-promocional; hermetic continua fail-closed |
| W3D-11 | DONE | Entregar Developer Preview no WSL2 | CLI, packs, integração e UX | coding + explain local pelo runtime comum, doctor com fatos reais, file-backed, sem bwrap obrigatório |
| W3D-12 | DONE | Remover shims, caminhos mortos e duplicação após paridade | loaders/compilers antigos, `lab_driver.py`, manifests legados, testes | RF-94 prova uma única autoridade; duplication/boundary gates verdes |
| W4-01 | IN_PROGRESS | Requalificar baseline e executar RF-85 hermético | release runner, sandbox/evaluator/WAL/evidence | nove linhas reais em uma lineage; WSL2 é aceito somente se passar os mesmos probes |
| W5-01 | LOCKED | Formal Pack #2 e prova de generalidade | novo `packs/formal-*`, adapter/checker/testes | RF-86; zero diff semântico no substrato durante o intervalo de prova |
| W6-01 | LOCKED | `agent.spawn` mediado | `runtime/delegation.py`, adapter de spawn, schemas/testes | RF-55…RF-59; autoridade, budget, lineage e recovery atenuados |
| W7-01 | PLANNED | Medir e decidir concorrência limitada | scheduler/measurement exterior, testes RF-46…RF-48 | benefício reproduzível antes de levantar I-11 |
| W8-01 | PLANNED | Topologias declarativas e Beta | packs/policies/topology data, sem diff de kernel/episode | RF-65/RF-66; reference topologies e release review independente |

## 1. Status, autoridade e decisão recomendada

Este relatório é um artefato de planejamento não canônico. Ele não autoriza implementação, não altera a Lei e não fecha M-4. A nomenclatura canônica do repositório é `M-*` para milestones e Wave/Sprint para execução. O nome `W-3D` é mantido aqui porque foi solicitado; se aprovado, o Director deve decidir se o gate será registrado como **Wave 3D dentro de M-4**, **M-3D**, ou **M-4.0 Product Runtime Correction**. Não se deve criar três nomes concorrentes nos documentos vivos.

A recomendação é pausar o início de qualquer candidato RF-85, abrir formalmente **W-3D Product Runtime Profiles**, implementar e revalidar RF-78…RF-84, congelar uma nova baseline e só então retomar M-4. Isso é necessário porque a Lei vigente declara que “M-4 adds no architecture”, mas a correção necessária modifica composição, profiles, bootstrap e a fronteira de isolamento. Fazer isso escondido dentro de M-4 tornaria a evidência do milestone inválida.

Há uma alternativa operacional mais curta: fechar RF-85 agora em uma VM Linux qualificada e realizar W-3D depois. Ela preserva o baseline `1a1ed6c`, mas entrega um certificado antes de entregar um produto utilizável e deixa M-5 bloqueado por um substrato que ainda exige refatoração. É tecnicamente válida, porém não é a melhor decisão de produto. A alternativa recomendada aceita reexecutar os gates de convergência para evitar consolidar o acoplamento atual.

### Decisão central

Separar três eixos que hoje aparecem misturados:

1. **Execução funcional:** um agente usa modelo, contexto e tools para realizar uma tarefa.
2. **Contenção:** onde e com quais limites um efeito físico executa.
3. **Assurance/certificação:** quais identidades, provas, evaluator, WAL e assinaturas tornam o resultado elegível para comparação ou promoção.

Um run local pode ser funcional, persistido, reproduzível e útil sem alegar contenção hermética. Um run hermético continua obrigado a provar tudo que RF-85 exige. Flexibilidade não significa falsificar segurança.

## 2. Diagnóstico baseado no código atual

### 2.1 WSL é o sintoma, não a incompatibilidade fundamental

O runtime Python, o Git environment, SQLite e o CLI não dependem conceitualmente de Linux puro. O bloqueio nasce em `vanguard/packages/runtime/root.py`: o método público constrói diretamente `RootlessSandboxRunner`, cria o bundle selado, escolhe SQLite, escolhe OpenRouter e qualifica containment. O `lab_driver.py` repete parte dessa seleção. Assim, uma decisão de deployment tornou-se uma condição do caminho comum.

O próprio direito vigente já contém `K-46`: degradação para runtime não contido é permitida no desenvolvimento local se ficar visível. Ao mesmo tempo, `RUNTIME.md §3` afirma que todo `proc.exec`/`patch.apply` passa pelo tier container e I-6 descreve plugins como não confiáveis por padrão. A redação não distingue claramente:

- isolamento do **código do plugin**;
- contenção do **efeito solicitado pelo agente**;
- assurance necessária para **publicar ou promover** um resultado.

Essa ambiguidade deve ser corrigida na Lei, não contornada com mais um booleano.

### 2.2 O `host-dev` atual é prova de viabilidade, não desenho final

O modo explícito `host-dev` demonstra que o mesmo `EpisodeEngine`, kernel, ledger e adapters podem operar em WSL sem bwrap. Ele preserva path checks, allowlist, receipts e compensação, e o release o recusa corretamente. Porém a seleção ainda está em `root.py` e `lab_driver.py`; manter esse formato produziria duas listas de modos e duas fábricas de environment. O código deve migrar para um `ExecutionProfile` resolvido uma vez pelo bootstrap.

### 2.3 A composição “plugin” ainda é parcialmente descritiva

`ActivationPlan` ordena componentes e emite `PluginDiscovered → … → PluginRetired`, mas `activate()` usa `build=None` por padrão e armazena `cell=None`. O `HarnessSession` não consome as cinco SPIs ativadas: ele constrói diretamente bindings, kernel, context compiler, operator, index e approval flow. Portanto, o lifecycle prova que metadados foram percorridos, mas não que os serviços declarados foram materializados e usados.

Existem ainda duas famílias de pack:

- `packs/code-default/`: `harness.yaml`, plugin manifests e classes Python;
- `vanguard/packages/agency/manifests/vg-*`: manifests e assets efetivamente localizados pelo runtime público.

O runtime normaliza `/1` e `/2` para `CanonicalManifest`, o que é bom, mas o pack documentado no README não é hoje a única fonte operacional. O código em `packs/code-default/planners/single_planner.py`, por exemplo, produz um patch literal e não é o planner do `HarnessSession`. Isso é uma implementação paralela/experimental, não uma base a ser ampliada sem convergência.

### 2.4 O CLI possui uma fronteira quebrada

`vanguard/clients/client-core/src/application/coding-commands.ts` tenta executar `vanguard.packages.runtime.coding_entrypoint`, módulo que não existe. `vg code` e `vg explain` usam o mesmo `CodingRequest`, mas não selecionam dois harnesses reais; o `explain` de `runtime/explain.py` serve `vg why` para explicar artefatos, não para explicar uma codebase. O TypeScript está corretamente fino, mas aponta para uma porta inexistente.

### 2.5 Eventos duráveis e streaming estão duplicados na aplicação

O `LedgerEmitter` é a autoridade de eventos de execução. `RuntimeService`, porém, mantém um `ServiceInboxStore`, publica envelopes em filas próprias e possui `_InboxEventStore` incompleto (`read=()`, digest vazio, count zero). Isso é aceitável como protótipo de transporte, mas não como verdade universal. SQLite-WAL não deve virar “WebSocket”; persistência e fan-out são responsabilidades distintas.

### 2.6 O custo de sandbox está no lugar errado

`RootlessSandboxRunner.execute()` consulta versão, executa três probes e lança outro bwrap para o comando em toda chamada. Além disso, `SandboxedEnvironmentAdapter` pode enviar operações leves de filesystem ao worker. O custo correto é:

- qualificação e probes: uma vez por backend/session;
- leitura, busca e patch estruturado confiável: in-process, com path containment e receipts;
- subprocesso arbitrário/código gerado: backend selecionado pelo profile;
- worker persistente: somente após benchmark demonstrar necessidade.

Não se deve construir agora um daemon bwrap complexo para resolver uma latência que ainda não foi medida no fluxo real.

### 2.7 Revisão independente de `TODO_W-3D_beta.md`

O relatório do junior é útil como inventário inicial, mas não deve ser implementado literalmente.

| Proposta do beta | Veredito | Correção adotada neste relatório |
|---|---|---|
| Extrair `ExecutionProfile` e ligar seu digest a `D_R` | **Correta** | Mantida, com eixos ortogonais em vez de um tier único |
| Separar filesystem leve de `proc.exec` | **Correta** | Mantida; filesystem direto continua sujeito a path/capability policy |
| Cachear probes de bwrap | **Correta** | Qualificação uma vez por session/backend |
| Criar worker bwrap persistente imediatamente | **Prematura** | Medir p50/p95 primeiro; manter spawn por `proc.exec` no MVP |
| “Graciosamente defaultar” de sandbox para local no WSL | **Insegura** | Sem fallback silencioso; novo run/profile local requer escolha ou approval explícita |
| Autoaprovação com assinaturas Ed25519 | **Errada** | Não misturar approval do operador com assinatura do evaluator; nenhuma chave de confiança é mintada para facilitar local dev |
| Criar `apps/coding/entrypoint.py` | **Acoplada ao primeiro caso** | Criar `runtime/entrypoint.py` genérico; coding e explain são packs/agents |
| Exigir JSON-RPC/UDS para todo CLI | **Desnecessária no one-shot** | NDJSON stdin/stdout no one-shot; UDS permanece adapter do daemon |
| Criar novas classes `AgentSpec` e `FlowSpec` agora | **Duplica conceitos e antecipa gates** | `FrozenComposition` já é a definição identity-bearing do agente; flow/topology fica para M-8 |
| ADR-0089 e ADR-0090 simultâneos | **Sprawl decisório** | Um ADR-0089 resolve o blocker atual; topology ADR somente quando M-8 abrir ou RF-66 exigir |
| Registrar todo token e “pensamento” no WAL | **Inviável e arriscada** | Persistir facts de controle; chunks e conteúdo seguem capture/redaction/blob policy opt-in |
| “Zero-overhead” | **Claim não demonstrável** | Definir budgets e medir; zero bwrap em fs leve, não overhead absoluto zero |

O beta também não identifica três fatos verificados que mudam a prioridade: o módulo `coding_entrypoint` está ausente; a ativação de produção normalmente aceita `cell=None`; e `packs/code-default/` convive com os manifests efetivamente consumidos em `agency/manifests/`. Esses três problemas entram como gates explícitos neste plano.

## 3. Arquitetura-alvo

```text
CLI / API / one-shot
        |
        v
Generic RunRequest(agent_id, profile_id, task, workspace)
        |
        v
RuntimeBootstrap -- resolve configuração e adapters concretos
        |
        +--> FrozenComposition / D_H        (o agente/harness)
        +--> EffectiveExecutionProfile      (deployment e policy)
        +--> RuntimeDependencies            (model/store/fs/process/evaluator)
        |
        v
RunPlan / D_R --> ActivationPlan --> HarnessSession --> EpisodeEngine --> Kernel S0-S12
                                         |                    |
                                         |                    +--> EffectAdapter por verbo
                                         +--> LedgerEmitter --> SQLite/EventStore
                                                           \--> EventStream fan-out
```

O kernel, S0–S12, JCS, budgets, grants, writer authority e identity tuple continuam estáveis. A mudança está no composition/bootstrap seam.

### 3.1 Primitivas, moléculas e agentes

Usar a taxonomia apenas como linguagem de produto:

- **Átomo:** uma capability/tool canônica (`fs.read`, `fs.search`, `patch.apply`, `proc.exec`, model invocation, event append, approval, evaluation request).
- **Molécula:** uma política reutilizável sobre átomos, como “inspect → patch → test → repair”. Não é uma nova authority nem um segundo engine.
- **Agente:** `FrozenComposition` + prompt/context policy + capability ceiling + model routes + entrada de execução.
- **Organização:** composição/delegação de agentes via `agent.spawn` quando M-6 abrir.
- **Topologia:** dados declarativos que M-8 reduzirá para scheduling e spawn; não um engine paralelo.

Não criar classes `Atom`, `Molecule`, `Swarm`, `MetaAgent` ou `MetaLoop`. Os contratos existentes já representam os conceitos mecanicamente. Criar uma classe por metáfora repetiria o bloat que o projeto quer remover.

### 3.2 O que é plugin e o que não é

Podem ser plugins/componentes:

- models e roteamento;
- tools e binding providers;
- context sections/compaction;
- memory, index, AST, cache e compression;
- approval policy e sandbox backend;
- event observers/exporters;
- commands e UI projections;
- planners/policies que operem sobre o loop universal;
- adapters de domínio e evaluators agent-side.

Permanecem mecanismo estável, não arbitrariamente substituível por um manifest não confiável:

- tipos wire/JCS e cálculo de identidade;
- writer authority e ledger append privilegiado;
- kernel S0–S12 e atenuação;
- `EpisodeEngine` enquanto loop universal vigente;
- verificação da assinatura exterior;
- decisão de elegibilidade/promotability;
- resolução do profile máximo imposto pelo operador/organização.

O princípio correto é **all product features are plugins; truth and authority are a small core**. Copiar literalmente “everything is a plugin” do DeepSeek removeria a separação de confiança que é uma das partes valiosas do AETHER.

### 3.3 Sem classe mãe universal

Não introduzir `BaseBox`, `BaseAgent`, `BaseTool` ou um service locator sem tipos. Reusar protocolos pequenos e composição. O lifecycle precisa somente de um handle reversível:

```python
@dataclass(frozen=True)
class ComponentHandle(Generic[T]):
    service: T
    close: Callable[[], None]

class ComponentFactory(Protocol[T]):
    def build(self, spec: ComponentSpec, dependencies: Mapping[str, object]) -> ComponentHandle[T]: ...
```

O resolver injeta apenas bindings declarados. O plugin não recebe um `Context` global do qual possa retirar store, evaluator, chaves ou adapters não autorizados. Essa escolha é menos conveniente que um container global, mas mantém a arquitetura hexagonal e evita autoridade ambiente.

## 4. `ExecutionProfile`: contrato novo

Um único `trust_tier` é insuficiente. Ele misturaria contenção, permissões, persistência, evaluator e captura em uma escala artificial. Usar eixos ortogonais e presets nomeados.

### 4.1 Shape proposto

```json
{
  "api": "mhf.execution-profile/1",
  "id": "local",
  "workspace": {"mode": "in-place", "access": "workspace-write"},
  "process": {"backend": "host", "fallback": "deny"},
  "network": {"mode": "inherited", "allow": []},
  "approval": {"default": "ask", "rules": []},
  "persistence": {"mode": "sqlite-wal", "durable": true},
  "evaluation": {"mode": "none", "absence_reason": "local product run"},
  "assurance": {"level": "recorded", "attestation_required": false},
  "capture": {"content": "redacted", "trainability": "prohibited"}
}
```

Campos que alteram execução entram no preimage de `D_R`. O `D_H` continua identificando o agente/harness. O host observado — plataforma, backend, versão, enforcement e probes — também entra em `D_R`. `D_X` permanece reservado ao protocolo/dataset experimental.

### 4.2 Presets built-in

| Profile | Processo | Filesystem | Aprovação | Store | Evaluator | Elegibilidade |
|---|---|---|---|---|---|---|
| `local` | host explícito | workspace-scoped por lógica | ask para efeitos privilegiados | SQLite-WAL local por padrão | `none` declarado | produto/replay; nunca promoção |
| `sandboxed` | backend de plataforma | read-only ou workspace-write | ask/allow/deny por regra | SQLite-WAL | opcional | comparável somente se enforcement suficiente for declarado |
| `hermetic` | backend qualificado sem fallback | workspace selado | política preregistrada | arquivo SQLite-WAL obrigatório | exterior Ed25519 | candidato RF-85/promoção |

O agent `code-explain` usa ceiling read-only independentemente do profile. Selecionar `local` não concede write a um harness que não declara write. A regra efetiva é a interseção:

```text
organization ceiling ∩ selected profile ∩ harness ceiling ∩ agent policy ∩ request
```

Overrides por agente/tool só estreitam. Uma ampliação one-shot exige approval sobre aquela chamada e nunca altera o profile persistido.

### 4.3 Fallback

- `local`: host é o backend solicitado, portanto não é fallback.
- `sandboxed`: backend ausente retorna `sandbox_unavailable`; a UI pode oferecer “reexecutar uma vez em local”, criando novo `D_R` e approval explícita.
- `hermetic`: backend ausente encerra antes do primeiro evento; não existe retry local elegível.

Isso reproduz a ergonomia dos concorrentes sem produzir evidência falsa. Claude Code permite sandbox opcional no Linux/WSL2 e possui `failIfUnavailable`; OpenCode prioriza `allow/ask/deny` por tool/agente; Codex expõe `read-only`, `workspace-write` e `full-access`. O AETHER deve combinar essas ideias com a sua identidade e ledger, não copiar internals de outro produto.

## 5. Plano de implementação detalhado

### W3D-00 — Governança e alterações normativas

Criar `docs/02_decisions/0089-execution-assurance-profiles-and-product-runtime.md` como ADR sucessor de 0088. O ADR deve:

1. registrar o falsificador observado: o produto funcional depende de um mecanismo específico de certificação e o CLI aponta para entrypoint inexistente;
2. abrir W-3D e pausar RF-85 até nova baseline;
3. distinguir plugin isolation, effect containment e assurance;
4. permitir execução local explicitamente não contida e não promocional;
5. substituir bloqueio “non-WSL” por qualificação baseada em capabilities/probes;
6. manter RF-85 hermético, evaluator exterior, WAL e assinatura sem redução;
7. decidir que o profile efetivo pertence a `D_R`;
8. autorizar um runtime loader/factory protocol sem classificá-lo como sexta SPI cognitiva;
9. manter I-11 e proibir DAG/spawn antecipados;
10. alocar RF-87…RF-94;
11. definir rollback para o baseline anterior e reexecução RF-78…RF-84.

Editar atomicamente:

- `docs/SPEC.md`: A-2/I-6, architectural refusals, concept lock e milestone compatibility.
- `docs/01_law/SECURITY.md`: explicar os três eixos e encaminhar para os novos clauses.
- `docs/01_law/DISPATCH.md`: tornar K-34…K-45 requisitos de profiles confinados/herméticos; preservar K-46 e exigir marcação não promocional no local.
- `docs/01_law/RUNTIME.md`: retirar “todo proc.exec/patch.apply sempre container” como regra universal; definir routing por profile e profile identity em `D_R`.
- `docs/01_law/EXTENSIBILITY.md`: definir factory/handle, bindings tipados e limites de pluginização.
- `docs/01_law/EVIDENCE.md`: deixar explícito que `evaluation:none` e containment ausente são válidos para produto, mas sempre `unattributable_for_promotion=true`.
- `docs/02_decisions/INDEX.md`: indexar ADR-0089.
- `docs/03_execution/sprint_active.md`: substituir o único próximo passo RF-85 pela sequência autorizada W-3D; não apagar o histórico de M-4.
- `docs/03_execution/milestones.md`: inserir o gate corretivo, rebaseline de M-4 e labels de release.

Não editar `_archive/`: 001, 006 e Higgs são provenance, não documentação viva.

### W3D-01 — Baseline, RED e proteção contra reescrita

Antes do refactor:

- registrar commit/base exatos e árvore semântica;
- rodar suites atuais e armazenar resultados como artefato CI, não Markdown novo;
- escrever falsificadores antes dos fixes;
- proibir alterações em `kernel/`, canonicalização, budgets, grants e evaluator signing.

Falsificadores propostos:

| RF | Prova negativa |
|---|---|
| RF-87 | seleção de profile fora de `D_R` ou mudança silenciosa de profile preservando `D_R` deve falhar |
| RF-88 | `sandboxed`/`hermetic` indisponível não pode executar no host |
| RF-89 | WSL2 qualificado não pode ser negado apenas pelo nome; WSL1/unqualified não pode alegar containment |
| RF-90 | `vg code` e `vg explain` devem alcançar o mesmo entrypoint/runtime e falhar se módulo/agent não existir |
| RF-91 | code/explain compartilham implementações de tools/model/context; explain não recebe write/exec |
| RF-92 | evento persistido e evento streamed representam o mesmo envelope/seq; reconnect não duplica nem perde |
| RF-93 | componente ativado em produção possui service/handle real e é fechado em ordem reversa |
| RF-94 | nenhum lab, CLI, daemon, repair ou scoring executa um loop/driver concorrente |

Arquivos:

- novos `test/falsifiers/test_rf87_execution_profile_identity.py` até `test_rf94_runtime_authority.py`, agrupando casos quando coesos;
- `tools/linters/check_falsifier_ids.py` apenas se o registro exigir atualização;
- `test/contracts/test_manifest_v2_graph.py` e `test/contracts/test_a1_canonical_composition.py` para os novos contracts;
- fixtures negativas sob os diretórios de teste existentes, nunca em produção.

### W3D-02 — Schema e resolução de profiles

Adicionar `schemas/mhf/execution_profile.schema.json`. O schema deve ser fechado (`additionalProperties:false`), versionado e conter somente configuração, nunca runtime facts observados.

Atualizar:

- `schemas/mhf/manifest_v2.schema.json`: substituir `profiles: object<object>` por refs/presets tipados ou remover sua autoridade em favor do schema separado, conforme ADR. A recomendação é permitir refs nomeadas e resolver os bytes no freeze, mas colocar a **seleção efetiva** em `RunPlan`.
- `schemas/v4/runtime-service.schema.json`: `StartRun` recebe `agentId`, `profileId`, workspace/task/budget; resposta expõe profile solicitado e efetivo.
- `tools/codegen/generate_types.py`: gerar readers Python/TS se o pipeline atual ainda não alcança os novos schemas.
- `vanguard/packages/domain/wire/types_gen.py` e `vanguard/packages/domain/contracts.ts`: somente outputs gerados.
- `vanguard/packages/domain/artifacts/manifest.py`: validar refs e policy floors; não construir adapters.
- novo `vanguard/packages/runtime/profiles.py`: `ExecutionProfile`, `EffectiveExecutionProfile`, resolver de presets e interseção monotônica.
- `vanguard/packages/runtime/run_plan.py`: incluir profile digest, backend solicitado, policies e assurance no preimage de `D_R`.
- `vanguard/packages/runtime/session.py`: `EpisodeStarted` registra `profileId`, `profileDigest`, effective containment e assurance, derivados do `RunPlan`.

Não criar `trust_tier`. Assurance não concede authority e containment não substitui approvals.

### W3D-03 — Runtime fino e bootstrap único

Objetivo: `Runtime.run_composed()` recebe tudo resolvido. Ele não escolhe OpenRouter, bwrap, SQLite ou evaluator.

Adicionar `vanguard/packages/runtime/bootstrap.py` com:

```python
@dataclass(frozen=True)
class RuntimeDependencies:
    model: ModelPort
    store: EventStorePort
    filesystem: EnvironmentAdapter
    process: EnvironmentAdapter
    verifier: EvaluatorPort | None
    approver: ApprovalChannel | None
    clock: ClockPort
    profile: EffectiveExecutionProfile

class RuntimeBootstrap:
    def build(config, profile, workspace) -> RuntimeDependencies: ...
```

Responsabilidades por arquivo:

- `runtime/root.py`: manter facade canônica pequena; `compose`, `execute` e `run_composed`; remover imports/fábricas concretas.
- `runtime/bootstrap.py` (novo): único lugar autorizado a selecionar adapters concretos a partir de config/profile.
- `runtime/model_selection.py`: tornar provider registry/factory reutilizável pelo bootstrap; nenhum default live implícito em release.
- `runtime/compose.py`: continuar compilando `D_H`; não receber ambiente físico.
- `runtime/wiring.py`: resolver verbs a adapters já construídos; remover dependência de um único environment universal.
- `runtime/session.py`: consumir `RuntimeDependencies`/ports e policy efetiva; não construir componentes de deployment.
- `runtime/lab_driver.py`, `runtime/dogfood.py`, `runtime/scoring.py`, `runtime/repair.py`: clientes do mesmo bootstrap/API; não criam environment nem loop próprios.

Manter temporariamente `SessionPorts` como nome interno se uma renomeação gerar churn sem valor. Remover somente após callers migrarem; não criar `RuntimePorts` e carregar ambos indefinidamente.

### W3D-04 — Portabilidade, doctor e WSL

Adicionar `vanguard/packages/adapters/sandbox/platform.py` com descoberta factual:

- OS e arquitetura;
- WSL1 versus WSL2;
- user namespace disponível;
- `bwrap` encontrado e versão;
- possibilidade real de criar namespace/mount/network boundary;
- seccomp/no-new-privs quando aplicável;
- UDS/loopback se evaluator exigir;
- enforcement `full`, `partial` ou `unavailable`;
- causas estruturadas, nunca uma string “WSL unsupported”.

Refatorar `adapters/sandbox/rootless.py`:

- criar `qualify() -> ContainmentReport` idempotente;
- probes rodam uma vez por runner/session;
- `execute()` usa o report congelado e lança apenas o processo da tool;
- remover dupla declaração redundante de namespaces somente se teste de equivalência provar;
- separar falha de runner, policy denial e exit code do comando;
- manter output bounds, timeout e kill de process group;
- não inferir containment de flags.

Atualizar `ports/sandbox.py` para expor qualificação/facts sem acoplar a bwrap. Não chamar o host adapter de sandbox.

CLI:

```text
vg doctor --profile local
vg doctor --profile sandboxed
vg doctor --profile hermetic
```

O resultado deve mostrar requested/effective profile, backend, enforcement e blockers. WSL2 passa se os mesmos probes passarem. WSL1 ou WSL2 sob um host/restrição que impeça namespaces falha apenas nos profiles confinados. `local` continua funcionando.

Matriz inicial:

| Plataforma | `local` | `sandboxed` | `hermetic` |
|---|---|---|---|
| Linux | obrigatório | bwrap/alternativa qualificada | se evaluator/UID/WAL também qualificarem |
| WSL2 | obrigatório | permitido por capabilities, não garantido | permitido somente com todos os probes/identidades |
| WSL1 | possível | indisponível | indisponível |
| macOS | futuro adapter local já viável | Seatbelt futuro | somente após gate próprio |
| Windows nativo/cmd | futuro adapter local | restricted token/ACL ou remote executor futuro | não alegar antes de prova |

Não anunciar suporte nativo a Windows apenas porque Python inicia: `preexec_fn`, UDS e bwrap ainda são Unix-specific.

### W3D-05 — Split filesystem/process e performance

O atual `BindingContext(environment=...)` força todos os verbs a um environment. Alterar para dependências por capability:

```python
@dataclass(frozen=True)
class BindingContext:
    verb: str
    services: RuntimeServices
    repo_path: Path
```

O code binding provider resolve:

- `fs.read`, `fs.search`: `GitEnvironmentAdapter.observe`, in-process;
- `fs.write`, `patch.apply`: Git/worktree adapter com preview/receipt/compensate;
- `proc.exec`: process adapter host ou sandboxed conforme profile;
- futuro AST/index/cache: serviços próprios, não wrappers de shell.

Alterar:

- `runtime/wiring.py`;
- `adapters/bindings/code.py`;
- `adapters/environment/git.py`;
- `adapters/environment/sandboxed.py` para representar processo confinado, não filesystem universal;
- `adapters/sandbox/worker.py` se o request wire precisar separar command facts;
- `packs/code-default/plugins/{fs,ast-patch,terminal}.yaml` para declarar a capability correta e policy mínima.

Critérios de performance:

- zero bwrap para read/search/context/index;
- no máximo um bwrap spawn por `proc.exec` no primeiro MVP;
- qualification amortizada por session;
- medir p50/p95 do overhead antes de autorizar worker persistente;
- payload grande permanece por blob/ref, não atravessa JSON-RPC repetidamente.

### W3D-06 — Plugin activation real

Não implementar um novo framework de DI. Completar o já existente:

1. `compose.py` resolve entrypoint/config digest e produz component specs completos.
2. `activation.py` exige `build` no caminho de produção.
3. `registry` constrói `ComponentHandle` conforme isolation e bindings.
4. `ActivationSession` contém serviços reais e typed accessors.
5. `HarnessSession` recebe os serviços ativados e não reconstrói versões paralelas.
6. teardown fecha handles em ordem reversa e propaga falha de persistência.

Arquivos:

- `runtime/activation.py`: proibir `cell=None` em produção; continuar permitindo fake builder explícito em testes.
- `runtime/registry/lifecycle.py`: manter FSM; não adicionar estados sem falsificador.
- `runtime/registry/broker.py` e `worker.py`: usar somente para tiers realmente selecionados; não colocar todo first-party plugin em subprocesso.
- `runtime/registry/compiler.py`: retirar após a última compatibilidade se não for mais autoridade; não manter dois compilers.
- `runtime/compose.py`: ser o único compile/freeze.
- `packs/code-default/load.py`: remover seu compile paralelo; discovery pode sobreviver como adapter do canonical compose.
- `ports/spi.py`: não aumentar a lista. Avaliar cada SPI: se não houver consumer real após W-3D, documentar como compatibility/experimental em vez de fingir ativação.

A decisão entre “operacionalizar” e “retirar” cada SPI deve ser feita por prova de uso, não por apego ao documento antigo. Para o Developer Preview, são necessários model proposal, context assembly, tools e evaluation mode; memory pode permanecer opcional.

### W3D-07 — Packs `code-default` e `code-explain`

Eleger `packs/` como localização canônica de produto, coerente com README e Lei. Migrar `code-default` para o authored `/2` aceito pelo runtime. A recomendação é adicionar `packs/code-default/manifest.json` canônico e manter `harness.yaml` apenas até uma data de sunset, em vez de introduzir YAML como segunda semântica.

`packs/code-explain/` deve conter somente o delta necessário:

- manifest `/2`;
- system prompt próprio;
- context/read policy própria;
- refs para os mesmos plugins de fs-read/search/index/model/context;
- capability ceiling sem `fs.write`, `patch.apply` ou `proc.exec` por padrão;
- `evaluation:none` com reason para uso local, ou checker opcional separado.

Não copiar os tool schemas nem suas classes. Se o schema atual não suporta `extends/includes`, resolver refs compartilhadas pelo plugin catalog; não inventar herança textual de manifest.

Migrar e depois retirar:

- `vanguard/packages/agency/manifests/vg-code-default/` como autoridade de produto;
- `vg-code-claude-shaped` e `vg-code-opencode-shaped`: transformá-los em presets/deltas de prompt/policy ou removê-los se não houver comportamento/teste que justifique sua existência;
- `vg-shell-only`: manter somente se usado como agent/harness real;
- `vg-table-default`: manter como probe de domínio até M-5 decidir seu status.

Atualizar `agency/manifests/registry.json`, discovery e testes para localizar packs canônicos. A compatibilidade `/1` deve terminar na data ratificada, nunca virar fallback de execução.

### W3D-08 — Entry point genérico e CLI

Adicionar `vanguard/packages/runtime/entrypoint.py`. Ele lê uma command frame schema-valid de stdin, chama `RuntimeService`/bootstrap e escreve NDJSON. Não deve conter coding loop, routing ou tool dispatch.

Fluxo:

```text
vg code    -> agentId=code-default,  profileId=local
vg explain -> agentId=code-explain,  profileId=local
vg run     -> agentId/profile explícitos
all        -> runtime.entrypoint -> RuntimeService -> Runtime.run_composed
```

Alterar TypeScript:

- `clients/client-core/src/application/coding-types.ts` → `agent-types.ts`;
- `coding-receipts.ts` → `agent-receipts.ts`;
- `coding-commands.ts` → `agent-commands.ts`;
- `client-core/src/index.ts`: exports genéricos;
- `clients/cli/src/main.tsx`: mapear comandos para agent/profile, sem defaults de provider hardcoded;
- `clients/cli/src/composition/parse-cli.ts`: adicionar `--agent`, `--profile`, `--sandbox` como alias de UX se desejado e `doctor`;
- `clients/cli/src/composition/client-for.ts`: direct/daemon/replay continuam transports, não runtimes distintos;
- package descriptions e testes.

Não criar `coding_entrypoint.py` apenas para satisfazer o import atual. O módulo não existe; corrigir a referência diretamente evita um legacy shim desde o primeiro commit.

UX mínima:

- banner sempre mostra `agent`, `profile`, `containment`, `approval` e `store` efetivos;
- `local/uncontained` é visível sem mensagem alarmista repetitiva;
- erro `sandbox_unavailable` sugere `vg doctor` e opção explícita de novo run local;
- `explain` mostra read-only;
- exit codes permanecem estáveis e typed.

### W3D-09 — Ledger, live events e ciência futura

Não adicionar FastAPI, WebSockets ou broker externo ao núcleo. A comunicação interna usa objetos tipados; JSONL/UDS são adapters de processo; HTTP/WebSocket podem ser transports futuros.

Implementar `runtime/event_stream.py` como fan-out read-only:

1. `LedgerEmitter` persiste no `EventStorePort`.
2. Somente após append bem-sucedido o mesmo envelope/seq é publicado aos subscribers.
3. Um subscriber que reconecta lê o gap do store e continua live.
4. Backpressure é bounded; overflow encerra subscriber com cursor recuperável, nunca bloqueia o ledger.
5. EventStream não aceita append arbitrário e não possui writer authority.

Refatorar `RuntimeService`:

- remover sua segunda construção livre de eventos de execução;
- substituir `_InboxEventStore` incompleto por adapter real ou limitar o inbox somente a commands/idempotency;
- `publish_event` deixa de inventar outro envelope e passa a consumir o stream canônico;
- `server.py` converte envelopes para frames `vg.4`.

Política de captura científica:

- **durável obrigatório:** requests, descriptors, grants, approvals, budgets, model identity/usage, effect intents/receipts, lifecycle, profile facts, outcomes, lineage e digests;
- **live opcional:** token chunks, progress e PTY chunks;
- **blob policy:** prompts, outputs grandes e diffs completos ficam em blob store com digest/ref/redaction;
- **trainability:** default `prohibited`; corpus é opt-in e separado;
- **projeções:** logs, trace, UI, trajectory e métricas derivam dos eventos, não gravam outra verdade.

Isso dá dados para benchmarking, causal analysis, macro mining e meta-cognition futura sem transformar cada log em blockchain ou reter segredos por padrão.

### W3D-10 — Evidence como assurance policy

Hoje `run_composed()` sempre chama `derive_foundation_bundle`. Mudar para collector selecionado:

- `recorded`: produz trajetória e runtime facts comuns; foundation bundle pode indicar linhas ausentes, mas não executa auditoria RF-85.
- `hermetic`: exige preregistration antes do primeiro evento, deriva as nove linhas e executa auditoria.
- `evaluation:none`: explicitamente não promocional; não é erro de produto.

Arquivos:

- `runtime/foundation_evidence.py`: collector/auditor hermético, sem ser chamado incondicionalmente.
- `runtime/root.py`: não contém `if release`; usa assurance policy resolvida.
- `runtime/evaluator_gateway.py` e `ports/evaluator.py`: sem enfraquecimento; absence versus forged permanece distinta.
- `domain/evidence/*`: incluir effective profile/assurance nos cross-bindings se o ADR exigir.
- `runtime/trajectory.py`: todos os runs continuam emitindo trajetória, com measurement/containment/evaluation `unavailable|none|measured` explícitos.
- `test/contracts/test_m4_foundation_audit.py` e RF-85 tests: provar que local jamais passa auditoria.

O boolean `release` deve desaparecer da API pública depois da migração. `profile=hermetic` e o assurance contract são mais explícitos e identity-bearing.

### W3D-11 — Developer Preview

Definition of Done:

```text
vg doctor --profile local                         -> PASS em WSL2
vg code <repo> "corrija o teste" --profile local -> model real/fake selecionado, tools reais, diff e tests
vg explain <repo> "explique X" --profile local   -> read-only, resposta com arquivos/símbolos
vg code ... --profile sandboxed                  -> sandbox real ou sandbox_unavailable; nunca host silencioso
```

O preview não precisa de evaluator UID 10002, preregistration ou RF-85. Ele precisa de:

- um model provider configurável;
- file-backed session store para resume;
- permissions `allow/ask/deny`;
- path containment lógico;
- tool receipts e trajetória;
- boa mensagem de status;
- testes E2E com fake determinístico e um smoke live opt-in.

### W3D-12 — Cleanup sem shim permanente

Somente depois de paridade:

- retirar `sandbox_mode` de `root.py`/`lab_driver.py`;
- retirar `release: bool`;
- eliminar compiler/loader sem caller de produção;
- remover assets duplicados de manifests shaped;
- remover imports/exports compatibility que passaram do sunset;
- atualizar authority audit para o entrypoint genérico;
- rodar `check_duplication --enforce` e AST caller audit.

Rollback é por slice: schema/profile; bootstrap; sandbox split; pack convergence; CLI; event stream. Nenhum slice deve depender da deleção do legado no mesmo commit em que introduz o novo caminho.

## 6. W-4, W-5 e W-6 após W-3D

### W-4 — Foundation E2E continua hermético

W-3D não reduz RF-85. Ele elimina o falso bloqueio de desenvolvimento e torna a qualificação capability-based.

Passos:

1. reexecutar RF-78…RF-84 sobre o novo runtime;
2. congelar novo SHA e recalcular todos os digests;
3. selecionar `profile=hermetic`;
4. executar `vg doctor --profile hermetic` antes do preregistro;
5. aceitar WSL2 se e somente se worker UID, mount/network/syscall, evaluator UID, RPC, trust root e WAL passarem; caso contrário usar Linux qualificado;
6. publicar preregistro;
7. executar exatamente um RF-85;
8. auditor independente e Director fecham M-4.

O board deve remover a proibição categórica “non-WSL” e substituí-la por “host que satisfaça o profile hermetic e todos os probes”. Isso não garante que o WSL2 atual passe; garante que a arquitetura não o nega sem observar capacidades.

### W-5 — Generalidade, não outro coding preset

`code-explain` prova reutilização dentro do domínio coding, mas não prova generalidade do substrato. Manter Math/Formal Pack #2 como teste forte:

- novo pack e checker exterior determinístico;
- mesmas APIs de compose/activate/run;
- zero diff semântico em `domain/ports/kernel/agency/runtime` durante o intervalo;
- se faltar uma primitiva genérica, W-5 falha e abre finding; não se esconde lógica formal no core;
- T0 memoization permanece evidence reuse, não memory/meta-cognition.

Ao fechar W-5, declarar **MVP do framework single-agent**: coding, explain e domínio formal usam a mesma base.

### W-6 — Delegação mediada

Implementar somente após W-5:

- `agent.spawn` continua uma capability S0–S12;
- adapter runtime cria child apenas após durable S8a intent;
- target é um `D_H`/agent pack existente;
- child recebe interseção de ceilings e sublease de budget;
- sem handles, credenciais, evaluator ou memory ambientes;
- child return é untrusted-derived;
- recovery nunca repete spawn settled;
- CLI pode mostrar parent/child tree como projeção de eventos.

Não criar `SwarmEngine`. Ao fechar W-6, declarar **MVP de orquestração**.

## 7. Planejamento W-7 e W-8

### W-7 — Scheduler medido

Primeiro executar baselines sequenciais e coletar:

- latência por tool/model;
- filas e idle time;
- selector overlap;
- custo e qualidade;
- duplicação de tentativa;
- overhead de sandbox e streaming.

Só então autorizar independence groups. Unknown overlap continua conflito. Tentativas físicas são at-least-once; settlement é idempotente por command identity. Worker persistente, batch reads e concurrency entram somente se medidas indicarem benefício.

### W-8 — Topologias declarativas e Beta

Representar padrões como pack/policy data:

- planner → executor → verifier;
- critic ↔ reviser;
- map/reduce bounded;
- debate limitado;
- árvore de pesquisa com budgets;
- supervisor com children atenuados.

Lowering usa scheduler W-7 + spawn W-6. O kernel e `EpisodeEngine` permanecem topology-blind. Uma modificação de topologia cria uma nova versão/configuration digest para o próximo run; não altera silenciosamente o `FrozenComposition` ativo. Evolução genética e metamorfose são experimentos exteriores que propõem candidatos, medem e aguardam promoção humana.

Ao fechar RF-65/RF-66, executar security/performance/UX/recovery review e publicar **Beta**, não “v1 final”.

## 8. Ordem de releases

| Marco | Produto |
|---|---|
| W-3D | Developer Preview: coding + explain no WSL2/local |
| W-4 | Foundation Assurance Certified: RF-85 hermético |
| W-5 | Framework MVP: segundo domínio sem alteração do substrato |
| W-6 | Orchestration MVP: delegation/spawn mediado |
| W-7 | Performance Candidate: concorrência somente se medida |
| W-8 | Beta Release: topologias de referência, UX e recovery revisados |
| Pós-W-8 | decisão separada de v1 e pesquisa M-9/M-10 |

## 9. Inventário de arquivos

### Novos arquivos autorizáveis

- `docs/02_decisions/0089-execution-assurance-profiles-and-product-runtime.md` — decisão binding.
- `schemas/mhf/execution_profile.schema.json` — profile data contract.
- `vanguard/packages/runtime/profiles.py` — parsing/resolução/interseção.
- `vanguard/packages/runtime/bootstrap.py` — concrete composition root.
- `vanguard/packages/runtime/entrypoint.py` — one-shot genérico NDJSON.
- `vanguard/packages/runtime/event_stream.py` — fan-out pós-append.
- `vanguard/packages/adapters/sandbox/platform.py` — capability discovery.
- `packs/code-explain/` — apenas manifest/prompt/policy; refs compartilhadas.
- novos falsificadores/testes nos diretórios já existentes.

### Arquivos existentes a modificar

**Lei/decisão/execução:**

- `docs/SPEC.md`
- `docs/01_law/RUNTIME.md`
- `docs/01_law/SECURITY.md`
- `docs/01_law/DISPATCH.md`
- `docs/01_law/EXTENSIBILITY.md`
- `docs/01_law/EVIDENCE.md`
- `docs/02_decisions/INDEX.md`
- `docs/03_execution/sprint_active.md`
- `docs/03_execution/milestones.md`

**Referências atualizadas depois do comportamento:**

- `README.md`
- `docs/04_architecture/{overview,c4_component,c4_container,sequences,state_machines}.md` conforme diagramas afetados
- `docs/05_contracts/{manifests,events,trajectories}.md`
- `docs/06_protocols/{sandbox,evaluator,stores,spi}.md`
- `docs/07_engineering/{adding_a_pack,adding_an_adapter,development,security_and_tcb}.md`

**Schemas/domain:**

- `schemas/mhf/manifest_v2.schema.json`
- `schemas/v4/runtime-service.schema.json`
- `vanguard/packages/domain/artifacts/manifest.py`
- generated wire readers somente via `tools/codegen/generate_types.py`

**Runtime:**

- `vanguard/packages/runtime/{root,run_plan,compose,wiring,activation,session,ledger_emitter,foundation_evidence,trajectory,lab_driver,model_selection}.py`
- `vanguard/packages/runtime/service/{service,server,inbox}.py`
- `vanguard/packages/runtime/registry/{lifecycle,broker,worker,compiler}.py` conforme o sunset

**Ports/adapters:**

- `vanguard/packages/ports/{sandbox,environment,event_store}.py`
- `vanguard/packages/adapters/bindings/code.py`
- `vanguard/packages/adapters/environment/{git,sandboxed}.py`
- `vanguard/packages/adapters/sandbox/{rootless,worker}.py`
- `vanguard/packages/adapters/stores/event_store.py`

**Packs:**

- `packs/code-default/` para authored `/2` e refs reais
- `vanguard/packages/agency/manifests/registry.json`
- `vanguard/packages/agency/manifests/vg-*` durante a migração/sunset
- `vanguard/packages/agency/manifests/{loader,discovery}.py`

**CLI:**

- `vanguard/clients/client-core/src/application/{coding-commands,coding-receipts,coding-types}.ts` por rename genérico
- `vanguard/clients/client-core/src/index.ts`
- `vanguard/clients/cli/src/{main.tsx,composition/parse-cli.ts,composition/client-for.ts}`
- componentes de status que mostram profile/containment
- package descriptions e testes TS

**Linters/testes:**

- `tools/linters/check_isolation_policy.py`: validar profile/policy, não exigir container globalmente.
- `tools/linters/check_boundaries.py`: permitir apenas o bootstrap importar concrete adapters.
- `tools/linters/check_active_mvp_contract.py`: acompanhar o novo board.
- suites `test/{contracts,runtime,security,integration,falsifiers}/` e CLI.

### Arquivos que W-3D não deve modificar semanticamente

- `vanguard/packages/kernel/*`
- canonicalização/JCS/digests
- grants, typed budget algebra e S0–S12
- Ed25519 signing/verification trust root
- evaluator exterior como autoridade de promoção
- `agency/episode/engine.py` salvo correção comprovada por falsificador independente
- `_archive/`

## 10. Estratégia de commits e paralelismo

### Lane Principal Architect

1. ADR/law/RF allocation.
2. Schemas e `ExecutionProfile` identity.
3. `RuntimeDependencies`/bootstrap contracts.
4. Event truth/fan-out contract.
5. integração final e authority audit.

### Lane Staff Engineer

Depois de cada interface RED publicada:

1. platform detection e rootless qualification cache;
2. filesystem/process split;
3. pack `code-explain` e shared refs;
4. generic entrypoint/CLI;
5. contract/integration/UX tests.

Hotspots exclusivos da lane Architect: `root.py`, `run_plan.py`, schemas de identity e Lei. Hotspots exclusivos da lane Staff: adapters de plataforma, packs e TS CLI. `wiring.py`, `activation.py` e service são integrados em slices separados, nunca editados simultaneamente.

Ordem de merge:

```text
ADR + RED
-> profile schema/domain
-> bootstrap facade
-> local vertical slice + generic entrypoint
-> WSL doctor + sandbox split
-> code-explain
-> event stream/service convergence
-> plugin activation convergence
-> cleanup/sunset
-> full gates + independent review
```

### 10.1 Prompt operacional — Principal Architect Specialist

```text
Você é o Principal Architect Specialist responsável pela lane de contrato e
composition root de W-3D no AETHER. Trabalhe sobre a baseline declarada no board,
preserve a Lei/ADRs vigentes até haver autorização formal para o ADR sucessor e
não declare M-4 concluída.

Objetivo: separar execução funcional, contenção e assurance sem alterar o kernel,
S0-S12, grant algebra, JCS/digests, trust root Ed25519 ou evaluator exterior.

Ownership exclusivo desta lane:
- proposta ADR-0089 e edições coordenadas da Clean Triad;
- schema execution_profile e sua identidade em D_R;
- vanguard/packages/runtime/profiles.py;
- vanguard/packages/runtime/bootstrap.py;
- interfaces de RuntimeDependencies/EffectiveExecutionProfile;
- root.py e run_plan.py durante a extração;
- contrato store-then-publish do event stream;
- allocation e critérios RED de RF-87...RF-94.

Não implemente packs, UI TypeScript ou adapters de plataforma pertencentes à lane
Staff. Não crie AgentSpec/FlowSpec novos: trate FrozenComposition como a definição
identity-bearing do agente. Não introduza fallback silencioso. Não adicione código
ao kernel. Não abra spawn, scheduler ou topology antes dos milestones autorizados.

Entregas em slices revisáveis:
1. relatório de conflitos normativos com citações exatas e proposta mínima do ADR;
2. testes RED dos contratos de profile/bootstrap/identity;
3. schema + domain reader + codegen verificado;
4. resolver de profile por interseção monotônica;
5. composition root que injeta dependências concretas e deixa o Runtime fino;
6. store-then-publish contract sem segundo ledger;
7. migration/sunset map para host-dev, lab_driver e manifests legados;
8. evidence package com boundary, TCB, security e falsifier results.

Contrato de handoff para a lane Staff:
- publique primeiro os Protocols/dataclasses e fixtures RED estáveis;
- forneça exemplos local/sandboxed/hermetic sem factories concretas no core;
- não renomeie interfaces depois do handoff sem teste de compatibilidade;
- integre mudanças em wiring/activation somente em commits separados;
- registre decisões no board, sem criar relatórios Markdown paralelos.

Critério de conclusão: coding e explain podem ser ligados pelo mesmo bootstrap;
local é explicitamente uncontained/non-promotional; sandboxed falha se solicitado e
indisponível; hermetic mantém integralmente RF-85; todos os perfis e runtime facts
ficam ligados a D_R; nenhum invariant foi enfraquecido implicitamente.
```

### 10.2 Prompt operacional — Staff Engineer

```text
Você é o Staff Engineer responsável pela lane de vertical slices de W-3D no
AETHER. Consuma apenas os contratos publicados pela lane Principal Architect;
quando ainda não existirem, prepare testes/fixtures e adapters atrás das portas
atuais sem editar os hotspots exclusivos daquela lane.

Objetivo: entregar um Developer Preview real no WSL2 com dois agentes compostos
pelas mesmas primitivas — code-default e code-explain — e preservar o caminho
hermético como opção explícita, sem fallback silencioso.

Ownership exclusivo desta lane:
- adapters/sandbox/platform.py e qualificação capability-based;
- cache session-scoped dos probes rootless;
- split de filesystem direto/path-checked e proc.exec pelo sandbox port;
- packs/code-default e code-explain, compartilhando referências de plugins;
- runtime/entrypoint.py genérico após o contrato do bootstrap;
- client-core/CLI TypeScript e UX de profile/containment;
- testes de integração local, WSL2, pack reuse e CLI;
- benchmarks p50/p95 do caminho fs e proc.exec.

Não altere docs/SPEC, ADRs, schemas de identity, root.py ou run_plan.py sem handoff
explícito. Não crie coding_entrypoint.py como shim. Não copie tools/prompts para o
pack explain: referencie os mesmos componentes e restrinja autoridade a read-only.
Não construa worker bwrap persistente antes de benchmark justificar. Não capture
chain-of-thought; persista apenas facts de controle e conteúdo permitido pela
capture/redaction policy. Não implemente spawn, DAG ou scheduler.

Entregas em slices revisáveis:
1. doctor que relata Linux/WSL1/WSL2/capabilities sem negar por nome do SO;
2. backend sandboxed que falha claramente quando solicitado e indisponível;
3. fs.read/search/write/patch path-checked sem custo bwrap e com receipts;
4. proc.exec roteado pelo backend efetivo e benchmarkado;
5. pack code-explain estruturalmente read-only, sem código duplicado;
6. entrypoint NDJSON one-shot genérico e adapter daemon/UDS separado;
7. vg code e vg explain pelo mesmo Runtime.run_composed;
8. testes, UX errors acionáveis e relatório de performance reproduzível.

Coordenação:
- baseie cada slice em um teste RED/contrato já publicado;
- não edite wiring.py, activation.py ou service simultaneamente com a outra lane;
- sinalize o commit-base e entregue commits pequenos por adapter/pack/CLI;
- trate qualquer necessidade de mudar o kernel ou a Lei como blocker de design,
  não como autorização para contornar a fronteira;
- não execute RF-85 durante a refatoração.

Critério de conclusão: em WSL2, vg code modifica uma workspace autorizada e vg
explain somente lê; ambos usam SQLite-WAL file-backed e o mesmo runtime/ledger;
status mostra profile, containment real e promotion eligibility; sandboxed e
hermetic jamais degradam silenciosamente; duplication, boundaries, tests Python e
TypeScript ficam verdes.
```

## 11. Gates finais W-3D

- coding e explain E2E pelo mesmo path;
- local funciona em WSL2 sem bwrap;
- sandboxed/hermetic nunca fazem fallback silencioso;
- profile efetivo e runtime facts alteram `D_R`;
- explain é estruturalmente read-only;
- bwrap probes executam uma vez por session;
- eventos streamed são os mesmos envelopes persistidos;
- componentes ativados têm services reais;
- nenhum código de domínio entra no kernel;
- nenhum novo loop/DAG/spawn;
- `check_boundaries`, TCB, domain blindness, isolation policy, duplication, schemas, links, secrets e suites completos verdes;
- RF-78…RF-84 revalidados;
- reviewer independente confirma novo baseline antes de RF-85.

## 12. Conclusão

A melhor solução não é remover segurança nem construir uma caixa hermética para todo read/write. É tornar deployment e assurance substituíveis na borda, enquanto o mecanismo de autoridade permanece pequeno.

O menor caminho sustentável é:

1. profile explícito e identity-bearing;
2. bootstrap único fora do loop;
3. filesystem leve separado de subprocesso;
4. local funcional e honestamente não contido;
5. sandbox capability-based compatível com WSL2 quando o host permite;
6. hermetic invariavelmente fail-closed;
7. dois agentes como composição dos mesmos plugins;
8. um ledger, um runtime e um entrypoint genérico;
9. spawn, concorrência e topologias somente nos gates já previstos.

Isso preserva as partes difíceis e valiosas do AETHER — authority, provenance, replay e evidence — e remove o que hoje impede que ele seja um harness utilizável.

## Referências externas primárias

- Claude Code: sandbox opcional, WSL2 e `failIfUnavailable`: https://code.claude.com/docs/en/sandboxing
- Claude Code settings: https://code.claude.com/docs/en/settings
- OpenCode permissions por tool/agente: https://opencode.ai/docs/permissions/
- OpenCode agents: https://opencode.ai/docs/agents/
- Codex Linux/WSL2 bwrap behavior: https://github.com/openai/codex/blob/main/codex-rs/linux-sandbox/README.md
- DeepSeek Harness plugin/profile architecture: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
- DeepSeek sandbox seam e enforcement facts: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/sandbox.md

## 13. Director execution log — appended 2026-08-24

This section is appended after the original W-3D text. The preceding text is unchanged.

### 13.1 Implemented work

- Identity-bearing `ExecutionProfile` and profile digest binding into `D_R`.
- Single `RuntimeBootstrap` composition seam.
- Capability-based platform discovery and rootless Bubblewrap qualification.
- Filesystem/process separation for local preview and confined subprocess execution.
- Real component materialization and reverse-order teardown.
- `code-default` / `code-explain` pack convergence and read-only explain capabilities.
- Generic runtime entrypoint plus `vg code`, `vg explain`, and `vg doctor` paths.
- Developer Studio preview.
- Durable event persistence with replay/live fan-out from the same store.
- Assurance policy and foundation-evidence integration.
- RF-90 generic-entrypoint, RF-92 durable-stream, and RF-94 authority-audit falsifiers.
- Pack aliases preserving canonical kernel verbs:

```json
{
  "read_file": "fs.read",
  "search_files": "fs.search",
  "edit_file": "patch.apply"
}
```

- Ollama errors now retain a bounded provider response body.
- OpenRouter and Ollama default completion budgets were raised from 256 to 1024 tokens because
  reasoning models were exhausting the old budget before emitting a tool call.

### 13.2 Verified focused gates

```text
RF-78 PASS
RF-79 PASS
RF-80 PASS
RF-81 PASS
RF-82 PASS
RF-83 PASS
RF-84 PASS
RF-87 PASS
RF-88 PASS
RF-89 PASS
RF-90 PASS
RF-91 PASS
RF-92 PASS
RF-93 PASS
RF-94 PASS
RF-ID allocation linter PASS
Boundary linter PASS — 262 source files
TCB budget PASS — 1366 / 1438 LOC
Duplication detector PASS
client-core TypeScript typecheck PASS
CLI TypeScript typecheck PASS
```

The full CLI suite still contains environment/legacy failures: restricted Unix-socket tests return
`EPERM`, and some legacy demo subprocess assertions fail in the current execution container. The
repository also contains pre-existing blank-line-at-EOF findings in `tools/002_LLM_API_MOCK` files.

### 13.3 Provider and model logs

All provider calls used the canonical runtime entrypoint and isolated temporary workspaces for coding
attempts. No benchmark workspace in the repository was modified.

WSL2 reached Windows-host Ollama at `http://127.0.0.1:11434`. Bubblewrap doctor reported WSL2,
Bubblewrap 0.9.0, user namespaces available, and `enforcement=full`. Relevant installed tags were:

```text
qwen2.5:1.5b
qwen2.5-coder:7b-instruct-q5_K_M
deepseek-coder-v2:16b
gemma4:26b
```

`qwen2.5:1.5b` completed a two-turn read request but returned a confused generic response and is
not suitable for reliable coding.

`qwen2.5-cod:7b` and `deepseek-code-v2:16b` returned HTTP 404 because those exact tags do not exist.

`qwen2.5-coder:7b-instruct-q5_K_M` initially returned `read_file`; before aliases this failed with:

```text
tool is not declared by manifest: read_file
```

After aliases were added, a four-turn proof completed and returned a `tool_result` digest plus
`docs/SPEC.md` content, proving alias canonicalization.

`deepseek-coder-v2:16b` returned HTTP 400 during tool calling; its current Ollama template remains
incompatible with the tool request/response format.

`gemma4:26b` completed a one-turn authority request and returned:

```text
The canonical execution authority is docs/03_execution/sprint_active.md.
```

The root `.env` contains `OPENROUTER_API_KEY`; its value was never printed. A direct probe of
`deepseek/deepseek-v4-flash` returned HTTP 200 from provider `StreamLake`:

```text
prompt_tokens=12 completion_tokens=8 total_tokens=20 cost=$0.0000016072
```

The eight-token probe ended during reasoning and returned no visible content. A four-turn coding
attempt using the same route returned:

```json
{
  "outcome": "abandoned",
  "turns": 4,
  "detail": "turn bound 4 reached"
}
```

The isolated task workspace remained unchanged.

### 13.4 Real coding benchmark logs

Benchmark: `DOGFOOD-01 Multi-Turn File Rollback`.

Task: fix `src/calculator.py` and verify with:

```text
python3 -m unittest test_calculator.py
```

Original defect:

```python
def divide(a, b):
    return b / a
```

Expected behavior is `divide(10, 2) == 5.0`.

```text
qwen2.5-coder:7b-instruct-q5_K_M: outcome=abandoned, turns=8,
  detail=turn bound 8 reached, test FAIL: 0.2 != 5.0
gemma4:26b: outcome=abandoned, turns=8,
  detail=turn bound 8 reached, test FAIL: 0.2 != 5.0
deepseek/deepseek-v4-flash: outcome=abandoned, turns=4,
  detail=turn bound 4 reached, test FAIL: 0.2 != 5.0
```

These runs prove the live provider paths were reached, but do not prove successful coding or RF-85.
The model proposal trace is not sufficiently exposed in the final entrypoint result; this remains an
observability defect. LAM and `tools/002_LLM_API_MOCK` are valid for deterministic wiring/cassette
tests only and are ineligible as RF-85 evidence.

### 13.5 Issues and likely causes

1. The former 256-token provider default was too small for reasoning models; it was raised to 1024.
2. Small/reasoning models can consume the budget without a visible tool call.
3. Several requested Ollama model names do not match installed tags.
4. `deepseek-coder-v2:16b` returns HTTP 400 for the current tool schema/template.
5. Model proposal and translation details are not sufficiently visible in final run output.
6. Local coding runs reached the runtime but failed to make the required edit within the turn bound.
7. Docker is installed but inaccessible through `/var/run/docker.sock`.
8. `sudo` cannot elevate because the container has `no new privileges`.
9. No evaluator process is available as UID 10002.

### 13.6 Remaining W-3D/M-4 TODO

- Persist and expose model proposal, tool-call, translation, and turn-failure diagnostics.
- Select a provider/model that completes the benchmark task reliably.
- Provision the evaluator as a separate UID-10002 process over UDS.
- Bind evaluator image digest, public key, oracle identity, and protocol.
- Freeze immutable task/oracle preregistration before the first run event.
- Use durable SQLite-WAL storage for the candidate run.
- Execute one uninterrupted hermetic coding run through Bubblewrap.
- Derive all nine RF-85 source-derived evidence rows from that same lineage.
- Obtain independent artifact audit and Director closure of M-4.

### 13.7 Requirements before M-5, M-6, and metacognition

M-5 requires M-4 closure, Formal Pack #2, RF-86, an exterior verifier, and zero semantic changes
under `domain/`, `ports/`, `kernel/`, `agency/`, or `runtime/` during the proof.

M-6 requires M-5 closure and capability-mediated `agent.spawn` with attenuated authority, budget,
depth, turns, lineage, and recovery behavior under RF-55–RF-59 and RF-26.

M-7 and M-8 must precede metacognition: measured scheduling/concurrency first, then declarative
topologies and mediated delegation. M-9/M-10 remain non-authorizing until those gates close.

### 13.8 Suggested approaches

**Approach A — Runtime observability first:** persist provider proposal/translation diagnostics,
run short provider probes, choose the first model that emits a valid declared tool call, then repeat
the benchmark with bounded turns.

**Approach B — Clean release host first:** move the RF-85 attempt to a clean Linux host/VM where
Docker or rootless UID provisioning works, start the UID-10002 evaluator, preregister the benchmark,
and execute the real hermetic run there.

**Director status:** W-3D focused implementation is largely green. M-4/RF-85 is not closed. M-5 and
M-6 remain locked. No metacognition work is authorized.

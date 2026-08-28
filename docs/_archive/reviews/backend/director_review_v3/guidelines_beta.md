# Relatório de solução

Sim, é possível substituir o modelo atual por uma execução autônoma, linear e previsível com dois times — sem Tech Lead disponível, sem aprovação externa, sem revisão cruzada obrigatória e sem “Leadership gates”.

A correção essencial é esta:

> A aprovação humana desaparece. A verificação técnica continua, executada pelo próprio time como parte da implementação.

Sem nenhuma verificação, “produto pronto” vira apenas uma opinião. Mas não precisamos de testes exaustivos, reuniões, comitês ou autorização para avançar. Precisamos de checks automáticos mínimos, objetivos e locais.

## 1. Diagnóstico do material atual

Os 14 documentos fornecidos contêm boa arquitetura e informação suficiente para orientar M‑4→M‑8, mas o modelo operacional está errado para a realidade atual.

Os principais problemas são:

* O `masterplan_todo_rev1` ainda depende de Leadership gates, decisões do Director, revisão independente, PR review e ativação formal.
* `SPRINT_ACTIVE` distribui trabalho para Dev A, Dev B, Dev C, Tech Lead, reviewer, tooling, TS e lab, embora existam apenas dois times reais.
* Vários itens estão formalmente bloqueados por ADRs ou decisões que poderiam ser tomadas pelos próprios owners técnicos.
* Existem especificações razoavelmente detalhadas para M‑4→M‑8, mas quase nada executável para M‑9 e M‑10.
* M‑1→M‑3 não estão especificadas no pacote fornecido; precisam ser reconstruídas do código, Git e releases anteriores.
* Os documentos foram auditados contra `f9d7ceb`. Se o código atual está em `624d80f` ou posterior, é obrigatória uma nova comparação code-first.
* Há conflito de versionamento: a documentação atual associa M‑7 à v0.9.0, M‑8 à v0.9.x e M‑9 à v1.0; você quer entregar v0.9 depois de M‑10. Isso precisa ser fixado antes do plano final.
* O projeto tem documentação suficiente para explicar a arquitetura, mas ainda não possui dois fluxos de implementação completos e autocontidos.

Portanto, não precisamos redesenhar o AETHER. Precisamos transformar a arquitetura existente em dois planos executáveis.

# 2. Nova metodologia: duas lanes autônomas

A estrutura recomendada é:

* Lane A: Runtime, execução e infraestrutura causal.
* Lane B: contratos, projeções, verificação, generalidade e aprendizagem.
* Cada lane possui uma sequência completamente linear.
* Cada time mantém WIP igual a um grande bloco.
* Cada time toma suas próprias decisões internas.
* Não existe aprovação cruzada.
* Não existe aprovação do CEO ou Tech Lead durante a execução.
* Ao terminar um bloco, o próprio time faz self-review, executa os checks definidos e continua.
* A integração entre lanes segue uma ordem previamente definida, sem decisão humana.
* O segundo time a terminar uma wave executa a integração mecânica.
* Defeitos de integração retornam diretamente ao owner do arquivo ou contrato.
* Resultado experimental negativo não bloqueia a roadmap: ativa um fallback previamente definido.

Uma milestone passa a ter esta regra:

> Está concluída quando o comportamento existe, o build funciona e os checks automáticos definidos no plano passam. Ninguém precisa aprovar.

## 3. O que não será mais usado

O plano final deve remover:

* Leadership gates.
* Approval checklist.
* Promotion manual de sprint.
* Tech Lead como owner de integração.
* Director como owner de decisão.
* Reviewer independente obrigatório.
* ADR pendente impedindo implementação.
* Boards concorrentes dizendo coisas diferentes.
* Tasks abertas sem owner concreto.
* Espera por decisão sobre detalhes internos.
* Exigência de resultado experimental positivo para continuar.
* Sprints cerimoniais.

ADRs podem continuar existindo como registro técnico, mas não como pedido de autorização. O próprio owner toma a decisão, registra a razão e implementa.

# 4. O que precisa ser coletado antes dos dois planos

Os documentos atuais não bastam para especificar código exato. Precisamos investigar o repositório real.

## 4.1 Baseline real

Coletar:

* Branch oficial de desenvolvimento.
* Commit exato que será o ponto de partida.
* Diferenças entre `f9d7ceb`, `624d80f` e o HEAD atual.
* Branches e PRs ainda não integrados.
* Tags e releases M‑1→M‑3.
* Estado atual do build.
* Comandos oficiais de instalação, lint, testes e execução.
* Plataformas oficialmente suportadas.
* Dependências externas e serviços necessários.

O plano não pode apontar para arquivos, funções ou contratos que já mudaram.

## 4.2 Auditoria code-first

Precisamos produzir um inventário de:

* Packages e módulos existentes.
* Grafo de imports entre `domain`, `ports`, `kernel`, `agency`, `runtime`, `adapters` e `packs`.
* Composition root real.
* Caminho real de uma execução completa.
* Event kinds existentes e seus writers.
* Schemas efetivamente usados.
* Reducers e projections existentes.
* WAL, ledger, artifact store, caches e indexes.
* Caminho de model invocation.
* Recovery, replay e resume existentes.
* Tools e adapters já implementados.
* Código morto, duplicado ou desconectado.
* Tests existentes e o que realmente cobrem.
* Performance atual.
* Packaging e instalação atuais.
* Funcionalidades documentadas, mas ausentes no código.
* Funcionalidades existentes no código, mas ausentes nos documentos.

O resultado é uma matriz:

`obrigação → estado atual → gap → lane owner → implementação → verificação`.

## 4.3 Reconstrução de M‑1→M‑3

Como os arquivos entregues começam praticamente em M‑4, M‑1→M‑3 não devem ser inventados nem reimplementados.

Precisamos usar:

* Histórico Git.
* Tags e changelogs.
* ADRs correspondentes.
* Testes associados.
* Schemas antigos.
* Estado atual do código.

Cada requisito M‑1→M‑3 será classificado como:

* Implementado e preservado.
* Implementado, mas sem verificação mínima.
* Parcial.
* Obsoleto.
* Regressado.
* Substituído por arquitetura posterior.
* Ainda necessário para M‑4→M‑10.

O trabalho de M‑1→M‑3 no plano será uma wave de baseline e reparo, não um rewrite.

# 5. O que já deve ser considerado decidido

O plano final não deve reabrir a arquitetura inteira. As seguintes decisões do material atual devem ser incorporadas diretamente como regras de implementação:

* Kernel permanece domain-blind.
* Runtime permanece a única composition seam concreta.
* Ledger e artifacts continuam sendo a verdade causal.
* Large content não entra diretamente no ledger.
* Agent é projection derivada, não objeto mutável autoritativo.
* Agency não importa Runtime.
* Schemas estritos `/1` não são modificados.
* Novos writers usam `/2`; readers fazem dual-read.
* Evidência obrigatória que falha encerra a execução evidenciária.
* Degradação opcional precisa ser registrada como incompleta.
* `GoalDeclared` guarda digest/referência, não texto bruto.
* Retention usa `digests_only`, `standard` e `full`.
* Capture authorization é diferente de retention.
* Recursos aditivos são `usd_micros`, `millis`, `tokens` e `bytes`.
* `depth` e `turns` são limites estruturais.
* TCB é calculado pela closure transitiva real, não apenas contando `kernel/`.
* Histórico persistido nunca é reescrito.
* Generator, evaluator e promoter continuam semanticamente separados.

Essas regras entram nos dois planos como invariantes, não como assuntos sujeitos à nova aprovação.

# 6. Divisão recomendada M‑1→M‑10

| Wave    | Lane A — execução/runtime                                                                                     | Lane B — contratos/avaliação                                                                                           |
| ------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| M‑1→M‑3 | Auditar e reparar runtime, kernel, ports, adapters, composition e persistence existentes                      | Auditar schemas, contracts, invariants, CI, compatibilidade e evidências históricas                                    |
| M‑4     | ArtifactWriter, model I/O capture, provenance, compaction/context capture e cache provenance                  | Execution Profile v2, Trajectory v2, RF‑100, golden vectors e benchmark                                                |
| M‑5a    | Event `/2`, write-path migration, vocabulary/codegen e writer authority                                       | ExecutionScope, LineageRef, OperationRecord, AgentView, checkpoints e reconstruction                                   |
| M‑6     | Recursive delegation, SpawnAdapter, nested lineages, budgets e recovery                                       | Enquanto A executa M‑6, B executa M‑5b com o formal-domain falsifier                                                   |
| M‑6.5   | MetaController integration e StrategyDirective lowering                                                       | Confidence, ProgressProjection, calibration e paired evaluation                                                        |
| M‑7     | Topology-as-data, lowering, scheduler policy e mecanismo runtime                                              | Análise de independência, concorrência, três topologias e decisão automática de escopo                                 |
| M‑8     | Memory, retrieval, knowledge/experience/project-memory infrastructure                                         | Skills, evaluation, promotion, regression e rollback                                                                   |
| M‑9     | Integração do produto, CLI/API/TUI, plugins, configuration, clean install, workflows reais e beta operacional | Product packs, end-to-end scenarios, quality evaluation, release evidence e operator experience                        |
| M‑10    | Reliability, persistence scalability, upgrade/migration, security enforcement, performance e deployment       | Release qualification, regression corpus, failure injection, compatibility, documentation operacional e release bundle |

Recomendo que M‑10 seja uma milestone de encerramento e productization, não mais uma expansão teórica. Populations, evolução aberta e adaptação distribuída podem ser prototipadas, mas não devem impedir a entrega da v0.9.

# 7. Como eliminar decisões bloqueantes

Cada decisão futura recebe um owner definitivo e um fallback.

| Decisão              | Owner                     | Regra                                                                    |
| -------------------- | ------------------------- | ------------------------------------------------------------------------ |
| Event roster M‑5a    | Lane A                    | Decide dentro dos invariantes e mantém compatibilidade                   |
| Checkpoint defaults  | Lane B                    | Escolhe pelo benchmark; usa default conservador se inconclusivo          |
| Formal oracle M‑5b   | Lane B                    | Seleciona o oracle determinístico mais simples disponível                |
| Confidence protocol  | Lane B                    | Define sinais versionados; nenhum sinal vira verdade absoluta            |
| Concurrency M‑7      | Lane B mede; A implementa | Se ganho não justificar complexidade, permanece sequencial/safe-parallel |
| Lifecycle events M‑8 | Lane B                    | Escolhe kinds completos ou typed claims pela menor mudança compatível    |
| Blob GC/legal hold   | Lane A                    | Implementa política separada de execution retention                      |
| Multi-tenancy        | A implementa; B verifica  | Só entra em M‑9/M‑10 se fizer parte do produto-alvo                      |

Nenhuma dessas decisões volta para você. O owner decide, registra e continua.

# 8. Estrutura obrigatória de cada task

Cada task dos dois planos deve conter:

1. ID único e posição na sequência.
2. Resultado funcional esperado.
3. Baseline exato.
4. Arquivos e símbolos conhecidos.
5. Superfície de código permitida.
6. Inputs e outputs públicos.
7. Protocolos e schemas consumidos.
8. Protocolos e schemas produzidos.
9. Invariantes que devem permanecer.
10. Fluxo comportamental em pseudocódigo.
11. Casos normais.
12. Edge cases.
13. Modelo de erros e degradação.
14. Persistência e migration.
15. Telemetria e eventos emitidos.
16. Compatibilidade backward/forward.
17. Requisitos de performance.
18. Segurança, capability e privacy.
19. Critério automático de conclusão.
20. Comandos de build/check relevantes.
21. Artefatos que comprovam a conclusão.
22. Rollback ou feature flag.
23. Próxima task automaticamente liberada.

O pseudocódigo deve especificar comportamento, ordem causal, I/O, erros e invariantes. Não precisa prescrever todos os helpers privados, pois isso destruiria a autonomia dos Seniors.

# 9. Como trabalhar sem bloqueio entre A e B

Antes de cada wave, os dois planos precisam conter um Contract Kit já fechado com:

* Schemas compartilhados.
* Interfaces públicas.
* Payload examples.
* Golden vectors.
* Stubs, mocks ou fakes.
* Ownership exclusivo de arquivos compartilhados.
* Ordem mecânica de integração.
* Compatibilidade esperada.

Assim:

* A implementa usando os contracts.
* B implementa usando fixtures e stubs.
* Nenhum consome a branch inacabada do outro.
* Cada time termina seu pacote isoladamente.
* A integração acontece na ordem já escrita.
* O segundo time a terminar executa a integração.
* Conflito mecânico é resolvido pelo integrador.
* Conflito semântico é resolvido pelo owner do contrato.
* Ninguém solicita aprovação.

Se um time terminar antes e a próxima task depender da integração, ele usa uma fila auxiliar previamente definida: benchmark, performance, fixtures, adapters, hardening ou documentação técnica do próprio pacote. Isso evita ociosidade sem produzir branches divergentes.

# 10. Testes sem burocracia

Eliminar completamente os testes impediria afirmar que a aplicação está pronta. A solução é reduzir a verificação ao mínimo necessário e torná-la parte da task.

Usaremos três níveis:

* Check local: rápido, executado pelo próprio developer enquanto implementa.
* Check da wave: integração dos dois pacotes e apenas os contratos afetados.
* Check de release: clean install, build, smoke test e cenários end-to-end essenciais.

Não haverá:

* Reviewer externo.
* Aprovação de resultado.
* Comitê de qualidade.
* Execução manual repetitiva.
* Suite completa após cada pequeno commit.
* Bloqueio esperando alguém interpretar o resultado.

Se um experimento der resultado negativo:

* M‑6.5: MetaController permanece disabled-by-default.
* M‑7: scheduler avançado é simplificado ou cancelado.
* M‑8: candidate promotion permanece desabilitada até existir evidência suficiente.
* A roadmap continua.

O experimento encerra uma decisão; ele não vira uma prisão administrativa.

# 11. Pesquisa realmente necessária

Não precisamos fazer outra pesquisa teórica ampla sobre agentes para começar M‑4→M‑8.

A pesquisa deve ser restrita a gaps implementáveis:

* M‑9/M‑10 e definição do produto final.
* Packaging e distribuição Python/CLI.
* Upgrade e migration de ledgers/schemas.
* Estratégia de storage e blob lifecycle.
* Multi-process ou distributed execution, somente se entrar no produto.
* Multi-tenant isolation, somente se houver servidor compartilhado.
* Plugin lifecycle e SDK.
* Benchmarking de coding/research agents.
* Recovery e fault injection.
* Security/capability enforcement.
* Meta-control evaluation.
* Skill promotion e rollback.
* Performance do append/fold/checkpoint/retrieval.
* UX operacional necessária para observar e controlar execuções.

Cada pesquisa deve terminar em uma decisão concreta, contrato, benchmark ou algoritmo. Nada de survey genérico.

# 12. Os dois documentos finais

Depois da auditoria, produziremos exatamente dois planos:

* Plano Lane A: sequência completa A‑001→A‑final, cobrindo M‑1→M‑10.
* Plano Lane B: sequência completa B‑001→B‑final, cobrindo M‑1→M‑10.

Cada documento será autocontido e terá:

* Baseline.
* Arquitetura relevante.
* Invariantes.
* Coding standards.
* Contratos consumidos e produzidos.
* Sequência linear completa.
* Pseudocódigo comportamental.
* Migrations.
* Failure modes.
* Checks automáticos.
* Integration order.
* Decision defaults.
* Build e release procedure.
* Definition of Product Ready.

Os contratos compartilhados aparecerão nos dois com o mesmo Plan ID e versão. Um terá owner explícito; o outro apenas consumirá.

# 13. TODO list para sair da situação atual

| Ordem | Trabalho                                          | Resultado                            |
| ----: | ------------------------------------------------- | ------------------------------------ |
|     1 | Fixar o commit/branch oficial                     | Um baseline incontestável            |
|     2 | Definir se M‑10 entrega v0.9.0 ou v1.0            | Versionamento único                  |
|     3 | Definir produto final de M‑9/M‑10                 | Escopo encerrado                     |
|     4 | Auditar o código real                             | Inventário de módulos, fluxos e gaps |
|     5 | Reconstruir M‑1→M‑3                               | Baseline histórico confirmado        |
|     6 | Comparar código com os 14 documentos              | Matriz spec→code→gap                 |
|     7 | Extrair apenas as decisões arquiteturais válidas  | Fundação congelada                   |
|     8 | Converter decisões abertas em owners e fallbacks  | Nenhuma aprovação pendente           |
|     9 | Criar ownership exclusivo de arquivos e contratos | A e B não colidem                    |
|    10 | Definir Contract Kits M‑4→M‑10                    | Desenvolvimento por stubs e fixtures |
|    11 | Especificar M‑9 Product Integration               | Beta utilizável                      |
|    12 | Especificar M‑10 Release Hardening                | Produto buildado e distribuível      |
|    13 | Decompor Lane A linearmente                       | Plano completo do Time A             |
|    14 | Decompor Lane B linearmente                       | Plano completo do Time B             |
|    15 | Inserir pseudocódigo, erros, migrations e checks  | Execução sem dúvidas                 |
|    16 | Simular dependências dos dois planos              | Nenhum bloqueio administrativo       |
|    17 | Entregar os planos aos times                      | Desenvolvimento autônomo             |
|    18 | Times implementam, verificam e integram           | M‑1→M‑10 concluído                   |
|    19 | Executar clean build e cenários de produto        | Release candidate                    |
|    20 | Você revisa somente o produto final               | Aceitação empresarial                |

## Resumo executivo

* A arquitetura atual pode ser preservada.
* O processo de aprovação atual deve ser removido.
* A e B tornam-se owners completos de duas lanes permanentes.
* Os developers tomam decisões, implementam, verificam e integram.
* Não haverá revisão cruzada nem aprovação externa.
* Haverá apenas checks automáticos mínimos, porque sem eles não existe definição objetiva de “pronto”.
* M‑1→M‑3 serão auditados, não reescritos.
* M‑4→M‑8 já possuem matéria-prima suficiente, mas precisam ser convertidos de planos de governança para tasks de código.
* M‑9/M‑10 precisam ser especificados; recomendo Product Integration em M‑9 e Release Hardening em M‑10.
* O próximo trabalho correto é auditar o repositório real e então produzir os dois planos completos e autocontidos.

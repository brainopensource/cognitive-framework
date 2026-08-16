# Revisão Arquitetural SOTA Pré-Sprints 5 e 6 — VANGUARD v4

Atue simultaneamente como **Tech Lead Sênior, Project Lead Sênior e Software Architect em nível PhD**, com experiência comprovada em sistemas agênticos, runtimes determinísticos, capability security, event sourcing, sandboxing, recuperação transacional, avaliação experimental e Agentic Coding Harnesses SOTA.

## Contexto

Estamos implementando o **VANGUARD v4**. As Sprints 0, 1, 2, 3 e 4 já foram concluídas, ao menos parcialmente no código.

Após as Sprints 3 e 4, já possuímos:

* runtime básico real construído sobre o kernel e o ledger;
* loop de Episodes dirigido por cassettes;
* fluxo de aprovação model-free;
* contratos, schemas, testes e componentes associados já implementados;
* base sobre a qual as Sprints 5 e 6 deverão entregar o primeiro Coding Agent Harness integrado.

As Sprints 5 e 6 irão conectar kernel, ledger, dispatcher, runtime, Episodes, approvals, ferramentas, avaliação e demais adapters. Portanto, esta é a última janela de baixo custo para corrigir erros estruturais antes que integrações adicionais consolidem acoplamentos, workarounds e dívida arquitetural.

## Missão

Produza um **relatório técnico SOTA de readiness e convergência arquitetural**, determinando exatamente o que deve ser corrigido, consolidado ou comprovado antes de continuar e concluir as Sprints 5 e 6.

Não implemente código durante esta revisão. Primeiro produza diagnóstico, evidências, decisões e plano de ação.

## Leitura obrigatória

Antes de emitir qualquer conclusão:

1. Leia integralmente todos os documentos normativos do VANGUARD v4, incluindo registry, handbook, charter, arquitetura, contratos, wire schemas, kernel, capabilities, segurança, memória, evidence plane, measurement doctrine, build plan, decision register, deferred/rejected register e vision annex.
2. Leia integralmente os dois relatórios arquiteturais já produzidos:

   * `vanguard_harness_cli_architectural_review_2026-08-15.md`;
   * `fuaa_harness_agentic_coding_clis_revisao_v2.md`.
3. Inspecione todo o código implementado nas Sprints 0–4, sem se limitar aos arquivos principais.
4. Leia testes, fixtures, cassettes, schemas, migrations, configurações, scripts, CI, ADRs, manifests e documentação operacional.
5. Examine o histórico Git relevante para entender decisões, alterações de contrato e possíveis divergências entre documentação e implementação.
6. Execute testes, linters, type checking e verificações não destrutivas necessárias para validar o estado real.
7. Não presuma que a documentação representa o código, nem que testes passando provam os invariantes arquiteturais.

Toda afirmação deve indicar sua base:

* contrato documental;
* evidência no código;
* teste executado;
* inferência explícita;
* ou lacuna ainda não comprovada.

## Questões obrigatórias

### 1. Conformidade entre arquitetura e implementação

Mapeie os contratos e invariantes normativos para os componentes reais do código e determine:

* o que está implementado corretamente;
* o que está parcialmente implementado;
* o que divergiu da especificação;
* o que existe apenas na documentação;
* o que existe apenas no código;
* o que não possui teste capaz de sustentar seu claim.

Inclua rastreabilidade entre requisito, módulo, símbolo, teste e evidência.

### 2. Revisão do Trust Spine

Audite especialmente:

* intent-before-effect;
* emissão e durabilidade de receipts;
* ledger append-only;
* replay e crash recovery;
* reconciliação de efeitos com resultado desconhecido;
* idempotência;
* capability resource-scoped;
* attenuation e delegação;
* separação entre autorização e containment;
* isolamento do dispatcher;
* exterioridade do evaluator;
* representação explícita de estado inconclusivo;
* ausência de caminhos que permitam bypass do kernel.

Identifique qualquer ponto em que o sistema possa inventar certeza após crash, duplicar efeitos, perder resultados ou aceitar evidência produzida pelo próprio episódio.

### 3. Conflitos P0/P1 já identificados

Valide no código e nos documentos, no mínimo:

* o problema do timestamp dentro do instrument tuple comparável;
* a tensão entre `DEF-12`, que adia suspensão/retomada, e `TK-06`, que exige cobertura dos failure paths correspondentes;
* a ambiguidade entre verification passando pelo dispatcher e a exterioridade do Evidence plane;
* o risco de perda de resultados no failure path de emissão de outcomes;
* referências normativas incorretas ou obsoletas;
* claims mais amplos do que as evidências ou proofs existentes.

Determine se cada finding continua válido, já foi corrigido ou assumiu uma forma diferente na implementação.

### 4. Qualidade estrutural do código

Procure ativamente por:

* acoplamento entre core e adapters;
* dependências invertidas incorretamente;
* abstrações prematuras;
* interfaces genéricas sem necessidade comprovada;
* duplicação de regras de autoridade;
* estado mutável fora do ledger;
* side effects escondidos;
* acesso direto ao filesystem, processos ou rede fora do dispatcher;
* lógica de policy em CLI, UI ou adapters;
* tipos permissivos que enfraquecem invariantes;
* schemas divergentes;
* tratamento genérico de exceções;
* retries capazes de duplicar efeitos;
* fallbacks fail-open;
* ordem de eventos não determinística;
* testes excessivamente mockados;
* cassettes que validam o happy path, mas não o contrato;
* workarounds que irão dificultar as Sprints 5 e 6.

Não recomende refatorações estéticas sem impacto mensurável em correção, segurança, integração ou custo futuro.

### 5. Readiness das Sprints 5 e 6

Avalie se a base atual suporta, sem violar o desenho:

* integração de um Coding Agent Harness real;
* loop observe → propose → authorise → effect → receipt → evaluate;
* ferramentas de leitura, edição, shell e teste;
* execução headless e reprodutível;
* sandbox obrigatório no benchmark mode;
* context assembly e compaction substituíveis;
* model/provider adapters sem contaminar o core;
* MCP/ACP exclusivamente nos boundaries adequados;
* avaliação exterior ao episódio;
* tracing completo da trajetória;
* stop conditions verificáveis;
* recovery após interrupções;
* testes determinísticos com cassettes;
* futura introdução de subagentes com child leases e authority attenuation.

### 6. Compatibilidade com padrões SOTA

Use os dois relatórios como referência, mas não copie features de outros harnesses indiscriminadamente.

Avalie quais propriedades devem ser:

* incorporadas antes das Sprints 5–6;
* mantidas como ports/adapters futuros;
* adiadas formalmente;
* ou rejeitadas por conflitarem com o Trust Spine.

Considere especialmente:

* ACI mínima;
* repo-map e localização estrutural;
* prefix-cache stability;
* context compaction;
* MCP/ACP;
* isolamento local, container ou microVM;
* subagentes;
* checkpoints;
* event sourcing;
* structured edits;
* evaluator exteriority.

Protocolo, memória, checkpoint ou plugin system não podem substituir autoridade, contenção, ledger ou evidência.

## Relatório esperado

Entregue o relatório com esta estrutura:

1. **Executive verdict** — no máximo uma página.
2. **Estado real das Sprints 0–4**.
3. **Matriz contrato → código → teste → status**.
4. **Findings classificados em P0, P1, P2 e P3**.
5. **Divergências entre documentação e implementação**.
6. **Riscos de acoplamento e retrabalho nas Sprints 5–6**.
7. **Refatorações mínimas recomendadas antes de continuar**.
8. **Melhorias que podem ser adiadas com segurança**.
9. **Itens que não devem ser implementados**.
10. **Plano de remediação ordenado por dependência**.
11. **Critérios objetivos de Go/No-Go para a Sprint 5**.
12. **Critérios objetivos de Go/No-Go para a Sprint 6**.
13. **Veredito final**:

    * continuar sem alterações;
    * continuar após correções localizadas;
    * executar refactor arquitetural moderado;
    * suspender integração por falha estrutural.

Para cada finding, informe:

* severidade;
* evidência concreta com arquivo e símbolo;
* contrato ou invariante afetado;
* impacto se não corrigido;
* mudança mínima recomendada;
* testes necessários;
* momento correto da correção;
* risco e custo estimado;
* dependências com as Sprints 5 e 6.

## Restrições

* Não proponha uma v5 ou reescrita integral sem demonstrar que os contratos fundamentais da v4 são irrecuperáveis.
* Prefira correções localizadas e explícitas quando preservarem os invariantes.
* Não recomende abstrações “para o futuro” sem consumidor real ou hipótese experimental.
* Não esconda hard gates dentro de médias, scores ou recomendações genéricas.
* Não trate teste passando como prova automática de segurança ou correção.
* Não altere código antes da aprovação do relatório.
* Não suavize findings críticos para preservar o cronograma.
* Não invente comportamento de sistemas externos nem detalhes ausentes do repositório.
* Quando a evidência for insuficiente, classifique o resultado como **inconclusivo**.

## Objetivo final

Determinar o menor conjunto de correções que deve ser executado agora para que as Sprints 5 e 6 integrem um Coding Agent Harness sobre uma fundação coerente, testável e desacoplada — evitando retrabalho tardio, workarounds, coupled code, violações do Trust Spine e uma reescrita desnecessária após a conclusão da v4.

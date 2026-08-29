# ATLAS OSS DOCS

Para **ganhar produtividade agora** e ao mesmo tempo produzir evidência prática para o futuro Atlas, eu não tentaria testar 20 ferramentas. Eu montaria um **Frankenstein deliberado de 8–10 componentes**, cada um validando uma hipótese específica do Atlas.

## Stack que eu usaria agora

| FerramentaUse agora?O que valida para Atlas |                                 |                                                     |
| ------------------------------------------- | ------------------------------- | --------------------------------------------------- |
| **MkDocs Material**                         | **SIM**                         | organização, navegação, busca, metadata, publicação |
| **Pandoc**                                  | **SIM**                         | migração/conversão de documentação legada           |
| **Docling**                                 | **SIM se houver PDF/DOCX/etc.** | ingestão de documentos complexos para Markdown/JSON |
| **YAML frontmatter + JSON Schema**          | **SIM**                         | futuro schema de Knowledge Nodes                    |
| **yq/jq**                                   | **SIM**                         | consultar/migrar metadata sem criar software        |
| **markdownlint-cli2**                       | **SIM**                         | documentação estruturalmente compilável             |
| **Vale**                                    | **SIM**                         | consistência semântica/editorial                    |
| **Lychee**                                  | **SIM**                         | integridade de links/referências                    |
| **Mermaid**                                 | **SIM**                         | architecture-as-code / diagram-as-data              |
| **pre-commit**                              | **SIM**                         | pipeline automático local + CI                      |
| **ast-grep**                                | **SIM, experimento**            | ligação docs ↔ código via AST                       |
| **SCIP**                                    | **SIM, experimento controlado** | symbols/definitions/references multi-language       |
| Tree-sitter direto                          | depois                          | só se ast-grep não bastar                           |
| Glean                                       | não agora                       | backend futuro/escala                               |
| Joern                                       | não agora                       | análise profunda futura                             |
| GraphRAG                                    | não agora                       | provavelmente secundário                            |
| Backstage                                   | não agora                       | portal, não knowledge substrate                     |
| Neo4j                                       | não agora                       | complexidade prematura                              |

---

# 1. Base imediata: MkDocs Material

Eu começaria por aqui.

Não porque MkDocs seja Atlas, mas porque ele obriga você a começar a transformar:

```text
500 arquivos aleatórios
```

em:

```text
Knowledge hierarchy
    ↓
navigation
    ↓
sections
    ↓
documents
    ↓
headings
    ↓
search
```

Material mantém Markdown como source, possui busca local, tags e metadata, e permite aplicar metadata por subseções. ([Squidfunk](https://squidfunk.github.io/mkdocs-material/?utm_source=chatgpt.com "Material for MkDocs"))

Para AETHER:

```text
docs/
├── index.md
├── architecture/
├── concepts/
├── contracts/
├── agents/
├── workflows/
├── decisions/
├── execution/
├── guides/
├── reference/
└── archive/
```

Não precisa ser perfeito.

Na verdade, **você quer descobrir onde essa taxonomia falha**. Isso é informação para Atlas.

---

# 2. Faça frontmatter obrigatório

Esse é provavelmente o experimento Atlas mais importante.

Mas mínimo.

```yaml
---
id: arch.kernel
type: architecture
status: active
authority: canonical
summary: Domain-blind effect authorization and execution mediation.
---
```

Talvez mais dois campos:

```yaml
supersedes:
  - legacy.kernel-v1

related:
  - concept.capability
  - concept.effect
```

Só.

**Não coloque 30 campos.**

A hipótese que você está testando é:

> Quanto metadata explícito precisa ser escrito por humanos para tornar o repository machine-readable sem aumentar demais a manutenção?

Isso é diretamente informação de design para PKIR.

---

# 3. JSON Schema para transformar documentação em contrato

Crie:

```text
docs/_schema/document.schema.json
```

E valide:

```yaml
id
type
status
authority
summary
```

com JSON Schema.

A implementação Python `jsonschema` já fornece validação da especificação; não há motivo para desenvolver validator próprio. ([GitHub](https://github.com/python-jsonschema/jsonschema/blob/main/docs/validate.rst?utm_source=chatgpt.com "jsonschema/docs/validate.rst at main · python-jsonschema/jsonschema · GitHub"))

Então começa a existir:

```text
Markdown
+
Frontmatter
+
Schema
=
semi-structured knowledge
```

Essa provavelmente será uma das fundações conceituais futuras do Atlas.

---

# 4. Use `yq` como o seu "proto Atlas query language"

Isso é surpreendentemente útil.

`yq` já processa YAML/JSON e consegue ler/modificar estruturas e frontmatter. ([GitHub](https://github.com/mikefarah/yq?utm_source=chatgpt.com "GitHub - mikefarah/yq: yq is a portable command-line YAML, JSON, XML, CSV, TOML, HCL and properties processor · GitHub"))

Por exemplo, você poderá fazer scripts equivalentes a:

```bash
docs status active
docs authority canonical
docs type architecture
```

sem escrever Atlas.

Você pode gerar algo como:

```text
generated/
└── catalog.jsonl
```

contendo:

```json
{"id":"arch.kernel","type":"architecture","path":"docs/architecture/kernel.md"}
{"id":"concept.capability","type":"concept","path":"docs/concepts/capability.md"}
```

Esse arquivo já começa a parecer PKIR-Lite.

---

# 5. Pandoc para destruir o primeiro problema: formatos legados

Se existirem:

```text
DOCX
RST
HTML
AsciiDoc
Org
LaTeX
MediaWiki
...
```

**Pandoc primeiro.**

Ele já converte uma enorme variedade de markup/word-processing formats para Markdown e outros formatos através de readers/writers e de uma representação intermediária própria. ([Pandoc](https://pandoc.org/MANUAL.html?utm_source=chatgpt.com "Pandoc - Pandoc User’s Guide"))

Isso inclusive é conceitualmente interessante para Atlas:

```text
Legacy Format
      ↓
Pandoc AST
      ↓
Markdown
```

É exatamente a filosofia:

> Normalize first, reason later.

---

# 6. Docling se houver PDFs e documentos complexos

Aqui eu faria questão de experimentar.

Docling hoje é open source, originado no IBM Research/LF AI & Data, e consegue converter:

- PDF;
- DOCX;
- PPTX;
- XLSX;
- HTML;
- imagens;
- LaTeX;
- EPUB;
- outros formatos;

para estruturas como Markdown e JSON. Também recupera layout, reading order e tabelas em PDFs. ([Docling Documentation & Resource Hub](https://docling.org/?utm_source=chatgpt.com "IBM Docling - Official Document Processing, Granite Docling VLM & OCR Engine | Docling.org"))

Para Atlas isso é particularmente interessante porque Docling já tem seu próprio:

```text
DoclingDocument
```

Ou seja:

```text
PDF
DOCX
PPTX
       ↓
   Docling IR
       ↓
Markdown / JSON
       ↓
future PKIR adapter
```

Eu testaria isso seriamente.

### Divisão

```text
Pandoc
→ markup/document conversion

Docling
→ difficult document ingestion
→ PDFs / layout / tables / Office
```

---

# 7. markdownlint-cli2 para tornar Markdown quase "compilável"

Use desde agora.

Ele aplica regras estruturais sobre Markdown/CommonMark e foi desenhado para CLI/CI. ([GitHub](https://github.com/DavidAnson/markdownlint-cli2?utm_source=chatgpt.com "GitHub - DavidAnson/markdownlint-cli2: A fast, flexible, configuration-based command-line interface for linting Markdown/CommonMark files with the markdownlint library · GitHub"))

Você começa a proibir coisas como:

```text
heading hierarchy quebrada
duplicated headings
malformed lists
spacing inconsistente
etc.
```

O Atlas futuro pode assumir:

> documentos que passaram pelo pipeline têm uma estrutura mínima confiável.

Isso é extremamente valioso.

---

# 8. Vale para consistência conceitual

Eu também colocaria Vale.

Vale é essencialmente:

```text
ESLint
para
prosa
```

Ele entende markup e permite regras customizadas em YAML. ([GitHub](https://github.com/vale-cli/vale?utm_source=chatgpt.com "GitHub - vale-cli/vale: \:pencil: A markup-aware linter for prose built with speed and extensibility in mind. · GitHub"))

Por exemplo, você pode criar regras AETHER:

```text
Não usar:
Agent Instance

Preferir:
AgentView
```

ou:

```text
"event log"
→ prefer "causal ledger"
```

Ou detectar termos deprecated:

```text
Vanguard → obsolete terminology
Higgs kernel → historical terminology
```

Esse é um experimento muito interessante para Atlas porque começa a transformar **ontology drift** em algo detectável automaticamente.

Vale já é usado dessa forma em docs-as-code; por exemplo, Elastic mantém regras próprias para sua documentação. ([GitHub](https://github.com/elastic/vale-rules?utm_source=chatgpt.com "GitHub - elastic/vale-rules: Elastic Docs' style guide rules for the Vale linter · GitHub"))

---

# 9. Lychee para links

Coloque imediatamente.

Lychee é um link checker async em Rust para Markdown, HTML e outros conteúdos e pode rodar como CLI, library, pre-commit ou GitHub Action. ([GitHub](https://github.com/lycheeverse/lychee?utm_source=chatgpt.com "GitHub - lycheeverse/lychee: ⚡ Fast, async, stream-based link checker written in Rust. Finds broken URLs and mail addresses inside Markdown, HTML, reStructuredText, websites and more! · GitHub"))

Então:

```text
doc → doc
doc → ADR
doc → code URL
doc → external reference
```

deixa de depender de inspeção humana.

Isso é um ancestral simples de:

```text
Atlas unresolved edge detection
```

---

# 10. Mermaid para todos os diagramas novos

Eu proibiria novos:

```text
architecture_final_v4_revised_REAL.png
```

quando o gráfico puder ser expresso como Mermaid.

Mermaid representa flowcharts, sequence diagrams, class diagrams, states, C4, architecture diagrams, timelines e diversas outras estruturas através de texto versionável. ([mermaid.ai](https://mermaid.ai/open-source/intro/index.html?utm_source=chatgpt.com "About Mermaid | Mermaid"))

Isso significa:

```text
Git diff
+
AI editable
+
searchable
+
parseable
+
regenerable
```

Excelente para Atlas.

---

# 11. pre-commit junta tudo sem precisar do Atlas

Configure:

```text
git commit
     │
     ├─ frontmatter schema
     ├─ markdownlint
     ├─ Vale
     ├─ Lychee
     └─ custom docs checks
```

`pre-commit` existe exatamente para coordenar hooks multi-language desse tipo. ([GitHub](https://github.com/pre-commit/pre-commit?utm_source=chatgpt.com "GitHub - pre-commit/pre-commit: A framework for managing and maintaining multi-language pre-commit hooks. · GitHub"))

Depois o mesmo pipeline roda no CI.

---

# 12. Agora vem o experimento mais importante: ast-grep

Depois que as docs estiverem minimamente estruturadas, eu testaria **ast-grep imediatamente no AETHER**.

Não integraria.

Só usaria.

Porque ele já faz AST-aware:

```text
search
lint
rewrite
```

em muitas linguagens e escala para milhares de arquivos. ([Ast Grep](https://ast-grep.github.io/?utm_source=chatgpt.com "ast-grep | structural search/rewrite tool for many languages"))

Por exemplo:

```text
docs dizem:

AgentView
```

Você consegue investigar:

```text
onde AgentView é definido?
onde é instanciado?
quais classes usam?
quais padrões antigos ainda existem?
```

Isso ajuda diretamente a fazer:

```text
documentation claim
        ↕
actual code
```

### O que você quer descobrir

Não "ast-grep é bom?"

Mas:

> Quanto do mapeamento docs ↔ code conseguimos resolver simplesmente com ast-grep?

Se for 70%, Atlas não precisa inventar muita coisa.

---

# 13. Depois teste SCIP em um subconjunto

SCIP é outro experimento que eu considero obrigatório.

Ele normaliza:

```text
definitions
references
implementations
symbol identities
```

em um protocolo language-agnostic e já possui indexadores para várias linguagens, além de bindings Rust. ([GitHub](https://github.com/scip-code/scip/?utm_source=chatgpt.com "GitHub - scip-code/scip: SCIP Code Intelligence Protocol · GitHub"))

Teste, por exemplo:

```text
Python backend
+
TypeScript frontend
```

e veja se consegue gerar algo como:

```text
symbol AgentView
    ↓
definition
references
implementations
```

### Pergunta de pesquisa

> SCIP fornece informação semântica suficiente para nosso future PKIR ou ainda precisamos combinar SCIP + AST?

Essa resposta só vale depois de experimentar no AETHER real.

---

# 14. Eu NÃO usaria Tree-sitter diretamente ainda

Porque `ast-grep` já usa Tree-sitter internamente e lhe oferece uma camada bem mais conveniente. ([Ast Grep](https://ast-grep.github.io/guide/introduction?utm_source=chatgpt.com "What is ast-grep? | ast-grep"))

Portanto:

```text
First:
ast-grep

Only if insufficient:
Tree-sitter API
```

Evita desenvolvimento prematuro.

---

# O "Frankenstein Alfa" que eu montaria

Na prática:

```text
                       AETHER REPO
                            │
            ┌───────────────┼────────────────┐
            │               │                │
        LEGACY DOCS       MARKDOWN          CODE
            │               │                │
      Pandoc/Docling        │          ast-grep / SCIP
            │               │                │
            └───────────────┼────────────────┘
                            │
                           docs/
                            │
                    YAML frontmatter
                            │
                  JSON Schema validation
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
   markdownlint           Vale              Lychee
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                        MkDocs
                            │
                   Human documentation
                            │
                            +
                     generated script
                            │
                            ▼
                     catalog.jsonl
```

E opcionalmente:

```text
                    code information
                           │
                ast-grep / SCIP
                           │
                           ▼
                     symbols.jsonl
```

Então sem Atlas você já terá:

```text
catalog.jsonl
documents.jsonl
symbols.jsonl
links.jsonl
```

Esse é essencialmente um **proto-PKIR construído com shell/Python + OSS**.

---

# O script proprietário agora deveria ser ridiculamente pequeno

Algo como:

```text
tools/docs/
├── inventory.py
├── validate_frontmatter.py
├── build_catalog.py
├── detect_duplicates.py
├── extract_links.py
└── report.py
```

Nada além disso inicialmente.

O Python só coordena.

---

# Estrutura que eu usaria agora

```text
docs/
├── index.md
│
├── architecture/
├── concepts/
├── contracts/
├── workflows/
├── agents/
├── plugins/
├── decisions/
├── execution/
├── guides/
├── reference/
│
├── _legacy/
│
└── _meta/
    ├── document.schema.json
    ├── taxonomy.yml
    ├── terminology.yml
    └── authority.yml

tools/docs/
├── inventory.py
├── catalog.py
├── validate.py
└── migration.py

generated/knowledge/
├── catalog.jsonl
├── links.jsonl
├── symbols.jsonl
└── report.json
```

Observe que isso já é praticamente preparado para:

```text
generated/knowledge/*
        ↓
future Atlas importer
```

---

# O que você deve medir enquanto trabalha

Essa parte é mais importante que as ferramentas.

Registre para cada uma:

| PerguntaMétrica                        |                                          |
| -------------------------------------- | ---------------------------------------- |
| Quanto trabalho automatizou?           | minutos/tarefa ou arquivos automatizados |
| Quantos falsos positivos?              | %                                        |
| Quantas informações úteis extraiu?     | facts/document                           |
| Quanto precisa de configuração manual? | config LOC                               |
| Funciona incrementalmente?             | sim/não                                  |
| Tem saída estruturada?                 | JSON/AST/etc                             |
| É determinístico?                      | sim/não                                  |
| Funciona multi-language?               | cobertura                                |
| É fácil para agentes usarem?           | CLI/API                                  |
| Seria adapter ou core Atlas?           | decisão                                  |

No final você não estará especulando sobre Atlas.

Terá empiricamente:

```text
Pandoc       → useful for X
Docling      → useful for Y
ast-grep     → resolves 73% of code relationships
SCIP         → resolves precise symbols but costs X
Vale         → catches terminology drift
frontmatter  → human maintenance cost acceptable/unacceptable
MkDocs       → sufficient/insufficient discovery
```

Isso vira requisitos reais.

---

# O que eu deliberadamente deixaria de fora agora

**Não instalar/operacionalizar ainda:**

```text
Glean
Joern
Neo4j
GraphRAG
Backstage
OpenRewrite
Cytoscape
Vector DB
custom Rust Atlas
MCP Atlas server
```

Não porque sejam ruins.

Porque **não resolvem sua dor mais urgente melhor do que o stack simples** e adicionariam variáveis demais ao experimento.

---

## Minha sequência prática

1. **MkDocs Material + estrutura de pastas.**
2. **Frontmatter mínimo + JSON Schema + yq.**
3. **Pandoc/Docling para converter legacy.**
4. **markdownlint + Vale + Lychee.**
5. **Mermaid para diagramas novos.**
6. **pre-commit/CI para impedir regressão.**
7. **Gerar** **`catalog.jsonl`** **e** **`links.jsonl`** **com scripts mínimos.**
8. **Experimentar ast-grep para docs ↔ code.**
9. **Experimentar SCIP para symbol graph.**
10. Só depois decidir o que realmente merece virar **Atlas**.

### Em resumo

Seu alfa não deveria ser um mini-Atlas. Deveria ser um **laboratório operacional composto por MkDocs + Pandoc/Docling + structured frontmatter + JSON Schema + Vale + markdownlint + Lychee + Mermaid + ast-grep + SCIP**, usando scripts mínimos para colar tudo; você resolve a documentação do AETHER agora e, ao mesmo tempo, coleta exatamente a evidência necessária para saber **o que o Atlas deve abstrair, o que deve apenas adaptar e o que não precisa existir**."""

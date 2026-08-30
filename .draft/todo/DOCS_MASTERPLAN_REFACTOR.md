# Documentation Refactor using OSS

## 1. Onde colocar os fluxogramas?

**Não criaria `docs/workflows/` no topo.** “Workflow” não é um domínio; é uma forma de explicar arquitetura/processo.

Use o owner semântico:

```text
docs/
├── architecture/
│   ├── overview.md
│   ├── boundaries.md
│   ├── data-flow.md
│   └── workflows/
│       ├── system-bootstrap.md
│       └── end-to-end-execution.md
│
├── backend/
│   └── architecture/
│       └── workflows/
│           ├── request-execution.md
│           ├── agent-lifecycle.md
│           ├── event-lifecycle.md
│           ├── artifact-lifecycle.md
│           ├── recovery-resume.md
│           ├── delegation.md
│           └── memory-learning.md
│
└── product/
    └── frontend/
        └── workflows.md
```

A regra é simples:

* fluxo **backend interno** → `backend/architecture/workflows/`
* fluxo **end-to-end backend ↔ client ↔ runtime** → `architecture/workflows/`
* fluxo **do usuário/produto/UX** → `product/...`
* fluxo temporário gerado por máquina → `.generated/diagrams/`

E eu colocaria o Mermaid **dentro do `.md` canônico** sempre que possível, em vez de manter `.mmd` separado.

Material for MkDocs já possui integração oficial com Mermaid usando `pymdownx.superfences`, incluindo flowcharts, sequence, state, class e ER diagrams. ([Squidfunk][1])

---

# 2. Você já pode gerar esses workflows do código?

**Sim, mas faça em dois estágios.**

Hoje você já possui:

```text
catalog.jsonl
ownership.jsonl
links.jsonl
code-map.jsonl
symbols.jsonl
```

Então já dá para a IA usar:

```text
docs canônicas
+
code-map
+
symbols
+
código real
+
testes
```

para construir Mermaid muito mais confiável que simplesmente “ler README e imaginar”.

Mas ainda não chame isso de geração 100% automática.

### Agora

```text
code + docs + generated knowledge
              ↓
       agent investigates
              ↓
      proposes Mermaid
              ↓
 validates against code
              ↓
       canonical .md
```

### Depois com P1

```text
SCIP
+
ast-grep
+
code-map
+
docs graph
        ↓
machine-extracted relationships
        ↓
diagram generator
```

SCIP é exatamente um protocolo language-agnostic para definitions, references e implementations, e possui indexadores para Python e TypeScript; `ast-grep` fornece structural AST search/rewrite. ([GitHub][2])

---

# 3. Ordem certa: **não instale tudo de uma vez**

Eu faria em **5 passes**.

```text
PASS 0  Freeze / baseline
   ↓
PASS 1  Docs site + Mermaid
   ↓
PASS 2  Validation / CI
   ↓
PASS 3  Machine knowledge
   ↓
PASS 4  Code intelligence
   ↓
PASS 5  Obsidian + RAG + Proto-Atlas
```

E sim: **eu daria isso para um coding agent bom rodando no repo**, porque 80% do trabalho agora é instalação, configuração, integração, testes e pequenos scripts — não raciocínio arquitetural criativo.

---

# PASS 0 — Congele o estado limpo

Antes de qualquer OSS novo:

```bash
git status
git add -A
git commit -m "docs: finalize canonical documentation cutover"
git tag docs-clean-baseline
```

Depois confirme:

```text
docs/               canonical
.generated/         regenerável
old docs/            gone
candidate-docs/      gone
legacy reconstruction gone
```

**Não reorganize mais a árvore.**

---

# PASS 1 — MkDocs + Mermaid primeiro

Esse é o primeiro passo porque já entrega valor visual imediatamente.

Material recomenda instalação como pacote Python e atualmente documenta `mkdocs-material` 9.x como major estável; o build continua sendo simplesmente `mkdocs build`. ([Squidfunk][3])

Como seu repositório já possui gerenciamento Python, eu pediria ao agente para **usar o gerenciador canônico existente**, não criar um terceiro esquema de lock.

Ele deve adicionar:

```text
mkdocs-material
```

e opcionalmente depois:

```text
mkdocstrings[python]
```

Crie:

```text
mkdocs.yml
```

com:

```yaml
site_name: AETHER

theme:
  name: material

markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

Essa configuração Mermaid é justamente a integração recomendada pelo Material. ([Squidfunk][1])

Então:

```bash
mkdocs serve
```

Você ganha imediatamente:

```text
navigation
search
rendering
Mermaid
local documentation site
```

---

# PASS 1.5 — Gere os primeiros workflows manualmente assistidos por IA

Comece com **5–7 diagramas**, não 50.

Eu escolheria:

```text
architecture/workflows/
├── end-to-end-execution.md
└── system-bootstrap.md

backend/architecture/workflows/
├── request-execution.md
├── agent-lifecycle.md
├── event-lifecycle.md
├── delegation.md
└── recovery-resume.md
```

Cada página deveria ser pequena:

````text
# Request Execution

breve explicação

## Flow

```mermaid
...
````

## Canonical components

links para architecture/reference relevantes

````

Não copie toda a arquitetura para essas páginas.

**O diagrama complementa a arquitetura; não vira outro owner dos fatos.**

---

# PASS 2 — Torne as docs compiláveis

Agora instale a barreira anti-bagunça.

### 2.1 JSON Schema

Você já possui frontmatter e validator.

Formalize:

```text
.docs/document.schema.json
````

com poucos campos obrigatórios.

Não volte para os campos gigantes da reconstruction.

### 2.2 markdownlint-cli2

Como seu repo já possui Node/npm:

```bash
npm install --save-dev markdownlint-cli2
```

Esse é um modo oficialmente suportado pelo projeto. ([GitHub][4])

Depois:

```bash
npx markdownlint-cli2 "docs/**/*.md"
```

### 2.3 Vale

Vale fica responsável por **prosa e terminologia**, não estrutura Markdown.

Exemplo:

```text
.docs/vale/
├── Aether/
│   ├── Terminology.yml
│   ├── Deprecated.yml
│   └── Normative.yml
```

Vale é markup-aware e roda totalmente offline. ([Vale][5])

Comece com **5–10 regras**, não 200.

Ex.:

```text
Vanguard -> warn em docs atuais se nome histórico
Agent Instance -> prefer AgentView
```

Mas não crie regras antes de saber que existe drift real.

### 2.4 Lychee

Use para links externos e, opcionalmente, internos.

Você já tem seu checker interno funcionando, então:

```text
seu checker
→ paths/anchors/canonical IDs

Lychee
→ principalmente URLs externas
```

Não duplique responsabilidade.

### 2.5 pre-commit

Depois:

```bash
pre-commit install
```

Essa é a operação padrão documentada pelo projeto; `pre-commit run --all-files` permite validar o repo inteiro. ([Pre-commit][6])

---

# PASS 3 — Coloque tudo atrás de UMA interface

Aqui entra `just`.

Não quero você digitando:

```text
python isso
npm aquilo
vale aquilo
mkdocs aquilo
lychee aquilo
```

Tenha:

```bash
just docs-check
just docs-build
just docs-serve
just docs-knowledge
just docs-full
```

### `docs-check`

```text
metadata/schema
canonical IDs
markdownlint
Vale
internal links
stale paths
```

### `docs-build`

```text
mkdocs build --strict
```

### `docs-knowledge`

```text
tools/generate_knowledge_base.py
```

### `docs-full`

```text
docs-check
+
knowledge zero-rebuild
+
MkDocs strict
+
external links
```

Esse pequeno command surface é importante porque depois:

```text
just docs-* 
       ↓
future
atlas *
```

---

# PASS 4 — Integre CI sem tornar commit infernal

Faça dois níveis.

### Local / pre-commit

Só rápido:

```text
frontmatter
IDs
markdownlint
Vale
internal links
stale paths
```

### CI

Tudo:

```text
local checks
+
MkDocs build --strict
+
external URLs
+
zero rebuild of .generated/knowledge
+
ownership collision
+
knowledge reproducibility
```

Se um link externo ficar offline temporariamente, tenha política de retry/allowlist adequada; não transforme falha da internet em caos de desenvolvimento.

---

# PASS 5 — API reference derivada do código

Depois que P0 estiver estável, pare de documentar APIs manualmente sempre que possível.

### Python

Use:

```text
Griffe
+
mkdocstrings
```

O handler Python do mkdocstrings usa essa abordagem para coletar APIs Python e pode ser configurado diretamente no `mkdocs.yml`. ([Mkdocstrings][7])

Isso é particularmente útil para:

```text
ports
protocols
public runtime APIs
interfaces
```

Mas eu **não geraria docs de cada função privada**.

API docs != architecture docs.

### TypeScript

Espere o frontend estabilizar.

Depois:

```bash
npm install --save-dev typedoc
```

TypeDoc pode produzir HTML **ou um modelo JSON**, o segundo sendo muito interessante para Atlas. ([TypeDoc][8])

---

# PASS 6 — ast-grep primeiro

Agora começa P1.

Como seu ambiente já tem npm, pode ser instalado via npm; também há Cargo, Homebrew e pip oficialmente suportados. ([Ast Grep][9])

Use inicialmente em read-only:

```text
find AgentView construction
find Kernel.dispatch callers
find Runtime.execute_profiled callers
find deprecated runtime APIs
find direct adapter dependencies
```

Saída:

```text
ast-grep
   ↓
structured code evidence
   ↓
code-map.jsonl
```

**Não automatize rewrites ainda.**

Primeiro valide precisão.

---

# PASS 7 — SCIP

Depois ast-grep, não antes.

Teste:

```text
Python backend
+
TypeScript clients
```

SCIP já possui ecossistema de indexadores para Python e TypeScript, além do protocolo comum. ([GitHub][2])

Seu objetivo é gerar:

```text
symbol
definition
references
implementations
```

e transformar em algo como:

```text
.generated/knowledge/
└── symbols.jsonl
```

Agora o `symbols.jsonl` deixa de ser apenas 11 símbolos manualmente extraídos e passa a ter uma fonte semântica real.

---

# PASS 8 — Automatize Mermaid

**Só aqui eu faria o generator.**

Porque agora você tem:

```text
Docs
+
links
+
ownership
+
code-map
+
ast-grep
+
SCIP
```

Então:

```bash
just docs-diagrams
```

pode gerar:

```text
.generated/diagrams/
├── subsystem-map.mmd
├── dependency-map.mmd
└── symbol-map.mmd
```

### Mas cuidado

Eu separaria:

**Generated diagrams**

```text
.generated/diagrams/
```

para visualizações exploratórias.

**Canonical explanatory diagrams**

```text
docs/.../workflows/*.md
```

revisados por humano/agent e mantidos deliberadamente.

Um call graph completo de 1.000 nós não é documentação.

É telemetria visual.

---

# PASS 9 — Obsidian Second Brain

Agora é praticamente grátis.

Abra:

```text
Aether-D-System/docs/
```

como Vault.

Não copie.

Não faça:

```text
repo/docs/
+
~/Obsidian/Aether/
```

Isso cria duas verdades.

Use:

```text
repo/docs = Vault
```

Obsidian passa a fornecer:

```text
backlinks
graph
local graph
search
editing
Canvas opcional
```

Mas mantenha Markdown normal.

---

# PASS 10 — RAG V0

Agora faça o primeiro RAG **sem vector DB**.

Pipeline:

```text
question
   ↓
exact canonical IDs
   ↓
metadata filter
   ↓
keyword/full-text
   ↓
ownership
   ↓
links
   ↓
code-map
   ↓
symbols
   ↓
top relevant canonical sources
   ↓
LLM
```

Isso já é um RAG estruturado.

Teste com perguntas reais:

```text
How does recursive delegation work?

Where is effect authorization enforced?

How does cold recovery work?

What must change to modify event/2?

Which tests verify budget attenuation?
```

Meça:

```text
precision
missing context
tokens
latency
wrong authority
```

---

# PASS 11 — Só depois embeddings

Se o RAG V0 falhar em perguntas sem vocabulário exato:

```text
BM25 / exact / graph
+
embedding similarity
```

Não substitua estrutura por embeddings.

Use embeddings como **mais um sinal**.

---

# PASS 12 — Docling/Pandoc são ferramentas sob demanda

Não precisa instalar agora se não estiver importando documentos.

Quando aparecer:

```text
PDF
Word
PPT
XLSX
```

use Docling.

O projeto atualmente instala simplesmente via `pip install docling` ou `uv add docling` e oferece CLI e export para Markdown/estruturas processáveis. ([Docling Project][10])

Para:

```text
RST
HTML
LaTeX
Org
legacy markup
```

Pandoc.

Eles são:

```text
INGESTION
```

não:

```text
DAILY DOCUMENTATION RUNTIME
```

---

# Seu guia está certo?

**Sim, ~85–90%.** Eu corrigiria principalmente estas partes:

| Seu guia                           | Ajuste                                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------------------ |
| “MkDocs + Lychee primeiro”         | MkDocs/Mermaid primeiro; depois quality stack                                                    |
| “pre-commit instala markdownlint”  | pre-commit **orquestra hooks**; markdownlint é uma ferramenta separada                           |
| “não precisa código P0”            | quase; vocês **já têm e devem manter pequena cola proprietária** para metadata/catalog/knowledge |
| SCIP junto das ferramentas básicas | mover para **P1 experimental**                                                                   |
| ast-grep junto das básicas         | mover para **P1**                                                                                |
| Docling como stack regular         | somente **ingestion on demand**                                                                  |
| TypeDoc agora                      | esperar frontend estabilizar                                                                     |
| frontmatter mostrado               | simplificar para ~7 campos permanentes                                                           |
| Mermaid                            | adicionar explicitamente ao P0                                                                   |
| `.generated/knowledge`             | incorporar como IR regenerável central                                                           |
| `just`                             | adicionar como interface única                                                                   |
| Obsidian/RAG                       | adicionar como consumers após P0                                                                 |

---

# Quem deve executar isso?

**Sim: dê para um agentic coding agent competente**, porque ele deve trabalhar diretamente sobre o repo e validar cada mudança.

Não peça:

> “instale todas essas bibliotecas e construa Atlas.”

Peça uma fase por vez.

Minha ordem de trabalho para o agente seria:

```text
TASK 1  MkDocs + Mermaid
TASK 2  Schema/markdownlint/Vale/Lychee
TASK 3  pre-commit + CI
TASK 4  justfile orchestration
TASK 5  normalize permanent frontmatter
TASK 6  integrate existing generated knowledge
TASK 7  create canonical Mermaid workflows
──── P0 DONE ────
TASK 8  mkdocstrings/Griffe
TASK 9  ast-grep experiment
TASK 10 SCIP experiment
──── P1 DONE ────
TASK 11 RAG V0
TASK 12 Obsidian conveniences
TASK 13 proto-Atlas
```

Eu deixaria o **Obsidian antes ou depois do RAG sem grande consequência**, porque é quase só uma view; mas P0 precisa estar pronto primeiro.

---

# Prompt para começar agora

Eu começaria **somente pelo P0**, usando o relatório master como referência, e pediria ao agente para não tocar no Atlas ainda:

Act as the Senior Documentation Infrastructure Engineer for AETHER.

Implement **P0 of the AETHER Documentation Control Plane** against the repository as it exists now.

Do not redesign or reorganize the canonical `docs/` hierarchy. The documentation reconstruction and cutover are complete.

Use the existing canonical documentation, existing validation scripts, and `.generated/knowledge/` pipeline as the baseline. Preserve current behavior unless a small correction is required to make the permanent docs infrastructure work.

## Goal

Turn the current clean `docs/` tree into a professional docs-as-code system using mature OSS, while keeping Markdown + Git as the source of truth.

Implement, in this order:

1. MkDocs + Material for MkDocs.
2. Native Mermaid rendering through Material/MkDocs.
3. Minimal permanent frontmatter/schema validation using the existing metadata model; simplify reconstruction-only metadata only where safe.
4. markdownlint-cli2.
5. Vale with a very small AETHER terminology ruleset based only on proven terminology drift.
6. Lychee for external-link validation while preserving the existing stronger repository-specific internal link/anchor checks.
7. pre-commit containing only fast local checks.
8. CI documentation validation containing the full checks.
9. A `justfile` documentation interface exposing:

   * `just docs-check`
   * `just docs-build`
   * `just docs-serve`
   * `just docs-knowledge`
   * `just docs-full`
10. Integrate the existing deterministic `.generated/knowledge/` rebuild rather than replacing it.
11. Create the initial canonical Mermaid workflow documentation from code-first evidence.

Initial Mermaid documentation should be limited to high-value architecture flows:

```text
docs/architecture/workflows/
  end-to-end-execution.md
  system-bootstrap.md

docs/backend/architecture/workflows/
  request-execution.md
  agent-lifecycle.md
  event-lifecycle.md
  delegation.md
  recovery-resume.md
```

Before writing each workflow, inspect the actual implementation, tests, schemas, current canonical architecture docs, `code-map.jsonl`, `symbols.jsonl`, and relevant relationships.

Do not infer runtime behavior from documentation alone.

The Mermaid diagrams are explanatory architecture documentation, not exhaustive call graphs.

## Dependency policy

Use the repository's existing canonical Python and Node dependency-management strategy.

Do not introduce a third lockfile or another package manager.

Pin/version dependencies using the repository's existing reproducibility conventions.

## Do not implement yet

Do NOT introduce:

* Atlas;
* PKIR;
* vector databases;
* embeddings;
* GraphRAG;
* Neo4j;
* Glean;
* Joern;
* OpenRewrite;
* direct Tree-sitter integration;
* SCIP;
* ast-grep-based production automation;
* TypeDoc while frontend documentation is intentionally deferred;
* a new docs taxonomy;
* another archive;
* new reconstruction reports.

SCIP and ast-grep belong to P1 after P0 is validated.

## Generated artifacts

Keep `.generated/knowledge/` non-authoritative, deterministic, small, and completely rebuildable.

Do not place reconstruction history there.

## Validation

At completion, prove:

1. `mkdocs build --strict` passes.
2. Mermaid diagrams render correctly.
3. metadata/schema validation passes.
4. canonical IDs remain unique.
5. markdownlint passes.
6. Vale passes at the configured severity.
7. internal links/anchors pass.
8. external link validation is operational.
9. stale-path validation passes.
10. `.generated/knowledge/` survives a zero rebuild.
11. pre-commit runs successfully.
12. CI-equivalent docs checks pass.
13. production runtime behavior was not modified.

Prefer configuration and existing OSS over custom code.

Only add proprietary code when an AETHER-specific invariant cannot be expressed by an existing tool.

At the end, report:

* dependencies added;
* configuration files added/modified;
* commands available;
* Mermaid workflows created;
* custom glue retained/added and why it was necessary;
* validation results;
* deferred P1 work.

Final verdict:

`AETHER DOCUMENTATION CONTROL PLANE P0 COMPLETE`

or clearly state the blocking condition.

---

## A sequência completa, em uma linha

```text
CLEAN DOCS
→ MkDocs/Mermaid
→ schema/lint/Vale/links
→ pre-commit/CI
→ just
→ generated knowledge
→ canonical workflows
→ Griffe
→ ast-grep
→ SCIP
→ Obsidian
→ structured RAG
→ PKIR
→ Atlas
```

Essa é a ordem que eu usaria. **A partir daqui você não está mais “organizando Markdown”; está progressivamente compilando o repositório em conhecimento estruturado, sem construir Atlas antes de descobrir empiricamente o que ele realmente precisa fazer.**

[1]: https://squidfunk.github.io/mkdocs-material/reference/diagrams/?utm_source=chatgpt.com "Diagrams - Material for MkDocs"
[2]: https://github.com/scip-code/scip/?utm_source=chatgpt.com "GitHub - scip-code/scip: SCIP Code Intelligence Protocol · GitHub"
[3]: https://squidfunk.github.io/mkdocs-material/getting-started/?utm_source=chatgpt.com "Installation - Material for MkDocs"
[4]: https://github.com/DavidAnson/markdownlint-cli2/blob/main/README.md?utm_source=chatgpt.com "markdownlint-cli2/README.md at main · DavidAnson/markdownlint-cli2 · GitHub"
[5]: https://vale.sh/?utm_source=chatgpt.com "Vale: Your style, our editor"
[6]: https://pre-commit.com/?utm_source=chatgpt.com "pre-commit"
[7]: https://mkdocstrings.github.io/python/usage/?utm_source=chatgpt.com "Usage - mkdocstrings-python"
[8]: https://typedoc.org/?utm_source=chatgpt.com "TypeDoc"
[9]: https://ast-grep.github.io/guide/quick-start?utm_source=chatgpt.com "Quick Start | ast-grep"
[10]: https://docling-project.github.io/docling/getting_started/installation/?utm_source=chatgpt.com "Installation - Docling"

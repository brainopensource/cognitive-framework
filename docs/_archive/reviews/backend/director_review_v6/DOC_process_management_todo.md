Separe o trabalho em **descoberta determinística → interpretação arquitetural → produção mecânica → auditoria**, usando modelo frontier só onde existe ambiguidade semântica ou decisão arquitetural.

| Etapa                         | Trabalho                                                                                             | Quem                                                     | Resultado                            |
| ----------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------ |
| **1. Baseline**               | Criar branch, registrar SHA, inventariar repo/docs/code/tests/schemas                                | **Dev ou IA simples**                                    | `inventory.jsonl`, árvore do repo    |
| **2. Extração**               | Rodar `rg`, ast-grep, SCIP, extrair packages, symbols, schemas, CLI, testes                          | **Dev / IA simples**                                     | mapas estruturais e evidence index   |
| **3. Architecture Discovery** | Entender de fato Kernel, Runtime, Agency, Events, Plugins, estado, fluxos e boundaries               | **GPT-5.6 Sol / Opus**                                   | arquitetura `AS_BUILT` validada      |
| **4. Doc Mapping**            | Decidir quais arquivos novos existirão, ownership, IDs, o que vira architecture/reference/guide/etc. | **Frontier**                                             | blueprint final de `candidate-docs/` |
| **5. Document Generation**    | Criar páginas individuais seguindo blueprint e evidências já determinadas                            | **Sonnet / Luna High / Dev**                             | Markdown novo                        |
| **6. Machine Layer**          | Frontmatter, JSON Schema, catalog, relations, code-map, MkDocs, Mermaid                              | **IA simples / Dev**                                     | docs estruturadas/indexadas          |
| **7. Legacy Audit**           | Procurar no legado apenas conhecimento único perdido: decisões, invariantes, requirements futuros    | **Frontier** para conflitos; **IA simples** para triagem | lista `retain/obsolete/unresolved`   |
| **8. Mechanical Cleanup**     | links, terminology, markdownlint, Vale, Lychee, paths, metadata                                      | **Dev / IA simples**                                     | validação limpa                      |
| **9. Final Audit**            | Comparar docs novas × código × testes × schemas × Vision/target e procurar erro conceitual           | **Frontier diferente do autor**                          | review final                         |
| **10. Cutover**               | substituir `docs/`, remover legado já absorvido, CI/pre-commit                                       | **Dev**                                                  | documentação oficial                 |

### Regra simples de delegação

```text
DETERMINÍSTICO / REPETITIVO
→ scripts + Dev + IA normal

ESCRITA COM ESTRUTURA JÁ DECIDIDA
→ Sonnet / Luna High

AMBIGUIDADE / CONFLITO / ARQUITETURA / OWNERSHIP
→ GPT-5.6 Sol / Opus

AUDITORIA FINAL
→ outro Frontier independente
```

Eu administraria em **quatro blocos**, sem mandar o mega-prompt inteiro de uma vez:

```text
BLOCK A — Dev / IA simples
Inventory + static extraction

        ↓

BLOCK B — Frontier
Discover AS_BUILT architecture
+ design canonical docs map

        ↓

BLOCK C — IA normal + Dev
Generate documents
+ metadata + indexes + diagrams + validation

        ↓

BLOCK D — Frontier
Legacy-loss audit
+ independent final architecture review
```

O ponto crítico é **não gastar Frontier extraindo arquivos, corrigindo links, escrevendo frontmatter ou criando 30 páginas cuja arquitetura já foi decidida**; use Frontier para descobrir **o que é verdade, como o sistema se organiza, onde cada conhecimento pertence e onde existem conflitos**, e delegue todo o resto.

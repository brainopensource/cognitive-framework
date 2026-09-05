---
id: sota-skills-techniques-proficiencies-guide
class: operational-guide
authority: operational-staging
status: active
version: "1.0.0"
date: "2026-09-05"
owner: engineering-architecture-council
applicable_trees:
  - ".agents/"
  - "vanguard/packages/adapters/models/"
  - "tools/"
---

# Guia Operacional SOTA: Skills, Techniques, Proficiencies e Roteamento Híbrido

Este documento consolida tudo o que foi implementado no repositório, como operar os componentes hoje, como testar e validar combinações locais e em nuvem (OpenRouter) e o roteiro de próximas etapas.

---

## 1. O Que Foi Feito (Status do Sistema)

Materializamos a progressão ontológica completa:
$$\text{Skill (Atômica)} \longrightarrow \text{Technique (Malha Aberta)} \longrightarrow \text{Proficiency (Malha Fechada)} \longrightarrow \text{Mastery (Adaptação Estratégica)}$$

### A. Capacidades no Sistema de Arquivos (`.agents/`)
1. **Skills Atômicas (`.agents/skills/`)**:
   - `lda-navigator`: Indexação e fatiamento simbólico de AST em SQLite-WAL ($<25\text{ms}$ para deltas).
   - `llama-cpp`: Inferência neural local via `llama-server` nativo com aceleração Vulkan em GPU AMD.
   - `test-runner`: Executor hermético e isolado de testes unitários com captura de streams e exit codes.
   - *Bridges*: `.agents/skills/{spec-driven-codegen, tdd-falsifier, autofix-loop}/SKILL.md` para compatibilidade com ferramentas que só descobrem skills.
2. **Techniques em Malha Aberta (`.agents/techniques/`)**:
   - `spec-driven-codegen`: Script [`generate_grounded_patch.py`](file:///home/rock-dev/Coding/cognitive-framework/.agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py) que compila o contexto de AST e invariantes antes de gerar o código, eliminando alucinações.
   - `tdd-falsifier`: Script [`run_falsifier.py`](file:///home/rock-dev/Coding/cognitive-framework/.agents/techniques/tdd-falsifier/scripts/run_falsifier.py) que mapeia alvos para suítes de teste via LDA e extrai `DiagnosticReport`.
3. **Proficiency em Malha Fechada (`.agents/proficiencies/`)**:
   - `autofix-swe-loop`: Orquestrador [`autofix_harness.py`](file:///home/rock-dev/Coding/cognitive-framework/.agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py) com ciclo Plan $\to$ Patch $\to$ Delta Sync $\to$ Test $\to$ Traceback Feedback $\to$ Verification/Rollback.

### B. Núcleo Vanguard / AETHER
1. **Cascading ModelPort Adapter** ([`cascade.py`](file:///home/rock-dev/Coding/cognitive-framework/vanguard/packages/adapters/models/cascade.py)):
   - Implementa `ModelPort` unindo modelo local primário e fallback secundário/fronteira com limiar de falhas consecutivas.
   - Zero dependências de `kernel` ou `agency` (100% em conformidade com fronteiras hexagonais).
2. **Fábrica e Seleção de Modelos**:
   - Registrado `"cascade"` e `"tiered"` em [`factory.py`](file:///home/rock-dev/Coding/cognitive-framework/vanguard/packages/adapters/models/factory.py) e [`model_selection.py`](file:///home/rock-dev/Coding/cognitive-framework/vanguard/packages/runtime/model_selection.py).
3. **Ponte Universal de Sincronização** ([`tools/universal_mcp_sync.py`](file:///home/rock-dev/Coding/cognitive-framework/tools/universal_mcp_sync.py)):
   - Espelha automaticamente skills, techniques e proficiencies para Claude Code (`~/.claude/`), Cursor (`~/.cursor/`), Codex CLI (`~/.codex/`) e Antigravity (`~/.gemini/`).
4. **Verificação de Regressão**:
   - [`test/runtime/test_techniques_and_proficiencies.py`](file:///home/rock-dev/Coding/cognitive-framework/test/runtime/test_techniques_and_proficiencies.py): 7/7 testes verdes em 0.002s.
   - TCB do Kernel mantido em 1386 LOC (52 linhas abaixo do teto de 1438).

---

## 2. Como Usar Hoje (Runbook Prático)

### A. Falsificação TDD Determinística
Para descobrir e rodar imediatamente os testes associados a qualquer arquivo alterado:
```bash
python3 .agents/techniques/tdd-falsifier/scripts/run_falsifier.py vanguard/packages/runtime/explain.py
# Saída estruturada em JSON:
python3 .agents/techniques/tdd-falsifier/scripts/run_falsifier.py vanguard/packages/kernel/attenuation.py --json
```

### B. Geração de Patches Ancorados na AST (Technique 1)
Para sintetizar código com contexto simbólico garantido via LLM local:
```bash
python3 .agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py \
  --task "Implementar validação estrita de tipos" \
  --target-file "vanguard/packages/runtime/explain.py" \
  --budget 2500 \
  --json
```

### C. Ciclo de Auto-Reparo Fechado (Proficiency 1)
Para disparar o loop de auto-correção com limite de turnos, re-indexação incremental e rollback:
```bash
python3 .agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py \
  --task "Corrigir falha no teste de monotonicidade" \
  --target-file "vanguard/packages/kernel/attenuation.py" \
  --max-turns 3
```

### D. Sincronização Universal entre CLIs
Para atualizar os links simbólicos de todos os harnesses de IA instalados:
```bash
python3 tools/universal_mcp_sync.py --sync
```

---

## 3. Validação e Testes Multi-Modelo (Local vs OpenRouter)

O sistema suporta três modos operacionais de modelos:

### Matriz de Combinações de Modelos

| Perfil | Primário | Secundário (Fallback) | Custo | Latência Típica | Quando Usar |
|---|---|---|---|---|---|
| **Local Rápido** | Qwen-1.5B (Vulkan) | Nenhum | $0.00 | ~0.8s (130 tok/s) | Edições simples, formatação, testes locais |
| **Local Médio** | Qwen-14B / 27B | Nenhum | $0.00 | ~2.5s (45 tok/s) | Refatoração de escopo médio |
| **Híbrido Cascata** | Qwen-1.5B Local | Claude 3.5 Sonnet / OpenRouter | Misto | Sub-segundo a 3s | **Padrão de Produção**: 80% grátis, 20% nuvem |
| **Fronteira Pura** | OpenRouter (Smart) | OpenRouter (Medium) | Orçado | 3s a 8s | Tarefas multi-arquivo e raciocínio complexo |

### Configuração de Ambiente para Testes

1. **Testar com Modelo Local Puro**:
   ```bash
   export VANGUARD_LLAMA_ENDPOINT="http://127.0.0.1:8080/v1/chat/completions"
   # Lançar llama-server se não estiver em execução:
   llama-server -m ~/Models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf -ngl 99 -c 4096 --port 8080 &
   ```

2. **Testar com Roteamento em Cascata (Local -> Nuvem)**:
   ```bash
   export OPENROUTER_API_KEY="sua-chave-openrouter"
   export VANGUARD_ALLOW_PAID="true"
   # O adapter tentará o modelo local; se falhar ou esgotar tentativas, escalará automaticamente.
   ```

3. **Verificar Prontidão de Todos os Provedores**:
   ```python
   from vanguard.packages.runtime.model_selection import inspect_model_providers
   print(inspect_model_providers())
   ```

---

## 4. O Que Devemos Fazer a Seguir (Roadmap Priorizado)

### Fase 1: Ergonomia de Produto (Curto Prazo)
- [ ] **Comando `vg autofix` na CLI Ink**:
  - Expor a Proficiency diretamente na CLI Vanguard (`vanguard/clients/cli/`) para que o desenvolvedor execute `vg autofix "descricao do bug"` diretamente do terminal interativo.
- [ ] **Integração com `CodingMaxFacade`**:
  - Permitir que o preset `fast` use `cascade` como modelo padrão em vez de `mock`/`fake`.

### Fase 2: Benchmark Formal e Qualificação M-8 (Médio Prazo)
- [ ] **Bateria de 20 Tarefas Empíricas**:
  - Executar a Proficiency contra uma amostra congelada de 20 bugs reais do framework.
  - Medir: taxa de resolução sem intervenção (*pass rate*), consumo médio de tokens e número de turnos até o sucesso.
- [ ] **Aferição do Orçamento Físico do Kernel**:
  - Validar que o `Governor` bloqueia fisicamente chamadas pagas à OpenRouter caso a reserva em `usd_micros` seja excedida.

### Fase 3: Expansão Greenfield e Escala Horizontal (Longo Prazo)
- [ ] **Technique 3 (`greenfield-scaffolder`)**:
  - Implementar o protocolo de 3 fases para novos componentes: criar stubs $\to$ escrever testes falsificadores vermelhos $\to$ implementar até exit code 0.
- [ ] **Test-Time Compute Scaling**:
  - Branching efêmero em worktrees git isolados, gerando 3 soluções em paralelo com modelos locais e selecionando a vencedora via falsificador determinístico.

---

## 5. Invariantes Invioláveis do Repositório

1. **Teto do Kernel TCB ($\le 1438$ LOC)**:
   - Todo novo código de automação, parsing e rede pertence estritamente a `adapters/`, `domain/`, `agency/` ou `.agents/`.
2. **Pureza Hexagonal**:
   - `domain ← ports ← kernel ← agency ← runtime → adapters`. Os adaptadores jamais importam `kernel` ou `agency`.
3. **Veto de Falsa Conclusão**:
   - O sistema nunca aceita autodeclaração de sucesso por prompt. A conclusão requer verificação executada com `exit code == 0`.
4. **Fail-Closed**:
   - Em caso de estouro de orçamento ou esgotamento de turnos, o rollback restaura o workspace para o estado limpo.

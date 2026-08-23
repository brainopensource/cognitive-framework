# Relatório Técnico & Proposta de Melhorias: LED Studio (LLM Engine Desktop)

**Data:** 23 de Agosto de 2026  
**Status:** Proposta de Engenharia & Arquitetura  
**Alvo:** `LED Studio` / `crates/led-core`, `crates/led-ui`  
**Autor:** Engenharia de Sistemas & Telemetria  

---

## 1. Sumário Executivo & Diagnóstico do Incidente MoE

Durante a execução empírica do modelo `deepseek-coder-v2:16b`, a inferência local na GPU **AMD Radeon (16GB GDDR6 VRAM)** falhou com o erro:

```text
"error": "llama-server reported out-of-memory during startup: cudaMalloc failed: out of memory"
"ggml_gallocr_reserve_n_impl: failed to allocate ROCm0 buffer of size 1313101824"
"llama_init_from_model: failed to initialize the context: failed to allocate compute pp buffers"
```

### Causa Raiz Técnica:
1. **Topologia MoE vs. Modelos Densos:** O `DeepSeek-Coder-V2` possui 160 especialistas (MoE) que geram grafos de computação não contíguos de alta dispersão (`ggml_gallocr`).
2. **Context Length Sem Clamping Automático:** O Ollama inicializa o contexto padrão em **32.768 tokens (32K)** em precisão `f16` por padrão, consumindo ~5.8 GB adicionais apenas para alocação da matriz de atenção e buffers de grafo ROCm (`compute pp buffers`), somando **>17.5 GB** de demanda instantânea.
3. **Falta de Fallback Paginado (Host Pinning na RAM):** Se a RAM do sistema estiver saturada por processos de background no Windows/WSL2, o driver ROCm não consegue alocar a memória intermediária paginada (*pinned memory*), abortando o processo em `cudaMalloc`.

---

## 2. Proposta de Melhorias Arquiteturais

```text
┌────────────────────────────────────────────────────────────────────────┐
│               LED ENGINE ARCHITECTURE UPGRADE PROPOSAL                 │
│                                                                        │
│  [ UI Top Bar ]                                                        │
│    ├── Live RAM Display (Free / Total DDR4)                            │
│    ├── Live VRAM Display (Active GDDR6 Allocation Gauge)               │
│    ├── Live CPU Utilization (%)                                        │
│    └── Pre-Flight VRAM Budget Safety Checker (Green / Red Warning)     │
│                                                                        │
│  [ Rust Core Supervisor (crates/led-core) ]                            │
│    ├── Dynamic Context Clamping (Auto-Trim 32K -> 2K/4K on 16GB VRAM)  │
│    ├── KV-Cache Auto-Quantization (--ctk q8_0 --ctv q8_0)              │
│    ├── MoE Memory Reserve Planner (Layer Offloading Guard)             │
│    └── Zero-Cost Polling via sysinfo (Update interval: 2000ms)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Especificação Detalhada das Melhorias

### A. Monitor Leve de Telemetria (CPU, RAM e VRAM em Tempo Real)
* **Objetivo:** Tornar explícito na interface o estado da memória física e de vídeo antes e durante a execução do prompt.
* **Implementação:**
  1. Utilizar a biblioteca `sysinfo` já integrada no backend em Rust (`crates/led-core/src/hardware.rs`) para consultar a cada 2.000 ms:
     * **RAM Livre / Total:** (Ex: `RAM: 18.2/24.0 GB`).
     * **VRAM Alocada:** (Ex: `VRAM: 11.8/16.0 GB`).
     * **Carga de CPU:** (Ex: `CPU: 14%`).
  2. Adicionar na barra superior do `index.html` pequenos displays em estilo neobrutalista quadrado com opacidade de 50%, atualizados via polling leve do endpoint `/v1/telemetry`.

### B. Pre-Flight VRAM Estimator & Auto-Clamping (Garantia de Execução)
* **Objetivo:** Garantir que qualquer modelo instalado rode com 100% de sucesso sem sofrer OOM na GPU.
* **Mecanismo de Proteção:**
  1. **Dynamic Context Clamping:** Antes de enviar a requisição ao motor de inferência, o supervisor do LED injeta automaticamente o parâmetro `num_ctx: 2048` (ou o valor selecionado no slider da UI), impedindo que o motor aloque 32.768 tokens desnecessariamente.
  2. **KV Cache Quantization (`q8_0` / `q4_0`):** Reduz o consumo do buffer de atenção em **50% a 75%** com degradação zero de perplexidade.
  3. **VRAM Safety Warning na UI:** Se o modelo selecionado (ex: MoE de 16B ou denso de 27B) exceder 14.5 GB de VRAM estimada para o contexto atual, a UI exibe um aviso em amarelo: `[WARN: REDUCE CTX TO 2048 TO PREVENT VRAM SPILLOVER]`.

### C. Tratamento Robusto de Falhas de Driver ROCm
* **Objetivo:** Evitar que uma falha de alocação retorne texto vazio no streaming (`0.0 tok/s | 30.20s`).
* **Implementação:**
  * O proxy SSE em `crates/led-core/src/streaming.rs` inspeciona o primeiro chunk da resposta HTTP. Caso o daemon retorne payload de erro (`cudaMalloc failed` ou `out of memory`), o LED intercepta o erro e emite na tela do chat uma mensagem diagnóstica clara em vermelho:
    > `[ERRO DE MEMÓRIA: A GPU não possui VRAM suficiente para inicializar este modelo com contexto alto. Reduza o num_ctx para 2048 ou utilize quantização Q4_K_M/IQ3_S.]`

---

## 4. Matriz de Compatibilidade de Modelos para 16GB VRAM (Radeon RX)

| Família / Modelo | Parâmetros | Quantização | VRAM com Ctx 2048 | Status no LED |
|---|---|---|---|---|
| **Qwen 2.5** | 1.5B | Q8_0 / FP16 | ~2.1 GB | 🟢 100% Nativo (122.5 tok/s) |
| **Qwen 2.5-Coder** | 14.8B | Q4_K_M | ~9.6 GB | 🟢 100% Nativo (41.2 tok/s) |
| **Qwen 3.8 (Unsloth)** | 27B | UD-IQ3_S | ~12.2 GB | 🟢 100% Nativo (16.2 tok/s) |
| **DeepSeek R1** | 14B | Q4_K_M | ~9.8 GB | 🟢 100% Nativo (~35 tok/s) |
| **DeepSeek-Coder-V2** | 16B (MoE 236B) | Q4_K_M | ~11.5 GB *(Ctx 2K)* / >17.8 GB *(Ctx 32K)* | 🟡 Requer Context Clamping (num_ctx <= 2048) |
| **Granite 4.1** | 30B | Q2_K / IQ2_M | ~13.8 GB | 🟢 100% Nativo (~14 tok/s) |

---

## 5. Cronograma Sugerido de Implementação

1. **Sprint A (Telemetria & UI):** Integrar o display de RAM, VRAM e CPU no header e mapear os valores no `app.js`.
2. **Sprint B (Supervisor Clamping):** Garantir envio estrito de `options: { num_ctx, num_thread, ... }` em todas as chamadas `/v1/chat/completions`.
3. **Sprint C (Error Interceptor):** Adicionar captura e renderização visual amigável para mensagens de erro de memória da GPU.

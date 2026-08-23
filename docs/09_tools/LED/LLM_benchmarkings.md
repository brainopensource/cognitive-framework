# TOP LLMs: MODELOS GRATUITOS E OPEN-WEIGHTS (HARDWARE: RX 9060 16GB VRAM + 32GB RAM + RYZEN 7 5800X3D)

> **NON-NORMATIVE / FROZEN PROVENANCE**
>
> This file preserves historical tooling and benchmark research in its original language. It does
> not authorize implementation, current model selection, or roadmap changes.

Esta seção analisa os **Top 10 melhores modelos de linguagem gratuitos (open-weights)** especificamente ranqueados com base nas especificações exatas da sua máquina: **AMD Radeon RX 9060 16GB VRAM**, **32GB RAM** (~22GB de RAM do sistema disponíveis) e **CPU Ryzen 7 5800X3D** (com 96MB L3 V-Cache, garantindo offloading de CPU ultra-eficiente se necessário).

### AVALIAÇÃO EM 3 BENCHMARKS ESTRATÉGICOS DA INDÚSTRIA:
1. **SWE-bench Verified:** Resolução real de problemas complexos de software e bugs em projetos reais do GitHub.
2. **Aider Polyglot Benchmark:** Capacidade de edição multi-arquivo e refatoração de código sem intervenção humana.
3. **LiveCodeBench / GPQA:** Capacidade de geração de algoritmos competitivos e raciocínio lógico em nível de doutorado.

---

### TABELA COMPARATIVA DOS TOP 10 MODELOS GRATUITOS (3 BENCHMARKS)

| Ranking | Modelo Ollama | Parâmetros / Quantização | VRAM / RAM Alocada | SWE-bench Verified | Aider Polyglot | LiveCodeBench / GPQA | Desempenho Estimado (RX 9060 + Ryzen) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1º** | `qwen2.5-coder:32b` | 32.5B (Q4_K_M) | 15.2 GB VRAM | **55.4%** | **73.7%** | **55.4% / 41.7%** | **~35 t/s** (100% VRAM) |
| **2º** | `deepseek-r1:32b` | 32.5B (Q4_K_M / Q3_K_M) | 15.2 GB VRAM | **50.8%** | **71.2%** | **57.2% / 62.1%** | **~30 t/s** (100% VRAM) |
| **3º** | `deepseek-r1:14b` | 14.7B (Q4_K_M) | 9.0 GB VRAM | **50.8%** | **68.5%** | **53.1% / 59.1%** | **~60 t/s** (100% VRAM) |
| **4º** | `qwen2.5-coder:14b` | 14.7B (Q4_K_M) | 9.0 GB VRAM | **42.8%** | **66.4%** | **42.8% / 41.2%** | **~65 t/s** (100% VRAM) |
| **5º** | `gemma2:27b` | 27.2B (Q4_K_M) | 15.0 GB VRAM | **38.5%** | **61.0%** | **40.1% / 41.9%** | **~35 t/s** (100% VRAM) |
| **6º** | `deepseek-r1:7b` | 7.6B (Q4_K_M) | 4.7 GB VRAM | **42.1%** | **62.0%** | **41.5% / 49.1%** | **~90 t/s** (100% VRAM) |
| **7º** | `qwen2.5:14b` | 14.7B (Q4_K_M) | 9.0 GB VRAM | **37.1%** | **58.2%** | **37.1% / 46.2%** | **~65 t/s** (100% VRAM) |
| **8º** | `qwen2.5-coder:7b` | 7.6B (Q4_K_M) | 4.7 GB VRAM | **34.2%** | **57.1%** | **34.2% / 35.8%** | **~90 t/s** (100% VRAM) |
| **9º** | `llama3.1:8b` | 8.0B (Q4_K_M) | 5.2 GB VRAM | **26.5%** | **49.8%** | **28.1% / 30.4%** | **~85 t/s** (100% VRAM) |
| **10º**| `phi3.5:3.8b` | 3.8B (Q4_K_M) | 2.3 GB VRAM | **21.0%** | **41.2%** | **23.0% / 29.8%** | **~120 t/s** (100% VRAM) |

---

# AUDITORIA DE PERFORMANCE PARA 16GB VRAM (AMD RADEON RX 9060)

Este documento analisa os 10 melhores modelos de linguagem (LLMs) open-weights capazes de rodar em placas de vídeo com **16GB de VRAM** (como a AMD Radeon RX 9060) e **32GB de RAM**, avaliados com base nos dois principais benchmarks globais da indústria:

1. **SWE-bench (Verified / LiveCodeBench):** Avalia a capacidade real de engenharia de software, resolução de issues em repositórios complexos do GitHub e geração de código funcional.
2. **GPQA (Graduate-Level Google-Proof Q&A):** Avalia raciocínio acadêmico profundo, ciências exatas e capacidade de resposta a perguntas complexas em nível de doutorado sem alucinação.

---

## TABELA COMPARATIVA GERAL (RANKING GERAL)

> **Nota de Hardware:** Todos os modelos listados cabem totalmente na VRAM de 16GB utilizando quantizações GGUF otimizadas (Q3_K_M, Q4_K_M ou Q5_K_M), atingindo máxima aceleração via Ollama.

| Ranking | Modelo Ollama | Tam. Parâmetros | Quantização | VRAM Usada | SWE-bench / LiveCodeBench | GPQA Diamond | Velocidade (RX 9060) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1º** | `deepseek-r1:32b` *(Distill-Qwen)* | 32.5B | Q3_K_M / Q4_K_S | ~15.2 GB | **50.8%** | **62.1%** | ~25 - 35 t/s |
| **2º** | `qwen2.5-coder:32b` | 32.5B | Q3_K_M / Q4_K_S | ~15.2 GB | **55.4%** | **41.7%** | ~30 - 40 t/s |
| **3º** | `deepseek-r1:14b` *(Distill-Qwen)* | 14.7B | Q4_K_M | ~9.0 GB | **50.8%** | **59.1%** | ~50 - 65 t/s |
| **4º** | `qwen2.5-coder:14b` | 14.7B | Q4_K_M | ~9.0 GB | **42.8%** | **41.2%** | ~55 - 70 t/s |
| **5º** | `gemma2:27b` | 27.2B | Q4_K_M | ~15.0 GB | **38.5%** | **41.9%** | ~30 - 40 t/s |
| **6º** | `deepseek-r1:7b` *(Distill-Qwen)* | 7.6B | Q4_K_M | ~4.7 GB | **42.1%** | **49.1%** | ~80 - 100 t/s |
| **7º** | `qwen2.5:14b` | 14.7B | Q4_K_M | ~9.0 GB | **37.1%** | **46.2%** | ~55 - 70 t/s |
| **8º** | `qwen2.5-coder:7b` | 7.6B | Q4_K_M | ~4.7 GB | **34.2%** | **35.8%** | ~80 - 100 t/s |
| **9º** | `llama3.1:8b` | 8.0B | Q4_K_M | ~5.2 GB | **26.5%** | **30.4%** | ~75 - 95 t/s |
| **10º**| `phi3.5:3.8b` | 3.8B | Q4_K_M | ~2.3 GB | **21.0%** | **29.8%** | ~110 - 140 t/s |

---

## RANKING 1: ENGENHARIA DE SOFTWARE & PROGRAMAÇÃO (SWE-bench / LiveCodeBench)

Focado em resolução de problemas reais de código, edição de arquivos e lógica de sistemas.

1. **`qwen2.5-coder:32b`** – **55.4%** *(Líder absoluto para coding completo em 16GB VRAM)*
2. **`deepseek-r1:32b`** – **50.8%** *(Excelente com raciocínio Chain of Thought avançado)*
3. **`deepseek-r1:14b`** – **50.8%** *(Melhor custo-benefício de VRAM vs capacidade)*
4. **`qwen2.5-coder:14b`** – **42.8%** *(Super rápido e extremamente preciso em autocompletar e refatoração)*
5. **`deepseek-r1:7b`** – **42.1%** *(Modelo leve de raciocínio de código)*
6. **`gemma2:27b`** – **38.5%** *(Arquitetura do Google focada em contexto técnico)*
7. **`qwen2.5:14b`** – **37.1%** *(Modelo de uso geral balanceado)*
8. **`qwen2.5-coder:7b`** – **34.2%** *(Ótimo para autocompletar em tempo real no VS Code)*
9. **`llama3.1:8b`** – **26.5%** *(Padrão da indústria Meta, baseline seguro)*
10. **`phi3.5:3.8b`** – **21.0%** *(Modelo ultra-compacto da Microsoft)*

---

## RANKING 2: RACIOCÍNIO CIENTÍFICO E LÓGICO DE NÍVEL AVANÇADO (GPQA Diamond)

Focado em matemática avançada, lógica pura, física e respostas de nível de pós-graduação.

1. **`deepseek-r1:32b`** – **62.1%** *(SOTA em raciocínio aberto entre modelos densos < 35B)*
2. **`deepseek-r1:14b`** – **59.1%** *(Performance incrível gastando apenas 9GB VRAM)*
3. **`deepseek-r1:7b`** – **49.1%** *(Supera a maioria dos modelos de 14B/70B sem raciocínio)*
4. **`qwen2.5:14b`** – **46.2%** *(Conhecimento geral amplo em português e inglês)*
5. **`gemma2:27b`** – **41.9%** *(Excelente baseline de conhecimento da linha Gemma)*
6. **`qwen2.5-coder:32b`** – **41.7%** *(Foco em código, mas com excelente lógica matemática)*
7. **`qwen2.5-coder:14b`** – **41.2%** *(Lógica estruturada de alta precisão)*
8. **`qwen2.5-coder:7b`** – **35.8%** *(Lógica rápida de 7B)*
9. **`llama3.1:8b`** – **30.4%** *(Benchmark padrão 8B)*
10. **`phi3.5:3.8b`** – **29.8%** *(Surpreendente para 3.8B de parâmetros)*

---

## RECOMENDAÇÃO PRÁTICA DE SETUP BENCHMARK (RX 9060 16GB)

1. **Para Desenvolvimento & Agentes de Código no VS Code:**
   * Use o **`qwen2.5-coder:14b`** (ocupa apenas 9GB, sobram 7GB de VRAM livres para contexto gigante de 32k tokens e respostas a ~60 t/s).

2. **Para Resolução de Problemas Lógicos Complexos & Raciocínio (Reasoning):**
   * Use o **`deepseek-r1:14b`** ou **`deepseek-r1:32b`**.

3. **Para Testes Instantâneos de Latência e Resposta:**
   * Use o **`qwen2.5:0.5b`** ou **`llama3.2:1b`** (>150 tok/s).

---

# MODELOS ULTRA-LEVES E DE ALTÍSSIMA VELOCIDADE (< 4B PARAMETROS)

Para tarefas diárias de **conversação rápida, resumo de textos e respostas instantâneas** a dúvidas cotidianas (sem foco em programação avançada), os modelos sub-4B oferecem vazão de mais de **100 a 180+ tokens por segundo** na GPU AMD Radeon RX 9060.

### TABELA COMPARATIVA DE MODELOS LEVES (< 4B)

| Modelo Ollama | Parâmetros | VRAM Alocada | MMLU (Conhecimento Geral) | GSM8K (Matemática Básica) | IFEval (Seguimento de Instrução) | Velocidade Estimada (RX 9060) | Foco Principal |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`llama3.2:3b`** | 3.2B | ~2.0 GB | **63.4%** | **77.7%** | **77.4%** | **~120 - 150 t/s** | Padrão ouro Meta para chat rápido e resumos |
| **`qwen2.5:3b`** | 3.0B | ~1.9 GB | **64.4%** | **86.7%** | **58.2%** | **~130 - 160 t/s** | Raciocínio matemático e português impecável |
| **`gemma2:2b`** | 2.6B | ~1.6 GB | **51.3%** | **23.9%** | **45.0%** | **~140 - 180 t/s** | Campeão de velocidade bruta do Google |
| **`qwen2.5:1.5b`** | 1.5B | ~1.0 GB | **60.5%** | **78.2%** | **52.1%** | **~150 - 180 t/s** | Modelo de 1.5B mais inteligente do mercado |
| **`llama3.2:1b`** | 1.2B | ~1.3 GB | **49.3%** | **44.4%** | **59.2%** | **~160 - 200 t/s** | Ultra-compacto da Meta para baixíssima latência |

---

# MODELOS SOTA FRONTIER 2026: BENCHMARKS & COMPATIBILIDADE

Avaliação dos modelos de fronteira mais recentes da indústria (linha Qwen 3.x, MoE e Kimi) e sua viabilidade no hardware do usuário (**16GB VRAM RX 9060 + 32GB RAM + Ryzen 7 5800X3D**):

### TABELA COMPARATIVA DE MODELOS FRONTIER (SWE-BENCH PRO & VERIFIED)

| Modelo | Arquitetura | SWE-bench Verified | SWE-bench Pro | Espaço no SSD (Q4_K_M) | VRAM / RAM Necessária | Viabilidade no Setup Local |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Qwen3.6-27B** | Denso 27B | **77.2%** | **53.5%** | **~15.5 GB** | **~15.2 GB VRAM** | ✅ **100% Compatível (VRAM)** |
| **Kimi K2.6** | 1T MoE (32B Act) | **80.2%** | **58.6%** | ~200+ GB | >128 GB VRAM/RAM | ❌ Requer Servidor Enterprise |
| **Qwen3-Coder-Next** | 80B MoE (3B Act) | **~70.0%** | **~48.0%** | **~21.0 GB** | 15GB VRAM + 5GB RAM | ✅ **Compatível (VRAM + Offload)** |
| **Qwen2.5-Coder-32B** | Denso 32.5B | **55.4%** | **38.2%** | **~18.5 GB** | **~15.5 GB VRAM** | ✅ **100% Compatível (VRAM)** |

---

# GUIA PRÁTICO: QUAL MODELO USAR E QUANDO (MATRIZ DE DECISÃO PARA 16GB VRAM)

Para balancear perfeitamente **desempenho em tokens por segundo (t/s)**, **uso de VRAM** e **inteligência**, utilize a seguinte matriz de escolha no seu dia a dia:

### 1. ⚡ Chat Rápido, Resumos de Texto & Dúvidas Cotidianas (Modo Ultra-Velocidade)
* **Modelo Indicado:** `qwen2.5:1.5b` ou `llama3.2:3b`
* **Vazão:** **~130 a 150+ tokens/segundo**
* **VRAM Usada:** apenas ~1.0 GB a 2.0 GB.
* **Quando usar:** Para conversas informais, resumir artigos de notícias, tirar dúvidas rápidas de sintaxe sem carregar modelos pesados.

### 2. 💻 Desenvolvimento no VS Code, Refatoração & Autocompletar (Modo Engenheiro de Código)
* **Modelo Indicado:** `qwen2.5-coder:14b` ou `qwen3.6-27b`
* **Vazão:** **~45 a 65 tokens/segundo**
* **VRAM Usada:** ~9.0 GB a 15.2 GB.
* **Quando usar:** Para agir como assistente de código no VS Code via extensões (como Continue.dev/Aider), gerar funções complexas em Rust/Python/Go e refatorar arquivos inteiros.

### 3. 🧠 Raciocínio Lógico Profundo & Resolução de Issues Complexas (Modo Reasoning / Chain of Thought)
* **Modelo Indicado:** `deepseek-r1:14b` ou `deepseek-r1:32b`
* **Vazão:** **~30 a 60 tokens/segundo**
* **VRAM Usada:** ~9.0 GB a 15.2 GB.
* **Quando usar:** Para depurar bugs difíceis de arquitetura, resolver exercícios matemáticos ou quando o modelo precisa "pensar" antes de responder (etapa `<think>`).

# 📐 006_LLM_INT_MACHINE Architectural SVG Workflows & Diagrams

This directory contains the visual system blueprints for the **006 Next-Generation Agentic Coding Harness**.

---

## 🗺️ Index of Architectural Workflow Diagrams

| Diagram File | Title | Core Concepts & Systems Illustrated |
|---|---|---|
| [`01_main_agentic_harness_architecture.svg`](./01_main_agentic_harness_architecture.svg) | **Main Agentic Harness Architecture** | End-to-end cognitive lifecycle: Static analysis, Tree-Sitter PageRank, SBFL Ochiai, L1–L5 Radix prefix compiler, tool dispatcher, AST syntax gate, mutation falsifier, and ground-truth oracle. |
| [`02_inner_vs_outer_loop_engineering.svg`](./02_inner_vs_outer_loop_engineering.svg) | **Inner vs. Outer Loop Engineering** | Separation of concerns: Outer deliberative System 2 loop (Supervisor POMDP planning, Claude Code subagents, MCTS tree search) vs. Inner high-throughput System 1 loop (0.2ms AST pre-flight, patch apply, pytest runner, mutation testing). |
| [`03_preset_workflows_comparison.svg`](./03_preset_workflows_comparison.svg) | **Parametric Presets Comparison** | Visual comparison of the 7 harness presets (`v1.0 Baseline ReAct`, `v1.1 Vanguard Core`, `v1.2 SOTA Full`, `v2.0 SBFL Graph`, `v2.1 MCTS Speculative`, `v2.2 Mutation Robust`, `v2.3 Compound Full`), with live empirical benchmarks and SWE-bench score projections. |
| [`04_input_output_algorithms_pipeline.svg`](./04_input_output_algorithms_pipeline.svg) | **Input & Output Algorithms Pipeline** | Exhaustive transformation flow: 5 deterministic algorithms applied to inputs (PageRank graph, SBFL Ochiai, dynamic tool pruning, Radix prefix compiler, subagent context compaction) vs. 5 algorithms applied to outputs (AST pre-flight 0.2ms, gated reproducer, head/tail log paging, mutation falsifier, signed SHA-256 receipt). |
| [`05_hierarchical_router_and_subagents.svg`](./05_hierarchical_router_and_subagents.svg) | **Hierarchical Router & Subagents** | Dual-tier model routing (Supervisor / Planner vs. Fast Worker), Claude Code-style context isolation sandboxes (Scout, QA, Solver), and 100% Air-Gapped Local Ollama vs. Hybrid Cloud/Local execution topologies. |

---

*Generated for Vanguard / LIM Autonomous Coding Substrate.*

# 2. AI-Powered Reverse Engineering Playbook (Step-by-Step)

  Here is how you use AI subagents to systematically break down their repository and map it directly to Vanguard in 4 steps:

    flowchart TD
        A["1. Directory & Entry Map"] --> B["2. Protocol & Data Tracing"]
        B --> C["3. Module-by-Module Audit"]
        C --> D["4. DeepSeek vs Vanguard Matrix"]

  #### Step 1: Directory Tree & Entry Point Mapping

  Run a tree scan of their repository and feed it to an AI subagent:

    # Capture full clean tree structure
    find . -maxdepth 3 -not -path '*/.*'

  • AI Prompt: "Categorize this folder tree into UI, API/Protocol, Execution Core, Tooling, and State Storage."

  #### Step 2: Core Data Structure & Entry Point Tracing

  Locate their CLI/API entry point (e.g., cli.py, main.py, app.py) and their core data shapes.

  • Find their equivalent of Vanguard's HarnessManifest, EffectRequest, and EventEnvelope.
  • AI Prompt: "Trace execution starting from entrypoint X. List all data structures passed between the agent loop and tools."

  #### Step 3: Module-by-Module AI Survey

  Spawn an AI research agent to analyze each subsystem folder and generate a 1-page summary:

  • AI Prompt: "Analyze package /path/to/module. Detail: (1) Its single responsibility, (2) Inputs/Outputs, (3) Key algorithms or prompt techniques used,
  (4) Dependencies."

  #### Step 4: Create the "DeepSeek vs. Vanguard" Comparative Matrix

  Synthesize all module summaries into a formal review document in your repo (e.g. docs/reviews/todo/deepseek_forensic_review.md):

   DeepSeek Component          │ Vanguard Equivalent                    │ Action (Keep, Steal, or Replace)
  ─────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────
   DeepSeek UI / Frontend      │ vanguard-gui / Client                  │ KEEP & PLUG: Use their UI, wire to Vanguard WebSocket.
   DeepSeek Agent Loop         │ Vanguard IPlanner + layer0/scheduler   │ STEAL IDEAS: Extract prompt strategies into Vanguard IPlanner plugin.
   DeepSeek Tools              │ Vanguard IToolkit (packs/code-default) │ STEAL TOOLS: Port their tree-sitter or search tools into Vanguard plugins.
   DeepSeek Backend & State    │ Vanguard layer0/ Microkernel           │ REPLACE: Replace their un-sandboxed backend with Vanguard's attenuation kernel.
  ──────
  ### Next Action:

  Provide the GitHub link or path to their repository, and we can launch an AI research pass right now to extract their file tree and start building your
  DeepSeek Forensic Matrix!
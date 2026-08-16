# Lane A (Dev A) Specification: Manifest Engine & Pure-Data Reconstruction Packs

**Target Branch:** `sprints7-8/integration`  
**Assigned Developer:** Dev A (Lane A Lead)  
**Parent Directive:** [`docs/agile/sprint7_8/sprint7_8_directive_and_playbook.md`](file:///home/rocha/Coding/Aether-D-System/docs/agile/sprint7_8/sprint7_8_directive_and_playbook.md)  
**Target Code Area:** `vanguard/packages/agency/manifests/`  

---

## 1. Objective & Technical Invariants

Build the declarative **Manifest Loader Engine** that loads pure-data agentic harness configurations and translates tool naming conventions without modifying microkernel Python code.

### Invariants
1. **Zero Kernel Mutation:** No changes allowed in `vanguard/packages/kernel/` or `agency/episode/`.
2. **Pure Data Declarations:** Manifest packs are self-contained folders containing `manifest.json`, `aliases.json`, and optional prompt files.
3. **Decoupled Verb Aliasing:** Model-specific tool verbs (`read_file`, `write_file`, `bash`) map to canonical kernel verbs (`fs.read`, `fs.write`, `proc.exec`) via `aliases.json`.

---

## 2. Manifest Pack Directory Structure

Every manifest pack inside `vanguard/packages/agency/manifests/<pack-name>/` must follow this layout:

```
vanguard/packages/agency/manifests/
├── loader.py                     # Dynamic manifest loader and validation
├── discovery.py                  # AGENTS.md / CLAUDE.md workspace parser
├── vg-code-default/
│   ├── manifest.json             # Core manifest definition
│   └── aliases.json              # Canonical to custom verb mappings
├── vg-code-claude-shaped/
│   ├── manifest.json             # Claude-Code shape reconstruction
│   └── aliases.json              # "read" -> "fs.read", "write" -> "fs.write", "bash" -> "proc.exec"
├── vg-code-opencode-shaped/
│   ├── manifest.json             # OpenCode shape reconstruction
│   └── aliases.json              # "view_file" -> "fs.read", "edit_file" -> "patch.apply"
└── vg-code-swe-mini/
    ├── manifest.json             # SWE-bench mini shape reconstruction
    └── aliases.json              # Standard SWE tool mappings
```

---

## 3. Tasks Breakdown for Dev A

### Task A.1 (Sprint 7): Manifest Loader & Aliases Engine (`loader.py`)
- Load manifest directories dynamically.
- Parse `manifest.json` schema: `name`, `version`, `allowed_capabilities`, `system_prompt_template`, `context_layers`.
- Load `aliases.json` and provide bidirectional verb translation:
  - `to_canonical(tool_name)` $\rightarrow$ `canonical_verb` (e.g. `read_file` $\rightarrow$ `fs.read`)
  - `to_wire(canonical_verb)` $\rightarrow$ `model_tool_name` (e.g. `fs.read` $\rightarrow$ `read_file`)

### Task A.2 (Sprint 7): Workspace Discovery Engine (`discovery.py`)
- Automatically scan the workspace root for instruction markdown files: `AGENTS.md`, `CLAUDE.md`, or `PROJECT.md`.
- Ingest discovered guidelines into L3/L4 context layers as read-only observation events without breaking prefix stability.

### Task A.3 (Sprint 8): Reconstruction Packs Construction
1. **`vg-code-claude-shaped`:** Emulates Claude Code tool interfaces (`Read`, `Edit`, `Write`, `Bash`, `Glob`, `Grep`).
2. **`vg-code-opencode-shaped`:** Emulates OpenCode tool interfaces (`view_file`, `edit_file`, `run_command`, `list_dir`, `grep_file`).
3. **`vg-code-swe-mini`:** Emulates standard SWE benchmark harness interfaces.

---

## 4. Acceptance Criteria & Quality Gate

- [ ] All manifest packs load and validate against `schemas/v4/` schemas.
- [ ] Tool verb translation is pure, bidirectional, and deterministic.
- [ ] Unit tests pass: `python3 -m unittest test/agency/test_manifest_loader.py`.
- [ ] `tools/check_boundaries.py` reports ZERO violations in `vanguard/packages/kernel/`.

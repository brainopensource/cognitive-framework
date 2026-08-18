# v0.4.3 — Harvest tutorial: OpenCode / Claude Code atoms on Vanguard

**Status:** working note for the product slice (one coding CLI). Not a second roadmap.
**Audit 2026-08-17 (first headless coding CLI = `lab_driver`, not TUI):** `[DONE]` in tree on the real episode path. `[TODO]` still required for that cut. `[LATER]` not this CLI.

**Good to have (coded, not the last delivery list):** `AutonomousGrant` (`runtime/autonomous_grant.py`) — signed workspace/verb/command/expiry/budget, better than a blanket approve. Explicit empty-workspace IndexPort map. `coding_progress` fingerprints as honest stop. Bind `format_skill_index` into the compiler prefix.

**Boards stay:** `docs/scrum/roadmap_backend.md`, `docs/scrum/roadmap_frontend.md`.
**Normative:** `docs/main_v4/`. Pack authoring: `docs/scrum/development_guides/02_manifest_and_pack_authoring.md`.
**Harvest ruling (010):** do not rewrite Vanguard; do not import a competitor catalogue; evolve in place.

This file answers: *how do we reuse OpenCode, Claude Code, mini-SWE-agent, Aider, Codex, Pi, … without rebuilding their loops, and without throwing away the kernel?*

---

## 1. The middle ground

Every 2026 coding CLI is the same loop with a different skin: **model proposes → tools run → context shrinks → repeat**. Vanguard already owns the loop (`observe → propose → authorize → effect → receipt → evaluate`). Competitors own **good atoms** (how a file is shown, how a patch is named, how a prompt stays short, how a permission is asked).

| Take (atom) | Leave (skin / second brain) |
|---|---|
| Tool JSON, aliases, prompt skeletons, ACI pagination | Their `while True` agent loop |
| Compaction *heuristic* (what to drop) | Their in-process memory mutation of the system prefix |
| Permission copy, allowlists, plan-mode UX | Policy-only “isolation” with no sandbox |
| LSP / lint / grep output shape | Evaluator-in-the-loop (LLM grades itself) |
| Repo-map / symbol index *as observations* | Workflow DAGs, playbook engines, MCP-as-authority |
| Session JSONL / resume ideas | Shadow-git as the source of truth (we have a ledger) |

**Rule.** The model is the brain. The pack is the DNA (prompt, tools, budget, routing, approval, compaction). The kernel is the immune system. A competitor file is a *reference*, never a vendored runtime.

If a harvest needs `kernel/` or `agency/episode/engine.py` changed, **stop** and write the finding (`C-01` falsified, or an ADR). That is a result, not a shortcut.

---

## 2. Recipe — clone a feature in four steps

Do this once per feature. Do not “port OpenCode.”

### Step A — Read public docs, not their `src/`

Preferred sources (confirmed in the Phase-2 review):

| Product | Steal from | Ignore |
|---|---|---|
| [OpenCode](https://opencode.ai/) | Provider-agnostic client, `AGENTS.md`, plugins-as-config, TUI/server split, permission prompts | Assumed AST patcher / “deep sandbox” unless you can point at a contract |
| [Claude Code / Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk) | `Read`/`Grep`/`Edit`/`Bash` names, `max_turns`, hooks, subagent *isolation*, compact-on-overflow | Anthropic lock-in, 28k-token cold start |
| [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) | 100-line viewer, succinct grep, lint-on-edit, empty-shell ack | The old SWE-agent scaffold |
| [Aider](https://aider.chat/2023/10/22/repomap.html) | Tree-sitter repo map as an **index observation** | Mixing Aider Polyglot with SWE-bench |
| [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) | OS sandbox **and** approval policy as two knobs | Cloud handoff as a v0.4.3 requirement |
| [Pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) | Four primitives, tiny system prompt, extensions outside the core | Importing their loop; our ledger already is the session |
| Reasonix (internal harvest in `docs/reviews/doing/010_…`) | Skills **index** in a frozen prefix; attribute cache misses | Rewriting the compiler in Go |
| Cline / Kilo | Approval modes, checkpoint *UX* | Shadow-git as authority; YOLO as a feature |

Write `REFERENCE.md` in the pack: URL, what was read, **what was not copied**. That is the license/hygiene line.

### Step B — Name the Vanguard slot

Every atom lands in **exactly one** of:

1. **Pack gene** — `vanguard/packages/agency/manifests/<id>/` (`system-prompt.txt`, `*-tool.json`, `aliases.json`, `context-policy.json`, `routing-policy.json`, `approval-policy.json`, `budget-policy.json`).
2. **Adapter behaviour** — `vanguard/packages/adapters/**` (how `fs.read` paginates, how `proc.exec` acks empty, lint on patch). Same verb, better receipt.
3. **Port + fake** — `ports/` + adapter (e.g. `IndexPort` for an Aider-style map). Manifest row binds it. No new engine.
4. **Client only** — `vanguard/clients/cli/**` (Ink TUI, `vg run --headless`, approve/resume). Must not fork VG-04.

If it does not fit (1)–(4), it is not a v0.4.3 harvest. It is V5, MCP (`ADR-0066`), or rejected (`REJ-01` DAG, `A-05` self-grade).

### Step C — Encode, freeze, prove a behavioural diff

```text
1. Copy the competitor idea into pack files (or adapter receipt text).
2. python3 -m unittest test.agency.test_reconstructions -v
   A mutated gene MUST change an observable (prompt byte, routing choice, compact outcome, approval).
   If the digest changes and behaviour does not, the component is decorative (FT-10) — fail.
3. Run the live path with MOCK first:
   vg run --headless --manifest vg-code-opencode-shaped --prompt "…" --repo <workspace>
4. Only then Ollama / OpenRouter free. Never band=top until spend (S9-J-03).
```

Unknown tool names **fail at composition**, not at first use. Aliases are pack-local:

```json
{ "Read": "fs.read", "Grep": "fs.search", "Edit": "patch.apply", "Bash": "proc.exec" }
```

The model sees `Read`. The kernel sees `fs.read`. Naming is not authority.

### Step D — Keep their loop out

Do **not** `git submodule` OpenCode and call it from `EpisodeEngine`.
Do **not** add `todo` / `terminal` / `subagent` / `web` packages in the core.
Do **not** apply the attenuated-child emit-guard to depth-0 (that deletes F-09 denials).
Do **not** implement MCP until `ADR-0066`.
Do **not** revive a workflow DAG.

Subagents = `ProposalKind.SPAWN` + child `Scope` from `args["scope"]` (fail-closed). That is OpenCode/Claude “Task” without a second engine.

---

## 3. Worked example — “OpenCode `view_file`”

OpenCode (and Claude) train the model on a **named file viewer**, not raw `cat`.

| Their atom | Vanguard slot | Already? |
|---|---|---|
| Name `view_file` / `Read` | `aliases.json` | Yes (`vg-code-opencode-shaped`, `vg-code-claude-shaped`) |
| Default 100 lines + offset | adapter `fs.read` (ACI-1, S8-B-06) | Yes |
| “Inspect before edit” | `system-prompt.txt` | Yes (one-liner; thicken from public Claude/OpenCode *style*, not their blobs) |
| LSP hover | new observation verb **or** lint receipt | Lint-on-patch is S8-B-09; LSP is a later `IndexPort` / adapter, not a loop |

You never clone their viewer source. You clone the **contract**: paginated read + alias + prompt line.

Same pattern for grep (ACI-2), empty bash (ACI-3), lint-on-edit (ACI-4), `AGENTS.md` first (ACI-5), `maxTurns` from budget (ACI-6).

---

## 4. Backend we already have (OpenCode-class, no TUI claim) — `[DONE]` unless noted

These are **in the runtime / packs / adapters**, not “we shipped OpenCode.”

| OpenCode / Claude surface | Vanguard form | Where |
|---|---|---|
| Agent loop | Episode engine | `agency/episode/engine.py` |
| Tools: read / search / patch / bash | `fs.read`, `fs.search`, `patch.apply`, `proc.exec` | pack tools + capabilities |
| Tool name skins | aliases | `aliases.json` |
| System prompt as config | `system-prompt.txt` | per pack |
| `AGENTS.md` / `CLAUDE.md` | workspace discovery → L3 | `agency/manifests/discovery.py` |
| Permissions | `approval_policy` + kernel authorize — `[DONE]` policy; `[TODO]` operator signer on CLI; `[LATER]` TUI `vg approve` | S8-B-04 |
| Sandbox | rootless bubblewrap adapter — `[DONE]` | `adapters/sandbox/` |
| Provider-agnostic model | `ModelPort` (OpenRouter, Ollama, OpenAI, DeepSeek, MOCK) — `[DONE]` adapters; `[TODO]` live writes | `adapters/models/` |
| Subagents | fail-closed `spawn` + attenuation — `[DONE]` engine; `[TODO]` not in coding pack | S8-B-01 (`8f5f16d`) |
| Compaction | `CompactionStrategy` registry + `structured_consolidate` / `deadEnds` | S8-B-02, S10-B-03 |
| Re-ground / brief | immutable brief; `regroundPolicy` as granted effect | VG-03; S10-B-04 |
| Turn budget | `maxTurns` from `budget_policy` | S8-B-10 |
| Model routing | `ModelRouter` from `routing_policy` | S8-B-03 |
| Session resume | ledger suspend/resume — `[DONE]` ledger; `[TODO]` operator `--resume` on `lab_driver` | S8-A-02 |
| Events / receipts | kernel ledger, `vg trace` / `vg why` | CLI + runtime |
| ACI quality | paginated read, succinct search, empty exec ack, lint receipt | S8-B-06…B-09 |
| Packs as plugins | `compose()` freeze; reconstructions differ on ≥3 DNA dims | S9-B-01 |
| Headless CLI | `[DONE]` shim → `lab_driver` (`python3 lab/run.py` or `-m vanguard.packages.runtime.lab_driver`). `[TODO]` `vg run --headless` is still the TUI/daemon path, not this cut. | `lab/run.py` + `runtime/lab_driver.py` |
| Second domain (not coding) | TableWorld | S10-B-01 (proves the compiler, not the coding CLI) — `[DONE]` as proof, `[LATER]` for coding CLI |

**Honest gaps vs a daily OpenCode:** `[TODO]` live LLM dogfood / Q2; `[DONE]` `lab/run.py` is a stdlib shim (no longer a fabricating stub); `[LATER]` daemon/TUI, LSP, MCP, playbooks. `[DONE]` session projector `tools/export_coding_session.py`. `[TODO]` `format_skill_index` exists but is **not bound** in `agency/context/compiler.py`. `[TODO]` `--in-place` and `--approve-writes` not on `lab_driver` argparse (`approve_writes` exists only as a Python kwarg). `[TODO]` live greenfield still often 0 verbs / `multi_action_proposal`.

---

## 5. Features to add for a *minimal* OpenCode-on-Vanguard

Order is the point. Each row is one harvest cycle (§2). Stop when `DOGFOOD-01..03` survive without a hand-patch.

### P0 — make the existing CLI actually code

| ID | Status | Feature | Harvest | Land in |
|---|---|---|---|---|
| P0-1 | `[DONE]` | One **product-default** pack | OpenCode + Claude public prompts (style only); Pi’s *length* (keep cold start tiny) | `vg-code-default` is `product-default` in `registry.json` |
| P0-2 | `[DONE]` via `lab_driver --model ollama\|openrouter`; `[TODO]` live verb rate | Live `ModelPort` | OpenCode provider list; our adapters already exist | env: Ollama or OpenRouter **free**; MOCK stays the test brain |
| P0-3 | `[DONE]` isolate-copy; `[TODO]` `--in-place` on a WSL checkout | Sandbox + workspace root on real repos | Codex: sandbox knob ≠ approval knob | `adapters/sandbox/rootless.py` + capability selectors |
| P0-4 | `[LATER]` TUI out of this cut; `[TODO]` CLI `--approve-writes` / `AutonomousGrant` | Interactive approve | OpenCode / Cline permission copy | kernel still decides; lab signer is labelled `auto_approved_writes` |
| P0-5 | `[TODO]` Q2; MOCK ≠ live | Execute `DOGFOOD-01..03` live | ourselves | protocol already at `docs/scrum/sprints/sprint09/evidence/s9-j-01-dogfood-protocol.md` |

### P1 — atoms that move SWE scores (adapter / pack, not engine)

| ID | Status | Feature | Harvest | Land in |
|---|---|---|---|---|
| P1-1 | `[DONE]` | Thicken tool schemas (offset, glob, uniqueness) | mini-SWE-agent ACI + Claude tool JSON *shapes* | `*-tool.json` + adapters; **same verbs** |
| P1-2 | `[TODO]` only if live models dump whole files | `write` vs `edit` if models dump whole files | Pi four primitives; still `patch.apply` or a second capability row | pack capability + adapter; no new kernel verb unless forced |
| P1-3 | `[DONE]` port + `lab_driver` bind when pack has `index_component`; `[TODO]` explicit empty-workspace map text | Repo map / symbols as observations | Aider repo map; sagiha `find_symbols` | `IndexPort` (S10-A-03) bound in the manifest |
| P1-4 | `[DONE]` pack genes + `format_skill_index`; `[TODO]` bind into compiler prefix | Skills index in the frozen prefix | Reasonix ≤4k names+descriptions | `skill` artifacts (kind already in `kinds.json`); bodies via `fs.read` |
| P1-5 | `[DONE]` | Bind or delete `proc.test` | our own orphan | S10-A-02 deleted; tests = allowlisted `proc.exec` |
| P1-6 | `[DONE]` | Domain strings out of `invocation.py` | C-01 | S10-A-01 — competitor names live in aliases, not Python |

### P2 — memory and loop *control* (already designed, not productized)

| ID | Status | Feature | Harvest | Land in |
|---|---|---|---|---|
| P2-1 | `[DONE]` | Short-term = episode dialogue + receipts | Pi JSONL DAG *idea*; our ledger is the store | do not add a second session DB |
| P2-2 | `[DONE]` | Long-term = files (`AGENTS.md`, notes) the model `fs.read`s | OpenCode project memory | workspace files + discovery; never mutate L1–L3 mid-turn |
| P2-3 | `[DONE]` `brief_exempt` | Chat → brief | VG-03 immutable brief, compaction-exempt | prompt compiler; keep the brief out of compact |
| P2-4 | `[DONE]` `deadEnds` / session_log; `[TODO]` wire `coding_progress` fingerprints into `lab_driver` stop | Retries / stuck detection | Claude compact-on-overflow; our `deadEnds` | context policy gene, not a new loop |
| P2-5 | `[DONE]` engine `spawn` + ADR-0067; `[TODO]` expose from coding pack | Subagent for “explore in isolation” | Claude Task / OpenCode subagent | spawn + narrowed `Scope`; prove with real Kernel tests, not mocks |

### P3 — explicitly later (do not sneak into v0.4.3) — `[LATER]`

MCP, playbooks / operator registry, G_C promotion, browser, parallel TUI sessions, LSP-as-IDE, paid model lifts. Kernel sealed-flag (`ADR-0067`) is `[DONE]` — do not relitigate. Playbook rigidity dial (`advisory` → `guided` → `strict`) stays `[LATER]` v0.5.

---

## 6. How to use a cloned repo as a reference (hygiene)

```text
# sibling directory — not inside Aether-D-System
git clone --depth 1 https://github.com/sst/opencode   ../_refs/opencode
git clone --depth 1 https://github.com/SWE-agent/mini-swe-agent ../_refs/mini-swe-agent
```

Then **read** `docs/`, tool schemas, and prompt files. Copy **strings and shapes** into pack JSON/txt. Do not copy TypeScript/Go agent cores. Do not commit `../_refs/` here.

For each harvested atom, the PR body cites: competitor doc URL, Vanguard slot (pack/adapter/port/client), test that proves a behavioural diff, `REQ-` / kit row if any.

---

## 7. The one command that means it works

`[TODO]` operator path (in-place + labelled writes). `[DONE]` module and shim exist. Real command for this cut:

```bash
python3 -m vanguard.packages.runtime.lab_driver \
  --pack vg-code-default \
  --task-dir /home/rocha/Coding/YOUR_REPO \
  --model ollama --model-name llama3.2:3b \
  --interactive \
  --jsonl-out /tmp/vg-run.jsonl
```

Stale `vg run --headless --manifest …` is `[LATER]` / TUI. When the command above returns a ledger of patches + passing `proc.exec` tests **on the WSL tree**, the framework is a coding harness. Measure it with:

```bash
python3 tools/export_coding_session.py --jsonl path/to/episode.jsonl
```

A Python API + static HTML greenfield is the same command with a bigger prompt — not a new architecture. PO checklist: `docs/scrum/sprints/wave11/PO_ACCEPTANCE.md`.

---

## 8. Stop conditions

- Second dispatch path or competitor loop inside `EpisodeEngine`.
- Decorative pack fields (digest moves, behaviour does not).
- Mock kernel that implements `action ∈ scope` in `dispatch` (that proved a mock once; never again).
- LLM-as-judge of the same artifact (`A-05`).
- History rewrite for `S7-J-04` before the OpenRouter key is rotated.

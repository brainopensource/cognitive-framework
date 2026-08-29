---
id: product.frontend.tui
class: product
authority: proposal
canonical_for:
  - aether-tui-product-requirements
  - terminal-cockpit-ux-and-streaming
status: proposed
owner: product-architecture
version: "0.1.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/PRD_AETHER_TUI.md
subordinate_to:
  - product.frontend.platform
  - ../../SPEC.md
---

# Product Requirements Document: AETHER TUI (Terminal Cockpit)

## 1. Executive Summary & Product Thesis

**AETHER TUI** is the interactive, keyboard-driven terminal cockpit for the AETHER substrate. It is designed for developers, systems researchers, and power users who demand ultra-fast, conversation-first interaction inside terminal emulators, SSH sessions, and developer workstations.

### 1.1 Core Thesis

> **The TUI is an ultra-fast, conversational cockpit: it delivers real-time token streaming, progressive activity disclosure, and in-terminal cryptographic approvals with sub-16ms reactive cell updates.**

By combining **SolidJS** and **OpenTUI**, the TUI eliminates the performance bottlenecks of virtual DOM reconcilers on terminal buffers, providing rock-solid 60 fps rendering during high-volume token streams.

---

## 2. AS_BUILT vs. TARGET State Assessment

| Dimension | AS_BUILT (Repository Evidence) | TARGET (Electroweak Baseline) | Strategic Gap & Action |
|---|---|---|---|
| **Terminal Rendering Engine** | React 18 + Ink (`ink@^5.1.0`), re-rendering full component trees and incurring high CPU usage during streaming. | **OpenTUI** + **SolidJS** on **Bun**, rendering via fine-grained reactive terminal cell buffers. | Replace Ink with OpenTUI + SolidJS; eliminate full-tree VDOM diffing. |
| **Interactive Approvals** | Minimal prompt in `ApprovalInterceptor.tsx` with basic text diff rendering. | Dedicated Approval Deck with interactive unified diff browser and one-key Ed25519 signing. | Implement dedicated terminal diff viewer and secure cryptographic signing flows. |
| **Progressive Disclosure** | Flat transcript window with limited folding and no collapsible tool activity cards. | Progressive disclosure hierarchy: compact folded summaries by default, expandable to full diffs/spans. | Build collapsible card primitives (`ui-tui`) for file changes, tool runs, and test outputs. |
| **Keyboard Grammar** | Basic readline input with limited navigation shortcuts. | Comprehensive Vim/standard keybinding grammar (modal navigation, transcript scrolling, command palette). | Implement modal focus system (`FocusManager`) and customizable keybinding maps. |

---

## 3. Users & Jobs-to-be-Done

- **Software Engineers & Terminal Natives**: Drive autonomous coding sessions, review proposed file diffs, approve system mutations, and trigger verification runs without switching away from tmux/neovim.
- **AI Systems Researchers**: Monitor multi-turn agent investigations, observe tool invocations, inspect live token/budget consumption, and detect execution bottlenecks in real time.

---

## 4. Visual Layout & Information Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ AETHER │ agent:coding-v2 │ repo:cognitive-framework │ model:claude-3-5-sonnet │ status:RUNNING│ ◄ Header Bar
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│ [User] 20:14:02                                                                              │
│ Fix the governor lease leak in kernel dispatch sequence (K-06).                              │
│                                                                                              │
│ [AETHER] 20:14:05                                                                            │
│ Investigating kernel dispatch pipeline and governor acquisition invariants...                │
│                                                                                              │
│ ▸ Read 4 files (dispatch.py, governor.py, test_dispatch.py, types.py)                        │ ◄ Folded Activity Card
│ ▾ Modified vanguard/packages/kernel/dispatch.py                                              │ ◄ Expanded Diff Card
│   @@ -315,5 +315,6 @@                                                                        │
│            outcome = adapter.execute(request)                                                │
│            settlement = self._governor.commit(lease, outcome.actual_cost)                    │
│   -        self._governor.release(lease)                                                     │
│   +    finally:                                                                              │
│   +        self._governor.release(lease)                                                     │
│                                                                                              │
│ ▸ Verified 42 unit tests (test_dispatch.py) · 100% pass [0.42s]                              │ ◄ Verification Badge
│                                                                                              │
│ Implemented guaranteed lease release in guarded block. Ready to apply patch.                 │
│                                                                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠ APPROVAL REQUIRED: Apply patch to dispatch.py (sha256:44a2...88f)                           │ ◄ Governance Deck
│ [y] Approve & Sign (Ed25519)   [d] View Full Diff   [n] Reject Action   [q] Cancel Run       │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ > Message AETHER... (Press '/' for commands, '?' for shortcuts)                              │ ◄ Message Composer
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ tokens: 3,420 (in: 2,850, out: 570) │ cost: $0.0142 │ seq: 84 │ latency: 48ms │ buf: 0 drop │ ◄ Status Footer
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Structural Regions

1. **Header Bar**: Displays active agent identity, repository path, model route, and live run status (`RUNNING`, `AWAITING_APPROVAL`, `SATISFIED`, `FAILED`).
2. **Conversation Transcript**: Virtualized, scrollable viewport displaying turn cards, streaming text, folded tool spans, and inline diffs.
3. **Governance Deck (Conditional)**: Appears automatically when `ApprovalRequested` is received, displaying the challenge, risk category, and action buttons.
4. **Message Composer**: Multi-line text input with slash-command autocompletion, history navigation, and prompt submission.
5. **Status Footer**: Real-time operational metrics: accumulated tokens, estimated cost, sequence cursor, stream health, and round-trip latency.

---

## 5. Navigation & Keyboard Grammar

The TUI supports an intuitive modal navigation model:

| Keybinding | Active Scope | Operation / Action |
|---|---|---|
| `Enter` | Composer | Submit draft prompt to active agent session. |
| `Shift+Enter` / `Alt+Enter`| Composer | Insert newline without submitting. |
| `Ctrl+C` | Global | Interrupt active turn / initiate graceful cancellation. |
| `Ctrl+D` / `Ctrl+Q` | Global | Exit TUI and disconnect client. |
| `Tab` / `Shift+Tab` | Navigation | Cycle active focus between Composer, Transcript, and Approval Deck. |
| `j` / `k` or `↑` / `↓` | Transcript Focus | Scroll conversation transcript line by line. |
| `Ctrl+U` / `Ctrl+D` | Transcript Focus | Half-page scroll up / down. |
| `Space` / `Enter` | Transcript Focus | Toggle expansion of selected folded card (diff, tool span). |
| `/` | Composer | Open command palette (switch agent, switch workflow, attach run). |
| `y` | Approval Deck | Cryptographically sign and submit `approved` decision. |
| `n` | Approval Deck | Submit `rejected` decision. |
| `d` | Approval Deck | Open interactive side-by-side terminal diff viewer. |
| `Esc` | Modal / Diff | Close diff viewer or command palette and return to Composer. |

---

## 6. Real-Time Streaming & Progressive Disclosure

### 6.1 Token Streaming Invariants

- **Incremental Token Updates**: Words and code tokens MUST stream directly into the active turn card without triggering re-layouts of historical messages.
- **Activity Folding**: High-volume tool events (file reads, grep scans, AST parses) MUST be grouped into single-line folded activity cards:
  - *Folded*: `▸ Read 8 files [0.14s]`
  - *Expanded*: Lists individual file paths, byte sizes, and read latencies.
- **Diff Presentation**: File patches MUST be syntax-highlighted using ANSI 24-bit TrueColor sequences with green additions, red deletions, and neutral context headers.

---

## 7. Cryptographic Approval Deck

When the runtime requests approval for an effect:

1. **Audio/Visual Alert**: The status bar pulses with the warning color, and an optional terminal bell (`\a`) is emitted if configured.
2. **Challenge Display**: The Governance Deck renders the action name, target path, and normalized patch diff.
3. **One-Key Signing**: Pressing `y` triggers the local `SignerPort`, signs the canonical RFC 8785 JSON bytes with the operator's Ed25519 key, and dispatches `ResolveApproval` to `RuntimeService`.

---

## 8. Non-Functional & Performance Budgets

- **First Frame Paint**: Cold binary launch to interactive shell $<40\text{ ms}$.
- **Keystroke Input Latency**: Keystroke to terminal cell buffer update $<12\text{ ms}$.
- **Streaming Frame Rate**: Solid 60 fps during continuous token streaming; zero terminal flickering.
- **Terminal Resize Latency**: Full layout reflow $<16\text{ ms}$ on `SIGWINCH`.
- **Memory Footprint**: Resident Set Size (RSS) $<45\text{ MB}$ during active sessions.

---

## 9. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Emulating full IDE features (file trees, LSP language servers, multi-window tiling).
- **NON-GOAL 2**: Rendering rich bitmap graphics or web-standard HTML elements in the terminal.
- **NON-GOAL 3**: Bypassing the public `RuntimeService` interface for local terminal-only shortcuts.

---

## 10. Deferred Documentation & Canonical References

- **Future Architecture Owner**: `docs/architecture/frontend/tui-opentui-architecture.md`
- **Future Reference Owner**: `docs/reference/frontend/tui-keybindings.md`
- **Future Decisions Owner**: `docs/decisions/frontend/0109-opentui-solid-selection.md`
- **Future Execution Owner**: `docs/execution/frontend/tui-backlog.md`

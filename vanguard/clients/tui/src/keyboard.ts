import type { KeyEvent } from "./terminal/input.js";
import type { TuiStore } from "./store.js";
import type { RuntimeClient } from "@aether/client";
import { filterCommandsByQuery, splitCommandQuery } from "@aether/tui-core";

export class KeyboardManager {
  constructor(
    private readonly store: TuiStore,
    private readonly client?: RuntimeClient,
    private readonly onExit?: () => void
  ) {}

  private setModalIndex(index: number): void {
    this.store.update((s) => ({ ...s, modalSelectedIndex: index }));
  }

  public handleKey(key: KeyEvent): void {
    const state = this.store.get();

    // Global: Ctrl+C -> cancel active run or exit
    if (key.ctrl && key.name === "c") {
      if (state.runId && this.client) {
        this.client.requestCancel(state.runId, { reason: "User pressed Ctrl+C" });
        this.store.update((s) => ({ ...s, statusMessage: "Cancellation requested..." }));
      } else if (this.onExit) {
        this.onExit();
      }
      return;
    }

    // Global: Ctrl+D -> exit
    if (key.ctrl && key.name === "d") {
      if (this.onExit) this.onExit();
      return;
    }

    // Modal Active Handling
    if (state.activeModal !== "none") {
      this.handleModalKey(key);
      return;
    }

    // Tab / Shift+Tab Focus Cycling
    if (key.name === "tab") {
      if (key.shift) {
        if (state.focus === "composer") {
          this.store.setFocus(state.pendingApproval ? "approval" : "transcript");
        } else if (state.focus === "approval") {
          this.store.setFocus("transcript");
        } else {
          this.store.setFocus("composer");
        }
      } else {
        if (state.focus === "composer") {
          this.store.setFocus("transcript");
        } else if (state.focus === "transcript") {
          this.store.setFocus(state.pendingApproval ? "approval" : "composer");
        } else {
          this.store.setFocus("composer");
        }
      }
      return;
    }

    // Dispatch to focused region
    if (state.focus === "composer") {
      this.handleComposerKey(key);
    } else if (state.focus === "transcript") {
      this.handleTranscriptKey(key);
    } else if (state.focus === "approval") {
      this.handleApprovalKey(key);
    }
  }

  private handleComposerKey(key: KeyEvent): void {
    const state = this.store.get();

    // Paste event
    if (key.isPaste && key.pasteText) {
      const text = state.composerText;
      const cur = state.composerCursor;
      const next = text.slice(0, cur) + key.pasteText + text.slice(cur);
      this.store.setComposerText(next, cur + key.pasteText.length);
      return;
    }

    // Submit prompt, execute slash command, or run a local "!cmd" shell command
    if (key.name === "return" && !key.shift && !key.meta) {
      if (state.composerText.startsWith("/")) {
        const fullCmd = state.composerText;
        this.store.setComposerText("", 0);
        this.store.executeSlashCommand(fullCmd, this.client, this.onExit);
        return;
      }
      if (state.composerText.startsWith("!")) {
        const cmd = state.composerText.slice(1).trim();
        this.store.setComposerText("", 0);
        if (cmd) this.store.runLocalShellCommand(cmd);
        return;
      }
      this.store.submitComposer(this.client);
      return;
    }

    // Newline in composer (Shift+Enter or Alt+Enter)
    if (key.name === "return" && (key.shift || key.meta)) {
      const text = state.composerText;
      const cur = state.composerCursor;
      const next = text.slice(0, cur) + "\n" + text.slice(cur);
      this.store.setComposerText(next, cur + 1);
      return;
    }

    // Slash command trigger
    if (key.name === "/" && state.composerText.length === 0) {
      this.store.update((s) => ({
        ...s,
        activeModal: "command-palette",
        activeCommandQuery: "",
        modalSelectedIndex: 0,
      }));
      return;
    }

    // Help overlay trigger ('?' on empty prompt)
    if (key.name === "?" && state.composerText.length === 0) {
      this.store.update((s) => ({ ...s, activeModal: "help" }));
      return;
    }

    // Backspace
    if (key.name === "backspace") {
      const text = state.composerText;
      const cur = state.composerCursor;
      if (cur > 0) {
        const next = text.slice(0, cur - 1) + text.slice(cur);
        this.store.setComposerText(next, cur - 1);
      }
      return;
    }

    // Delete
    if (key.name === "delete") {
      const text = state.composerText;
      const cur = state.composerCursor;
      if (cur < text.length) {
        const next = text.slice(0, cur) + text.slice(cur + 1);
        this.store.setComposerText(next, cur);
      }
      return;
    }

    // Cursor navigation
    if (key.name === "left") {
      this.store.update((s) => ({ ...s, composerCursor: Math.max(0, s.composerCursor - 1) }));
      return;
    }
    if (key.name === "right") {
      this.store.update((s) => ({ ...s, composerCursor: Math.min(s.composerText.length, s.composerCursor + 1) }));
      return;
    }
    if (key.name === "home" || (key.ctrl && key.name === "a")) {
      this.store.update((s) => ({ ...s, composerCursor: 0 }));
      return;
    }
    if (key.name === "end" || (key.ctrl && key.name === "e")) {
      this.store.update((s) => ({ ...s, composerCursor: s.composerText.length }));
      return;
    }

    // Prompt History (Up / Down)
    if (key.name === "up") {
      const hist = state.composerHistory;
      if (hist.length > 0) {
        const nextIdx = state.historyIndex === -1 ? hist.length - 1 : Math.max(0, state.historyIndex - 1);
        const item = hist[nextIdx] ?? "";
        this.store.update((s) => ({
          ...s,
          historyIndex: nextIdx,
          composerText: item,
          composerCursor: item.length,
        }));
      }
      return;
    }
    if (key.name === "down") {
      const hist = state.composerHistory;
      if (state.historyIndex !== -1) {
        const nextIdx = state.historyIndex + 1;
        if (nextIdx < hist.length) {
          const item = hist[nextIdx] ?? "";
          this.store.update((s) => ({
            ...s,
            historyIndex: nextIdx,
            composerText: item,
            composerCursor: item.length,
          }));
        } else {
          this.store.update((s) => ({
            ...s,
            historyIndex: -1,
            composerText: "",
            composerCursor: 0,
          }));
        }
      }
      return;
    }

    // Regular typing character
    if (key.name.length === 1 && !key.ctrl && !key.meta) {
      const text = state.composerText;
      const cur = state.composerCursor;
      const next = text.slice(0, cur) + key.name + text.slice(cur);
      this.store.setComposerText(next, cur + 1);
    }
  }

  private handleTranscriptKey(key: KeyEvent): void {
    if (key.name === "j" || key.name === "down") {
      this.store.update((s) => ({ ...s, scrollOffset: Math.max(0, s.scrollOffset - 1) }));
      return;
    }
    if (key.name === "k" || key.name === "up") {
      this.store.update((s) => ({ ...s, scrollOffset: s.scrollOffset + 1 }));
      return;
    }
    if (key.name === "pageup" || (key.ctrl && key.name === "u")) {
      this.store.update((s) => ({ ...s, scrollOffset: s.scrollOffset + 8 }));
      return;
    }
    if (key.name === "pagedown" || (key.ctrl && key.name === "d")) {
      this.store.update((s) => ({ ...s, scrollOffset: Math.max(0, s.scrollOffset - 8) }));
      return;
    }
    if (key.name === "G") {
      this.store.update((s) => ({ ...s, scrollOffset: 0 }));
      return;
    }
    if (key.name === " " || key.name === "return") {
      // Toggle first activity card in latest turn
      const turns = this.store.get().turns;
      if (turns.length > 0) {
        const lastTurn = turns[turns.length - 1]!;
        if (lastTurn.activityCards.length > 0) {
          this.store.toggleCardExpansion(lastTurn.activityCards[0]!.id);
        }
      }
    }
  }

  private handleApprovalKey(key: KeyEvent): void {
    if (key.name === "y") {
      if (this.client) this.store.resolvePendingApproval(this.client, "approve");
      return;
    }
    if (key.name === "n") {
      if (this.client) this.store.resolvePendingApproval(this.client, "reject");
      return;
    }
    if (key.name === "d") {
      const pending = this.store.get().pendingApproval;
      if (pending && pending.unifiedDiff) {
        this.store.update((s) => ({
          ...s,
          activeModal: "diff-viewer",
          diffViewerContent: pending.unifiedDiff,
        }));
      }
      return;
    }
    if (key.name === "q") {
      const state = this.store.get();
      if (state.runId && this.client) {
        this.client.requestCancel(state.runId, { reason: "Rejected and cancelled from approval deck" });
      }
    }
  }

  private handleModalKey(key: KeyEvent): void {
    if (key.name === "escape") {
      this.store.update((s) => ({ ...s, activeModal: "none", modalSelectedIndex: 0, focus: "composer" }));
      return;
    }

    const state = this.store.get();
    const idx = state.modalSelectedIndex;

    if (state.activeModal === "command-palette") {
      if (key.name === "up") {
        this.setModalIndex(Math.max(0, idx - 1));
        return;
      }
      if (key.name === "down") {
        const filteredCount = filterCommandsByQuery(state.activeCommandQuery).length;
        this.setModalIndex(Math.min(Math.max(0, filteredCount - 1), idx + 1));
        return;
      }
      if (key.name === "return") {
        this.executePaletteCommand(idx, state.activeCommandQuery);
        // Only close back to "none" if the command didn't already switch to a
        // different modal (e.g. /agent opening the agent picker).
        this.store.update((s) =>
          s.activeModal === "command-palette"
            ? { ...s, activeModal: "none", modalSelectedIndex: 0 }
            : s,
        );
        return;
      }
      if (key.name === "backspace") {
        this.store.update((s) => ({
          ...s,
          activeCommandQuery: s.activeCommandQuery.slice(0, -1),
          modalSelectedIndex: 0,
        }));
        return;
      }
      if (key.name.length === 1 && !key.ctrl && !key.meta) {
        this.store.update((s) => ({
          ...s,
          activeCommandQuery: s.activeCommandQuery + key.name,
          modalSelectedIndex: 0,
        }));
      }
    } else if (state.activeModal === "select-agent") {
      this.handleSelectListKey(key, state.availableAgents, (picked) => this.store.selectAgent(picked.id));
    } else if (state.activeModal === "select-workflow") {
      this.handleSelectListKey(key, state.availableWorkflows, (picked) => this.store.selectWorkflow(picked.id));
    } else if (state.activeModal === "select-model") {
      this.handleSelectListKey(key, state.availableModels, (picked) => this.store.setModel(picked.id));
    } else if (state.activeModal === "history") {
      const convs = this.store.controller.getState().conversations;
      this.handleSelectListKey(key, convs, (picked) => this.store.controller.selectConversation(picked.id));
    }
  }

  private handleSelectListKey<T>(
    key: KeyEvent,
    items: readonly T[],
    pick: (item: T) => void,
  ): void {
    const idx = this.store.get().modalSelectedIndex;
    if (key.name === "up") {
      this.setModalIndex(Math.max(0, idx - 1));
    } else if (key.name === "down") {
      this.setModalIndex(Math.min(Math.max(0, items.length - 1), idx + 1));
    } else if (key.name === "return") {
      const picked = items[idx];
      if (picked) pick(picked);
      this.store.update((s) => ({ ...s, activeModal: "none", modalSelectedIndex: 0, focus: "composer" }));
    }
  }

  /**
   * Executes the exact CommandSpec at the selected palette index, applying the
   * same query filter the palette rendered against (filterCommandsByQuery)
   * so a filtered selection can never resolve to a different command than
   * the one on screen. Args typed after the command name (e.g. "busy queue")
   * are parsed via splitCommandQuery and passed through -- previously the
   * palette path always dispatched with empty args, silently dropping
   * anything typed after the command name.
   */
  private executePaletteCommand(index: number, query: string): void {
    const filtered = filterCommandsByQuery(query);
    const cmd = filtered[index];
    if (!cmd) return;
    const { args } = splitCommandQuery(query);
    const ctx = this.store.buildCommandContext(this.client, this.onExit);
    cmd.run(ctx, args);
  }
}

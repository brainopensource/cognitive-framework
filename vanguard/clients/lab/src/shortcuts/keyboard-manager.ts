import type { LabStore } from "../state/lab-store.js";
import { copyToClipboard } from "../util/clipboard.js";

export type ShortcutAction =
  | "nextEvent"
  | "prevEvent"
  | "nextError"
  | "prevError"
  | "nextApproval"
  | "prevApproval"
  | "toggleInspector"
  | "closeInspector"
  | "focusSearch"
  | "switchRuns"
  | "switchEvents"
  | "switchTrace"
  | "switchArtifacts"
  | "switchContext"
  | "switchSystem"
  | "jumpToLive"
  | "copyId"
  | "toggleHelp";

export class KeyboardManager {
  private store: LabStore;
  private keyListener: (e: KeyboardEvent) => void;
  private helpModalVisible: boolean = false;
  private helpModalEl: HTMLElement | null = null;

  constructor(store: LabStore) {
    this.store = store;
    this.keyListener = (e: KeyboardEvent) => this.handleKeyDown(e);
  }

  public attach(): void {
    if (typeof window !== "undefined") {
      window.addEventListener("keydown", this.keyListener);
    }
  }

  public detach(): void {
    if (typeof window !== "undefined") {
      window.removeEventListener("keydown", this.keyListener);
    }
  }

  public handleKeyDown(e: KeyboardEvent): void {
    // If active element is an input, textarea, or select, ignore single key shortcuts unless Escape
    const activeEl = typeof document !== "undefined" ? document.activeElement : null;
    const isEditing =
      activeEl &&
      (activeEl.tagName === "INPUT" ||
        activeEl.tagName === "TEXTAREA" ||
        activeEl.tagName === "SELECT" ||
        (activeEl as HTMLElement).isContentEditable);

    if (e.key === "Escape") {
      if (this.helpModalVisible) {
        this.toggleHelpModal(false);
        e.preventDefault();
        return;
      }
      if (isEditing) {
        (activeEl as HTMLElement).blur();
        e.preventDefault();
        return;
      }
      this.store.selection.toggleInspector(false);
      e.preventDefault();
      return;
    }

    if (isEditing) {
      return;
    }

    if (e.key === "?" && !e.ctrlKey && !e.metaKey) {
      this.toggleHelpModal();
      e.preventDefault();
      return;
    }

    // Workbench Navigation (1-6)
    if (e.key === "1") {
      this.store.selection.setWorkbench("runs");
      e.preventDefault();
      return;
    }
    if (e.key === "2") {
      this.store.selection.setWorkbench("events");
      e.preventDefault();
      return;
    }
    if (e.key === "3") {
      this.store.selection.setWorkbench("trace");
      e.preventDefault();
      return;
    }
    if (e.key === "4") {
      this.store.selection.setWorkbench("artifacts");
      e.preventDefault();
      return;
    }
    if (e.key === "5") {
      this.store.selection.setWorkbench("context");
      e.preventDefault();
      return;
    }
    if (e.key === "6") {
      this.store.selection.setWorkbench("system");
      e.preventDefault();
      return;
    }

    // Search focus
    if (e.key === "/" && !e.ctrlKey && !e.metaKey) {
      const searchInput = document.querySelector<HTMLInputElement>(".aether-search-input");
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
        e.preventDefault();
      }
      return;
    }

    // Jump to live
    if ((e.key === "l" && !e.ctrlKey && !e.metaKey) || e.key === "End") {
      this.store.jumpToLive();
      e.preventDefault();
      return;
    }

    // Copy selected ID
    if (e.key === "c" && !e.ctrlKey && !e.metaKey) {
      const sel = this.store.selection.get();
      const idToCopy =
        sel.selectedArtifactId ||
        sel.selectedApprovalId ||
        sel.selectedEventId ||
        sel.selectedRunId;
      if (idToCopy) {
        copyToClipboard(idToCopy);
      }
      e.preventDefault();
      return;
    }

    // Inspector toggle
    if (e.key === "i" || e.key === "Enter" || e.key === " ") {
      this.store.selection.toggleInspector();
      e.preventDefault();
      return;
    }

    // Event ledger navigation: j/k, Down/Up
    if (e.key === "j" || e.key === "ArrowDown") {
      this.navigateEvent(1);
      e.preventDefault();
      return;
    }
    if (e.key === "k" || e.key === "ArrowUp") {
      this.navigateEvent(-1);
      e.preventDefault();
      return;
    }

    // Error navigation: e / Shift+E
    if (e.key === "e" || e.key === "E") {
      const direction = e.shiftKey ? -1 : 1;
      this.navigateFilteredEvent("errors", direction);
      e.preventDefault();
      return;
    }

    // Approval navigation: a / Shift+A
    if (e.key === "a" || e.key === "A") {
      const direction = e.shiftKey ? -1 : 1;
      this.navigateFilteredEvent("approvals", direction);
      e.preventDefault();
      return;
    }
  }

  private navigateEvent(delta: number): void {
    const filtered = this.store.getFilteredEvents();
    if (filtered.length === 0) return;

    const currentId = this.store.selection.get().selectedEventId;
    let currentIndex = currentId ? filtered.findIndex((e) => e.eventId === currentId) : -1;

    let targetIndex = currentIndex + delta;
    if (targetIndex < 0) targetIndex = 0;
    if (targetIndex >= filtered.length) targetIndex = filtered.length - 1;

    const targetEvent = filtered[targetIndex];
    if (targetEvent) {
      this.store.selection.selectEvent(targetEvent.eventId, targetEvent.seq);
    }
  }

  private navigateFilteredEvent(type: "errors" | "approvals", delta: number): void {
    const events = this.store.get().events;
    if (events.length === 0) return;

    const matching = events.filter((env) => {
      const kind = env.payload.kind;
      if (type === "errors") {
        return (
          kind === "EffectFailed" ||
          kind === "ServiceError" ||
          typeof env.payload.error === "string" ||
          env.payload.outcome === "failed"
        );
      } else {
        return kind === "ApprovalRequested" || kind === "ApprovalResolved";
      }
    });

    if (matching.length === 0) return;

    const currentId = this.store.selection.get().selectedEventId;
    let matchIndex = currentId ? matching.findIndex((e) => e.eventId === currentId) : -1;

    let targetIndex = matchIndex + delta;
    if (targetIndex < 0) targetIndex = matching.length - 1;
    if (targetIndex >= matching.length) targetIndex = 0;

    const target = matching[targetIndex];
    if (target) {
      this.store.selection.selectEvent(target.eventId, target.seq);
    }
  }

  public toggleHelpModal(show?: boolean): void {
    this.helpModalVisible = show !== undefined ? show : !this.helpModalVisible;
    if (typeof document === "undefined") return;

    if (!this.helpModalVisible) {
      if (this.helpModalEl && this.helpModalEl.parentNode) {
        this.helpModalEl.parentNode.removeChild(this.helpModalEl);
        this.helpModalEl = null;
      }
      return;
    }

    if (!this.helpModalEl) {
      this.helpModalEl = document.createElement("div");
      this.helpModalEl.className = "aether-shortcuts-modal-backdrop";
      this.helpModalEl.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.75);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
      `;

      const dialog = document.createElement("div");
      dialog.className = "aether-shortcuts-dialog";
      dialog.setAttribute("role", "dialog");
      dialog.setAttribute("aria-label", "Keyboard Shortcuts");
      dialog.style.cssText = `
        background: var(--lab-bg-surface);
        border: 1px solid var(--lab-border);
        border-radius: var(--lab-radius-md);
        padding: 20px;
        max-width: 520px;
        width: 90%;
        color: var(--lab-text-primary);
        font-family: var(--lab-font-sans);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      `;

      dialog.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--lab-border); padding-bottom: 8px;">
          <h2 style="margin: 0; font-size: 16px; font-weight: 600;">Forensic Keyboard Navigation</h2>
          <span style="font-size: 12px; color: var(--lab-text-muted);">Press Esc to close</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
          <div>
            <div style="color: var(--lab-accent); font-weight: 600; margin-bottom: 6px;">Ledger Navigation</div>
            <div><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">j</kbd> / <kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">↓</kbd> Next event</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">k</kbd> / <kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">↑</kbd> Prev event</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">e</kbd> / <kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">Shift+E</kbd> Error jumps</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">a</kbd> / <kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">Shift+A</kbd> Approval jumps</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">l</kbd> / <kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">End</kbd> Jump to live tail</div>
          </div>
          <div>
            <div style="color: var(--lab-accent); font-weight: 600; margin-bottom: 6px;">Workbenches & Actions</div>
            <div><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">1</kbd>–<kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">6</kbd> Switch workbench</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">i</kbd> / <kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">Enter</kbd> Toggle inspector</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">/</kbd> Focus search filter</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">c</kbd> Copy selected ID</div>
            <div style="margin-top: 4px;"><kbd style="background: var(--lab-bg-panel); padding: 2px 6px; border: 1px solid var(--lab-border); border-radius: 3px; font-family: var(--lab-font-mono);">Esc</kbd> Close drawer</div>
          </div>
        </div>
      `;

      this.helpModalEl.appendChild(dialog);
      this.helpModalEl.addEventListener("click", (evt) => {
        if (evt.target === this.helpModalEl) {
          this.toggleHelpModal(false);
        }
      });
      document.body.appendChild(this.helpModalEl);
    }
  }
}

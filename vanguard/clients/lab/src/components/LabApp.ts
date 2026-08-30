import { LabStore } from "../state/lab-store.js";
import { WorkbenchRegistry } from "./workbenches/workbench-registry.js";
import { KeyboardManager } from "../shortcuts/keyboard-manager.js";
import { renderLabShell } from "./LabShell.js";
import { getCssVariables, LAB_THEME } from "../theme/tokens.js";
import type { RuntimeClient } from "@aether/client";

export type LabAppOptions = {
  store?: LabStore;
  client?: RuntimeClient;
  registry?: WorkbenchRegistry;
};

export class LabApp {
  public readonly store: LabStore;
  public readonly registry: WorkbenchRegistry;
  public readonly keyboard: KeyboardManager;
  public readonly client?: RuntimeClient;

  private rootElement: HTMLElement | null = null;
  private unsubscribeStore?: () => void;
  private unsubscribeSelection?: () => void;
  private hashListener?: () => void;

  constructor(options: LabAppOptions = {}) {
    this.store = options.store ?? new LabStore();
    this.registry = options.registry ?? new WorkbenchRegistry();
    this.keyboard = new KeyboardManager(this.store);
    this.client = options.client;
  }

  public mount(target: HTMLElement): void {
    this.rootElement = target;

    // Inject CSS Tokens
    if (typeof document !== "undefined") {
      const styleEl = document.createElement("style");
      styleEl.id = "aether-lab-theme-vars";
      styleEl.textContent = getCssVariables(LAB_THEME);
      document.head.appendChild(styleEl);
    }

    // Attach Keyboard Manager
    this.keyboard.attach();

    // Read initial deep link from hash if in browser
    if (typeof window !== "undefined") {
      this.store.selection.fromHashString(window.location.hash);

      this.hashListener = () => {
        this.store.selection.fromHashString(window.location.hash);
      };
      window.addEventListener("hashchange", this.hashListener);
    }

    // Subscribe to state changes
    this.unsubscribeStore = this.store.state.subscribe(() => {
      this.render();
    });

    this.unsubscribeSelection = this.store.selection.state.subscribe(() => {
      // Sync URL hash
      if (typeof window !== "undefined") {
        const hash = this.store.selection.toHashString();
        if (window.location.hash !== hash) {
          window.history.replaceState(null, "", hash);
        }
      }
      this.render();
    });

    // Auto-load runs if client provided
    if (this.client) {
      this.store.loadRuns(this.client);
      this.store.checkSystemCapabilities(this.client);
    }

    this.render();
  }

  public unmount(): void {
    if (this.unsubscribeStore) this.unsubscribeStore();
    if (this.unsubscribeSelection) this.unsubscribeSelection();
    if (this.hashListener && typeof window !== "undefined") {
      window.removeEventListener("hashchange", this.hashListener);
    }
    this.keyboard.detach();

    if (this.rootElement) {
      this.rootElement.innerHTML = "";
      this.rootElement = null;
    }
  }

  public render(): HTMLElement {
    const shell = renderLabShell(this.store, this.registry, this.client);

    if (this.rootElement) {
      this.rootElement.innerHTML = "";
      this.rootElement.appendChild(shell);
    }

    return shell;
  }
}

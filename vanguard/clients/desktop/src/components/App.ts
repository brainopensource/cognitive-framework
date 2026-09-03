import { DesktopStore } from "../state/desktop-store.js";
import { captureFocus, restoreFocus } from "../dom/focus-preservation.js";
import { TauriNativeBridge } from "../bridge/tauri-bridge.js";
import { generateCssVariables, getThemeTokens } from "@aether/projections";
import { renderSidebar } from "./Sidebar.js";
import { renderTopBar } from "./TopBar.js";
import { renderApprovalBanner } from "./ApprovalBanner.js";
import { renderTranscriptPane } from "./TranscriptPane.js";
import { renderComposer } from "./Composer.js";
import { renderForensicDrawer } from "./ForensicDrawer.js";
import { renderCommandPalette } from "./CommandPalette.js";
import { renderStartupReadinessModal, renderMultiAgentStatusBar } from "@aether/ui-web";
import type { RuntimeClient } from "@aether/client";

export class DesktopApp {
  public readonly store: DesktopStore;
  public readonly bridge: TauriNativeBridge;
  private readonly client?: RuntimeClient;
  private rootElement: HTMLElement | null = null;
  private unsubscribe?: () => void;
  private keydownHandler?: (e: KeyboardEvent) => void;
  private readinessDismissed = false;

  constructor(options: { store?: DesktopStore; client?: RuntimeClient; bridge?: TauriNativeBridge } = {}) {
    this.bridge = options.bridge ?? new TauriNativeBridge();
    this.store = options.store ?? new DesktopStore({ bridge: this.bridge });
    this.client = options.client;
  }

  public mount(target: HTMLElement): void {
    this.rootElement = target;

    // Inject CSS variables
    if (typeof document !== "undefined" && document.head) {
      const themeName = this.store.get().settings.appearance.theme ?? "dark";
      const styleEl = document.createElement("style");
      styleEl.textContent = generateCssVariables(getThemeTokens(themeName));
      document.head.appendChild(styleEl);
    }

    // Keyboard Shortcuts
    this.keydownHandler = (e: KeyboardEvent) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey;

      if (isCmdOrCtrl && e.key.toLowerCase() === "k") {
        e.preventDefault();
        this.store.toggleCommandPalette();
      } else if (isCmdOrCtrl && e.key.toLowerCase() === "n") {
        e.preventDefault();
        this.store.newChat();
      } else if (isCmdOrCtrl && e.key.toLowerCase() === "l") {
        e.preventDefault();
        const textarea = document.querySelector(".aether-composer textarea") as HTMLTextAreaElement;
        if (textarea) textarea.focus();
      } else if (isCmdOrCtrl && e.key.toLowerCase() === "f") {
        e.preventDefault();
        const searchInput = document.querySelector(".aether-search-input-wrapper input") as HTMLInputElement;
        if (searchInput) searchInput.focus();
      } else if (e.key === "Escape") {
        if (this.store.get().commandPaletteOpen) {
          this.store.toggleCommandPalette(false);
        } else if (this.store.get().forensicDrawerOpen) {
          this.store.closeForensicDrawer();
        }
      }
    };

    if (typeof window !== "undefined") {
      window.addEventListener("keydown", this.keydownHandler);
    }

    this.unsubscribe = this.store.state.subscribe(() => {
      this.render();
    });

    this.render();
  }

  public unmount(): void {
    if (this.unsubscribe) this.unsubscribe();
    if (typeof window !== "undefined" && this.keydownHandler) {
      window.removeEventListener("keydown", this.keydownHandler);
    }
    if (this.rootElement) this.rootElement.innerHTML = "";
    this.store.destroy();
  }

  public render(): HTMLElement {
    const state = this.store.get();
    const appContainer = document.createElement("div");
    appContainer.className = `aether-desktop-app layout-${state.layoutMode.toLowerCase()}`;
    appContainer.style.cssText = `
      display: flex;
      width: 100vw;
      height: 100vh;
      background: var(--aether-bg, #11111b);
      color: var(--aether-text-primary, #cdd6f4);
      font-family: var(--aether-font-sans, sans-serif);
      overflow: hidden;
      position: relative;
    `;

    // 1. Sidebar (Left - collapsible)
    if (state.sidebarOpen && state.layoutMode !== "COMPACT") {
      appContainer.appendChild(renderSidebar(this.store));
    }

    // 2. Main Content (Center)
    const mainCol = document.createElement("div");
    mainCol.style.cssText = "flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; min-width: 0;";

    mainCol.appendChild(renderTopBar(this.store, this.bridge));

    // Multi-Agent status bar if applicable
    if (state.workflowExecution && state.workflowExecution.participants.length > 1) {
      mainCol.appendChild(renderMultiAgentStatusBar(state.workflowExecution));
    }

    const banner = renderApprovalBanner(this.store, this.client);
    if (banner) mainCol.appendChild(banner);

    mainCol.appendChild(renderTranscriptPane(this.store));
    mainCol.appendChild(renderComposer(this.store, this.client));

    appContainer.appendChild(mainCol);

    // 3. Forensic Drawer (Right - Pinned in WIDE, Overlay/Slide in STANDARD)
    const drawer = renderForensicDrawer(this.store);
    if (drawer) appContainer.appendChild(drawer);

    // 4. Command Palette (Modal Overlay)
    const palette = renderCommandPalette(this.store);
    if (palette) appContainer.appendChild(palette);

    // 5. Startup Readiness Gate (Modal when unready and not dismissed)
    if (!state.readiness.isReady && !this.readinessDismissed) {
      const readinessModal = renderStartupReadinessModal({
        readiness: state.readiness,
        onAction: (step) => {
          if (step.id === "provider" || step.id === "credential") {
            this.store.openForensicDrawer("settings");
            this.store.update((s) => ({ ...s, activeSettingsTab: "providers" }));
          } else if (step.id === "runtime") {
            void this.store.connectRuntime();
          } else if (step.id === "workspace") {
            this.bridge.openDirectoryDialog().then((dir) => {
              if (dir) this.store.controller.selectWorkspace(dir);
            });
          }
          this.readinessDismissed = true;
          this.render();
        },
      });
      appContainer.appendChild(readinessModal);
    }

    if (this.rootElement) {
      // Focus lives on a node that is about to be discarded, so it has to be
      // carried across the swap explicitly or every keystroke blurs the field
      // that produced it.
      const focused = captureFocus(this.rootElement.ownerDocument ?? document);
      this.rootElement.innerHTML = "";
      this.rootElement.appendChild(appContainer);
      restoreFocus(focused, this.rootElement);
    }

    return appContainer;
  }
}

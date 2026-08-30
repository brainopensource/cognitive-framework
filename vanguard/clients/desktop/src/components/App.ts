import { DesktopStore } from "../state/desktop-store.js";
import { TauriNativeBridge } from "../bridge/tauri-bridge.js";
import { getCssVariables, DARK_DESKTOP_THEME } from "../theme/tokens.js";
import { renderSidebar } from "./Sidebar.js";
import { renderTopBar } from "./TopBar.js";
import { renderApprovalBanner } from "./ApprovalBanner.js";
import { renderTranscriptPane } from "./TranscriptPane.js";
import { renderComposer } from "./Composer.js";
import { renderForensicDrawer } from "./ForensicDrawer.js";
import type { RuntimeClient } from "@aether/client";

export class DesktopApp {
  public readonly store: DesktopStore;
  public readonly bridge: TauriNativeBridge;
  private readonly client?: RuntimeClient;
  private rootElement: HTMLElement | null = null;
  private unsubscribe?: () => void;

  constructor(options: { store?: DesktopStore; client?: RuntimeClient; bridge?: TauriNativeBridge } = {}) {
    this.store = options.store ?? new DesktopStore();
    this.bridge = options.bridge ?? new TauriNativeBridge();
    this.client = options.client;
  }

  public mount(target: HTMLElement): void {
    this.rootElement = target;

    // Inject CSS variables
    const styleEl = document.createElement("style");
    styleEl.textContent = getCssVariables(DARK_DESKTOP_THEME);
    document.head.appendChild(styleEl);

    this.unsubscribe = this.store.state.subscribe(() => {
      this.render();
    });

    this.render();
  }

  public unmount(): void {
    if (this.unsubscribe) this.unsubscribe();
    if (this.rootElement) this.rootElement.innerHTML = "";
  }

  public render(): HTMLElement {
    const appContainer = document.createElement("div");
    appContainer.className = "aether-desktop-app";
    appContainer.style.cssText = `
      display: flex;
      width: 100vw;
      height: 100vh;
      background: var(--aether-bg);
      color: var(--aether-text-primary);
      font-family: var(--aether-font-sans);
      overflow: hidden;
    `;

    // 1. Sidebar (Left)
    appContainer.appendChild(renderSidebar(this.store));

    // 2. Main Content (Center)
    const mainCol = document.createElement("div");
    mainCol.style.cssText = "flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden;";

    mainCol.appendChild(renderTopBar(this.store, this.bridge));

    const banner = renderApprovalBanner(this.store, this.client);
    if (banner) mainCol.appendChild(banner);

    mainCol.appendChild(renderTranscriptPane(this.store));
    mainCol.appendChild(renderComposer(this.store, this.client));

    appContainer.appendChild(mainCol);

    // 3. Forensic Drawer (Right - Collapsible)
    const drawer = renderForensicDrawer(this.store);
    if (drawer) appContainer.appendChild(drawer);

    if (this.rootElement) {
      this.rootElement.innerHTML = "";
      this.rootElement.appendChild(appContainer);
    }

    return appContainer;
  }
}

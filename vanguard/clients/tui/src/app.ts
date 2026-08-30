import { TerminalScreen, type ScreenOptions } from "./terminal/screen.js";
import { KeyParser } from "./terminal/input.js";
import { TuiStore, type TuiStoreState } from "./store.js";
import { KeyboardManager } from "./keyboard.js";
import { DEFAULT_THEME, type ThemeTokens } from "./theme.js";
import { renderHeader } from "./components/header.js";
import { renderTranscript } from "./components/transcript.js";
import { renderApprovalDeck } from "./components/approval-deck.js";
import { renderComposer } from "./components/composer.js";
import { renderStatusFooter } from "./components/status-footer.js";
import { renderConnectionBanner } from "./components/connection-banner.js";
import { renderCommandPalette } from "./components/command-palette.js";
import { renderHelpOverlay } from "./components/help-overlay.js";
import { renderDiffViewer } from "./components/diff-viewer.js";
import { renderSelectModal } from "./components/select-modal.js";
import type { RuntimeClient } from "@aether/client";

export type TuiAppOptions = {
  client?: RuntimeClient;
  initialState?: Partial<TuiStoreState>;
  screenOptions?: ScreenOptions;
  theme?: ThemeTokens;
};

export class TuiApplication {
  public readonly screen: TerminalScreen;
  public readonly store: TuiStore;
  public readonly keyboard: KeyboardManager;
  private readonly parser: KeyParser;
  private readonly theme: ThemeTokens;
  private isRunning: boolean = false;
  private unsubscribeStore?: () => void;
  private resizeHandler?: () => void;

  constructor(options: TuiAppOptions = {}) {
    this.theme = options.theme ?? DEFAULT_THEME;
    this.screen = new TerminalScreen(options.screenOptions);
    this.store = new TuiStore(options.initialState);
    this.parser = new KeyParser();
    this.keyboard = new KeyboardManager(this.store, options.client, () => this.stop());
  }

  public start(): void {
    if (this.isRunning) return;
    this.isRunning = true;

    this.screen.enterRawMode();

    // Key input listener
    process.stdin.on("data", (chunk: Buffer) => {
      const keys = this.parser.parse(chunk);
      for (const key of keys) {
        this.keyboard.handleKey(key);
      }
    });

    // Resize listener (SIGWINCH)
    this.resizeHandler = () => {
      if (process.stdout.columns && process.stdout.rows) {
        this.screen.resize(process.stdout.columns, process.stdout.rows);
        this.renderFrame();
      }
    };
    process.stdout.on("resize", this.resizeHandler);

    // Reactive store subscription
    this.unsubscribeStore = this.store.state.subscribe(() => {
      this.renderFrame();
    });

    this.renderFrame();
  }

  public stop(): void {
    if (!this.isRunning) return;
    this.isRunning = false;

    if (this.unsubscribeStore) this.unsubscribeStore();
    if (this.resizeHandler) process.stdout.off("resize", this.resizeHandler);

    this.screen.exitRawMode();
  }

  public renderFrame(): void {
    const state = this.store.get();
    const height = this.screen.height;
    const width = this.screen.width;

    this.screen.clear();

    // 1. Header (2 rows: content + border)
    renderHeader(this.screen, state, 0, this.theme);
    let curRow = 2;

    // 2. Connection Banner if needed
    const bannerRows = renderConnectionBanner(this.screen, state.connectionState, curRow, this.theme);
    curRow += bannerRows;

    // 3. Status Footer at bottom
    const footerRow = height - 1;
    renderStatusFooter(this.screen, state, footerRow, this.theme);

    // 4. Composer above footer (3 rows)
    const composerHeight = 3;
    const composerStartRow = footerRow - composerHeight;
    renderComposer(this.screen, state, composerStartRow, composerHeight, this.theme);

    // 5. Governance / Approval Deck above composer if pending
    let approvalRows = 0;
    if (state.pendingApproval) {
      const approvalStartRow = composerStartRow - 5;
      approvalRows = renderApprovalDeck(this.screen, state, approvalStartRow, this.theme);
    }

    // 6. Transcript in the remaining viewport
    const transcriptEndRow = composerStartRow - approvalRows;
    const transcriptHeight = Math.max(1, transcriptEndRow - curRow);
    renderTranscript(this.screen, state, curRow, transcriptHeight, this.theme);

    // 7. Modals / Overlays if active
    if (state.activeModal === "command-palette") {
      const commands = [
        { id: "agent", name: "/agent", description: "Switch active agent manifest", action: () => {} },
        { id: "workflow", name: "/workflow", description: "Switch workflow definition", action: () => {} },
        { id: "cancel", name: "/cancel", description: "Cancel current active agent run", action: () => {} },
        { id: "help", name: "/help", description: "Show keyboard shortcuts and help", action: () => {} },
        { id: "quit", name: "/quit", description: "Exit AETHER terminal cockpit", action: () => {} },
      ];
      renderCommandPalette(
        this.screen,
        commands,
        this.keyboard.getCommandSelectedIndex(),
        state.activeCommandQuery,
        this.theme
      );
    } else if (state.activeModal === "help") {
      renderHelpOverlay(this.screen, this.theme);
    } else if (state.activeModal === "diff-viewer") {
      renderDiffViewer(this.screen, state.diffViewerContent, 0, this.theme);
    } else if (state.activeModal === "select-agent") {
      renderSelectModal(
        this.screen,
        "Agent",
        state.availableAgents.map((a) => ({ id: a.id, name: a.name, description: a.description })),
        this.keyboard.getSelectModalIndex(),
        this.theme
      );
    } else if (state.activeModal === "select-workflow") {
      renderSelectModal(
        this.screen,
        "Workflow",
        state.availableWorkflows.map((w) => ({ id: w.id, name: w.name, description: w.description })),
        this.keyboard.getSelectModalIndex(),
        this.theme
      );
    } else if (state.activeModal === "history") {
      const convs = this.store.controller.getState().conversations;
      renderSelectModal(
        this.screen,
        "Conversation History",
        convs.map((c: any) => ({ id: c.id.slice(0, 8), name: c.title, description: `${c.turnCount} turns • ${c.workspacePath}` })),
        this.keyboard.getSelectModalIndex(),
        this.theme
      );
    }

    this.screen.render();
  }
}

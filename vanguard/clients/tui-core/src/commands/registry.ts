/**
 * Single source of truth for slash commands: the palette, /help, tab-completion,
 * and dispatch all render from this one array. Replaces the two independently
 * indexed command lists (tui/src/app.ts palette entries vs. tui/src/keyboard.ts
 * executePaletteCommand) whose positions could silently drift apart.
 */
export interface TuiCommandContext {
  openModal(modal: string): void;
  closeModal(): void;
  selectAgent(agentId: string): void;
  selectWorkflow(workflowId: string): void;
  selectWorkspace(path: string): void;
  setProvider(providerId: string): void;
  setModel(modelId: string): void;
  togglePlanMode(): void;
  showStatus(message: string): void;
  resume(runIdOrLatest?: string): void;
  attach(runId: string): void;
  cancelRun(): void;
  newChat(): void;
  clearTranscript(): void;
  exit(): void;
  login(): void;
  logout(): void;
  setTitle(title: string): void;
  showRunStatus(): void;
  showContext(): void;
  showCost(): void;
  compactTranscript(): void;
  showDoctor(): void;
  showDiff(): void;
  undo(): void;
  initWorkspace(): void;
}

export interface CommandSpec {
  /** Canonical name, without the leading "/". */
  readonly name: string;
  readonly aliases: readonly string[];
  readonly description: string;
  readonly argHint?: string;
  /** Whether this command may run while plan mode withholds write authority. */
  readonly availableInPlanMode: boolean;
  readonly run: (ctx: TuiCommandContext, args: string) => void;
}

function command(spec: CommandSpec): CommandSpec {
  return spec;
}

export const COMMAND_REGISTRY: readonly CommandSpec[] = [
  command({
    name: "help",
    aliases: ["?"],
    description: "Show keyboard shortcuts and available commands",
    availableInPlanMode: true,
    run: (ctx) => ctx.openModal("help"),
  }),
  command({
    name: "agents",
    aliases: ["agent"],
    description: "Switch active agent manifest",
    argHint: "[agent-id]",
    availableInPlanMode: true,
    run: (ctx, args) => (args ? ctx.selectAgent(args) : ctx.openModal("select-agent")),
  }),
  command({
    name: "workflow",
    aliases: [],
    description: "Switch workflow definition",
    argHint: "[workflow-id]",
    availableInPlanMode: true,
    run: (ctx, args) => (args ? ctx.selectWorkflow(args) : ctx.openModal("select-workflow")),
  }),
  command({
    name: "workspace",
    aliases: [],
    description: "Switch active workspace root",
    argHint: "[path]",
    availableInPlanMode: true,
    run: (ctx, args) => (args ? ctx.selectWorkspace(args) : ctx.showStatus("workspace")),
  }),
  command({
    name: "provider",
    aliases: [],
    description: "Set the default model provider",
    argHint: "[provider-id]",
    availableInPlanMode: true,
    run: (ctx, args) => (args ? ctx.setProvider(args) : ctx.showStatus("provider")),
  }),
  command({
    name: "model",
    aliases: [],
    description: "Pick or set the active model, validated against the model registry",
    argHint: "[model-id]",
    availableInPlanMode: true,
    run: (ctx, args) => (args ? ctx.setModel(args) : ctx.openModal("select-model")),
  }),
  command({
    name: "plan",
    aliases: [],
    description: "Toggle plan mode (read-only execution profile for the next turn)",
    availableInPlanMode: true,
    run: (ctx) => ctx.togglePlanMode(),
  }),
  command({
    name: "resume",
    aliases: [],
    description: "Resume a prior run; \"/resume latest\" skips the picker",
    argHint: "[run-id|latest]",
    availableInPlanMode: true,
    run: (ctx, args) => ctx.resume(args || undefined),
  }),
  command({
    name: "attach",
    aliases: [],
    description: "Attach to a live run by id",
    argHint: "<run-id>",
    availableInPlanMode: true,
    run: (ctx, args) => args && ctx.attach(args),
  }),
  command({
    name: "sessions",
    aliases: ["history"],
    description: "Browse conversation history",
    availableInPlanMode: true,
    run: (ctx) => ctx.openModal("history"),
  }),
  command({
    name: "new",
    aliases: [],
    description: "Start a new conversation",
    availableInPlanMode: true,
    run: (ctx) => ctx.newChat(),
  }),
  command({
    name: "clear",
    aliases: [],
    description: "Clear the transcript view",
    availableInPlanMode: true,
    run: (ctx) => ctx.clearTranscript(),
  }),
  command({
    name: "cancel",
    aliases: [],
    description: "Cancel the current active agent run",
    availableInPlanMode: true,
    run: (ctx) => ctx.cancelRun(),
  }),
  command({
    name: "login",
    aliases: [],
    description: "Sign in and persist a session",
    availableInPlanMode: true,
    run: (ctx) => ctx.login(),
  }),
  command({
    name: "logout",
    aliases: [],
    description: "Clear the persisted session",
    availableInPlanMode: true,
    run: (ctx) => ctx.logout(),
  }),
  command({
    name: "exit",
    aliases: ["quit", "q"],
    description: "Cancel any live run, flush state, and exit",
    availableInPlanMode: true,
    run: (ctx) => ctx.exit(),
  }),
  command({
    name: "init",
    aliases: [],
    description: "Seed a workspace context file (AETHER.md) describing this repo for the agent",
    availableInPlanMode: false,
    run: (ctx) => ctx.initWorkspace(),
  }),
  command({
    name: "title",
    aliases: [],
    description: "Rename the current conversation",
    argHint: "<name>",
    availableInPlanMode: true,
    run: (ctx, args) => args && ctx.setTitle(args),
  }),
  command({
    name: "status",
    aliases: [],
    description: "Show agent, workflow, model, workspace, and connection status",
    availableInPlanMode: true,
    run: (ctx) => ctx.showRunStatus(),
  }),
  command({
    name: "context",
    aliases: [],
    description: "Show current token usage against the model's context budget",
    availableInPlanMode: true,
    run: (ctx) => ctx.showContext(),
  }),
  command({
    name: "cost",
    aliases: [],
    description: "Show accumulated cost for the current run",
    availableInPlanMode: true,
    run: (ctx) => ctx.showCost(),
  }),
  command({
    name: "compact",
    aliases: [],
    description: "Trim the transcript view to the most recent turns (local view only)",
    availableInPlanMode: true,
    run: (ctx) => ctx.compactTranscript(),
  }),
  command({
    name: "doctor",
    aliases: [],
    description: "Check daemon connectivity and runtime health",
    availableInPlanMode: true,
    run: (ctx) => ctx.showDoctor(),
  }),
  command({
    name: "diff",
    aliases: [],
    description: "View the unified diff for the pending approval, if any",
    availableInPlanMode: true,
    run: (ctx) => ctx.showDiff(),
  }),
  command({
    name: "undo",
    aliases: [],
    description: "Git-backed undo of the last applied patch (not yet implemented)",
    availableInPlanMode: false,
    run: (ctx) => ctx.undo(),
  }),
];

export function listCommands(): readonly CommandSpec[] {
  return COMMAND_REGISTRY;
}

export function findCommand(nameOrAlias: string): CommandSpec | undefined {
  const needle = nameOrAlias.toLowerCase().replace(/^\//, "");
  return COMMAND_REGISTRY.find(
    (c) => c.name === needle || c.aliases.includes(needle)
  );
}

export type CommandExecutionResult =
  | { ok: true; command: CommandSpec }
  | { ok: false; error: string };

/** Parses "/name arg text" and dispatches to the matching CommandSpec. */
export function executeCommandLine(
  line: string,
  ctx: TuiCommandContext,
  opts: { planMode?: boolean } = {}
): CommandExecutionResult {
  const body = line.trim().replace(/^\//, "");
  const spaceIdx = body.indexOf(" ");
  const name = (spaceIdx === -1 ? body : body.slice(0, spaceIdx)).toLowerCase();
  const args = spaceIdx === -1 ? "" : body.slice(spaceIdx + 1).trim();

  const spec = findCommand(name);
  if (!spec) {
    return { ok: false, error: `Unknown slash command: /${name}` };
  }
  if (opts.planMode && !spec.availableInPlanMode) {
    return { ok: false, error: `/${spec.name} is unavailable in plan mode` };
  }
  spec.run(ctx, args);
  return { ok: true, command: spec };
}

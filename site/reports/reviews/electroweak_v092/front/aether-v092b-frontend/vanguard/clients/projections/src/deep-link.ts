import type { DeepLinkTarget } from "@aether/contracts";

export type ResolvedSurfaceAction = {
  surface: "desktop" | "lab" | "tui" | "cli";
  target: DeepLinkTarget;
  actionName: string;
  uri: string;
  desktopRoute?: {
    tab?: "diffs" | "evidence" | "artifacts" | "trace";
    runId?: string;
    seq?: string;
    digest?: string;
    approvalId?: string;
  };
  labRoute?: {
    workbench: "runs" | "events" | "trace" | "artifacts" | "context" | "system";
    runId?: string;
    selectedEventSeq?: string;
    selectedNodeId?: string;
    artifactDigest?: string;
  };
  tuiAction?: {
    focus?: "composer" | "transcript" | "approval" | "modal" | "diff";
    modal?: "none" | "command-palette" | "help" | "diff-viewer" | "select-agent" | "select-workflow";
    runId?: string;
  };
  cliCommand?: string;
};

export function parseDeepLink(uri: string): DeepLinkTarget | null {
  if (!uri || !uri.startsWith("aether://")) {
    return null;
  }

  const path = uri.slice("aether://".length).replace(/^\/+/, "");
  const parts = path.split("/").filter(Boolean);

  if (parts.length === 0) return null;

  const [resource, id, subResource, subId] = parts;

  if (resource === "run" && id) {
    if (subResource === "event" && subId) {
      return { kind: "event", runId: id, seq: subId };
    }
    return { kind: "run", runId: id };
  }

  if (resource === "event" && id && subResource) {
    return { kind: "event", runId: id, seq: subResource };
  }

  if (resource === "artifact" && id) {
    return { kind: "artifact", digest: id };
  }

  if (resource === "approval" && id) {
    return { kind: "approval", approvalId: id };
  }

  if (resource === "trace" && id && subResource) {
    return { kind: "trace", runId: id, nodeId: subResource };
  }

  if (resource === "trace" && id) {
    return { kind: "trace", runId: id, nodeId: "root" };
  }

  if (resource === "context") {
    return { kind: "context", layer: id };
  }

  return null;
}

export function formatDeepLink(target: DeepLinkTarget): string {
  switch (target.kind) {
    case "run":
      return target.eventSeq ? `aether://run/${target.runId}/event/${target.eventSeq}` : `aether://run/${target.runId}`;
    case "event":
      return `aether://run/${target.runId}/event/${target.seq}`;
    case "artifact":
      return `aether://artifact/${target.digest}`;
    case "approval":
      return `aether://approval/${target.approvalId}`;
    case "trace":
      return `aether://trace/${target.runId}/${target.nodeId}`;
    case "context":
      return target.layer ? `aether://context/${target.layer}` : "aether://context";
  }
}

export function resolveDeepLink(
  target: DeepLinkTarget,
  surface: "desktop" | "lab" | "tui" | "cli"
): ResolvedSurfaceAction {
  const uri = formatDeepLink(target);

  switch (surface) {
    case "desktop": {
      switch (target.kind) {
        case "run":
          return {
            surface: "desktop",
            target,
            actionName: "switch-run",
            uri,
            desktopRoute: { runId: target.runId },
          };
        case "event":
          return {
            surface: "desktop",
            target,
            actionName: "inspect-event",
            uri,
            desktopRoute: { runId: target.runId, seq: target.seq, tab: "evidence" },
          };
        case "artifact":
          return {
            surface: "desktop",
            target,
            actionName: "inspect-artifact",
            uri,
            desktopRoute: { digest: target.digest, tab: "artifacts" },
          };
        case "approval":
          return {
            surface: "desktop",
            target,
            actionName: "focus-approval",
            uri,
            desktopRoute: { approvalId: target.approvalId },
          };
        case "trace":
          return {
            surface: "desktop",
            target,
            actionName: "inspect-trace",
            uri,
            desktopRoute: { runId: target.runId, tab: "trace" },
          };
        case "context":
          return {
            surface: "desktop",
            target,
            actionName: "inspect-context",
            uri,
            desktopRoute: { tab: "evidence" },
          };
      }
    }

    case "lab": {
      switch (target.kind) {
        case "run":
          return {
            surface: "lab",
            target,
            actionName: "open-runs-workbench",
            uri,
            labRoute: { workbench: "runs", runId: target.runId },
          };
        case "event":
          return {
            surface: "lab",
            target,
            actionName: "open-events-workbench",
            uri,
            labRoute: { workbench: "events", runId: target.runId, selectedEventSeq: target.seq },
          };
        case "artifact":
          return {
            surface: "lab",
            target,
            actionName: "open-artifacts-workbench",
            uri,
            labRoute: { workbench: "artifacts", artifactDigest: target.digest },
          };
        case "approval":
          return {
            surface: "lab",
            target,
            actionName: "open-approval-inspector",
            uri,
            labRoute: { workbench: "events" },
          };
        case "trace":
          return {
            surface: "lab",
            target,
            actionName: "open-trace-workbench",
            uri,
            labRoute: { workbench: "trace", runId: target.runId, selectedNodeId: target.nodeId },
          };
        case "context":
          return {
            surface: "lab",
            target,
            actionName: "open-context-workbench",
            uri,
            labRoute: { workbench: "context" },
          };
      }
    }

    case "tui": {
      switch (target.kind) {
        case "run":
          return {
            surface: "tui",
            target,
            actionName: "attach-run",
            uri,
            tuiAction: { focus: "transcript", runId: target.runId },
          };
        case "event":
          return {
            surface: "tui",
            target,
            actionName: "view-event",
            uri,
            tuiAction: { focus: "transcript", runId: target.runId },
          };
        case "artifact":
          return {
            surface: "tui",
            target,
            actionName: "view-artifact",
            uri,
            tuiAction: { modal: "diff-viewer" },
          };
        case "approval":
          return {
            surface: "tui",
            target,
            actionName: "focus-approval-deck",
            uri,
            tuiAction: { focus: "approval" },
          };
        case "trace":
          return {
            surface: "tui",
            target,
            actionName: "view-trace",
            uri,
            tuiAction: { focus: "transcript" },
          };
        case "context":
          return {
            surface: "tui",
            target,
            actionName: "view-context",
            uri,
            tuiAction: { focus: "transcript" },
          };
      }
    }

    case "cli": {
      switch (target.kind) {
        case "run":
          return {
            surface: "cli",
            target,
            actionName: "cli-run",
            uri,
            cliCommand: `vg run --attach ${target.runId}`,
          };
        case "event":
          return {
            surface: "cli",
            target,
            actionName: "cli-event",
            uri,
            cliCommand: `vg event inspect --run ${target.runId} --seq ${target.seq}`,
          };
        case "artifact":
          return {
            surface: "cli",
            target,
            actionName: "cli-artifact",
            uri,
            cliCommand: `vg artifact explain ${target.digest}`,
          };
        case "approval":
          return {
            surface: "cli",
            target,
            actionName: "cli-approve",
            uri,
            cliCommand: `vg approve --id ${target.approvalId}`,
          };
        case "trace":
          return {
            surface: "cli",
            target,
            actionName: "cli-trace",
            uri,
            cliCommand: `vg lineage ${target.runId}`,
          };
        case "context":
          return {
            surface: "cli",
            target,
            actionName: "cli-context",
            uri,
            cliCommand: "vg doctor",
          };
      }
    }
  }
}

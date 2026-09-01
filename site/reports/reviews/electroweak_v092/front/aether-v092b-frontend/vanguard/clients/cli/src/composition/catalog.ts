import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";

export const DEMO_SCENARIOS = [
  "successful-episode",
  "authorization-denied",
  "approval-pending-resolved",
  "cancel-requested-confirmed",
  "checkpoint-requested-confirmed",
  "stream-interrupt-reconnect",
  "resume-from-checkpoint",
  "effect-failed-undeterminable",
  "unknown-future-event",
  "why-artifact-active-inactive-unknown",
  "why-typed-tools",
] as const;

export type DemoScenario = (typeof DEMO_SCENARIOS)[number];

export function packageRootFrom(url: string): string {
  let dir = dirname(fileURLToPath(url));
  while (!existsSync(join(dir, "package.json"))) {
    const parent = dirname(dir);
    if (parent === dir) throw new Error("package root not found");
    dir = parent;
  }
  return dir;
}

export function demoFixturePath(root: string, scenario: string): string {
  const sessions = join(root, "fixtures", "sessions", `${scenario}.jsonl`);
  if (existsSync(sessions)) return sessions;
  const legacy = join(root, "fixtures", `${scenario}.jsonl`);
  if (existsSync(legacy)) return legacy;
  return sessions;
}

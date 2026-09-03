import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import type { AgentDescriptor } from "@aether/contracts";
import { ProductPaths } from "./paths.js";

export const HARNESS_ALIASES: Readonly<Record<string, string>> = {
  "coding-agent": "vg-code-default",
  "research-agent": "vg-research-minimal",
  "review-agent": "vg-code-critic-reviser",
};

export const DEFAULT_PRODUCT_HARNESS = "vg-code-balanced";

export type AgentCatalogEntry = {
  readonly id: string;
  readonly role: string;
  readonly undeletable: boolean;
  readonly capabilityVerbs: readonly string[];
  readonly budgetPolicy?: string;
};

type RegistryEntry = {
  name: string;
  path: string;
  undeletable?: boolean;
  role?: string;
};

type RegistryFile = {
  manifests: RegistryEntry[];
};

type ManifestFile = {
  capabilities?: { verb: string }[];
  budgetPolicy?: string;
  undeletable?: boolean;
};

export function canonicalHarnessId(agentId: string): string {
  const trimmed = agentId.trim();
  return HARNESS_ALIASES[trimmed] ?? trimmed;
}

export function executionProfileFor(planMode: boolean): "plan" | "local" {
  return planMode ? "plan" : "local";
}

/**
 * Resolve the agency manifests directory: env override, then walk up from cwd
 * looking for the in-repo registry, then the packaged app root.
 */
export function resolveManifestsDir(cwd: string = process.cwd()): string | null {
  const envRoot = process.env.VANGUARD_ROOT ?? process.env.AETHER_REPO_ROOT ?? process.env.AETHER_HOME;
  if (envRoot) {
    const candidate = join(envRoot, "vanguard/packages/agency/manifests");
    if (existsSync(join(candidate, "registry.json"))) return candidate;
  }

  let dir = cwd;
  for (let i = 0; i < 32; i++) {
    if (existsSync(join(dir, ".vanguard/workspace.toml"))) {
      const candidate = join(dir, "vanguard/packages/agency/manifests");
      if (existsSync(join(candidate, "registry.json"))) return candidate;
    }
    const candidate = join(dir, "vanguard/packages/agency/manifests");
    if (existsSync(join(candidate, "registry.json"))) return candidate;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  try {
    const appRoot = ProductPaths.resolveLayout().appRoot;
    const packaged = join(appRoot, "vanguard/packages/agency/manifests");
    if (existsSync(join(packaged, "registry.json"))) return packaged;
  } catch {
    /* ignore */
  }
  return null;
}

export function loadAgentCatalog(manifestsDir: string | null = resolveManifestsDir()): AgentCatalogEntry[] {
  if (!manifestsDir) return [];

  const registryPath = join(manifestsDir, "registry.json");
  if (!existsSync(registryPath)) return [];

  const registry = JSON.parse(readFileSync(registryPath, "utf-8")) as RegistryFile;
  const entries: AgentCatalogEntry[] = [];

  for (const entry of registry.manifests ?? []) {
    const manifestPath = join(manifestsDir, entry.path);
    let manifest: ManifestFile = {};
    if (existsSync(manifestPath)) {
      try {
        manifest = JSON.parse(readFileSync(manifestPath, "utf-8")) as ManifestFile;
      } catch {
        manifest = {};
      }
    }

    entries.push({
      id: entry.name,
      role: entry.role ?? "unknown",
      undeletable: entry.undeletable ?? manifest.undeletable ?? false,
      capabilityVerbs: (manifest.capabilities ?? []).map((c) => c.verb),
      budgetPolicy: manifest.budgetPolicy,
    });
  }

  return entries;
}

export function canWrite(entry: AgentCatalogEntry): boolean {
  return entry.capabilityVerbs.some((v) => v === "patch.apply" || v === "proc.exec");
}

export function resolveHarnessManifestPath(
  agentId: string,
  workspacePath: string = process.cwd(),
): string | undefined {
  const name = canonicalHarnessId(agentId);
  const manifestsDir = resolveManifestsDir(workspacePath) ?? resolveManifestsDir(process.cwd());
  if (!manifestsDir) return undefined;
  const path = join(manifestsDir, name, "manifest.json");
  return existsSync(path) ? path : undefined;
}

export function descriptorsFromCatalog(entries: AgentCatalogEntry[], manifestsDir: string | null): AgentDescriptor[] {
  return entries.map((entry) => ({
    id: entry.id,
    name: entry.id,
    description: `${entry.role}${entry.capabilityVerbs.length ? ` • ${entry.capabilityVerbs.slice(0, 6).join(", ")}` : ""}`,
    validationStatus: "valid",
    modelSummary: "",
    toolSummary: [...entry.capabilityVerbs],
    capabilitySummary: entry.budgetPolicy ? [entry.budgetPolicy] : [],
    manifestPath: manifestsDir ? join(manifestsDir, entry.id, "manifest.json") : entry.id,
  }));
}

export function mergeAgentCatalog(
  fallback: readonly AgentDescriptor[],
  workspacePath: string,
): AgentDescriptor[] {
  const dir = resolveManifestsDir(workspacePath);
  const catalog = loadAgentCatalog(dir);
  const fromDisk = descriptorsFromCatalog(catalog, dir);
  if (fromDisk.length === 0) return [...fallback];
  const seen = new Set(fromDisk.map((a) => a.id));
  const extras = fallback.filter((a) => !seen.has(a.id));
  return [...fromDisk, ...extras];
}

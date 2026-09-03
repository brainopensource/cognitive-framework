import { existsSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";

export interface AgentCatalogEntry {
  readonly id: string;
  readonly role: string;
  readonly undeletable: boolean;
  /** Capability verbs declared on the manifest ceiling, e.g. fs.read, patch.apply. */
  readonly capabilityVerbs: readonly string[];
  readonly budgetPolicy?: string;
}

interface RegistryEntry {
  name: string;
  path: string;
  undeletable?: boolean;
  role?: string;
}

interface RegistryFile {
  manifests: RegistryEntry[];
}

interface ManifestCapability {
  verb: string;
}

interface ManifestFile {
  capabilities?: ManifestCapability[];
  budgetPolicy?: string;
  undeletable?: boolean;
}

/**
 * Resolves the manifest registry directory: explicit env override first, then
 * walking up from cwd looking for .vanguard/workspace.toml, then the
 * in-repo default under vanguard/packages/agency/manifests.
 */
export function resolveManifestsDir(cwd: string = process.cwd()): string | null {
  const envRoot = process.env.VANGUARD_ROOT ?? process.env.AETHER_REPO_ROOT;
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

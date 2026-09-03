import { existsSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";

export class ModelPolicyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ModelPolicyError";
  }
}

export interface ModelCatalogEntry {
  readonly id: string;
  readonly tier: number;
  readonly free: boolean;
}

export interface ModelCatalog {
  readonly defaultModel: string;
  readonly defaultPaidModel: string;
  readonly aliases: Readonly<Record<string, string>>;
  readonly entries: readonly ModelCatalogEntry[];
}

interface ModelsRegistryFile {
  default_model: string;
  default_paid_model: string;
  aliases?: Record<string, string>;
  tiers: Record<string, string[]>;
}

export function resolveModelsRegistryPath(cwd: string = process.cwd()): string | null {
  const envRoot = process.env.VANGUARD_ROOT ?? process.env.AETHER_REPO_ROOT;
  if (envRoot) {
    const candidate = join(envRoot, "vanguard/packages/adapters/models/models_registry.json");
    if (existsSync(candidate)) return candidate;
  }

  let dir = cwd;
  for (let i = 0; i < 32; i++) {
    const candidate = join(dir, "vanguard/packages/adapters/models/models_registry.json");
    if (existsSync(candidate)) return candidate;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

function isFreeModelId(id: string): boolean {
  return id.endsWith(":free") || id === "openrouter/free";
}

/**
 * Loads the model registry as the source of truth for /model. Throws
 * ModelPolicyError, rather than silently returning an empty catalog, so a
 * missing/unreadable registry fails closed instead of letting hardcoded
 * model names slip through unvalidated.
 */
export function loadModelCatalog(registryPath: string | null = resolveModelsRegistryPath()): ModelCatalog {
  if (!registryPath) {
    throw new ModelPolicyError("models_registry.json not found; refusing to fabricate a model catalog");
  }

  let raw: ModelsRegistryFile;
  try {
    raw = JSON.parse(readFileSync(registryPath, "utf-8")) as ModelsRegistryFile;
  } catch (err) {
    throw new ModelPolicyError(`Failed to read model registry at ${registryPath}: ${(err as Error).message}`);
  }

  const entries: ModelCatalogEntry[] = [];
  for (const [tierStr, ids] of Object.entries(raw.tiers ?? {})) {
    const tier = Number(tierStr);
    for (const id of ids) {
      entries.push({ id, tier, free: isFreeModelId(id) });
    }
  }

  return {
    defaultModel: raw.default_model,
    defaultPaidModel: raw.default_paid_model,
    aliases: raw.aliases ?? {},
    entries,
  };
}

/**
 * Validates a requested model id/alias against the registry. Returns the
 * resolved canonical model id, or throws ModelPolicyError if it is not a
 * known model, tier alias, or if it is a paid model and VANGUARD_ALLOW_PAID
 * is unset.
 */
export function resolveModelSelection(
  requested: string,
  catalog: ModelCatalog,
  env: NodeJS.ProcessEnv = process.env
): string {
  const aliased = catalog.aliases[requested] ?? requested;
  const entry = catalog.entries.find((e) => e.id === aliased);
  if (!entry) {
    throw new ModelPolicyError(`Unknown model or alias: "${requested}"`);
  }
  if (!entry.free && !env.VANGUARD_ALLOW_PAID) {
    throw new ModelPolicyError(
      `"${entry.id}" is a paid model; set VANGUARD_ALLOW_PAID=1 to select it`
    );
  }
  return entry.id;
}

export function groupByTier(catalog: ModelCatalog): Map<number, ModelCatalogEntry[]> {
  const groups = new Map<number, ModelCatalogEntry[]>();
  for (const entry of catalog.entries) {
    const list = groups.get(entry.tier) ?? [];
    list.push(entry);
    groups.set(entry.tier, list);
  }
  return groups;
}

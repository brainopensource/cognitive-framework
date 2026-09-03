import { jcsCanonicalize } from "@aether/contracts";

export type AgentDefinition = {
  schemaVersion: "aether.agent-definition/1";
  name: string;
  description: string;
  model: { router: string; temperature: number; maxTokens: number; reasoningEffort: "low" | "medium" | "high" };
  systemPrompt: string;
  skills: string[];
  context: { strategy: string; retrieval: string[] };
  memory: { policy: string; scopes: string[] };
  tools: string[];
  plugins: string[];
  budget: { usdMicros: number; tokens: number; timeoutMs: number; maxDepth: number; maxTurns: number };
  approvalPolicy: { mode: "always" | "governed-effects" | "never"; editable: boolean };
  planner: { policy: string };
  recoveryPolicy: { policy: string; maxRetries: number };
  verifier: { policy: string; exteriorRequired: boolean };
  completionGate: { policy: string; requireVerification: boolean };
  subagents: Array<{ role: string; agentRef: string; grant: string[] }>;
  topology: { kind: string; channels: Array<{ from: string; to: string; protocol: string }> };
};

export type AgentManifest = Readonly<AgentDefinition & {
  manifestVersion: "mhf.manifest/2";
}>;

export type ValidationIssue = { path: string; code: string; message: string };

export type CompositionDelta = {
  baseDigest: string;
  childRole: string;
  changes: Partial<Pick<AgentDefinition, "model" | "skills" | "tools" | "budget" | "approvalPolicy" | "planner" | "recoveryPolicy" | "verifier" | "completionGate" | "topology">>;
  disposition: "discard" | "rollback" | "propose-promotion";
};

export function validateAgentDefinition(value: AgentDefinition): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const required = (path: string, input: string) => {
    if (!input.trim()) issues.push({ path, code: "required", message: `${path} must not be empty` });
  };
  required("name", value.name);
  required("model.router", value.model.router);
  required("systemPrompt", value.systemPrompt);
  required("planner.policy", value.planner.policy);
  required("verifier.policy", value.verifier.policy);
  required("completionGate.policy", value.completionGate.policy);
  if (!/^[a-z0-9][a-z0-9._-]*$/i.test(value.name)) issues.push({ path: "name", code: "invalid_format", message: "name must be a stable identifier" });
  if (value.model.temperature < 0 || value.model.temperature > 2) issues.push({ path: "model.temperature", code: "out_of_range", message: "temperature must be between 0 and 2" });
  for (const [key, amount] of Object.entries(value.budget)) {
    if (!Number.isSafeInteger(amount) || amount < 0) issues.push({ path: `budget.${key}`, code: "invalid_budget", message: `${key} must be a non-negative safe integer` });
  }
  const uniqueLists: Array<[string, string[]]> = [["skills", value.skills], ["tools", value.tools], ["plugins", value.plugins]];
  for (const [path, items] of uniqueLists) {
    if (new Set(items).size !== items.length) issues.push({ path, code: "duplicate", message: `${path} must not contain duplicates` });
  }
  if (value.approvalPolicy.mode === "never" && value.tools.some((tool) => tool === "fs.patch" || tool === "proc.exec")) {
    issues.push({ path: "approvalPolicy.mode", code: "unsafe_policy", message: "governed effects require an approval policy" });
  }
  return issues;
}

function normalized(definition: AgentDefinition): AgentDefinition {
  return {
    ...definition,
    skills: [...definition.skills].sort(),
    tools: [...definition.tools].sort(),
    plugins: [...definition.plugins].sort(),
    context: { ...definition.context, retrieval: [...definition.context.retrieval].sort() },
    memory: { ...definition.memory, scopes: [...definition.memory.scopes].sort() },
    subagents: [...definition.subagents].map((item) => ({ ...item, grant: [...item.grant].sort() })).sort((a, b) => a.role.localeCompare(b.role)),
    topology: { ...definition.topology, channels: [...definition.topology.channels].sort((a, b) => jcsCanonicalize(a).localeCompare(jcsCanonicalize(b))) },
  };
}

export function compileManifest(definition: AgentDefinition): AgentManifest {
  const issues = validateAgentDefinition(definition);
  if (issues.length) throw new Error(issues.map((issue) => `${issue.path}: ${issue.message}`).join("\n"));
  return deepFreeze({ ...normalized(definition), manifestVersion: "mhf.manifest/2" as const });
}

function deepFreeze<T>(value: T): T {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}

export function canonicalManifestJson(manifest: AgentManifest): string {
  return jcsCanonicalize(manifest);
}

export async function compositionDigest(manifest: AgentManifest): Promise<string> {
  const bytes = new TextEncoder().encode(canonicalManifestJson(manifest));
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return `sha256:${Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("")}`;
}

export function generateAaaCSource(definition: AgentDefinition): string {
  const canonicalDefinition = jcsCanonicalize(normalized(definition));
  return `"""Generated Agent-as-a-Code definition. Pure construction; no effects."""\n` +
    `import json\n` +
    `from copy import deepcopy\n\n` +
    `AGENT_DEFINITION = json.loads(${JSON.stringify(canonicalDefinition)})\n\n` +
    `def build_composition_request():\n` +
    `    """Return data for the canonical runtime composition path."""\n` +
    `    return {"schema": "aether.composition-request/1", "agentDefinition": deepcopy(AGENT_DEFINITION)}\n`;
}

export function applyCompositionDelta(base: AgentDefinition, delta: CompositionDelta): AgentDefinition {
  if (!/^sha256:[0-9a-f]{64}$/.test(delta.baseDigest)) throw new Error("delta.baseDigest must bind an exact composition");
  if (!delta.childRole.trim()) throw new Error("delta.childRole is required");
  const child = normalized({ ...base, ...delta.changes, name: `${base.name}.${delta.childRole}` });
  const issues = validateAgentDefinition(child);
  if (issues.length) throw new Error(issues.map((issue) => `${issue.path}: ${issue.message}`).join("\n"));
  return child;
}

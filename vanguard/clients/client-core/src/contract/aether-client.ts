// AUTO-GENERATED: AETHER frontend SDK expansion (Phase F0)

import type { CommandReceipt, Result, RunRef, RunSnapshot, StartRunRequest } from "./types.js";
import type { StreamMessage, StreamCursor } from "./stream-protocol.js";

export type SystemHealth = Readonly<{ status: string; version: string }>;
export type CompatibilityInfo = Readonly<{ compatible: boolean; minClientVersion: string }>;
export type SchemaDef = Readonly<{ schemaId: string; definition: unknown }>;

export type CompositionRef = Readonly<{ compositionId: string; version: string }>;
export type CompositionSummary = Readonly<{ compositionId: string; name: string }>;
export type CompositionDetail = Readonly<{ compositionId: string; definition: unknown }>;

export type AgentRef = Readonly<{ agentId: string; version: string }>;
export type AgentSummary = Readonly<{ agentId: string; name: string }>;
export type AgentDetail = Readonly<{ agentId: string; description: string; definition: unknown }>;

export type ArtifactSummary = Readonly<{ artifactId: string; type: string }>;
export type ArtifactDetail = Readonly<{ artifactId: string; content: unknown }>;

export interface SystemClient {
  health(signal?: AbortSignal): Promise<Result<SystemHealth>>;
  compatibility(clientVersion: string, signal?: AbortSignal): Promise<Result<CompatibilityInfo>>;
  schemas(signal?: AbortSignal): Promise<Result<ReadonlyArray<SchemaDef>>>;
}

export interface CompositionClient {
  list(signal?: AbortSignal): Promise<Result<ReadonlyArray<CompositionSummary>>>;
  get(compositionId: string, signal?: AbortSignal): Promise<Result<CompositionDetail>>;
  validate(definition: unknown, signal?: AbortSignal): Promise<Result<{ valid: boolean; errors?: string[] }>>;
  freeze(compositionId: string, signal?: AbortSignal): Promise<Result<CompositionRef>>;
  diff(baseId: string, targetId: string, signal?: AbortSignal): Promise<Result<{ diff: unknown }>>;
  activate(compositionId: string, signal?: AbortSignal): Promise<Result<{ activated: boolean }>>;
}

export interface AgentCatalogClient {
  list(signal?: AbortSignal): Promise<Result<ReadonlyArray<AgentSummary>>>;
  get(agentId: string, signal?: AbortSignal): Promise<Result<AgentDetail>>;
  validate(definition: unknown, signal?: AbortSignal): Promise<Result<{ valid: boolean; errors?: string[] }>>;
  freeze(agentId: string, signal?: AbortSignal): Promise<Result<AgentRef>>;
}

export interface RunClient {
  start(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  streamEvents(runId: string, cursor?: StreamCursor, signal?: AbortSignal): AsyncIterable<Result<StreamMessage>>;
  get(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  cancel(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  checkpoint(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  resume(runId: string, checkpointId?: string, signal?: AbortSignal): Promise<Result<RunRef>>;
  inspect(runId: string, signal?: AbortSignal): Promise<Result<{ details: unknown }>>;
  export(runId: string, signal?: AbortSignal): Promise<Result<{ data: unknown }>>;
}

export interface ArtifactClient {
  list(runId: string, signal?: AbortSignal): Promise<Result<ReadonlyArray<ArtifactSummary>>>;
  get(artifactId: string, signal?: AbortSignal): Promise<Result<ArtifactDetail>>;
  verify(artifactId: string, signature: string, signal?: AbortSignal): Promise<Result<{ verified: boolean }>>;
  preview(artifactId: string, signal?: AbortSignal): Promise<Result<{ url: string }>>;
}

export interface ExperimentClient {
  stubbed(): void;
}

export interface SkillClient {
  stubbed(): void;
}

export interface GovernanceClient {
  stubbed(): void;
}

export interface AetherClient {
  readonly system: SystemClient;
  readonly compositions: CompositionClient;
  readonly agents: AgentCatalogClient;
  readonly runs: RunClient;
  readonly artifacts: ArtifactClient;
  readonly experiments: ExperimentClient;
  readonly skills: SkillClient;
  readonly governance: GovernanceClient;
}

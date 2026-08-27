// AUTO-GENERATED: AETHER frontend SDK expansion (Phase F0)

import type { EventEnvelope } from "./types.js";

export type StreamCursor = string;

export type ProjectionDelta = Readonly<{
  baseVersion: string;
  newVersion: string;
  patch: unknown;
}>;

export type TelemetrySample = Readonly<{
  metricName: string;
  value: number;
  labels: Readonly<Record<string, string>>;
  timestamp: string;
}>;

export type StreamControl =
  | { type: "heartbeat" }
  | { type: "resync_required"; reason: string }
  | { type: "schema_change"; newVersion: string }
  | { type: "retention_gap"; skippedEvents: number };

export type StreamMessage =
  | { channel: "event"; cursor: StreamCursor; event: EventEnvelope }
  | { channel: "projection"; cursor: StreamCursor; projection: ProjectionDelta }
  | { channel: "telemetry"; cursor: StreamCursor; sample: TelemetrySample }
  | { channel: "control"; cursor: StreamCursor; message: StreamControl };

export function isStreamGap(message: StreamMessage): boolean {
  return message.channel === "control" && message.message.type === "retention_gap";
}

export function isResyncRequired(message: StreamMessage): boolean {
  return message.channel === "control" && message.message.type === "resync_required";
}

import { existsSync } from "node:fs";
import type { EventCursor, Result, StreamItem } from "@aether/contracts";

export function resolveSocketPath(explicit?: string): string {
  if (explicit) return explicit;
  if (process.env.AETHER_RUNTIME_SOCKET) return process.env.AETHER_RUNTIME_SOCKET;
  if (process.env.VANGUARD_RUNTIME_SOCKET) return process.env.VANGUARD_RUNTIME_SOCKET;
  if (existsSync("/tmp/aether-runtime.sock")) return "/tmp/aether-runtime.sock";
  if (existsSync("/tmp/vanguard-runtime.sock")) return "/tmp/vanguard-runtime.sock";
  return "/tmp/vanguard-runtime.sock";
}

export interface RuntimeTransport {
  readonly kind: "feed" | "socket" | "http";
  sendCommand<T>(
    name: string,
    payload: Record<string, unknown>,
    runId: string,
    actor?: string
  ): Promise<Result<T>>;
  streamItems(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
}

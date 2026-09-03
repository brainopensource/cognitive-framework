import type { ClientFailure, EventCursor, RuntimeClient, StreamItem } from "../contract/types.js";

export async function subscribeRun(
  client: Pick<RuntimeClient, "streamEvents">,
  cursor: EventCursor,
  handlers: {
    onItem: (item: StreamItem) => void;
    onError?: (error: ClientFailure) => void;
    onDone?: () => void;
  },
  signal?: AbortSignal
): Promise<void> {
  if (signal?.aborted) return;
  try {
    for await (const result of client.streamEvents(cursor, signal)) {
      if (signal?.aborted) break;
      if (!result.ok) {
        handlers.onError?.(result.error);
      } else {
        handlers.onItem(result.value);
      }
    }
  } catch (err) {
    if (!signal?.aborted) {
      handlers.onError?.({
        code: "transport_interrupted",
        message: err instanceof Error ? err.message : String(err),
        retryable: true,
      });
    }
  } finally {
    if (!signal?.aborted) {
      handlers.onDone?.();
    }
  }
}

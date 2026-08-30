import type { EventEnvelope } from "@aether/contracts";

export function reconcileOfflineStream(
  existingEvents: EventEnvelope[],
  incomingEvents: EventEnvelope[],
  afterSeq?: string
): EventEnvelope[] {
  const seenKeys = new Set<string>();
  const combined: EventEnvelope[] = [];

  const addEvent = (env: EventEnvelope) => {
    // Unique key combines runId, seq, and eventId
    const key = `${env.runId ?? ""}:${env.seq ?? ""}:${env.eventId ?? ""}`;
    if (!seenKeys.has(key)) {
      seenKeys.add(key);
      combined.push(env);
    }
  };

  for (const env of existingEvents) {
    addEvent(env);
  }

  const cursorNum = afterSeq ? Number(afterSeq) : -1;

  for (const env of incomingEvents) {
    const seqNum = Number(env.seq ?? "0");
    if (cursorNum >= 0 && seqNum <= cursorNum) {
      // Check if already present, otherwise allow if valid
      addEvent(env);
    } else {
      addEvent(env);
    }
  }

  // Sort deterministically by sequence number
  combined.sort((a, b) => {
    const seqA = BigInt(a.seq || "0");
    const seqB = BigInt(b.seq || "0");
    if (seqA < seqB) return -1;
    if (seqA > seqB) return 1;
    return a.eventId.localeCompare(b.eventId);
  });

  return combined;
}

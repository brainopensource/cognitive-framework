import type { TimelineEntry } from "../components/event-timeline.js";

export function useEventTimeline(events: readonly any[]): TimelineEntry[] {
  return events.map((e) => ({
    seq: e.seq ?? "",
    kind: e.event?.kind ?? "unknown",
    lineageId: e.lineageId,
    writer: e.writer,
    summary: e.event?.summary ?? "Event",
    status: "committed",
  }));
}

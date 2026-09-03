import {
  windowTranscript,
  type TranscriptRow,
} from "@aether/client";

export { windowTranscript, type TranscriptRow };

export const DEFAULT_TRANSCRIPT_HEIGHT = 16;

export function moveTranscriptCursor(
  cursor: number,
  total: number,
  height: number,
  delta: number
): number {
  const h = Math.max(1, height);
  const maxCursor = Math.max(0, total - h);
  return Math.min(Math.max(0, cursor + delta), maxCursor);
}

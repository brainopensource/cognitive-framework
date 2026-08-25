import type { TrajectorySpan } from "../store/fold.js";

export type SpanLayoutNode = {
  readonly span: TrajectorySpan;
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly depth: number;
};

export type WaterfallLayout = {
  readonly nodes: readonly SpanLayoutNode[];
  readonly totalWidth: number;
  readonly totalHeight: number;
  readonly minMs: number;
  readonly maxMs: number;
};

export const DEFAULT_ROW_HEIGHT = 24;
export const MIN_SPAN_WIDTH_PX = 4;

export function computeWaterfallLayout(
  spans: readonly TrajectorySpan[],
  canvasWidth: number = 800,
  rowHeight: number = DEFAULT_ROW_HEIGHT
): WaterfallLayout {
  if (spans.length === 0) {
    return {
      nodes: [],
      totalWidth: canvasWidth,
      totalHeight: rowHeight,
      minMs: 0,
      maxMs: 1000,
    };
  }

  let minMs = spans[0]!.startMs;
  let maxMs = spans[0]!.endMs;

  for (const s of spans) {
    if (s.startMs < minMs) minMs = s.startMs;
    if (s.endMs > maxMs) maxMs = s.endMs;
  }

  const durationRange = Math.max(1, maxMs - minMs);
  const scale = (canvasWidth - 20) / durationRange;

  const nodes: SpanLayoutNode[] = [];
  let maxDepth = 0;

  for (let i = 0; i < spans.length; i++) {
    const s = spans[i]!;
    const x = Math.max(0, (s.startMs - minMs) * scale + 10);
    const rawW = s.durationMs * scale;
    const width = Math.max(rawW, MIN_SPAN_WIDTH_PX);
    const depth = s.depth;
    if (depth > maxDepth) maxDepth = depth;
    const y = i * (rowHeight + 2);

    nodes.push({
      span: s,
      x,
      y,
      width,
      height: rowHeight,
      depth,
    });
  }

  return {
    nodes,
    totalWidth: canvasWidth,
    totalHeight: Math.max(rowHeight * 2, spans.length * (rowHeight + 2)),
    minMs,
    maxMs,
  };
}

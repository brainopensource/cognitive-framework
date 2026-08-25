import React, { useMemo } from "react";
import type { TrajectorySpan } from "../store/fold.js";
import { computeWaterfallLayout } from "../render/waterfall-layout.js";

export type TrajectoryWaterfallProps = {
  readonly spans: readonly TrajectorySpan[];
  readonly selectedSpanId?: string;
  readonly onSelectSpan?: (spanId: string) => void;
  readonly width?: number;
};

export const TrajectoryWaterfall: React.FC<TrajectoryWaterfallProps> = ({
  spans,
  selectedSpanId,
  onSelectSpan,
  width = 700,
}) => {
  const layout = useMemo(() => computeWaterfallLayout(spans, width), [spans, width]);

  if (spans.length === 0) {
    return (
      <div style={{ padding: 16, color: "var(--text-muted)", fontSize: 12 }}>
        No trajectory spans recorded yet.
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 11, color: "var(--text-muted)" }}>
        <span>Trajectory Waterfall ({spans.length} spans)</span>
        <span>Window: {layout.maxMs - layout.minMs} ms</span>
      </div>

      <div
        style={{
          position: "relative",
          width: "100%",
          height: layout.totalHeight,
          background: "var(--bg-canvas)",
          border: "1px solid var(--border-subtle)",
          borderRadius: 6,
          overflow: "hidden",
        }}
      >
        {layout.nodes.map((node) => {
          const isSelected = node.span.spanId === selectedSpanId;
          let bg = "var(--signal-flow)";
          if (node.span.outcome === "denied") bg = "var(--signal-deny)";
          else if (node.span.outcome === "undeterminable") bg = "var(--signal-void)";
          else if (node.span.outcome === "failed") bg = "var(--signal-deny)";
          else if (node.span.outcome === "satisfied") bg = "var(--signal-proof)";

          return (
            <div
              key={node.span.spanId}
              onClick={() => onSelectSpan && onSelectSpan(node.span.spanId)}
              title={`${node.span.name} (${node.span.durationMs}ms)`}
              style={{
                position: "absolute",
                left: node.x,
                top: node.y,
                width: node.width,
                height: node.height,
                background: bg,
                opacity: isSelected ? 1 : 0.8,
                border: isSelected ? "2px solid #fff" : "1px solid rgba(0,0,0,0.3)",
                borderRadius: 3,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                paddingLeft: 4,
                overflow: "hidden",
                fontSize: 10,
                color: "#000",
                fontWeight: "bold",
                whiteSpace: "nowrap",
              }}
            >
              {node.width > 40 && node.span.name}
            </div>
          );
        })}
      </div>
    </div>
  );
};

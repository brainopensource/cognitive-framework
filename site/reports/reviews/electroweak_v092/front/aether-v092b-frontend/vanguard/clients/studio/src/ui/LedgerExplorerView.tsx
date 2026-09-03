import React, { useMemo } from "react";
import type { InternedRow } from "../store/event-store.js";

export type LedgerExplorerProps = {
  readonly rows: readonly InternedRow[];
  readonly filterQuery: string;
  readonly onFilterChange: (query: string) => void;
};

export const LedgerExplorerView: React.FC<LedgerExplorerProps> = ({
  rows,
  filterQuery,
  onFilterChange,
}) => {
  const filteredRows = useMemo(() => {
    if (!filterQuery.trim()) return rows;
    const q = filterQuery.toLowerCase();
    return rows.filter((r) => {
      const kind = String(r.envelope.payload?.kind ?? "").toLowerCase();
      const seq = String(r.seq);
      const span = r.spanId.toLowerCase();
      return kind.includes(q) || seq.includes(q) || span.includes(q);
    });
  }, [rows, filterQuery]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 14, color: "var(--text-primary)" }}>
            Ledger Explorer (⌘7 Query Surface)
          </h3>
          <p style={{ margin: "4px 0 0 0", fontSize: 12, color: "var(--text-muted)" }}>
            Schema-derived, redaction-aware event query engine with server cursor compatibility.
          </p>
        </div>

        <input
          type="text"
          value={filterQuery}
          onChange={(e) => onFilterChange(e.target.value)}
          placeholder="Filter kind, seq, spanId..."
          style={{
            background: "var(--bg-panel)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 4,
            padding: "6px 12px",
            color: "var(--text-primary)",
            fontSize: 12,
            fontFamily: "var(--font-mono)",
            width: 240,
          }}
        />
      </div>

      <div
        style={{
          border: "1px solid var(--border-subtle)",
          borderRadius: 6,
          overflow: "hidden",
          background: "var(--bg-panel)",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, fontFamily: "var(--font-mono)" }}>
          <thead>
            <tr style={{ background: "var(--bg-card)", borderBottom: "1px solid var(--border-subtle)" }}>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 64 }}>Seq</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 180 }}>Event Kind</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 140 }}>Span ID</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 100 }}>Confidentiality</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 100 }}>Redaction</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)" }}>Payload Summary</th>
            </tr>
          </thead>
          <tbody>
            {filteredRows.slice(0, 100).map((row) => {
              const env = row.envelope;
              const kind = String(env.payload?.kind ?? "unknown");
              const isRedacted = env.redactionStatus && env.redactionStatus !== "none";

              return (
                <tr key={row.index} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                  <td style={{ padding: "6px 12px", color: "var(--text-muted)" }}>{row.seq.toString()}</td>
                  <td style={{ padding: "6px 12px", color: "var(--signal-flow)", fontWeight: "bold" }}>{kind}</td>
                  <td style={{ padding: "6px 12px", color: "var(--text-secondary)" }}>{env.spanId.slice(0, 8)}</td>
                  <td style={{ padding: "6px 12px", color: "var(--text-muted)" }}>{env.confidentiality}</td>
                  <td style={{ padding: "6px 12px", color: isRedacted ? "var(--signal-hold)" : "var(--text-muted)" }}>
                    {env.redactionStatus}
                  </td>
                  <td style={{ padding: "6px 12px", color: "var(--text-secondary)", fontSize: 11, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {JSON.stringify(env.payload)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

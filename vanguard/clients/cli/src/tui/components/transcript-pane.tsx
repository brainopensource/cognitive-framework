import React from "react";
import { Box, Text } from "ink";
import type { TranscriptRow } from "../transcript-window.js";

export function TranscriptPane({ rows, selected }: { rows: TranscriptRow[]; selected: number }) {
  return (
    <Box flexDirection="column" flexGrow={1} marginRight={1}>
      <Text dimColor>transcript</Text>
      {rows.length === 0 ? <Text dimColor>(empty)</Text> : rows.map((row, index) => {
        const mark = index === selected ? ">" : " ";
        if (row.kind === "thought") {
          return <Text key={`t-${index}`}>{mark} · {row.text}</Text>;
        }
        return <Text key={`tool-${index}`}>{mark} {row.name} [{row.status}]</Text>;
      })}
    </Box>
  );
}

import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export type ContextSource = {
  name: string;
  kind: string;
  tokens: number;
  selected: boolean;
};

export type ContextPanelProps = {
  sources: readonly ContextSource[];
  totalTokens: number;
  compacted: boolean;
  height: number;
};

export const ContextPanel: React.FC<ContextPanelProps> = (props) => {
  return (
    <Box flexDirection="column" height={props.height}>
      <Text color={theme.accent}>Context ({props.totalTokens} tokens) {props.compacted ? "[COMPACTED]" : ""}</Text>
      {props.sources.map(s => (
        <Text key={s.name} dimColor={!s.selected}>
          {s.selected ? "[x]" : "[ ]"} {s.name} ({s.tokens})
        </Text>
      ))}
    </Box>
  );
};

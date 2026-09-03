import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export type SidebarEntry = {
  id: string;
  label: string;
  kind: "run" | "agent" | "lineage" | "header";
  status?: string;
  depth?: number;
  selected?: boolean;
};

export type SidebarProps = {
  entries: readonly SidebarEntry[];
  selectedIndex: number;
  onSelect: (index: number) => void;
  width?: number;
};

export const Sidebar: React.FC<SidebarProps> = (props) => {
  const { entries, selectedIndex, width = 20 } = props;
  return (
    <Box flexDirection="column" width={width} borderStyle="single" borderRight>
      {entries.map((entry, idx) => {
        const isSelected = idx === selectedIndex;
        const indent = " ".repeat((entry.depth ?? 0) * 2);
        const prefix = isSelected ? "> " : "  ";
        return (
          <Box key={`${entry.id}-${idx}`}>
            <Text color={isSelected ? theme.accent : undefined} dimColor={entry.kind === "header"}>
              {prefix}{indent}{entry.label}
              {entry.status ? ` [${entry.status}]` : ""}
            </Text>
          </Box>
        );
      })}
    </Box>
  );
};

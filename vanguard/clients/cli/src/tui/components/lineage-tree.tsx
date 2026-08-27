import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export type LineageNode = {
  id: string;
  label: string;
  status: "running" | "completed" | "failed" | "cancelled";
  budget?: { used: string; total: string };
  children: readonly LineageNode[];
  depth: number;
};

export const LineageTree: React.FC<{ root?: LineageNode; height: number; onSelect: (id: string) => void }> = (props) => {
  if (!props.root) return <Box><Text>No Lineage</Text></Box>;
  
  const renderNode = (node: LineageNode) => {
    const indent = "  ".repeat(node.depth);
    return (
      <Box key={node.id} flexDirection="column">
        <Text>
          {indent}- {node.label} [{node.status}] {node.budget ? `(${node.budget.used}/${node.budget.total})` : ""}
        </Text>
        {node.children.map(child => renderNode(child))}
      </Box>
    );
  };
  return <Box flexDirection="column" height={props.height}>{renderNode(props.root)}</Box>;
};

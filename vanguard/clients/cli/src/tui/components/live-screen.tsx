import React from "react";
import { Box, Text } from "ink";
import type { RunViewModel } from "../../application/run-view.js";

export function LiveScreen({ view, repo }: { view: RunViewModel; repo: string }) {
  return (
    <Box flexDirection="column">
      <Text>
        repo: {repo}  tokens: {String(view.tokens)}  cost: {view.costMicros}µ
      </Text>
      <Text dimColor>thoughts</Text>
      {view.thoughts.length === 0 ? <Text dimColor>(none)</Text> : view.thoughts.slice(-6).map((thought) => <Text key={thought}>· {thought}</Text>)}
      <Text dimColor>tools</Text>
      {view.tools.length === 0 ? <Text dimColor>(none)</Text> : view.tools.slice(-6).map((tool, index) => <Text key={`${tool.name}-${index}`}>{tool.name} [{tool.status}]</Text>)}
    </Box>
  );
}

import React from "react";
import { Box, Text } from "ink";
import type { TuiMode } from "../focus.js";

export function PromptBar({
  mode,
  buffer,
  hints,
}: {
  mode: TuiMode;
  buffer: string;
  hints: string;
}) {
  const focused = mode === "prompt" || mode === "resume";
  return (
    <Box flexDirection="column">
      <Text>
        {focused ? ">" : " "} brief: {buffer}
        {focused ? "█" : ""}
      </Text>
      <Text dimColor>{hints}</Text>
    </Box>
  );
}

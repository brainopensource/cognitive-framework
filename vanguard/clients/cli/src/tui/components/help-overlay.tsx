import React from "react";
import { Box, Text } from "ink";
import { HELP_TEXT } from "../focus.js";

export function HelpOverlay() {
  return (
    <Box flexDirection="column" borderStyle="round" paddingX={1}>
      {HELP_TEXT.split("\n").map((line) => (
        <Text key={line}>{line}</Text>
      ))}
    </Box>
  );
}

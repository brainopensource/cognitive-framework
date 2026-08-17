import React from "react";
import { Box, Text } from "ink";

export function CorrectionPrompt() {
  return (
    <Box flexDirection="column" borderStyle="round" borderColor="magenta" paddingX={1}>
      <Text color="magenta" bold>CORRECTION TAXONOMY</Text>
      <Text>[d]efect  [s]tyle  [t]est  [e]curity  [a]rchitecture</Text>
      <Text dimColor>single keystroke · style/architecture stay repo-scoped</Text>
    </Box>
  );
}

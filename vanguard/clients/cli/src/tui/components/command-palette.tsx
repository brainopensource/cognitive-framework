import React, { useState } from "react";
import { Box, Text, useInput } from "ink";
import { theme } from "../theme/tokens.js";

export const CommandPalette: React.FC<{
  visible: boolean;
  onExecute: (command: string) => void;
  onDismiss: () => void;
  availableCommands: readonly string[];
}> = (props) => {
  const [query, setQuery] = useState("");

  useInput((input, key) => {
    if (!props.visible) return;
    if (key.escape) {
      props.onDismiss();
      setQuery("");
      return;
    }
    if (key.return) {
      props.onExecute(query);
      setQuery("");
      return;
    }
    if (key.backspace || key.delete) {
      setQuery(q => q.slice(0, -1));
      return;
    }
    setQuery(q => q + input);
  }, { isActive: props.visible });

  if (!props.visible) return null;

  return (
    <Box flexDirection="column" borderStyle="round" borderColor={theme.accent}>
      <Text>Type a command (Esc to cancel):</Text>
      <Text color={theme.accent}>{"> "}{query}</Text>
      <Box flexDirection="column">
        {props.availableCommands.filter(c => c.includes(query)).map(c => (
          <Text key={c} dimColor>{c}</Text>
        ))}
      </Box>
    </Box>
  );
};

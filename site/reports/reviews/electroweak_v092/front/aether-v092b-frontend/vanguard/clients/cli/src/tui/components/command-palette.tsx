import React, { useState } from "react";
import { Box, Text, useInput } from "ink";
import { theme } from "../theme/tokens.js";

export type PaletteCommand = {
  command: string;
  description: string;
};

export const DEFAULT_CLI_COMMANDS: PaletteCommand[] = [
  { command: "/checkpoint", description: "Create an immediate durable SQLite WAL checkpoint" },
  { command: "/resume", description: "Resume execution from historical checkpoint" },
  { command: "/cancel", description: "Gracefully abort in-flight agent run" },
  { command: "/help", description: "Display full interactive keyboard shortcut guide" },
  { command: "/doctor", description: "Run environment and sandbox diagnostic health check" },
  { command: "/quit", description: "Exit interactive TUI session" },
];

export const CommandPalette: React.FC<{
  visible: boolean;
  onExecute: (command: string) => void;
  onDismiss: () => void;
  availableCommands?: readonly (string | PaletteCommand)[];
}> = (props) => {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const rawCommands = props.availableCommands ?? DEFAULT_CLI_COMMANDS;
  const normalized: PaletteCommand[] = rawCommands.map((c) =>
    typeof c === "string" ? { command: c, description: "" } : c
  );

  const filtered = normalized.filter(
    (c) =>
      c.command.toLowerCase().includes(query.toLowerCase()) ||
      c.description.toLowerCase().includes(query.toLowerCase())
  );

  useInput(
    (input, key) => {
      if (!props.visible) return;
      if (key.escape) {
        props.onDismiss();
        setQuery("");
        setSelectedIndex(0);
        return;
      }
      if (key.downArrow) {
        setSelectedIndex((idx) => (idx + 1) % Math.max(1, filtered.length));
        return;
      }
      if (key.upArrow) {
        setSelectedIndex((idx) => (idx - 1 + filtered.length) % Math.max(1, filtered.length));
        return;
      }
      if (key.return) {
        const target = filtered[selectedIndex]?.command ?? query;
        props.onExecute(target);
        setQuery("");
        setSelectedIndex(0);
        return;
      }
      if (key.backspace || key.delete) {
        setQuery((q) => q.slice(0, -1));
        setSelectedIndex(0);
        return;
      }
      if (input && !key.ctrl && !key.meta) {
        setQuery((q) => q + input);
        setSelectedIndex(0);
      }
    },
    { isActive: props.visible }
  );

  if (!props.visible) return null;

  return (
    <Box flexDirection="column" borderStyle="round" borderColor={theme.accent} paddingX={1}>
      <Text bold color={theme.accent}>COMMAND PALETTE [Esc to cancel · ↑/↓ to navigate · Enter to run]</Text>
      <Box flexDirection="row" marginY={0}>
        <Text color={theme.accent} bold>{"> "}</Text>
        <Text>{query || " "}</Text>
      </Box>
      <Box flexDirection="column" marginTop={0}>
        {filtered.length === 0 ? (
          <Text dimColor>No matching commands</Text>
        ) : (
          filtered.slice(0, 6).map((c, idx) => {
            const isSelected = idx === selectedIndex;
            return (
              <Box key={c.command} flexDirection="row" justifyContent="space-between">
                <Text color={isSelected ? theme.accent : undefined} bold={isSelected}>
                  {isSelected ? "▶ " : "  "}
                  {c.command}
                </Text>
                {c.description ? (
                  <Text dimColor> · {c.description}</Text>
                ) : null}
              </Box>
            );
          })
        )}
      </Box>
    </Box>
  );
};

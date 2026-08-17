import React from "react";
import { Text } from "ink";
import { theme } from "../theme/tokens.js";
import { formatStatusBar } from "../status-bar.js";

export function StatusBar(props: {
  source: string;
  seq?: string;
  tokens: number;
  costMicros: string;
  kind: string;
}) {
  return <Text color={theme.accent} bold>{formatStatusBar(props)}</Text>;
}

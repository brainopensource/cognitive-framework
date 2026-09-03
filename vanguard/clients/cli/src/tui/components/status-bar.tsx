import React from "react";
import { Text } from "ink";
import { theme } from "../theme/tokens.js";
import { statusBarFromView } from "../status-bar.js";
import type { RunViewModel } from "@aether/client";
import type { StreamSource } from "@aether/contracts";

export function StatusBar(props: {
  view: RunViewModel;
  source: StreamSource | "unknown";
  lastSeq?: string;
  lastKind?: string;
}) {
  return (
    <Text color={theme.accent} bold>
      {statusBarFromView(props)}
    </Text>
  );
}

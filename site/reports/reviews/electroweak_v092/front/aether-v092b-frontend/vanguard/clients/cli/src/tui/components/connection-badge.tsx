import React from "react";
import { Text } from "ink";
import { sourceLabel } from "../theme/tokens.js";

export function ConnectionBadge({ source }: { source: string }) {
  const mock = source === "mock" || source === "replay";
  return <Text color={mock ? "yellow" : "green"}>{sourceLabel(source)}</Text>;
}

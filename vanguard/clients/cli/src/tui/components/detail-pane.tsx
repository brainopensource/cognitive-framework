import React from "react";
import { Box, Text } from "ink";
import type { PendingApproval } from "@vanguard/client-core";
import type { TuiMode } from "../focus.js";
import type { TranscriptRow } from "../transcript-window.js";
import { ApprovalModal } from "./approval-modal.js";
import { CorrectionPrompt } from "./correction-prompt.js";

export function DetailPane({
  mode,
  approval,
  selected,
  why,
}: {
  mode: TuiMode;
  approval?: PendingApproval;
  selected?: TranscriptRow;
  why?: string;
}) {
  return (
    <Box flexDirection="column" flexGrow={1}>
      <Text dimColor>detail</Text>
      {mode === "correct" ? <CorrectionPrompt /> : undefined}
      {approval && mode !== "correct" ? <ApprovalModal approval={approval} /> : undefined}
      {!approval && why ? <Text>{why}</Text> : undefined}
      {!approval && !why && selected?.kind === "thought" ? <Text>{selected.text}</Text> : undefined}
      {!approval && !why && selected?.kind === "tool" ? <Text>{selected.name} [{selected.status}]</Text> : undefined}
      {!approval && !why && selected?.kind === "opaque" ? <Text>{selected.label}</Text> : undefined}
      {!approval && !why && !selected ? <Text dimColor>(select a row)</Text> : undefined}
    </Box>
  );
}

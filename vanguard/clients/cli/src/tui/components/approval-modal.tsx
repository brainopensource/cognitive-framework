import React from "react";
import { Box, Text } from "ink";
import { colorizeUnifiedDiff } from "../diff.js";
import type { PendingApproval } from "@vanguard/client-core";

/** Display-only: keyboard routing lives in RunTui, not in unused callbacks. */
export function ApprovalModal({ approval }: { approval: PendingApproval }) {
  const lines = colorizeUnifiedDiff(approval.unifiedDiff);
  return (
    <Box flexDirection="column" borderStyle="round" borderColor="yellow" paddingX={1}>
      <Text color="yellow" bold>DIFF APPROVAL {approval.approvalId}</Text>
      {lines.map((line, index) => <Text key={`${index}-${line.text}`} color={line.color}>{line.text}</Text>)}
      <Text dimColor>[y] Approve  [n] Reject  [c] Correct</Text>
    </Box>
  );
}

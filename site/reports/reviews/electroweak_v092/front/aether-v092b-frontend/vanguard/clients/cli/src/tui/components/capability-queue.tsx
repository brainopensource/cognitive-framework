import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export type PendingCapability = {
  approvalId: string;
  action: string;
  scope: string;
  risk: string;
  requestedBy: string;
};

export const CapabilityQueue: React.FC<{
  pending: readonly PendingCapability[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}> = (props) => {
  if (props.pending.length === 0) return <Box><Text>No pending approvals</Text></Box>;
  
  return (
    <Box flexDirection="column">
      <Text color={theme.accent}>Pending Approvals:</Text>
      {props.pending.map(p => (
        <Box key={p.approvalId} flexDirection="column" paddingLeft={2} borderStyle="single" borderColor={theme.warning}>
          <Text>Action: {p.action}</Text>
          <Text>Scope: {p.scope}</Text>
          <Text>Risk: {p.risk}</Text>
          <Text dimColor>Requested By: {p.requestedBy}</Text>
          <Text color={theme.warning}>(y) Approve (n) Reject</Text>
        </Box>
      ))}
    </Box>
  );
};

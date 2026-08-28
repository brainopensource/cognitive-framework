import React from "react";
import { Box, Text } from "ink";
import { colorizeUnifiedDiff } from "../diff.js";
import type { PendingApproval } from "@vanguard/client-core";

/** Display-only: keyboard routing lives in RunTui, not in unused callbacks. */
export function ApprovalModal({ approval }: { approval: PendingApproval }) {
  const lines = colorizeUnifiedDiff(approval.unifiedDiff);
  return (
    <Box flexDirection="column" borderStyle="round" borderColor="yellow" paddingX={1} marginY={1}>
      <Box flexDirection="row" justifyContent="space-between">
        <Text color="yellow" bold>
          🔒 CRYPTOGRAPHIC APPROVAL CHALLENGE [{approval.approvalId}]
        </Text>
        <Text color="yellow" bold>
          [GATE: S5 DISPATCH]
        </Text>
      </Box>

      <Box flexDirection="column" marginY={0}>
        <Text dimColor>
          Episode: {approval.episodeId} · Descriptor: {approval.descriptorDigest?.slice(0, 24)}...
        </Text>
        <Text dimColor>
          Args Digest: {approval.argsDigest?.slice(0, 24)}... · Expires: {approval.expiresAt?.slice(11, 19) || "1h"}
        </Text>
      </Box>

      <Box flexDirection="column" marginY={1} borderStyle="single" borderColor="gray" paddingX={1}>
        <Text bold dimColor>PROPOSED SURGICAL DIFF:</Text>
        {lines.length === 0 ? (
          <Text dimColor>(No diff content)</Text>
        ) : (
          lines.slice(0, 15).map((line, index) => (
            <Text key={`${index}-${line.text}`} color={line.color}>
              {line.text}
            </Text>
          ))
        )}
        {lines.length > 15 && (
          <Text dimColor>... ({lines.length - 15} more lines hidden)</Text>
        )}
      </Box>

      <Box flexDirection="row" justifyContent="space-between">
        <Text bold color="green">
          [y] Sign &amp; Approve (Ed25519)
        </Text>
        <Text bold color="red">
          [n] Reject
        </Text>
        <Text bold color="cyan">
          [c] Record Correction
        </Text>
      </Box>
    </Box>
  );
}

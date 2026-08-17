import React, { useState } from "react";
import { Box, Text, useApp, useInput } from "ink";
import { captureCorrection } from "../../application/corrections.js";
import { dispatchApproval } from "../../application/approvals.js";
import type { RuntimeClient } from "../../contract/types.js";
import { ApprovalModal } from "../components/approval-modal.js";
import { ConnectionBadge } from "../components/connection-badge.js";
import { CorrectionPrompt } from "../components/correction-prompt.js";
import { LiveScreen } from "../components/live-screen.js";
import { useVanguardRun } from "../hooks/use-vanguard-run.js";
import { approvalActionForKey } from "../keys.js";

export function RunTui({ runtime, repo, runId, resumeFrom }: { runtime: RuntimeClient; repo: string; runId?: string; resumeFrom?: string }) {
  const { exit } = useApp();
  const { view, status, activeRunId, source } = useVanguardRun(runtime, repo, runId, resumeFrom);
  const [mode, setMode] = useState<"run" | "correct">("run");

  useInput((input, key) => {
    if (key.escape || input === "q") {
      exit();
      return;
    }
    if (mode === "correct") {
      const approval = view.pendingApproval;
      if (!approval) {
        setMode("run");
        return;
      }
      void captureCorrection(runtime, {
        episodeId: approval.episodeId,
        proposedPatchDigest: approval.proposedPatchDigest,
        acceptedPatchDigest: approval.proposedPatchDigest,
        key: input,
      }).then((result) => {
        if (result.ok) setMode("run");
      });
      return;
    }
    if (view.pendingApproval) {
      const action = approvalActionForKey(input);
      if (action === "approve" || action === "reject") void dispatchApproval(runtime, view.pendingApproval.approvalId, input);
      if (action === "correct") setMode("correct");
      return;
    }
    if (input === "c" && activeRunId) void runtime.requestCancel(activeRunId);
  });

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
      <Text color="cyan" bold>VG / RUN</Text>
      <ConnectionBadge source={source} />
      <Text>status: <Text color="yellow">{status}</Text></Text>
      <LiveScreen view={view} repo={repo} />
      {view.pendingApproval && mode === "run" ? <ApprovalModal approval={view.pendingApproval} /> : undefined}
      {mode === "correct" ? <CorrectionPrompt /> : undefined}
      <Text dimColor>{view.pendingApproval ? (mode === "correct" ? "taxonomy keys" : "y/n/c") : "c cancel · q quit"}</Text>
    </Box>
  );
}

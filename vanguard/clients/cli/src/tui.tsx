import React, { useEffect, useState } from "react";
import { Box, Text, useApp, useInput } from "ink";
import { captureCorrection } from "./application/corrections.js";
import { dispatchApproval } from "./application/approvals.js";
import { emptyRunView, reduceRunView, type RunViewModel } from "./application/run-view.js";
import type { RuntimeClient } from "./contract/types.js";
import { ApprovalModal } from "./ui/approval-modal.js";
import { CorrectionPrompt } from "./ui/correction-prompt.js";
import { approvalActionForKey } from "./ui/keys.js";
import { LiveScreen } from "./ui/live-screen.js";

export function RunTui({ runtime, repo, runId, resumeFrom }: { runtime: RuntimeClient; repo: string; runId?: string; resumeFrom?: string }) {
  const { exit } = useApp();
  const [view, setView] = useState<RunViewModel>(emptyRunView);
  const [status, setStatus] = useState("starting");
  const [mode, setMode] = useState<"run" | "correct">("run");
  const [activeRunId, setActiveRunId] = useState(runId ?? "");

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const started = await runtime.startRun({ repo, runId, resumeFrom });
        const streamId = started.ok ? started.value.runId : runId ?? "";
        setActiveRunId(streamId);
        setStatus(started.ok ? "requested" : started.error.code);
        for await (const result of runtime.streamEvents({ runId: streamId })) {
          if (!alive) return;
          if (!result.ok) {
            setStatus(result.error.code);
            continue;
          }
          setView((current) => reduceRunView(current, result.value.envelope));
          setStatus(result.value.envelope.payload.kind);
        }
      } catch (error) {
        setStatus(error instanceof Error ? error.message : String(error));
      }
    })();
    return () => {
      alive = false;
    };
  }, [repo, resumeFrom, runId, runtime]);

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
      <Text>status: <Text color="yellow">{status}</Text></Text>
      <LiveScreen view={view} repo={repo} />
      {view.pendingApproval && mode === "run" ? (
        <ApprovalModal
          approval={view.pendingApproval}
          onApprove={() => void runtime.resolveApproval({ approvalId: view.pendingApproval!.approvalId, decision: "approve" })}
          onReject={() => void runtime.resolveApproval({ approvalId: view.pendingApproval!.approvalId, decision: "reject" })}
          onCorrect={() => setMode("correct")}
        />
      ) : undefined}
      {mode === "correct" ? <CorrectionPrompt /> : undefined}
      <Text dimColor>{view.pendingApproval ? (mode === "correct" ? "taxonomy keys" : "y/n/c") : "c cancel · q quit"}</Text>
    </Box>
  );
}

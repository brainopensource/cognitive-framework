import React, { useEffect, useState } from "react";
import { Box, Text, useApp, useInput, useStdout } from "ink";
import { captureCorrection, type RuntimeClient } from "@vanguard/client-core";
import { submitInteractiveApproval } from "../../composition/operator-approval.js";
import { DetailPane } from "../components/detail-pane.js";
import { HelpOverlay } from "../components/help-overlay.js";
import { PromptBar } from "../components/prompt-bar.js";
import { StatusBar } from "../components/status-bar.js";
import { TranscriptPane } from "../components/transcript-pane.js";
import {
  modeAfterPendingApproval,
  shouldDispatchApproval,
  shouldEnterCorrect,
  shouldQuit,
  shouldRequestCancel,
  submitBrief,
  type TuiMode,
} from "../focus.js";
import { useVanguardRun } from "../hooks/use-vanguard-run.js";
import { DEFAULT_TRANSCRIPT_HEIGHT, moveTranscriptCursor, windowTranscript } from "../transcript-window.js";

export function RunTui({
  runtime,
  repo,
  runId,
  resumeFrom,
  autostart,
  initialBrief,
}: {
  runtime: RuntimeClient;
  repo: string;
  runId?: string;
  resumeFrom?: string;
  autostart: boolean;
  initialBrief: string;
}) {
  const { exit } = useApp();
  const { stdout } = useStdout();
  const columns = stdout?.columns ?? 80;
  const stacked = columns < 80;
  const { view, status, activeRunId, source, lastSeq, begin } = useVanguardRun(runtime, {
    repo,
    runId,
    resumeFrom,
    brief: initialBrief,
    autostart,
  });
  const [mode, setMode] = useState<TuiMode>(autostart ? "run" : "prompt");
  const [previousMode, setPreviousMode] = useState<TuiMode>(autostart ? "run" : "prompt");
  const [buffer, setBuffer] = useState(autostart ? "" : initialBrief);
  const [cursor, setCursor] = useState(0);
  const [localStatus, setLocalStatus] = useState<string | undefined>(undefined);
  const [why, setWhy] = useState<string | undefined>(undefined);

  useEffect(() => {
    setMode((current) => modeAfterPendingApproval(current, Boolean(view.pendingApproval)));
  }, [view.pendingApproval]);

  const windowed = windowTranscript(view, cursor, DEFAULT_TRANSCRIPT_HEIGHT);
  const selected = windowed.rows[0];

  useInput((input, key) => {
    if (key.ctrl && input === "c") {
      if (activeRunId) void runtime.requestCancel(activeRunId);
      return;
    }
    if (input === "?") {
      if (mode === "help") setMode(previousMode);
      else {
        setPreviousMode(mode);
        setMode("help");
      }
      return;
    }
    if (mode === "help") {
      if (key.escape) setMode(previousMode);
      return;
    }
    if (shouldQuit(mode, input)) {
      exit();
      return;
    }
    if (shouldRequestCancel(mode, { ctrlC: false, escape: Boolean(key.escape) })) {
      if (activeRunId) void runtime.requestCancel(activeRunId);
      return;
    }
    if (mode === "prompt") {
      if (key.return) {
        const submitted = submitBrief(buffer);
        if (!submitted.ok) {
          setLocalStatus(submitted.error.code);
          return;
        }
        setLocalStatus(undefined);
        setMode("run");
        begin(submitted.value.brief);
        return;
      }
      if (key.tab) {
        setMode("run");
        return;
      }
      if (key.backspace || key.delete) {
        setBuffer((current) => current.slice(0, -1));
        return;
      }
      if (input && !key.ctrl && !key.meta) setBuffer((current) => current + input);
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
    if (shouldDispatchApproval(mode, input) && view.pendingApproval) {
      void submitInteractiveApproval(runtime, view.pendingApproval, input);
      return;
    }
    if (shouldEnterCorrect(mode, input)) {
      setMode("correct");
      return;
    }
    if (mode === "run") {
      if (key.tab) {
        setMode("prompt");
        return;
      }
      if (input === "j" || key.downArrow || key.pageDown) {
        setCursor((c) => moveTranscriptCursor(c, windowed.total, DEFAULT_TRANSCRIPT_HEIGHT, 1));
        return;
      }
      if (input === "k" || key.upArrow || key.pageUp) {
        setCursor((c) => moveTranscriptCursor(c, windowed.total, DEFAULT_TRANSCRIPT_HEIGHT, -1));
        return;
      }
      if (input === "w") {
        const artifactId = selected?.kind === "tool" ? selected.name : "unknown";
        void runtime.explainArtifact(artifactId).then((result) => {
          setWhy(result.ok ? JSON.stringify(result.value) : result.error.code);
        });
      }
    }
  });

  const kind = localStatus ?? status;
  const hints =
    mode === "prompt"
      ? "Enter start · Tab run · empty Enter = invalid_request"
      : view.pendingApproval
        ? (mode === "correct" ? "taxonomy keys" : "y/n/c · ? help")
        : "Tab prompt · ctrl+c cancel · ? help · q quit";

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
      <StatusBar
        source={source}
        seq={lastSeq}
        tokens={view.tokens}
        costMicros={view.costMicros}
        kind={kind}
      />
      <Box flexDirection={stacked ? "column" : "row"}>
        <TranscriptPane rows={windowed.rows} selected={0} />
        {mode === "help" ? <HelpOverlay /> : <DetailPane mode={mode} approval={view.pendingApproval} selected={selected} why={why} />}
      </Box>
      <PromptBar mode={mode} buffer={buffer} hints={hints} />
      <Text dimColor>{repo}</Text>
    </Box>
  );
}

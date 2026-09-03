import React, { useEffect, useState } from "react";
import { Box, Text, useApp, useInput, useStdout } from "ink";
import { captureCorrection, type RuntimeClient } from "@vanguard/client-core";
import { submitInteractiveApproval } from "../../composition/operator-approval.js";
import { DetailPane } from "../components/detail-pane.js";
import { HelpOverlay } from "../components/help-overlay.js";
import { PromptBar } from "../components/prompt-bar.js";
import { StatusBar } from "../components/status-bar.js";
import { TranscriptPane } from "../components/transcript-pane.js";
import { Sidebar } from "../components/sidebar.js";
import { EventTimeline } from "../components/event-timeline.js";
import { AgentViewPanel } from "../components/agent-view-panel.js";
import { ContextPanel } from "../components/context-panel.js";
import { CommandPalette } from "../components/command-palette.js";
import { GapIndicator } from "../components/gap-indicator.js";
import { useEventTimeline } from "../hooks/use-event-timeline.js";
import { useAgentView } from "../hooks/use-agent-view.js";
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
import { whyText } from "../why-display.js";

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
  const { view, status, activeRunId, source, lastSeq, begin, beginResume } = useVanguardRun(runtime, {
    repo,
    runId,
    resumeFrom,
    brief: initialBrief,
    autostart,
  });
  const [mode, setMode] = useState<TuiMode>(autostart ? (resumeFrom ? "run" : "run") : "prompt");
  const [previousMode, setPreviousMode] = useState<TuiMode>(autostart ? "run" : "prompt");
  const [buffer, setBuffer] = useState(autostart ? "" : initialBrief);
  const [cursor, setCursor] = useState(0);
  const [localStatus, setLocalStatus] = useState<string | undefined>(undefined);
  const [why, setWhy] = useState<string | undefined>(undefined);
  
  // New layout state
  const [centerPanel, setCenterPanel] = useState<"transcript" | "timeline">("transcript");
  const [inspectorView, setInspectorView] = useState<"context" | "tools" | "artifacts" | "agent">("agent");
  const [showCommandPalette, setShowCommandPalette] = useState(false);

  const events = (view as any).events ?? [];
  const timelineEvents = useEventTimeline(events);
  const agentViewData = useAgentView(view);

  useEffect(() => {
    setMode((current) => modeAfterPendingApproval(current, Boolean(view.pendingApproval)));
  }, [view.pendingApproval]);

  const windowed = windowTranscript(view, cursor, DEFAULT_TRANSCRIPT_HEIGHT);
  const selected = windowed.rows[0];

  useInput((input, key) => {
    if (showCommandPalette) return; // Handled by CommandPalette itself if it had one, but here we just ignore outside

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
    if (input === "/") {
      setShowCommandPalette(true);
      setPreviousMode(mode);
      setMode("command_palette");
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
    if (mode === "prompt" || mode === "resume") {
      if (key.return) {
        const submitted = submitBrief(buffer);
        if (!submitted.ok) {
          setLocalStatus(submitted.error.code);
          return;
        }
        setLocalStatus(undefined);
        setMode("run");
        if (mode === "resume") beginResume(submitted.value.brief);
        else begin(submitted.value.brief);
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
    if (mode === "run" || mode === "timeline" || mode === "inspector") {
      if (key.tab) {
        setCenterPanel(p => p === "transcript" ? "timeline" : "transcript");
        setMode(centerPanel === "transcript" ? "timeline" : "run");
        return;
      }
      if (input === "1") setInspectorView("context");
      if (input === "2") setInspectorView("tools");
      if (input === "3") setInspectorView("artifacts");
      if (input === "4") setInspectorView("agent");
      
      if (input === "j" || key.downArrow || key.pageDown) {
        setCursor((c) => moveTranscriptCursor(c, windowed.total, DEFAULT_TRANSCRIPT_HEIGHT, 1));
        return;
      }
      if (input === "k" || key.upArrow || key.pageUp) {
        setCursor((c) => moveTranscriptCursor(c, windowed.total, DEFAULT_TRANSCRIPT_HEIGHT, -1));
        return;
      }
      if (input === "r") {
        setBuffer(activeRunId || "");
        setMode("resume");
        return;
      }
      if (input === "w") {
        const artifactId = selected?.kind === "tool" ? selected.name : "unknown";
        void runtime.explainArtifact(artifactId).then((result) => setWhy(whyText(result)));
      }
    }
  });

  const kind = localStatus ?? status;
  const hints =
    mode === "prompt"
      ? "Enter start · Tab run · empty Enter = invalid_request"
      : mode === "resume"
        ? "Enter resume run id · empty Enter = invalid_request"
        : view.pendingApproval
          ? (mode === "correct" ? "taxonomy keys" : "y/n/c · ? help")
          : "Tab panel · 1-4 inspector · r resume · / command · ? help · q quit";

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
      <StatusBar view={view} source={source} lastSeq={lastSeq} lastKind={kind} />
      <Box flexDirection={stacked ? "column" : "row"} flexGrow={1}>
        <Sidebar entries={[{ id: activeRunId || "none", label: "Run " + (activeRunId || ""), kind: "run", selected: true }]} selectedIndex={0} onSelect={() => {}} width={20} />
        <Box flexDirection="column" flexGrow={1} marginLeft={1}>
          {centerPanel === "timeline" ? (
             <EventTimeline events={timelineEvents} height={DEFAULT_TRANSCRIPT_HEIGHT} onSelectEvent={() => {}} />
          ) : (
             <TranscriptPane rows={windowed.rows} selected={0} />
          )}
        </Box>
        <Box flexDirection="column" width={40} marginLeft={1}>
          {mode === "help" ? <HelpOverlay /> : inspectorView === "agent" ? (
             <AgentViewPanel data={agentViewData} height={DEFAULT_TRANSCRIPT_HEIGHT} />
          ) : inspectorView === "context" ? (
             <ContextPanel sources={[]} totalTokens={0} compacted={false} height={DEFAULT_TRANSCRIPT_HEIGHT} />
          ) : (
             <DetailPane mode={mode} approval={view.pendingApproval} selected={selected} why={why} />
          )}
        </Box>
      </Box>
      <PromptBar mode={mode} buffer={buffer} hints={hints} />
      <CommandPalette 
        visible={showCommandPalette} 
        availableCommands={["/help", "/quit", "/cancel"]} 
        onExecute={(cmd) => { 
          setShowCommandPalette(false); 
          setMode(previousMode); 
          if(cmd === "/quit") exit(); 
          if(cmd === "/cancel" && activeRunId) void runtime.requestCancel(activeRunId);
        }} 
        onDismiss={() => { 
          setShowCommandPalette(false); 
          setMode(previousMode); 
        }} 
      />
      <Box flexDirection="row">
        <Text dimColor>{repo}</Text>
        <GapIndicator isLive={status !== "disconnected"} hasGap={false} reconnecting={status === "reconnecting"} />
      </Box>
    </Box>
  );
}

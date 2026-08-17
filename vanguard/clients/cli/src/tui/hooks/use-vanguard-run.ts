import { useEffect, useState } from "react";
import {
  emptyRunView,
  reduceRunView,
  type RuntimeClient,
  type RunViewModel,
  type StreamSource,
} from "@vanguard/client-core";

export type UseVanguardRunOptions = {
  repo: string;
  runId?: string;
  resumeFrom?: string;
  brief?: string;
  autostart: boolean;
};

export function useVanguardRun(runtime: RuntimeClient, options: UseVanguardRunOptions) {
  const { repo, runId, resumeFrom, autostart } = options;
  const [view, setView] = useState<RunViewModel>(emptyRunView);
  const [status, setStatus] = useState(autostart ? "starting" : "idle");
  const [activeRunId, setActiveRunId] = useState(runId ?? "");
  const [source, setSource] = useState<StreamSource | "unknown">("unknown");
  const [lastSeq, setLastSeq] = useState<string | undefined>(undefined);
  const [armedBrief, setArmedBrief] = useState<string | undefined>(
    autostart ? (options.brief ?? "") : undefined
  );

  useEffect(() => {
    if (armedBrief === undefined) return;
    let alive = true;
    (async () => {
      try {
        const started = await runtime.startRun({
          repo,
          runId,
          resumeFrom,
          prompt: armedBrief,
          brief: armedBrief,
        });
        const streamId = started.ok ? started.value.runId : runId ?? "";
        setActiveRunId(streamId);
        setStatus(started.ok ? "requested" : started.error.code);
        for await (const result of runtime.streamEvents({ runId: streamId })) {
          if (!alive) return;
          if (!result.ok) {
            setStatus(result.error.code);
            continue;
          }
          setSource(result.value.source);
          setLastSeq(result.value.envelope.seq);
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
  }, [armedBrief, repo, resumeFrom, runId, runtime]);

  return {
    view,
    status,
    activeRunId,
    source,
    lastSeq,
    begin: (brief: string) => setArmedBrief(brief),
  };
}

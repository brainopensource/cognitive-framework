import { useEffect, useState } from "react";
import { emptyRunView, reduceRunView, type RunViewModel } from "../../application/run-view.js";
import type { RuntimeClient, StreamSource } from "../../contract/types.js";

export function useVanguardRun(runtime: RuntimeClient, repo: string, runId?: string, resumeFrom?: string) {
  const [view, setView] = useState<RunViewModel>(emptyRunView);
  const [status, setStatus] = useState("starting");
  const [activeRunId, setActiveRunId] = useState(runId ?? "");
  const [source, setSource] = useState<StreamSource | "unknown">("unknown");

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
          setSource(result.value.source);
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

  return { view, status, activeRunId, source };
}

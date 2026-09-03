import { useEffect, useState } from "react";
import {
  emptyRunView,
  reduceRunView,
  subscribeRun,
  type RuntimeClient,
  type RunViewModel,
  type StreamSource,
} from "@vanguard/client-core";
import { performResume } from "../../composition/resume-session.js";

export type UseVanguardRunOptions = {
  repo: string;
  runId?: string;
  resumeFrom?: string;
  brief?: string;
  autostart: boolean;
};

type Intent =
  | { type: "start"; brief: string }
  | { type: "resume"; runId: string; checkpointId?: string };

function initialIntent(options: UseVanguardRunOptions): Intent | undefined {
  if (!options.autostart) return undefined;
  if (options.resumeFrom) {
    if (options.runId) {
      return { type: "resume", runId: options.runId, checkpointId: options.resumeFrom };
    }
    return { type: "resume", runId: options.resumeFrom };
  }
  return { type: "start", brief: options.brief ?? "" };
}

export function useVanguardRun(runtime: RuntimeClient, options: UseVanguardRunOptions) {
  const { repo, runId, resumeFrom } = options;
  const [view, setView] = useState<RunViewModel>(emptyRunView);
  const [status, setStatus] = useState(options.autostart ? "starting" : "idle");
  const [activeRunId, setActiveRunId] = useState(runId ?? "");
  const [source, setSource] = useState<StreamSource | "unknown">("unknown");
  const [lastSeq, setLastSeq] = useState<string | undefined>(undefined);
  const [intent, setIntent] = useState<Intent | undefined>(initialIntent(options));

  useEffect(() => {
    if (!intent) return;
    const ac = new AbortController();
    (async () => {
      try {
        let streamId = "";
        if (intent.type === "resume") {
          const outcome = await performResume(runtime, intent.runId, intent.checkpointId);
          if (!outcome.ok) {
            setStatus(outcome.code);
            return;
          }
          streamId = outcome.runId;
          setActiveRunId(streamId);
          setStatus("requested");
        } else {
          const started = await runtime.startRun({
            repo,
            runId,
            resumeFrom,
            prompt: intent.brief,
            brief: intent.brief,
          });
          if (!started.ok) {
            setStatus(started.error.code);
            return;
          }
          streamId = started.value.runId;
          setActiveRunId(streamId);
          setStatus("requested");
        }
        await subscribeRun(
          runtime,
          { runId: streamId },
          {
            onItem: (item) => {
              setSource(item.source);
              setLastSeq(item.envelope.seq);
              setView((current) => reduceRunView(current, item.envelope));
              setStatus(item.envelope.payload.kind);
            },
            onError: (error) => setStatus(error.code),
          },
          ac.signal
        );
      } catch (error) {
        setStatus(error instanceof Error ? error.message : String(error));
      }
    })();
    return () => ac.abort();
  }, [intent, repo, resumeFrom, runId, runtime]);

  return {
    view,
    status,
    activeRunId,
    source,
    lastSeq,
    begin: (brief: string) => setIntent({ type: "start", brief }),
    beginResume: (resumeId: string, checkpointId?: string) =>
      setIntent({ type: "resume", runId: resumeId, checkpointId }),
  };
}

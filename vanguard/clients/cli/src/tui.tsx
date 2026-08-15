import React, { useEffect, useState } from "react";
import { Box, Text, useApp, useInput } from "ink";
import type { RuntimeClient, StreamItem } from "./contract/types.js";

export function RunTui({ runtime, repo, runId, resumeFrom }: { runtime: RuntimeClient; repo: string; runId?: string; resumeFrom?: string }) {
  const { exit } = useApp();
  const [events, setEvents] = useState<StreamItem[]>([]);
  const [status, setStatus] = useState("starting");
  const activeRunId = events[0]?.envelope.runId ?? runId;

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const started = await runtime.startRun({ repo, runId, resumeFrom });
        const streamId = started.ok ? started.value.runId : runId ?? "";
        if (started.ok) setStatus("requested");
        else setStatus(started.error.code);
        for await (const result of runtime.streamEvents({ runId: streamId })) {
          if (!alive) return;
          if (!result.ok) {
            setStatus(result.error.code);
            continue;
          }
          setEvents((current) => [...current.slice(-11), result.value]);
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
    if (input === "c" && activeRunId) void runtime.requestCancel(activeRunId);
    if (input === "q" || key.escape) exit();
  });

  return <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
    <Text color="cyan" bold>VG / RUN</Text>
    <Text>repo: {repo}  status: <Text color="yellow">{status}</Text></Text>
    <Text dimColor>controls: c cancel · q quit</Text>
    <Box flexDirection="column" marginTop={1}>
      {events.map((item) => <Text key={`${item.envelope.eventId}-${item.envelope.seq}`}>[{item.envelope.seq.padStart(2, "0")}] {item.envelope.payload.kind.padEnd(20)} {item.source}</Text>)}
    </Box>
  </Box>;
}

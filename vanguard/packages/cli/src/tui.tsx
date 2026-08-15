import React, { useEffect, useState } from "react";
import { Box, Text, useApp, useInput } from "ink";
import type { RuntimeEvent, RuntimePort } from "./runtime.js";

export function RunTui({ runtime, repo, runId, resumeFrom, checkpointEvery }: { runtime: RuntimePort; repo: string; runId?: string; resumeFrom?: string; checkpointEvery?: number }) {
  const { exit } = useApp();
  const [events, setEvents] = useState<RuntimeEvent[]>([]);
  const [status, setStatus] = useState("starting");
  const activeRunId = events[0]?.runId ?? runId;

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const source = resumeFrom ? runtime.resume(resumeFrom) : runtime.run({ repo, runId, checkpointEvery });
        for await (const event of source) {
          if (!alive) return;
          setEvents((current) => [...current.slice(-11), event]);
          setStatus(event.type.replace(".", " "));
        }
      } catch (error) { setStatus(error instanceof Error ? error.message : String(error)); }
    })();
    return () => { alive = false; };
  }, [repo, resumeFrom, runId, checkpointEvery, runtime]);

  useInput((input, key) => {
    if (input === "c" && activeRunId) void runtime.cancel(activeRunId);
    if (input === "q" || key.escape) exit();
  });

  return <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
    <Text color="cyan" bold>VG / RUN</Text>
    <Text>repo: {repo}  status: <Text color="yellow">{status}</Text></Text>
    <Text dimColor>controls: c cancel · q quit</Text>
    <Box flexDirection="column" marginTop={1}>
      {events.map((event) => <Text key={`${event.runId}-${event.seq}`} color={event.type === "run.completed" ? "green" : event.type === "run.cancelled" ? "red" : undefined}>[{String(event.seq).padStart(2, "0")}] {event.type.padEnd(20)} {event.message}</Text>)}
    </Box>
  </Box>;
}

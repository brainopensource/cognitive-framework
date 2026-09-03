import { useEffect, useMemo, useRef, useState } from "react";
import type { RuntimeClient } from "@vanguard/client-core/contract/types.js";
import { ColumnarEventStore } from "../store/event-store.js";
import { initialStudioFold, StudioFoldEngine, type StudioFold } from "../store/fold.js";
import { INITIAL_SESSION_STATE, type StudioSessionState } from "../store/session.js";
import { StudioApp } from "../ui/StudioApp.js";

export type StudioRuntimeProps = {
  readonly client: RuntimeClient;
  readonly runId: string;
  readonly initialSession?: Partial<StudioSessionState>;
};

export function useStudioRuntime({ client, runId, initialSession }: StudioRuntimeProps) {
  const store = useMemo(() => new ColumnarEventStore(), []);
  const engine = useMemo(() => new StudioFoldEngine(), []);
  const [rows, setRows] = useState(store.getAllRows());
  const [fold, setFold] = useState<StudioFold>(initialStudioFold());
  const [session, setSession] = useState<StudioSessionState>({ ...INITIAL_SESSION_STATE, ...initialSession });
  const [connection, setConnection] = useState<"connecting" | "live" | "interrupted" | "complete">("connecting");
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    const controller = new AbortController();
    setConnection("connecting");
    void (async () => {
      let sawEvent = false;
      try {
        for await (const result of client.streamEvents({ runId }, controller.signal)) {
          if (!mounted.current) return;
          if (!result.ok) { setConnection("interrupted"); continue; }
          sawEvent = true;
          store.append(result.value.envelope);
          const nextRows = store.getAllRows();
          setRows(nextRows);
          setFold(engine.foldAll(nextRows));
          setConnection("live");
        }
        if (mounted.current) setConnection(sawEvent ? "complete" : "interrupted");
      } catch {
        if (mounted.current) setConnection("interrupted");
      }
    })();
    return () => { mounted.current = false; controller.abort(); };
  }, [client, engine, runId, store]);

  const selectSurface = (activeSurface: StudioSessionState["activeSurface"]) => setSession((current) => ({ ...current, activeSurface }));
  const selectSeq = (selectedSeq: bigint) => setSession((current) => ({ ...current, selectedSeq, isScrubbing: selectedSeq > 0n && selectedSeq < fold.atSeq }));
  const foldedView = session.isScrubbing ? engine.foldToSeq(session.selectedSeq, rows) : fold;
  const visibleFold: StudioFold = {
    ...foldedView,
    streamHealth: connection === "interrupted" || store.getGaps().length > 0 ? "gap" : connection === "live" ? "live" : foldedView.streamHealth,
  };

  return {
    fold: visibleFold,
    rows,
    session,
    connection,
    latestSeq: fold.atSeq,
    onSelectSurface: selectSurface,
    onSelectSeq: selectSeq,
    onResolveApproval: async (approvalId: string, decision: "approve" | "reject") => {
      const result = await client.resolveApproval({ approvalId, decision });
      if (!result.ok) throw new Error(result.error.message);
    },
  };
}

export function StudioRuntime(props: StudioRuntimeProps) {
  const runtime = useStudioRuntime(props);
  return <StudioApp {...runtime} />;
}

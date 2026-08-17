import { useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { attachLive, ReplayRuntimeClient, emptyRunView, reduceRunView, type EventEnvelope, type RunViewModel, type RuntimeClient } from "@vanguard/client-core";
import { FilesSlot, SlotFrame, type WorkspaceFile } from "./slots/files";
import { EditorSlot } from "./slots/editor";
import { TerminalSlot } from "./slots/terminal";
import { TraceSlot } from "./slots/trace";
import { ApproveSlot } from "./slots/approve";
import { GitSlot } from "./slots/git";
import { Palette } from "./slots/palette";
import { WhySlot } from "./slots/why";
import "./style.css";

type SlotId = "files" | "editor" | "terminal" | "run" | "trace-canvas" | "approve" | "why" | "git";
type Mode = "replay" | "live";
const slots: SlotId[] = ["files", "editor", "terminal", "run", "trace-canvas", "approve", "why", "git"];

function RunSlot({ view, events, mode, liveError }: { view: RunViewModel; events: EventEnvelope[]; mode: Mode; liveError?: string }) {
  return <SlotFrame title="RUN / REPLAY"><div className="badge">source: {mode === "replay" ? "mock · replay fixture" : "live"}</div>{liveError && <div className="not-available">not_available · {liveError}</div>}<div className="metrics"><div><b>{view.tokens}</b><small>TOKENS</small></div><div><b>{view.costMicros}</b><small>COST (μ)</small></div><div><b>{view.lastKind || "—"}</b><small>LAST EVENT</small></div></div><div className="stream">{events.slice(-100).map(event => <div className="event" key={event.eventId}><span>{event.seq}</span><code>{event.payload.kind}</code><em>{String(event.payload.text ?? event.payload.tool ?? event.payload.state ?? event.payload.outcome ?? "ledger event")}</em></div>)}</div><div className="subgrid"><div><h4>THOUGHTS</h4>{view.thoughts.length ? view.thoughts.map((x, i) => <p key={i}>{x}</p>) : <p className="muted">No thoughts recorded.</p>}</div><div><h4>TOOLS</h4>{view.tools.length ? view.tools.map((x, i) => <p key={i}><code>{x.name}</code> {x.status}</p>) : <p className="muted">No tools recorded.</p>}</div></div></SlotFrame>;
}

function App() {
  const [active, setActive] = useState<SlotId>("run"); const [mode, setMode] = useState<Mode>("replay"); const [file, setFile] = useState<WorkspaceFile>(); const [view, setView] = useState(emptyRunView()); const [events, setEvents] = useState<EventEnvelope[]>([]); const [client, setClient] = useState<RuntimeClient>(); const [liveError, setLiveError] = useState<string>(); const [palette, setPalette] = useState(true);
  async function loadReplay() { const text = await fetch("/successful-episode.jsonl").then(response => response.text()); const replay = ReplayRuntimeClient.fromJsonl(text, "mock"); const ref = await replay.startRun({ repo: "." }); if (!ref.ok) throw new Error(ref.error.message); let next = emptyRunView(); const windowed: EventEnvelope[] = []; for await (const item of replay.streamEvents({ runId: ref.value.runId })) if (item.ok) { windowed.push(item.value.envelope); if (windowed.length > 100) windowed.shift(); next = reduceRunView(next, item.value.envelope); } setClient(replay); setEvents(windowed); setView(next); setLiveError(undefined); }
  async function switchMode(next: Mode) { setMode(next); setEvents([]); setView(emptyRunView()); if (next === "replay") { await loadReplay(); return; } try { const live = attachLive({ repo: "." }); setClient(live); const ref = await live.startRun({ repo: ".", brief: "GUI live attach" }); if (!ref.ok) setLiveError(ref.error.code); } catch (error) { setLiveError(error instanceof Error ? error.message : "daemon is unavailable"); } }
  useEffect(() => { void loadReplay(); }, []);
  function focus(slot: string) { setActive(slot as SlotId); setPalette(false); }
  let content: ReactNode; switch (active) { case "files": content = <SlotFrame title="WORKSPACE FILES"><FilesSlot onOpen={selected => { setFile(selected); setActive("editor"); }} /></SlotFrame>; break; case "editor": content = <EditorSlot file={file} />; break; case "terminal": content = <TerminalSlot />; break; case "trace-canvas": content = <TraceSlot events={events} />; break; case "approve": content = <ApproveSlot approval={view.pendingApproval} client={client ?? ReplayRuntimeClient.fromJsonl("", "mock")} />; break; case "why": content = <WhySlot client={client} />; break; case "git": content = <GitSlot />; break; default: content = <RunSlot view={view} events={events} mode={mode} liveError={liveError} />; }
  return <main><header><div><span className="logo">VG</span><strong>VANGUARD</strong><span className="crumb"> / standalone GUI</span></div><div className="mode-switch"><button className={mode === "replay" ? "active" : ""} onClick={() => void switchMode("replay")}>REPLAY</button><button className={mode === "live" ? "active" : ""} onClick={() => void switchMode("live")}>LIVE</button><span className="status">● {mode === "replay" ? "source: mock" : liveError ? "not_available" : "attaching"}</span></div></header><div className="workbench"><aside className="activity">{slots.map(slot => <button className={active === slot ? "active" : ""} title={slot} onClick={() => setActive(slot)} key={slot}>{slot === "files" ? "▤" : slot === "editor" ? "□" : slot === "terminal" ? "⌁" : slot === "run" ? "▶" : slot === "trace-canvas" ? "⌘" : slot === "approve" ? "✓" : slot === "git" ? "⑂" : "?"}</button>)}</aside><aside className="sidebar"><h3>VANGUARD</h3>{slots.map(slot => <button className={active === slot ? "selected" : ""} onClick={() => setActive(slot)} key={slot}>◼ {slot}</button>)}</aside><section className="center"><div className="tabs"><button className="active">{file?.path ?? "replay.run"}</button><button onClick={() => setPalette(true)}>⌘K</button></div><div className="editor-group">{content}</div><div className="bottom-panel"><TerminalSlot /><GitSlot /></div></section></div><footer>VG-04 · client-core · <button onClick={() => setPalette(true)}>COMMAND PALETTE</button></footer>{palette && <Palette onFocus={focus} onReplay={() => void switchMode("replay")} />}</main>;
}
createRoot(document.getElementById("root")!).render(<App />);

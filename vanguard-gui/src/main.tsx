import { useEffect, useMemo, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { ReplayRuntimeClient, emptyRunView, reduceRunView, type EventEnvelope, type RunViewModel } from "@vanguard/client-core";
import "./style.css";

type SlotId = "files" | "editor" | "terminal" | "run" | "trace-canvas" | "approve";
const slots: SlotId[] = ["files", "editor", "terminal", "run", "trace-canvas", "approve"];

function Slot({ title, children }: { title: string; children: ReactNode }) {
  return <section className="slot"><div className="slot-title"><span>{title}</span><span className="slot-mark">SLOT</span></div>{children}</section>;
}

function RunPanel({ view, events }: { view: RunViewModel; events: EventEnvelope[] }) {
  return <Slot title="RUN / REPLAY"><div className="badge">source: mock · replay fixture</div><div className="metrics"><div><b>{view.tokens}</b><small>TOKENS</small></div><div><b>{view.costMicros}</b><small>COST (μ)</small></div><div><b>{view.lastKind || "—"}</b><small>LAST EVENT</small></div></div><div className="stream">{events.map((event) => <div className="event" key={event.eventId}><span>{event.seq}</span><code>{event.payload.kind}</code><em>{String(event.payload.text ?? event.payload.tool ?? event.payload.state ?? event.payload.outcome ?? "ledger event")}</em></div>)}</div><div className="subgrid"><div><h4>THOUGHTS</h4>{view.thoughts.length ? view.thoughts.map((x, i) => <p key={i}>{x}</p>) : <p className="muted">No ObservationProduced events in this fixture.</p>}</div><div><h4>TOOLS</h4>{view.tools.length ? view.tools.map((x, i) => <p key={i}><code>{x.name}</code> {x.status}</p>) : <p className="muted">No OperatorInvoked events in this fixture.</p>}</div></div></Slot>;
}

function App() {
  const [view, setView] = useState(emptyRunView());
  const [events, setEvents] = useState<EventEnvelope[]>([]);
  const [active, setActive] = useState<SlotId>("run");
  useEffect(() => { fetch("/successful-episode.jsonl").then(r => r.text()).then(async text => { const client = ReplayRuntimeClient.fromJsonl(text, "mock"); const ref = await client.startRun({ repo: "." }); if (!ref.ok) return; let next = emptyRunView(); const collected: EventEnvelope[] = []; for await (const item of client.streamEvents({ runId: ref.value.runId })) { if (item.ok) { collected.push(item.value.envelope); next = reduceRunView(next, item.value.envelope); } } setEvents(collected); setView(next); }); }, []);
  const content = useMemo(() => { switch (active) { case "run": return <RunPanel view={view} events={events} />; case "files": return <Slot title="WORKSPACE FILES"><div className="tree">⌄ workspace<br />　⌄ src<br />　　<span>main.tsx</span><br />　　<span>style.css</span><br />　 README.md</div></Slot>; case "editor": return <Slot title="MONACO EDITOR"><div className="editor"><div className="tab">main.tsx</div><pre>const runtime = ReplayRuntimeClient.fromJsonl(text);{`\n`}await runtime.streamEvents(cursor);</pre></div></Slot>; case "terminal": return <Slot title="TERMINAL PTY"><div className="terminal">$ vg --replay successful-episode.jsonl<br /><span>PTY adapter stub · native Tauri shell in next wave</span><br />$ _</div></Slot>; case "trace-canvas": return <Slot title="VG-04 EVENT VISUALIZER"><div className="canvas">{events.map((e, i) => <div className="node" key={e.eventId} style={{ left: `${8 + (i % 3) * 30}%`, top: `${20 + Math.floor(i / 3) * 35}%` }}><b>{e.payload.kind}</b><small>seq {e.seq}</small></div>)}</div><p className="muted">Passive xyflow slot · events only, no dispatch.</p></Slot>; return <Slot title="DIFF / APPROVE"><div className="diff">No ApprovalRequested envelope in this replay.</div><button disabled>APPROVE &amp; SIGN</button><button disabled>REJECT</button><p className="muted">Ed25519 action bar binds to OperatorSigner when a populated challenge is present.</p></Slot>; } }, [active, events, view]);
  return <main><header><div><span className="logo">VG</span><strong>VANGUARD</strong><span className="crumb"> / standalone GUI</span></div><span className="status">● OFFLINE REPLAY</span></header><nav>{slots.map(slot => <button className={active === slot ? "active" : ""} onClick={() => setActive(slot)} key={slot}>{slot.replace("-", " ")}</button>)}</nav><div className="workspace"><aside><h3>SLOTS</h3>{slots.map(slot => <button className={active === slot ? "selected" : ""} onClick={() => setActive(slot)} key={slot}>◼ {slot}</button>)}</aside><div className="content">{content}</div></div><footer>VG-04 · client-core · fixture: successful-episode.jsonl</footer></main>;
}
createRoot(document.getElementById("root")!).render(<App />);

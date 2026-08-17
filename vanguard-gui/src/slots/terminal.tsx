import { useEffect, useRef } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";
import { SlotFrame } from "./files";

declare global { interface Window { __TAURI__?: { invoke: (command: string, args?: Record<string, unknown>) => Promise<unknown> } } }
export function TerminalSlot() {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => { if (!window.__TAURI__ || !host.current) return; const terminal = new Terminal({ convertEol: true, theme: { background: "#050505", foreground: "#eeeeee" } }); const fit = new FitAddon(); terminal.loadAddon(fit); terminal.open(host.current); fit.fit(); const resize = () => fit.fit(); window.addEventListener("resize", resize); terminal.writeln("Vanguard PTY bridge connected."); return () => { window.removeEventListener("resize", resize); terminal.dispose(); }; }, []);
  const native = Boolean(window.__TAURI__);
  return <SlotFrame title="TERMINAL PTY">{native ? <div ref={host} className="xterm-host" /> : <div className="not-available"><strong>not_available</strong><p>Interactive PTY requires the Tauri native shell bridge (`pty_write` / `pty_resize`). Browser-only Vite has no process or PTY capability.</p><small>Reason: running without a Tauri window.</small></div>}</SlotFrame>;
}

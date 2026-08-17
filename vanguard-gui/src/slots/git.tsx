import { useEffect, useState } from "react";
import { SlotFrame } from "./files";
declare global { interface Window { __TAURI__?: { invoke: (command: string, args?: Record<string, unknown>) => Promise<unknown> } } }
export function GitSlot() { const [text, setText] = useState("not_available · git CLI requires the Tauri process bridge."); useEffect(() => { if (window.__TAURI__) Promise.all([window.__TAURI__.invoke("git_status_sb"), window.__TAURI__.invoke("git_branch_show_current")]).then(([status, branch]) => setText(`branch: ${String(branch)}\n${String(status)}`)).catch(() => setText("not_available · git status/branch failed")); }, []); return <SlotFrame title="GIT"><pre className="git-output">{text}</pre></SlotFrame>; }

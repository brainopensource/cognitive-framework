# Prompt — Frontend Senior review (for Tech Lead)

Broad briefing. **The Tech Lead decides.** Do not pre-load a full TODO list, lane map, or stack choice — that is the reviewer’s job to recommend.

Yes, the previous prompt was too rigid: locking UDS, Ink, VS Code fork, two named lanes, wave order, and a pile of “do not import” items can block a better design. Those stay below as **inventory / current defaults**, not as the assignment.

---

## Copy-paste prompt

```text
You are advising the Tech Lead on Aether Vanguard’s operator-facing frontend (CLI and/or IDE).

## Ask
Review the frontend we already have (docs + code). Recommend what a SOTA interaction plane should be for this product, how to staff it (including whether two lanes make sense), and in what order to build — so the Tech Lead can decide.

You are not executing a backlog. You are not required to keep the current FE-xxx table, Ink, UDS, a VS Code fork, two lanes, or any prototype. Recommend the best option; list alternatives and trade-offs. The Tech Lead will cut.

## Context (where to look — not what to conclude)
- vanguard/clients/cli/** — existing TypeScript client / TUI scaffold
- docs/scrum/development_guides/cli_tui_architecture.md — current FE note (may be revised)
- docs/scrum/ROADMAP.MD — FRONTEND section (staging; may be wrong)
- docs/main_v4/ — especially VG-03 (planes) and VG-04 (wire). If FE should change a contract, say so as a recommendation to Joint/TL; do not silently fork the wire.
- Optional extra repo (reference only): Harness-D-power docs_front + src_front — a different product’s prototype. Use if useful; ignore if not.

This pass: frontend docs/plan only. Do not implement vanguard/packages or backend.

## Deliverable (keep it short — for the Tech Lead)
1. Verdict: extend / reshape / replace the current CLI scaffold — and why.
2. Product shape: what “CLI” and “IDE” should mean here (one surface, two, fork vs extension vs something else).
3. Staffing: one stream or two lanes; if two, a clean split of ownership — not a task dump.
4. Sequence: a few phases with checkpoints (not a 17-row ticket list unless TL asks).
5. Risks and open questions only the TL can close.
6. Optional: 3–7 principles you would bind if you were TL (you may challenge today’s notes).

Do not update ROADMAP or create sprints_front until the Tech Lead accepts a plan.
```

---

## Appendix — current inventory (not part of the assignment)

Noise for the reviewer if they want it; **the Tech Lead is not asked to work this list.**

- Staging IDs FE-101…404 live in ROADMAP FRONTEND (demo, live client, signer, supervisor, install, Code-OSS, webview, DLP, E2E, packages).
- Today’s default split people have used: FE-A = `clients/cli`, FE-B = `vanguard-ide`, demo → live → IDE.
- Today’s default caution: stay a client of the Python runtime; don’t add a second kernel in TS.
- Prototype often not worth merging wholesale: Tauri + xyflow DAG, WebSocket engine UI, fake diffs, meta-loop commands.

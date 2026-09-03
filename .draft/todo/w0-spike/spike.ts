// W0 qualification spike: streams 10k synthetic tokens into a scrolling
// transcript with a live status footer, measuring against
// PRD_AETHER_TUI.md §9 budgets. Self-reports hrtime measurements to
// /tmp/w0-spike/receipt.json so they can be read back outside the pty.
import { CliRenderer, TextRenderable, BoxRenderable, createCliRenderer } from "@opentui/core";
import { writeFileSync } from "node:fs";

function nowMs(): number {
  return Number(process.hrtime.bigint()) / 1e6;
}

async function main() {
  const t0 = nowMs();
  const renderer = await createCliRenderer({ exitOnCtrlC: false, targetFps: 30 });
  const root = renderer.root;

  const transcript = new BoxRenderable(renderer, {
    id: "transcript",
    width: "100%",
    height: renderer.terminalHeight - 1,
    flexDirection: "column",
    overflow: "scroll",
  });
  const footer = new TextRenderable(renderer, {
    id: "footer",
    content: "status: streaming...",
    width: "100%",
    height: 1,
  });
  root.add(transcript);
  root.add(footer);

  const lines: TextRenderable[] = [];
  const firstFrame = new Promise<number>((resolve) => {
    let resolved = false;
    renderer.on("frame", () => {
      if (!resolved) {
        resolved = true;
        resolve(nowMs() - t0);
      }
    });
  });
  renderer.start();
  const firstFrameMs = await firstFrame;

  // Stream 10k synthetic tokens, one text node every 50 tokens (200 nodes),
  // measuring event -> next render tick latency for a sample of appends.
  const TOKENS = 10_000;
  const NODES = 200;
  const tokensPerNode = TOKENS / NODES;
  const eventLatencies: number[] = [];

  for (let i = 0; i < NODES; i++) {
    const text = `line ${i}: ` + "token ".repeat(tokensPerNode);
    const evtStart = nowMs();
    const node = new TextRenderable(renderer, { id: `line-${i}`, content: text });
    transcript.add(node);
    lines.push(node);
    footer.content = `status: streaming... ${(i + 1) * tokensPerNode}/${TOKENS} tokens`;
    await new Promise<void>((resolve) => {
      const timeout = setTimeout(() => resolve(), 200);
      renderer.once("frame", () => {
        clearTimeout(timeout);
        eventLatencies.push(nowMs() - evtStart);
        resolve();
      });
    });
  }

  eventLatencies.sort((a, b) => a - b);
  const p95 = eventLatencies[Math.floor(eventLatencies.length * 0.95)] ?? null;

  // Resize reflow measurement
  const resizeStart = nowMs();
  const resizeDone = new Promise<number>((resolve) => {
    renderer.once("resize", () => resolve(nowMs() - resizeStart));
  });
  renderer.terminalWidth && process.stdout.emit("resize");
  const resizeMs = await Promise.race([
    resizeDone,
    new Promise<number | null>((r) => setTimeout(() => r(null), 500)),
  ]);

  const memMb = process.memoryUsage().rss / (1024 * 1024);

  const receipt = {
    env: {
      TERM: process.env.TERM ?? null,
      COLORTERM: process.env.COLORTERM ?? null,
      isTTY: process.stdout.isTTY ?? false,
      bunVersion: Bun.version,
      cols: renderer.terminalWidth,
      rows: renderer.terminalHeight,
    },
    measured: {
      firstFrameMs,
      eventToRenderP95Ms: p95,
      eventToRenderSamples: eventLatencies.length,
      resizeReflowMs: resizeMs,
      rssMb: memMb,
    },
    budgets: {
      firstFrameMs: 40,
      keystrokeToCellP95Ms: 12,
      eventToRenderP95Ms: 50,
      resizeReflowMs: 16,
      rssMb: 45,
    },
    notes: [
      "keystroke->cell P95 not measured: this harness has no attached TTY to inject synthetic keypresses through the real input path.",
      "resizeReflowMs measured via a synthetic SIGWINCH-equivalent event emit, not a real terminal resize; treat as indicative only.",
    ],
  };

  writeFileSync("/tmp/w0-spike/receipt.json", JSON.stringify(receipt, null, 2));
  renderer.stop();
  process.exit(0);
}

const hardTimeout = setTimeout(() => {
  writeFileSync("/tmp/w0-spike/receipt.json", JSON.stringify({ error: "hard timeout after 25s" }, null, 2));
  process.exit(1);
}, 25_000);
hardTimeout.unref?.();

main().catch((err) => {
  writeFileSync("/tmp/w0-spike/receipt.json", JSON.stringify({ error: String(err?.stack || err) }, null, 2));
  process.exit(1);
});

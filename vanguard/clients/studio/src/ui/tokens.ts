export const CSS_VARIABLES = `
:root {
  --font-sans: "Avenir Next", "Gill Sans", "Trebuchet MS", sans-serif;
  --font-mono: "IBM Plex Mono", "Cascadia Code", monospace;

  /* Five-Signal Semantic Palette */
  --signal-flow: #00d2ff;     /* Cyan: mediated execution & open lease */
  --signal-hold: #f59e0b;     /* Amber: awaiting human approval */
  --signal-deny: #ec4899;     /* Magenta: fail-closed denial & refusal */
  --signal-void: #8b5cf6;     /* Violet: undeterminable outcome (F-22) */
  --signal-proof: #10b981;    /* Emerald: cryptographically verified proof */

  /* Neutral Surface Palette (Dark Default) */
  --bg-canvas: #071014;
  --bg-surface: #0b171b;
  --bg-panel: #102126;
  --bg-card: #163038;
  --bg-card-hover: #1d4148;
  
  --border-subtle: #1e3b40;
  --border-medium: #2e5960;
  --border-focus: #e4b86a;

  --text-primary: #f6f0df;
  --text-secondary: #b3c7c1;
  --text-muted: #78938e;
  --text-faint: #42615f;

  /* Density Tokens */
  --spacing-unit: 8px;
  --header-height: 48px;
  --footer-height: 40px;
  --shadow-glow: 0 0 32px rgba(0, 210, 255, 0.08);
}

* { box-sizing: border-box; }
button, input { font: inherit; }
button:focus-visible, input:focus-visible { outline: 2px solid var(--border-focus); outline-offset: 2px; }
body { margin: 0; background: var(--bg-canvas); }

[data-theme="light"] {
  --bg-canvas: #f8fafc;
  --bg-surface: #ffffff;
  --bg-panel: #f1f5f9;
  --bg-card: #e2e8f0;
  --bg-card-hover: #cbd5e1;

  --border-subtle: #e2e8f0;
  --border-medium: #cbd5e1;
  --border-focus: #0284c7;

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;
  --text-faint: #94a3b8;
}

[data-density="watch"] {
  --spacing-unit: 14px;
}

/* Animations */
@keyframes pulse-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.font-mono {
  font-family: var(--font-mono);
}

.observatory-shell {
  background:
    radial-gradient(circle at 12% 0%, rgba(0, 210, 255, .11), transparent 28rem),
    radial-gradient(circle at 92% 84%, rgba(228, 184, 106, .07), transparent 24rem),
    linear-gradient(135deg, rgba(255,255,255,.025) 1px, transparent 1px),
    var(--bg-canvas);
  background-size: auto, auto, 28px 28px, auto;
}

.observatory-panel { box-shadow: var(--shadow-glow); }

@media (prefers-reduced-motion: no-preference) {
  .reveal { animation: reveal-in 420ms ease-out both; }
  .reveal:nth-child(2) { animation-delay: 45ms; }
  .reveal:nth-child(3) { animation-delay: 90ms; }
}

@keyframes reveal-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
`;

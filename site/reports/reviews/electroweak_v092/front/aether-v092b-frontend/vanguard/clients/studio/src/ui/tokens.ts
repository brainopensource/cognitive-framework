export const CSS_VARIABLES = `
:root {
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", "Fira Code", "Cascadia Code", monospace;

  /* 2026 SOTA Monochromatic High-Density Palette (Obsidian / Titanium) */
  --bg-canvas: #09090b;       /* Deep Obsidian */
  --bg-surface: #121215;      /* Elevated Obsidian Surface */
  --bg-panel: #18181b;        /* Component Panel */
  --bg-card: #222226;         /* Interactive Card */
  --bg-card-hover: #2a2a30;   /* Hover State */
  --bg-elevated: #323238;     /* Floating Overlays */
  
  --border-subtle: #27272a;   /* Hairline Border */
  --border-medium: #3f3f46;   /* Active / Focused Border */
  --border-strong: #71717a;   /* Highlighted Boundary */
  --border-focus: #fafafa;    /* Keyboard Focus Ring */

  --text-primary: #fafafa;    /* Titanium White */
  --text-secondary: #a1a1aa;  /* Muted Zinc */
  --text-muted: #71717a;      /* Faint Zinc */
  --text-faint: #52525b;      /* Ghost Text */

  /* Precise Semantic Status Signals (Muted & Scientific) */
  --signal-flow: #38bdf8;     /* Sky Blue: Active Execution & Open Lease */
  --signal-proof: #4ade80;    /* Mint Green: Cryptographically Verified */
  --signal-hold: #fbbf24;     /* Amber: Awaiting Ed25519 Human Approval */
  --signal-deny: #f87171;     /* Coral Red: Fail-Closed Denial & Error */
  --signal-void: #c084fc;     /* Violet: Ephemeral Projection / Undeterminable */
  --signal-amber: #eab308;    /* Warning */

  /* Layout & Sizing Tokens */
  --spacing-unit: 8px;
  --header-height: 48px;
  --footer-height: 36px;
  --sidebar-width: 240px;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --shadow-subtle: 0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px -1px rgba(0, 0, 0, 0.4);
  --shadow-elevation: 0 10px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.7);
  --shadow-glow: 0 0 24px rgba(56, 189, 248, 0.08);
}

* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 0;
  background: var(--bg-canvas);
  color: var(--text-primary);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

button, input, select, textarea {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: var(--bg-surface);
}
::-webkit-scrollbar-thumb {
  background: var(--border-subtle);
  border-radius: var(--radius-sm);
}
::-webkit-scrollbar-thumb:hover {
  background: var(--border-medium);
}

.font-mono {
  font-family: var(--font-mono);
}

.observatory-shell {
  background-color: var(--bg-canvas);
  background-image:
    radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 100%, rgba(192, 132, 252, 0.03) 0%, transparent 40%),
    linear-gradient(to right, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
}

.hairline-border {
  border: 1px solid var(--border-subtle);
}

.badge-mono {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

@keyframes pulse-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes slide-down {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-slide-down {
  animation: slide-down 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
`;


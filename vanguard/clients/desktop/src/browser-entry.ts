/**
 * Browser entry point for the AETHER Desktop workspace.
 *
 * The desktop UI is plain DOM, so it runs unchanged inside a Chromium app
 * window served from loopback. What it must not do is reach for the Unix
 * domain socket: `SocketRuntimeClient` needs `node:net`, which no page has.
 * The gateway speaks the same protocol over HTTP, so this entry uses
 * `HttpRuntimeClient` against the same origin the page was served from, and
 * the local dev server proxies `/api/*` through to the Python gateway.
 */
import { HttpRuntimeClient } from "@aether/client";
import { DesktopApp } from "./components/App.js";
import { DesktopKeychainSigner } from "./bridge/keychain-signer.js";
import { DesktopStore } from "./state/desktop-store.js";

type DesktopConfig = {
  workspacePath?: string;
  gatewayUrl?: string;
};

function fatal(root: HTMLElement, heading: string, detail: string): void {
  root.innerHTML = "";
  const panel = document.createElement("div");
  panel.style.cssText = [
    "font-family: ui-monospace, SFMono-Regular, Menlo, monospace",
    "background: #11111b",
    "color: #cdd6f4",
    "height: 100vh",
    "display: flex",
    "flex-direction: column",
    "gap: 12px",
    "align-items: center",
    "justify-content: center",
    "padding: 32px",
    "text-align: center",
  ].join(";");
  const title = document.createElement("h1");
  title.textContent = heading;
  title.style.cssText = "font-size: 18px; margin: 0; color: #f38ba8;";
  const body = document.createElement("pre");
  body.textContent = detail;
  body.style.cssText = "margin: 0; white-space: pre-wrap; font-size: 13px; color: #a6adc8; max-width: 720px;";
  panel.append(title, body);
  root.appendChild(panel);
}

async function loadConfig(): Promise<DesktopConfig> {
  try {
    const response = await fetch("/desktop-config.json", { cache: "no-store" });
    if (!response.ok) return {};
    return (await response.json()) as DesktopConfig;
  } catch {
    return {};
  }
}

async function main(): Promise<void> {
  const root = document.getElementById("root");
  if (!root) return;

  const config = await loadConfig();
  const baseUrl = config.gatewayUrl ?? window.location.origin;

  // Probe before mounting. A dead gateway otherwise shows up as an empty
  // transcript pane rather than as the connection failure it is.
  try {
    const health = await fetch(`${baseUrl}/api/health`, { cache: "no-store" });
    if (!health.ok) throw new Error(`HTTP ${health.status}`);
  } catch (error) {
    fatal(
      root,
      "Runtime gateway unreachable",
      `The desktop UI could not reach the AETHER Studio Gateway at ${baseUrl}/api/health.\n\n` +
        `${String(error)}\n\n` +
        `Start it with:\n    uv run vanguard-studio --port 8000 --workspace .\n\n` +
        `or relaunch the whole stack with:\n    ./bin/aether-desktop`,
    );
    return;
  }

  const client = new HttpRuntimeClient({
    baseUrl,
    signer: new DesktopKeychainSigner(),
  });

  const app = new DesktopApp({
    client,
    store: new DesktopStore({
      client,
      runtimeTarget: { httpUrl: baseUrl, transport: "http" },
    }),
  });

  // The gateway serves one workspace root, chosen at launch. Adopting it here
  // keeps the composer from defaulting to "." -- a path that means the page's
  // origin, not the repository the agents will actually edit.
  if (config.workspacePath) {
    app.store.controller.selectWorkspace(config.workspacePath);
  }

  app.mount(root);
  await app.store.connectRuntime();
}

// A blank window is the worst failure report there is: it looks like the app
// simply did not start. Anything thrown on the mount path gets rendered.
window.addEventListener("error", (event) => {
  const root = document.getElementById("root");
  if (root && !root.firstChild) {
    fatal(root, "Desktop failed to start", String(event.error?.stack ?? event.message));
  }
});

main().catch((error) => {
  const root = document.getElementById("root");
  if (root) {
    fatal(root, "Desktop failed to start", String((error as Error)?.stack ?? error));
  }
});

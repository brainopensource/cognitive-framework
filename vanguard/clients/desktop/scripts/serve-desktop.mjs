/**
 * Static host for the desktop bundle, with a pass-through proxy to the Python
 * Studio Gateway.
 *
 * Same-origin is the point. The gateway echoes only configured origins on
 * `Access-Control-Allow-Origin` and refuses wildcards, so a page served from a
 * different port would need `VANGUARD_GATEWAY_ORIGINS` set before a single
 * request succeeded. Proxying `/api/*` here means the page and the runtime
 * share one origin and CORS never enters the picture.
 */
import { createServer, request as httpRequest } from "node:http";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { resolve, dirname, extname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "../dist-browser");

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
};

export function createDesktopServer({ gatewayPort = 8000, workspacePath = process.cwd() } = {}) {
  return createServer((req, res) => {
    const pathname = new URL(req.url ?? "/", "http://127.0.0.1").pathname;

    if (pathname === "/desktop-config.json") {
      res.writeHead(200, { "Content-Type": MIME_TYPES[".json"], "Cache-Control": "no-store" });
      res.end(JSON.stringify({ workspacePath, gatewayPort }));
      return;
    }

    if (pathname.startsWith("/api/")) {
      const proxyReq = httpRequest(
        {
          host: "127.0.0.1",
          port: gatewayPort,
          path: req.url,
          method: req.method,
          headers: { ...req.headers, host: `127.0.0.1:${gatewayPort}` },
        },
        (proxyRes) => {
          // SSE must not be buffered: `flushHeaders` plus per-chunk writes keep
          // `events:stream` incremental instead of arriving all at once on close.
          res.writeHead(proxyRes.statusCode ?? 200, proxyRes.headers);
          res.flushHeaders?.();
          proxyRes.on("data", (chunk) => {
            res.write(chunk);
            res.flush?.();
          });
          proxyRes.on("end", () => res.end());
        },
      );
      proxyReq.on("error", (err) => {
        if (res.headersSent) return res.end();
        res.writeHead(503, { "Content-Type": MIME_TYPES[".json"] });
        res.end(
          JSON.stringify({
            error: `AETHER Studio Gateway is not answering on 127.0.0.1:${gatewayPort}`,
            detail: String(err),
          }),
        );
      });
      req.on("aborted", () => proxyReq.destroy());
      req.pipe(proxyReq);
      return;
    }

    const requested = pathname === "/" ? "/index.html" : pathname;
    const filePath = resolve(root, `.${requested}`);
    if (!filePath.startsWith(root)) {
      res.writeHead(403);
      res.end("Forbidden");
      return;
    }
    readFile(filePath).then(
      (body) => {
        res.writeHead(200, {
          "Content-Type": MIME_TYPES[extname(filePath)] ?? "application/octet-stream",
        });
        res.end(body);
      },
      () => {
        res.writeHead(404);
        res.end("Not found");
      },
    );
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.env.AETHER_DESKTOP_PORT ?? 4180);
  const gatewayPort = Number(process.env.AETHER_GATEWAY_PORT ?? 8000);
  createDesktopServer({ gatewayPort }).listen(port, "127.0.0.1", () => {
    console.log(`AETHER Desktop: http://127.0.0.1:${port} (API proxy -> 127.0.0.1:${gatewayPort})`);
  });
}

import { createServer, request as httpRequest } from "node:http";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { resolve, dirname, extname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "../dist-browser");
const PYTHON_GATEWAY_PORT = 8000;

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

const server = createServer(async (req, res) => {
  const urlObj = new URL(req.url ?? "/", "http://127.0.0.1:4173");
  const pathname = urlObj.pathname;

  // Proxy /api/* to Python Gateway
  if (pathname.startsWith("/api/")) {
    const proxyReq = httpRequest(
      {
        host: "127.0.0.1",
        port: PYTHON_GATEWAY_PORT,
        path: req.url,
        method: req.method,
        headers: req.headers,
      },
      (proxyRes) => {
        res.writeHead(proxyRes.statusCode || 200, proxyRes.headers);
        proxyRes.pipe(res);
      }
    );

    proxyReq.on("error", () => {
      res.writeHead(503, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Python Studio Gateway offline on port 8000" }));
    });

    req.pipe(proxyReq);
    return;
  }

  // Serve static files from dist-browser/
  const requested = pathname === "/" ? "/index.html" : pathname;
  const path = resolve(root, `.${requested}`);
  if (!path.startsWith(root)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  try {
    const body = await readFile(path);
    const contentType = MIME_TYPES[extname(path)] ?? "application/octet-stream";
    res.writeHead(200, { "Content-Type": contentType });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
});

server.listen(4173, "127.0.0.1", () => {
  console.log("AETHER Observatory: http://127.0.0.1:4173 (API proxy -> 127.0.0.1:8000)");
});


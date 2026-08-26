import { createServer, request as httpRequest } from "node:http";
import { readFile } from "node:fs/promises";
import { resolve, extname } from "node:path";

const root = resolve("dist-browser");
const PYTHON_GATEWAY_PORT = 8000;

const server = createServer(async (req, res) => {
  // Proxy /api/* to Python Gateway
  if (req.url && req.url.startsWith("/api/")) {
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
  const requested = req.url === "/" ? "/index.html" : req.url ?? "/index.html";
  const path = resolve(root, `.${requested}`);
  if (!path.startsWith(root)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  try {
    const body = await readFile(path);
    res.writeHead(200, { "Content-Type": extname(path) === ".js" ? "text/javascript" : "text/html" });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
});

server.listen(4173, "127.0.0.1", () => {
  console.log("AETHER Observatory: http://127.0.0.1:4173 (API proxy -> 127.0.0.1:8000)");
});


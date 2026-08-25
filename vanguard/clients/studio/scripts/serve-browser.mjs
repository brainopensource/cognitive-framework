import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { resolve, extname } from "node:path";

const root = resolve("dist-browser");
const server = createServer(async (request, response) => {
  const requested = request.url === "/" ? "/index.html" : request.url ?? "/index.html";
  const path = resolve(root, `.${requested}`);
  if (!path.startsWith(root)) { response.writeHead(403); response.end("Forbidden"); return; }
  try { const body = await readFile(path); response.writeHead(200, { "Content-Type": extname(path) === ".js" ? "text/javascript" : "text/html" }); response.end(body); }
  catch { response.writeHead(404); response.end("Not found"); }
});
server.listen(4173, "127.0.0.1", () => console.log("AETHER Observatory: http://127.0.0.1:4173"));

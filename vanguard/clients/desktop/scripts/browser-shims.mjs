/**
 * esbuild plugin: resolve Node built-ins for the browser desktop bundle.
 *
 * `@aether/client` is one package serving two hosts. Its barrel re-exports the
 * managed-runtime host, the operator signer and the UDS transport, all of which
 * import `node:*` at module scope. The browser never *calls* them -- it uses
 * `HttpRuntimeClient` plus `WebCryptoSigner` -- but ESM hoists the imports, so
 * the bundle will not load without a resolution for each specifier.
 *
 * Two kinds of shim, and the difference is deliberate:
 *
 *   - Pure functions (`node:path`, `node:url`, `randomUUID`) get real
 *     implementations. They compute the same answer in either host.
 *   - Everything a browser genuinely cannot do (`node:fs`, `node:net`,
 *     `node:os`, `node:child_process`) throws a named error when called. A
 *     stub that returned a plausible-looking value would let the UI render a
 *     fabricated home directory or silently drop a write.
 */

const UNAVAILABLE = {
  "node:fs": [
    "existsSync", "mkdirSync", "readFileSync", "writeFileSync", "chmodSync",
    "unlinkSync", "createWriteStream",
  ],
  "node:fs/promises": ["readFile", "writeFile", "mkdir"],
  "node:os": ["homedir", "platform", "tmpdir"],
  "node:net": ["createConnection", "connect"],
  "node:child_process": ["spawn", "spawnSync", "exec", "execSync"],
  "node:readline": ["createInterface"],
};

const PURE = {
  "node:path": `
const norm = (p) => {
  const abs = p.startsWith("/");
  const out = [];
  for (const seg of p.split("/")) {
    if (!seg || seg === ".") continue;
    if (seg === "..") { if (out.length && out[out.length - 1] !== "..") out.pop(); else if (!abs) out.push(".."); continue; }
    out.push(seg);
  }
  return (abs ? "/" : "") + out.join("/");
};
export const join = (...parts) => norm(parts.filter(Boolean).join("/")) || ".";
export const resolve = (...parts) => {
  let acc = "/";
  for (const part of parts) { if (!part) continue; acc = part.startsWith("/") ? part : acc + "/" + part; }
  return norm(acc) || "/";
};
export const dirname = (p) => { const i = norm(p).lastIndexOf("/"); return i > 0 ? norm(p).slice(0, i) : i === 0 ? "/" : "."; };
export const basename = (p) => norm(p).split("/").pop() ?? "";
export const extname = (p) => { const b = basename(p); const i = b.lastIndexOf("."); return i > 0 ? b.slice(i) : ""; };
export const sep = "/";
export default { join, resolve, dirname, basename, extname, sep };
`,
  "node:url": `
export const fileURLToPath = (url) => {
  const href = typeof url === "string" ? url : String(url);
  if (!href.startsWith("file://")) {
    throw new TypeError("fileURLToPath: not a file: URL (browser desktop bundle)");
  }
  return decodeURIComponent(href.slice("file://".length)) || "/";
};
export const pathToFileURL = (p) => new URL("file://" + encodeURI(p));
export default { fileURLToPath, pathToFileURL };
`,
  // WebCrypto supplies randomUUID on secure contexts, and 127.0.0.1 counts as one.
  "node:crypto": `
export const randomUUID = () => globalThis.crypto.randomUUID();
const denied = (name) => () => {
  throw new Error(name + "() is unavailable in the browser desktop bundle: approvals are signed by WebCryptoSigner, not the Node operator signer.");
};
export const generateKeyPairSync = denied("generateKeyPairSync");
export const sign = denied("sign");
export const createPrivateKey = denied("createPrivateKey");
export default { randomUUID, generateKeyPairSync, sign, createPrivateKey };
`,
};

function deniedModule(specifier, names) {
  const body = names
    .map(
      (n) =>
        `export function ${n}() { throw new Error(${JSON.stringify(
          `${specifier}.${n}() is unavailable in the browser desktop bundle. This code path needs the Node or Tauri host.`,
        )}); }`,
    )
    .join("\n");
  return `${body}\nexport default { ${names.join(", ")} };\n`;
}

export function nodeBrowserShims() {
  const specifiers = [...Object.keys(UNAVAILABLE), ...Object.keys(PURE)];
  const filter = new RegExp(
    `^(node:)?(${specifiers.map((s) => s.replace("node:", "").replace("/", "\\/")).join("|")})$`,
  );
  return {
    name: "aether-node-browser-shims",
    setup(build) {
      build.onResolve({ filter }, (args) => ({
        path: args.path.startsWith("node:") ? args.path : `node:${args.path}`,
        namespace: "node-shim",
      }));
      build.onLoad({ filter: /.*/, namespace: "node-shim" }, (args) => ({
        contents: PURE[args.path] ?? deniedModule(args.path, UNAVAILABLE[args.path] ?? []),
        loader: "js",
      }));
    },
  };
}

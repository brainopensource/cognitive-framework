# `@aether/desktop`

The AETHER desktop workspace: sidebar, transcript, composer, approval banner,
forensic drawer and command palette, rendered as plain DOM over
`FrontendAppController`.

## Running it on Linux

```bash
uv sync          # Python runtime + Studio Gateway
npm install      # workspace packages
./bin/aether-desktop
```

With no `--workspace` it opens on the current directory. To point it at another
repository, give a real path — `--workspace ~/Coding/some-project`. The gateway
creates `.vanguard/` inside whatever you name, so the directory has to exist and
be writable.

`bin/aether-desktop` builds the browser bundle, starts the Studio Gateway on
`127.0.0.1:8000`, serves the UI on `127.0.0.1:4180`, and opens a window.

| Flag | Meaning |
|---|---|
| `--workspace <dir>` | Repository the agents operate on (default: cwd) |
| `--port <n>` | UI port on loopback (default: 4180) |
| `--gateway-port <n>` | Studio Gateway port (default: 8000) |
| `--no-gateway` | Attach to a gateway that is already running |
| `--no-open` | Print the URL instead of opening a window |
| `--no-build` | Serve `dist-browser/` as-is |

Everything binds loopback only. The gateway refuses a non-loopback bind unless
`VANGUARD_GATEWAY_TOKENS` is set, because that surface resolves approvals and
launches runs.

### The window

With a Chromium-family browser installed the launcher opens a frameless
`--app=` window on a throwaway profile, which is as close to a native window as
this gets without shipping an Electron runtime. With only Firefox available it
opens an ordinary browser window instead — `sudo dnf install chromium` (Fedora)
gets the frameless one.

## Why HTTP and not the Unix socket

`src/browser-entry.ts` uses `HttpRuntimeClient`, never `SocketRuntimeClient`.
The UDS transport needs `node:net`, which a page does not have; the gateway
speaks the same `vg.4` protocol over HTTP and SSE. `scripts/serve-desktop.mjs`
proxies `/api/*` to the gateway so the page and the runtime share one origin,
which keeps the gateway's deliberately strict CORS policy out of the way.

Approvals are signed in-page by `DesktopKeychainSigner`, which delegates to
`WebCryptoSigner` (Ed25519 via WebCrypto) outside Tauri.

`scripts/browser-shims.mjs` resolves the `node:*` specifiers that reach the
bundle through the `@aether/client` barrel. Pure modules (`node:path`,
`node:url`, `randomUUID`) get real implementations; anything a browser genuinely
cannot do throws a named error rather than returning a plausible-looking
fabrication.

## Developing

```bash
npm --workspace @aether/desktop run build:browser   # bundle to dist-browser/
npm --workspace @aether/desktop run dev             # bundle + serve on :4180
npm --workspace @aether/desktop test                # tsc + node --test
```

`npm run dev` expects a gateway already listening on `:8000`:

```bash
uv run vanguard-studio --port 8000 --workspace .
```

## Tauri

`src/bridge/tauri-bridge.ts` targets a native shell that does not exist in this
repository yet. Every method degrades to a browser-safe path when
`__TAURI_INTERNALS__` is absent, so the bridge is a seam, not a dependency.

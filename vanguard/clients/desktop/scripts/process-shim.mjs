// Injected as the `process` global for the browser bundle.
//
// `@aether/client` reads `process.env.*` for socket/home overrides and
// `process.versions.node` to decide whether the filesystem persistence adapter
// is usable. In a browser both answers are "no", and this shim says so
// truthfully: no env overrides, no Node, so the controller keeps its
// LocalStorage adapter instead of silently discarding writes.
export const process = {
  env: {},
  versions: {},
  platform: "browser",
  argv: [],
  cwd: () => "/",
};

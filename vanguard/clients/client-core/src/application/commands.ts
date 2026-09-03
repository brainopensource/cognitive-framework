// F4 Phase 5: ported to @aether/client (the converged AETHER client SDK).
// This re-export shim keeps every existing @vanguard/client-core consumer
// working unchanged while there is exactly one implementation underneath.
// coding-commands.ts still imports jsonLine and renderProjectionLines from
// their sibling modules by relative path, which resolve correctly through
// these shims without any change on its side.
export * from "@aether/client/application/commands.js";

// F4 Phase 5: ported to @aether/client (the converged AETHER client SDK).
// This re-export shim keeps every existing @vanguard/client-core consumer
// working unchanged while there is exactly one implementation underneath.
// coding-commands.ts's local `import { jsonLine } from "./commands.js"` and
// `import { renderProjectionLines } from "./coding-receipts.js"` still
// resolve correctly through this shim.
export * from "@aether/client/application/commands.js";

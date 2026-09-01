// F4 Phase 5: ported to @aether/client (the converged AETHER client SDK).
// This re-export shim keeps every existing @vanguard/client-core consumer
// working unchanged while there is exactly one implementation underneath.
// Safe to shim now: the CLI's cutover to @aether/client's split
// requestResume(runId, options) call convention landed in the same phase.
export * from "@aether/client/application/resume.js";

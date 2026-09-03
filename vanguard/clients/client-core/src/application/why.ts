// F4 Phase 3: ported to @aether/client (the converged AETHER client SDK).
// This re-export shim keeps every existing @vanguard/client-core consumer
// working unchanged while there is exactly one implementation underneath.
// Safe to shim (unlike resume.ts/commands.ts this phase): why.ts never
// calls a RuntimeClient method itself, it only formats an already-obtained
// Result<ArtifactExplanation>, so there is no bundled-vs-split call
// convention to break.
export * from "@aether/client/application/why.js";

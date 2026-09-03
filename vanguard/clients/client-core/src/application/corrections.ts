// F4 Phase 5: ported to @aether/client (the converged AETHER client SDK),
// standardized on the canonical vg.4 CorrectionRecord shape. This re-export
// shim keeps every existing @vanguard/client-core consumer working
// unchanged while there is exactly one implementation underneath -- safe
// now that the CLI's real consumer (run-tui.tsx) has cut over to
// @aether/client's RuntimeClient for its whole runtime object.
export * from "@aether/client/application/corrections.js";

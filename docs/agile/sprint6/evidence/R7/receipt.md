# Gate R7 Evidence Receipt — ModelPort & Context Compiler Wiring

**Date:** 2026-08-15  
**Gate:** R7 (ModelPort & Context Compiler Wiring)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14, `ADR-0045`, `ADR-0046`, `ADR-0047`  

---

## 1. Adapter Implementation & Features
- **Component:** `vanguard.packages.adapters.models.openrouter` & `vanguard.packages.agency.context.compiler`
- **Unit Suite:** `python3 -m unittest test.adapters.test_openrouter` (21 tests passed)
- **Features Implemented:**
  1. **Streaming SSE Parsing:** Reassembles chunked Server-Sent Events (`choices[0].delta`) into text and tool calls across streaming fragments.
  2. **TTFT Monotonic Timing:** Time-to-first-token measured in integer milliseconds (`ttft_millis: int`) via `time.monotonic()`.
  3. **Integer Micros Accounting:** Integer token counts and USD micros calculated using `MODEL_PRICING_MICROS` and `calculate_cost_micros()`.
  4. **Explicit Pricing Known Status:** Explicit `pricing_known: bool` flag returned in usage structure.
  5. **Secret Redaction:** Raw secrets are scrubbed from all error messages and logs; credentials referenced solely by env name (`OPENROUTER_API_KEY`).
  6. **Immutable Context Prefix:** L1–L3 system core and tool schemas remain byte-identical across multi-turn episodes; L5 dialogue notes record tool execution outcomes with provenance.

## 2. Adversarial Broken Controls
- `MF-CTX-001`: Direct bypass of compiled context fails closed.
- `MF-CTX-002`: Missing tool observations on turn 2 fails closed.
- `MF-SEC-002`: Secret leaked in event envelope fails closed.

## 3. Verdict
All ModelPort and ContextCompiler requirements are fully implemented, tested, and adversarially validated.

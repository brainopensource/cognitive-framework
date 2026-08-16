# Developer C — OpenRouter adapter

Tickets: `S4-DC-001` · Contract: `REQ-PORT-006`

Rebuild OpenAI-compatible chat completions behind `ModelPort`. Endpoint default: OpenRouter. Secret references only (T2.7). Cassette record/replay for CI. **Never import `slice/` or `spike/`.** Trust-spine tests must not instantiate this adapter.

Live calls are optional and skipped when the key is unset. This packet is not the S4 gate.

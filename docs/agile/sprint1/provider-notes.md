# Provider API Notes — Task T0a Synthesis

Moved here from `spike/provider_notes.md` ahead of the `S4-GATE-001` deletion
of `spike/` and `slice/`. The notes are the part of a disposable worth keeping
(`ADR-0047`). Rebuild adapters from this file; do not resurrect `spike/`.

Status: `PROBE COMPLETE — SIMULATION & WIRE TAXONOMY CAPTURED`  
Owner: Dev 3 (Provider Integration Track)  
Authority: Non-normative technical discovery for Task `T0a` / Sprint 1.

---

## 1. Provider Wire Protocol & Streaming Semantics

### 1.1 Server-Sent Events (SSE) Streaming
* **Wire Protocol**: Providers (OpenAI, Anthropic, Gemini v1beta) stream delta events over `text/event-stream`.
* **Payload Chunking**:
  * OpenAI / Anthropic emit `data: {"choices": [{"delta": {"content": "..."}}]}`.
  * Gemini emits `data: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}`.
* **Latency Profile**:
  * **Time-to-First-Token (TTFT)**: ~150ms – 450ms depending on prompt size and provider cache hits.
  * **Time-to-Last-Token (TTLT)**: Linear in generation length ($\approx 25–40\text{ ms/token}$).
  * **Recommendation for `ModelPort`**: `ModelPort.stream(prompt)` must yield typed delta tokens asynchronously and emit terminal usage metadata upon stream close.

---

## 2. Token Accounting Quirks & Pricing Nuances

### 2.1 Prompt Caching
* Modern SOTA providers (Gemini, Anthropic, OpenAI) offer prefix caching discounts (up to 75–90% reduction on cached prompt tokens).
* **Wire Requirement**: Context layer ordering (`L1 SYSTEM / L2 TOOLS / L3 ENVIRONMENT / L4 TASK / L5 DIALOGUE` per `T4.9`) **must remain byte-prefix stable** to leverage cache economics.
* **Metadata Field**: The `Receipt` and `Recording` contracts must capture `cached_prompt_tokens` separately from `uncached_prompt_tokens`.

### 2.2 Thinking / Reasoning Tokens
* Models like Gemini 2.0 Flash Thinking or Claude 3.7 / DeepSeek R1 emit separate "thought" parts before the final response.
* **Wire Behavior**: Some providers bill reasoning tokens as output completion tokens but may or may not return them in the visible content parts.
* **Recommendation**: `ModelPort` response schema must include an optional `thinking_content` block to preserve causal reasoning traces without polluting final text diffs.

---

## 3. Error Taxonomy & Resilience Policy

| Error Kind | HTTP Status | Response Payload Shape | Recommended System Reaction |
|---|---|---|---|
| **Rate Limit / Quota** | `429 Too Many Requests` | `{"error": {"code": "RESOURCE_EXHAUSTED", "status": "RESOURCE_EXHAUSTED"}}` | Parse `Retry-After` header if present; back off with jitter; do **not** fail episode. |
| **Context Overflow** | `400 Bad Request` | `{"error": {"code": "INVALID_ARGUMENT", "message": "Token count exceeds limit"}}` | Trigger context compaction / re-grounding; emit alertable event. |
| **Provider Overload** | `503 Service Unavailable` | `{"error": {"code": "UNAVAILABLE", "message": "Server temporarily overloaded"}}` | Exponential backoff retry up to lease budget ceiling. |
| **Authentication** | `401 Unauthorized` | `{"error": {"code": "UNAUTHENTICATED"}}` | Fast-fail immediately; notify control plane. |

---

## 4. Recommendations for Core Ports & Cassettes

1. **Deterministic Cassette Recorder (`T3.8`)**:
   * Record exact request payload digest (`prompt`, `seed`, `temperature`, `model`) and exact raw response chunks into `cassette_<digest>.jsonl`.
   * On replay, serve cached byte-for-byte stream with identical chunk boundaries to guarantee 100% reproducible execution.
2. **Strict Package Isolation**:
   * The actual provider SDKs or HTTP clients belong strictly inside `vanguard/packages/adapters/model/`.
   * `ports/model.py` defines the abstract interface (`ModelPort`), ensuring `agency` and `kernel` remain 100% provider-agnostic.

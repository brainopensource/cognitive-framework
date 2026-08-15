# adapters

Fake and real port implementations. May import `domain` and `ports` only. Adapter families may not import one another.

`stores/` contains the deterministic in-memory `EventStorePort` fake and its SQLite/WAL real adapter. `models/` contains the `ModelPort` cassette player, scripted fake, and rebuilt OpenRouter adapter (`models/openrouter.py`; not imported by `TEST-TRUST-001`). `evaluators/` contains the `EvaluatorPort` fake; agency must not import it. `sandbox/` contains the visibly non-contained `SandboxRunner` fake and the rootless perimeter adapter. `models/cassette.py` is replay infrastructure, not a live provider adapter. Do not import or recreate `spike/` or `slice/`; rebuild from `docs/sprint1/provider-notes.md` and `docs/sprint2/slice-findings.md`.

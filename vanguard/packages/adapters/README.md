# adapters

Fake and real port implementations. May import `domain` and `ports` only. Adapter families may not import one another.

`stores/` contains the deterministic in-memory `EventStorePort` fake and its SQLite/WAL real adapter. `models/` contains the `ModelPort` cassette player, scripted fake, and rebuilt OpenRouter adapter (`models/openrouter.py`; not imported by `TEST-TRUST-001`). `evaluators/` contains the `EvaluatorPort` fake; agency must not import it. `sandbox/` contains the visibly non-contained `SandboxRunner` fake; unverified reports block publication. `models/cassette.py` is replay infrastructure, not a live provider adapter. The disposable provider probe remains wholly inside `slice/` and is never a production dependency.

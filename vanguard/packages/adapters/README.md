# adapters

Fake and real port implementations. May import `domain` and `ports` only. Adapter families may not import one another.

`stores/` contains the deterministic in-memory `EventStorePort` fake and its SQLite/WAL real adapter. `models/` contains the `ModelPort` cassette player, scripted fake, and (Sprint 4) rebuilt OpenRouter adapter. `models/cassette.py` is replay infrastructure, not a live provider adapter. The disposable provider probe remains wholly inside `slice/` and is never a production dependency.

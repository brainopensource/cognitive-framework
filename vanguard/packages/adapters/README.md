# adapters

Fake and real port implementations. May import `domain` and `ports` only. Adapter families may not import one another.

`fakes/` contains deterministic, in-memory implementations for the T0b port surface. The disposable real provider adapter lives in `slice/` and is deleted at S4; it is never a production dependency.

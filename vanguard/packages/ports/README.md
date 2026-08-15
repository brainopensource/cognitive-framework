# ports

Interfaces and typed failure contracts only. May import `domain` only; concrete fakes and real adapters belong in `adapters/`.

The Sprint T0b surface is `ModelProvider`, `EnvironmentAdapter`, `EvaluatorPort`, `EventStore`, `BlobStore`, `IndexPort`, `ClockPort`, and `RandomPort`. See `contracts.ts` for substitutability rules.

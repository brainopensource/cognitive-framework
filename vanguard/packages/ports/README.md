# ports

Interfaces and typed failure contracts only. This package may import `domain` only; concrete fakes and real adapters belong in `adapters/`.

Only ports whose full activation bundle is present belong here: interface, shared contract suite, deterministic fake, and real adapter. The active storage seam is `EventStorePort`; its in-memory fake and SQLite/WAL adapter are in `adapters/stores/`. Kernel collaboration protocols are in `kernel.py` and do not create alternate effect paths.

The disposable T0b provider vocabulary remains local to `slice/`. Planned provider, environment, evaluator, blob, observation, policy, governor, sandbox, clock, and random ports must not be added here until their activation bundle lands. See `schemas/v4/port-interfaces.md`.

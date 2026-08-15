# ports

Interfaces and typed failure contracts only. This package may import `domain` only; concrete fakes and real adapters belong in `adapters/`.

Only ports whose full activation bundle is present belong here: interface, shared contract suite, deterministic fake, and real adapter. The active storage seam is `EventStorePort`; its in-memory fake and SQLite/WAL adapter are in `adapters/stores/`. Kernel collaboration protocols are in `kernel.py` and do not create alternate effect paths.

`ModelPort` is activated with a shared suite (`test/contracts/test_model_port.py`) and deterministic cassette/scripted fakes in `adapters/models/`. Live OpenRouter is `REQ-PORT-006` and must not land in this package. Provider failures are typed `instrument_error` values, never task failures.

`EvaluatorPort` is activated with a fixed-verdict fake and `test/contracts/test_evaluator_port.py`. Agency must not import it. Exterior OS identity is Sprint 5.

The disposable T0b provider vocabulary remains local to `slice/`. Planned environment, blob, observation, policy, governor, sandbox, clock, and random ports must not be added here until their activation bundle lands. See `schemas/v4/port-interfaces.md`.

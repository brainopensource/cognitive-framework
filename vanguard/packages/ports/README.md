# ports

Interfaces and typed failure contracts only. This package may import `domain` only; concrete fakes and real adapters belong in `adapters/`.

Only ports whose full activation bundle is present belong here: interface, shared contract suite, deterministic fake, and real adapter. The active storage seam is `EventStorePort`; its in-memory fake and SQLite/WAL adapter are in `adapters/stores/`. Kernel collaboration protocols are in `kernel.py` and do not create alternate effect paths.

`ModelPort` is activated with a shared suite (`test/contracts/test_model_port.py`) and deterministic cassette/scripted fakes in `adapters/models/`. The OpenRouter adapter (`REQ-PORT-006`) lives in `adapters/models/openrouter.py` and must not be imported from this package. Provider failures are typed `instrument_error` values, never task failures.

`EvaluatorPort` is activated with a fixed-verdict fake and `test/contracts/test_evaluator_port.py`. Agency must not import it. Exterior OS identity is Sprint 5.

`SandboxRunner` is activated with a visibly non-contained fake and `test/contracts/test_sandbox_port.py`. Unverified containment reports block publication. The real perimeter adapter is Sprint 4 (`REQ-SEC-001`).

T0a/T0b disposable trees are gone (`S4-GATE-001`). Provider wire notes live in `docs/sprint1/provider-notes.md`; slice findings live in `docs/sprint2/slice-findings.md`. Planned blob, observation, policy, governor, clock, and random ports must not be added here until their activation bundle lands. See `schemas/v4/port-interfaces.md`.

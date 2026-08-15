# T0b disposable-slice findings

Status: deterministic path proven; live-provider run pending a disposable credential and expendable repository.

- Provider text cannot be treated as a patch: extraction, repository containment, and `git apply --check` are distinct failure stages.
- Human approval must see the exact patch and file stat after validation, not only the model's explanation.
- A test command must cross the boundary as argv. Accepting a shell string would add quoting ambiguity and injection before the permanent environment adapter exists.
- Repository root and working directory are operational contract fields. The runner rejects a subdirectory even when Git can discover a parent root.
- Provider failure, invalid patch, human rejection, apply failure, and test failure are different outcomes; collapsing them would make the future ledger misleading.
- The provider response shape and patch latency still require one live run. No numbers are claimed until that receipt exists.

Nothing in this directory is suitable for promotion. T6.1 rebuilds provider and Git adapters behind activated ports; S4 deletes this directory.

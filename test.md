Perform a full independent technical review and refactor plan of the entire project—code, architecture, docs, tests, migration path, and product goals—and, if the current plan is materially flawed, replace it with a cleaner plan from first principles while preserving only what remains justified by the evidence and the project goals.


cd /home/rocha/Coding/Aether-D-System && git status && echo "---" && git branch --show-current && git rev-parse HEAD && git log -1 --oneline && echo "---" && git diff --stat && echo "---STAGED---" && git diff --cached --stat
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
---
main
4f9f8b11c5454ce5d414799fe96c7d666888c3da
4f9f8b1 (HEAD -> main, origin/main) docs: V0.6.0-BETA Locked. Director Review is next
---
---STAGED---

Current review baseline: main @ 4f9f8b1, synced with origin/main, clean working tree, with v0.6 Concept Lock, SPEC, ADRs 0069–0074, GAMMA, and the foundation gap register committed; production implementation for Waves has not started.





| Wave                       | Sprint | Task                                 | Dev tier  |   Score |
| -------------------------- | ------ | ------------------------------------ | --------- | ------: |
| **W0 — CI Truth**          | S0.1   | Rewire CI to `packages/`             | Senior    |      65 |
|                            |        | Collect integration/governance tests | Average   |      35 |
|                            |        | Fix stale oracle paths               | Junior    |      25 |
|                            |        | Wire codegen `--check`               | Average   |      40 |
|                            | S0.2   | Add F-01…F-21 tests                  | Senior    |      70 |
|                            |        | Build duplication detector           | Senior    |      55 |
|                            |        | Separate env-sensitive tests         | Average   |      35 |
| **W1 — Trust Spine**       | S1.1   | Remove fabricated verdict path       | Senior    |      80 |
|                            |        | Verify signed verdict binding        | Principal |      90 |
|                            |        | Enforce writer authority             | Principal |      92 |
|                            |        | Fail-closed capability ceiling       | Senior    |      80 |
|                            | S1.2   | Add full event lineage               | Senior    |      82 |
|                            |        | Complete `D_H` identity              | Senior    |      75 |
|                            |        | Implement trajectory schema          | Senior    |      70 |
|                            |        | Fix spawn attenuation                | Senior    |      78 |
|                            |        | Budget/grant lineage in receipts     | Senior    |      72 |
|                            | S1.3   | Real cold replay from WAL            | Principal |      90 |
|                            |        | Unify selector semantics             | Principal |      88 |
|                            |        | Durable-intent crash tests           | Senior    |      85 |
| **W2 — Convergence**       | S2.1   | Port SPI contracts into packages     | Senior    |      75 |
|                            |        | Port JSON-RPC / UDS                  | Senior    |      82 |
|                            |        | Port plugin lifecycle FSM            | Senior    |      80 |
|                            | S2.2   | Behavioral parity tests              | Principal |      92 |
|                            |        | Remove duplicate kernel/scheduler    | Principal |      95 |
|                            |        | Enforce duplication gate             | Senior    |      65 |
|                            | S2.3   | Split `root.py` in place             | Principal |      90 |
|                            |        | Stabilize canonical composition      | Senior    |      80 |
| **W3 — Plugin Foundation** | S3.1   | Manifest → Resolve → Verify          | Senior    |      78 |
|                            |        | Freeze correct `FrozenHarness`       | Senior    |      82 |
|                            |        | Capability validation at compose     | Senior    |      80 |
|                            | S3.2   | Echo plugin over UDS                 | Average   |      55 |
|                            |        | Full plugin lifecycle                | Senior    |      75 |
|                            |        | Fault/quiesce/restart tests          | Senior    |      78 |
|                            | S3.3   | Extract coding functionality         | Senior    |      72 |
|                            |        | Enforce domain blindness             | Average   |      45 |
| **W4 — Coding E2E**        | S4.1   | Real model → planner                 | Senior    |      72 |
|                            |        | Authorized filesystem effect         | Senior    |      82 |
|                            |        | Sandbox execution                    | Senior    |      85 |
|                            | S4.2   | Patch/edit coding flow               | Senior    |      78 |
|                            |        | Run tests / lint / commands          | Average   |      60 |
|                            |        | Exterior signed evaluation           | Principal |      92 |
|                            | S4.3   | WAL + cold replay E2E                | Principal |      95 |
|                            |        | Valid trajectory emission            | Senior    |      80 |
|                            |        | Final one-runtime proof              | Principal | **100** |

# OD-7 non-author review — Lane 3 / Dev C — 2026-09-15

Reviewer: Dev C (W6a author). Did not author W0/W2a/W2b/W5 source.
Subject inspected: HEAD `5cd3603a` plus uncommitted W6a (not in this review).
Independence basis: pairwise non-author; this reviewer is not the packet author
for A/B leaves. Leadership did not supply these diffs. No `tasks.md` edit
(Senior-owned). `docs/execution/main/*` untouched.

## Accepted (reproduced this session)

| Packet | Subject | Evidence | Notes |
|---|---|---|---|
| **W0** | `test/tools/runner_instrument/test_runner.py` | 8/8 OK incl. grandchild timeout | Counts parse independently of key order; parse miss is not zero; timeout kills the group. |
| **W2a+W2b** | `d614e5ce` then `7a297760` | `test.falsifiers.test_w2a_candidate_identity` 5/5 OK; `test.adapters.test_git_snapshot_identity` OK | W2a was authored red; after W2b the same predicates are green. `snapshot_id` still varies; digest follows content. |
| **W1 slice** | tamper `repo_map` bind in `5cd3603a` | `test.runtime.test_tamper_shield` 8/8 OK | Predicate unchanged: assertion-edit still rejects. Epoch bound via successful `repo_map` so INDEX_UNBOUND no longer masks the shield. |

## Not accepted

| Packet | Reason |
|---|---|
| **W5** (`29b294d1`) | Existing `test.adapters.test_openrouter.OpenRouterModelContract.test_deepseek_dsml_tool_call_is_translated` fails: `proposal contains unsupported fields: ['provider_usd_micros']`. Provider cost was written onto the proposal object, so tool-schema validation rejects a previously passing DSML translation. Packet 4.1 required normalized calls to still pass tool-schema validation. **Reject until the observation lives beside the proposal (usage/diagnostics) and this test is green.** No W5-owned falsifier was found for the accounting split. |
| **W1 remainder** | `5cd3603a` also mixes LDA and W6a test planting | Full `test/runtime` + `test/falsifiers` classification table was not reproduced. Only the tamper-shield slice is accepted. |
| **W3a** | Lane 3 / C lease. Out of OD-7 scope for this reviewer even though reproduced 4/4 green. |

## Environment (not packet defects)

`just check` is red on this tree independently of W6a: `check_path_hygiene.py` vs `docs/research/coding_harness/aux_cli_multi_profiles.md`, `check_doc_metadata.py` vs several `docs/reports/benchmark/quick_benchs/` files, and broken `.draft/temp_auxiliary_table.md` links from `docs/execution/main/{backlog,milestones}.md`. Those files are outside W6a. Ceilings were not raised.

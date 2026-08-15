# Reconstruction and ambiguity report

Status: `INDEPENDENT REVIEW COMPLETED; GAPS FOUND; SIGN-OFF WITHHELD`

The reconstruction below used only the four TSV traces and their referenced `reproduction-evidence.md`. The same repository principal performed the original work and this review, so it is not represented as independent evidence. `tools/check_schema_archaeology.py` independently checks structure, ordering, required fields and trace completeness but cannot judge semantic sufficiency.

## Reconstructed outcomes

| Trace | Reconstructed start | Reconstructed causal path | Accepted end | Ambiguities |
|---|---|---|---|---|
| `BUG-01` | audit returned a vacuous success from repository root | inspect discovery paths → propose repository anchor → patch one tool → verify audit and CV-10 | cwd-safe audit with non-empty registry/disk bijection | original source snapshot unavailable; hands-on time absent |
| `BUG-02` | acceptance verifier crashed opening the registry | inspect direct/nested paths → anchor tools consistently → patch two files → run full verifier | 12/12 mechanical checks, human residues still explicit | original source snapshot unavailable; identity roles share one principal |
| `BUG-03` | rule-map test unexpectedly reported zero rules | inspect generated receipt → identify incompatible input/output cwd → patch generator → rerun and compare digests | truthful 203/28/42/133 report; red gap state retained | exact erroneous-file digests not captured before deletion |
| `NONCODE-01` | authority/topology statements disagreed | classify package, mediation and wire conflicts → map physical names → append ADR → defer schema decision | single physical mapping and explicit unresolved schema ownership | no separate reviewer challenged conflict classification |

## Gaps converted to fields

| Gap | Missing information | Candidate field/control |
|---|---|---|
| `GAP-001` | exact immutable pre-effect source state | `environmentSnapshot` must be mandatory for reproducible effects |
| `GAP-002` | a successful exit did not prove non-empty audit scope | `verificationPopulation` plus expected cardinality/invariant |
| `GAP-003` | command meaning depended on caller cwd | normalised `workingDirectory` in effect descriptor and receipt |
| `GAP-004` | output names changed without an explicit resource set | declared read/write sets and affected resource receipts |
| `GAP-005` | deletion occurred before erroneous artifacts were digested | receipt must enumerate created/modified/deleted resources and pre/post digests |
| `GAP-006` | retrospective work had no human hands-on measurement | capture `handsOnMillis` prospectively for T0 only; do not place it in universal runtime schema |
| `GAP-007` | one principal occupied recorder, reviewer and approver roles | `principal`, `roleAtAction`, and approval identity must remain separate concepts |
| `GAP-008` | local success and governance approval were easy to conflate | explicit evidence status versus approval/activation status |
| `GAP-009` | uncertainty concerned evidence completeness, not only effect occurrence | typed uncertainty scope/reason on reconstruction records |
| `GAP-010` | referenced evidence and receipts were outside the trace-only review corpus | self-contained, content-addressed evidence bundle with resolvable references |
| `GAP-011` | digest labels did not identify byte scope, ordering or the bytes being verified | digest subject, canonicalisation rule and artifact binding |
| `GAP-012` | effects summarized patches/deletions without enumerating changed resources | complete affected-resource list plus patch or pre/post content references |
| `GAP-013` | verification results named counts or success without captured command output and check definitions | executable acceptance definition plus content-addressed stdout/stderr receipt |
| `GAP-014` | the governance trace ended with approvals pending and no final independent judgement | explicit reviewer judgement, authority role and approval state transition |

## Independent review result

An isolated third-engineer agent reviewed only the four trace TSVs on 2026-08-15. It reconstructed all four claimed narratives and added `GAP-010` through `GAP-014`; sign-off was withheld. See `independent-review-2026-08-15.md`. A re-review must receive a self-contained, content-addressed evidence bundle rather than the blank `manual-trace-template.tsv`.

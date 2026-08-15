# Field inventory — T0 evidence synthesis

Status: `EVIDENCE COMPLETE; INDEPENDENT HUMAN SIGN-OFF AND HUMAN TIMING OPEN`  
Owner: repository principal `rocha`, acting Tech Lead  
Evidence: `BUG-01`, `BUG-02`, `BUG-03`, `NONCODE-01`

## Trace register

| Trace | Shape | Acceptance evidence | Structural reconstruction | Human timing |
|---|---|---|---|---|
| `BUG-01` | single-file | cwd-safe audit plus CV-10 | reconstructed | unmeasured |
| `BUG-02` | multi-file | 12/12 mechanical checks | reconstructed | unmeasured |
| `BUG-03` | test-reactive | 203/28/42/133 plus stable generated digests | reconstructed | unmeasured |
| `NONCODE-01` | structured reconciliation | ICD mapping, ADR-0051 and contract deferral | reconstructed | unmeasured |

## Fields evidenced by reconstruction

| Candidate field | Needed by | Why needed | VG-04 owner | Fillable at capture? | Class | v0.1 disposition |
|---|---|---|---|---|---|---|
| `eventId` / `stepId` | all | stable reference and correction target | `EventEnvelope.eventId` | yes | universal | enter |
| `parentEventId` / `previousStepId` | all | reconstruct causal ordering beyond timestamps | `EventEnvelope.parentEventId` | yes | universal | enter |
| `eventKind` | all | distinguish observation, proposal, effect, receipt and judgement | typed event discriminator | yes | universal | enter |
| `principal` | all | identify who observed, acted or approved | `EventEnvelope.principal` | yes | universal | enter |
| `roleAtAction` | NONCODE-01 | distinguish one identity acting under different authorities | not explicit in VG-04 | yes | universal | amend before approval events lock |
| `occurredAt` | all | temporal order and latency | `EventEnvelope.occurredAt` | yes | universal | enter |
| `recordedAt` | all | distinguish occurrence from durable capture | `EventEnvelope.recordedAt` | yes | universal | enter |
| `environmentSnapshot` | BUG-01..03 | make observations/effects reproducible | `EventEnvelope.environmentSnapshot` | yes prospectively | universal | enter and require for environment effects |
| `workingDirectory` | BUG-01..03 | command semantics and discovery scope depended on cwd | execution receipt in VG-04 §5.4 | yes | domain | enter execution receipt |
| `resourceSelector` | all | state exact files/documents affected | capability/resource contracts | yes | universal | enter |
| `readSet` / `writeSet` | BUG-02..03 | expose multi-file coupling and generated outputs | tool contract VG-04 §7 | yes | universal | enter tool descriptor |
| `argsDigest` / normalised args | BUG-01..03 | bind approval and reproduction to exact command | effect descriptor VG-04 §5.5 | yes | universal | enter |
| `purposeDigest` / acceptance ref | all | connect action to task acceptance | grant/task contracts | yes | universal | enter |
| `outcome` | all | separate proposal, observed result and judgement | typed events / Receipt | yes | universal | enter |
| `resultDigest` | BUG-01..03 | prove exact stdout/artifact result | Receipt | yes | universal | enter |
| `affectedResources` with pre/post digests | BUG-03 | reconstruct created/modified/deleted artifacts | not explicit as one receipt field | yes | universal | amend receipt schema |
| `verificationPopulation` | BUG-01,03 | prevent a vacuous success over zero items | not explicit | yes | domain | add to verifier evidence, not EventEnvelope |
| `uncertaintyScope` and `reason` | all | distinguish unknown effect occurrence from incomplete evidence | Receipt only models occurrence outcome | yes | universal evidence record | amend evidence/reconstruction contract |
| provenance axes | all | separate direct source, derived analysis and approval | VG-04 §3 | yes | universal | enter |
| data-policy/redaction fields | all | safely retain outputs and references | EventEnvelope | yes | universal | enter |
| `handsOnMillis` | T0 only | human baseline requested by T0.6 | absent | only prospectively | domain/research | keep out of universal runtime v0.1 |

## VG-04 fields unfillable or unjustified in these traces

| VG-04 field | Finding | Disposition for v0.1 |
|---|---|---|
| `tenantId`, `ownerId` | no tenant/owner context existed; values would be invented | retain in normative v4, require explicit local singleton identities rather than omission |
| `branchId` | none of these repairs used parallel branches | optional; speculative for these traces |
| `encryptionKeyRef` | no encrypted payload was created | optional and classification-dependent |
| `trainability` | no trace was eligible for training | retain data-policy label with default-deny value |
| `EvaluatorId` and evaluation protocol | manual acceptance judgements were not independent evaluators | do not fabricate; required only when constructing an evidence claim |
| artifact `invalidationConditions` | no competence artifact was promoted | not applicable to raw event capture |

## Fields present but not used in reconstruction

| Field | Finding | Disposition |
|---|---|---|
| `redaction_note` | always stated “No secrets”; not needed to reconstruct behavior | retain as data-policy evidence, not causal input |
| `confidentiality` provenance axis | did not change these internal decisions | retain because security need is independent of these benign traces |
| exact wall timestamps | ordering came from step links; only durations used timestamps | retain for audit/latency, never use as causal order |

## Decisions

1. Do not replace VG-04's resource-selector taxonomy with the simplified GTS-13C projection from these traces; evidence supports resource scoping but not a new kind set.
2. Add `roleAtAction`, affected-resource pre/post digests, verification population and scoped uncertainty to the T1 design review before schema lock.
3. Keep `handsOnMillis` in the archaeology dataset, not the universal event envelope.
4. Preserve conditional VG-04 fields when their security purpose exceeds what four benign traces exercise; mark them unevidenced rather than deleting them.
5. No durable trajectory may be recorded until the schema review resolves these four candidate additions and conformance vectors exist.

## Exit checklist

- [x] Three real repository bugs traced: single-file, multi-file and test-reactive.
- [x] One non-coding reconciliation traced.
- [x] Structural reconstruction and ambiguity inventory completed.
- [x] VG-04 fields classified without inventing values.
- [x] Missing candidate fields have stable gap IDs.
- [ ] Independent third-engineer reconstruction signed.
- [ ] Prospective human hands-on baseline captured; retrospective values remain honestly unmeasured.

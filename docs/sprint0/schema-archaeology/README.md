# T0.1–T0.6 schema archaeology protocol

Purpose: discover the smallest honest event fields from real work before v0.1 wire schemas are locked. This is manual observation, not product implementation.

## Task selection

Choose three already-resolved or reproducible bugs in one repository the team knows well:

| Trace | Required shape | Selection evidence |
|---|---|---|
| `BUG-01` | single-file diagnosis and fix | issue/commit link; one production file changes |
| `BUG-02` | multi-file diagnosis and fix | issue/commit link; at least two coupled files change |
| `BUG-03` | test-reactive fix | issue/commit link; engineer must run a test, interpret failure and alter the next action |
| `NONCODE-01` | structured-data reconciliation or log triage | input snapshot, invariant and accepted result |

Do not invent toy bugs. Record repository, immutable base revision, issue reference, acceptance condition and why the engineer already understands the area. Remove secrets and personal data before tracing.

## Manual run

Two engineers independently or collaboratively fix each task by hand. They append one row per step to a copy of `manual-trace-template.tsv`. They may use ordinary editor/shell tools, but no Vanguard/GTS trace tooling and no proposed wire schema. The five allowed step kinds are `observation`, `proposal`, `effect`, `receipt`, and `judgement`.

Rules:

1. append only; correct a mistake with a new `judgement` row referencing the earlier `step_id`;
2. record what was known at that time, never rewrite a row using hindsight;
3. reference large or sensitive content by redacted digest plus a human-readable locator;
4. record start/end timestamps and hands-on/elapsed milliseconds for the human baseline;
5. record every ambiguity in plain language instead of guessing a field;
6. the recorder notes tool and environment facts only when they were needed to understand or reproduce the next step.

## Independent reconstruction

A third engineer receives only the task brief, immutable starting snapshot and flat trace. They must reconstruct:

- what was observed and from which snapshot;
- why each next action was available;
- the exact external effect and affected resource;
- whether it succeeded, failed or remained undeterminable;
- how receipts changed the next decision;
- the accepted final change and verification evidence.

They may not interview the original engineers until they have written `reconstruction-gaps.md`. Each question or ambiguity becomes a candidate missing field in `field-inventory.md`; information present but unusable is marked `present_ambiguous`.

## Field-inventory synthesis

For every candidate field, record which of the four traces needed it; its candidate universality (`universal`, `domain`, or `speculative`); whether VG-04 already defines it; whether a human could fill it at capture time; and whether reconstruction referenced it. A VG-04 field not evidenced by any trace is `speculative` and does not enter v0.1. A needed field absent from VG-04 is a schema finding, not permission to edit the schema before Tech Lead review.

## Exit evidence

T0 exits only when all three coding traces and the non-coding trace exist, the independent reconstructor signs each gap list, `field-inventory.md` is populated, and timing contains elapsed and hands-on values. T0 blocks locking T1 schemas; it does not block repository/CI scaffolding.


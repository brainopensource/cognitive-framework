# TODO
Give both teams the consolidated guidelines and this prompt. Then let them execute and integrate continuously; do not wait to approve each task.

Execute the autonomous AETHER v0.9 delivery program defined in:

docs/_archive/reviews/backend/director_review_v3/guidelines.md

This document is the controlling delivery methodology. Follow its ownership boundaries, decision defaults,
verification policy, integration procedure, and ordered TODO exactly.

Before coding:

1. Lane A completes Order 1:
    - Update the existing canonical triad only.
    - Remove C1-GATE, Leadership, Dev C, Director-control tables, and mandatory human acceptance dependencies.
    - Replace them with Lane A/Lane B ownership and machine-evaluable completion predicates.
    - Record the successor decision that automated verifier identity separation replaces mandatory human review.
    - Encode M-9 = 0.9.0b1 and M-10 = 0.9.0 in milestones and SPEC.
    - Do not create new planning Markdown files.

2. Lane B then completes Order 2:
    - Freeze the canonical manifest and vg.4 schemas.
    - Resolve schemas/mhf versus schemas/v4 authority.
    - Regenerate Python/TypeScript readers and shared golden vectors.
    - Publish the frozen contract commit.

3. Lane A consumes that commit and completes Order 3:
    - Replace parents[N] schema lookup with packaged resource resolution.
    - Package schemas and packs into the real distribution.
    - Prove operation from both a checkout and an installed wheel.
    - Eliminate all 17 manifest errors without weakening fail-closed validation.

Afterward, execute Orders 4 through 21 continuously.

Operating rules:

- Each lane has WIP=1 and edits only its permanently owned files.
- Use the existing canonical backlog, sprint_active, milestones, and SPEC; create no documentation sprawl.
- Every package must use the complete §15 template and satisfy its machine-evaluable completion predicate.
- Developers make local technical decisions themselves.
- Shared-contract decisions belong to the contract owner.
- Constitutional invariants require a successor ADR and falsifier.
- Apply the §9.2 default whenever an experiment or optional facility is inconclusive.
- No CEO, Tech Lead, Leadership, committee, cross-review, or human approval is required between packages.
- Self-review, focused checks, and mechanical integration are mandatory.
- Do not generate new milestone evidence while the canonical Python, TypeScript, packaging, or architecture baseline
is red.
- Fix integration failures forward according to permanent file ownership.
- A valid negative experiment selects its documented fallback and advances the roadmap.
- Integrate each completed package mechanically and begin the next package immediately.
- Do not stop after M-8, M-9, or the beta.
- Completion occurs only when Order 21 runs ci/release_qualify.sh successfully for the exact candidate, produces a
matching signed release envelope, and publishes AETHER v0.9.0.

Provide status through the two canonical active-package rows. Escalate only if a constitutional invariant cannot be
preserved and no documented fallback exists.

After sending this, wait for integrated code and objective check results—not intermediate approval requests.
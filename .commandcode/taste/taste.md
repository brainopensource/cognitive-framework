# Taste

## Workflow & process
- Prefers strict scope boundaries: define explicit "never touch" vs. "may edit" path lists up front, keep out-of-scope code (e.g., backend) frozen, and route cross-boundary needs to the owning team as notes instead of editing or silently working around them. Confidence: 0.9
- Prefers a plan-first workflow: lock a written plan (binding decisions, deliverables, verification steps) before implementation begins, and build only after the plan is locked. Confidence: 0.9
- Prefers decomposing work into parallel work streams with clear per-path ownership (e.g., one person owns `clients/cli/**`, another owns `vanguard-ide/**`) so multiple people can build concurrently without blocking each other. Confidence: 0.8
- Prefers ground truth over docs: review existing docs and code first, then rewrite or throw away anything wrong or hallucinated (docs citing files that don't exist, invented protocols), writing from scratch when that is better — keep only docs that match implemented reality. Confidence: 0.8

## Communication & documentation
- Expects planning documentation as a deliverable: ROADMAP sections, architecture guides, and sprint kits with acceptance criteria, lane ownership, and verification commands. Confidence: 0.7

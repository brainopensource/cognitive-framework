# Paired DNA case study (not a published lift)

Same live model, same HOLDOUT task, two manifests. `D_treatment` is **only** the pack. n is a case study; do not compute p-values.

## Arms

| Arm | Manifest | Tools the model may call |
|---|---|---|
| Product | `vg-code-default` | read / search / patch / test → `fs.read`, `fs.search`, `patch.apply`, `proc.exec` |
| Control | `vg-shell-only` | shell → `proc.exec` (git, python3, pytest, ruff) |

Reconstruction packs (`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`) are tool-name + prompt reconstructions. They are not Anthropic/OpenCode schedulers (episode depth remains 1).

## Protocol

1. `--check-fixtures` must pass (public tests fail on the fixture; no oracle/FIXME leak).
2. Cap `--max-turns 8`.
3. Run product then control:

```bash
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test005_named_amounts --task test003_invoice_cents \
  --manifest vg-code-default --max-turns 8 --model ollama/<tag>

python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test005_named_amounts --task test003_invoice_cents \
  --manifest vg-shell-only --max-turns 8 --model ollama/<tag>
```

4. Record in `result.json`: `manifest`, `gene_digests`, `evidence_label`, tool histogram (`receipts[].verb`), public vs oracle, `public_overfit`.
5. Do not spend OpenRouter until a local run shows `patch.apply` (or a shell write) on T1.
6. Change a pack only if this pairing shows a discordant pass that is not a leak.

## Report

Discordant outcomes, turns, tokens. No lift claim.

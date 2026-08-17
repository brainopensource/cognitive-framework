# Retracted benchmark artifacts

Retracted 2026-08-16 under S7-C-04.

`matrix_results_tier3_token_bucket.json` reported passes where the precondition
was already satisfied and no intervention was applied (`patch_length: 0`). It
is not evidence about Vanguard. The S7-C-01 dependency gate and S7-C-02
fail-closed guard now prevent adapter-bypassing and degenerate runs from being
scored.

This is a retraction with cause, not a deletion. No comparative lift or
significance claim is made.

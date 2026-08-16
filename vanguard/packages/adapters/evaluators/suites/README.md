# Sealed evaluator suite registry

Each suite is preregistered by `docs/agile/sprint6B/preregistered_oracles.json`.
The evaluator consumes the SHA-256 digest map, not a model-provided test path.
The files in this source tree are development copies; release execution must
mount an independently sealed copy read-only and verify the same digests.

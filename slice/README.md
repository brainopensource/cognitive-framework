# Disposable provider slice (T0b)

This directory is a direct, disposable provider probe. It imports the `ModelProvider` interface only; it does not import or wire the engine, kernel, grants, ledger, runtime, or production adapters. Production code must never import `slice/`, and the S4 exit gate deletes this directory.

Run only with a disposable credential supplied by the environment:

```bash
VG_SLICE_ENDPOINT=https://provider.example/v1/chat/completions \
VG_SLICE_API_KEY=... \
VG_SLICE_MODEL=... \
npm --workspace @vanguard/disposable-slice run run
```

The runner emits a typed, secret-free result. It treats provider failure as an `instrument_error`; it does not claim task failure or persistent system behavior.

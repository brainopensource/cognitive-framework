# Disposable end-to-end slice (T0b)

This is the disposable real-provider path: prompt → provider → proposed git patch → `git apply --check` preview → explicit human approval → apply → test → result. It has local interfaces, imports no production package, and is deleted outright at the S4 exit.

Use a disposable credential and an expendable clean repository/worktree. The test command is an argv JSON array, never a shell string:

```bash
VG_SLICE_ENDPOINT=https://provider.example/v1/chat/completions \
VG_SLICE_API_KEY=... \
VG_SLICE_MODEL=... \
VG_SLICE_REPO=/absolute/path/to/expendable-repo \
VG_SLICE_TASK='Make the smallest requested change.' \
VG_SLICE_TEST_ARGV='["python3","-m","unittest"]' \
npm --workspace @vanguard/disposable-slice run run
```

The runner requires typing `approve` after showing the exact diff and stat. Git rejects paths outside the repository, commands use `spawn` without a shell, and credentials are never logged. This is integration evidence, not reusable provider or environment code.

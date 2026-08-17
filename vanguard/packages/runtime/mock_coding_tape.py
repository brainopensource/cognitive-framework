"""A scripted MOCK brain that actually takes coding turns (`S18-A-01`).

`REQ-TRUST-001`. `FakeModel([])` proposes nothing, so every MOCK run reported
`turns: 0, instrument_error: model_not_invoked`. That was honest -- the brain
was never bound -- but it is a failure of the *harness wiring*, not a
measurement of anything, and a task set that only ever produces it tells you
nothing about the loop.

This tape makes the MOCK behave like a very poor engineer: look at the file,
attempt an edit, run the suite, stop. That exercises observe → propose → effect
→ receipt → ledger end to end.

**It is a behaviour script, not a solution.** The patch it proposes is
deliberately generic and will not fix any of the seeded bugs. Putting a working
diff here would be a gold patch in the sandbox -- the run would go green
without the model having reasoned about anything, and every number downstream
would be measuring this file instead of a brain. A MOCK that cannot code is the
correct MOCK; `oracle_green` from this tape would be the bug.

The verbs come from the pack, so a manifest that does not grant `patch.apply`
simply produces a denial receipt -- which is also data.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = ["coding_tape", "brief_from_task_dir"]

#: What the tape reads first. Relative, workspace-scoped, no oracle path.
_PROBE_CANDIDATES = ("src/calculator.py", "src/app.py", "app.py", "README.md")


def brief_from_task_dir(task_dir: Any) -> str | None:
    """Read `TASK.md` as the brief, if the task supplies one.

    The task states its own goal. Inventing a brief here would mean the harness
    telling the model what the task is, which is a different experiment from
    the one the task directory describes.
    """
    from pathlib import Path

    candidate = Path(task_dir) / "TASK.md"
    if not candidate.is_file():
        return None
    try:
        return candidate.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def _effect(action: str, args: Mapping[str, Any], note: str) -> dict[str, Any]:
    return {"kind": "effect", "action": action, "args": dict(args), "note": note}


def coding_tape(
    *,
    verbs: Sequence[str] = (),
    probe_path: str = "src/calculator.py",
    test_argv: Sequence[str] = ("python3", "-m", "unittest", "discover"),
    attempts: int = 1,
) -> list[dict[str, Any]]:
    """A read → edit → test → finish tape, filtered to the pack's verbs.

    Only verbs the manifest granted are proposed. A tape that proposes an
    ungranted verb would spend its turns collecting denials, which measures the
    tape rather than the loop.
    """

    granted = set(verbs)
    tape: list[dict[str, Any]] = []

    for attempt in range(max(int(attempts), 1)):
        if "fs.read" in granted:
            tape.append(_effect("fs.read", {"path": probe_path},
                                f"read the implementation (attempt {attempt + 1})"))
        if "patch.apply" in granted:
            # Deliberately not a fix. See the module docstring: a working diff
            # here is a gold patch, and the green it produced would be this
            # file's, not a model's.
            tape.append(_effect(
                "patch.apply",
                {"diff": f"--- a/{probe_path}\n+++ b/{probe_path}\n"
                         "@@ -1 +1 @@\n-# mock edit\n+# mock edit\n"},
                "attempt an edit the mock cannot reason about"))
        if "proc.exec" in granted:
            tape.append(_effect("proc.exec", {"argv": list(test_argv)},
                                "run the suite through the allowlisted verb"))

    tape.append({"kind": "finish",
                 "note": "mock brain exhausted its scripted behaviour"})
    return tape

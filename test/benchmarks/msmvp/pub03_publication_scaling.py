"""PUB-03 measurement rig: child-publication cost as a function of tree size.

`docs/execution/main/mvp_delivery_protocol.md` §8 defers "base computation at
repository scale" with an explicit instruction: *needs a measurement before an
optimization; an unmeasured optimization here would trade a proven invariant
for a guess*. This module is that measurement and nothing else. It changes no
production source, asserts no target, and is read-only on
`vanguard/packages/runtime/workspace.py`.

What is measured, per tree size, on a real `ChildWorkspaceSupervisor` against a
real on-disk tree:

* `shared_entries()`      -- the full-tree read on the hot path
* `shared_digest()`       -- entries + RFC 8785 canonicalisation
* `workspace_for(seed=)`  -- first-use view creation, which also binds the base
* `retain_candidate()`    -- freeze the view into a base-bound candidate
* `stage()`               -- materialise the combined tree an evaluator reads
* `publish()`             -- five-fold revalidation, then apply

Reported for each: wall time (median of `--repeats`), peak resident bytes
(`tracemalloc`), and the durable bytes the control directory accumulates --
the last because the base record and the candidate record each persist a full
copy of the tree as JSON, which is a storage cost that does not appear in a
timing number.

Run:
    python3 -m benchmarks.pub03.publication_scaling
    python3 -m benchmarks.pub03.publication_scaling --sizes 100 1000 --json
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import sys
import tempfile
import time
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from vanguard.packages.runtime.workspace import (  # noqa: E402
    ChildWorkspaceSupervisor,
    MutationTicket,
    PublicationVerdict,
)

# -- corpus ----------------------------------------------------------------

# A realistic source tree is not N files in one directory. This mix is taken
# from the shape of this repository: a few wide package directories, moderate
# nesting, and a file-size distribution dominated by 1-6 KB modules with a
# long tail of larger ones.
_SIZE_MIX = ((0.55, 1_200), (0.30, 4_000), (0.12, 12_000), (0.03, 60_000))

_LINE = (
    "def _handler_{i}(request, *, context=None):  # generated corpus line\n"
    "    return {{'route': {i}, 'ok': True, 'ctx': context}}\n"
)


def _file_text(index: int, target_bytes: int) -> str:
    body = "".join(_LINE.format(i=index + n) for n in range(max(1, target_bytes // 96)))
    return f'"""corpus module {index}."""\n' + body


def _plan_sizes(count: int) -> list[int]:
    sizes: list[int] = []
    for fraction, nbytes in _SIZE_MIX:
        sizes.extend([nbytes] * int(round(count * fraction)))
    while len(sizes) < count:
        sizes.append(_SIZE_MIX[0][1])
    return sizes[:count]


def build_tree(root: Path, count: int) -> tuple[int, int]:
    """Write `count` files in a repository-shaped layout. Returns (files, bytes)."""
    total = 0
    for index, nbytes in enumerate(_plan_sizes(count)):
        package = f"pkg_{index % 24:02d}"
        module = f"sub_{(index // 24) % 12:02d}"
        path = root / package / module / f"mod_{index:05d}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = _file_text(index, nbytes)
        path.write_text(text, encoding="utf-8")
        total += len(text.encode("utf-8"))
    return count, total


# -- measurement -----------------------------------------------------------


@dataclass
class Sample:
    label: str
    seconds: list[float] = field(default_factory=list)
    peak_bytes: int = 0
    note: str = ""

    def as_row(self) -> dict[str, Any]:
        return {
            "operation": self.label,
            "median_seconds": round(statistics.median(self.seconds), 6),
            "min_seconds": round(min(self.seconds), 6),
            "max_seconds": round(max(self.seconds), 6),
            "peak_bytes": self.peak_bytes,
            "note": self.note,
        }


def _measure(label: str, call: Callable[[], Any], repeats: int) -> tuple[Sample, Any]:
    sample = Sample(label)
    result: Any = None
    for attempt in range(repeats):
        tracemalloc.start()
        started = time.perf_counter()
        result = call()
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sample.seconds.append(elapsed)
        sample.peak_bytes = max(sample.peak_bytes, peak)
        if attempt == 0:
            first = result
    return sample, first


def _dir_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def measure_size(count: int, *, repeats: int, workdir: Path) -> dict[str, Any]:
    """One full publication lifecycle over a tree of `count` files."""
    shared = workdir / f"tree_{count}"
    shared.mkdir(parents=True)
    files, corpus_bytes = build_tree(shared, count)

    supervisor = ChildWorkspaceSupervisor(shared)
    child = "c-pub03"
    rows: list[Sample] = []

    # Read-only probes first: these are the two calls the protocol names as
    # O(tree) and they run on *every* view creation and *every* publication.
    sample, entries = _measure(
        "shared_entries", lambda: dict(supervisor.shared_entries()), repeats)
    sample.note = f"{len(entries)} entries read as text"
    rows.append(sample)

    sample, _ = _measure("shared_digest", supervisor.shared_digest, repeats)
    sample.note = "entries + RFC 8785 JCS digest"
    rows.append(sample)

    # Lifecycle probes are order-dependent and mutate durable state, so each is
    # measured once (repeats would hit the idempotent path and measure nothing).
    sample, view = _measure(
        "workspace_for(seed=True)",
        lambda: supervisor.workspace_for(child, seed=True), 1)
    sample.note = "first use: binds base + materialises view"
    rows.append(sample)
    base_bytes = _dir_bytes(supervisor.control_dir)

    # A realistic child touches a handful of files, not the whole tree.
    touched = sorted(dict(entries))[: max(1, min(8, count // 10))]
    for relpath in touched:
        view.write(relpath, view.read(relpath) + "\n# child edit\n")

    sample, candidate = _measure(
        "retain_candidate", lambda: supervisor.retain_candidate(child), 1)
    sample.note = f"{len(touched)} files changed by the child"
    rows.append(sample)
    candidate_bytes = _dir_bytes(supervisor.control_dir) - base_bytes

    ticket: MutationTicket = supervisor.acquire(child)
    sample, combined = _measure(
        "stage", lambda: supervisor.stage(ticket, candidate_digest=candidate), 1)
    sample.note = "base overlay + staged tree on disk"
    rows.append(sample)
    staged_bytes = _dir_bytes(supervisor.control_dir) - base_bytes - candidate_bytes

    verdict = PublicationVerdict(
        subject_digest=combined.digest,
        disposition="passed",
        envelope_digest="sha256:measurement-rig",
    )
    sample, outcome = _measure(
        "publish", lambda: supervisor.publish(ticket, combined, verdict=verdict), 1)
    sample.note = f"five-fold revalidation; outcome={outcome!r}"
    rows.append(sample)
    supervisor.release(ticket)

    control_bytes = _dir_bytes(supervisor.control_dir)
    lifecycle = sum(statistics.median(s.seconds) for s in rows[2:])
    hot_path = sum(statistics.median(s.seconds) for s in rows[:2])

    return {
        "files": files,
        "corpus_bytes": corpus_bytes,
        "operations": [s.as_row() for s in rows],
        "durable_bytes": {
            "base_record": base_bytes,
            "candidate_record": candidate_bytes,
            "staged_tree": staged_bytes,
            "control_dir_total": control_bytes,
            "amplification_vs_corpus": round(control_bytes / max(1, corpus_bytes), 2),
        },
        "totals": {
            "read_only_probes_seconds": round(hot_path, 6),
            "lifecycle_seconds": round(lifecycle, 6),
        },
    }


def _scaling(results: list[dict[str, Any]], operation: str) -> dict[str, Any]:
    """Empirical exponent: seconds ~ files^k. k ~= 1.0 is linear."""
    points = []
    for result in results:
        for row in result["operations"]:
            if row["operation"] == operation:
                points.append((result["files"], row["median_seconds"]))
    if len(points) < 2:
        return {"operation": operation, "exponent": None}
    (n0, t0), (n1, t1) = points[0], points[-1]
    import math
    exponent = math.log(t1 / t0) / math.log(n1 / n0) if t0 > 0 and n1 > n0 else None
    return {
        "operation": operation,
        "exponent": round(exponent, 3) if exponent else None,
        "points": points,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 1000, 10000])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)

    workdir = Path(tempfile.mkdtemp(prefix="pub03-"))
    try:
        results = [
            measure_size(count, repeats=args.repeats, workdir=workdir)
            for count in sorted(args.sizes)
        ]
    finally:
        if not args.keep:
            shutil.rmtree(workdir, ignore_errors=True)

    report = {
        "rig": "PUB-03 publication scaling",
        "results": results,
        "scaling": [
            _scaling(results, name)
            for name in ("shared_entries", "shared_digest", "stage", "publish")
        ],
    }
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    for result in results:
        print(f"\n=== {result['files']} files "
              f"({result['corpus_bytes'] / 1e6:.1f} MB corpus) ===")
        print(f"{'operation':<26} {'median s':>10} {'peak MB':>9}  note")
        for row in result["operations"]:
            print(f"{row['operation']:<26} {row['median_seconds']:>10.4f} "
                  f"{row['peak_bytes'] / 1e6:>9.1f}  {row['note']}")
        durable = result["durable_bytes"]
        print(f"{'durable control bytes':<26} "
              f"{durable['control_dir_total'] / 1e6:>10.1f} MB "
              f"(x{durable['amplification_vs_corpus']} corpus)")
    print("\n=== empirical scaling (seconds ~ files^k) ===")
    for row in report["scaling"]:
        print(f"{row['operation']:<26} k = {row['exponent']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

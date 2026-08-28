#!/usr/bin/env python3
"""Produce a signed, accepted, independently verified evidence bundle.

Evidence is only worth as much as the subject it pins. Building a bundle from
the working tree records ``dirty: true``, and a dirty pin means the recorded
commit does not describe the code that ran -- the verifier answers
``undeterminable`` and no predicate is satisfied. So this runner builds from a
throwaway git worktree checked out at an exact commit, writes run artifacts
outside that worktree so the subject stays clean, signs with a registered
producer key, has a registered reviewer accept it, and finally re-verifies the
result with the independent verifier before anything is copied into the
repository.

Nothing here can turn a negative into a pass: the falsifier subprocess decides
the outcome, and the last step is the same verifier that gates the milestone.

Usage:
    python3 tools/runners/publish_evidence.py --claim M-6 --label order11 \
        --producer dev-b --producer-key ~/.aether/keys/dev-b-evidence-1.key \
        --key-id dev-b-evidence-1 \
        --reviewer aether-evidence-reviewer \
        --reviewer-key ~/.aether/keys/aether-evidence-reviewer-1.key \
        --reviewer-key-id aether-evidence-reviewer-1
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = _ROOT / "docs" / "03_execution" / "evidence"


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, text=True,
                            check=False, **kwargs)
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"command failed: {' '.join(command)}")
    return result


def _git(*args: str, cwd: Path = _ROOT) -> str:
    return _run(["git", "-C", str(cwd), *args]).stdout.strip()


def publish(args: argparse.Namespace) -> int:
    commit = _git("rev-parse", args.commit)
    stems = {
        "M-6": "M-6-canonical-recursion",
        "M-4": "M-4-rf95",
        "M-5b": "M-5b-graph-coloring",
        "M-6.5": "M-6.5-attributable-paired-study",
    }
    bundle_name = f"{stems[args.claim]}-{args.label}"
    destination = EVIDENCE_DIR / f"{bundle_name}.json"
    if destination.exists():
        # Publishing over a bundle destroys the earlier claim and invalidates
        # any acceptance bound to its digest. Successors get their own label.
        raise SystemExit(f"{destination} already exists; choose a new --label")

    with tempfile.TemporaryDirectory(prefix="aether-evidence-") as staging:
        stage = Path(staging)
        subject = stage / "subject"
        evidence_out = stage / "evidence"
        _run(["git", "-C", str(_ROOT), "worktree", "add", "-q", "--detach",
              str(subject), commit])
        try:
            if _git("status", "--porcelain", cwd=subject):
                raise SystemExit("freshly created worktree is dirty; aborting")

            bundle = evidence_out / f"{bundle_name}.json"
            # The builder is tooling, not the subject: it runs from the current
            # checkout so a fix to the builder is not required to have existed
            # at the commit under test. Only --subject-root is pinned. The M-6
            # falsifiers below are the opposite case: they must be the subject's
            # own code, so they run from the worktree.
            build = [sys.executable,
                     str(_ROOT / "tools" / "runners" / "build_evidence_bundle.py"),
                     "--claim", args.claim,
                     "--producer", args.producer,
                     "--producer-key", str(Path(args.producer_key).expanduser()),
                     "--key-id", args.key_id,
                     "--subject-root", str(subject),
                     "--evidence-root", str(evidence_out),
                     "--out", str(bundle)]
            if args.claim == "M-6":
                # The falsifier subprocess is the only thing that decides the
                # outcome. A nonzero return here is a real negative result.
                report = stage / "report.json"
                _run([sys.executable,
                      str(subject / "tools" / "runners" / "run_m6_recursive_proof.py"),
                      "--root", str(subject), "--out", str(report)])
                build += ["--report", str(report), "--label", args.label]
            elif args.claim == "M-5b":
                pass  # the surface is the subject worktree; nothing else to pass
            elif args.claim == "M-6.5":
                # The accepted study is re-emitted, never re-run: a study rerun
                # to repair its packaging is a different study.
                if not args.from_bundle:
                    raise SystemExit("--claim M-6.5 requires --from-bundle")
                build += ["--from-bundle",
                          str(Path(args.from_bundle).expanduser().resolve())]
            else:
                # M-4 rests on a product run that already happened: its ledger
                # and preregistration are inputs here, not something this runner
                # can synthesise. Cold reconstruction still runs inside the
                # builder, against the subject worktree.
                if not args.ledger or not args.prereg:
                    raise SystemExit("--claim M-4 requires --ledger and --prereg")
                build += ["--ledger", str(Path(args.ledger).expanduser().resolve()),
                          "--prereg", str(Path(args.prereg).expanduser().resolve()),
                          "--artifact-name", bundle_name]
                if args.workload:
                    build += ["--workload",
                              str(Path(args.workload).expanduser().resolve())]
            _run(build, cwd=_ROOT)

            _run([sys.executable, "tools/runners/accept_evidence.py", str(bundle),
                  "--reviewer", args.reviewer,
                  "--key", str(Path(args.reviewer_key).expanduser()),
                  "--key-id", args.reviewer_key_id], cwd=_ROOT)

            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bundle, destination)
            shutil.copy2(bundle.with_name(bundle.name + ".acceptance.json"),
                         destination.with_name(destination.name + ".acceptance.json"))
            artifacts = evidence_out / "artifacts" / bundle_name
            if artifacts.is_dir():
                shutil.copytree(artifacts, EVIDENCE_DIR / "artifacts" / bundle_name)
        finally:
            _run(["git", "-C", str(_ROOT), "worktree", "remove", "--force", str(subject)])

    # The gate, not a self-report: the same verifier that decides the milestone.
    verdict = subprocess.run(
        [sys.executable, "tools/linters/verify_evidence.py",
         "--milestone", bundle_name],
        cwd=_ROOT, capture_output=True, text=True, check=False)
    sys.stdout.write(verdict.stdout)
    sys.stderr.write(verdict.stderr)
    return verdict.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", default="M-6",
                        choices=("M-6", "M-4", "M-5b", "M-6.5"))
    parser.add_argument("--from-bundle", default="",
                        help="M-6.5: existing bundle whose study report is re-emitted")
    parser.add_argument("--ledger", default="", help="M-4: event store from the run")
    parser.add_argument("--prereg", default="", help="M-4: preregistration file")
    parser.add_argument("--workload", default="", help="M-4: workload descriptor")
    parser.add_argument("--label", required=True, help="successor label, e.g. order11")
    parser.add_argument("--commit", default="HEAD", help="subject commit to pin")
    parser.add_argument("--producer", default="dev-b")
    parser.add_argument("--producer-key", required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--reviewer", default="aether-evidence-reviewer")
    parser.add_argument("--reviewer-key", required=True)
    parser.add_argument("--reviewer-key-id", required=True)
    return publish(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())

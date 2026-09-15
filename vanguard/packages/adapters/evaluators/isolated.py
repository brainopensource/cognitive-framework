"""Exterior evaluator adapter with immutable-input and pollution probes.

Owning contract: REQ-EVAL-001, ICD §4, VG-05 §2.1/§6, VG-06 §4.3.

This adapter is instantiated in the evaluator daemon, never in agency.  The
daemon's OS supervisor is responsible for its namespace and immutable image;
the adapter verifies the identity/image facts before constructing a verdict.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

from ...domain.workspace import controlled_environment
from ...ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ...ports.event_store import Result

__all__ = ["IsolatedEvaluator"]

Runner = Callable[..., subprocess.CompletedProcess[bytes]]

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_POLLUTION_NAMES = frozenset({"conftest.py", "sitecustomize.py", "usercustomize.py"})
_IGNORED_CANDIDATE_DIRS = frozenset({
    ".git", ".hg", ".svn", ".vanguard", ".pytest_cache", "__pycache__", ".venv",
})
_IGNORED_CANDIDATE_NAMES = frozenset({
    ".gitignore", ".editorconfig", "README.md", "TASK.md",
})
_VACUOUS_ARGV = re.compile(
    r"^\s*(?:true|/bin/true|/usr/bin/true|echo\b|printf\b)\b",
    re.IGNORECASE,
)
_HOST_POLLUTION_VARS = ("PYTHONPATH", "PYTHONSTARTUP", "LD_PRELOAD", "PYTHONHOME")
_INCOMPLETE_REASONS = frozenset({
    "empty_stub_solution",
    "vacuous_discovery",
    "omitted_required_file",
    "unauthorized_addition",
    "candidate_substitution",
    "stale_verification",
})


class IsolatedEvaluator:
    """Evaluate a completed workspace from the exterior evidence plane.

    ``oracle_digests`` is the sealed, pre-registered manifest supplied to the
    evaluator image.  ``command`` is an argv vector; shell command strings are
    deliberately unsupported.
    """

    def __init__(
        self,
        workspace: Path | str,
        oracle_digests: Mapping[str, str],
        command: Sequence[str],
        *,
        expected_uid: int = 10002,
        image_digest: str,
        timeout_seconds: float = 60.0,
        oracle_root: Path | str | None = None,
        runner: Runner = subprocess.run,
        candidate_digest: str | None = None,
        required_files: Sequence[str] = (),
        allowed_files: Sequence[str] = (),
        verification_subject_digest: str | None = None,
    ) -> None:
        self._workspace = Path(workspace).resolve()
        self._oracle_root = (Path(oracle_root).resolve() if oracle_root is not None
                             else self._workspace)
        self._oracle_digests = dict(oracle_digests)
        self._command = tuple(command)
        self._expected_uid = expected_uid
        self._image_digest = image_digest
        self._timeout_seconds = timeout_seconds
        self._runner = runner
        # DIR-C7: optional immutable candidate reference. Workers emit these;
        # this adapter never mints acceptance or merge authority.
        self._candidate_digest = candidate_digest
        self._required_files = tuple(str(item) for item in required_files)
        self._allowed_files = tuple(str(item) for item in allowed_files)
        self._verification_subject_digest = verification_subject_digest

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        """Return a confirmed claim or preserve uncertainty as inconclusive."""
        try:
            instrument_problem = self._validate_instrument()
            if instrument_problem is not None:
                return self._inconclusive(instrument_problem)

            terminal_problem = self._verify_terminal_evidence(run_ref)
            if terminal_problem is not None:
                return self._inconclusive(terminal_problem)

            immutable, immutable_details = self._probe_immutability()
            non_polluted, pollution_details = self._probe_non_pollution()
            if not immutable:
                return Result.success(
                    self._tampered_claim(
                        run_ref,
                        protocol,
                        immutable=False,
                        non_pollution=non_polluted,
                        details=immutable_details,
                    )
                )

            if not non_polluted:
                return Result.success(
                    self._tampered_claim(
                        run_ref,
                        protocol,
                        immutable=True,
                        non_pollution=False,
                        details=pollution_details,
                    )
                )

            live_digest, completeness_reason, completeness_details = (
                self._probe_candidate_completeness(protocol)
            )
            if completeness_reason is not None:
                return Result.success(
                    self._incomplete_claim(
                        run_ref,
                        protocol,
                        reason=completeness_reason,
                        details=completeness_details,
                        candidate_digest=live_digest,
                    )
                )

            # Bind the child import path to the submitted tree. Running
            # ``python3 tests/test_oracle.py`` puts ``tests/`` on ``sys.path[0]``;
            # without this, candidate modules at the workspace root are invisible
            # and a valid positive control looks like a failed oracle.
            completed = self._runner(
                self._command,
                cwd=self._workspace,
                env=self._oracle_child_env(),
                capture_output=True,
                timeout=self._timeout_seconds,
                check=False,
            )
            return Result.success(
                Verdict(
                    outcome="claims",
                    claims=(
                        {
                            "event": "EvaluationCompleted",
                            "status": "passed" if completed.returncode == 0 else "failed",
                            "runId": run_ref.run_id,
                            "protocol": protocol.name,
                            "probes": {
                                "immutability": True,
                                "nonPollution": True,
                                "candidateCompleteness": True,
                            },
                            "candidateDigest": live_digest,
                            "evaluatorUid": os.getuid(),
                            "imageDigest": self._image_digest,
                            "exitCode": completed.returncode,
                        },
                    ),
                )
            )
        except Exception as exc:
            # Keep the verdict fail-closed while leaving a bounded diagnostic
            # for the supervised container log; the client still receives
            # only the generic inconclusive outcome.
            print(f"evaluator probe failed: {type(exc).__name__}", file=sys.stderr)
            return self._inconclusive("instrument_error")

    def _validate_instrument(self) -> str | None:
        if os.getuid() != self._expected_uid:
            return "evaluator_identity_unverified"
        if not _DIGEST.fullmatch(self._image_digest):
            return "evaluator_image_unverified"
        if not self._workspace.is_dir() or not self._command:
            return "instrument_configuration_invalid"
        if any(not isinstance(argument, str) or not argument for argument in self._command):
            return "instrument_configuration_invalid"
        return None

    def _verify_terminal_evidence(self, run_ref: RunRef) -> str | None:
        if not run_ref.episode_id:
            return "evaluator_non_terminal_evidence"
        return None

    def _probe_immutability(self) -> tuple[bool, tuple[str, ...]]:
        mismatches: list[str] = []
        if not self._oracle_digests:
            return False, ("oracle manifest is empty",)

        oracle_dirs: set[Path] = set()

        for relative, expected in sorted(self._oracle_digests.items()):
            path = self._oracle_path(relative)
            if path is None or not _DIGEST.fullmatch(expected) or not path.is_file() or path.is_symlink():
                mismatches.append(relative)
                continue
            
            actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                mismatches.append(relative)
            else:
                oracle_dirs.add(path.parent)

        for d in oracle_dirs:
            current = d
            is_symlink = False
            while current != self._oracle_root:
                if current.is_symlink():
                    is_symlink = True
                    break
                current = current.parent
            
            if is_symlink:
                mismatches.append(str(d.relative_to(self._oracle_root)))
                continue

            for item in d.iterdir():
                if item.is_file():
                    rel_item = str(item.relative_to(self._oracle_root))
                    if rel_item not in self._oracle_digests:
                        mismatches.append(rel_item)

        return not mismatches, tuple(sorted(set(mismatches)))

    def _oracle_path(self, relative: str) -> Path | None:
        pure = PurePosixPath(relative)
        if pure.is_absolute() or not pure.parts or ".." in pure.parts:
            return None
        candidate = (self._oracle_root / Path(*pure.parts)).resolve(strict=False)
        try:
            candidate.relative_to(self._oracle_root)
        except ValueError:
            return None
        return candidate

    def _oracle_child_env(self) -> dict[str, str]:
        """Bind the oracle process to the submitted tree; strip host import hooks."""
        env = controlled_environment(os.environ)
        for var in _HOST_POLLUTION_VARS:
            env.pop(var, None)
        env["PYTHONPATH"] = str(self._workspace)
        return env

    def _probe_non_pollution(self) -> tuple[bool, tuple[str, ...]]:
        pollution: list[str] = []

        for root, dirs, files in os.walk(self._workspace):
            for name in dirs + files:
                p = Path(root) / name
                if p.is_symlink():
                    try:
                        target = p.resolve(strict=False)
                        target.relative_to(self._workspace)
                    except ValueError:
                        pollution.append(str(p.relative_to(self._workspace)))

        git_hooks = self._workspace / ".git" / "hooks"
        if git_hooks.is_dir():
            for root, dirs, files in os.walk(git_hooks):
                for file in files:
                    # Ignore standard samples usually placed by git init
                    if not file.endswith(".sample"):
                        p = Path(root) / file
                        pollution.append(str(p.relative_to(self._workspace)))

        status = subprocess.run(
            ["git", "-c", f"safe.directory={self._workspace}", "status",
             "--porcelain", "--untracked-files=all"],
            cwd=self._workspace,
            capture_output=True,
            text=True,
            timeout=self._timeout_seconds,
            check=False,
        )
        if status.returncode != 0:
            raise RuntimeError("workspace tracking state unavailable")

        for line in status.stdout.splitlines():
            if len(line) < 4:
                continue
            relative = line[3:].strip().strip('"')
            path = PurePosixPath(relative)
            lowered_parts = tuple(part.lower() for part in path.parts)
            
            if (
                path.name.lower() in _POLLUTION_NAMES
                or path.suffix.lower() == ".pth"
                or "site-packages" in lowered_parts
            ):
                pollution.append(relative)
                continue
                
            if path.name in ("requirements.txt", "poetry.lock", "Pipfile.lock"):
                pollution.append(relative)
                continue
                
            if path.name in ("python", "python3", "pip", "git", "bash", "sh"):
                pollution.append(relative)
                continue
                
            actual_path = self._workspace / Path(*path.parts)
            if actual_path.is_file() and os.access(actual_path, os.X_OK):
                pollution.append(relative)
                continue

        return not pollution, tuple(sorted(set(pollution)))

    def _bound_ref(self, protocol: EvaluationProtocol) -> dict[str, Any]:
        params = dict(protocol.parameters or {})
        required = params.get("requiredFiles") or params.get("required_files")
        allowed = params.get("allowedFiles") or params.get("allowed_files")
        return {
            "candidate_digest": (
                params.get("candidateDigest") or params.get("candidate_digest")
                or self._candidate_digest
            ),
            "required_files": tuple(
                str(item) for item in (required if required is not None else self._required_files)
            ),
            "allowed_files": tuple(
                str(item) for item in (allowed if allowed is not None else self._allowed_files)
            ),
            "verification_subject_digest": (
                params.get("verificationSubjectDigest")
                or params.get("verification_subject_digest")
                or self._verification_subject_digest
            ),
        }

    def _candidate_files(self) -> dict[str, Path]:
        found: dict[str, Path] = {}
        oracle_keys = set(self._oracle_digests)
        for path in sorted(self._workspace.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(self._workspace)
            if any(part in _IGNORED_CANDIDATE_DIRS for part in rel.parts):
                continue
            if rel.name in _IGNORED_CANDIDATE_NAMES:
                continue
            key = rel.as_posix()
            if key in oracle_keys:
                continue
            found[key] = path
        return found

    def _live_candidate_digest(self, files: Mapping[str, Path]) -> str:
        entries = [
            f"{rel}:{hashlib.sha256(path.read_bytes()).hexdigest()}"
            for rel, path in sorted(files.items())
        ]
        return "sha256:" + hashlib.sha256("\n".join(entries).encode()).hexdigest()

    @staticmethod
    def _is_stub_source(text: str) -> bool:
        meaningful: list[str] = []
        in_doc = False
        fence = ""
        for raw in text.splitlines():
            line = raw.strip()
            if in_doc:
                if fence in line:
                    in_doc = False
                continue
            if not line or line.startswith("#"):
                continue
            if line.startswith(('"""', "'''")):
                fence = line[:3]
                if line.count(fence) < 2:
                    in_doc = True
                continue
            if line.startswith(("import ", "from ")):
                continue
            if line.startswith(("def ", "class ", "@")):
                continue
            if line in {"pass", "..."} or line.startswith("raise NotImplementedError"):
                continue
            meaningful.append(line)
        return not meaningful

    def _command_is_vacuous(self) -> bool:
        if not self._command:
            return True
        if "-c" in self._command:
            return True
        joined = " ".join(self._command)
        return bool(_VACUOUS_ARGV.match(joined))

    def _oracles_cover(self, required: Sequence[str]) -> bool:
        if not required:
            return False
        texts: list[str] = []
        for relative in self._oracle_digests:
            path = self._oracle_path(relative)
            if path is None or not path.is_file() or path.is_symlink():
                continue
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
        blob = "\n".join(texts)
        if not blob.strip():
            return False
        for rel in required:
            stem = Path(rel).stem
            if rel not in blob and stem not in blob:
                return False
        command_blob = " ".join(self._command)
        names_oracle = any(
            relative in command_blob or Path(relative).name in command_blob
            for relative in self._oracle_digests
        )
        runner_named = any(
            token in command_blob for token in ("unittest", "pytest", "py.test")
        )
        return names_oracle or runner_named

    def _probe_candidate_completeness(
        self, protocol: EvaluationProtocol,
    ) -> tuple[str, str | None, tuple[str, ...]]:
        """Exterior completeness of the exact submitted candidate (DIR-C7).

        Returns ``(live_digest, reason, details)``. ``reason is None`` means
        the candidate is complete enough to run required-behavior tests.
        A failed completeness probe never becomes acceptance.
        """
        bound = self._bound_ref(protocol)
        files = self._candidate_files()
        live = self._live_candidate_digest(files)
        required = bound["required_files"]
        allowed = set(bound["allowed_files"]) | set(required) | set(self._oracle_digests)

        if self._command_is_vacuous():
            return live, "vacuous_discovery", ("verification command cannot witness required behavior",)
        if not files:
            return live, "empty_stub_solution", ("submitted candidate contains no solution files",)

        if required:
            missing = tuple(rel for rel in required if rel not in files)
            if missing:
                return live, "omitted_required_file", missing
            extras = tuple(sorted(rel for rel in files if rel not in allowed))
            if extras:
                return live, "unauthorized_addition", extras
            stubs = tuple(rel for rel in required if self._is_stub_source(files[rel].read_text(encoding="utf-8", errors="replace")))
            if stubs:
                return live, "empty_stub_solution", stubs
            if not self._oracles_cover(required):
                return live, "vacuous_discovery", ("oracle does not exercise required files",)
        else:
            stubs = tuple(
                rel for rel, path in files.items()
                if self._is_stub_source(path.read_text(encoding="utf-8", errors="replace"))
            )
            if stubs and len(stubs) == len(files):
                return live, "empty_stub_solution", stubs
            if not self._oracles_cover(tuple(files)):
                return live, "vacuous_discovery", ("oracle does not exercise submitted files",)

        expected = bound["candidate_digest"]
        if expected:
            if not isinstance(expected, str) or not _DIGEST.fullmatch(expected):
                return live, "candidate_substitution", ("bound candidate digest is not a sha256 reference",)
            if expected != live:
                return live, "candidate_substitution", (expected, live)

        subject = bound["verification_subject_digest"]
        if subject:
            if not isinstance(subject, str) or not _DIGEST.fullmatch(subject):
                return live, "stale_verification", ("verification subject is not a sha256 reference",)
            if subject != live:
                return live, "stale_verification", (subject, live)
        return live, None, ()

    def _incomplete_claim(
        self,
        run_ref: RunRef,
        protocol: EvaluationProtocol,
        *,
        reason: str,
        details: tuple[str, ...],
        candidate_digest: str,
    ) -> Verdict:
        return Verdict(
            outcome="claims",
            claims=(
                {
                    "event": "EvaluationIncomplete",
                    "status": "failed",
                    "runId": run_ref.run_id,
                    "protocol": protocol.name,
                    "reason": reason,
                    "details": details,
                    "candidateDigest": candidate_digest,
                    "probes": {
                        "immutability": True,
                        "nonPollution": True,
                        "candidateCompleteness": False,
                    },
                    "evaluatorUid": os.getuid(),
                    "imageDigest": self._image_digest,
                },
            ),
            reason=reason,
        )

    def _tampered_claim(
        self,
        run_ref: RunRef,
        protocol: EvaluationProtocol,
        *,
        immutable: bool,
        non_pollution: bool,
        details: tuple[str, ...],
    ) -> Verdict:
        return Verdict(
            outcome="claims",
            claims=(
                {
                    "event": "EvaluationTampered",
                    "status": "failed",
                    "runId": run_ref.run_id,
                    "protocol": protocol.name,
                    "probes": {
                        "immutability": immutable,
                        "nonPollution": non_pollution,
                    },
                    "details": details,
                    "evaluatorUid": os.getuid(),
                    "imageDigest": self._image_digest,
                },
            ),
            reason="evaluation_tampered",
        )

    @staticmethod
    def _inconclusive(reason: str) -> Result[Verdict]:
        return Result.success(Verdict(outcome="inconclusive", reason=reason))

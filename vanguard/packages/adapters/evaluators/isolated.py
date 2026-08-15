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
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Sequence

from ...ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ...ports.event_store import Result

__all__ = ["IsolatedEvaluator"]

Runner = Callable[..., subprocess.CompletedProcess[bytes]]

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_POLLUTION_NAMES = frozenset({"conftest.py", "sitecustomize.py", "usercustomize.py"})


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
        runner: Runner = subprocess.run,
    ) -> None:
        self._workspace = Path(workspace).resolve()
        self._oracle_digests = dict(oracle_digests)
        self._command = tuple(command)
        self._expected_uid = expected_uid
        self._image_digest = image_digest
        self._timeout_seconds = timeout_seconds
        self._runner = runner

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        """Return a confirmed claim or preserve uncertainty as inconclusive."""
        try:
            instrument_problem = self._validate_instrument()
            if instrument_problem is not None:
                return self._inconclusive(instrument_problem)

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

            completed = self._runner(
                self._command,
                cwd=self._workspace,
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
                            },
                            "evaluatorUid": os.getuid(),
                            "imageDigest": self._image_digest,
                            "exitCode": completed.returncode,
                        },
                    ),
                )
            )
        except Exception:
            # Socket drops, timeouts, perimeter crashes, malformed runner
            # responses, and probe failures are instrument uncertainty.  No
            # exception may become a fabricated task verdict or cross the port.
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

    def _probe_immutability(self) -> tuple[bool, tuple[str, ...]]:
        mismatches: list[str] = []
        if not self._oracle_digests:
            return False, ("oracle manifest is empty",)

        for relative, expected in sorted(self._oracle_digests.items()):
            path = self._oracle_path(relative)
            if path is None or not _DIGEST.fullmatch(expected) or not path.is_file():
                mismatches.append(relative)
                continue
            actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                mismatches.append(relative)
        return not mismatches, tuple(mismatches)

    def _oracle_path(self, relative: str) -> Path | None:
        pure = PurePosixPath(relative)
        if pure.is_absolute() or not pure.parts or ".." in pure.parts:
            return None
        candidate = (self._workspace / Path(*pure.parts)).resolve()
        try:
            candidate.relative_to(self._workspace)
        except ValueError:
            return None
        return candidate

    def _probe_non_pollution(self) -> tuple[bool, tuple[str, ...]]:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=self._workspace,
            capture_output=True,
            text=True,
            timeout=self._timeout_seconds,
            check=False,
        )
        if status.returncode != 0:
            raise RuntimeError("workspace tracking state unavailable")

        pollution: list[str] = []
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
        return not pollution, tuple(sorted(pollution))

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

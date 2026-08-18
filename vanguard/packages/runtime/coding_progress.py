"""Objective progress analysis, workspace hashing, and escalation decisions (REQ-TRUST-001, S31).

Canonical, deterministic signals computed directly from the workspace filesystem,
receipts, and test runs -- never from model-authored self-ratings or subjective confidence.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = [
    "EscalationAction",
    "EscalationDecision",
    "ProgressAnalyzer",
    "ProgressSignals",
    "compute_action_digest",
    "compute_patch_digest",
    "compute_test_fingerprint",
    "compute_workspace_digest",
]

#: Directories and files excluded from workspace content digests
WORKSPACE_EXCLUSIONS = frozenset({
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".coverage",
    ".system_generated",
    "evidence",
})


@dataclass(frozen=True, slots=True)
class ProgressSignals:
    """Canonical objective progress signals for a turn or attempt."""

    real_tool_action: bool
    workspace_changed: bool
    changed_paths: tuple[str, ...]
    test_fingerprint: str | None
    test_improved: bool
    malformed_response: bool
    translator_refusal: str | None
    repeated_action_digest: bool
    repeated_patch_digest: bool


class EscalationAction:
    """Deterministic escalation decisions."""

    RETRY_SAME = "retry_same"
    ROTATE_FREE_PROVIDER = "rotate_free_provider"
    REQUEST_DIAGNOSTIC_REPLAN = "request_diagnostic_replan"
    DESCEND_TO_FREE_EXECUTOR = "descend_to_free_executor"
    STOP_FAIL_CLOSED = "stop_fail_closed"
    REQUIRE_FRONTIER_AUTHORIZATION = "require_frontier_authorization"
    PROCEED_NORMAL = "proceed_normal"


@dataclass(frozen=True, slots=True)
class EscalationDecision:
    """Output recommendation of progress and failure analysis."""

    action: str
    reason: str
    target_tier: str | None = None
    target_model: str | None = None


def compute_workspace_digest(root: str | Path) -> tuple[str, dict[str, str]]:
    """Compute deterministic SHA256 digest of workspace files.

    Returns:
        (composite_sha256, path_to_hash_dict)
    """
    base = Path(root).resolve()
    if not base.is_dir():
        return "sha256:workspace_missing", {}

    file_hashes: dict[str, str] = {}
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(base).parts
        if any(part in WORKSPACE_EXCLUSIONS for part in rel_parts):
            continue
        rel_posix = path.relative_to(base).as_posix()
        try:
            content = path.read_bytes()
            file_hashes[rel_posix] = hashlib.sha256(content).hexdigest()
        except (OSError, PermissionError):
            continue

    composite = hashlib.sha256()
    for rel_path in sorted(file_hashes.keys()):
        composite.update(rel_path.encode("utf-8"))
        composite.update(file_hashes[rel_path].encode("utf-8"))

    return f"sha256:{composite.hexdigest()}", file_hashes


def compute_action_digest(verb: str, args: Mapping[str, Any] | None) -> str:
    """Compute canonical SHA256 digest of a requested tool action."""
    payload = {
        "verb": verb,
        "args": dict(args or {}),
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()}"


def compute_patch_digest(patch_content: str | bytes) -> str:
    """Compute canonical SHA256 digest of a patch."""
    data = patch_content.encode("utf-8") if isinstance(patch_content, str) else patch_content
    # Normalize line endings
    normalized = data.replace(b"\r\n", b"\n")
    return f"sha256:{hashlib.sha256(normalized).hexdigest()}"


def compute_test_fingerprint(
    argv: Sequence[str],
    exit_code: int,
    stdout: str = "",
    stderr: str = "",
) -> str:
    """Compute normalized test failure fingerprint.

    Captures command argv, exit code, parsed failed test names, and error kinds.
    """
    output = f"{stdout}\n{stderr}"
    # Parse unittest / pytest failure names
    failed_tests: list[str] = []
    # Match lines like "FAIL: test_foo (module.TestClass)" or "FAILED test_file.py::test_foo"
    for match in re.finditer(r"(?:FAIL|ERROR|FAILED)[:\s]+([\w\.\:\-\_]+)", output):
        name = match.group(1).strip()
        if name and name not in failed_tests:
            failed_tests.append(name)

    # Match error types like "AssertionError", "SyntaxError", "TypeError"
    error_kinds: list[str] = []
    for match in re.finditer(r"([A-Z]\w*(?:Error|Exception|Failure))", output):
        kind = match.group(1).strip()
        if kind and kind not in error_kinds:
            error_kinds.append(kind)

    canonical_repr = {
        "argv": list(argv),
        "exit_code": int(exit_code),
        "failed_tests": sorted(failed_tests),
        "error_kinds": sorted(error_kinds),
    }
    dumped = json.dumps(canonical_repr, sort_keys=True, separators=(",", ":"))
    return f"test-fp:{hashlib.sha256(dumped.encode('utf-8')).hexdigest()[:16]}"


class ProgressAnalyzer:
    """Tracks turns and attempts to detect stalls and make escalation decisions."""

    def __init__(self, initial_workspace_root: str | Path | None = None) -> None:
        self.workspace_root = Path(initial_workspace_root) if initial_workspace_root else None
        self._last_workspace_digest = ""
        self._last_file_hashes: dict[str, str] = {}
        if self.workspace_root and self.workspace_root.is_dir():
            self._last_workspace_digest, self._last_file_hashes = compute_workspace_digest(self.workspace_root)

        self._action_digests: set[str] = set()
        self._patch_digests: set[str] = set()
        self._last_test_fingerprint: str | None = None

        # Counters
        self.consecutive_malformed: int = 0
        self.consecutive_identical_test_failures: int = 0
        self.consecutive_unchanged_workspace_turns: int = 0
        self.no_progress_episodes: int = 0

    def analyze_turn(
        self,
        *,
        verb: str | None = None,
        args: Mapping[str, Any] | None = None,
        patch: str | None = None,
        malformed: bool = False,
        translator_refusal: str | None = None,
        test_result: tuple[Sequence[str], int, str, str] | None = None,
        workspace_root: str | Path | None = None,
    ) -> ProgressSignals:
        """Analyze one turn and update tracking state."""
        target_root = workspace_root or self.workspace_root
        workspace_changed = False
        changed_paths: list[str] = []
        if target_root:
            new_digest, new_hashes = compute_workspace_digest(target_root)
            if new_digest != self._last_workspace_digest:
                workspace_changed = True
                # Detect changed / added / removed paths
                all_paths = set(self._last_file_hashes.keys()) | set(new_hashes.keys())
                for p in all_paths:
                    if self._last_file_hashes.get(p) != new_hashes.get(p):
                        changed_paths.append(p)
                self._last_workspace_digest = new_digest
                self._last_file_hashes = new_hashes

        if workspace_changed:
            self.consecutive_unchanged_workspace_turns = 0
        else:
            self.consecutive_unchanged_workspace_turns += 1

        repeated_action = False
        if verb:
            act_digest = compute_action_digest(verb, args)
            if act_digest in self._action_digests:
                repeated_action = True
            else:
                self._action_digests.add(act_digest)

        repeated_patch = False
        if patch:
            patch_digest = compute_patch_digest(patch)
            if patch_digest in self._patch_digests:
                repeated_patch = True
            else:
                self._patch_digests.add(patch_digest)

        test_fp = None
        test_improved = False
        if test_result:
            argv, exit_code, stdout, stderr = test_result
            test_fp = compute_test_fingerprint(argv, exit_code, stdout, stderr)
            if test_fp == self._last_test_fingerprint:
                self.consecutive_identical_test_failures += 1
            else:
                if self._last_test_fingerprint is not None and exit_code == 0:
                    test_improved = True
                self.consecutive_identical_test_failures = 1
                self._last_test_fingerprint = test_fp
        else:
            self.consecutive_identical_test_failures = 0

        if malformed:
            self.consecutive_malformed += 1
        else:
            self.consecutive_malformed = 0

        real_action = bool(verb and not malformed and not translator_refusal)

        signals = ProgressSignals(
            real_tool_action=real_action,
            workspace_changed=workspace_changed,
            changed_paths=tuple(sorted(changed_paths)),
            test_fingerprint=test_fp,
            test_improved=test_improved,
            malformed_response=malformed,
            translator_refusal=translator_refusal,
            repeated_action_digest=repeated_action,
            repeated_patch_digest=repeated_patch,
        )
        return signals

    def record_episode_outcome(self, made_progress: bool) -> None:
        if made_progress:
            self.no_progress_episodes = 0
        else:
            self.no_progress_episodes += 1

    def decide_escalation(
        self,
        *,
        current_tier: str = "free",
        missing_key: bool = False,
        unknown_price: bool = False,
        workspace_missing: bool = False,
        frontier_requested: bool = False,
        frontier_authorized: bool = False,
        diagnosis_succeeded: bool = False,
    ) -> EscalationDecision:
        """Determine next action based on deterministic policy rules."""
        # Stop fail-closed conditions
        if missing_key:
            return EscalationDecision(
                action=EscalationAction.STOP_FAIL_CLOSED,
                reason="provider_key_missing",
            )
        if unknown_price:
            return EscalationDecision(
                action=EscalationAction.STOP_FAIL_CLOSED,
                reason="pricing_unknown",
            )
        if workspace_missing:
            return EscalationDecision(
                action=EscalationAction.STOP_FAIL_CLOSED,
                reason="workspace_missing",
            )

        # Frontier authorization check
        if frontier_requested and not frontier_authorized:
            return EscalationDecision(
                action=EscalationAction.REQUIRE_FRONTIER_AUTHORIZATION,
                reason="frontier_requires_explicit_authorization",
                target_tier="high",
            )

        # Successful diagnostic -> descend to free executor
        if diagnosis_succeeded:
            return EscalationDecision(
                action=EscalationAction.DESCEND_TO_FREE_EXECUTOR,
                reason="diagnostic_completed_descending_to_free_executor",
                target_tier="free",
            )

        # Malformed response rules
        if self.consecutive_malformed == 1:
            return EscalationDecision(
                action=EscalationAction.RETRY_SAME,
                reason="first_malformed_response_retrying_same_provider",
            )
        if self.consecutive_malformed >= 2:
            return EscalationDecision(
                action=EscalationAction.ROTATE_FREE_PROVIDER,
                reason="multiple_malformed_responses_rotating_free_provider",
                target_tier="free",
            )

        # Repeated identical test failure -> request diagnostic / replan
        if self.consecutive_identical_test_failures >= 2:
            return EscalationDecision(
                action=EscalationAction.REQUEST_DIAGNOSTIC_REPLAN,
                reason="repeated_identical_test_failure",
                target_tier="medium",
                target_model="deepseek/deepseek-v4-flash",
            )

        # 3 no-progress episodes -> request diagnostic / replan
        if self.no_progress_episodes >= 3:
            return EscalationDecision(
                action=EscalationAction.REQUEST_DIAGNOSTIC_REPLAN,
                reason="three_no_progress_episodes",
                target_tier="medium",
                target_model="deepseek/deepseek-v4-flash",
            )

        # Frontier authorization check
        if frontier_requested and not frontier_authorized:
            return EscalationDecision(
                action=EscalationAction.REQUIRE_FRONTIER_AUTHORIZATION,
                reason="frontier_requires_explicit_authorization",
                target_tier="high",
            )

        return EscalationDecision(
            action=EscalationAction.PROCEED_NORMAL,
            reason="progress_normal",
            target_tier=current_tier,
        )

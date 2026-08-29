"""Bounded autonomous coding grants (REQ-TRUST-001, K-17, S32).

Constructs an explicit, signed capability grant for autonomous INTERACTIVE execution
restricted strictly by workspace path, allowed verbs, command allowlists, turn/attempt expiry,
and budget ceilings. BENCHMARK mode remains fail-closed and cannot execute privileged writes.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .governance.approvals import ApprovalChallenge, OperatorSigner

__all__ = [
    "AutonomousGrant",
    "create_autonomous_grant",
    "validate_grant_request",
]

DEFAULT_ALLOWED_VERBS = ("fs.read", "fs.search", "patch.apply", "proc.exec")
DEFAULT_COMMAND_ALLOWLIST = ("git", "pytest", "python3", "python", "ruff")


@dataclass(frozen=True, slots=True)
class AutonomousGrant:
    """Signed, bounded authorization for autonomous coding episodes."""

    grant_id: str
    workspace_root: str
    allowed_verbs: tuple[str, ...]
    command_allowlist: tuple[str, ...]
    max_turns: int
    max_attempts: int
    max_budget_micros: int
    network_egress: bool
    created_at: str
    reviewer: str
    signature: str
    signer_public_key: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "grantId": self.grant_id,
            "workspaceRoot": self.workspace_root,
            "allowedVerbs": list(self.allowed_verbs),
            "commandAllowlist": list(self.command_allowlist),
            "maxTurns": self.max_turns,
            "maxAttempts": self.max_attempts,
            "maxBudgetMicros": self.max_budget_micros,
            "networkEgress": self.network_egress,
            "createdAt": self.created_at,
            "reviewer": self.reviewer,
            "signature": self.signature,
            "signerPublicKey": self.signer_public_key,
        }


def create_autonomous_grant(
    workspace_root: str | Path,
    *,
    allowed_verbs: Sequence[str] = DEFAULT_ALLOWED_VERBS,
    command_allowlist: Sequence[str] = DEFAULT_COMMAND_ALLOWLIST,
    max_turns: int = 30,
    max_attempts: int = 4,
    max_budget_micros: int = 500_000,
    network_egress: bool = False,
    reviewer: str = "vanguard-autonomous-operator",
    seed_key: bytes | None = None,
    signer: OperatorSigner | None = None,
) -> AutonomousGrant:
    """Issue a signed, cryptographically attributable autonomous grant.

    The signing identity must be supplied. A shared literal default -- which
    this parameter previously carried -- makes every grant in every
    installation attributable to the same key, which is the opposite of
    "cryptographically attributable": anyone holding the source could mint a
    grant indistinguishable from the operator's own.

    Pass `signer` (preferred: the installation's `OperatorSigner`), or
    `seed_key` for a caller-controlled ephemeral identity.
    """
    if signer is None:
        if seed_key is None:
            raise ValueError(
                "create_autonomous_grant requires a signer or an explicit seed_key; "
                "there is no default signing identity"
            )
        signer = OperatorSigner(seed_key)

    resolved_ws = Path(workspace_root).resolve().as_posix()
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    descriptor = {
        "workspaceRoot": resolved_ws,
        "allowedVerbs": sorted(allowed_verbs),
        "commandAllowlist": sorted(command_allowlist),
        "maxTurns": max_turns,
        "maxAttempts": max_attempts,
        "maxBudgetMicros": max_budget_micros,
        "networkEgress": network_egress,
        "createdAt": created_at,
        "reviewer": reviewer,
    }
    canonical_bytes = json.dumps(descriptor, sort_keys=True).encode("utf-8")
    grant_id = f"grant-{hashlib.sha256(canonical_bytes).hexdigest()[:12]}"
    digest_str = f"sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"

    challenge = ApprovalChallenge(
        approval_id=grant_id,
        process_id="autonomous-coding-session",
        action="autonomous_grant",
        normalized_diff="",
        args_digest=digest_str,
        descriptor_digest=digest_str,
        principal=reviewer,
        expires_at="2099-12-31T23:59:59.000Z",
    )

    decision = signer.approve(challenge, reviewer=reviewer)

    return AutonomousGrant(
        grant_id=grant_id,
        workspace_root=resolved_ws,
        allowed_verbs=tuple(sorted(allowed_verbs)),
        command_allowlist=tuple(sorted(command_allowlist)),
        max_turns=max_turns,
        max_attempts=max_attempts,
        max_budget_micros=max_budget_micros,
        network_egress=network_egress,
        created_at=created_at,
        reviewer=reviewer,
        signature=decision.signature,
        signer_public_key=signer.public_bytes.hex(),
    )


def validate_grant_request(
    grant: AutonomousGrant,
    *,
    verb: str,
    target_path: str | Path | None = None,
    command_argv: Sequence[str] | None = None,
    turn: int = 1,
    spent_micros: int = 0,
) -> tuple[bool, str]:
    """Check if an effect request strictly satisfies the bounds of the autonomous grant."""
    # Check verb membership
    if verb not in grant.allowed_verbs:
        return False, f"verb_denied:{verb}"

    # Check turn expiry
    if turn > grant.max_turns:
        return False, f"turn_limit_exceeded:{turn}>{grant.max_turns}"

    # Check budget ceiling
    if spent_micros > grant.max_budget_micros:
        return False, f"budget_ceiling_exceeded:{spent_micros}>{grant.max_budget_micros}"

    # Check path containment
    if target_path is not None:
        try:
            resolved_ws = Path(grant.workspace_root).resolve()
            candidate = Path(target_path)
            resolved_target = (
                candidate.resolve()
                if candidate.is_absolute()
                else (resolved_ws / candidate).resolve()
            )
            resolved_target.relative_to(resolved_ws)
        except ValueError:
            return False, f"workspace_path_escape_denied:{target_path}"

    # Check command binary allowlist
    if verb == "proc.exec" and command_argv:
        if isinstance(command_argv, str):
            try:
                import shlex
                parsed_argv = shlex.split(command_argv)
            except Exception:
                parsed_argv = command_argv.split()
        else:
            parsed_argv = [str(x) for x in command_argv]
        if parsed_argv:
            binary = Path(parsed_argv[0]).name
            if binary not in grant.command_allowlist:
                return False, f"command_disallowed:{binary}"

    return True, "ok"

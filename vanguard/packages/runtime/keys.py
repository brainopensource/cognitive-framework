"""Per-installation operator key material and interactive approval.

Owning contract: `I-5`, `GOV-01`, ADR-0062, WP-C1.

The operator's Ed25519 private key is the root of the approval trust spine. A
key that ships inside the distribution is not a key: every installation would
hold the same secret, so any reader of the source could mint approvals for any
other installation. This module is the only supported way for a product
entrypoint to obtain an `OperatorSigner`, and it refuses every shortcut that
would put key material back into the tree:

- there is no default seed, and no derivation from a constant;
- a key is created only under explicit initialisation (`allow_create=True`),
  never as a side effect of running a task;
- a key file readable by anyone but its owner is refused rather than loaded;
- an absent key is `KeyMaterialUnavailable`, never a freshly minted identity.

Approval follows the same rule in the other direction. `interactive_approver`
puts the challenge in front of a human and signs only what that human accepted.
When there is no human -- no TTY -- it denies, because an unattended process has
no reviewer and a self-approving signature attests to nothing. Unattended
execution stays possible, but only through an explicit scoped autonomous grant
the operator created deliberately (`autonomous_grant.py`).
"""

from __future__ import annotations

import os
import secrets
import stat
import sys
from pathlib import Path
from typing import Any, Callable, Protocol, TextIO

from .governance.approvals import ApprovalChallenge, ApprovalDecision, OperatorSigner

__all__ = [
    "DEFAULT_KEY_DIR",
    "InsecureKeyMaterial",
    "KeyMaterialError",
    "KeyMaterialUnavailable",
    "default_key_path",
    "interactive_approver",
    "load_operator_signer",
    "render_challenge",
]

#: Ed25519 seed length. A file of any other size is not a seed we wrote.
_SEED_BYTES = 32

#: Only the owner may read or write the key. Anything wider is refused.
_REQUIRED_MODE = 0o600
_REQUIRED_DIR_MODE = 0o700


class KeyMaterialError(RuntimeError):
    """Base for every refusal to produce a signer."""


class KeyMaterialUnavailable(KeyMaterialError):
    """No key exists and this call site is not allowed to create one.

    Deliberately distinct from `InsecureKeyMaterial`: "you have not initialised"
    is an ordinary first-run state with an obvious remedy, while "your key is
    world-readable" is a security finding.
    """


class InsecureKeyMaterial(KeyMaterialError):
    """Key material exists but its storage cannot be trusted."""


def DEFAULT_KEY_DIR() -> Path:  # noqa: N802 - callable so tests can redirect HOME
    """The per-user key directory. Resolved per call so `HOME` stays authoritative."""
    return Path(os.path.expanduser("~")) / ".vanguard" / "keys"


def default_key_path(key_id: str = "operator") -> Path:
    return DEFAULT_KEY_DIR() / f"{key_id}.ed25519"


def load_operator_signer(
    *,
    allow_create: bool = False,
    key_path: Path | None = None,
    key_id: str = "operator-key-default",
) -> OperatorSigner:
    """Return this installation's operator signer.

    `allow_create` is the initialisation switch. `vanguard init` passes `True`;
    every execution path passes `False`, so running a task can never silently
    mint an identity that no human chose to create.
    """
    path = key_path if key_path is not None else default_key_path()

    if path.exists():
        return OperatorSigner(_read_seed(path), key_id=key_id)

    if not allow_create:
        raise KeyMaterialUnavailable(
            f"no operator key at {path}; run `vanguard init` to create one"
        )

    return OperatorSigner(_create_seed(path), key_id=key_id)


def _read_seed(path: Path) -> bytes:
    info = path.stat()
    mode = stat.S_IMODE(info.st_mode)
    if mode != _REQUIRED_MODE:
        raise InsecureKeyMaterial(
            f"{path} has mode {mode:04o}; refusing to load key material that is not "
            f"{_REQUIRED_MODE:04o}. Fix with: chmod 600 {path}"
        )
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise InsecureKeyMaterial(f"{path} is not owned by the current user")

    seed = path.read_bytes()
    if len(seed) != _SEED_BYTES:
        # OperatorSigner would hash a wrong-length input into *some* key. That
        # silent recovery is exactly how a corrupt file becomes a stable but
        # unintended identity, so refuse instead.
        raise InsecureKeyMaterial(
            f"{path} holds {len(seed)} bytes; an Ed25519 seed is {_SEED_BYTES}"
        )
    return seed


def _create_seed(path: Path) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path.parent, _REQUIRED_DIR_MODE)
    except OSError:  # pragma: no cover - platform dependent
        pass

    seed = secrets.token_bytes(_SEED_BYTES)
    # O_EXCL so a concurrent initialisation loses instead of overwriting a key
    # that may already have signed approvals recorded in a ledger.
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, _REQUIRED_MODE)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(seed)
    except BaseException:
        try:
            path.unlink()
        except OSError:  # pragma: no cover
            pass
        raise
    return seed


class _Approver(Protocol):
    def __call__(self, challenge: ApprovalChallenge) -> ApprovalDecision: ...


def render_challenge(challenge: Any) -> str:
    """Human-reviewable rendering of what is about to be authorised.

    The reviewer signs the argument digest, so what is shown must be the
    material that digest covers -- not a summary of it.
    """
    lines = [
        "",
        "=" * 68,
        "  APPROVAL REQUIRED",
        "=" * 68,
        f"  action      : {getattr(challenge, 'action', '<unknown>')}",
        f"  principal   : {getattr(challenge, 'principal', '<unknown>')}",
        f"  approval id : {getattr(challenge, 'approval_id', '<unknown>')}",
        f"  args digest : {getattr(challenge, 'args_digest', '<unknown>')}",
        f"  descriptor  : {getattr(challenge, 'descriptor_digest', '<unknown>')}",
        f"  expires at  : {getattr(challenge, 'expires_at', '<unknown>')}",
        "-" * 68,
    ]
    material = getattr(challenge, "normalized_diff", "")
    if material:
        lines.extend(str(material).rstrip("\n").splitlines())
        lines.append("-" * 68)
    return "\n".join(lines)


def interactive_approver(
    signer: OperatorSigner,
    *,
    reviewer: str,
    stream: TextIO | None = None,
    output: TextIO | None = None,
    prompt: Callable[[str], str] | None = None,
) -> _Approver:
    """An approver that asks a human, and denies when there is no human.

    Returns a *rejection* rather than raising when the operator declines: a
    refusal is a legitimate signed outcome that the ledger should record, while
    the absence of a reviewer is a capability failure.
    """
    in_stream = stream if stream is not None else sys.stdin
    out_stream = output if output is not None else sys.stderr
    ask = prompt if prompt is not None else input

    def approve(challenge: ApprovalChallenge) -> ApprovalDecision:
        if not _is_interactive(in_stream):
            raise KeyMaterialUnavailable(
                "approval required but no interactive terminal is attached; "
                "supply an explicit scoped autonomous grant for unattended runs"
            )
        print(render_challenge(challenge), file=out_stream, flush=True)
        try:
            answer = ask("approve? [y/N] ")
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            return signer.reject(challenge, reviewer=reviewer)
        return signer.approve(challenge, reviewer=reviewer)

    return approve


def _is_interactive(stream: TextIO) -> bool:
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False

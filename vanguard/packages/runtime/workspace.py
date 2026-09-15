"""Runtime workspace management, child isolation and fenced mutation ownership.

Two responsibilities live here, and they are not the same thing.

The first is the long-standing one: workspace root resolution and path
validation, re-exported from `domain.workspace` so runtime callers have one
import site. Those names are unchanged.

The second is `T-141`. `RuntimeChildRunner` used to hand every spawned child
`repo_path=parent_task.repo_path` -- the parent's own tree, unmodified.
Recursion was genuine, authority was attenuated and spend landed in one ledger,
but the *filesystem* was shared by every node in the tree with nothing
serialising it. Two causally-ready siblings interleaved their edits, a child
could overwrite its parent's working state, and a child that died mid-edit left
the shared tree in a condition nobody had declared.

`DIR-C5`: git worktrees alone are not containment. A worktree hands a child a
separate *directory*. It does not say who may mutate the shared tree, for how
long, or what becomes true when that owner dies. This module is the missing
half, and it is deliberately three separable pieces:

* **An isolated writable view.** Each child mutates only its own subtree. The
  boundary is enforced on every resolution, after symlinks, so containment does
  not depend on the child's cooperation or on how a path is spelled.
* **An exclusive, expiring, token-checked fence.** Mutation of the *shared*
  tree is serialised to one owner at a time. Expiry alone would not be
  containment: the dangerous writer is the one descheduled mid-call that wakes
  after its lease was reclaimed still holding a ticket it believes is good. A
  takeover therefore invalidates that ticket by monotonic **token**, so a stale
  writer fails closed without consulting a clock it cannot be trusted to read.
* **Content-addressed candidate retention, then controlled integration.** The
  child's work is frozen and retained durably *before* anything touches the
  shared tree, and acceptance is a marker written *last*. Everything between
  those two points is replayable.

The crash contract falls out of that ordering rather than from a lock:

* crash before retention -- nothing was accepted, and nothing is claimed;
* crash after retention, before acceptance -- the candidate is on disk and
  `recover()` re-applies it in full, so acceptance is never partial;
* crash after acceptance -- the marker is keyed by candidate digest, so a
  replayed integration is a no-op and no effect settles twice;
* crash during cleanup -- the lease is merely left held and expires; nothing
  about acceptance depends on cleanup having run.

Scope: this is workspace lifecycle only. It is not a CAS journal, it does not
enable concurrent mutating workers, and it makes no provider calls.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..domain.workspace import (
    DEFAULT_WORKSPACE_ROOT,
    ENV_WORKSPACE_ROOT,
    controlled_environment,
    get_workspace_path,
    get_workspace_root,
    validate_workspace_path,
)

__all__ = [
    "DEFAULT_WORKSPACE_ROOT",
    "ENV_WORKSPACE_ROOT",
    "controlled_environment",
    "get_workspace_path",
    "get_workspace_root",
    "validate_workspace_path",
    # T-141
    "ChildWorkspace",
    "ChildWorkspaceSupervisor",
    "MutationTicket",
    "OwnershipConflict",
    "StaleWriterError",
    "WorkspaceEscapeError",
    "WorkspaceFenceError",
    "CONTROL_DIRNAME",
    "DEFAULT_LEASE_SECONDS",
]

#: Where child views and fence state live, relative to the shared tree. Inside
#: the tree so a restart finds it without being told, and named so that
#: integration can refuse to write into it (a candidate that could rewrite the
#: control state could forge its own acceptance).
CONTROL_DIRNAME = os.path.join(".vanguard", "children")

#: How long one ownership lease is good for. A lease is a bound on how long a
#: *dead* owner can block the tree, not a bound on useful work: a live owner
#: renews by re-acquiring.
DEFAULT_LEASE_SECONDS = 300.0

_CANDIDATE = "candidate.json"
_INTEGRATED = "integrated.json"
_FENCE = "fence.json"
_VIEW = "view"


class WorkspaceEscapeError(RuntimeError):
    """A path resolved outside the view that was allowed to contain it."""


class WorkspaceFenceError(RuntimeError):
    """Base for every refusal to mutate the shared tree."""


class OwnershipConflict(WorkspaceFenceError):
    """Someone else holds an unexpired lease on the shared tree."""


class StaleWriterError(WorkspaceFenceError):
    """This ticket no longer speaks for the shared tree."""


def _atomic_write(path: Path, text: str) -> None:
    """Replace `path` in one step, or leave the previous contents intact.

    Every durable fact this module records goes through here. A half-written
    marker would be indistinguishable from a forged one on the next read.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A truncated or absent record is *absent*, never a default. Reading it
        # as an empty success is how a crash turns into a forged acceptance.
        return None


@dataclass(frozen=True, slots=True)
class MutationTicket:
    """Proof of exclusive mutation ownership, valid until superseded.

    `token` is the authority, not `expires_at`. The deadline says when the
    lease *may* be reclaimed; the token says whether it already was.
    """

    child_id: str
    token: int
    expires_at: float


class ChildWorkspace:
    """One child's isolated writable view.

    Containment is checked on resolution rather than on construction, and after
    symlinks, so neither a traversal spelling (`../`, `a/../../b`), an absolute
    path, nor a symlink planted inside the view can address anything the view
    does not own.
    """

    __slots__ = ("child_id", "root")

    def __init__(self, child_id: str, root: Path) -> None:
        self.child_id = child_id
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relpath: str) -> Path:
        """The absolute path `relpath` names inside this view, or refuse."""
        candidate = Path(relpath)
        if candidate.is_absolute():
            # Rebasing an absolute path onto the view would silently grant the
            # child a write it explicitly asked to perform somewhere else.
            raise WorkspaceEscapeError(
                f"{self.child_id}: absolute path {relpath!r} is outside its view")

        base = self.root.resolve()
        target = (base / candidate).resolve()
        if target != base and base not in target.parents:
            raise WorkspaceEscapeError(
                f"{self.child_id}: {relpath!r} resolves outside its view")
        return target

    def write(self, relpath: str, text: str) -> Path:
        target = self.resolve(relpath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def read(self, relpath: str) -> str:
        return self.resolve(relpath).read_text(encoding="utf-8")

    def entries(self) -> Mapping[str, str]:
        """Every regular file in the view, as `relpath -> text`, sorted.

        Symlinks are skipped rather than followed: a candidate is a statement
        about this child's own content, and a link's target is not that.
        """
        base = self.root.resolve()
        found: dict[str, str] = {}
        for path in sorted(base.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                found[path.relative_to(base).as_posix()] = path.read_text(
                    encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
        return found


class ChildWorkspaceSupervisor:
    """Isolated views for children; one serialised fence over the shared tree.

    Holds no policy and mints no identities: `child_id` arrives already derived
    by `delegation.derive_child_id`, which is content-addressed and therefore
    restart-stable. That is what makes retention *recoverable* rather than
    merely durable -- a retried spawn lands on the same view and finds its own
    work rather than starting a second one beside it.
    """

    def __init__(
        self,
        shared_root: Path | str,
        *,
        now: Callable[[], float] = time.time,
        lease_seconds: float = DEFAULT_LEASE_SECONDS,
    ) -> None:
        self.shared_root = Path(shared_root).resolve()
        self.control_dir = self.shared_root / CONTROL_DIRNAME
        self.control_dir.mkdir(parents=True, exist_ok=True)
        self._now = now
        self._lease_seconds = float(lease_seconds)

    # -- views -------------------------------------------------------------

    def workspace_for(self, child_id: str) -> ChildWorkspace:
        """This child's view, created on first use and stable across restarts."""
        return ChildWorkspace(child_id, self._child_dir(child_id) / _VIEW)

    def _child_dir(self, child_id: str) -> Path:
        if not child_id or "/" in child_id or "\\" in child_id or child_id in {".", ".."}:
            raise WorkspaceEscapeError(f"unusable child id {child_id!r}")
        return self.control_dir / child_id

    # -- the fence ---------------------------------------------------------

    def _fence_path(self) -> Path:
        return self.control_dir / _FENCE

    def _fence(self) -> dict[str, Any]:
        return _read_json(self._fence_path()) or {"holder": None, "token": 0, "expires_at": 0.0}

    def acquire(self, child_id: str) -> MutationTicket:
        """Take exclusive ownership of the shared tree, or refuse.

        Re-acquiring as the current holder renews rather than conflicts: a
        retry after a crash is the same writer returning, not a competitor.
        """
        fence = self._fence()
        holder = fence.get("holder")
        expires_at = float(fence.get("expires_at") or 0.0)
        if holder and holder != child_id and self._now() < expires_at:
            raise OwnershipConflict(
                f"shared workspace is owned by {holder} until {expires_at}")

        token = int(fence.get("token") or 0) + 1
        ticket = MutationTicket(
            child_id=child_id,
            token=token,
            expires_at=self._now() + self._lease_seconds,
        )
        _atomic_write(self._fence_path(), json.dumps({
            "holder": child_id, "token": token, "expires_at": ticket.expires_at,
        }, sort_keys=True))
        return ticket

    def release(self, ticket: MutationTicket) -> None:
        """Give the tree back -- but only if this ticket still holds it.

        A late release from a writer whose lease was already reclaimed must not
        free the *new* owner's lease. The token counter is preserved so it
        never goes backwards.
        """
        fence = self._fence()
        if int(fence.get("token") or 0) != ticket.token:
            return
        _atomic_write(self._fence_path(), json.dumps({
            "holder": None, "token": int(fence.get("token") or 0), "expires_at": 0.0,
        }, sort_keys=True))

    def _validate(self, ticket: MutationTicket) -> None:
        fence = self._fence()
        if fence.get("holder") != ticket.child_id or int(fence.get("token") or 0) != ticket.token:
            raise StaleWriterError(
                f"{ticket.child_id}: ticket {ticket.token} was superseded")
        if self._now() >= float(fence.get("expires_at") or 0.0):
            raise StaleWriterError(f"{ticket.child_id}: lease expired")

    # -- retention ---------------------------------------------------------

    def retain_candidate(self, child_id: str) -> str:
        """Freeze the child's view into a durable, content-addressed candidate.

        Called before the shared tree is touched, so an accepted child's work
        can never be lost to a crash that happens during integration.
        """
        entries = dict(self.workspace_for(child_id).entries())
        digest = digest_of({"childId": child_id, "entries": entries})
        _atomic_write(
            self._child_dir(child_id) / _CANDIDATE,
            json.dumps({"digest": digest, "entries": entries}, sort_keys=True))
        return digest

    def candidate_digest(self, child_id: str) -> str | None:
        record = _read_json(self._child_dir(child_id) / _CANDIDATE)
        return str(record["digest"]) if record and record.get("digest") else None

    def settled_digest(self, child_id: str) -> str | None:
        """Which candidate has been accepted, if any. The acceptance marker."""
        record = _read_json(self._child_dir(child_id) / _INTEGRATED)
        return str(record["digest"]) if record and record.get("digest") else None

    # -- integration -------------------------------------------------------

    def integrate(self, ticket: MutationTicket, *, candidate_digest: str) -> str:
        """Apply this child's retained candidate to the shared tree, once.

        Returns `"integrated"` or `"already_integrated"`. The second is not a
        failure: a retry after a crash during handoff cannot know whether the
        first attempt landed, and must not settle the same effect twice.
        """
        self._validate(ticket)
        if self.settled_digest(ticket.child_id) == candidate_digest:
            return "already_integrated"

        record = _read_json(self._child_dir(ticket.child_id) / _CANDIDATE)
        if not record or record.get("digest") != candidate_digest:
            # Refused *before* anything is applied: a candidate that cannot be
            # named is a candidate that must not be accepted.
            raise StaleWriterError(
                f"{ticket.child_id}: no retained candidate {candidate_digest}")

        self._apply(ticket.child_id, record)
        return "integrated"

    def _apply(self, child_id: str, record: Mapping[str, Any]) -> None:
        """Land every entry, then record acceptance. Order is the contract."""
        for relpath in sorted(record.get("entries", {})):
            self._apply_one(child_id, relpath, record=record)
        _atomic_write(
            self._child_dir(child_id) / _INTEGRATED,
            json.dumps({"digest": record["digest"]}, sort_keys=True))

    def _apply_one(
        self,
        child_id: str,
        relpath: str,
        *,
        record: Mapping[str, Any] | None = None,
    ) -> Path:
        """Land one entry of a retained candidate into the shared tree."""
        if record is None:
            record = _read_json(self._child_dir(child_id) / _CANDIDATE) or {}
        target = self._shared_target(relpath)
        _atomic_write(target, record.get("entries", {})[relpath])
        return target

    def _shared_target(self, relpath: str) -> Path:
        """Where `relpath` lands in the shared tree, or refuse.

        The control directory is excluded: a candidate able to rewrite fence or
        acceptance state could forge its own settlement.
        """
        candidate = Path(relpath)
        if candidate.is_absolute():
            raise WorkspaceEscapeError(f"candidate entry {relpath!r} is absolute")
        target = (self.shared_root / candidate).resolve()
        if self.shared_root not in target.parents:
            raise WorkspaceEscapeError(
                f"candidate entry {relpath!r} resolves outside the shared tree")
        control = self.control_dir.resolve()
        if target == control or control in target.parents:
            raise WorkspaceEscapeError(
                f"candidate entry {relpath!r} would rewrite workspace control state")
        return target

    # -- recovery ----------------------------------------------------------

    def recover(self) -> tuple[str, ...]:
        """Finish every retained-but-unaccepted candidate. Idempotent.

        This is what makes acceptance all-or-nothing without a transaction: a
        candidate whose marker is missing is re-applied *in full*, so a tree
        left half-written by a crash converges rather than staying partial. A
        candidate whose marker already matches is left alone, which is what
        stops recovery from settling an effect a second time.
        """
        recovered: list[str] = []
        for child_dir in sorted(self.control_dir.iterdir()):
            if not child_dir.is_dir():
                continue
            child_id = child_dir.name
            record = _read_json(child_dir / _CANDIDATE)
            if not record or not record.get("digest"):
                continue
            if self.settled_digest(child_id) == record["digest"]:
                continue
            self._apply(child_id, record)
            recovered.append(child_id)
        return tuple(recovered)

    def discard(self, child_id: str) -> None:
        """Drop a child's view once its candidate is settled.

        Cleanup is deliberately the *last* thing and owns nothing: acceptance
        has already been recorded, so a crash here costs disk space and never
        correctness.
        """
        if self.settled_digest(child_id) is None:
            raise WorkspaceFenceError(
                f"{child_id}: refusing to discard an unsettled workspace")
        shutil.rmtree(self._child_dir(child_id) / _VIEW, ignore_errors=True)

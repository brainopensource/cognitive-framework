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
* **Base-bound retention, exterior verification, then publication.** The
  child's work is frozen and retained durably *before* anything touches the
  shared tree, bound to the base it was computed against. What an evaluator
  then verifies is the **combined tree** -- that base overlaid with the
  candidate -- staged on disk, and what publication writes is byte-for-byte
  that same staged tree (`DIR-C7`). Acceptance is a marker written *last*.

The crash contract falls out of that ordering rather than from a lock:

* crash before retention -- nothing was accepted, and nothing is claimed;
* crash after retention, before authorization -- the candidate is on disk but
  nothing verified it, so `recover()` deliberately leaves it alone. A retained
  candidate is work, never permission;
* crash after authorization, before acceptance -- the verified tree is on disk
  and `recover()` re-applies it in full, so acceptance is never partial;
* crash after acceptance -- the marker is keyed by the published tree digest,
  so a replayed publication is a no-op and no effect settles twice;
* crash during cleanup -- the lease is merely left held and expires; nothing
  about acceptance depends on cleanup having run.

Scope: this is workspace lifecycle only. It is not a CAS journal, it does not
enable concurrent mutating workers, and it makes no provider calls.
"""

from __future__ import annotations

import json
import fcntl
import tempfile
from functools import wraps
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..kernel.attenuation import Scope
from ..ports.child_runtime import ChildRunPlan
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
    "CombinedTree",
    "PublicationAuthority",
    "PublicationRefused",
    "MutationTicket",
    "OwnershipConflict",
    "PublicationVerdict",
    "StaleBaseError",
    "StaleWriterError",
    "UnverifiedPublicationError",
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

#: Directories that are *about* the working tree rather than part of it. A
#: candidate never describes them and publication never writes into them, so
#: folding them into the base would make an ordinary `git` operation look like
#: a concurrent mutation and refuse every publication on a real repository.
EXCLUDED_DIRNAMES = frozenset({".git", ".hg", ".svn"})

#: How long one ownership lease is good for. A lease is a bound on how long a
#: *dead* owner can block the tree, not a bound on useful work: a live owner
#: renews by re-acquiring.
DEFAULT_LEASE_SECONDS = 300.0

_CANDIDATE = "candidate.json"
_BASE = "base.json"
_AUTHORIZED = "authorized.json"
_INTEGRATED = "integrated.json"
_FENCE = "fence.json"
_VIEW = "view"
_STAGED = "staged"


class WorkspaceEscapeError(RuntimeError):
    """A path resolved outside the view that was allowed to contain it."""


class WorkspaceFenceError(RuntimeError):
    """Base for every refusal to mutate the shared tree."""


class OwnershipConflict(WorkspaceFenceError):
    """Someone else holds an unexpired lease on the shared tree."""


class StaleWriterError(WorkspaceFenceError):
    """This ticket no longer speaks for the shared tree."""


class StaleBaseError(WorkspaceFenceError):
    """The shared tree moved under a candidate that was computed against it."""


class UnverifiedPublicationError(WorkspaceFenceError):
    """Nothing exterior verified the exact tree this would publish."""


def _atomic_write(path: Path, text: str) -> None:
    """Replace `path` in one step, or leave the previous contents intact.

    Every durable fact this module records goes through here. A half-written
    marker would be indistinguishable from a forged one on the next read.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".workspace-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


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


class PublicationRefused(RuntimeError):
    """A child's work was not published, and nothing pretends it was."""


@dataclass(frozen=True, slots=True)
class PublicationAuthority:
    """The live authority a child's work must still hold to be published.

    Built by `SpawnAdapter` at the moment it dispatches, because that is the
    only place that holds the *granted* scope and the parent's *remaining*
    balance. It is passed down rather than captured, so the runner revalidates
    what the kernel actually decided instead of re-deriving a second opinion.

    `recheck` runs again after the child has finished and immediately before
    the shared tree changes. A grant that expired during a long child, or a
    balance a sibling consumed in the meantime, refuses the publication --
    completion is not a licence to spend authority that has since lapsed.
    """

    grant: Scope
    remaining_budget: Callable[[], Mapping[str, int]]
    now: Callable[[], str]

    def recheck(self, plan: ChildRunPlan, cost: Mapping[str, int]) -> str:
        """`""` when the child may still publish, else why it may not."""
        expires_at = str(self.grant.constraints.expires_at or "")
        if expires_at and self.now() >= expires_at:
            return f"grant expired at {expires_at}"
        if not set(plan.authority).issubset(set(self.grant.actions)):
            return "child holds authority the current grant does not carry"
        remaining = dict(self.remaining_budget())
        for dimension, spent in dict(cost).items():
            if dimension not in remaining:
                continue
            if int(spent) > int(remaining.get(dimension, 0)):
                return (f"budget dimension {dimension!r} spent {spent} against "
                        f"{remaining.get(dimension, 0)} remaining")
        return ""


@dataclass(frozen=True, slots=True)
class PublicationVerdict:
    """What an exterior evaluator said about one exact tree.

    Runtime never constructs a passing verdict from a terminal state: this is
    a carrier for what the evaluator gateway already admitted. `subject_digest`
    is the identity of the tree that was *actually* verified, and publication
    compares it to the tree it is about to write rather than trusting the
    caller to have verified the right thing.
    """

    subject_digest: str
    disposition: str
    envelope_digest: str = ""

    def passed(self) -> bool:
        return self.disposition.strip().lower() in {"pass", "passed"}


@dataclass(frozen=True, slots=True)
class CombinedTree:
    """The exact tree a publication would write: base overlaid with candidate.

    Staged on disk so an exterior evaluator can verify *this* content, and
    carried by digest so the thing verified and the thing published are the
    same object rather than two computations that happen to agree.
    """

    child_id: str
    digest: str
    base_digest: str
    candidate_digest: str
    root: Path
    entries: Mapping[str, str]


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
            except (OSError, UnicodeDecodeError) as exc:
                raise WorkspaceEscapeError(
                    f"cannot retain complete text candidate: {path}") from exc
        return found


def _serialized(method: Callable[..., Any]) -> Callable[..., Any]:
    """Serialize lifecycle operations across threads and supervisor processes."""
    @wraps(method)
    def locked(self: Any, *args: Any, **kwargs: Any) -> Any:
        descriptor = os.open(
            self.control_dir / "lifecycle.lock",
            os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            return method(self, *args, **kwargs)
        finally:
            os.close(descriptor)
    return locked


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

    def workspace_for(self, child_id: str, *, seed: bool = False) -> ChildWorkspace:
        """This child's view, created on first use and stable across restarts.

        The first creation also binds the **base**: the state of the shared
        tree this child's work will be computed against. Publication later
        revalidates that binding, so a candidate produced against a tree that
        has since moved is refused rather than silently overwriting whatever
        arrived in the meantime.

        `seed` materialises the shared tree into the view, which is what a
        brownfield child needs to do real work. It is opt-in because an
        unseeded view is the stricter default: a child that was given nothing
        cannot leak anything it was not handed.
        """
        view = ChildWorkspace(child_id, self._child_dir(child_id) / _VIEW)
        base = self._bind_base(child_id)
        if seed and not any(view.root.iterdir()):
            for relpath, text in base["entries"].items():
                view.write(relpath, text)
        return view

    def _bind_base(self, child_id: str) -> dict[str, Any]:
        """Record, once, the shared-tree state this child is derived from."""
        path = self._child_dir(child_id) / _BASE
        record = _read_json(path)
        if isinstance(record, dict) and isinstance(record.get("entries"), dict):
            return record
        entries = dict(self.shared_entries())
        record = {"digest": digest_of({"entries": entries}), "entries": entries}
        _atomic_write(path, json.dumps(record, sort_keys=True))
        return record

    def shared_entries(self) -> Mapping[str, str]:
        """Every regular file in the shared tree except the control state.

        Control state is excluded because it is *about* the tree rather than
        part of it: including it would make every fence write look like a base
        change and make a stale base indistinguishable from ordinary progress.
        """
        base = self.shared_root
        control = self.control_dir.resolve()
        found: dict[str, str] = {}
        for path in sorted(base.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(base)
            if EXCLUDED_DIRNAMES.intersection(relative.parts[:-1]):
                continue
            resolved = path.resolve()
            if resolved == control or control in resolved.parents:
                continue
            try:
                found[relative.as_posix()] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                # A binary or unreadable file is not text this module can bind.
                # It is excluded from the base rather than guessed at, and a
                # candidate can never name it (`entries` would refuse too).
                continue
        return found

    def shared_digest(self) -> str:
        """The identity of the shared tree right now."""
        return digest_of({"entries": dict(self.shared_entries())})

    def bound_base(self, child_id: str) -> str | None:
        """The base digest this child's work is bound to, if it has one."""
        record = _read_json(self._child_dir(child_id) / _BASE)
        if not isinstance(record, dict) or not isinstance(record.get("entries"), dict):
            return None
        return str(record.get("digest") or "") or None

    def _child_dir(self, child_id: str) -> Path:
        if not child_id or "/" in child_id or "\\" in child_id or child_id in {".", ".."}:
            raise WorkspaceEscapeError(f"unusable child id {child_id!r}")
        return self.control_dir / child_id

    # -- the fence ---------------------------------------------------------

    def _fence_path(self) -> Path:
        return self.control_dir / _FENCE

    def _fence(self) -> dict[str, Any]:
        path = self._fence_path()
        if not path.exists():
            return {"holder": None, "token": 0, "expires_at": 0.0}
        record = _read_json(path)
        if not isinstance(record, dict) or not {
            "holder", "token", "expires_at"
        }.issubset(record):
            raise StaleWriterError("workspace fence is corrupt")
        return record

    @_serialized
    def acquire(self, child_id: str) -> MutationTicket:
        """Take exclusive ownership of the shared tree, or refuse.

        Re-acquiring as the current holder renews rather than conflicts: a
        retry after a crash is the same writer returning, not a competitor.
        """
        return self._acquire_unlocked(child_id)

    def _acquire_unlocked(self, child_id: str) -> MutationTicket:
        """`acquire` without the lifecycle lock, for already-serialized callers.

        `flock` is taken per open description, so a serialized method calling
        another serialized method would deadlock against itself. Recovery needs
        the fence *and* the lifecycle lock, so the fence body lives here and
        both entry points wrap it exactly once.
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

    @_serialized
    def release(self, ticket: MutationTicket) -> None:
        """Give the tree back -- but only if this ticket still holds it.

        A late release from a writer whose lease was already reclaimed must not
        free the *new* owner's lease. The token counter is preserved so it
        never goes backwards.
        """
        self._release_unlocked(ticket)

    def _release_unlocked(self, ticket: MutationTicket) -> None:
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

    @_serialized
    def retain_candidate(self, child_id: str) -> str:
        """Freeze the child's view into a durable, base-bound candidate.

        Called before the shared tree is touched, so an accepted child's work
        can never be lost to a crash that happens during publication.

        The identity covers the **base** as well as the content. A candidate is
        a claim about what the tree becomes when this work is applied to the
        state it was computed against; two identical file sets computed against
        different bases are different claims, and giving them one digest would
        let a retry launder a stale candidate onto a tree that had moved.
        """
        base = self._bind_base(child_id)
        entries = dict(self.workspace_for(child_id).entries())
        digest = digest_of({
            "childId": child_id, "base": base["digest"], "entries": entries})
        path = self._child_dir(child_id) / _CANDIDATE
        if path.exists():
            retained = self._candidate(child_id)
            if retained["digest"] != digest:
                raise StaleWriterError("retained candidate is immutable")
            return digest
        _atomic_write(path, json.dumps(
            {"digest": digest, "base": base["digest"], "entries": entries},
            sort_keys=True))
        return digest

    def _candidate(self, child_id: str) -> dict[str, Any]:
        record = _read_json(self._child_dir(child_id) / _CANDIDATE)
        if not isinstance(record, dict) or not isinstance(record.get("entries"), dict):
            raise StaleWriterError("retained candidate is missing or corrupt")
        entries = record["entries"]
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in entries.items()):
            raise StaleWriterError("retained candidate entries are malformed")
        base = str(record.get("base") or "")
        if record.get("digest") != digest_of(
            {"childId": child_id, "base": base, "entries": entries}
        ):
            raise StaleWriterError("retained candidate content does not match identity")
        return record

    def candidate_digest(self, child_id: str) -> str | None:
        if not (self._child_dir(child_id) / _CANDIDATE).exists():
            return None
        return str(self._candidate(child_id)["digest"])

    def settled_digest(self, child_id: str) -> str | None:
        """Which candidate has been published, if any. The acceptance marker."""
        record = _read_json(self._child_dir(child_id) / _INTEGRATED)
        return str(record["digest"]) if record and record.get("digest") else None

    def published_tree_digest(self, child_id: str) -> str | None:
        """The identity of the tree that was actually written, if any.

        Distinct from `settled_digest`: the candidate says what the child
        produced, this says what the shared tree was made to become. A reader
        checking `DIR-C7` wants the second, because that is the thing an
        exterior evaluator was asked about.
        """
        record = _read_json(self._child_dir(child_id) / _INTEGRATED)
        if not record:
            return None
        return str(record.get("treeDigest") or "") or None

    # -- publication -------------------------------------------------------

    @_serialized
    def stage(self, ticket: MutationTicket, *, candidate_digest: str) -> CombinedTree:
        """Materialise the exact tree publication would write. Nothing lands.

        This is the half `DIR-C7` was missing. Verifying the child's *view* and
        then writing something else into the shared tree verifies the wrong
        object: the view is not the tree the parent ends up with. The combined
        tree -- the bound base overlaid with the candidate -- is that object,
        so it is built here, staged on disk, and carried by digest to whoever
        publishes it.

        The fence and the base are both revalidated before anything is built,
        so a staged tree is never computed from a base that already moved.
        """
        self._validate(ticket)
        child_id = ticket.child_id

        # A replay after a crash during handoff cannot know whether the first
        # attempt landed, and must not be answered by *recomputing* a combined
        # tree: the shared tree has moved -- it moved because the publication
        # succeeded -- so a recomputation would read as a stale base and turn a
        # settled effect into a refusal. The authorized tree is the answer, and
        # `publish` recognises it as already settled.
        authorized = self._authorization(child_id)
        if authorized is not None:
            if str(authorized["candidateDigest"]) != candidate_digest:
                raise StaleWriterError(
                    f"{child_id}: an authorized publication already names "
                    f"{authorized['candidateDigest']}, not {candidate_digest}")
            return CombinedTree(
                child_id=child_id,
                digest=str(authorized["treeDigest"]),
                base_digest=str(authorized["baseDigest"]),
                candidate_digest=str(authorized["candidateDigest"]),
                root=self._child_dir(child_id) / _STAGED,
                entries=dict(authorized["entries"]),
            )

        record = self._candidate(child_id)
        if record.get("digest") != candidate_digest:
            raise StaleWriterError(
                f"{child_id}: no retained candidate {candidate_digest}")
        base = self._require_current_base(child_id, record)

        entries = dict(base["entries"])
        entries.update(record["entries"])
        for relpath in entries:
            # Refuse before staging, not after: a candidate that could name
            # the control directory could forge its own acceptance, and a
            # staged tree containing it would already have been verified.
            self._shared_target(relpath)

        staged_root = self._child_dir(child_id) / _STAGED
        shutil.rmtree(staged_root, ignore_errors=True)
        staged = ChildWorkspace(child_id, staged_root)
        for relpath, text in sorted(entries.items()):
            staged.write(relpath, text)

        return CombinedTree(
            child_id=child_id,
            digest=digest_of({"entries": entries}),
            base_digest=str(base["digest"]),
            candidate_digest=candidate_digest,
            root=staged_root,
            entries=entries,
        )

    @_serialized
    def publish(
        self,
        ticket: MutationTicket,
        combined: CombinedTree,
        *,
        verdict: PublicationVerdict,
    ) -> str:
        """Write the verified combined tree into the shared tree, once.

        Returns `"published"` or `"already_published"`. The second is not a
        failure: a retry after a crash during handoff cannot know whether the
        first attempt landed, and must not settle the same effect twice.

        Every authority is rechecked *here*, at the only moment that matters --
        the instant before the shared tree changes:

        * the **fence**, so a writer that slept through a takeover fails closed;
        * the **base**, so a candidate computed against a tree that has since
          moved is refused instead of overwriting the mover's work;
        * the **candidate**, re-read and re-digested from disk;
        * the **staged tree**, re-digested from the staging directory, so the
          bytes an evaluator saw are the bytes that land;
        * the **exterior verdict**, which must name *this* tree and must have
          passed. Retention, completion and a held lease authorize nothing by
          themselves.
        """
        self._validate(ticket)
        child_id = ticket.child_id
        if child_id != combined.child_id:
            raise StaleWriterError(
                f"{child_id}: ticket does not hold the staged tree "
                f"for {combined.child_id}")
        if self.published_tree_digest(child_id) == combined.digest:
            return "already_published"

        # An authorization that was written and never marked is a decision this
        # process already made and a crash interrupted. Finishing it is the
        # same act `recover()` performs, not a second decision, so it is
        # completed here rather than refused for a base the publication itself
        # moved.
        authorized = self._authorization(child_id)
        if authorized is not None and str(authorized["treeDigest"]) == combined.digest:
            self._apply_authorized(child_id)
            return "published"

        if not verdict.passed():
            raise UnverifiedPublicationError(
                f"{child_id}: exterior verdict is {verdict.disposition!r}; "
                "publication requires a pass")
        if verdict.subject_digest != combined.digest:
            raise UnverifiedPublicationError(
                f"{child_id}: verdict names {verdict.subject_digest} but the "
                f"tree to publish is {combined.digest}")

        record = self._candidate(child_id)
        if record.get("digest") != combined.candidate_digest:
            raise StaleWriterError(
                f"{child_id}: retained candidate is not {combined.candidate_digest}")
        base = self._require_current_base(child_id, record)
        if base["digest"] != combined.base_digest:
            raise StaleBaseError(
                f"{child_id}: staged against base {combined.base_digest}, "
                f"bound base is {base['digest']}")

        entries = self._staged_entries(child_id)
        if digest_of({"entries": entries}) != combined.digest:
            raise UnverifiedPublicationError(
                f"{child_id}: staged tree no longer matches the verified "
                f"{combined.digest}")

        # The authorization is durable *before* the first byte lands. This is
        # what makes recovery safe to run without re-deriving authority it
        # cannot re-derive after a crash: recovery finishes authorized
        # publications and refuses to invent one.
        _atomic_write(self._child_dir(child_id) / _AUTHORIZED, json.dumps({
            "treeDigest": combined.digest,
            "candidateDigest": combined.candidate_digest,
            "baseDigest": combined.base_digest,
            "fenceToken": ticket.token,
            "verdict": {
                "subjectDigest": verdict.subject_digest,
                "disposition": verdict.disposition,
                "envelopeDigest": verdict.envelope_digest,
            },
            "entries": entries,
        }, sort_keys=True))
        self._apply_authorized(child_id)
        return "published"

    def _require_current_base(
        self, child_id: str, record: Mapping[str, Any]
    ) -> dict[str, Any]:
        """The child's bound base, proven to still be the shared tree's state."""
        base = _read_json(self._child_dir(child_id) / _BASE)
        if not isinstance(base, dict) or not isinstance(base.get("entries"), dict):
            raise StaleBaseError(f"{child_id}: base binding is missing or corrupt")
        if str(record.get("base") or "") != str(base.get("digest") or ""):
            raise StaleBaseError(
                f"{child_id}: retained candidate is bound to a different base")
        current = self.shared_digest()
        if current != base["digest"]:
            raise StaleBaseError(
                f"{child_id}: shared tree is {current}, candidate was computed "
                f"against {base['digest']}")
        return base

    def _staged_entries(self, child_id: str) -> dict[str, str]:
        staged_root = self._child_dir(child_id) / _STAGED
        if not staged_root.is_dir():
            raise UnverifiedPublicationError(
                f"{child_id}: nothing is staged to publish")
        return dict(ChildWorkspace(child_id, staged_root).entries())

    def _authorization(self, child_id: str) -> dict[str, Any] | None:
        """The durable publication authorization, revalidated on read."""
        record = _read_json(self._child_dir(child_id) / _AUTHORIZED)
        if not isinstance(record, dict) or not isinstance(record.get("entries"), dict):
            return None
        entries = record["entries"]
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in entries.items()):
            raise UnverifiedPublicationError(
                f"{child_id}: publication authorization is malformed")
        verdict = record.get("verdict")
        if not isinstance(verdict, Mapping):
            raise UnverifiedPublicationError(
                f"{child_id}: publication authorization carries no verdict")
        tree_digest = str(record.get("treeDigest") or "")
        if tree_digest != digest_of({"entries": entries}):
            raise UnverifiedPublicationError(
                f"{child_id}: authorized content does not match its identity")
        if str(verdict.get("subjectDigest") or "") != tree_digest:
            raise UnverifiedPublicationError(
                f"{child_id}: authorized verdict names a different tree")
        if str(verdict.get("disposition") or "").strip().lower() not in {
            "pass", "passed"
        }:
            raise UnverifiedPublicationError(
                f"{child_id}: authorized verdict did not pass")
        return record

    def _apply_authorized(self, child_id: str) -> None:
        """Land every entry of the authorized tree, then record acceptance.

        Order is the contract: content first, marker last. A crash between them
        leaves a tree that `recover()` completes in full, never a partial
        acceptance and never a settled effect that is settled twice.
        """
        record = self._authorization(child_id)
        if record is None:
            raise UnverifiedPublicationError(
                f"{child_id}: no authorized publication to apply")
        entries: Mapping[str, str] = record["entries"]
        for relpath in sorted(entries):
            _atomic_write(self._shared_target(relpath), entries[relpath])
        _atomic_write(self._child_dir(child_id) / _INTEGRATED, json.dumps({
            "digest": record["candidateDigest"],
            "treeDigest": record["treeDigest"],
            "baseDigest": record["baseDigest"],
            "verdict": record["verdict"],
        }, sort_keys=True))

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
        if EXCLUDED_DIRNAMES.intersection(candidate.parts):
            # Excluded from the base *and* forbidden as a target, and the two
            # must go together. Excluding `.git` from the base while still
            # allowing a candidate to write into it would hand a child the one
            # directory nothing compares -- and `core.hooksPath` in a published
            # `.git/config` is code execution on the parent's next git command.
            raise WorkspaceEscapeError(
                f"candidate entry {relpath!r} would rewrite repository metadata")
        return target

    # -- recovery ----------------------------------------------------------

    @_serialized
    def recover(self) -> tuple[str, ...]:
        """Finish every **authorized** publication that has not been marked.

        This is what makes acceptance all-or-nothing without a transaction: a
        publication whose marker is missing is re-applied *in full*, so a tree
        left half-written by a crash converges rather than staying partial. One
        whose marker already matches is left alone, which is what stops
        recovery from settling an effect a second time.

        What recovery deliberately cannot do is *start* one. A merely retained
        candidate -- no exterior verdict, no base revalidation, no authority
        recheck -- is skipped, because recovery runs after a crash and cannot
        re-derive the authority the crash interrupted. Recovery finishes
        decisions; it never makes them.

        Exclusion here is the lifecycle lock, not a fresh lease. Recovery runs
        precisely when the authorizing owner is *dead* with its lease still
        held, so demanding the fence would make recovery impossible in the only
        case it exists for -- and taking the fence by force would hand a
        recovering restart a live owner's tree. The lock already serialises
        recovery against every publisher in every process, and the authority
        being replayed was validated against the fence at the moment it was
        written, so nothing here mutates the tree on weaker authority than the
        publication it is finishing.
        """
        recovered: list[str] = []
        for child_dir in sorted(self.control_dir.iterdir()):
            if not child_dir.is_dir():
                continue
            child_id = child_dir.name
            record = self._authorization(child_id)
            if record is None:
                continue
            if self.published_tree_digest(child_id) == record["treeDigest"]:
                continue
            self._apply_authorized(child_id)
            recovered.append(child_id)
        return tuple(recovered)

    @_serialized
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

"""What one run actually captured, for the `mhf.trajectory/2` writer (EVO-06).

Extracted from `HarnessSession._capture_evidence`: a pure function of the
artifact writer and provenance sink a session already holds, with no other
session state involved. Kept duck-typed (`Any`) rather than importing
`ArtifactWriter`/`RuntimeProvenanceSink` concretely -- `provenance.py`
already imports from `artifacts.py`, and a concrete import here in the
other direction would cycle.

T-131.6 adds product-route identity qualification over the *existing*
candidate snapshot and DIR-D1 carriers. It does not hash a second tree,
write a ledger, or own a loop.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = [
    "capture_evidence",
    "last_kind_payload",
    "qualify_candidate_identity",
    "submitted_workspace_digests",
    "verification_subject_digest",
]


def capture_evidence(artifacts: Any, provenance: Any) -> dict[str, Any]:
    """Empty on the legacy path, and deliberately so.

    `assemble_trajectory` renders an absent artifact index and a null
    capture status rather than synthesising a complete one, so a run that
    captured nothing says that instead of claiming it captured everything
    it was asked to.
    """
    if artifacts is None:
        return {}
    trajectory_provenance = provenance.trajectory_provenance()
    return {
        "artifact_index": list(artifacts.index_entries()),
        "context_provenance": trajectory_provenance["context"],
        "compaction_provenance": trajectory_provenance["compaction"],
        "cache_provenance": trajectory_provenance["cache"],
        "capture_status": artifacts.capture_state(),
    }


def submitted_workspace_digests(workspace: Path | str) -> tuple[str, ...]:
    """Existing product snapshot identities of the submitted tree.

    Reuses the environment adapters the product already uses for candidate
    identity (`SandboxedEnvironmentAdapter.snapshot`, and the host git
    snapshot when that adapter can bind). A third tree hash is not minted.
    """
    root = Path(workspace)
    digests: list[str] = []
    from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter

    snapshot = SandboxedEnvironmentAdapter(
        worker=None, workspace=root, environment_id="product-candidate",
    ).snapshot()
    if snapshot.ok and snapshot.value is not None:
        digest = str(getattr(snapshot.value, "digest", "") or "")
        if digest.startswith("sha256:"):
            digests.append(digest)
    try:
        from ..adapters.environment.git import GitEnvironmentAdapter

        git_snapshot = GitEnvironmentAdapter(
            root, environment_id="product-candidate-git").snapshot()
    except Exception:
        git_snapshot = None
    if git_snapshot is not None and git_snapshot.ok and git_snapshot.value is not None:
        digest = str(getattr(git_snapshot.value, "digest", "") or "")
        if digest.startswith("sha256:") and digest not in digests:
            digests.append(digest)
    return tuple(digests)


def last_kind_payload(events: Sequence[Any], kind: str) -> dict[str, Any] | None:
    """The last durable payload of `kind`, or None when the carrier is absent."""
    found: dict[str, Any] | None = None
    for event in events or ():
        if getattr(event, "kind", "") != kind:
            continue
        payload = getattr(event, "payload", None)
        if isinstance(payload, Mapping):
            found = dict(payload)
    return found


def verification_subject_digest(
    argv: Sequence[Any], workspace_digest: str, task_digest: str,
) -> str:
    """The T-07 subject preimage already used by `VerificationSubject.digest`."""
    return digest_of({
        "argv": list(argv),
        "workspaceDigest": workspace_digest,
        "taskDigest": task_digest,
    })


def _field(payload: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = payload.get(name)
        if isinstance(value, str) and value:
            return value
    return ""


def qualify_candidate_identity(
    *,
    submitted_digests: Sequence[str],
    task_digest: str | None,
    composition_digest: str | None,
    verification: Mapping[str, Any] | None,
    change_surface: Mapping[str, Any] | None = None,
    captured_artifacts: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """Whether every identity carrier names the exact submitted tree.

    A missing verification is not a green claim: qualification is not
    applicable and the caller must not invent a pass. A present passing
    verification that names any other tree, task, composition, oracle
    subject, extra/deleted file, or stale artifact is not qualified.
    """
    submitted = tuple(
        digest for digest in submitted_digests
        if isinstance(digest, str) and digest.startswith("sha256:")
    )
    candidate = submitted[0] if submitted else ""
    if verification is None:
        return {
            "qualified": True,
            "applicable": False,
            "reason": None,
            "candidateDigest": candidate or None,
            "identity": None,
        }

    workspace = _field(verification, "workspaceDigest", "workspace_digest")
    task = _field(verification, "taskDigest", "task_digest")
    composition = _field(verification, "compositionDigest", "composition_digest")
    subject = _field(verification, "verificationSubjectDigest", "verification_subject_digest")
    argv = verification.get("argv") or ()
    identity = {
        "workspaceDigest": workspace,
        "taskDigest": task,
        "compositionDigest": composition,
        "verificationSubjectDigest": subject,
    }

    def refused(reason: str) -> dict[str, Any]:
        return {
            "qualified": False,
            "applicable": True,
            "reason": reason,
            "candidateDigest": candidate or None,
            "identity": identity,
        }

    if not workspace.startswith("sha256:"):
        return refused("VERIFICATION_UNBOUND")
    if workspace not in submitted:
        return refused("VERIFICATION_STALE")
    if task_digest and task and task != task_digest:
        return refused("TASK_IDENTITY_MISMATCH")
    if composition_digest and composition and composition != composition_digest:
        return refused("COMPOSITION_IDENTITY_MISMATCH")
    if change_surface is not None:
        surface_tree = _field(change_surface, "candidateDigest", "candidate_digest")
        if surface_tree and surface_tree != workspace:
            return refused("VERIFICATION_STALE")
        surface_task = _field(change_surface, "taskDigest", "task_digest")
        if surface_task and task and surface_task != task:
            return refused("TASK_IDENTITY_MISMATCH")
    if isinstance(argv, (list, tuple)) and task:
        expected = verification_subject_digest(argv, workspace, task)
        if subject and subject != expected:
            return refused("VERIFICATION_SUBJECT_STALE")
        identity["verificationSubjectDigest"] = subject or expected
    for item in captured_artifacts or ():
        if not isinstance(item, Mapping):
            continue
        bound = _field(item, "workspaceDigest", "candidateDigest", "workspace_digest", "candidate_digest")
        if bound.startswith("sha256:") and bound not in submitted:
            return refused("STALE_ARTIFACT")
    return {
        "qualified": True,
        "applicable": True,
        "reason": None,
        "candidateDigest": workspace,
        "identity": identity,
    }

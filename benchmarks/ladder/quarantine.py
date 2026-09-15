"""Q-01 corpus quarantine: DEV and HOLDOUT are separate authorization domains.

Public commitments carry opaque identity, fingerprints, roles and attestations
only. Replacement task or solution plaintext does not belong here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "aether.corpus-quarantine/1"
ROLE_DEV = "DEV"
ROLE_HOLDOUT = "HOLDOUT"
ROLE_EXPOSED = "EXPOSED"
ROLES = frozenset({ROLE_DEV, ROLE_HOLDOUT, ROLE_EXPOSED})
HOLD_OUT_UNACCEPTED = "UNACCEPTED"
SCOPE_REGISTERED = "registered_corpus"
SCOPE_ORDINARY_USER = "ordinary_user"
SCOPES = frozenset({SCOPE_REGISTERED, SCOPE_ORDINARY_USER})
ORACLE_MOUNT_NAMES = frozenset({
    "oracle",
    "reference",
    "gold",
    "private",
    "test_oracle.py",
    "reference.py",
    "gold.py",
    "solution.py",
})
DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parent / "corpus_registry.json"
_DIGEST_PREFIX = "sha256:"
PLAINTEXT_KEYS = frozenset({
    "brief",
    "prompt",
    "problem",
    "solution",
    "oracle_text",
    "patch",
    "source_text",
    "task_text",
    "content",
    "body",
})
EXPECTED_HOLDOUT_STRATA = {
    "brownfield": 10,
    "greenfield": 11,
    "multi_file": 5,
    "multi_turn": 1,
    "single_file": 3,
}

__all__ = [
    "EXPECTED_HOLDOUT_STRATA",
    "PLAINTEXT_KEYS",
    "QuarantineError",
    "SCHEMA",
    "SealedStore",
    "SCOPE_ORDINARY_USER",
    "SCOPE_REGISTERED",
    "admit_development",
    "admit_evaluation",
    "bound_evaluation_authority",
    "digest_canonical",
    "evaluation_frozen_manifest",
    "fingerprint_bytes",
    "fingerprint_tree",
    "guard_capture",
    "guard_export",
    "guard_loader",
    "guard_materialization",
    "guard_product_execution",
    "load_registry",
    "lookup_member",
    "materialize",
    "promote_to_holdout",
    "refuse_unfrozen_scoring",
    "validate_registry_document",
]


class QuarantineError(ValueError):
    """Fail-closed corpus authorization error."""


@dataclass(frozen=True)
class SealedStore:
    """Hermetic directory that may hold synthetic evaluation material."""

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", Path(self.root))
        self.root.mkdir(parents=True, exist_ok=True)

    def member_path(self, member_id: str) -> Path:
        return self.root / member_id

    def write_member(self, member_id: str, files: Mapping[str, bytes]) -> Path:
        dest = self.member_path(member_id)
        dest.mkdir(parents=True, exist_ok=True)
        for relative, data in files.items():
            path = dest / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return dest


def digest_canonical(obj: object) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _DIGEST_PREFIX + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fingerprint_bytes(data: bytes) -> str:
    return _DIGEST_PREFIX + hashlib.sha256(data).hexdigest()


def fingerprint_tree(root: Path) -> str:
    base = Path(root)
    digest = hashlib.sha256()
    for path in sorted(item for item in base.rglob("*") if item.is_file()):
        if path.is_symlink():
            continue
        relative = path.relative_to(base).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return _DIGEST_PREFIX + digest.hexdigest()


def load_registry(path: Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    if not target.is_file():
        raise QuarantineError("missing corpus registry")
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise QuarantineError("corpus registry must be an object")
    return data


def lookup_member(registry: Mapping[str, Any], identity: str) -> dict[str, Any] | None:
    for member in registry.get("members") or []:
        if not isinstance(member, dict):
            continue
        if member.get("id") == identity:
            return member
        aliases = member.get("aliases") or []
        if identity in aliases:
            return member
    return None


def bound_evaluation_authority(member: Mapping[str, Any], *, run_id: str) -> str:
    return digest_canonical({
        "kind": "evaluation-authority",
        "run_id": run_id,
        "id": member.get("id"),
        "role": member.get("role"),
        "source_fingerprint": member.get("source_fingerprint"),
        "oracle_fingerprint": member.get("oracle_fingerprint"),
        "task_fingerprint": member.get("task_fingerprint"),
        "attestation": member.get("attestation"),
    })


def evaluation_frozen_manifest(member: Mapping[str, Any], *, run_id: str) -> dict[str, Any]:
    return {
        "status": "FROZEN",
        "run_id": run_id,
        "id": member.get("id"),
        "role": member.get("role"),
        "source_fingerprint": member.get("source_fingerprint"),
        "oracle_fingerprint": member.get("oracle_fingerprint"),
        "task_fingerprint": member.get("task_fingerprint"),
        "attestation": member.get("attestation"),
    }


def _require_scope(scope: str | None) -> str:
    if scope is None:
        return SCOPE_REGISTERED
    if scope not in SCOPES:
        raise QuarantineError("unknown corpus scope")
    return scope


def _identity_kind(registry: Mapping[str, Any], identity: str) -> str:
    for member in registry.get("members") or []:
        if not isinstance(member, dict):
            continue
        if member.get("id") == identity:
            return "canonical"
        aliases = member.get("aliases") or []
        if identity in aliases:
            return "renamed"
    return "unknown"


def member_tokens(member: Mapping[str, Any]) -> set[str]:
    tokens = {
        str(member.get("id") or ""),
        str(member.get("origin") or ""),
        str(member.get("source_fingerprint") or ""),
        str(member.get("oracle_fingerprint") or ""),
        str(member.get("task_fingerprint") or ""),
    }
    for alias in member.get("aliases") or []:
        tokens.add(str(alias))
    return {token for token in tokens if token}


def _plaintext_errors(node: object, trail: str) -> list[str]:
    errors: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            location = f"{trail}.{key}" if trail else key
            if key in PLAINTEXT_KEYS:
                errors.append(f"plaintext field {location}")
            errors.extend(_plaintext_errors(value, location))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            errors.extend(_plaintext_errors(item, f"{trail}[{index}]"))
    return errors


def validate_registry_document(registry: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema") != SCHEMA:
        errors.append("invalid corpus quarantine schema")
    members = registry.get("members")
    if not isinstance(members, list):
        return errors + ["members must be a list"]
    errors.extend(_plaintext_errors(registry, ""))

    seen_ids: set[str] = set()
    d_star: set[str] = set()
    holdout: set[str] = set()
    exposed_ids: set[str] = set()
    for index, member in enumerate(members):
        prefix = f"members[{index}]"
        if not isinstance(member, dict):
            errors.append(f"{prefix} must be an object")
            continue
        member_id = member.get("id")
        if not isinstance(member_id, str) or not member_id.strip():
            errors.append(f"{prefix} missing identity")
            continue
        if member_id in seen_ids:
            errors.append(f"duplicate identity {member_id}")
        seen_ids.add(member_id)
        role = member.get("role")
        if role not in ROLES:
            errors.append(f"{member_id} missing or invalid role")
            continue
        attestation = member.get("attestation")
        if not isinstance(attestation, str) or not attestation.startswith(_DIGEST_PREFIX):
            errors.append(f"{member_id} missing attestation receipt")
        tombstone = member.get("exposure_tombstone")
        if role == ROLE_EXPOSED:
            exposed_ids.add(member_id)
            if not isinstance(tombstone, str) or not tombstone.startswith(_DIGEST_PREFIX):
                errors.append(f"{member_id} removed exposure tombstone")
        if role == ROLE_HOLDOUT and isinstance(tombstone, str) and tombstone:
            errors.append(f"{member_id} role spoofing: EXPOSED tombstone cannot be HOLDOUT")
        tokens = member_tokens(member)
        if role == ROLE_HOLDOUT:
            holdout |= tokens
        else:
            d_star |= tokens

    overlap = sorted(d_star & holdout)
    if overlap:
        sample = overlap[0]
        kind = "alias" if not sample.startswith(_DIGEST_PREFIX) else "fingerprint"
        if sample.startswith(_DIGEST_PREFIX):
            errors.append(f"closure overlap on copied {kind} {sample[:18]}")
        else:
            errors.append(f"closure overlap on alias or origin {sample}")

    declared = registry.get("irreversible_exposed_ids")
    if isinstance(declared, list):
        missing = [item for item in declared if item not in exposed_ids]
        if missing:
            errors.append(f"removed exposure tombstone for {missing[0]}")
    return errors


def _require_member(registry: Mapping[str, Any], identity: str) -> dict[str, Any]:
    if not identity:
        raise QuarantineError("missing identity")
    member = lookup_member(registry, identity)
    if member is None:
        raise QuarantineError("unknown identity")
    if member.get("role") not in ROLES:
        raise QuarantineError("missing role")
    if not isinstance(member.get("attestation"), str) or not str(member.get("attestation")).startswith(_DIGEST_PREFIX):
        raise QuarantineError("missing attestation receipt")
    return member


def _commitments_match(member: Mapping[str, Any], claimed: Mapping[str, Any]) -> bool:
    for key in ("id", "role", "source_fingerprint", "oracle_fingerprint", "task_fingerprint", "attestation"):
        if claimed.get(key) != member.get(key):
            return False
    return True


def _iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    files: list[Path] = []
    for item in path.rglob("*"):
        if item.is_symlink() or not item.is_file():
            continue
        files.append(item)
    return files


def _refuse_solver_mounted_oracle(path: Path, member: Mapping[str, Any]) -> None:
    oracle_fp = member.get("oracle_fingerprint")
    for item in _iter_files(path):
        digest = fingerprint_bytes(item.read_bytes())
        if oracle_fp and digest == oracle_fp:
            raise QuarantineError("solver-mounted oracle")
        name = item.name.lower()
        rel = item.relative_to(path).as_posix().lower() if path.is_dir() and item != path else name
        parts = set(rel.split("/"))
        if name in ORACLE_MOUNT_NAMES or parts & {n for n in ORACLE_MOUNT_NAMES if "/" not in n}:
            raise QuarantineError("solver-mounted reference")


def _check_source_bytes(source: Path, member: Mapping[str, Any], *, purpose: str) -> None:
    if not source.exists():
        raise QuarantineError("missing source")
    if purpose != "evaluation":
        _refuse_solver_mounted_oracle(source, member)
    if source.is_file():
        digest = fingerprint_bytes(source.read_bytes())
        if digest == member.get("oracle_fingerprint"):
            raise QuarantineError("solver-mounted oracle")
        if digest != member.get("source_fingerprint"):
            raise QuarantineError("copied content")
        return
    if fingerprint_tree(source) != member.get("source_fingerprint"):
        for item in _iter_files(source):
            digest = fingerprint_bytes(item.read_bytes())
            if digest == member.get("oracle_fingerprint"):
                raise QuarantineError("solver-mounted oracle")
        raise QuarantineError("copied content")


def _assert_evaluation_authority(
    member: Mapping[str, Any],
    *,
    authority: str | None,
    frozen_manifest: Mapping[str, Any] | None,
) -> None:
    if not authority or not isinstance(authority, str):
        raise QuarantineError("absent evaluation receipt")
    if not isinstance(frozen_manifest, Mapping):
        raise QuarantineError("unfrozen scoring")
    if frozen_manifest.get("status") != "FROZEN":
        raise QuarantineError("unfrozen scoring")
    if not _commitments_match(member, frozen_manifest):
        if frozen_manifest.get("id") != member.get("id") or frozen_manifest.get("role") != member.get("role"):
            raise QuarantineError("forged FROZEN")
        raise QuarantineError("altered commitments")
    run_id = frozen_manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise QuarantineError("forged FROZEN")
    expected = bound_evaluation_authority(member, run_id=run_id)
    if authority != expected:
        raise QuarantineError("forged authority")


def admit_development(
    identity: str,
    *,
    source: Path | None = None,
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    member = _require_member(registry, identity)
    if member["role"] == ROLE_HOLDOUT:
        raise QuarantineError("HOLDOUT cannot be admitted as development")
    if member["role"] not in {ROLE_DEV, ROLE_EXPOSED}:
        raise QuarantineError("missing role")
    if source is not None:
        _check_source_bytes(Path(source), member, purpose="development")
        if Path(source).is_dir() and fingerprint_tree(Path(source)) != member["source_fingerprint"]:
            raise QuarantineError("copied content")
    return dict(member)


def admit_evaluation(
    identity: str,
    *,
    registry: Mapping[str, Any],
    authority: str | None,
    frozen_manifest: Mapping[str, Any] | None,
    store: SealedStore,
) -> dict[str, Any]:
    member = _require_member(registry, identity)
    _assert_evaluation_authority(member, authority=authority, frozen_manifest=frozen_manifest)
    if member["role"] != ROLE_HOLDOUT:
        raise QuarantineError("evaluation requires HOLDOUT identity")
    source = store.member_path(member["id"])
    if not source.is_dir():
        raise QuarantineError("missing sealed evaluation material")
    return dict(member)


def _assert_no_symlink_escape(source: Path, authorized_root: Path) -> None:
    authorized = authorized_root.resolve()
    resolved_source = source.resolve()
    if authorized != resolved_source and authorized not in resolved_source.parents:
        raise QuarantineError("symlink escape")
    for path in source.rglob("*"):
        if path.is_symlink():
            target = path.resolve()
            if authorized != target and authorized not in target.parents:
                raise QuarantineError("symlink escape")


def _copy_tree_without_symlinks(
    source: Path,
    destination: Path,
    *,
    member: Mapping[str, Any] | None = None,
    purpose: str = "development",
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if path.is_symlink():
            raise QuarantineError("symlink escape")
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            if path.name.lower() in ORACLE_MOUNT_NAMES and purpose != "evaluation":
                raise QuarantineError("solver-mounted reference")
            target.mkdir(parents=True, exist_ok=True)
            continue
        payload = path.read_bytes()
        if member is not None and purpose != "evaluation":
            if fingerprint_bytes(payload) == member.get("oracle_fingerprint"):
                raise QuarantineError("solver-mounted oracle")
            if path.name.lower() in ORACLE_MOUNT_NAMES:
                raise QuarantineError("solver-mounted reference")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)


def materialize(
    *,
    identity: str,
    destination: Path,
    registry: Mapping[str, Any],
    purpose: str,
    store: SealedStore | None = None,
    authority: str | None = None,
    frozen_manifest: Mapping[str, Any] | None = None,
) -> Path:
    member = _require_member(registry, identity)
    dest = Path(destination)
    if purpose == "evaluation":
        if store is None:
            raise QuarantineError("evaluation requires a sealed store")
        admit_evaluation(
            identity,
            registry=registry,
            authority=authority,
            frozen_manifest=frozen_manifest,
            store=store,
        )
        source = store.member_path(member["id"])
        _assert_no_symlink_escape(source, store.root)
        _copy_tree_without_symlinks(source, dest, member=member, purpose="evaluation")
        return dest
    if member["role"] == ROLE_HOLDOUT:
        raise QuarantineError("DEV capture of HOLDOUT is forbidden")
    if store is None:
        raise QuarantineError("missing store for development materialization")
    source = store.member_path(member["id"])
    if not source.is_dir():
        raise QuarantineError("missing development material")
    _assert_no_symlink_escape(source, store.root)
    _copy_tree_without_symlinks(source, dest, member=member, purpose="development")
    _refuse_solver_mounted_oracle(dest, member)
    return dest


def guard_materialization(
    *,
    task_id: str | None,
    source: Path | str | None = None,
    purpose: str = "development",
    registry: Mapping[str, Any] | None = None,
    scope: str | None = None,
) -> None:
    resolved_scope = _require_scope(scope)
    if resolved_scope == SCOPE_ORDINARY_USER:
        if task_id:
            active = registry if registry is not None else load_registry()
            if lookup_member(active, str(task_id)) is not None:
                raise QuarantineError("registered corpus identity cannot use ordinary-user scope")
        return
    if not task_id:
        raise QuarantineError("missing identity")
    active = registry if registry is not None else load_registry()
    kind = _identity_kind(active, str(task_id))
    if kind == "unknown":
        raise QuarantineError("unknown identity")
    if kind == "renamed":
        raise QuarantineError("renamed identity")
    member = lookup_member(active, str(task_id))
    if member is None:
        raise QuarantineError("unknown identity")
    if member.get("role") not in ROLES:
        raise QuarantineError("forged role")
    if purpose == "evaluation" and member.get("role") != ROLE_HOLDOUT:
        raise QuarantineError("evaluation requires HOLDOUT identity")
    if purpose != "evaluation" and member.get("role") == ROLE_HOLDOUT:
        raise QuarantineError("DEV capture of HOLDOUT is forbidden")
    if source is not None:
        source_path = Path(source)
        if source_path.exists():
            _check_source_bytes(source_path, member, purpose=purpose)


def guard_capture(
    *,
    task_id: str | None,
    registry: Mapping[str, Any] | None = None,
    scope: str | None = None,
) -> None:
    resolved_scope = _require_scope(scope)
    if resolved_scope == SCOPE_ORDINARY_USER:
        if task_id:
            active = registry if registry is not None else load_registry()
            if lookup_member(active, str(task_id)) is not None:
                raise QuarantineError("registered corpus identity cannot use ordinary-user scope")
        return
    if not task_id:
        raise QuarantineError("missing identity")
    active = registry if registry is not None else load_registry()
    kind = _identity_kind(active, str(task_id))
    if kind == "unknown":
        raise QuarantineError("unknown identity")
    if kind == "renamed":
        raise QuarantineError("renamed identity")
    member = lookup_member(active, str(task_id))
    if member is None:
        raise QuarantineError("unknown identity")
    if member.get("role") == ROLE_HOLDOUT:
        raise QuarantineError("HOLDOUT capture is forbidden")


def guard_export(
    *,
    task_id: str | None,
    registry: Mapping[str, Any] | None = None,
    scope: str | None = None,
) -> None:
    guard_capture(task_id=task_id, registry=registry, scope=scope)


def guard_loader(
    *,
    task_id: str | None,
    source: Path | str | None = None,
    purpose: str = "development",
    registry: Mapping[str, Any] | None = None,
    capture: bool = False,
    scope: str | None = None,
) -> None:
    """Fail-closed loader helper. Unregistered IDs are ordinary work only when named.

    Unknown, renamed, or omitted identities refuse unless the caller passes an
    explicit ordinary-user scope. This helper never treats an omitted ID as
    ordinary work and never converts an alias into a canonical bypass.
    """
    if not task_id:
        raise QuarantineError("missing identity")
    active = registry if registry is not None else load_registry()
    resolved_scope = _require_scope(scope)
    kind = _identity_kind(active, str(task_id))
    if kind == "renamed":
        raise QuarantineError("renamed identity")
    if kind == "unknown":
        if resolved_scope == SCOPE_ORDINARY_USER:
            return
        if capture:
            guard_capture(task_id=str(task_id), registry=active)
        else:
            guard_materialization(
                task_id=str(task_id),
                source=source,
                purpose=purpose,
                registry=active,
            )
        return
    if resolved_scope == SCOPE_ORDINARY_USER:
        raise QuarantineError("registered corpus identity cannot use ordinary-user scope")
    if capture:
        guard_capture(task_id=str(task_id), registry=active)
        return
    guard_materialization(
        task_id=str(task_id),
        source=source,
        purpose=purpose,
        registry=active,
    )


def guard_product_execution(
    *,
    workspace: Path | str | None,
    extra: Mapping[str, Any] | None = None,
    registry: Mapping[str, Any] | None = None,
) -> None:
    extra = extra or {}
    task_id = extra.get("task_id") or extra.get("taskId") or extra.get("corpus_id")
    scope = extra.get("corpus_scope") or extra.get("corpusScope")
    if scope is None and not task_id:
        scope = SCOPE_ORDINARY_USER
    guard_materialization(
        task_id=str(task_id) if task_id is not None else None,
        source=workspace,
        purpose="development",
        registry=registry,
        scope=str(scope) if scope is not None else None,
    )


def refuse_unfrozen_scoring(
    task_ids: Sequence[str],
    preregistration: Mapping[str, Any],
    *,
    registry: Mapping[str, Any] | None = None,
) -> None:
    active = registry if registry is not None else load_registry()
    holdout_hits = []
    for task_id in task_ids:
        if not task_id:
            continue
        member = lookup_member(active, task_id)
        if member is not None and member.get("role") == ROLE_HOLDOUT:
            holdout_hits.append(task_id)
    if not holdout_hits:
        return
    frozen = preregistration if isinstance(preregistration, Mapping) else {}
    if frozen.get("status") != "FROZEN":
        raise QuarantineError("unfrozen scoring")
    for task_id in holdout_hits:
        member = lookup_member(active, task_id)
        if member is None:
            continue
        if not _commitments_match(member, frozen) and frozen.get("id") not in {None, member.get("id")}:
            raise QuarantineError("forged FROZEN")
        # A corpus-wide frozen flag is allowed only when it restates commitments
        # or is a scoring gate over already-admitted identities. A bare status
        # without identity is not evaluation authority; materialization still
        # requires bound credentials. Scoring a holdout with only status=FROZEN
        # is refused unless the record names the member or omits identity fields.
        if "id" in frozen and frozen.get("id") != member.get("id"):
            raise QuarantineError("forged FROZEN")


def promote_to_holdout(identity: str, *, registry: Mapping[str, Any]) -> None:
    member = _require_member(registry, identity)
    if member["role"] in {ROLE_DEV, ROLE_EXPOSED}:
        raise QuarantineError("captured development data cannot migrate to HOLDOUT")
    raise QuarantineError("illegal HOLDOUT promotion")

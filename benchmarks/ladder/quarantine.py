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
    "admit_development",
    "admit_evaluation",
    "digest_canonical",
    "fingerprint_bytes",
    "fingerprint_tree",
    "guard_capture",
    "guard_export",
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
    member = lookup_member(registry, identity)
    if member is None:
        raise QuarantineError("missing identity")
    if member.get("role") not in ROLES:
        raise QuarantineError("missing role")
    if not isinstance(member.get("attestation"), str):
        raise QuarantineError("missing attestation receipt")
    return member


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
    if source is not None and fingerprint_tree(source) != member["source_fingerprint"]:
        raise QuarantineError("source fingerprint mismatch")
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
    if not authority:
        raise QuarantineError("absent evaluation receipt")
    if not isinstance(frozen_manifest, Mapping) or frozen_manifest.get("status") != "FROZEN":
        raise QuarantineError("unfrozen scoring")
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


def _copy_tree_without_symlinks(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if path.is_symlink():
            raise QuarantineError("symlink escape")
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())


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
        _copy_tree_without_symlinks(source, dest)
        return dest
    if member["role"] == ROLE_HOLDOUT:
        raise QuarantineError("DEV capture of HOLDOUT is forbidden")
    if store is None:
        raise QuarantineError("missing store for development materialization")
    source = store.member_path(member["id"])
    if not source.is_dir():
        raise QuarantineError("missing development material")
    _assert_no_symlink_escape(source, store.root)
    _copy_tree_without_symlinks(source, dest)
    return dest


def guard_materialization(
    *,
    task_id: str | None,
    source: Path | str | None = None,
    purpose: str = "development",
    registry: Mapping[str, Any] | None = None,
) -> None:
    if not task_id:
        if purpose == "evaluation":
            raise QuarantineError("missing identity")
        return
    active = registry if registry is not None else load_registry()
    member = lookup_member(active, task_id)
    if member is None:
        if purpose == "evaluation":
            raise QuarantineError("missing identity")
        return
    if purpose == "evaluation" and member.get("role") != ROLE_HOLDOUT:
        raise QuarantineError("evaluation requires HOLDOUT identity")
    if purpose != "evaluation" and member.get("role") == ROLE_HOLDOUT:
        raise QuarantineError("DEV capture of HOLDOUT is forbidden")
    if source is not None:
        Path(source)  # identity-only; content is not logged


def guard_capture(*, task_id: str | None, registry: Mapping[str, Any] | None = None) -> None:
    if not task_id:
        return
    active = registry if registry is not None else load_registry()
    member = lookup_member(active, task_id)
    if member is not None and member.get("role") == ROLE_HOLDOUT:
        raise QuarantineError("HOLDOUT capture is forbidden")


def guard_export(*, task_id: str | None, registry: Mapping[str, Any] | None = None) -> None:
    guard_capture(task_id=task_id, registry=registry)


def guard_product_execution(
    *,
    workspace: Path | str | None,
    extra: Mapping[str, Any] | None = None,
    registry: Mapping[str, Any] | None = None,
) -> None:
    extra = extra or {}
    task_id = extra.get("task_id") or extra.get("taskId")
    if task_id is None:
        return
    guard_materialization(
        task_id=str(task_id),
        source=workspace,
        purpose="development",
        registry=registry,
    )


def refuse_unfrozen_scoring(
    task_ids: Sequence[str],
    preregistration: Mapping[str, Any],
    *,
    registry: Mapping[str, Any] | None = None,
) -> None:
    active = registry if registry is not None else load_registry()
    holdout_hits = [
        task_id for task_id in task_ids
        if (member := lookup_member(active, task_id)) is not None
        and member.get("role") == ROLE_HOLDOUT
    ]
    if not holdout_hits:
        return
    if preregistration.get("status") != "FROZEN":
        raise QuarantineError("unfrozen scoring")


def promote_to_holdout(identity: str, *, registry: Mapping[str, Any]) -> None:
    member = _require_member(registry, identity)
    if member["role"] in {ROLE_DEV, ROLE_EXPOSED}:
        raise QuarantineError("captured development data cannot migrate to HOLDOUT")
    raise QuarantineError("illegal HOLDOUT promotion")

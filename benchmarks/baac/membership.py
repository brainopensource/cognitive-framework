"""Schema-valid BAAC challenge discovery (T-41). Distinct from B20 T-01."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import yaml

from benchmarks.baac.schema import ChallengeMetadata
from benchmarks.protocols import is_rejected_b20_name

__all__ = [
    "BAAC_CHALLENGE_SCHEMA",
    "BAACMembershipError",
    "enumerate_baac_challenges",
    "parse_baac_challenge_manifest",
]

BAAC_CHALLENGE_SCHEMA = "aether.baac.challenge/1"


class BAACMembershipError(ValueError):
    """BAAC discovery is invalid; the campaign must stop."""


def parse_baac_challenge_manifest(path: Path) -> ChallengeMetadata:
    """Admit one challenge only from a schema-valid ``challenge.yaml``."""
    try:
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise BAACMembershipError("challenge manifest is not valid YAML") from exc
    if not isinstance(payload, Mapping) or payload.get("schema") != BAAC_CHALLENGE_SCHEMA:
        raise BAACMembershipError(
            f"challenge manifest schema must be {BAAC_CHALLENGE_SCHEMA}"
        )
    task_id = str(payload.get("id") or "").strip()
    if not task_id:
        raise BAACMembershipError("each challenge requires id")
    if is_rejected_b20_name(task_id):
        raise BAACMembershipError(f"rejected challenge id: {task_id}")
    return ChallengeMetadata.from_dict(payload)


def enumerate_baac_challenges(suite_root: Path) -> tuple[Path, ...]:
    """Admit BAAC challenges from schema-valid manifests only.

    Directory names and a bare ``TASK.md`` are never sufficient.
    ``__pycache__``, hidden, and tmp entries are not challenges. A present
    but invalid ``challenge.yaml`` fails closed.
    """
    root = Path(suite_root)
    if not root.is_dir():
        return ()
    admitted: list[Path] = []
    for tier_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if is_rejected_b20_name(tier_dir.name):
            continue
        for challenge_dir in sorted(path for path in tier_dir.iterdir() if path.is_dir()):
            if is_rejected_b20_name(challenge_dir.name):
                continue
            manifest = challenge_dir / "challenge.yaml"
            if not manifest.is_file():
                continue
            parse_baac_challenge_manifest(manifest)
            admitted.append(challenge_dir)
    return tuple(admitted)

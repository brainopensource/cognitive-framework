"""Immutable task/oracle preregistration identity for an RF-85 run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..canonicalisation.digest import digest_of

API = "mhf.preregistration/1"


class PreregistrationError(ValueError):
    """The preregistration is incomplete or internally inconsistent."""


@dataclass(frozen=True, slots=True)
class Preregistration:
    task_digest: str
    oracle_id: str
    oracle_digest: str
    evaluator_key_id: str
    evaluator_public_key: str
    protocol: str
    subject_digest: str
    created_at: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    api: str = API
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        required = (
            self.task_digest, self.oracle_id, self.oracle_digest,
            self.evaluator_key_id, self.evaluator_public_key, self.protocol,
            self.subject_digest, self.created_at,
        )
        if not all(isinstance(value, str) and value.strip() for value in required):
            raise PreregistrationError("all preregistration bindings are required")
        object.__setattr__(self, "metadata", dict(self.metadata))
        object.__setattr__(self, "digest", digest_of(self.identity()))

    def identity(self) -> Mapping[str, Any]:
        return {
            "api": self.api,
            "task_digest": self.task_digest,
            "oracle_id": self.oracle_id,
            "oracle_digest": self.oracle_digest,
            "evaluator_key_id": self.evaluator_key_id,
            "evaluator_public_key": self.evaluator_public_key,
            "protocol": self.protocol,
            "subject_digest": self.subject_digest,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    def to_wire(self) -> Mapping[str, Any]:
        return {**self.identity(), "preregistration_digest": self.digest}

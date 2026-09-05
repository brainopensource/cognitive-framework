"""Cryptographic test-oracle freeze hashed at turn 0 via IndexPort.

INV-DELTA-4: agents MUST NOT mutate enumerated tests during implementation.
Enumeration is `IndexPort.tests()`, never `Path.glob("test/**")` — a glob of
the conventional test tree misses index-known oracles outside that prefix.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ...ports.index import IndexPort

__all__ = ["TamperVerdict", "TestTamperShield"]

_TAMPER = "TAMPER_VIOLATION"
_OK = "test_integrity_verified"
_ENUM_FAILED = "TAMPER_VIOLATION:INDEX_ENUMERATION_FAILED"


@dataclass(frozen=True, slots=True)
class TamperVerdict:
    """Admission-shaped verdict; session maps this without rewriting epoch."""

    admissible: bool
    reason: str


@dataclass(frozen=True, slots=True)
class TestTamperShield:
    """Turn-0 freeze of IndexPort-enumerated test files; evaluate on admit."""

    workspace: Path
    frozen_test_digests: Mapping[str, str]
    enumeration_failed: bool = False

    @classmethod
    def freeze(cls, workspace: Path, index: IndexPort) -> TestTamperShield:
        root = Path(workspace).resolve()
        listed = index.tests()
        if not listed.ok or listed.value is None:
            return cls(workspace=root, frozen_test_digests={}, enumeration_failed=True)
        digests: dict[str, str] = {}
        for association in listed.value:
            rel = str(association.test_path).replace("\\", "/").lstrip("/")
            if not rel or rel in digests:
                continue
            if Path(rel).is_absolute() or ".." in Path(rel).parts:
                return cls(workspace=root, frozen_test_digests={}, enumeration_failed=True)
            candidate = root / rel
            if not candidate.is_file():
                return cls(workspace=root, frozen_test_digests={}, enumeration_failed=True)
            digests[rel] = hashlib.sha256(candidate.read_bytes()).hexdigest()
        return cls(workspace=root, frozen_test_digests=digests)

    def evaluate(self, workspace: Path | None = None) -> TamperVerdict:
        if self.enumeration_failed:
            return TamperVerdict(False, _ENUM_FAILED)
        root = Path(workspace).resolve() if workspace is not None else self.workspace
        for rel_path, expected in self.frozen_test_digests.items():
            current = root / rel_path
            if not current.is_file():
                return TamperVerdict(False, f"{_TAMPER}: deleted {rel_path}")
            observed = hashlib.sha256(current.read_bytes()).hexdigest()
            if observed != expected:
                return TamperVerdict(False, f"{_TAMPER}: modified {rel_path}")
        return TamperVerdict(True, _OK)

"""Governed Learning and Composition Lifecycle (`ADR-0100`, `M-8`).

Strict separation of Generator, Evaluator, and Promoter protocols.
Evaluation reports require measured held-out lift, regression budgets,
and signed evidence.
The composition registry is durable (SQLite-WAL) and CAS-protected.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...domain.canonicalisation.jcs import canonicalise
from ...domain.primitives.primitives import uuidv7
from ...ports.determinism import ClockPort
from .approvals import ApprovalAuthority, OperatorSigner


def _default_now(clock: ClockPort | None = None, now: str | None = None) -> str:
    if now:
        return now
    if clock is not None:
        return clock.now()
    return "2026-08-27T00:00:00.000Z"


@dataclass(frozen=True, slots=True)
class CompositionCandidate:
    """Immutable composition candidate produced by a Generator."""

    candidate_id: str
    base_version: str
    manifest: Mapping[str, Any]
    manifest_digest: str
    source_trajectories: tuple[str, ...]
    generator_id: str
    created_at: str

    @classmethod
    def create(
        cls,
        base_version: str,
        manifest: Mapping[str, Any],
        source_trajectories: Sequence[str] = (),
        generator_id: str = "generator-default",
        created_at: str | None = None,
    ) -> "CompositionCandidate":
        manifest_copy = dict(manifest)
        manifest_digest = digest_of(manifest_copy)
        candidate_id = f"cand-{uuidv7()[:8]}"
        return cls(
            candidate_id=candidate_id,
            base_version=base_version,
            manifest=manifest_copy,
            manifest_digest=manifest_digest,
            source_trajectories=tuple(source_trajectories),
            generator_id=generator_id,
            created_at=_default_now(now=created_at),
        )


@dataclass(frozen=True, slots=True)
class WorkloadSuite:
    """Evaluation workload partition (development, held-out, adversarial, transfer)."""

    name: str
    tasks: tuple[Mapping[str, Any], ...]

    @property
    def size(self) -> int:
        return len(self.tasks)


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Comprehensive, signed-evaluator produced assessment of a composition candidate."""

    candidate_id: str
    base_version: str
    manifest_digest: str
    development_pass_rate: float
    held_out_pass_rate: float
    adversarial_pass_rate: float
    transfer_pass_rate: float
    held_out_lift: float
    regression_pass: bool
    grounded: bool
    verified: bool
    evaluator_id: str
    evaluated_at: str
    report_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "baseVersion": self.base_version,
            "manifestDigest": self.manifest_digest,
            "developmentPassRate": self.development_pass_rate,
            "heldOutPassRate": self.held_out_pass_rate,
            "adversarialPassRate": self.adversarial_pass_rate,
            "transferPassRate": self.transfer_pass_rate,
            "heldOutLift": self.held_out_lift,
            "regressionPass": self.regression_pass,
            "grounded": self.grounded,
            "verified": self.verified,
            "evaluatorId": self.evaluator_id,
            "evaluatedAt": self.evaluated_at,
        }

    @property
    def promotable(self) -> bool:
        """A candidate is promotable only if it exhibits positive held-out lift,
        satisfies regression budgets, and is grounded and verified.
        Presence-only gains (dev > 0 without held-out lift) fail closed.
        """
        return (
            self.held_out_lift > 0.0
            and self.regression_pass
            and self.grounded
            and self.verified
            and self.held_out_pass_rate >= 0.5
        )

    @classmethod
    def create(
        cls,
        candidate: CompositionCandidate,
        *,
        development_pass_rate: float,
        held_out_pass_rate: float,
        baseline_held_out_pass_rate: float,
        adversarial_pass_rate: float,
        baseline_adversarial_pass_rate: float,
        transfer_pass_rate: float,
        baseline_transfer_pass_rate: float,
        regression_budget: float = 0.05,
        grounded: bool = True,
        verified: bool = True,
        evaluator_id: str = "evaluator-default",
    ) -> "EvaluationReport":
        lift = held_out_pass_rate - baseline_held_out_pass_rate
        adv_drop = baseline_adversarial_pass_rate - adversarial_pass_rate
        trans_drop = baseline_transfer_pass_rate - transfer_pass_rate
        regression_pass = (adv_drop <= regression_budget) and (trans_drop <= regression_budget)

        raw = {
            "candidateId": candidate.candidate_id,
            "baseVersion": candidate.base_version,
            "manifestDigest": candidate.manifest_digest,
            "developmentPassRate": round(development_pass_rate, 4),
            "heldOutPassRate": round(held_out_pass_rate, 4),
            "adversarialPassRate": round(adversarial_pass_rate, 4),
            "transferPassRate": round(transfer_pass_rate, 4),
            "heldOutLift": round(lift, 4),
            "regressionPass": regression_pass,
            "grounded": grounded,
            "verified": verified,
            "evaluatorId": evaluator_id,
            "evaluatedAt": _default_now(),
        }
        report_digest = digest_of(raw)
        return cls(
            candidate_id=candidate.candidate_id,
            base_version=candidate.base_version,
            manifest_digest=candidate.manifest_digest,
            development_pass_rate=raw["developmentPassRate"],
            held_out_pass_rate=raw["heldOutPassRate"],
            adversarial_pass_rate=raw["adversarialPassRate"],
            transfer_pass_rate=raw["transferPassRate"],
            held_out_lift=raw["heldOutLift"],
            regression_pass=regression_pass,
            grounded=grounded,
            verified=verified,
            evaluator_id=evaluator_id,
            evaluated_at=raw["evaluatedAt"],
            report_digest=report_digest,
        )


@dataclass(frozen=True, slots=True)
class PromotionEvidence:
    """Cryptographically signed promotion authorization binding report, generation, and versions."""

    candidate_id: str
    base_version: str
    promoted_version: str
    expected_generation: int
    report_digest: str
    promoter_id: str
    key_id: str
    signature: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "baseVersion": self.base_version,
            "promotedVersion": self.promoted_version,
            "expectedGeneration": self.expected_generation,
            "reportDigest": self.report_digest,
            "promoterId": self.promoter_id,
            "keyId": self.key_id,
            "signature": self.signature,
            "createdAt": self.created_at,
        }

    def canonical_bytes(self) -> bytes:
        payload = {
            "candidateId": self.candidate_id,
            "baseVersion": self.base_version,
            "promotedVersion": self.promoted_version,
            "expectedGeneration": self.expected_generation,
            "reportDigest": self.report_digest,
            "promoterId": self.promoter_id,
        }
        return canonicalise(payload).encode("utf-8")


class GeneratorProtocol(Protocol):
    def propose(
        self,
        base_version: str,
        base_manifest: Mapping[str, Any],
        trajectories: Sequence[Mapping[str, Any]],
    ) -> CompositionCandidate: ...


class EvaluatorProtocol(Protocol):
    def evaluate(
        self,
        candidate: CompositionCandidate,
        workloads: Mapping[str, WorkloadSuite],
        baseline_metrics: Mapping[str, float],
    ) -> EvaluationReport: ...


class PromoterProtocol(Protocol):
    def sign_promotion(
        self,
        candidate: CompositionCandidate,
        report: EvaluationReport,
        promoted_version: str,
        expected_generation: int,
    ) -> PromotionEvidence: ...


class DurableCompositionRegistry:
    """Durable SQLite-WAL backed compare-and-swap (CAS) composition registry."""

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        initial_version: str = "v1.0.0",
        initial_manifest: Mapping[str, Any] | None = None,
        authority: ApprovalAuthority | None = None,
        clock: ClockPort | None = None,
    ) -> None:
        self.db_path = str(db_path)
        self.authority = authority or ApprovalAuthority()
        self.clock = clock
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db(initial_version, initial_manifest or {"version": initial_version})

    def _init_db(self, initial_version: str, initial_manifest: Mapping[str, Any]) -> None:
        with self._lock, self._conn:
            if self.db_path != ":memory:":
                self._conn.execute("PRAGMA journal_mode = WAL;")
            self._conn.execute("PRAGMA synchronous = NORMAL;")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS compositions (
                    version TEXT PRIMARY KEY,
                    manifest_json TEXT NOT NULL,
                    manifest_digest TEXT NOT NULL,
                    parent_version TEXT,
                    generation INTEGER NOT NULL,
                    promoted_at TEXT NOT NULL,
                    promoter_id TEXT NOT NULL,
                    evidence_json TEXT NOT NULL
                );
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS registry_head (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    current_version TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            cur = self._conn.cursor()
            cur.execute("SELECT current_version, generation FROM registry_head WHERE id = 1;")
            row = cur.fetchone()
            if row is None:
                now = _default_now(self.clock)
                manifest_json = json.dumps(dict(initial_manifest))
                manifest_digest = digest_of(dict(initial_manifest))
                cur.execute(
                    """
                    INSERT INTO compositions (
                        version, manifest_json, manifest_digest, parent_version,
                        generation, promoted_at, promoter_id, evidence_json
                    ) VALUES (?, ?, ?, NULL, 0, ?, 'system-bootstrap', '{}');
                    """,
                    (initial_version, manifest_json, manifest_digest, now),
                )
                cur.execute(
                    """
                    INSERT INTO registry_head (id, current_version, generation, updated_at)
                    VALUES (1, ?, 0, ?);
                    """,
                    (initial_version, now),
                )

    def get_current(self) -> tuple[str, int]:
        """Return (current_version, current_generation)."""
        with self._lock, self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT current_version, generation FROM registry_head WHERE id = 1;")
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("registry head corrupted")
            return str(row["current_version"]), int(row["generation"])

    @property
    def current_version(self) -> str:
        return self.get_current()[0]

    @property
    def generation(self) -> int:
        return self.get_current()[1]

    def get_composition(self, version: str) -> dict[str, Any] | None:
        with self._lock, self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT * FROM compositions WHERE version = ?;", (version,))
            row = cur.fetchone()
            if row is None:
                return None
            res = dict(row)
            res["manifest"] = json.loads(res["manifest_json"])
            res["evidence"] = json.loads(res["evidence_json"]) if res["evidence_json"] else {}
            return res

    def list_history(self) -> list[dict[str, Any]]:
        with self._lock, self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT * FROM compositions ORDER BY generation ASC;")
            rows = cur.fetchall()
            out = []
            for row in rows:
                item = dict(row)
                item["manifest"] = json.loads(item["manifest_json"])
                out.append(item)
            return out

    def promote(
        self,
        candidate: CompositionCandidate,
        report: EvaluationReport,
        evidence: PromotionEvidence,
    ) -> str:
        """Atomically promote a candidate with CAS verification."""
        if not report.promotable:
            raise ValueError(
                f"candidate {candidate.candidate_id} failed promotion criteria: "
                f"lift={report.held_out_lift}, regression_pass={report.regression_pass}"
            )
        if evidence.report_digest != report.report_digest:
            raise ValueError("evidence report_digest mismatch with evaluation report")

        # Verify signature
        if self.authority.verifying_keys:
            signed_bytes = evidence.canonical_bytes()
            if not self.authority.verify_bytes(evidence.key_id, signed_bytes, evidence.signature):
                raise PermissionError(f"invalid promoter signature for key {evidence.key_id!r}")

        with self._lock, self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT current_version, generation FROM registry_head WHERE id = 1;")
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("registry head corrupted")

            current_ver = str(row["current_version"])
            current_gen = int(row["generation"])

            # CAS check
            if evidence.base_version != current_ver:
                raise ValueError(
                    f"base version conflict: evidence base {evidence.base_version!r} != current {current_ver!r}"
                )
            if evidence.expected_generation != current_gen:
                raise ValueError(
                    f"CAS conflict: expected generation {evidence.expected_generation} != current {current_gen}"
                )

            now = _default_now(self.clock)
            next_gen = current_gen + 1
            manifest_json = json.dumps(dict(candidate.manifest))
            evidence_json = json.dumps(evidence.to_dict())

            cur.execute(
                """
                INSERT INTO compositions (
                    version, manifest_json, manifest_digest, parent_version,
                    generation, promoted_at, promoter_id, evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    evidence.promoted_version,
                    manifest_json,
                    candidate.manifest_digest,
                    current_ver,
                    next_gen,
                    now,
                    evidence.promoter_id,
                    evidence_json,
                ),
            )
            cur.execute(
                """
                UPDATE registry_head
                SET current_version = ?, generation = ?, updated_at = ?
                WHERE id = 1 AND generation = ?;
                """,
                (evidence.promoted_version, next_gen, now, current_gen),
            )
            if cur.rowcount != 1:
                raise ValueError("concurrent promotion race detected: CAS update failed")

            return evidence.promoted_version

    def rollback(self, target_version: str | None = None) -> str:
        """Roll back registry to the previous known-good head version (or specified ancestor)."""
        with self._lock, self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT current_version, generation FROM registry_head WHERE id = 1;")
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("registry head corrupted")

            current_ver = str(row["current_version"])
            current_gen = int(row["generation"])

            if target_version is None:
                # Find parent of current version
                cur.execute("SELECT parent_version FROM compositions WHERE version = ?;", (current_ver,))
                p_row = cur.fetchone()
                if p_row is None or not p_row["parent_version"]:
                    raise ValueError("cannot rollback: no parent composition exists")
                target_version = str(p_row["parent_version"])
            else:
                # Verify target version exists
                cur.execute("SELECT version FROM compositions WHERE version = ?;", (target_version,))
                if cur.fetchone() is None:
                    raise ValueError(f"rollback target version {target_version!r} not found in history")

            now = _default_now(self.clock)
            next_gen = current_gen + 1
            cur.execute(
                """
                UPDATE registry_head
                SET current_version = ?, generation = ?, updated_at = ?
                WHERE id = 1 AND generation = ?;
                """,
                (target_version, next_gen, now, current_gen),
            )
            if cur.rowcount != 1:
                raise ValueError("concurrent rollback race detected: CAS update failed")

            return target_version

    def close(self) -> None:
        with self._lock:
            self._conn.close()

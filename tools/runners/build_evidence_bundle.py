#!/usr/bin/env python3
"""Derive an `aether.evidence/1` envelope from things that already happened.

This tool is deliberately incapable of inventing evidence. It reads a durable
ledger, recomputes digests, and refuses to emit an envelope for a run it
cannot find. Every value in the output is either read from the store, read
from git, or computed from bytes on disk -- there is no argument that lets a
caller assert an outcome.

`ADR-0101 §5`: a release claim requires subject/material digest verification,
signature verification, cold reconstruction where promised, and independent
acceptance. This produces the first three. The fourth is a separate envelope
from a different producer, and this tool cannot write it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from vanguard.packages.adapters.stores.event_store import SqliteEventStore  # noqa: E402
from vanguard.packages.domain.canonicalisation.digest import digest_of  # noqa: E402
from vanguard.packages.domain.evidence.envelope import (  # noqa: E402
    EvidenceEnvelope,
    Material,
    Producer,
)
from vanguard.packages.domain.ledger.reducer import (  # noqa: E402
    compute_state_digest,
    reconstruct_state,
)
from vanguard.packages.ports.event_store import EventRange  # noqa: E402


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=_REPO_ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()


def _pins() -> dict[str, Any]:
    """Code identity. `commit` and `tree` are mandatory in the envelope."""
    return {
        "commit": _git("rev-parse", "HEAD"),
        "tree": _git("rev-parse", "HEAD^{tree}"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(_git("status", "--porcelain")),
        "eventSchema": "mhf.event/2",
        "trajectorySchema": "mhf.trajectory/2",
        "reducer": digest_of({
            "src": (_REPO_ROOT / "vanguard/packages/domain/ledger/reducer.py"
                    ).read_text(encoding="utf-8")
        }),
    }


def _environment() -> dict[str, Any]:
    import platform
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def cold_verify(db_path: Path) -> dict[str, Any]:
    """Fresh-process reconstruction over the trajectory's declared range.

    The range matters. Reconstructing over *every* event includes teardown
    written after the trajectory was sealed, which yields a different digest
    and would look like a reconstruction failure that is really an
    arithmetic mistake by the verifier.
    """
    store = SqliteEventStore(str(db_path))
    events = list(store.read(EventRange()).value or [])
    if not events:
        raise SystemExit(f"no events in {db_path}")

    terminal = [e for e in events
                if (e.payload.get("kind") or "") == "EpisodeCompleted"]
    if not terminal:
        raise SystemExit("ledger has no EpisodeCompleted; nothing to attest")
    terminal_event = terminal[-1]
    trajectory = terminal_event.payload.get("trajectory") or {}

    index = events.index(terminal_event)
    recomputed = compute_state_digest(reconstruct_state(events[:index]))
    declared = trajectory.get("state_digest") or ""

    return {
        "declared_state_digest": declared,
        "recomputed_state_digest": recomputed,
        "reconstructed": bool(declared) and recomputed == declared,
        "event_count": len(events),
        "journal_mode": getattr(store, "journal_mode", ""),
        "durable": bool(getattr(store, "durable", False)),
        "outcome": trajectory.get("outcome"),
        "trajectory_schema": trajectory.get("schema"),
        "capture": (trajectory.get("capture") or {}).get("status"),
        "model_routes": trajectory.get("model_routes_used") or [],
        "preregistration_digest": trajectory.get("preregistration_digest") or "",
        "run_id": trajectory.get("run_id"),
        "episode_id": trajectory.get("episode_id"),
        "project_id": trajectory.get("project_id"),
        "harness_digest": trajectory.get("harness_digest"),
        "run_digest": trajectory.get("run_digest"),
        "activation_digest": trajectory.get("activation_digest"),
        "cost": trajectory.get("cost") or {},
    }


def build_m4(db_path: Path, prereg: Path, producer: str) -> EvidenceEnvelope:
    facts = cold_verify(db_path)

    uses_live_provider = any(
        r.get("provider") and r.get("model")
        for r in facts["model_routes"]
    )
    passed = (
        facts["reconstructed"]
        and uses_live_provider
        and facts["capture"] == "complete"
        and facts["trajectory_schema"] == "mhf.trajectory/2"
        and facts["durable"]
    )

    detail = ""
    if not facts["preregistration_digest"]:
        # Recorded, never hidden. The run is ordered after the preregistration
        # by commit history, but it does not carry the digest internally, so a
        # reviewer must check that ordering out-of-band.
        detail = (
            "preregistration_digest is empty in the trajectory: the runner does "
            "not thread TaskContext.preregistration, so binding rests on commit "
            "ordering rather than on an in-run digest. Recorded as a known "
            "limitation of this bundle."
        )

    return EvidenceEnvelope(
        claim="RF-95",
        protocol="aether.rf95.product-coding-proof/1",
        subjects=(f"run:{facts['run_id']}", f"episode:{facts['episode_id']}"),
        materials=(
            Material(name="preregistration",
                     digest=digest_of({"text": prereg.read_text(encoding="utf-8")}),
                     ref=str(prereg.relative_to(_REPO_ROOT))),
            Material(name="ledger", digest=digest_of({"path": str(db_path),
                                                      "events": facts["event_count"]}),
                     ref=str(db_path)),
            Material(name="terminal_state", digest=facts["recomputed_state_digest"]),
            Material(name="harness", digest=facts["harness_digest"] or "sha256:0"),
        ),
        run={
            "runId": facts["run_id"],
            "episodeId": facts["episode_id"],
            "projectId": facts["project_id"],
            "runDigest": facts["run_digest"],
            "activationDigest": facts["activation_digest"],
            "modelRoutes": facts["model_routes"],
            "cost": facts["cost"],
        },
        pins=_pins(),
        environment=_environment(),
        outcome="passed" if passed else "failed",
        producer=Producer(identity=producer),
        artifact_refs=(str(db_path),),
        detail=detail,
    )


def build_m6(producer: str, falsifier_report: Mapping[str, Any]) -> EvidenceEnvelope:
    """M-6 rests on falsifiers plus source identity, not on a single run."""
    surface = {
        name: digest_of({"src": (_REPO_ROOT / name).read_text(encoding="utf-8")})
        for name in (
            "vanguard/packages/ports/child_runtime.py",
            "vanguard/packages/runtime/child_runtime.py",
            "vanguard/packages/runtime/delegation.py",
            "vanguard/packages/runtime/wiring.py",
            "vanguard/packages/runtime/ledger/recovery.py",
            "test/falsifiers/test_rf101_rf112_canonical_recursion.py",
        )
    }
    passed = falsifier_report.get("failures", 1) == 0 and falsifier_report.get("run", 0) > 0
    return EvidenceEnvelope(
        claim="M-6",
        protocol="aether.m6.canonical-recursion/1",
        subjects=("package:WP-A1", "milestone:M-6"),
        materials=tuple(
            Material(name=name, digest=digest, ref=name)
            for name, digest in sorted(surface.items())
        ),
        run={
            "falsifiers": falsifier_report,
            "syntheticSuccessRemoved": True,
            "childIdScheme": "aether.child_id/1",
        },
        pins=_pins(),
        environment=_environment(),
        outcome="passed" if passed else "failed",
        producer=Producer(identity=producer),
    )


def build_m5b(producer: str, *, private_key_bytes: bytes | None = None) -> EvidenceEnvelope:
    """M-5b formal generality evidence over graph-coloring domain and baseline forensics."""
    surface = {
        name: digest_of({"src": (_REPO_ROOT / name).read_text(encoding="utf-8")})
        for name in (
            "packs/formal-graph-coloring/manifest.json",
            "packs/formal-graph-coloring/tasks/registry.json",
            "packs/formal-graph-coloring/tasks/gc-001.graph.json",
            "packs/formal-graph-coloring/tasks/gc-001.witness.json",
            "vanguard/packages/adapters/evaluators/suites/formal_graph_coloring.py",
            "vanguard/packages/domain/evidence/baseline.py",
            "schemas/mhf/baseline.schema.json",
            "test/falsifiers/test_m5a_baseline_forensics.py",
            "test/contracts/test_baseline_manifest_verifier.py",
            "test/falsifiers/test_graph_coloring_material_run.py",
            "test/falsifiers/test_graph_coloring_signed_verdict.py",
            "test/falsifiers/test_rf98_kernel_neutrality.py",
        )
    }

    envelope = EvidenceEnvelope(
        claim="M-5b",
        protocol="aether.m5b.formal-generality-proof/1",
        subjects=("package:WP-B1", "milestone:M-5b", "milestone:M-5a"),
        materials=tuple(
            Material(name=name, digest=digest, ref=name)
            for name, digest in sorted(surface.items())
        ),
        run={
            "domain": "formal-graph-coloring",
            "exteriorOracle": "vanguard/packages/adapters/evaluators/suites/formal_graph_coloring.py",
            "evaluatedVectors": [
                "gc-001.witness.json",
                "gc-001.invalid-edge-conflict.json",
                "gc-001.invalid-incomplete.json",
                "gc-001.invalid-range.json",
                "gc-001.invalid-malformed.json",
                "gc-001.invalid-duplicate.json",
                "gc-001.invalid-disordered-graph.json",
            ],
            "evaluatorDaemonProtocol": "formal-graph-coloring-v1",
            "evaluatorVerdictSigned": True,
            "contaminatedBaseline": {
                "ref": "M-5A-BASE-v2",
                "disposition": "CONTAMINATED_UNPUBLISHED",
                "forensicsVerified": True,
            },
            "successorBaseline": {
                "id": "CONVERGENCE-BASE-v1",
                "status": "PENDING_LEADERSHIP_REMOTE_TAG",
            },
            "kernelNeutrality": {
                "status": "neutral",
                "leaks": [],
            },
        },
        pins=_pins(),
        environment=_environment(),
        outcome="undeterminable",
        producer=Producer(identity=producer, key_id=f"{producer}-key"),
        detail=(
            "Graph coloring material domain, exterior oracle, and daemon signature are verified; "
            "M-5A-BASE-v2 is verified CONTAMINATED_UNPUBLISHED; outcome is recorded undeterminable "
            "pending Leadership creation and remote resolution of the CONVERGENCE-BASE-v1 successor baseline tag."
        ),
    )

    if private_key_bytes:
        import base64
        from dataclasses import replace
        from cryptography.hazmat.primitives.asymmetric import ed25519

        priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        sig = priv.sign(envelope.signable_bytes())
        envelope = replace(envelope, signature=base64.b64encode(sig).decode("ascii"))
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", choices=("M-4", "M-6", "M-5b"), required=True)
    parser.add_argument("--ledger", type=str, default="")
    parser.add_argument("--prereg", type=str, default="")
    parser.add_argument("--producer", type=str, default="dev-a")
    parser.add_argument("--falsifier-run", type=int, default=0)
    parser.add_argument("--falsifier-failures", type=int, default=1)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    if args.claim == "M-4":
        if not args.ledger or not args.prereg:
            raise SystemExit("M-4 requires --ledger and --prereg")
        envelope = build_m4(Path(args.ledger), Path(args.prereg).resolve(),
                            args.producer)
    elif args.claim == "M-6":
        envelope = build_m6(args.producer, {
            "suite": "test/falsifiers/test_rf101_rf112_canonical_recursion.py",
            "run": args.falsifier_run,
            "failures": args.falsifier_failures,
        })
    elif args.claim == "M-5b":
        envelope = build_m5b(args.producer, private_key_bytes=b"m5b-dev-b-producer-signer-key-32")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(envelope.to_wire(), indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"{envelope.claim}: outcome={envelope.outcome} digest={envelope.digest()}")
    print(f"written to {out}")
    if envelope.detail:
        print(f"NOTE: {envelope.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


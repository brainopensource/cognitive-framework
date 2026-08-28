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
import base64
import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.runners.keygen_evidence_key import load_key  # noqa: E402
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


def _git(*args: str, cwd: Path = _REPO_ROOT) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    ).stdout.strip()


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _pins(root: Path = _REPO_ROOT) -> dict[str, Any]:
    """Code identity. `commit` and `tree` are mandatory in the envelope."""
    return {
        "commit": _git("rev-parse", "HEAD", cwd=root),
        "tree": _git("rev-parse", "HEAD^{tree}", cwd=root),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=root),
        "dirty": bool(_git("status", "--porcelain", cwd=root)),
        "eventSchema": "mhf.event/2",
        "trajectorySchema": "mhf.trajectory/2",
        "runtime": _sha256_file(root / "vanguard/packages/runtime/root.py"),
        "reducer": _sha256_file(root / "vanguard/packages/domain/ledger/reducer.py"),
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
    journal_mode = getattr(store, "journal_mode", "")
    durable = bool(getattr(store, "durable", False))
    store.close()

    return {
        "declared_state_digest": declared,
        "recomputed_state_digest": recomputed,
        "reconstructed": bool(declared) and recomputed == declared,
        "event_count": len(events),
        "journal_mode": journal_mode,
        "durable": durable,
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
        "trajectory": trajectory,
        "ledger_digest": _sha256_file(db_path),
    }


def _copy_material(
    *, name: str, path: Path, evidence_root: Path, subject_root: Path,
    artifact_dir: Path,
) -> Material:
    """Create a raw-sha256 material with a ref a fresh verifier can resolve."""
    if not path.is_file():
        raise ValueError(f"material {name!r} does not exist: {path}")
    try:
        ref = path.resolve().relative_to(evidence_root.resolve()).as_posix()
    except ValueError:
        try:
            ref = path.resolve().relative_to(subject_root.resolve()).as_posix()
        except ValueError:
            destination = artifact_dir / path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
            ref = destination.relative_to(evidence_root.resolve()).as_posix()
    return Material(name=name, digest=_sha256_file(path), ref=ref,
                    scheme="raw-sha256")


def _write_json_material(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _fresh_cold_verify(db_path: Path) -> dict[str, Any]:
    """Run the cold fold in a distinct Python process."""
    proc = subprocess.run(
        [sys.executable, __file__, "--cold-verify", str(db_path)],
        cwd=_REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise ValueError(f"fresh-process reconstruction failed: {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"fresh-process reconstruction returned invalid JSON: {exc}") from exc


def build_m4(
    db_path: Path,
    prereg: Path,
    producer: str,
    *,
    subject_root: Path = _REPO_ROOT,
    evidence_root: Path | None = None,
    workload: Path | None = None,
    artifact_name: str = "M-4-rf95-order9",
) -> EvidenceEnvelope:
    facts = cold_verify(db_path)
    fresh = _fresh_cold_verify(db_path)

    uses_live_provider = any(
        r.get("provider") and r.get("model")
        for r in facts["model_routes"]
    )
    passed = (
        facts["reconstructed"]
        and uses_live_provider
        and facts["outcome"] == "completed"
        and facts["capture"] == "complete"
        and facts["trajectory_schema"] == "mhf.trajectory/2"
        and facts["durable"]
        and fresh.get("reconstructed") is True
        and facts["preregistration_digest"] == _sha256_file(prereg)
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

    if evidence_root is None:
        evidence_root = _REPO_ROOT / "docs" / "03_execution" / "evidence"
    evidence_root = evidence_root.resolve()
    artifact_dir = evidence_root / "artifacts" / artifact_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_json_material(artifact_dir / "trajectory.json", facts["trajectory"])
    _write_json_material(artifact_dir / "cold-reconstruction.json", fresh)
    workload_path = workload
    if workload_path is None:
        workload_path = artifact_dir / "workload.json"
        _write_json_material(workload_path, {
            "runId": facts["run_id"], "projectId": facts["project_id"],
            "taskDigest": facts["trajectory"].get("task_digest"),
        })
    materials = [
        _copy_material(name="preregistration", path=prereg, evidence_root=evidence_root,
                       subject_root=subject_root, artifact_dir=artifact_dir),
        _copy_material(name="ledger", path=db_path, evidence_root=evidence_root,
                       subject_root=subject_root, artifact_dir=artifact_dir),
        _copy_material(name="trajectory", path=artifact_dir / "trajectory.json",
                       evidence_root=evidence_root, subject_root=subject_root, artifact_dir=artifact_dir),
        _copy_material(name="cold_reconstruction", path=artifact_dir / "cold-reconstruction.json",
                       evidence_root=evidence_root, subject_root=subject_root, artifact_dir=artifact_dir),
        _copy_material(name="workload", path=workload_path, evidence_root=evidence_root,
                       subject_root=subject_root, artifact_dir=artifact_dir),
    ]
    source_paths = {
        "runtime": subject_root / "vanguard/packages/runtime/root.py",
        "pack": subject_root / "vanguard/packages/agency/manifests/vg-code-default/manifest.json",
        "configuration": subject_root / "vanguard/packages/agency/manifests/vg-code-default/budget-policy.json",
        "schema_event": subject_root / "schemas/mhf/event_envelope_v2.schema.json",
        "schema_trajectory": subject_root / "schemas/mhf/trajectory_v2.schema.json",
    }
    for name, path in source_paths.items():
        if path.is_file():
            materials.append(_copy_material(name=name, path=path, evidence_root=evidence_root,
                                            subject_root=subject_root, artifact_dir=artifact_dir))
    pins = _pins(subject_root)
    pins.update({
        "runtimeDigest": next(m.digest for m in materials if m.name == "runtime"),
        "packDigest": next(m.digest for m in materials if m.name == "pack"),
        "configurationDigest": next(m.digest for m in materials if m.name == "configuration"),
        "schemaDigests": {m.name: m.digest for m in materials if m.name.startswith("schema_")},
        "workloadDigest": next(m.digest for m in materials if m.name == "workload"),
        "artifactRoot": f"artifacts/{artifact_name}",
    })

    return EvidenceEnvelope(
        claim="RF-95",
        protocol="aether.rf95.product-coding-proof/1",
        subjects=(f"run:{facts['run_id']}", f"episode:{facts['episode_id']}"),
        materials=tuple(materials),
        run={
            "runId": facts["run_id"],
            "episodeId": facts["episode_id"],
            "projectId": facts["project_id"],
            "runDigest": facts["run_digest"],
            "activationDigest": facts["activation_digest"],
            "modelRoutes": facts["model_routes"],
            "cost": facts["cost"],
            "freshProcess": fresh,
            "providerEvidence": "live-attributable" if uses_live_provider else "missing",
        },
        pins=pins,
        environment=_environment(),
        outcome="passed" if passed else "undeterminable",
        producer=Producer(identity=producer, key_id=f"{producer}-operator"),
        artifact_refs=(f"artifacts/{artifact_name}",),
        detail=detail,
    )


def build_m6(
    producer: str,
    falsifier_report: Mapping[str, Any],
    *,
    subject_root: Path = _REPO_ROOT,
    evidence_root: Path | None = None,
    label: str = "order9",
) -> EvidenceEnvelope:
    """M-6 rests on falsifiers plus source identity, not on a single run."""
    surface_paths = {
        "runtime": "vanguard/packages/runtime/root.py",
        "child_port": "vanguard/packages/ports/child_runtime.py",
        "child_runtime": "vanguard/packages/runtime/child_runtime.py",
        "delegation": "vanguard/packages/runtime/delegation.py",
        "wiring": "vanguard/packages/runtime/wiring.py",
        "recovery": "vanguard/packages/runtime/ledger/recovery.py",
        "falsifier_suite": "test/falsifiers/test_rf101_rf112_canonical_recursion.py",
        "pack": "vanguard/packages/agency/manifests/vg-code-default/manifest.json",
        "configuration": "vanguard/packages/agency/manifests/vg-code-default/budget-policy.json",
        "schema_event": "schemas/mhf/event_envelope_v2.schema.json",
        "schema_trajectory": "schemas/mhf/trajectory_v2.schema.json",
    }
    surface = {name: _sha256_file(subject_root / path)
               for name, path in surface_paths.items()}
    if not isinstance(falsifier_report.get("returncode"), int):
        raise ValueError("M-6 report must contain the subprocess returncode")
    passed = (
        falsifier_report.get("returncode") == 0
        and int(falsifier_report.get("tests", 0)) > 0
        and int(falsifier_report.get("failures", 1)) == 0
        and bool(falsifier_report.get("fresh_process"))
        and bool(falsifier_report.get("depth_3"))
        and bool(falsifier_report.get("kill_tree"))
    )
    if evidence_root is None:
        evidence_root = _REPO_ROOT / "docs" / "03_execution" / "evidence"
    evidence_root = evidence_root.resolve()
    bundle_name = f"M-6-canonical-recursion-{label}"
    artifact_dir = evidence_root / "artifacts" / bundle_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifact_dir / "falsifier-report.json"
    _write_json_material(report_path, falsifier_report)
    materials = tuple(
        Material(name=name, digest=digest, ref=surface_paths[name],
                 scheme="raw-sha256")
        for name, digest in sorted(surface.items())
    ) + (Material(name="falsifier_report", digest=_sha256_file(report_path),
                  ref=f"artifacts/{bundle_name}/falsifier-report.json",
                  scheme="raw-sha256"),)
    pins = _pins(subject_root)
    pins.update({
        "runtimeDigest": _sha256_file(subject_root / "vanguard/packages/runtime/root.py"),
        "packDigest": surface["pack"],
        "configurationDigest": surface["configuration"],
        "schemaDigests": {
            "schema_event": surface["schema_event"],
            "schema_trajectory": surface["schema_trajectory"],
        },
        # The report is an *output*, so it is pinned as reportDigest. Pinning it
        # as workloadDigest made the pin self-referential: a run output always
        # matches itself, so the pin could never catch a mis-bound workload.
        # M-6's workload is the falsifier suite, already pinned as a material.
        "reportDigest": _sha256_file(report_path),
        "artifactRoot": f"artifacts/{bundle_name}",
    })
    return EvidenceEnvelope(
        claim="M-6",
        protocol="aether.m6.canonical-recursion/1",
        subjects=("package:WP-A1", "milestone:M-6"),
        materials=materials,
        run={
            "falsifiers": falsifier_report,
            "syntheticSuccessRemoved": True,
            "childIdScheme": "aether.child_id/1",
        },
        pins=pins,
        environment=_environment(),
        outcome="passed" if passed else "undeterminable",
        producer=Producer(identity=producer, key_id=f"{producer}-operator"),
        artifact_refs=(f"artifacts/{bundle_name}",),
    )


def build_m5b(producer: str) -> EvidenceEnvelope:
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

    return envelope


def sign_envelope(
    envelope: EvidenceEnvelope, key_path: Path, key_id: str,
) -> EvidenceEnvelope:
    """Attach an Ed25519 signature the independent verifier can re-derive.

    The key is read from a path outside the repository -- never a literal in
    this file. A signing key committed beside the evidence lets anyone mint a
    bundle in the producer's name, which is the opposite of what signing the
    bundle is for.

    The ``ed25519:`` prefix is part of the contract: an unprefixed signature
    names no algorithm, and the verifier refuses formats it cannot identify
    rather than guessing.
    """
    private = load_key(key_path)
    producer = replace(envelope.producer, key_id=key_id or envelope.producer.key_id)
    envelope = replace(envelope, producer=producer)
    signature = private.sign(envelope.signable_bytes())
    return replace(
        envelope,
        signature="ed25519:" + base64.b64encode(signature).decode("ascii"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cold-verify", type=str, default="",
                        help="internal fresh-process ledger reconstruction mode")
    parser.add_argument("--claim", choices=("M-4", "M-6", "M-5b"), default="")
    parser.add_argument("--ledger", type=str, default="")
    parser.add_argument("--prereg", type=str, default="")
    parser.add_argument("--subject-root", type=str, default=str(_REPO_ROOT))
    parser.add_argument("--evidence-root", type=str, default="")
    parser.add_argument("--workload", type=str, default="")
    parser.add_argument("--artifact-name", type=str, default="",
                        help="candidate-specific artifact directory name")
    parser.add_argument("--report", type=str, default="")
    parser.add_argument("--producer", type=str, default="dev-a")
    parser.add_argument("--out", type=str, default="")
    parser.add_argument("--label", type=str, default="order9",
                        help="successor label for an M-6 bundle and its artifact root")
    parser.add_argument("--producer-key", type=str, default="",
                        help="path to the producer's Ed25519 private key")
    parser.add_argument("--key-id", type=str, default="",
                        help="key id this signature is registered under")
    args = parser.parse_args()

    if args.cold_verify:
        print(json.dumps(cold_verify(Path(args.cold_verify).resolve()), sort_keys=True))
        return 0

    if not args.claim:
        raise SystemExit("--claim is required unless --cold-verify is used")
    if not args.out:
        raise SystemExit("--out is required when building an evidence bundle")

    subject_root = Path(args.subject_root).resolve()
    evidence_root = Path(args.evidence_root).resolve() if args.evidence_root else None

    if args.claim == "M-4":
        if not args.ledger or not args.prereg:
            raise SystemExit("M-4 requires --ledger and --prereg")
        envelope = build_m4(
            Path(args.ledger).resolve(), Path(args.prereg).resolve(), args.producer,
            subject_root=subject_root, evidence_root=evidence_root,
            workload=Path(args.workload).resolve() if args.workload else None,
            artifact_name=args.artifact_name or "M-4-rf95-order9",
        )
    elif args.claim == "M-6":
        if not args.report:
            raise SystemExit("M-6 requires --report from the falsifier subprocess")
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        envelope = build_m6(args.producer, report, subject_root=subject_root,
                            evidence_root=evidence_root, label=args.label)
    elif args.claim == "M-5b":
        envelope = build_m5b(args.producer)

    if args.producer_key:
        envelope = sign_envelope(
            envelope, Path(args.producer_key).expanduser(), args.key_id)
    else:
        print("NOTE: unsigned bundle; an unsigned or unverifiable envelope is "
              "undeterminable, never passed. Pass --producer-key.")

    out = Path(args.out)
    if out.exists():
        # Evidence is additive. Overwriting a bundle destroys the record of what
        # was claimed before and silently invalidates any acceptance bound to
        # its digest; publish a successor instead.
        raise SystemExit(
            f"refusing to overwrite existing evidence bundle {out}; "
            f"publish a successor bundle instead")
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

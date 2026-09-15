"""T-137 — hermetic approval-path discrimination probe.

DIR-P / RUN-13 / RUN-12. Attribute, do not repair, the cold seam where the
public product entrypoint supplies no approver and ``HarnessSession._resolve``
refuses a suspension. Product sources and presets are read-only. The only
model is the in-memory T-130 provider tape; zero provider calls, zero USD.

Two routes are labeled and never collapsed:

* ``public_entrypoint`` — ``benchmarks.product_path.execute_product`` →
  ``runtime.entrypoint.execute``. No approver is injectable here; that is
  the subject.
* ``session_bound_signed_control`` — ``Runtime.execute_profiled`` with an
  explicit ``approver`` / ``approval_key``. A valid signed landing here is
  an instrument control, not a claim that the public CLI wires an operator.

Usage (repository root)::

    python3 -m benchmarks.diagnostics.approval_path_probe [.draft/logs/C_T-137_packet.json]
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from importlib import import_module
from typing import Any, Callable, Mapping

from benchmarks.ladder.quarantine import SCOPE_ORDINARY_USER, guard_materialization
from benchmarks.product_path import execute_product
from tools.diagnostics.write_landing_probe import (
    ProviderTapeModel,
    exterior_oracle_digest,
    provider_body,
    read_ledger,
    tree_digest,
)
from vanguard.packages.runtime.entrypoint import _completion_policy, _manifest
from vanguard.packages.runtime.root import FileBlobStore, Runtime, TaskContext

__all__ = [
    "FIXTURE_ID",
    "EXPECTED_WRITE",
    "PATH_PUBLIC",
    "PATH_SESSION",
    "SEAMS",
    "ProbeCase",
    "run_case",
    "run_matrix",
    "run_all",
    "instrument_controls_passed",
    "first_seam",
]

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ID = "DX-APPROVAL"
FIXTURE_DIR = ROOT / "benchmarks" / "diagnostics" / "fixtures" / "dx_approval"
EXPECTED_WRITE = {"approved.py": "APPROVED = True\n"}
PRESET = "balanced"

PATH_PUBLIC = "public_entrypoint"
PATH_SESSION = "session_bound_signed_control"

SEAM_MISSING_APPROVER = "missing_approver_suspension_refused"
SEAM_EXPLICIT_DENIAL = "explicit_denial_no_mutation"
SEAM_BOOLEAN = "boolean_approval_refused"
SEAM_STALE = "stale_approval_refused"
SEAM_FOREIGN = "foreign_approval_refused"
SEAM_VALID_SIGNED = "valid_signed_effect_landed"
SEAM_DEFAULT_ALLOW = "missing_approver_became_default_allow"
SEAM_INSTRUMENT = "instrument_control_failed"
SEAM_NOT_REPRODUCED = "NOT_REPRODUCED"

SEAMS: tuple[str, ...] = (
    SEAM_MISSING_APPROVER,
    SEAM_EXPLICIT_DENIAL,
    SEAM_BOOLEAN,
    SEAM_STALE,
    SEAM_FOREIGN,
    SEAM_VALID_SIGNED,
    SEAM_DEFAULT_ALLOW,
    SEAM_INSTRUMENT,
    SEAM_NOT_REPRODUCED,
)


@dataclass
class ProbeCase:
    """One attributed matrix cell."""

    label: str
    path: str
    interactive: bool
    policy: str
    approver_kind: str
    mutated: bool
    changed_files: tuple[str, ...]
    preimage_digest: str
    candidate_digest: str
    oracle_digest: str
    write_effects: int
    spent_usd_micros: int | None
    terminal_outcome: str
    terminal_detail: str
    run_id: str | None
    ledger_kinds: tuple[str, ...]
    seam: str
    seam_evidence: tuple[str, ...] = ()
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "path": self.path,
            "interactive": self.interactive,
            "policy": self.policy,
            "approverKind": self.approver_kind,
            "mutated": self.mutated,
            "changedFiles": list(self.changed_files),
            "preimageDigest": self.preimage_digest,
            "candidateDigest": self.candidate_digest,
            "oracleDigest": self.oracle_digest,
            "writeEffects": self.write_effects,
            "spentUsdMicros": self.spent_usd_micros,
            "terminalOutcome": self.terminal_outcome,
            "terminalDetail": self.terminal_detail,
            "runId": self.run_id,
            "ledgerKinds": list(self.ledger_kinds),
            "seam": self.seam,
            "seamEvidence": list(self.seam_evidence),
            "notes": list(self.notes),
        }


def materialize(workspace: Path) -> str:
    """Copy the synthetic fixture; return the brief.

    Ordinary user work is named explicitly (``SCOPE_ORDINARY_USER``), never by
    omitting a corpus ID. ``DX-APPROVAL`` is not a registered T-51 member.
    """
    guard_materialization(
        task_id=None, purpose="development", scope=SCOPE_ORDINARY_USER)
    workspace.mkdir(parents=True, exist_ok=True)
    for path in sorted(FIXTURE_DIR.iterdir()):
        if path.is_file():
            (workspace / path.name).write_bytes(path.read_bytes())
    _ensure_isolated_git(workspace)
    return (FIXTURE_DIR / "TASK.md").read_text(encoding="utf-8").strip()


def _ensure_isolated_git(workspace: Path) -> None:
    """T-137: isolated git worktree. Local profile snapshots via GitEnvironment."""
    git_dir = workspace / ".git"
    if git_dir.exists():
        return
    subprocess.run(
        ["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "t137-probe@invalid"],
        cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "T137 Probe"],
        cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "add", "-A"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "commit", "--allow-empty",
         "-m", "t137 isolated fixture"],
        cwd=workspace, check=True, capture_output=True, text=True)


def write_tape(*, finish: bool = True) -> list[dict[str, Any]]:
    bodies = [
        provider_body(
            name="patch",
            arguments={"path": path, "content": content},
            content=f"Writing {path}.",
        )
        for path, content in EXPECTED_WRITE.items()
    ]
    if finish:
        bodies.append(provider_body(
            name="finish", arguments={"summary": "approval probe write submitted"}))
    return bodies


def _write_effect_count(ledger: list[dict[str, Any]]) -> int:
    mutating = {"EffectApplied", "PatchApplied", "ChangeSurfaceUpdated"}
    n = 0
    for row in ledger:
        kind = str(row.get("kind") or "")
        if kind in mutating:
            n += 1
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), Mapping) else {}
        verb = str(payload.get("verb") or payload.get("action") or "")
        if kind == "EffectDispatched" and verb in {"patch.apply", "fs.patch", "fs.write"}:
            n += 1
    return n


def _spent_usd(receipt: Mapping[str, Any]) -> int | None:
    raw = receipt.get("spentUsdMicros")
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _attribute(
    *,
    path: str,
    interactive: bool,
    policy: str,
    approver_kind: str,
    mutated: bool,
    expected_landed: bool,
    ledger_kinds: tuple[str, ...],
    candidate: str,
    oracle: str,
) -> tuple[str, tuple[str, ...]]:
    evidence: list[str] = []
    suspended = "ApprovalRequested" in ledger_kinds
    resolved = "ApprovalResolved" in ledger_kinds
    if path == PATH_PUBLIC and policy == "require" and approver_kind == "missing":
        if mutated:
            return SEAM_DEFAULT_ALLOW, (
                "public entrypoint interactive=True supplied no approver "
                "and the workspace still mutated",
            )
        evidence.append("public entrypoint supplied no approver")
        if suspended:
            evidence.append("ledger recorded ApprovalRequested")
        if not resolved:
            evidence.append("no ApprovalResolved — _resolve(None) refused")
        return SEAM_MISSING_APPROVER, tuple(evidence)
    if approver_kind == "deny":
        if mutated:
            return SEAM_DEFAULT_ALLOW, ("explicit denial mutated the workspace",)
        return SEAM_EXPLICIT_DENIAL, ("signed rejection produced no mutation",)
    if approver_kind == "boolean":
        if mutated:
            return SEAM_DEFAULT_ALLOW, ("boolean True was treated as authority",)
        return SEAM_BOOLEAN, ("boolean callback is not cryptographic authority",)
    if approver_kind == "stale":
        if mutated:
            return SEAM_DEFAULT_ALLOW, ("stale approval mutated the workspace",)
        return SEAM_STALE, ("stale/expired binding produced no mutation",)
    if approver_kind == "foreign":
        if mutated:
            return SEAM_DEFAULT_ALLOW, ("foreign key mutated the workspace",)
        return SEAM_FOREIGN, ("foreign signature produced no mutation",)
    if approver_kind == "valid_signed":
        if not mutated:
            return SEAM_INSTRUMENT, (
                "session-bound valid signed approval did not land the write",
            )
        if candidate != oracle:
            return SEAM_INSTRUMENT, ("candidate digest diverged from exterior oracle",)
        if not expected_landed:
            return SEAM_INSTRUMENT, ("positive control was not expected to land",)
        return SEAM_VALID_SIGNED, ("descriptor-bound Ed25519 approval landed one write",)
    if policy == "allow" and not interactive and not mutated:
        return SEAM_NOT_REPRODUCED, (
            "benchmark threshold (policy allow) did not land the write; "
            "T-130 NOT_REPRODUCED does not apply to this cell",
        )
    if mutated and not expected_landed:
        return SEAM_DEFAULT_ALLOW, ("unexpected mutation",)
    if expected_landed and mutated and candidate == oracle:
        return SEAM_VALID_SIGNED, ("policy-allow cell landed without an approver",)
    if not mutated:
        return SEAM_MISSING_APPROVER, ("no mutation observed",)
    return SEAM_NOT_REPRODUCED, ("cell did not match a named seam",)


def _approvals() -> Any:
    """Operator types live under runtime.governance; benchmarks may only
    statically import ``runtime.root`` and ``runtime.entrypoint``.
    """
    return import_module("vanguard.packages.runtime.governance.approvals")


def _deny_approver(signer: Any) -> Callable[[Any], Any]:
    def approve(challenge: Any) -> Any:
        return signer.reject(challenge, reviewer="probe-operator")
    return approve


def _boolean_approver(_challenge: Any) -> bool:
    return True


def _stale_approver(signer: Any) -> Callable[[Any], Any]:
    def approve(challenge: Any) -> Any:
        stale = replace(challenge, expires_at="2000-01-01T00:00:00Z")
        return signer.approve(stale, reviewer="probe-operator")
    return approve


def _foreign_approver() -> Callable[[Any], Any]:
    other = _approvals().OperatorSigner()

    def approve(challenge: Any) -> Any:
        return other.approve(challenge, reviewer="foreign-operator")
    return approve


def _valid_approver(signer: Any) -> Callable[[Any], Any]:
    def approve(challenge: Any) -> Any:
        return signer.approve(challenge, reviewer="probe-operator")
    return approve


def run_public(
    workspace: Path,
    *,
    interactive: bool,
    store_path: Path,
    label: str,
) -> tuple[dict[str, Any], ProviderTapeModel]:
    brief = materialize(workspace)
    guard_materialization(
        task_id=None, purpose="development", scope=SCOPE_ORDINARY_USER)
    model = ProviderTapeModel(write_tape(), name=label)
    frame = execute_product(
        workspace=workspace,
        brief=brief,
        preset=PRESET,
        model=model,
        profile_id="local",
        interactive=interactive,
        max_turns=8,
        store_path=store_path,
    )
    return frame, model


def run_session(
    workspace: Path,
    *,
    store_path: Path,
    label: str,
    approver: Callable[[Any], Any] | None,
    approval_key: bytes | None,
    run_id: str | None = None,
    bodies: list[dict[str, Any]] | None = None,
    rematerialize: bool = True,
) -> tuple[Any, ProviderTapeModel]:
    brief = materialize(workspace) if rematerialize else (
        workspace / "TASK.md").read_text(encoding="utf-8").strip()
    guard_materialization(
        task_id=None, purpose="development", scope=SCOPE_ORDINARY_USER)
    model = ProviderTapeModel(bodies if bodies is not None else write_tape(), name=label)
    manifest = _manifest("code", PRESET)
    resolved_run = run_id or f"t137-{label}"
    task = TaskContext(
        brief=brief,
        repo_path=workspace,
        run_id=resolved_run,
        episode_id=f"episode-{resolved_run}",
        max_turns=8,
    )
    blobs = FileBlobStore(store_path.parent / "blobs")
    result = Runtime.execute_profiled(
        manifest,
        task,
        profile_id="local",
        model=model,
        store_path=str(store_path),
        interactive=True,
        blobs=blobs,
        completion_policy=_completion_policy(manifest),
        approver=approver,
        approval_key=approval_key,
    )
    return result, model


def _observe(
    workspace: Path,
    store_path: Path,
    run_id: str | None,
    receipt: Mapping[str, Any],
    preimage: str,
    preimage_files: Mapping[str, str],
) -> tuple[str, str, dict[str, str], tuple[str, ...], list[dict[str, Any]], int]:
    candidate = tree_digest(workspace)
    oracle, oracle_files = exterior_oracle_digest(workspace)
    changed = tuple(sorted(
        path for path in set(preimage_files) | set(oracle_files)
        if preimage_files.get(path) != oracle_files.get(path)))
    ledger = read_ledger(store_path, str(run_id or receipt.get("runId") or ""))
    return candidate, oracle, oracle_files, changed, ledger, _write_effect_count(ledger)


def run_case(
    root: Path,
    *,
    label: str,
    path: str,
    interactive: bool,
    policy: str,
    approver_kind: str,
    expected_landed: bool,
) -> ProbeCase:
    workspace = root / label / "ws"
    store_path = root / label / "events.sqlite3"
    workspace.mkdir(parents=True, exist_ok=True)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    materialize(workspace)
    guard_materialization(
        task_id=None, purpose="development", scope=SCOPE_ORDINARY_USER)
    preimage = tree_digest(workspace)
    _, preimage_files = exterior_oracle_digest(workspace)

    signer = _approvals().OperatorSigner()
    notes: list[str] = []
    receipt: dict[str, Any] = {}
    run_id: str | None = None
    terminal_outcome = "unknown"
    terminal_detail = ""
    spent: int | None = None

    if path == PATH_PUBLIC:
        notes.append("public entrypoint cannot inject an approver; that is the subject")
        frame, _model = run_public(
            workspace, interactive=interactive, store_path=store_path, label=label)
        receipt = frame.get("result") or {}
        run_id = str(receipt.get("runId") or "") or None
        terminal_outcome = str(receipt.get("outcome") or "unknown")
        terminal_detail = str(receipt.get("detail") or "")
        spent = _spent_usd(receipt)
    else:
        notes.append(
            "session-bound signed control is not public-entrypoint wiring")
        approver: Callable[[Any], Any] | None
        key: bytes | None = signer.public_bytes
        if approver_kind == "missing":
            approver, key = None, None
        elif approver_kind == "deny":
            approver = _deny_approver(signer)
        elif approver_kind == "boolean":
            approver = _boolean_approver
        elif approver_kind == "stale":
            approver = _stale_approver(signer)
        elif approver_kind == "foreign":
            approver = _foreign_approver()
        elif approver_kind == "valid_signed":
            approver = _valid_approver(signer)
        else:
            raise ValueError(f"unknown approver kind {approver_kind!r}")
        result, _model = run_session(
            workspace,
            store_path=store_path,
            label=label,
            approver=approver,
            approval_key=key,
            run_id=f"t137-{label}",
        )
        run_id = f"t137-{label}"
        terminal_outcome = str(getattr(result, "outcome", None)
                               or getattr(getattr(result, "terminal", None), "value", "")
                               or "unknown")
        terminal_detail = str(getattr(result, "detail", "") or "")
        telemetry = getattr(result, "telemetry", None)
        spent_raw = getattr(telemetry, "spent_usd_micros", None) if telemetry else None
        spent = int(spent_raw) if spent_raw is not None else 0

    candidate, oracle, _files, changed, ledger, writes = _observe(
        workspace, store_path, run_id, receipt, preimage, preimage_files)
    mutated = candidate != preimage
    kinds = tuple(str(row.get("kind") or "") for row in ledger)
    seam, evidence = _attribute(
        path=path, interactive=interactive, policy=policy,
        approver_kind=approver_kind, mutated=mutated,
        expected_landed=expected_landed, ledger_kinds=kinds,
        candidate=candidate, oracle=oracle,
    )
    if spent not in (None, 0):
        notes.append(f"nonzero spentUsdMicros={spent}")
    return ProbeCase(
        label=label,
        path=path,
        interactive=interactive,
        policy=policy,
        approver_kind=approver_kind,
        mutated=mutated,
        changed_files=changed,
        preimage_digest=preimage,
        candidate_digest=candidate,
        oracle_digest=oracle,
        write_effects=writes,
        spent_usd_micros=spent,
        terminal_outcome=terminal_outcome,
        terminal_detail=terminal_detail,
        run_id=run_id,
        ledger_kinds=kinds,
        seam=seam,
        seam_evidence=evidence,
        notes=tuple(notes),
    )


def run_resume_duplicate_check(root: Path, valid: ProbeCase) -> dict[str, Any]:
    """Resume the valid signed run; a second tape must not duplicate the write."""
    workspace = root / valid.label / "ws"
    store_path = root / valid.label / "events.sqlite3"
    before = tree_digest(workspace)
    before_writes = valid.write_effects
    signer = _approvals().OperatorSigner()
    result, _model = run_session(
        workspace,
        store_path=store_path,
        label=f"{valid.label}-resume",
        approver=_valid_approver(signer),
        approval_key=signer.public_bytes,
        run_id=valid.run_id or f"t137-{valid.label}",
        bodies=write_tape(),
        rematerialize=False,
    )
    after = tree_digest(workspace)
    oracle, _ = exterior_oracle_digest(workspace)
    ledger = read_ledger(store_path, str(valid.run_id or ""))
    writes = _write_effect_count(ledger)
    duplicated = after != before and writes > before_writes
    return {
        "runId": valid.run_id,
        "preResumeDigest": before,
        "postResumeDigest": after,
        "oracleDigest": oracle,
        "writeEffectsBefore": before_writes,
        "writeEffectsAfter": writes,
        "duplicated": duplicated,
        "terminalOutcome": str(getattr(result, "outcome", "") or ""),
        "note": "resume must not apply a second privileged write of the same candidate",
    }


def run_matrix(root: Path) -> list[ProbeCase]:
    """DIR-P matrix. Public path is unchanged; session-bound is labeled."""
    cells = [
        ("pub-allow-missing", PATH_PUBLIC, False, "allow", "missing", True),
        ("pub-require-missing", PATH_PUBLIC, True, "require", "missing", False),
        ("sess-require-missing", PATH_SESSION, True, "require", "missing", False),
        ("sess-require-deny", PATH_SESSION, True, "require", "deny", False),
        ("sess-require-boolean", PATH_SESSION, True, "require", "boolean", False),
        ("sess-require-stale", PATH_SESSION, True, "require", "stale", False),
        ("sess-require-foreign", PATH_SESSION, True, "require", "foreign", False),
        ("sess-require-valid", PATH_SESSION, True, "require", "valid_signed", True),
    ]
    return [
        run_case(
            root,
            label=label,
            path=path,
            interactive=interactive,
            policy=policy,
            approver_kind=kind,
            expected_landed=expected,
        )
        for label, path, interactive, policy, kind, expected in cells
    ]


def instrument_controls_passed(cases: list[ProbeCase]) -> bool:
    by_label = {c.label: c for c in cases}
    positive = by_label.get("sess-require-valid")
    negative = by_label.get("sess-require-deny")
    public_cold = by_label.get("pub-require-missing")
    if positive is None or negative is None or public_cold is None:
        return False
    landed = (
        positive.mutated
        and set(positive.changed_files) == set(EXPECTED_WRITE)
        and positive.candidate_digest == positive.oracle_digest
        and positive.seam == SEAM_VALID_SIGNED
    )
    denied = (not negative.mutated) and negative.seam == SEAM_EXPLICIT_DENIAL
    # The public cold path is a *finding*, not an instrument control: the
    # instrument is valid if the session-bound signed write can land and a
    # denial cannot. Public missing-approver is attributed separately.
    return landed and denied and (public_cold.spent_usd_micros in (None, 0))


def first_seam(cases: list[ProbeCase], *, controls_ok: bool) -> str:
    if not controls_ok:
        return SEAM_INSTRUMENT
    public_cold = next(c for c in cases if c.label == "pub-require-missing")
    return public_cold.seam


def _digest_of(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def run_all(root: Path | None = None) -> dict[str, Any]:
    """Run the matrix, resume check, and emit the T-137 packet."""
    cleanup = None
    if root is None:
        cleanup = tempfile.TemporaryDirectory(prefix="t137-")
        root = Path(cleanup.name)
    try:
        cases = run_matrix(root)
        controls_ok = instrument_controls_passed(cases)
        valid = next(c for c in cases if c.label == "sess-require-valid")
        try:
            resume = run_resume_duplicate_check(root, valid) if controls_ok else {
                "skipped": True, "reason": "instrument controls failed"}
        except Exception as exc:  # noqa: BLE001 — diagnostic packet must still emit
            resume = {
                "skipped": False,
                "error": f"{type(exc).__name__}: {exc}",
                "duplicated": False,
                "note": "resume probe errored; not interpreted as a clean no-duplicate",
            }
        seam = first_seam(cases, controls_ok=controls_ok)
        traces = [c.to_dict() for c in cases]
        packet = {
            "schema": "t137.approval-path-probe/1",
            "subject": {
                "fixture": FIXTURE_ID,
                "preset": PRESET,
                "expectedWrite": dict(EXPECTED_WRITE),
                "publicRoute": "entrypoint.execute via benchmarks.product_path.execute_product",
                "sessionRoute": "Runtime.execute_profiled with explicit approver/approval_key",
            },
            "config": {
                "interactiveFalsePolicy": "allow — vg-code-balanced threshold=standard in benchmark mode",
                "interactiveTruePolicy": "require — assisted mode fail-closed; missing approver is refusal",
                "zeroUsd": True,
                "repairAuthorized": False,
            },
            "controls": {
                "passed": controls_ok,
                "positive": "sess-require-valid",
                "negative": "sess-require-deny",
            },
            "traces": traces,
            "traceDigest": _digest_of(traces),
            "resume": resume,
            "firstSeam": seam,
            "infrastructure": {
                "providerCalls": 0,
                "spentUsdMicros": 0,
                "model": "ProviderTapeModel",
            },
            "unresolved": _unresolved(cases, seam, resume, controls_ok),
        }
        packet["configDigest"] = _digest_of(packet["config"])
        packet["subjectDigest"] = _digest_of(packet["subject"])
        return packet
    finally:
        if cleanup is not None:
            cleanup.cleanup()


def _unresolved(
    cases: list[ProbeCase], seam: str, resume: Mapping[str, Any], controls_ok: bool,
) -> list[str]:
    notes: list[str] = []
    if not controls_ok:
        notes.append("instrument controls failed; no product finding is licensed")
    if seam == SEAM_MISSING_APPROVER:
        notes.append(
            "cold public-entrypoint seam reproduced: missing approver refuses "
            "suspension. RUN-13 remains open; this is not a repair lease")
    if seam == SEAM_DEFAULT_ALLOW:
        notes.append(
            "missing approver became default-allow on the public path; "
            "return a named delta, do not repair in this row")
    if seam == SEAM_NOT_REPRODUCED:
        notes.append("approval suspension path was not exercised; RUN-13 stays open")
    if resume.get("duplicated"):
        notes.append("resume duplicated a privileged write")
    if any(c.spent_usd_micros not in (None, 0) for c in cases):
        notes.append("nonzero USD observed — RUN-12 violation")
    return notes


def main(argv: list[str] | None = None) -> int:
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    out = Path(args[0]) if args else ROOT / ".draft" / "logs" / "C_T-137_packet.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    packet = run_all()
    out.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "packet": str(out),
        "firstSeam": packet["firstSeam"],
        "controls": packet["controls"]["passed"],
        "traceDigest": packet["traceDigest"],
        "unresolved": packet["unresolved"],
    }, indent=2))
    return 0 if packet["controls"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

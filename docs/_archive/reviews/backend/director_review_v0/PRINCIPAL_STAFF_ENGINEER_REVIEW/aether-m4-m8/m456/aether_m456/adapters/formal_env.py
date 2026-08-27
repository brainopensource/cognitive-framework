"""M-5 formal environment adapter. Same EnvironmentAdapter port as Git.
Nothing under domain/ kernel/ ports/ runtime/ agency/episode/ changes."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from typing import Any, Mapping
from ..runtime.memo import digest_of, memo_key, WitnessMemo, MemoEntry

UNAVAILABLE = None  # explicit missingness carries a reason, never a fake zero

@dataclass(frozen=True, slots=True)
class Cost:
    usd_micros: int = 0
    millis: int = 0
    tokens: Any = UNAVAILABLE
    tokens_reason: str = "not_a_model_call"

@dataclass(frozen=True, slots=True)
class Receipt:
    verb: str
    outcome: str
    result_digest: str
    artifacts: Mapping[str, bytes]
    cost: Cost
    memo_hit: bool = False

class FormalEnvironment:
    """kind='formal'. Verbs mirror the coding pack's sink taxonomy:
       formal.check = observation (read-only, no workspace mutation)
       proof.emit   = privileged  (writes a witness -> needs a grant)"""
    kind = "formal"

    def __init__(self, solver, *, checker_identity: str, toolchain: str,
                 memo: WitnessMemo | None = None) -> None:
        self._solver, self._memo = solver, memo or WitnessMemo()
        self._checker, self._toolchain = checker_identity, toolchain

    def execute(self, req, ctx) -> Receipt:
        if req.verb == "formal.check":
            key = memo_key(obligation=req.args["goal"],
                           input_digests=sorted(req.args.get("inputs", [])),
                           environment_digest=ctx.environment_digest,
                           checker_identity=self._checker,
                           toolchain_version=self._toolchain,
                           assurance_level=ctx.assurance_level,
                           policy_version=ctx.policy_version)
            if hit := self._memo.get(key):
                # narrows WORK, not authority: still returns through the
                # same receipt path and is still checked exteriorly.
                return Receipt("formal.check", hit.outcome, hit.witness_digest,
                               {}, Cost(millis=0), memo_hit=True)
            r = self._solver.solve(req.args["goal"])
            wd = digest_of({"proof": r.proof.decode("utf-8", "replace")})
            self._memo.put(key, MemoEntry(wd, ctx.run_id, r.status))
            return Receipt("formal.check", r.status, wd,
                           {"proof": r.proof}, Cost(millis=r.millis))

        if req.verb == "proof.emit":
            blob = req.args["witness"].encode()
            return Receipt("proof.emit", "ok", digest_of({"w": req.args["witness"]}),
                           {"witness": blob}, Cost(millis=1))
        return Receipt(req.verb, "failed", "", {}, Cost(), )

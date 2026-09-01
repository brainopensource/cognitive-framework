"""Attributable stochastic ModelPort adapter (`WP-B2`).

Implements an attributable, stochastic-yet-reproducible model adapter for the
M-6.5 paired study.

Invariants:
- Common-random perturbation key:
    `H(task_manifest_digest, environment_seed, checkpoint, attempt_ordinal, perturbation)`
- Key binds to `SemanticCheckpointRef(run_id, episode_id, epoch, attempt)`, NEVER raw turn index.
- Same-key replay: identical key and inputs produce byte-identical proposals.
- Interior variance: changing seeds or tasks produces stochastic variance.
- Elicits 4 recoverable block types (context_deficit, plan_stalemate, hypothesis_loop, verification_gap).
- Valid, non-degenerate A/A noise floor under pure stochasticity.
- Fails closed with typed instrument errors, zero ambient I/O or network.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...domain.ledger.progress import SemanticCheckpointRef
from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .invocation import ProposalTranslator

__all__ = [
    "RECOVERABLE_BLOCK_TYPES",
    "StochasticModelAdapter",
    "perturbation_key",
    "pseudo_random_float",
]

RECOVERABLE_BLOCK_TYPES = frozenset({
    "context_deficit",
    "plan_stalemate",
    "hypothesis_loop",
    "verification_gap",
})

_DEFAULT_ALIASES = {
    "read": "fs.read",
    "search": "fs.search",
    "patch": "patch.apply",
    "test": "proc.exec",
    "view_file": "fs.read",
    "grep_file": "fs.search",
    "edit_file": "patch.apply",
    "run_command": "proc.exec",
}


def perturbation_key(
    task_manifest_digest: str,
    environment_seed: int | str,
    checkpoint: SemanticCheckpointRef | Mapping[str, Any] | str,
    attempt_ordinal: int = 0,
    perturbation: str | Mapping[str, Any] = "",
) -> str:
    """Derive common-random perturbation key from task, seed, checkpoint, attempt, perturbation.

    `ADR-0103`: binds to SemanticCheckpointRef (run_id, episode_id, epoch, attempt),
    NEVER to raw turn index.
    """
    if isinstance(checkpoint, SemanticCheckpointRef):
        checkpoint_val = checkpoint.to_dict()
    elif isinstance(checkpoint, Mapping):
        checkpoint_val = dict(checkpoint)
    else:
        checkpoint_val = str(checkpoint)

    body = {
        "taskManifestDigest": task_manifest_digest,
        "environmentSeed": str(environment_seed),
        "checkpoint": checkpoint_val,
        "attemptOrdinal": attempt_ordinal,
        "perturbation": perturbation if not isinstance(perturbation, Mapping) else dict(perturbation),
    }
    return digest_of(body)


def pseudo_random_float(key_digest: str, salt: str = "") -> float:
    """Generate a deterministic float in [0.0, 1.0) from a sha256 hex digest."""
    h = hashlib.sha256((key_digest + ":" + salt).encode("utf-8")).hexdigest()
    val = int(h[:12], 16)
    return val / float(0xFFFFFFFFFFFF)


_pseudo_random_float = pseudo_random_float


class StochasticModelAdapter:
    """Stochastic attributable ModelPort adapter for M-6.5 paired evaluation."""

    pseudo_random_float = staticmethod(pseudo_random_float)


    def __init__(
        self,
        *,
        model_name: str = "stochastic/m65-v1",
        task_manifest_digest: str = "sha256:task-default",
        environment_seed: int = 42,
        checkpoint: SemanticCheckpointRef | None = None,
        attempt_ordinal: int = 0,
        perturbation: str = "",
        block_type: str | None = None,
        baseline_success_prob: float = 0.5,
    ) -> None:
        self.model_name = model_name
        self.task_manifest_digest = task_manifest_digest
        self.environment_seed = environment_seed
        self.checkpoint = checkpoint or SemanticCheckpointRef(
            run_id=f"run-{environment_seed}",
            episode_id=f"ep-{environment_seed}",
            epoch=0,
            attempt=attempt_ordinal,
        )
        self.attempt_ordinal = attempt_ordinal
        self.perturbation = perturbation
        self.block_type = block_type if block_type in RECOVERABLE_BLOCK_TYPES else None
        self.baseline_success_prob = baseline_success_prob
        self.is_deterministic = False

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas = (),
        sampling: Sampling = {},
    ) -> Result[Proposal]:
        del sampling
        # Extract directive or strategy context if present in context
        directive_kind = self._detect_directive(context)
        
        pkey = perturbation_key(
            self.task_manifest_digest,
            self.environment_seed,
            self.checkpoint,
            self.attempt_ordinal,
            self.perturbation,
        )

        r_outcome = _pseudo_random_float(pkey, "outcome")
        r_cost = _pseudo_random_float(pkey, "cost")
        r_tool = _pseudo_random_float(pkey, "tool")

        # Check block resolution:
        # If task has a block, resolving it requires the corresponding meta-controller directive.
        unblocked = False
        if self.block_type is None:
            # Ordinary stochastic task
            unblocked = True
            success_threshold = self.baseline_success_prob
        elif self.block_type == "context_deficit":
            # Recovers on request_context
            if directive_kind == "request_context":
                unblocked = True
                success_threshold = 0.85
            else:
                success_threshold = 0.15
        elif self.block_type == "plan_stalemate":
            # Recovers on revise_plan
            if directive_kind == "revise_plan":
                unblocked = True
                success_threshold = 0.85
            else:
                success_threshold = 0.15
        elif self.block_type == "hypothesis_loop":
            # Recovers on abandon_hypothesis
            if directive_kind == "abandon_hypothesis":
                unblocked = True
                success_threshold = 0.85
            else:
                success_threshold = 0.15
        elif self.block_type == "verification_gap":
            # Recovers on change_verification
            if directive_kind == "change_verification":
                unblocked = True
                success_threshold = 0.85
            else:
                success_threshold = 0.15
        else:
            success_threshold = self.baseline_success_prob

        succeeds = r_outcome < success_threshold

        # Derive proposal structure deterministically
        usd_micros = int(100 + r_cost * 150)
        tool_call_id = f"call_{pkey[:8]}"

        if succeeds:
            raw_proposal: dict[str, Any] = {
                "text": "Applying verified patch for task solution.",
                "toolCalls": [{
                    "id": tool_call_id,
                    "name": "edit_file",
                    "arguments": {
                        "path": "src/solution.py",
                        "patch": "--- a/src/solution.py\n+++ b/src/solution.py\n@@ -1 +1 @@\n-VALUE = 0\n+VALUE = 1\n",
                    },
                }],
                "resolved_model": self.model_name,
                "pricing_known": True,
                "usd_micros": usd_micros,
            }
        else:
            # Generate a failing / repeat / stalled proposal
            tool_name = "grep_file" if r_tool < 0.5 else "edit_file"
            raw_proposal = {
                "text": f"Exploring workspace under {self.block_type or 'stochastic noise'}.",
                "toolCalls": [{
                    "id": tool_call_id,
                    "name": tool_name,
                    "arguments": {
                        "path": "src/solution.py",
                        "pattern": "TODO" if tool_name == "grep_file" else "invalid",
                        "patch": "--- a/src/solution.py\n+++ b/src/solution.py\n@@ -1 +1 @@\n-VALUE = 0\n+VALUE = 0\n",
                    },
                }],
                "resolved_model": self.model_name,
                "pricing_known": True,
                "usd_micros": usd_micros,
            }

        return ProposalTranslator.translate(
            raw_proposal,
            tool_schemas=tools,
            aliases=_DEFAULT_ALIASES,
        )

    def _detect_directive(self, context: ContextBundle) -> str | None:
        """Inspect context messages for strategy directives."""
        texts: list[str] = []
        if isinstance(context, Mapping):
            layers = context.get("layers") or ()
            for l in layers:
                if isinstance(l, Mapping):
                    texts.append(str(l.get("content", "")))
            msgs = context.get("messages") or ()
            for m in msgs:
                if isinstance(m, Mapping):
                    texts.append(str(m.get("content", "")))
        elif isinstance(context, Sequence) and not isinstance(context, (str, bytes)):
            for m in context:
                if isinstance(m, Mapping):
                    texts.append(str(m.get("content", "")))
                else:
                    texts.append(str(m))
        else:
            texts.append(str(context))

        combined = " ".join(texts).lower()
        for kind in ("request_context", "revise_plan", "abandon_hypothesis", "change_verification", "delegate", "conclude"):
            if kind in combined:
                return kind
        return None

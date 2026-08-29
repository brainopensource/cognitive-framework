"""Response Handler & Telemetry Normalizer (EVO-06, GTS-13C §7.4, ADR-0096 §14.1).

Normalizes raw model provider responses, records model I/O provenance and cache participation,
and extracts usage metrics (tokens, usd_micros, ttft_millis).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..agency.provenance import ProvenanceSink
from .artifacts import ArtifactWriter
from .provenance import cache_participation

__all__ = [
    "ResponseHandler",
]


def _route_of(model: Any) -> Mapping[str, Any]:
    """Which provider/model this call actually went to.

    Small and identity-only: a route that carried credentials or headers
    would put them in an append-only store.
    """
    return {
        "adapter": type(model).__name__,
        "provider": str(getattr(model, "provider", "")),
        "model": str(getattr(model, "model", getattr(model, "model_name", getattr(model, "_model", "")))),
        "mode": str(getattr(model, "mode", getattr(model, "_mode", ""))),
    }


class ResponseHandler:
    """Handles raw provider proposals and extracts telemetry and provenance."""

    def __init__(
        self,
        model: Any,
        *,
        provenance: ProvenanceSink | None = None,
        artifacts: ArtifactWriter | None = None,
    ) -> None:
        self._model = model
        self._provenance = provenance
        self._artifacts = artifacts

    def handle(
        self,
        answer: Any,
        turn: int,
        context_record: Mapping[str, Any],
        *,
        input_ref: Any = None,
        output_ref: Any = None,
    ) -> dict[str, Any]:
        """Process model answer, update context record, and record provenance."""
        stamped = dict(context_record)
        if input_ref is not None and getattr(input_ref, "digest", None):
            stamped["model_input_ref"] = input_ref.digest
        if output_ref is not None and getattr(output_ref, "digest", None):
            stamped["model_output_ref"] = output_ref.digest

        value = getattr(answer, "value", None)
        raw = value if value is not None else answer

        if self._provenance is not None and hasattr(self._provenance, "record_model_io"):
            policy = self._artifacts.policy.identity() if self._artifacts is not None else {}
            self._provenance.record_model_io(
                route=_route_of(self._model),
                input_ref=input_ref,
                output_ref=output_ref,
                capture_policy=policy,
                turn=turn,
            )
            self._provenance.record_cache(
                reported=cache_participation(value),
                turn=turn,
                source_digest=output_ref.digest if output_ref else "",
            )

        if isinstance(value, Mapping):
            usage = value.get("usage")
            if isinstance(usage, Mapping):
                for key in ("prompt_tokens", "completion_tokens", "usd_micros", "ttft_millis"):
                    reported = usage.get(key)
                    if isinstance(reported, int) and not isinstance(reported, bool):
                        stamped[key] = reported
                stamped["provider_usage_reported"] = True

            resolved = value.get("resolved_model")
            if isinstance(resolved, str) and resolved:
                stamped["model"] = resolved

            fingerprint = value.get("model_fingerprint")
            if isinstance(fingerprint, str) and fingerprint:
                stamped["model_fingerprint"] = fingerprint

        return stamped

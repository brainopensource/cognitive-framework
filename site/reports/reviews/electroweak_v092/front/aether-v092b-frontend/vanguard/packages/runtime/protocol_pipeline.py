"""Composition-root factory for the protocol-recovery pipeline (`ADR-0106 §3`).

Agency must never import pack middleware directly — the dependency direction
is `packs -> runtime -> agency`. This module is the one place that knows both
sides: it adapts the pack's pure dialect decoders onto the
`ProposalDecoderProtocol` seam the episode engine consumes, and degrades to an
empty pipeline when the pack is absent so the engine stays operational.
"""
from __future__ import annotations

from typing import Any, Mapping

from vanguard.packages.domain.transforms.contracts import ProposalDecoderProtocol


class _FnDecoder:
    """Adapt a plain decode function onto `ProposalDecoderProtocol`."""

    def __init__(self, fn: Any) -> None:
        self._fn = fn

    def decode(self, raw: object) -> Mapping[str, object] | None:
        return self._fn(raw)


def _decode_dsml_from_raw(raw: object) -> Mapping[str, object] | None:
    import importlib

    module = importlib.import_module(
        "packs.code-default.middleware.protocol.dsml_decoder")
    decode_dsml_markup = module.decode_dsml_markup

    text = raw if isinstance(raw, str) else ""
    if not text and isinstance(raw, Mapping):
        text = str(raw.get("content") or raw.get("text") or "")
    return decode_dsml_markup(text)


def _patch_detector_fn(text: str) -> Any:
    import importlib

    module = importlib.import_module(
        "packs.code-default.middleware.protocol.markdown_patch_detector")
    return module.detect_markdown_patch(text)


def _truncation_detector_fn(raw: object) -> bool:
    import importlib

    module = importlib.import_module(
        "packs.code-default.middleware.protocol.truncation_detector")
    return bool(module.detect_truncation(raw))


def _load(name: str, fn_name: str) -> Any:
    try:
        import importlib

        module = importlib.import_module(name)
        return getattr(module, fn_name)
    except Exception:
        return None


def default_protocol_pipeline() -> tuple[tuple[ProposalDecoderProtocol, ...], Any, Any]:
    """Return `(decoders, patch_detector, truncation_detector)` for the engine.

    Native tool-call decoding is attempted first, then DSML markup as a
    compatibility path (`ADR-0106 §3`). Missing pack modules degrade to an
    empty pipeline instead of failing composition.
    """
    decoders: list[ProposalDecoderProtocol] = []
    native_fn = _load(
        "packs.code-default.middleware.protocol.native_tool_call_decoder",
        "decode_native_tool_call")
    if native_fn is not None:
        decoders.append(_FnDecoder(native_fn))
    if _load("packs.code-default.middleware.protocol.dsml_decoder",
             "decode_dsml_markup") is not None:
        decoders.append(_FnDecoder(_decode_dsml_from_raw))
    patch_fn = _load(
        "packs.code-default.middleware.protocol.markdown_patch_detector",
        "detect_markdown_patch")
    patch_detector = _patch_detector_fn if patch_fn is not None else None
    trunc_fn = _load(
        "packs.code-default.middleware.protocol.truncation_detector",
        "detect_truncation")
    truncation_detector = _truncation_detector_fn if trunc_fn is not None else None
    return tuple(decoders), patch_detector, truncation_detector
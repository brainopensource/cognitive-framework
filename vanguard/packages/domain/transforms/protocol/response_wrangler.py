"""Modular LLM Response Wrangler and Protocol Decoders.

Enforces protocol recovery and proposal normalization across provider formats (DSML,
Markdown unified diffs, unescaped JSON tool arguments, and raw content blocks).
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class WrangleResult:
    """Standardized output from response wrangling."""

    text: str
    tool_calls: tuple[dict[str, Any], ...]
    classification: str
    diagnostics: tuple[str, ...] = ()
    candidate_diff: str | None = None


class DecoderPlugin:
    """Base class for pluggable LLM response decoders."""

    name: str = "base"

    def decode(self, text: str, existing_calls: Sequence[dict[str, Any]]) -> WrangleResult | None:
        return None


class DSMLDecoderPlugin(DecoderPlugin):
    """Decoder for DeepSeek DSML markup tags (<｜DSML｜tool_calls> and <tool_call>)."""

    name = "dsml"
    DSML_REGEX = re.compile(
        r"<｜DSML｜tool_calls>(.*?)(?:</｜DSML｜tool_calls>|<｜DSML｜end_tool_calls>|$)",
        re.DOTALL,
    )
    XML_TOOL_REGEX = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
    CALL_NAME_REGEX = re.compile(r"<call:([a-zA-Z0-9_.]+)\s*(?:\{.*?\})?>", re.DOTALL)

    def decode(self, text: str, existing_calls: Sequence[dict[str, Any]]) -> WrangleResult | None:
        if not text:
            return None

        extracted_calls: list[dict[str, Any]] = list(existing_calls)
        clean_text = text
        found = False

        # Match DSML block
        dsml_match = self.DSML_REGEX.search(clean_text)
        if dsml_match:
            block = dsml_match.group(1).strip()
            clean_text = self.DSML_REGEX.sub("", clean_text).strip()
            found = True
            try:
                calls_data = json.loads(block)
                if isinstance(calls_data, list):
                    for idx, item in enumerate(calls_data):
                        if isinstance(item, dict):
                            name = item.get("name") or item.get("verb")
                            args = item.get("arguments") or item.get("args") or {}
                            if name:
                                extracted_calls.append({
                                    "id": f"dsml_{idx}",
                                    "type": "function",
                                    "function": {"name": str(name), "arguments": json.dumps(args) if isinstance(args, dict) else str(args)},
                                })
            except Exception:
                pass

        # Match XML <tool_call> tags
        for idx, match in enumerate(self.XML_TOOL_REGEX.finditer(clean_text)):
            found = True
            raw_payload = match.group(1).strip()
            try:
                payload = json.loads(raw_payload)
                name = payload.get("name") or payload.get("verb")
                args = payload.get("arguments") or payload.get("args") or {}
                if name:
                    extracted_calls.append({
                        "id": f"xml_tool_{idx}",
                        "type": "function",
                        "function": {"name": str(name), "arguments": json.dumps(args) if isinstance(args, dict) else str(args)},
                    })
            except Exception:
                pass

        if found:
            clean_text = self.XML_TOOL_REGEX.sub("", clean_text).strip()
            return WrangleResult(
                text=clean_text,
                tool_calls=tuple(extracted_calls),
                classification="dsml_decoded",
            )
        return None


class MarkdownPatchDecoderPlugin(DecoderPlugin):
    """Decoder extracting inline Markdown diff blocks into synthetic patch.apply tool calls."""

    name = "markdown_patch"
    DIFF_BLOCK_REGEX = re.compile(
        r"```(?:diff|patch)\n(--- [^\n]+\n\+\+\+ [^\n]+\n@@ [^\n]+ @@.*?)```",
        re.DOTALL,
    )
    FILE_DIFF_HEADER_REGEX = re.compile(r"--- ([^\n]+)\n\+\+\+ ([^\n]+)\n@@")

    def decode(self, text: str, existing_calls: Sequence[dict[str, Any]]) -> WrangleResult | None:
        if not text or existing_calls:
            return None

        diff_matches = self.DIFF_BLOCK_REGEX.findall(text)
        if not diff_matches:
            return None

        full_diff = "\n\n".join(diff_matches)
        extracted_calls = list(existing_calls)

        # Map to synthetic patch.apply tool call
        extracted_calls.append({
            "id": "synthetic_patch_0",
            "type": "function",
            "function": {
                "name": "patch.apply",
                "arguments": json.dumps({"patch": full_diff}),
            },
        })

        clean_text = self.DIFF_BLOCK_REGEX.sub("", text).strip()
        return WrangleResult(
            text=clean_text,
            tool_calls=tuple(extracted_calls),
            classification="markdown_patch_extracted",
            candidate_diff=full_diff,
        )


class JSONArgumentNormalizerPlugin(DecoderPlugin):
    """Normalizes unescaped string arguments, single quotes, or truncation in tool call JSON."""

    name = "json_normalizer"

    @staticmethod
    def normalize_arguments(args_raw: Any) -> dict[str, Any]:
        if isinstance(args_raw, dict):
            return args_raw
        if not isinstance(args_raw, str) or not args_raw.strip():
            return {}

        text = args_raw.strip()

        # Attempt 1: Strict json.loads
        try:
            val = json.loads(text)
            if isinstance(val, dict):
                return val
        except Exception:
            pass

        # Attempt 2: Non-strict json.loads
        try:
            val = json.loads(text, strict=False)
            if isinstance(val, dict):
                return val
        except Exception:
            pass

        # Attempt 3: ast.literal_eval
        try:
            val = ast.literal_eval(text)
            if isinstance(val, dict):
                return val
        except Exception:
            pass

        # Attempt 4: Clean control characters and unescaped newlines in JSON string literals
        try:
            sanitized = re.sub(r'(?<!\\)\n', r'\\n', text)
            val = json.loads(sanitized, strict=False)
            if isinstance(val, dict):
                return val
        except Exception:
            pass

        return {}


class ResponseWrangler:
    """Configurable pipeline for decoding, sanitizing, and normalizing model output."""

    def __init__(self, decoders: Sequence[DecoderPlugin] | None = None) -> None:
        self.decoders = tuple(decoders) if decoders is not None else (
            DSMLDecoderPlugin(),
            MarkdownPatchDecoderPlugin(),
            JSONArgumentNormalizerPlugin(),
        )

    def wrangle(
        self,
        text: str,
        tool_calls: Sequence[dict[str, Any]] = (),
    ) -> WrangleResult:
        current_text = text or ""
        current_calls: list[dict[str, Any]] = []

        # 1. Normalize existing tool call arguments
        for call in tool_calls:
            if not isinstance(call, dict):
                continue
            normalized_call = dict(call)
            func = dict(normalized_call.get("function") or {})
            if "arguments" in func:
                raw_args = func["arguments"]
                args_dict = JSONArgumentNormalizerPlugin.normalize_arguments(raw_args)
                func["arguments"] = json.dumps(args_dict)
                normalized_call["function"] = func
            current_calls.append(normalized_call)

        classification = "native"
        candidate_diff: str | None = None

        # 2. Pass through decoder plugins sequentially
        for decoder in self.decoders:
            res = decoder.decode(current_text, current_calls)
            if res is not None:
                current_text = res.text
                current_calls = list(res.tool_calls)
                classification = res.classification
                if res.candidate_diff:
                    candidate_diff = res.candidate_diff

        return WrangleResult(
            text=current_text,
            tool_calls=tuple(current_calls),
            classification=classification,
            candidate_diff=candidate_diff,
        )

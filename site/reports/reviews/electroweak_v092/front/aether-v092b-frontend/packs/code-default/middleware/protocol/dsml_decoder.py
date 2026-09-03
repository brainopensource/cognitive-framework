"""Decodes DSML and XML function call markup into normalized proposal dictionaries."""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

_DSML_PATTERN = re.compile(
    r"<invoke\s+name=[\"']([^\"']+)[\"']\s*>(.*?)</invoke>",
    re.DOTALL,
)
_FUNCTION_TAG_PATTERN = re.compile(
    r"<function=[\"']?([^\"'>\s]+)[\"']?\s*>(.*?)</function>",
    re.DOTALL,
)
_ARG_PATTERN = re.compile(
    r"<parameter\s+name=[\"']([^\"']+)[\"']\s*>(.*?)</parameter>",
    re.DOTALL,
)


def decode_dsml_markup(text: str) -> Mapping[str, Any] | None:
    """Parse DSML or XML-style invocation markup into a canonical proposal."""
    if not isinstance(text, str) or ("<invoke" not in text and "<function=" not in text):
        return None

    # Check <invoke name="...">...</invoke>
    match = _DSML_PATTERN.search(text)
    if match:
        action = match.group(1).strip()
        body = match.group(2).strip()
        args: dict[str, Any] = {}
        # Check for sub-parameters
        param_matches = list(_ARG_PATTERN.finditer(body))
        if param_matches:
            for p in param_matches:
                p_name = p.group(1).strip()
                p_val = p.group(2).strip()
                try:
                    args[p_name] = json.loads(p_val)
                except Exception:
                    args[p_name] = p_val
        else:
            try:
                parsed_body = json.loads(body)
                if isinstance(parsed_body, Mapping):
                    args = dict(parsed_body)
                else:
                    args = {"content": parsed_body}
            except Exception:
                if body:
                    args = {"content": body}
        return {
            "kind": "effect",
            "action": action,
            "args": args,
            "note": "recovered_from_dsml",
        }

    # Check <function=name>body</function>
    fn_match = _FUNCTION_TAG_PATTERN.search(text)
    if fn_match:
        action = fn_match.group(1).strip()
        body = fn_match.group(2).strip()
        try:
            parsed = json.loads(body)
            args = dict(parsed) if isinstance(parsed, Mapping) else {"content": parsed}
        except Exception:
            args = {"content": body} if body else {}
        return {
            "kind": "effect",
            "action": action,
            "args": args,
            "note": "recovered_from_function_tag",
        }

    return None

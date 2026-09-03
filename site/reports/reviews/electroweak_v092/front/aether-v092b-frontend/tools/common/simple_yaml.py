"""Minimal YAML 1.1 subset (block maps/lists + scalars). Stdlib only."""

from __future__ import annotations

from typing import Any

__all__ = ["YamlError", "load"]


class YamlError(ValueError):
    pass


def load(text: str) -> Any:
    lines = _preprocess(text)
    if not lines:
        return {}
    value, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise YamlError("trailing YAML content")
    return value


def _preprocess(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for raw in text.splitlines():
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped:
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        out.append((indent, stripped[indent:]))
    return out


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    _, content = lines[index]
    if content.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_map(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        current, content = lines[index]
        if current < indent:
            break
        if current > indent:
            raise YamlError(f"unexpected indent at {content!r}")
        if content.startswith("- "):
            break
        if ":" not in content:
            raise YamlError(f"expected mapping at {content!r}")
        key, rest = content.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        index += 1
        if rest:
            result[key] = _scalar(rest)
            continue
        if index < len(lines) and lines[index][0] > indent:
            child, index = _parse_block(lines, index, lines[index][0])
            result[key] = child
        else:
            result[key] = None
    return result, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        current, content = lines[index]
        if current < indent:
            break
        if current > indent:
            raise YamlError(f"unexpected indent at {content!r}")
        if not content.startswith("- "):
            break
        item = content[2:].strip()
        index += 1
        if not item:
            if index < len(lines) and lines[index][0] > indent:
                child, index = _parse_block(lines, index, lines[index][0])
                result.append(child)
            else:
                result.append(None)
            continue
        if item.endswith(":") and not item.startswith("{"):
            key = item[:-1].strip()
            nested: dict[str, Any] = {}
            if index < len(lines) and lines[index][0] > indent:
                child, index = _parse_block(lines, index, lines[index][0])
                nested[key] = child
            else:
                nested[key] = None
            result.append(nested)
            continue
        if ":" in item and not item.startswith("{") and not item.startswith("["):
            key, rest = item.split(":", 1)
            entry: dict[str, Any] = {key.strip(): _scalar(rest.strip())}
            while index < len(lines) and lines[index][0] > indent and not lines[index][1].startswith("- "):
                extra, index = _parse_map(lines, index, lines[index][0])
                entry.update(extra)
            result.append(entry)
            continue
        result.append(_scalar(item))
    return result, index


def _scalar(text: str) -> Any:
    if text in {"null", "~", ""}:
        return None
    if text in {"true", "True", "yes"}:
        return True
    if text in {"false", "False", "no"}:
        return False
    if text.startswith("'") and text.endswith("'") and len(text) >= 2:
        return text[1:-1]
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        return text[1:-1]
    if text.startswith("{") and text.endswith("}"):
        return _inline_map(text[1:-1])
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_scalar(part.strip()) for part in _split_top(inner)]
    if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
        return int(text)
    return text


def _inline_map(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if not text.strip():
        return result
    for part in _split_top(text):
        if ":" not in part:
            raise YamlError(f"bad inline mapping {text!r}")
        key, rest = part.split(":", 1)
        result[key.strip()] = _scalar(rest.strip())
    return result


def _split_top(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in text:
        if char in "{[":
            depth += 1
        elif char in "}]":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(char)
    if buf:
        parts.append("".join(buf).strip())
    return parts

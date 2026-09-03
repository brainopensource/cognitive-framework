#!/usr/bin/env python3
"""Validate standardized YAML metadata on living repository documentation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

DOC_PATTERNS = (
    "README.md",
    "AGENTS.md",
    "VISION.md",
    "docs/**/*.md",
)

REQUIRED_KEYS = {
    "id",
    "class",
    "authority",
    "canonical_for",
    "status",
    "owner",
    "version",
    "last_verified",
}

VALID_CLASSES = {
    "navigation",
    "law",
    "architecture",
    "decision",
    "execution",
    "standard",
    "archive",
    "contract-reference",
    "protocol-reference",
    "theory",
    "how-to",
    "reference",
    "normative",
    "meta",
    "product",
    "research",
    "report",
    "charter",
}

VALID_AUTHORITIES = {
    "normative",
    "binding-decision",
    "execution",
    "descriptive",
    "advisory",
    "non-canonical",
    "conceptual",
    "constitutional",
    "current-decision-navigation",
    "proposal",
}

VALID_STATUSES = {
    "living",
    "append-only",
    "frozen",
    "superseded",
    "reference",
    "proposal",
    "proposed",
    "experiment",
    "historical-reference",
    "locked",
}

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def discover_living_docs(root: Path) -> list[Path]:
    files: list[Path] = []
    for pat in DOC_PATTERNS:
        files.extend(root.glob(pat))
    return sorted(set(
        f for f in files
        if f.is_file() and "docs/reports/reviews/" not in f.relative_to(root).as_posix()
    ))


def parse_frontmatter(text: str) -> dict[str, object] | None:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    raw = match.group(1)
    data: dict[str, object] = {}
    current_list_key: str | None = None
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- ") and current_list_key:
            item = line[2:].strip().strip('"').strip("'")
            if isinstance(data.get(current_list_key), list):
                data[current_list_key].append(item)  # type: ignore
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
                data[key] = items
                current_list_key = None
            elif not val:
                data[key] = []
                current_list_key = key
            else:
                data[key] = val.strip('"').strip("'")
                current_list_key = None
    return data


def check() -> list[str]:
    errors: list[str] = []
    seen_canonical_topics: dict[str, str] = {}
    seen_ids: dict[str, str] = {}

    docs = discover_living_docs(_ROOT)
    if not docs:
        return ["no living documents discovered to check"]

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        rel = str(doc_path.relative_to(_ROOT))
        if fm is None:
            errors.append(f"{rel}: Missing or malformed YAML frontmatter (must start with '---')")
            continue

        is_non_canonical = fm.get("authority") == "non-canonical"
        if not is_non_canonical:
            missing = REQUIRED_KEYS - set(fm.keys())
            if missing:
                errors.append(f"{rel}: Missing required frontmatter keys: {', '.join(sorted(missing))}")

        doc_id = str(fm.get("id", ""))
        if not doc_id:
            errors.append(f"{rel}: Empty document 'id'")
        elif doc_id in seen_ids:
            errors.append(f"{rel}: Duplicate document id '{doc_id}' (first seen in {seen_ids[doc_id]})")
        else:
            seen_ids[doc_id] = rel

        doc_class = str(fm.get("class", ""))
        if doc_class and doc_class not in VALID_CLASSES:
            errors.append(f"{rel}: Invalid class '{doc_class}'. Must be one of: {sorted(VALID_CLASSES)}")

        doc_auth = str(fm.get("authority", ""))
        if doc_auth not in VALID_AUTHORITIES:
            errors.append(f"{rel}: Invalid authority '{doc_auth}'. Must be one of: {sorted(VALID_AUTHORITIES)}")

        doc_status = str(fm.get("status", ""))
        if doc_status and doc_status not in VALID_STATUSES:
            errors.append(f"{rel}: Invalid status '{doc_status}'. Must be one of: {sorted(VALID_STATUSES)}")

        canonical_for = fm.get("canonical_for")
        if canonical_for is not None and not isinstance(canonical_for, list):
            errors.append(f"{rel}: 'canonical_for' must be a list")
        elif isinstance(canonical_for, list):
            if (doc_class == "archive" or is_non_canonical) and len(canonical_for) > 0:
                errors.append(f"{rel}: Non-canonical or archived documents must claim no canonical topics ('canonical_for' must be empty)")
            for topic in canonical_for:
                if topic in seen_canonical_topics:
                    errors.append(
                        f"{rel}: Duplicate canonical_for topic '{topic}' (already claimed by {seen_canonical_topics[topic]})"
                    )
                else:
                    seen_canonical_topics[topic] = rel

    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"DOC METADATA FAIL: {error}")
        return 1
    count = len(discover_living_docs(_ROOT))
    print(f"DOC METADATA PASS: {count} living documents verified with valid, unique metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())

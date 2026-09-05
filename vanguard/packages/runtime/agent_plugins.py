"""
Agent Plugin and Capability Architecture (Skills, Techniques, Proficiencies).

Provides unified, modular discovery, composition, prefix indexing, and execution
of declarative capabilities defined under `.agents/`:
- Skills (Atomic capabilities)
- Techniques (Synergistic open-loop compositions)
- Proficiencies (Closed feedback loops with falsifiers and fail-closed rollback)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .skill_index import DEFAULT_BUDGET_CHARS, SkillEntry, SkillIndex, build_skill_index

__all__ = [
    "PluginSpec",
    "load_agent_plugins",
    "filter_plugins",
    "build_plugin_index",
]

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_yaml_frontmatter(text: str) -> Dict[str, Any]:
    """Extract and parse YAML frontmatter cleanly with fallback."""
    match = _FRONTMATTER_RE.search(text)
    if not match:
        return {}
    raw_yaml = match.group(1)
    
    try:
        import yaml
        parsed = yaml.safe_load(raw_yaml)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Simple regex-based fallback if PyYAML is unavailable
    result: Dict[str, Any] = {}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip("\"'")
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                result[key] = items
            else:
                result[key] = val
    return result


@dataclass(frozen=True, slots=True)
class PluginSpec:
    """Declarative capability specification."""
    name: str
    category: str  # "skill" | "technique" | "proficiency"
    description: str
    doc_path: str
    runner_path: Optional[str] = None
    mode: str = "atomic"  # "atomic" | "open_loop" | "closed_loop"
    composes_skills: Tuple[str, ...] = ()
    composes_techniques: Tuple[str, ...] = ()
    invariants: Tuple[str, ...] = ()

    def to_skill_entry(self) -> SkillEntry:
        prefix = f"[{self.category.upper()}] " if self.category != "skill" else ""
        desc = f"{prefix}{self.description}"
        return SkillEntry(
            name=self.name,
            description=desc,
            path=self.doc_path,
        )


def _find_runner_script(directory: Path) -> Optional[str]:
    """Finds primary executable Python script in directory or scripts/ subdir."""
    scripts_dir = directory / "scripts"
    search_dirs = [scripts_dir, directory]
    for sdir in search_dirs:
        if sdir.exists() and sdir.is_dir():
            for p in sdir.glob("*.py"):
                if p.name != "__init__.py":
                    return str(p)
    return None


def load_agent_plugins(repo_root: Optional[Path | str] = None) -> Tuple[PluginSpec, ...]:
    """Discovers and parses all skills, techniques, and proficiencies under .agents/."""
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    agents_dir = root / ".agents"
    if not agents_dir.exists():
        return ()

    plugins: List[PluginSpec] = []
    
    categories = [
        ("skill", agents_dir / "skills", "SKILL.md", "atomic"),
        ("technique", agents_dir / "techniques", "TECHNIQUE.md", "open_loop"),
        ("proficiency", agents_dir / "proficiencies", "PROFICIENCY.md", "closed_loop"),
    ]

    for cat_name, cat_dir, doc_filename, default_mode in categories:
        if not cat_dir.exists() or not cat_dir.is_dir():
            continue

        for item in sorted(cat_dir.iterdir()):
            if not item.is_dir():
                continue
            doc_file = item / doc_filename
            if not doc_file.exists():
                continue

            try:
                content = doc_file.read_text(encoding="utf-8")
            except Exception:
                continue

            fm = _parse_yaml_frontmatter(content)
            name = str(fm.get("name") or item.name).strip()
            desc = " ".join(str(fm.get("description", "")).split())
            mode = str(fm.get("mode") or default_mode).strip()

            # Composed dependencies
            comp_skills = tuple(str(x).strip() for x in (fm.get("composes_skills") or fm.get("composed_skills") or ()))
            comp_techs = tuple(str(x).strip() for x in (fm.get("composes_techniques") or fm.get("composed_techniques") or ()))
            invariants = tuple(str(x).strip() for x in (fm.get("invariants") or ()))

            runner = _find_runner_script(item)
            rel_doc_path = str(doc_file.relative_to(root)) if doc_file.is_relative_to(root) else str(doc_file)
            rel_runner = str(Path(runner).relative_to(root)) if runner and Path(runner).is_relative_to(root) else runner

            spec = PluginSpec(
                name=name,
                category=cat_name,
                description=desc,
                doc_path=rel_doc_path,
                runner_path=rel_runner,
                mode=mode,
                composes_skills=comp_skills,
                composes_techniques=comp_techs,
                invariants=invariants,
            )
            plugins.append(spec)

    return tuple(plugins)


def filter_plugins(
    plugins: Sequence[PluginSpec],
    *,
    categories: Optional[Sequence[str]] = None,
    names: Optional[Sequence[str]] = None,
    modes: Optional[Sequence[str]] = None,
) -> Tuple[PluginSpec, ...]:
    """Filters plugins by category, name, or execution mode."""
    cat_set = set(categories) if categories else None
    name_set = set(names) if names else None
    mode_set = set(modes) if modes else None

    result: List[PluginSpec] = []
    for p in plugins:
        if cat_set and p.category not in cat_set:
            continue
        if name_set and p.name not in name_set:
            continue
        if mode_set and p.mode not in mode_set:
            continue
        result.append(p)
    return tuple(result)


def build_plugin_index(
    plugins: Sequence[PluginSpec],
    *,
    budget_chars: int = DEFAULT_BUDGET_CHARS,
) -> SkillIndex:
    """Builds a token-efficient prefix SkillIndex, strictly bounding size under budget_chars."""
    raw_items = [
        {
            "name": p.name,
            "description": f"[{p.category.upper()}] {p.description}" if p.category != "skill" else p.description,
            "path": p.doc_path,
        }
        for p in plugins
    ]
    return build_skill_index(raw_items, budget_chars=budget_chars)

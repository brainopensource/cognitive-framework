"""Workspace Discovery Engine (REQ-CTX-001, GTS-13C §7.4).

Scans workspace roots for guideline markdown files (AGENTS.md, CLAUDE.md, PROJECT.md)
and formats them for ingestion into L3/L4 context layers without breaking prefix stability.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ..context.layers import Block, Fragment, Layer

#: Discovered file priority order
DISCOVERY_CANDIDATES: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    "PROJECT.md",
    ".github/copilot-instructions.md",
)


@dataclass(frozen=True, slots=True)
class DiscoveredInstruction:
    """An instruction document discovered in the workspace."""

    filename: str
    relative_path: str
    content: str

    @property
    def label(self) -> str:
        return f"instruction:{self.filename.lower().replace('.', '_')}"


class WorkspaceDiscovery:
    """Scans and ingests workspace instructions into L3/L4 context layers."""

    def __init__(self, workspace_root: str | Path) -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def discover(self) -> tuple[DiscoveredInstruction, ...]:
        """Scan workspace root for instruction files."""
        discovered: list[DiscoveredInstruction] = []
        if not self.workspace_root.exists() or not self.workspace_root.is_dir():
            return ()

        for rel_path in DISCOVERY_CANDIDATES:
            target = self.workspace_root / rel_path
            if target.exists() and target.is_file():
                try:
                    content = target.read_text(encoding="utf-8").strip()
                    if content:
                        discovered.append(
                            DiscoveredInstruction(
                                filename=target.name,
                                relative_path=rel_path,
                                content=content,
                            )
                        )
                except Exception:
                    # Ignore unreadable files
                    pass

        return tuple(discovered)

    def render_environment_text(self) -> str:
        """Render all discovered instructions into a single L3 environment text block."""
        instructions = self.discover()
        if not instructions:
            return ""

        sections: list[str] = []
        for inst in instructions:
            sections.append(
                f"=== Workspace Instructions ({inst.filename}) ===\n{inst.content}"
            )
        return "\n\n".join(sections)

    def as_environment_block(self) -> Block | None:
        """Render discovered instructions as an L3 Environment Block (Prefix-Stable)."""
        text = self.render_environment_text()
        if not text:
            return None
        return Block(
            layer=Layer.ENVIRONMENT,
            source="workspace_discovery",
            label="workspace-instructions",
            text=text,
        )

    def as_fragments(self) -> tuple[Fragment, ...]:
        """Render discovered instructions as L4 Fragments."""
        instructions = self.discover()
        fragments: list[Fragment] = []
        for inst in instructions:
            fragments.append(
                Fragment(
                    source="workspace_discovery",
                    label=inst.label,
                    text=f"[{inst.filename}]\n{inst.content}",
                    evictable=False,
                )
            )
        return tuple(fragments)

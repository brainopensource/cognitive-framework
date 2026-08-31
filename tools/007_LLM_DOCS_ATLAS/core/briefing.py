"""Deterministic task briefing compiler for LDA (``lda brief``).

Turns a ContextPacket into a human+agent readable briefing artifact: task
read-back, intent, authority map, key code with skeletons, documentation
obligations, test falsifiers, and provenance. Same HEAD-bound provenance as
the packet; JSON is the stable machine interface, markdown the human one.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .compiler import ContextCompiler
from .models import ContextPacket
from .profile import RepositoryProfile
from .query import analyze_query
from .storage import FactGraphStorage


def compile_brief(
    repo_root: Path,
    task: str,
    budget: int = 8000,
    strategy: str = "ppr_submodular",
    profile: Optional[RepositoryProfile] = None,
    head_sha: Optional[str] = None,
    storage: Optional[FactGraphStorage] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Compile a packet and render it into a structured briefing."""
    root = Path(repo_root)
    if storage is None:
        storage = get_storage_for(root)
    if profile is None:
        from .config import AtlasContext

        profile = AtlasContext.discover(root).profile
    compiler = ContextCompiler(root, storage, profile=profile, head_sha=head_sha)
    packet = compiler.compile(task, budget=budget, strategy=strategy, use_cache=use_cache)
    intent = analyze_query(task).intent
    obligations = _doc_obligations(root, packet)
    falsifiers = _test_falsifiers(packet)
    return {
        "task": task,
        "intent": intent,
        "budget": budget,
        "strategy": strategy,
        "authority": packet.authority,
        "provenance": packet.provenance,
        "token_accounting": packet.token_accounting,
        "warnings": packet.warnings,
        "key_documents": [
            {"locator": c.locator, "title": c.title, "authority": c.authority,
             "reason": c.reason, "tokens": c.tokens}
            for c in packet.documents[:8]
        ],
        "key_code": [
            {"locator": c.locator, "title": c.title, "representation": c.representation,
             "reason": c.reason, "tokens": c.tokens}
            for c in (packet.symbols[:6] + packet.code)
        ],
        "doc_obligations": obligations,
        "test_falsifiers": falsifiers,
        "callers": packet.callers,
        "brief_markdown": render_brief_markdown(
            task, intent, packet, obligations, falsifiers
        ),
    }


def get_storage_for(repo_root: Path) -> FactGraphStorage:
    from ..atlas import get_storage

    return get_storage(Path(repo_root))


def _doc_obligations(root: Path, packet: ContextPacket) -> List[Dict[str, Any]]:
    """Canonical documents the task touches that constrain implementation."""
    obligations: List[Dict[str, Any]] = []
    for c in packet.documents:
        if c.authority in ("normative", "canonical", "specification") or "spec" in c.locator.lower():
            obligations.append({
                "document": c.locator,
                "authority": c.authority,
                "reason": c.reason,
            })
    return obligations[:5]


def _test_falsifiers(packet: ContextPacket) -> List[Dict[str, Any]]:
    """Tests/falsifiers attached to the selected code candidates."""
    out: List[Dict[str, Any]] = []
    for c in packet.tests[:6]:
        out.append({"test": c.locator, "title": c.title, "reason": c.reason})
    return out


def render_brief_markdown(
    task: str,
    intent: str,
    packet: ContextPacket,
    obligations: List[Dict[str, Any]],
    falsifiers: List[Dict[str, Any]],
) -> str:
    """Render the structured briefing as compact markdown."""
    lines: List[str] = []
    lines.append("# LDA Task Briefing")
    lines.append("")
    lines.append(f"**Task:** {task}")
    lines.append(f"**Intent:** {intent}")
    lines.append(
        f"**Provenance:** HEAD `{(packet.provenance or {}).get('source_head_sha')}`, "
        f"strategy `{packet.provenance.get('strategy')}`, "
        f"profile `{packet.provenance.get('profile')}`"
    )
    used = packet.token_accounting.get("used_tokens", packet.estimated_tokens)
    lines.append(f"**Budget:** {packet.budget} tokens ({used} used)")
    lines.append("")

    lines.append("## Authority map")
    if packet.authority:
        for a in packet.authority:
            lines.append(f"- `{a}`")
    else:
        lines.append("- (no authority-tagged documents selected)")
    lines.append("")

    lines.append("## Key documents")
    for c in packet.documents[:8]:
        lines.append(f"- `{c.locator}` — {c.title} ({c.tokens} tok; {c.reason})")
    if not packet.documents:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Key code")
    for c in packet.symbols[:6]:
        lines.append(f"- `{c.locator}` — {c.title} [{c.representation}] ({c.reason})")
    if not packet.symbols:
        lines.append("- (none)")
    lines.append("")

    if obligations:
        lines.append("## Documentation obligations (read before implementing)")
        for o in obligations:
            lines.append(f"- `{o['document']}` (authority: {o['authority']})")
        lines.append("")

    if falsifiers:
        lines.append("## Test falsifiers")
        for f in falsifiers:
            lines.append(f"- `{f['test']}`")
        lines.append("")

    if packet.warnings:
        lines.append("## Warnings")
        for w in packet.warnings:
            lines.append(f"- {w}")
        lines.append("")

    head = (packet.provenance or {}).get("source_head_sha")
    lines.append(
        "> Facts are bound to workspace HEAD. On HEAD mismatch, recompile "
        "(`lda context`) or fail closed — never serve stale line numbers."
    )
    if head is None:
        lines.append("> Note: workspace has no git HEAD; freshness binding is inactive.")
    return "\n".join(lines)


__all__ = ["compile_brief", "render_brief_markdown"]

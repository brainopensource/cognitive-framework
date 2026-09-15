"""One-Shot Task Bundle Compiler for LDA (Requirement Phase 1).

Executes a unified DRY pass over the fact graph to return:
- Target architectural symbols with signatures and line bounds
- Blast-radius upstream callers and dependents
- Associated test falsifiers and executable runner commands
- Canonical documentation obligations
- Token-budgeted high-signal context extracts and code skeletons
- Zero stale AST line ranges via seamless auto-delta freshness check
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from .compiler import ContextCompiler
from .delta import index_delta
from .gitinfo import current_head_sha
from .models import ContextPacket, serialise
from .profile import RepositoryProfile
from .query import analyze_query
from .resolve import resolve_symbol_intent
from .storage import FactGraphStorage
from .test_association import TestAssociationEngine


_SUBSYSTEM_DOC_MAP = {
    "vanguard/packages/kernel": ("docs/backend/architecture/kernel.md", "normative", "TCB kernel specification & invariants"),
    "vanguard/packages/domain": ("docs/backend/architecture/domain.md", "normative", "Domain pure value contracts & selectors"),
    "vanguard/packages/ports": ("docs/backend/reference/ports.md", "canonical", "Hexagonal boundary port interfaces"),
    "vanguard/packages/agency": ("docs/backend/architecture/agency.md", "canonical", "Recursive turn engine & context compaction"),
    "vanguard/packages/runtime": ("docs/architecture/system_composition.md", "canonical", "System lifecycle, wiring, and governance"),
    "vanguard/packages/adapters": ("docs/architecture/isolation_and_sandboxing.md", "canonical", "Adapters, Bubblewrap sandbox, and stores"),
}


def _resolve_doc_obligations(
    touched_files: Sequence[str],
    packet: Optional[ContextPacket] = None,
    profile: Optional[RepositoryProfile] = None,
    repo_root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Determine normative and canonical docs governing the affected code."""
    obligations: List[Dict[str, Any]] = []
    seen_docs: Set[str] = set()

    subsystem_map = profile.subsystem_doc_map if profile and profile.subsystem_doc_map else _SUBSYSTEM_DOC_MAP
    default_docs = profile.default_normative_docs if profile and profile.default_normative_docs else ()

    # 1. Top specification / normative documents
    if default_docs:
        for d in default_docs:
            if repo_root and not (repo_root / d).is_file():
                continue
            seen_docs.add(d)
            obligations.append({
                "document": d,
                "authority": "normative",
                "reason": "Specification / normative law of record",
            })
    elif not profile or profile.name == "generic":
        # Dynamic brownfield discovery for generic repos
        for root_doc in ("spec.md", "docs/spec.md", "docs/architecture.md", "ARCHITECTURE.md", "README.md", "CONTRIBUTING.md"):
            if repo_root and (repo_root / root_doc).is_file() and root_doc not in seen_docs:
                seen_docs.add(root_doc)
                obligations.append({
                    "document": root_doc,
                    "authority": "canonical",
                    "reason": "Root architectural documentation and specification baseline",
                })
                break
    else:
        # Backward-compatible fallback for AETHER
        default_spec = "docs/execution/main/spec.md"
        if not repo_root or (repo_root / default_spec).is_file():
            obligations.append({
                "document": default_spec,
                "authority": "normative",
                "reason": "Compact Normative Law & System Specification of record",
            })
            seen_docs.add(default_spec)

    # 2. Map touched files to governing subsystem docs
    for tf in touched_files:
        norm_tf = str(Path(tf)).replace("\\", "/")
        matched_explicit = False
        for prefix, doc_info in subsystem_map.items():
            if norm_tf.startswith(prefix):
                matched_explicit = True
                doc_path, authority, reason = doc_info[0], doc_info[1], doc_info[2]
                if doc_path not in seen_docs and (not repo_root or (repo_root / doc_path).is_file()):
                    seen_docs.add(doc_path)
                    obligations.append({
                        "document": doc_path,
                        "authority": authority,
                        "reason": f"Governs `{prefix}/` touched by task ({reason})",
                    })

        # Dynamic brownfield directory documentation discovery
        if not matched_explicit and repo_root:
            parent_dir = Path(norm_tf).parent
            if parent_dir and str(parent_dir) not in (".", "/"):
                dir_name = parent_dir.name
                dir_readme = parent_dir / "README.md"
                doc_file = Path("docs") / f"{dir_name}.md"
                if (repo_root / doc_file).is_file() and str(doc_file) not in seen_docs:
                    seen_docs.add(str(doc_file))
                    obligations.append({
                        "document": str(doc_file),
                        "authority": "canonical",
                        "reason": f"Governs subsystem `{dir_name}` touched by task",
                    })
                elif (repo_root / dir_readme).is_file() and str(dir_readme) not in seen_docs:
                    seen_docs.add(str(dir_readme))
                    obligations.append({
                        "document": str(dir_readme),
                        "authority": "canonical",
                        "reason": f"Directory documentation for `{parent_dir}`",
                    })

    # 3. Include normative candidates selected by the context compiler
    if packet:
        for c in packet.documents:
            if c.locator not in seen_docs and (c.authority in ("normative", "canonical", "specification") or "spec" in c.locator.lower()):
                if not repo_root or (repo_root / c.locator).is_file():
                    seen_docs.add(c.locator)
                    obligations.append({
                        "document": c.locator,
                        "authority": c.authority or "canonical",
                        "reason": c.reason or "Task-relevant documentation constraint",
                    })

    return obligations[:6]


def compile_task_plan(
    repo_root: Path,
    task: str,
    budget: int = 8000,
    strategy: str = "ppr_submodular",
    top_symbols: int = 5,
    auto_delta: bool = True,
    profile: Optional[RepositoryProfile] = None,
    storage: Optional[FactGraphStorage] = None,
    head_sha: Optional[str] = None,
) -> Dict[str, Any]:
    """Compile a complete one-shot task bundle in a single unified execution pass."""
    t0 = time.perf_counter()
    root = Path(repo_root).resolve()

    from ..atlas import get_storage
    storage = storage or get_storage(root)
    active_profile = profile or RepositoryProfile()
    head = head_sha or current_head_sha(root)

    # 1. Seamless Auto-Delta freshness check (<25ms)
    delta_result = None
    if auto_delta:
        delta_result = index_delta(root, profile=active_profile, storage=storage)

    # 2. Intent Analysis & Primary Symbol Resolution
    query_meta = analyze_query(task)
    primary_syms = resolve_symbol_intent(storage, task, top_k=top_symbols, profile=active_profile)

    # If query mentions a specific known symbol exactly, prioritize it
    explicit_names = [w for w in task.split() if w[0].isupper() or "_" in w]
    for exp in explicit_names:
        exact_matches = storage.get_symbol(exp, exact=True)
        for em in exact_matches:
            if not any(ps["symbol_id"] == em["id"] for ps in primary_syms):
                primary_syms.insert(0, {
                    "symbol_id": em["id"],
                    "name": em["name"],
                    "qualified_name": em.get("qualified_name", ""),
                    "kind": em.get("kind", "symbol"),
                    "language": em.get("language", "python"),
                    "file_path": em["file_path"],
                    "start_line": em.get("start_line", 1),
                    "end_line": em.get("end_line", 1),
                    "signature": em.get("signature") or f"{em['name']}()",
                    "docstring": (em.get("docstring") or "").split("\n\n")[0][:150],
                    "confidence_score": 1.0,
                    "callers_count": 0,
                    "reason": f"explicit mention in query: {exp}",
                })

    primary_syms = primary_syms[:top_symbols]

    # 3. Blast Radius (Callers & References)
    callers_list: List[Dict[str, Any]] = []
    affected_files: Set[str] = {s["file_path"] for s in primary_syms}

    for s in primary_syms:
        sym_callers = storage.get_callers(s["symbol_id"])
        for c in sym_callers[:4]:
            c_file = c.get("file_path", "")
            if c_file:
                affected_files.add(c_file)
            callers_list.append({
                "target_symbol": s["name"],
                "caller_name": c.get("caller_name", "anonymous"),
                "caller_file": c_file,
                "line": c.get("start_line", 1),
                "confidence": c.get("confidence_tier", 80),
            })

    # 4. Associated Test Falsifiers
    engine = TestAssociationEngine(storage)
    test_results = engine.find_associated_tests(
        touched_files=list(affected_files),
        touched_symbols=[s["symbol_id"] for s in primary_syms],
    )

    # 5. Token-Budgeted Context Packet Compilation
    compiler = ContextCompiler(root, storage, profile=active_profile, head_sha=head)
    packet = compiler.compile(task, budget=budget, strategy=strategy, use_cache=True)

    # 6. Documentation Obligations
    doc_obligations = _resolve_doc_obligations(list(affected_files), packet=packet, profile=active_profile, repo_root=root)

    # 7. Render Markdown Briefing
    elapsed = time.perf_counter() - t0
    elapsed_ms = round(elapsed * 1000, 2)

    plan_md = render_plan_markdown(
        task=task,
        intent=query_meta.intent,
        primary_syms=primary_syms,
        callers=callers_list,
        test_results=test_results,
        doc_obligations=doc_obligations,
        packet=packet,
        elapsed_ms=elapsed_ms,
        delta_info=delta_result,
    )

    return {
        "task": task,
        "intent": query_meta.intent,
        "strategy": strategy,
        "budget": budget,
        "duration_seconds": round(elapsed, 4),
        "duration_ms": elapsed_ms,
        "freshness": {
            "auto_delta_applied": auto_delta,
            "dirty_files_synchronized": (delta_result or {}).get("files_indexed", 0),
            "index_status": (delta_result or {}).get("status", "UP_TO_DATE"),
            "head_sha": head,
        },
        "primary_symbols": primary_syms,
        "blast_radius": {
            "callers": callers_list[:8],
            "affected_files": sorted(affected_files),
        },
        "test_falsifiers": {
            "test_files": test_results.get("associated_test_files", [])[:8],
            "test_symbols": test_results.get("associated_test_symbols", [])[:6],
            "suggested_commands": test_results.get("suggested_commands", [])[:6],
        },
        "doc_obligations": doc_obligations,
        "context_packet": {
            "estimated_tokens": packet.estimated_tokens,
            "token_accounting": packet.token_accounting,
            "documents_count": len(packet.documents),
            "code_snippets_count": len(packet.code) + len(packet.symbols),
        },
        "plan_markdown": plan_md,
    }


def render_plan_markdown(
    task: str,
    intent: str,
    primary_syms: List[Dict[str, Any]],
    callers: List[Dict[str, Any]],
    test_results: Dict[str, Any],
    doc_obligations: List[Dict[str, Any]],
    packet: ContextPacket,
    elapsed_ms: float,
    delta_info: Optional[Dict[str, Any]] = None,
) -> str:
    """Render high-signal Markdown for terminal output."""
    lines: List[str] = []
    lines.append(f"# LDA Task Plan: {task}\n")
    delta_status = (delta_info or {}).get("status", "UP_TO_DATE")
    delta_files = (delta_info or {}).get("files_indexed", 0)
    lines.append(
        f"> **Intent:** `{intent}` | **Plan Latency:** `{elapsed_ms:.1f}ms` | "
        f"**Freshness:** `{delta_status}` ({delta_files} dirty files synced) | "
        f"**Budget:** `{packet.estimated_tokens}/{packet.budget} tokens`\n"
    )

    # 1. Primary Symbols
    lines.append("## 1. Primary Target Symbols")
    if primary_syms:
        for s in primary_syms:
            lines.append(
                f"- **`{s['name']}`** (`{s['kind']}`) in [`{s['file_path']}:L{s['start_line']}-L{s['end_line']}`]({s['file_path']}#L{s['start_line']})"
            )
            lines.append(f"  Confidence: `{s['confidence_score']}` | Callers: `{s.get('callers_count', 0)}`")
            if s.get("signature"):
                lines.append(f"  Signature: `{s['signature']}`")
            if s.get("reason"):
                lines.append(f"  Signal: *{s['reason']}*")
            if s.get("docstring"):
                lines.append(f"  Doc: *{s['docstring']}*")
            lines.append("")
    else:
        lines.append("*No high-confidence symbols pinpointed. Context compiler candidates will guide orientation.*\n")

    # 2. Blast Radius (Upstream Callers)
    lines.append("## 2. Blast Radius (Upstream Dependents)")
    if callers:
        for c in callers[:6]:
            c_file = c.get("caller_file") or "unknown"
            c_line = c.get("line") or 1
            lines.append(
                f"- **`{c['caller_name']}`** calls `{c['target_symbol']}` in [`{c_file}:L{c_line}`]({c_file}#L{c_line})"
            )
        lines.append("")
    else:
        lines.append("*No direct callers recorded in graph. Symbol is either leaf, dynamic entrypoint, or root interface.*\n")

    # 3. Canonical Documentation Obligations
    lines.append("## 3. Canonical Documentation Obligations")
    if doc_obligations:
        for doc in doc_obligations:
            lines.append(
                f"- [`{doc['document']}`]({doc['document']}) (`{doc['authority']}`): {doc['reason']}"
            )
        lines.append("")
    else:
        lines.append("*No canonical documentation obligations mapped for this scope.*\n")

    # 4. Targeted Test Falsifiers
    lines.append("## 4. Targeted Test Falsifiers (Executable Commands)")
    commands = test_results.get("suggested_commands", [])
    if commands:
        lines.append("```bash")
        for cmd in commands[:5]:
            lines.append(cmd)
        lines.append("```\n")
    else:
        lines.append("*No targeted unit tests found. Full regression suite applies.*\n")

    # 5. Key Context Extracts
    lines.append("## 5. Working Memory & Context Extracts")
    for doc in packet.documents[:3]:
        lines.append(f"- **Document:** [`{doc.locator}`]({doc.locator}) — *{doc.title}* ({doc.tokens} tok)")
    valid_codes = [c for c in (packet.symbols + packet.code) if not c.locator.startswith("lang:") and ("." in c.locator or "/" in c.locator)]
    for code in valid_codes[:4]:
        lines.append(f"- **Code:** [`{code.locator}`]({code.locator}) — `{code.representation}` ({code.tokens} tok)")
    lines.append("")

    return "\n".join(lines)

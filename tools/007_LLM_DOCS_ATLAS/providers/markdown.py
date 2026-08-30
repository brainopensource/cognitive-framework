"""Markdown and documentation intelligence provider."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.ir import (
    ConfidenceTier,
    EntityKind,
    IRDocSection,
    IRDocument,
    IREntity,
    IRRelation,
    Provenance,
    RelationKind,
    SourceLocation,
)
from ..core.models import Entity, ProviderResult, Relation
from .base import BaseProvider


class MarkdownDocProvider(BaseProvider):
    """Extracts structure, headings, anchors, frontmatter, and relations from Markdown."""

    name = "markdown"
    confidence_tier = ConfidenceTier.STRUCTURED_DOC

    def collect(
        self,
        repo_root: Path | Any,
        incremental: bool = False,
        file_states: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> ProviderResult:
        root = repo_root.root if hasattr(repo_root, "root") else Path(repo_root)
        documents: List[IRDocument] = []
        doc_sections: List[IRDocSection] = []
        relations: List[Relation] = []
        legacy_entities: List[Entity] = []

        md_files = list(root.rglob("*.md")) + list(root.rglob("*.mdx"))
        for fpath in md_files:
            if any(part in fpath.parts for part in [".git", "node_modules", ".venv", "dev_context_logs"]):
                continue
            try:
                rel_path = str(fpath.relative_to(root)).replace("\\", "/")
                content = fpath.read_text(errors="replace")
                lines = content.splitlines()

                # Extract frontmatter if present
                title = fpath.stem.replace("_", " ").title()
                canonical_id = rel_path
                authority = None
                summary = ""

                if content.startswith("---"):
                    fm_end = content.find("---", 3)
                    if fm_end != -1:
                        fm_text = content[3:fm_end]
                        for line in fm_text.splitlines():
                            if ":" in line:
                                k, v = line.split(":", 1)
                                k, v = k.strip(), v.strip().strip("\"'")
                                if k in ("title", "id"):
                                    if k == "title": title = v
                                    if k == "id": canonical_id = v
                                elif k == "authority":
                                    authority = v
                                elif k == "summary" or k == "purpose":
                                    summary = v

                # Parse headings and sections
                sections: List[IRDocSection] = []
                current_heading = title
                current_level = 1
                current_anchor = "header"
                section_lines: List[str] = []
                section_start = 1

                for idx, line in enumerate(lines, 1):
                    h_match = re.match(r"^(#{1,6})\s+(.*)$", line)
                    if h_match:
                        # Flush previous section
                        if section_lines:
                            sec_text = "\n".join(section_lines)
                            sec_id = f"{rel_path}#{current_anchor}"
                            sections.append(
                                IRDocSection(
                                    id=sec_id,
                                    doc_id=rel_path,
                                    heading=current_heading,
                                    level=current_level,
                                    anchor=current_anchor,
                                    content=sec_text,
                                    estimated_tokens=len(sec_text.split()),
                                    start_line=section_start,
                                    end_line=idx - 1
                                )
                            )
                        current_level = len(h_match.group(1))
                        current_heading = h_match.group(2).strip()
                        current_anchor = re.sub(r"[^a-zA-Z0-9_-]", "", current_heading.lower().replace(" ", "-"))
                        section_lines = [line]
                        section_start = idx
                    else:
                        section_lines.append(line)

                # Flush last section
                if section_lines:
                    sec_text = "\n".join(section_lines)
                    sec_id = f"{rel_path}#{current_anchor}"
                    sections.append(
                        IRDocSection(
                            id=sec_id,
                            doc_id=rel_path,
                            heading=current_heading,
                            level=current_level,
                            anchor=current_anchor,
                            content=sec_text,
                            estimated_tokens=len(sec_text.split()),
                            start_line=section_start,
                            end_line=len(lines)
                        )
                    )

                doc_record = IRDocument(
                    id=rel_path,
                    file_path=rel_path,
                    title=title,
                    canonical_id=canonical_id,
                    authority=authority,
                    summary=summary or (sections[0].content[:200] if sections else ""),
                    estimated_tokens=len(content.split())
                )
                documents.append(doc_record)
                doc_sections.extend(sections)

                # Extract markdown cross-references e.g. [Link](docs/SPEC.md) or code tokens `foo.bar`
                for m in re.finditer(r"\[([^\]]+)\]\(([^)]+\.md(?:#[^)]+)?)\)", content):
                    target_link = m.group(2)
                    relations.append(
                        Relation(
                            source=rel_path,
                            target=target_link,
                            kind="documents",
                            evidence=m.group(1)
                        )
                    )

                legacy_entities.append(
                    Entity(
                        id=canonical_id or rel_path,
                        kind="document",
                        locator=rel_path,
                        authority=authority,
                        metadata={
                            "title": title,
                            "path": rel_path,
                            "canonical_id": canonical_id,
                            "authority": authority,
                            "estimated_tokens": doc_record.estimated_tokens,
                            "summary": doc_record.summary
                        }
                    )
                )

            except Exception:
                pass

        res = ProviderResult(provider=self.name, entities=legacy_entities, relations=relations)
        res.metadata["ir_documents"] = documents
        res.metadata["ir_doc_sections"] = doc_sections
        return res

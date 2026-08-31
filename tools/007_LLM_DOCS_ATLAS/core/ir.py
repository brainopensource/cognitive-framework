"""Normalized Repository Intelligence Intermediate Representation (IR).

Defines the universal entities, relations, provenance, and deterministic
Kythe-inspired SymbolId generation. Completely repository-agnostic.
"""
from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional, Sequence


class ConfidenceTier(enum.IntEnum):
    """Explicit confidence hierarchy for repository intelligence facts."""
    HEURISTIC = 40
    STRUCTURED_DOC = 60
    AST_GREP = 70
    TREE_SITTER = 80
    SCIP = 90
    COMPILER = 100

    @classmethod
    def from_string(cls, val: str) -> ConfidenceTier:
        normalized = val.upper().strip()
        for member in cls:
            if member.name == normalized:
                return member
        return cls.HEURISTIC


class EntityKind(str, enum.Enum):
    REPOSITORY = "repository"
    PACKAGE = "package"
    FILE = "file"
    SYMBOL = "symbol"
    DOCUMENT = "document"
    DOC_SECTION = "doc_section"
    SCHEMA = "schema"
    TEST = "test"
    COMMIT = "commit"


class RelationKind(str, enum.Enum):
    CONTAINS = "contains"
    DEFINES = "defines"
    REFERENCES = "references"
    CALLS = "calls"
    IMPORTS = "imports"
    IMPLEMENTS = "implements"
    INHERITS = "inherits"
    TESTS = "tests"
    DOCUMENTS = "documents"
    SPECIFIED_BY = "specified_by"
    GENERATED_FROM = "generated_from"
    DEPENDS_ON = "depends_on"


class RepresentationKind(str, enum.Enum):
    FULL = "FULL"
    SKELETON = "SKELETON"
    SIGNATURE = "SIGNATURE"
    SUMMARY = "SUMMARY"
    REFERENCE = "REFERENCE"


def compute_symbol_id(
    corpus: str,
    language: str,
    package_or_module: str,
    qualified_symbol: str,
    semantic_kind: str,
) -> str:
    """Generate a deterministic, Kythe-inspired stable SymbolId.

    SymbolId is independent of source line movements and re-indexing.
    Format: sym:<sha256(corpus|language|package|symbol|kind)[:16]>
    """
    corpus_norm = (corpus or "repo").strip().lower()
    lang_norm = (language or "unknown").strip().lower()
    pkg_norm = (package_or_module or "").strip().replace("\\", "/").lower()
    sym_norm = (qualified_symbol or "").strip()
    kind_norm = (semantic_kind or "").strip().lower()

    raw = f"{corpus_norm}|{lang_norm}|{pkg_norm}|{sym_norm}|{kind_norm}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"sym:{digest}"


@dataclass(frozen=True)
class SourceLocation:
    """Source location attribute for an entity or fact."""
    file_path: str
    start_line: int = 1
    end_line: int = 1
    start_col: int = 0
    end_col: int = 0

    def to_reference(self) -> str:
        if self.start_line == self.end_line:
            return f"{self.file_path}#L{self.start_line}"
        return f"{self.file_path}#L{self.start_line}-L{self.end_line}"


@dataclass(frozen=True)
class Provenance:
    """Provenance tracking fact source, indexer, revision, and confidence."""
    provider: str
    indexer: str
    source_path: str
    revision_sha: Optional[str] = None
    content_hash: Optional[str] = None
    location: Optional[SourceLocation] = None
    confidence_tier: ConfidenceTier = ConfidenceTier.STRUCTURED_DOC
    schema_version: str = "1.0.0"


@dataclass
class IREntity:
    """Universal repository entity."""
    id: str
    kind: EntityKind
    name: str
    locator: str
    provenance: Provenance
    authority: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IRSymbol:
    """Detailed code symbol record."""
    symbol_id: str
    name: str
    qualified_name: str
    kind: str
    language: str
    file_path: str
    signature: Optional[str] = None
    docstring: Optional[str] = None
    location: Optional[SourceLocation] = None
    provenance: Optional[Provenance] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IRDocument:
    """Document record with hierarchical structure."""
    id: str
    file_path: str
    title: str
    canonical_id: Optional[str] = None
    authority: Optional[str] = None
    summary: Optional[str] = None
    estimated_tokens: int = 0
    provenance: Optional[Provenance] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IRDocSection:
    """Document section bounded by headings."""
    id: str
    doc_id: str
    heading: str
    level: int
    anchor: str
    content: str
    estimated_tokens: int = 0
    start_line: int = 1
    end_line: int = 1


@dataclass
class IRRelation:
    """Typed directional relationship between two entities."""
    id: str
    source_id: str
    target_id: str
    kind: RelationKind
    confidence_tier: ConfidenceTier
    evidence: Optional[str] = None
    source_path: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class IRIndexRun:
    """Metadata for an indexing execution."""
    id: str
    repo_id: str
    started_at: str
    completed_at: str
    files_indexed: int
    symbols_found: int
    relations_found: int
    indexer_version: str = "1.0.0"
    is_incremental: bool = False


def to_dict(obj: Any) -> Any:
    """Recursively convert IR objects into standard JSON-serializable dicts."""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for k, v in asdict(obj).items():
            result[k] = to_dict(v)
        return result
    if isinstance(obj, (list, tuple, set)):
        return [to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, enum.Enum):
        return obj.value
    return obj

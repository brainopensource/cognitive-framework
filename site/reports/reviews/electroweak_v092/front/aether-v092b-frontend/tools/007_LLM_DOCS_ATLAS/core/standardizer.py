"""Standardizer: language detection, symbol-kind normalization, and tokenization.

Universal, project-agnostic rules shared by extractors, rankers, health checks,
and the CLI. This is the "ruler" — one canonical registry for what a language
looks like, what kinds of symbols exist, and how identifiers should be split
into search tokens (camelCase / snake_case / kebab-case / dot-paths).

Extractors SHOULD emit raw, language-native kinds and then pass them through
`normalize_kind` so every downstream consumer (FTS, ranking, packets, health)
speaks one vocabulary.
"""
from __future__ import annotations

import re
from typing import Iterable, Union

PathLike = Union[str, "Path"]

# ---------------------------------------------------------------------------
# Language registry (generic defaults; profiles may override code/document
# extension sets)
# ---------------------------------------------------------------------------

EXT_TO_LANG: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".cs": "csharp",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".rb": "ruby",
    ".php": "php",
    ".sh": "bash",
    ".bash": "bash",
    ".sql": "sql",
    ".md": "markdown",
    ".mdx": "markdown",
    ".rst": "rst",
    ".txt": "text",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".html": "html",
    ".css": "css",
}

# Reverse registry: language -> its known extensions (profile-agnostic).
LANG_EXTENSIONS: dict[str, tuple[str, ...]] = {}
for _ext, _lang in EXT_TO_LANG.items():
    LANG_EXTENSIONS[_lang] = LANG_EXTENSIONS.get(_lang, ()) + (_ext,)

# Default code/document extension sets (a profile may override these).
DEFAULT_CODE_EXTENSIONS: tuple[str, ...] = (
    ".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs",
    ".rs", ".go", ".java", ".kt", ".kts", ".cs", ".c", ".h", ".cpp",
    ".hpp", ".cc", ".rb", ".php", ".sh", ".bash", ".sql",
)
DEFAULT_DOCUMENT_EXTENSIONS: tuple[str, ...] = (".md", ".mdx", ".rst", ".txt")

# Canonical symbol kinds spoken by every consumer.
CANONICAL_KINDS: frozenset[str] = frozenset({
    "class", "function", "method", "interface", "protocol", "type", "enum",
    "struct", "const", "var", "field", "module", "import", "symbol",
})

# Language-native kind -> canonical kind.
KIND_SYNONYMS: dict[str, str] = {
    "fn": "function",
    "func": "function",
    "function": "function",
    "def": "function",
    "constructor": "function",
    "lambda": "function",
    "arrow": "function",
    "class": "class",
    "object": "class",
    "struct": "struct",
    "record": "struct",
    "data": "type",
    "typealias": "type",
    "type_alias": "type",
    "typedef": "type",
    "type": "type",
    "interface": "interface",
    "protocol": "protocol",
    "trait": "interface",
    "enum": "enum",
    "const": "const",
    "constant": "const",
    "let": "var",
    "var": "var",
    "field": "field",
    "property": "field",
    "member": "field",
    "method": "method",
    "import": "import",
    "use": "import",
    "module": "module",
    "package": "module",
}

# Tokens that carry no retrieval signal.
STOPWORDS: frozenset[str] = frozenset({
    "and", "for", "the", "with", "from", "that", "this", "into", "over",
    "what", "when", "where", "which", "make", "help", "need", "your", "you",
    "are", "not", "all", "any", "out", "use", "using", "via", "per", "each",
})


def detect_language(path: str) -> str:
    """Return the canonical language name for a path (defaults: 'text')."""
    lower = str(path).lower()
    suffix = "." + lower.rsplit(".", 1)[-1] if "." in lower else ""
    return EXT_TO_LANG.get(suffix, "text")


def file_kind(
    path: str,
    code_exts: Iterable[str] = (),
    doc_exts: Iterable[str] = (),
) -> str:
    """Classify a path as 'document', 'code', or 'file' for entity kinds.

    A profile may supply finer extension sets; when absent, the generic
    defaults are used.
    """
    lower = str(path).lower()
    suffix = "." + lower.rsplit(".", 1)[-1] if "." in lower else ""
    code_set = tuple(code_exts) or DEFAULT_CODE_EXTENSIONS
    doc_set = tuple(doc_exts) or DEFAULT_DOCUMENT_EXTENSIONS
    if suffix in doc_set:
        return "document"
    if suffix in code_set:
        return "code"
    return "file"


def normalize_kind(kind: str | None) -> str:
    """Map an arbitrary extractor/language-native kind onto the canonical set.

    Also handles namespaced enum str values (`EntityKind.SYMBOL` -> `symbol`).
    Unknown kinds collapse to a safe fallback so no symbol is ever dropped.
    """
    if not kind:
        return "symbol"
    k = str(kind).strip().lower()
    if "." in k:
        k = k.rsplit(".", 1)[-1]
    if k in KIND_SYNONYMS:
        return KIND_SYNONYMS[k]
    if k in CANONICAL_KINDS:
        return k
    if "symbol" in k:
        return "symbol"
    if "class" in k:
        return "class"
    if "struct" in k:
        return "struct"
    if "func" in k or "fn" in k or "def" in k:
        return "function"
    return "symbol"


def split_identifiers(text: str) -> tuple[str, ...]:
    """Split arbitrary identifiers/paths into lowercase search tokens.

    Handles camelCase, PascalCase, snake_case, kebab-case, dot-paths, and
    space-separated queries. Stopwords and single characters are dropped.
    Deterministic, sorted, deduplicated — safe for FTS OR-expansion.
    """
    tokens: set[str] = set()
    ngrams = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*", text)
    for ngram in ngrams:
        for part in re.split(r"[._/-]", ngram):
            if not part:
                continue
            part_lower = part.lower()
            if part_lower in STOPWORDS or len(part_lower) < 2:
                continue
            # Split camelCase / PascalCase sub-words (e.g. FrontendPersistencePort).
            boundaries = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+", part)
            if boundaries and any(len(b) > 1 for b in boundaries):
                tokens.update(
                    b.lower() for b in boundaries
                    if len(b) >= 2 and b.lower() not in STOPWORDS
                )
            tokens.add(part_lower)
    return tuple(sorted(tokens))


__all__ = [
    "CANONICAL_KINDS",
    "DEFAULT_CODE_EXTENSIONS",
    "DEFAULT_DOCUMENT_EXTENSIONS",
    "EXT_TO_LANG",
    "KIND_SYNONYMS",
    "LANG_EXTENSIONS",
    "STOPWORDS",
    "detect_language",
    "file_kind",
    "normalize_kind",
    "split_identifiers",
]
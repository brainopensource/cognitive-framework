from __future__ import annotations
import hashlib, re
from pathlib import Path
from ..core.models import Entity, Metric, ProviderResult
from .base import BaseProvider

LANGUAGES = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript", ".rs": "Rust", ".go": "Go", ".java": "Java", ".c": "C", ".cpp": "C++", ".h": "C/C++"}

class FilesystemProvider(BaseProvider):
    name = "filesystem"
    def collect(self, ctx):
        result = ProviderResult(self.name); docs = []
        for path in sorted(ctx.root.rglob("*")):
            if not path.is_file() or ctx.profile.is_excluded(path.relative_to(ctx.root)): continue
            rel = path.relative_to(ctx.root).as_posix(); suffix = path.suffix.lower()
            if suffix in ctx.profile.document_extensions:
                text = path.read_text(encoding="utf-8", errors="replace"); words = len(text.split()); tokens = max(1, round((len(text)/4 + words/.75)/2))
                docs.append((rel, text, tokens))
                result.entities.append(Entity(rel, "document", rel, None, {"path": rel, "kind": "doc", "bytes": path.stat().st_size, "lines": len(text.splitlines()), "words": words, "estimated_tokens": tokens, "title": next((x.strip().lstrip("# ") for x in text.splitlines() if x.startswith("#")), path.stem)}))
            elif suffix in LANGUAGES:
                text = path.read_text(encoding="utf-8", errors="replace")
                kind = "test" if any(part.lower() in {"test", "tests", "spec", "specs"} for part in path.parts) else "code"
                tokens = max(1, round(len(text)/4))
                result.entities.append(Entity(rel, kind, rel, None, {"path": rel, "kind": kind, "language": LANGUAGES[suffix], "bytes": path.stat().st_size, "lines": len(text.splitlines()), "words": len(text.split()), "estimated_tokens": tokens, "title": path.name}))
        result.metrics.extend([Metric("filesystem_entities", len(result.entities), "entities"), Metric("documents", len(docs), "documents")])
        result.metadata["fingerprint"] = hashlib.sha256("".join(x[0] + str(x[2]) for x in docs).encode()).hexdigest()
        return result

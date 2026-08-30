import json
from pathlib import Path
from ..core.models import Diagnostic, Entity, Metric, ProviderResult, Relation
from .base import BaseProvider

class KnowledgeProvider(BaseProvider):
    name = "knowledge"
    def collect(self, ctx):
        result = ProviderResult(self.name)
        files = {"catalog.jsonl": "document", "symbols.jsonl": "symbol", "code-map.jsonl": "code"}
        rows = {}
        for filename, kind in files.items():
            path = ctx.knowledge / filename
            rows[filename] = []
            if not path.exists():
                result.diagnostics.append(Diagnostic("warning", "MISSING_INDEX", f"missing {path}", str(path), self.name)); continue
            for line_no, line in enumerate(path.read_text().splitlines(), 1):
                try: rows[filename].append(json.loads(line))
                except json.JSONDecodeError as exc: result.diagnostics.append(Diagnostic("error", "INVALID_JSONL", str(exc), f"{path}:{line_no}", self.name))
            for row in rows[filename]:
                locator = row.get("path") or row.get("defined_in") or row.get("package_path") or row.get("canonical_owner", "")
                ident = row.get("canonical_id") or row.get("symbol") or row.get("subsystem") or locator
                result.entities.append(Entity(str(ident), kind, str(locator), row.get("authority"), row))
        linkpath = ctx.knowledge / "links.jsonl"
        if linkpath.exists():
            for line in linkpath.read_text().splitlines():
                row = json.loads(line); result.relations.append(Relation(row["source_id"], row["target_id"], row.get("relationship_type", "references"), str(linkpath)))
        result.metrics.append(Metric("knowledge_entities", len(result.entities), "entities")); result.artifacts.append(str(ctx.knowledge))
        return result

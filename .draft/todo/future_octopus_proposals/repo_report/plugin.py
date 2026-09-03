"""LDA plugin entry point for deterministic repository reporting."""
from __future__ import annotations

from ...core.models import Diagnostic, Metric, ProviderResult
from ...core.registry import PluginManifest
from .report import generate_report


class RepoReportProvider:
    name = "repo_report"

    def available(self, ctx) -> bool:
        return getattr(ctx, "root", None) is not None

    def collect(self, ctx) -> ProviderResult:
        result = generate_report(ctx.root, output_dir=ctx.root / ".lda" / "repo-report")
        out = ProviderResult(provider=self.name)
        out.metrics.extend(
            Metric(str(key), value, "count")
            for key, value in result["metrics"].items()
            if isinstance(value, (int, float))
        )
        out.artifacts.extend(result["artifacts"])
        out.metadata.update(result)
        if result["freshness"]["status"] != "FRESH":
            out.diagnostics.append(
                Diagnostic(
                    "warning",
                    "REPORT_STALE",
                    result["freshness"]["reason"],
                    provider=self.name,
                )
            )
        return out


class RepoReportPlugin:
    """Optional plugin compatible with ``PluginManager``."""

    name = "repo_report"
    manifest = PluginManifest(
        name=name,
        version="0.1.0",
        description="Incremental deterministic repository snapshot and report",
        tags=("snapshot", "freshness", "contracts", "graph", "metrics"),
    )

    def providers(self):
        return (RepoReportProvider(),)

    def analyzers(self):
        return ()

    def skeletonizers(self):
        return {}


def plugin():
    """Setuptools entry-point friendly factory."""
    return RepoReportPlugin()

from ..core.models import Metric, ProviderResult
from ..core.runner import run_command
from .base import BaseProvider

class GitProvider(BaseProvider):
    name = "git"
    def collect(self, ctx):
        code, out, err = run_command(["git", "rev-parse", "HEAD"], ctx.root)
        result = ProviderResult(self.name, metadata={"revision": out.strip() if code == 0 else None})
        if code == 0: result.metrics.append(Metric("git_revision_available", 1, "boolean"))
        else: result.diagnostics.append(__import__("tools.007_LLM_DOCS_ATLAS.core.models", fromlist=["Diagnostic"]).Diagnostic("warning", "GIT_UNAVAILABLE", err.strip(), provider=self.name))
        return result

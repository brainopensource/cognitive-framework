"""Deterministic repository report plugin for LDA.

The plugin consumes LDA's existing providers, IR and SQLite fact graph. It
does not replace LDA routing, emit ``.generated/knowledge`` files, or become
an authority source.
"""
__all__ = ["RepoReportPlugin", "generate_report"]


def __getattr__(name):
    if name == "RepoReportPlugin":
        from .plugin import RepoReportPlugin
        return RepoReportPlugin
    if name == "generate_report":
        from .report import generate_report
        return generate_report
    raise AttributeError(name)

"""Stable ``lda-mcp`` console entry point (delegates to the Atlas MCP server)."""
from importlib import import_module


def main(argv=None):
    return import_module("tools.007_LLM_DOCS_ATLAS.server_mcp").main(argv)


if __name__ == "__main__":
    raise SystemExit(main())

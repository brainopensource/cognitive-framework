"""Stable ``lda`` console entry point."""
from importlib import import_module

def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv[1:]
    if argv and argv[0] == "serve":
        return import_module("tools.lda.server").main(argv[1:])
    return import_module("tools.007_LLM_DOCS_ATLAS.cli").main(argv)

if __name__ == "__main__":
    raise SystemExit(main())

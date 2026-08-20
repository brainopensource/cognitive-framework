"""test/integration — end-to-end integration tests for vanguard/packages/.

Wave 0 (ADR-0075 F-19): __init__.py added so standard unittest discovery
(python3 -m unittest discover -s test -t .) collects these modules. They were
previously silently excluded because this directory lacked a package marker.

These tests require live external dependencies (Ollama, real filesystem mounts,
etc.) and are expected to fail in hermetic CI. Tests using unavailable services
MUST use @unittest.skipUnless; they must NOT silently pass.
"""

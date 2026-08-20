"""test/governance — governance and approval tests for vanguard/packages/.

Wave 0 (ADR-0075 F-19): __init__.py added so standard unittest discovery
(python3 -m unittest discover -s test -t .) collects these modules. They were
previously silently excluded because this directory lacked a package marker.

Note: test/governance/ had a __pycache__/ from prior ad-hoc invocations, which
created a false impression that the suite was being collected. Without __init__.py,
`discover -s test -t .` would skip all modules in this directory.
"""

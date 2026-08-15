"""`TEST-SCHEMA-001..012` — the T1 contract suite.

The Active MVP Contract registry runs `python3 -m unittest test.contracts.test_t1`
for every T1 requirement, so this module aggregates the per-packet suites
instead of holding assertions of its own. Each developer adds one import line
for their own module; nobody edits anybody else's.
"""

from .t1_dev1_canonicalisation import *  # noqa: F401,F403  REQ-SCHEMA-001
from .t1_dev1_primitives import *  # noqa: F401,F403  REQ-SCHEMA-002
from .t1_dev1_selectors import *  # noqa: F401,F403  REQ-SCHEMA-003
from .t1_wire_contracts import *  # noqa: F401,F403  REQ-SCHEMA-004..012
from .t7_artifact_graph import *  # noqa: F401,F403  REQ-GRAPH-001/REQ-BASELINE-001

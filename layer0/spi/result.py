# Wave-2 (2.1-A) compatibility shim: the canonical `Ok`/`Err`/`Result` ADT
# lives at vanguard/packages/domain/wire/result.py. This re-export keeps
# layer0/ and packs/ importing unmodified -- and, critically, means an
# `isinstance(x, Ok)` check here and one against a packages adapter's return
# value are checking the *same* class -- until 2.2-B deletes layer0/ entirely.
"""Re-export of the canonical SPI Result ADT.

See vanguard/packages/domain/wire/result.py -- the only place `Ok`/`Err`/
`Result` are defined.
"""

from __future__ import annotations

from vanguard.packages.domain.wire.result import Err, Ok, Result

__all__ = ["Err", "Ok", "Result"]

"""Table domain namespaced binding provider and effect adapter.

Owning contract: ADR-0088 §1.7, S10-B-01, REQ-BENCH-001.
Hexagonal boundary: Adapters package (imports only domain and ports).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from ...domain.canonicalisation.digest import digest_of
from ...ports.event_store import Result


@dataclass(frozen=True, slots=True)
class TableAdapterOutcome:
    """Outcome value object for table domain effects compatible with ports/kernel."""

    status: str
    occurrence: str
    cost: Mapping[str, int]
    result_digest: str = "sha256:" + "0" * 64
    detail: str = ""


class TableEffectAdapter:
    """Effect adapter executing tabular domain operations on TableWorldEnvironment."""

    def __init__(self, verb: str, environment: Any) -> None:
        self.name = verb
        self.verb = verb
        self._environment = environment

    def healthy(self) -> bool:
        return self._environment is not None

    def execute(self, request: Any) -> TableAdapterOutcome:
        args = getattr(request, "args", {}) or {}
        table_name = args.get("table") or args.get("table_name") or args.get("name")
        if not table_name:
            return TableAdapterOutcome(
                status="error",
                occurrence="not_occurred",
                cost={"usd_micros": 0},
                detail="table name is required in effect args",
            )

        if not hasattr(self._environment, "handle_read"):
            return TableAdapterOutcome(
                status="error",
                occurrence="not_occurred",
                cost={"usd_micros": 0},
                detail="environment does not support tabular operations",
            )

        if self.verb == "table.read":
            filter_key = args.get("filter_key") or args.get("filter_field") or args.get("column")
            filter_val = args.get("filter_val") or args.get("filter_value") or args.get("value")
            res: Result[dict[str, Any], str] = self._environment.handle_read(
                table_name, filter_key=filter_key, filter_val=filter_val
            )
            if not res.ok:
                return TableAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail=res.error or f"failed reading table {table_name}",
                )
            digest = digest_of(res.value)
            return TableAdapterOutcome(
                status="ok",
                occurrence="occurred",
                cost={"usd_micros": 1},
                result_digest=digest,
                detail=json.dumps(res.value, sort_keys=True),
            )

        elif self.verb == "table.patch":
            record_id = str(args.get("record_id") or args.get("id") or "")
            updates = args.get("updates") or args.get("patch") or args.get("data") or {}
            if not isinstance(updates, Mapping):
                return TableAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="updates must be an object",
                )
            res = self._environment.handle_patch(table_name, record_id, updates)
            if not res.ok:
                return TableAdapterOutcome(
                    status="error",
                    occurrence="undeterminable",
                    cost={"usd_micros": 0},
                    detail=res.error or f"failed patching table {table_name}",
                )
            digest = digest_of(res.value)
            return TableAdapterOutcome(
                status="ok",
                occurrence="occurred",
                cost={"usd_micros": 1},
                result_digest=digest,
                detail=json.dumps(res.value, sort_keys=True),
            )

        return TableAdapterOutcome(
            status="error",
            occurrence="not_occurred",
            cost={"usd_micros": 0},
            detail=f"unsupported table verb: {self.verb}",
        )


class TableBindingProvider:
    """Namespaced binding provider for the 'table' domain."""

    @property
    def namespace(self) -> str:
        return "table"

    @property
    def supported_verbs(self) -> tuple[str, ...]:
        return ("table.read", "table.patch", "table.diff")

    def create_adapter(self, verb: str, environment: Any, **kwargs: Any) -> TableEffectAdapter:
        if verb not in self.supported_verbs:
            raise ValueError(f"Verb {verb!r} not supported by TableBindingProvider")
        return TableEffectAdapter(verb, environment)

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
    """Outcome value object for the table domain adapter boundary."""

    status: str
    occurrence: str
    cost: Mapping[str, int]
    result_digest: str = "sha256:" + "0" * 64
    detail: str = ""

    @property
    def actual_cost(self) -> Mapping[str, int]:
        """Name used by the kernel outcome projection at the runtime seam."""
        return self.cost


class TableEffectAdapter:
    """Effect adapter executing tabular domain operations on TableWorldEnvironment."""

    def __init__(self, verb: str, environment: Any) -> None:
        self.name = verb
        self.verb = verb
        self._environment = environment

    def healthy(self) -> bool:
        if self._environment is None:
            return False
        method = "handle_read" if self.verb == "table.read" else "handle_patch"
        return callable(getattr(self._environment, method, None))

    def execute(self, request: Any) -> TableAdapterOutcome:
        args = getattr(request, "args", {}) or {}
        if not isinstance(args, Mapping):
            return TableAdapterOutcome(
                status="error",
                occurrence="not_occurred",
                cost={"usd_micros": 0},
                detail="effect args must be an object",
            )
        table_name = args.get("table") or args.get("table_name") or args.get("name")
        if not table_name:
            return TableAdapterOutcome(
                status="error",
                occurrence="not_occurred",
                cost={"usd_micros": 0},
                detail="table name is required in effect args",
            )

        required_method = "handle_read" if self.verb == "table.read" else "handle_patch"
        if not hasattr(self._environment, required_method):
            return TableAdapterOutcome(
                status="error",
                occurrence="not_occurred",
                cost={"usd_micros": 0},
                detail="environment does not support tabular operations",
            )

        if self.verb == "table.read":
            filter_key = args.get("filter_key") or args.get("filter_field") or args.get("column")
            filter_val = args.get("filter_val") or args.get("filter_value") or args.get("value")
            res: Result[dict[str, Any]] = self._environment.handle_read(
                table_name, filter_key=filter_key, filter_val=filter_val
            )
            if not res.ok:
                return TableAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail=(res.error.message if res.error else f"failed reading table {table_name}"),
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
            raw_record_id = args.get("record_id") or args.get("id")
            if raw_record_id is None or raw_record_id == "":
                return TableAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="record id is required in effect args",
                )
            record_id = str(raw_record_id)
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
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail=(res.error.message if res.error else f"failed patching table {table_name}"),
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
        # The shipped TableWorld pack declares only these two operations. Do
        # not advertise table.diff until the environment has a frozen diff
        # contract and implementation.
        return ("table.read", "table.patch")

    def create_adapter(self, verb: str, environment: Any, **kwargs: Any) -> TableEffectAdapter:
        if verb not in self.supported_verbs:
            raise ValueError(f"Verb {verb!r} not supported by TableBindingProvider")
        return TableEffectAdapter(verb, environment)

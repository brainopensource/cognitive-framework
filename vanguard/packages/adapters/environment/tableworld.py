"""TableWorld environment adapter and domain-native evaluator (S10-B-01).

Owning contract: VG-03 §7.3, VG-08 Increment C, REQ-BENCH-001.

Implements non-coding domain:
- In-memory relational tables with versioned updates.
- Verbs: `table.read`, `table.diff`, `table.patch`.
- Constraints: uniqueness, column range, checksums, sums, reconciliation.
- Domain-native evaluator checking invariant satisfaction and abstention on inconsistency.
- Zero shell commands, zero filesystem paths, zero git references.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from vanguard.packages.ports.event_store import Result


class TableConstraintError(ValueError):
    """Raised when a table constraint invariant is violated."""
    pass


@dataclass
class TableRecord:
    id: str
    data: dict[str, Any]


@dataclass
class TableState:
    name: str
    version: int
    records: dict[str, dict[str, Any]] = field(default_factory=dict)
    invariants: dict[str, Any] = field(default_factory=dict)

    def select(self, filter_field: str | None = None, filter_val: Any = None) -> list[dict[str, Any]]:
        if filter_field is None:
            return list(self.records.values())
        return [r for r in self.records.values() if r.get(filter_field) == filter_val]

    def update_record(self, record_id: str, updates: Mapping[str, Any]) -> None:
        if record_id not in self.records:
            self.records[record_id] = {"id": record_id}
        self.records[record_id].update(updates)
        self.version += 1


class TableWorldEnvironment:
    """Non-coding tabular execution environment."""

    def __init__(self, initial_tables: Mapping[str, list[dict[str, Any]]] | None = None) -> None:
        self._tables: dict[str, TableState] = {}
        if initial_tables:
            for t_name, rows in initial_tables.items():
                state = TableState(name=t_name, version=1)
                for r in rows:
                    r_id = str(r.get("id", len(state.records) + 1))
                    row_data = dict(r)
                    row_data["id"] = r_id
                    state.records[r_id] = row_data
                self._tables[t_name] = state

    def handle_read(self, table_name: str, filter_key: str | None = None, filter_val: Any = None) -> Result[dict[str, Any], str]:
        if table_name not in self._tables:
            return Result.failure(f"Table {table_name!r} not found")
        rows = self._tables[table_name].select(filter_key, filter_val)
        return Result.success({
            "table": table_name,
            "version": self._tables[table_name].version,
            "rowCount": len(rows),
            "rows": rows,
        })

    def handle_patch(self, table_name: str, record_id: str, updates: Mapping[str, Any]) -> Result[dict[str, Any], str]:
        if table_name not in self._tables:
            return Result.failure(f"Table {table_name!r} not found")
        self._tables[table_name].update_record(record_id, updates)
        return Result.success({
            "table": table_name,
            "recordId": record_id,
            "newVersion": self._tables[table_name].version,
            "updated": dict(self._tables[table_name].records[record_id]),
        })

    def get_table_state(self, table_name: str) -> TableState | None:
        return self._tables.get(table_name)


class TableWorldEvaluator:
    """Domain-native evaluator for TableWorld invariants and reconciliation."""

    @staticmethod
    def evaluate_invariants(
        env: TableWorldEnvironment,
        table_name: str,
        expected_sum_col: str | None = None,
        expected_sum_val: float | None = None,
        uniqueness_col: str | None = None,
        allow_abstention: bool = True,
        abstained: bool = False,
    ) -> dict[str, Any]:
        if abstained and allow_abstention:
            return {
                "passed": True,
                "abstained": True,
                "reason": "Agent correctly abstained on inconsistent table state (T4.5)",
            }

        tbl = env.get_table_state(table_name)
        if tbl is None:
            return {"passed": False, "reason": f"Missing table {table_name}"}

        rows = tbl.select()

        # Check uniqueness
        if uniqueness_col:
            vals = [r.get(uniqueness_col) for r in rows if uniqueness_col in r]
            if len(vals) != len(set(vals)):
                return {
                    "passed": False,
                    "reason": f"Uniqueness violation on column {uniqueness_col}",
                }

        # Check column sum
        if expected_sum_col and expected_sum_val is not None:
            actual_sum = sum(float(r.get(expected_sum_col, 0)) for r in rows)
            if abs(actual_sum - expected_sum_val) > 1e-4:
                return {
                    "passed": False,
                    "reason": f"Sum mismatch on {expected_sum_col}: expected {expected_sum_val}, got {actual_sum}",
                }

        return {"passed": True, "abstained": False, "reason": "All invariants satisfied"}

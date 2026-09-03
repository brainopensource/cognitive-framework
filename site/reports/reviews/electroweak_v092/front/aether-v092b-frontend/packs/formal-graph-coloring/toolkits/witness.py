"""Typed schemas for producing a Graph Coloring witness artifact; no self-grading."""

from __future__ import annotations


class GraphColoringWitnessToolkit:
    @staticmethod
    def schemas() -> tuple[dict, ...]:
        return ({
            "name": "graph_coloring.witness.write",
            "description": "Write a complete graph coloring assignment candidate",
            "inputSchema": {
                "type": "object",
                "required": ["path", "assignment"],
                "properties": {
                    "path": {"type": "string"},
                    "assignment": {
                        "type": "object",
                        "additionalProperties": {"type": "integer"},
                    },
                },
                "additionalProperties": False,
            },
        },)

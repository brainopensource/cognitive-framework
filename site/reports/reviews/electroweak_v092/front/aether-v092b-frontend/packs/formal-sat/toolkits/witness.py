"""Typed schemas for producing a SAT witness artifact; no self-grading."""

from __future__ import annotations


class SatWitnessToolkit:
    @staticmethod
    def schemas() -> tuple[dict, ...]:
        return ({
            "name": "sat.witness.write",
            "description": "Write a complete Boolean assignment candidate",
            "inputSchema": {
                "type": "object",
                "required": ["path", "assignment"],
                "properties": {
                    "path": {"type": "string"},
                    "assignment": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"},
                    },
                },
                "additionalProperties": False,
            },
        },)

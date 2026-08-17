"""A runtime module that is not the composition root constructing its own judge.

A-05 / LT-4: a component that can construct its own evaluator is a second judge.
"""

from __future__ import annotations

from ..adapters.evaluators.client import EvaluatorClient


def judge() -> EvaluatorClient:
    return EvaluatorClient()

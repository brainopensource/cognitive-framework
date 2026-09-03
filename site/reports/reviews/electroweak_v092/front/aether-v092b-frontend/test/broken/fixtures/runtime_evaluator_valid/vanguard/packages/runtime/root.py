"""The composition root. The one place the evaluator binding table may live."""

from __future__ import annotations

from ..adapters.evaluators.client import EvaluatorClient

EVALUATOR_BINDINGS = {"client": EvaluatorClient}

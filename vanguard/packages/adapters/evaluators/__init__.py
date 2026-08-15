"""Evaluator adapter family; sibling adapter families must not import this package."""

from .fake import FakeEvaluator

__all__ = ["FakeEvaluator"]

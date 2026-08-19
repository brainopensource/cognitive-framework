"""Retired with apps/coding (M3). Semantics live in packs/code-default/."""

from __future__ import annotations

import unittest


def load_tests(loader, tests, pattern):  # noqa: ARG001
    return unittest.TestSuite()

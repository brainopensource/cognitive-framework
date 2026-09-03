"""Unit tests for domain transform contracts and protocol conformance."""

from __future__ import annotations

import unittest
from typing import Mapping

from vanguard.packages.domain.transforms.contracts import (
    ArtifactTransform,
    TransformDiagnostic,
    TransformInput,
    TransformOutput,
    TransformResult,
    TransformSpec,
)


class DummyTransform:
    def __init__(self) -> None:
        self._spec = TransformSpec(
            transform_id="dummy.upper/1",
            version="1.0.0",
            input_schema="schema.text.utf8/1",
            output_schema="schema.text.utf8/1",
            deterministic=True,
        )

    @property
    def spec(self) -> TransformSpec:
        return self._spec

    def apply(self, payload: bytes, config: Mapping[str, object] | None = None) -> TransformOutput:
        text = payload.decode("utf-8")
        return TransformOutput(
            status="accepted",
            payload=text.upper().encode("utf-8"),
            output_schema=self._spec.output_schema,
            diagnostics=(TransformDiagnostic(code="UPPER_SUCCESS", severity="info", message="converted to upper"),),
            confidence_ppm=1_000_000,
        )


class TestTransformContracts(unittest.TestCase):
    def test_protocol_conformance(self) -> None:
        t = DummyTransform()
        self.assertIsInstance(t, ArtifactTransform)
        self.assertEqual(t.spec.transform_id, "dummy.upper/1")
        self.assertTrue(t.spec.deterministic)

    def test_apply_execution(self) -> None:
        t = DummyTransform()
        res = t.apply(b"hello world")
        self.assertEqual(res.status, "accepted")
        self.assertEqual(res.payload, b"HELLO WORLD")
        self.assertEqual(len(res.diagnostics), 1)
        self.assertEqual(res.diagnostics[0].code, "UPPER_SUCCESS")


if __name__ == "__main__":
    unittest.main()

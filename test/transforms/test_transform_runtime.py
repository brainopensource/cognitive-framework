"""Tests for TransformRuntime, byte bound enforcement, and error isolation."""

from __future__ import annotations

import hashlib
import unittest
from typing import Mapping

from vanguard.packages.domain.transforms.contracts import (
    ArtifactTransform,
    TransformDiagnostic,
    TransformOutput,
    TransformSpec,
)
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.transform_registry import TransformRegistry
from vanguard.packages.runtime.transform_runtime import TransformRuntime


class MemoryBlobStore:
    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}

    def put(self, data: bytes) -> Result[str]:
        digest = f"sha256:{hashlib.sha256(data).hexdigest()}"
        self._blobs[digest] = data
        return Result.success(digest)

    def get(self, digest: str) -> Result[bytes]:
        if digest in self._blobs:
            return Result.success(self._blobs[digest])
        return Result.fail("not_found", f"blob {digest} not found")

    def has(self, digest: str) -> bool:
        return digest in self._blobs


class JsonLowerTransform:
    def __init__(self, max_input: int = 1000) -> None:
        self._spec = TransformSpec(
            transform_id="test.lower/1",
            version="1.0.0",
            input_schema="schema.text.utf8/1",
            output_schema="schema.text.utf8/1",
            max_input_bytes=max_input,
        )

    @property
    def spec(self) -> TransformSpec:
        return self._spec

    def apply(self, payload: bytes, config: Mapping[str, object] | None = None) -> TransformOutput:
        text = payload.decode("utf-8")
        return TransformOutput(
            status="accepted",
            payload=text.lower().encode("utf-8"),
            output_schema=self._spec.output_schema,
        )


class TestTransformRuntime(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryBlobStore()
        self.registry = TransformRegistry()
        self.registry.register(JsonLowerTransform(max_input=100))
        self.runtime = TransformRuntime(self.store, self.registry)

    def test_successful_execution(self) -> None:
        put_res = self.store.put(b"HELLO WORLD")
        in_digest = put_res.value

        res = self.runtime.execute("test.lower/1", in_digest)
        self.assertEqual(res.status, "accepted")
        self.assertIsNotNone(res.output_digest)

        out_res = self.store.get(res.output_digest)
        self.assertEqual(out_res.value, b"hello world")

    def test_input_too_large_rejection(self) -> None:
        large_payload = b"A" * 200
        put_res = self.store.put(large_payload)
        in_digest = put_res.value

        res = self.runtime.execute("test.lower/1", in_digest)
        self.assertEqual(res.status, "rejected")
        self.assertEqual(res.diagnostics[0].code, "INPUT_TOO_LARGE")

    def test_transform_not_found(self) -> None:
        res = self.runtime.execute("unknown.transform/1", "sha256:123")
        self.assertEqual(res.status, "fatal_error")
        self.assertEqual(res.diagnostics[0].code, "TRANSFORM_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()

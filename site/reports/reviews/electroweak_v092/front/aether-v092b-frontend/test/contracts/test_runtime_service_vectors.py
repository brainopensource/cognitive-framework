"""B-O2-01: replay the frozen vg.4 RuntimeService golden vectors.

The corpus in ``schemas/v4/vectors/runtime-service/`` is data, not tests
(``schemas/v4/vectors/README.md``): it is the cross-language contract that
``vanguard/packages/runtime/service/contract.py`` and client-core's TypeScript
reader must both agree with. This module is the Python half of that replay;
``vanguard/clients/client-core/test/runtime-service-vectors.test.ts`` is the
TypeScript half, and both read the same bytes.

Per GV-1 every case is checked twice: once against the JSON Schema (when a
``$ref``-resolving engine is installed) and once against the handwritten
ingress validator, because the schema is the authority but the mirror is what
actually guards the command inbox at runtime.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.runtime.service.contract import (
    ContractError,
    validate_command,
    validate_frame_envelope,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_VECTORS = _REPO_ROOT / "schemas" / "v4" / "vectors" / "runtime-service"


def _cases(kind: str) -> list[tuple[str, Path]]:
    d = _VECTORS / kind
    return sorted((p.stem, p) for p in d.glob("*.json") if not p.name.endswith(".expect.json"))


def _ingest(frame: object) -> None:
    """Run one frame through the full ingress path, exactly as server.py does."""
    validate_frame_envelope(frame)
    validate_command(frame["command"])  # type: ignore[index]


class RuntimeServiceVectorCorpus(unittest.TestCase):
    """The corpus itself is well-formed (GV-1, GV-6)."""

    def test_corpus_is_present_and_non_trivial(self) -> None:
        self.assertTrue(_cases("valid"), "no valid vectors published")
        self.assertTrue(_cases("invalid"), "no invalid vectors published")

    def test_every_invalid_case_declares_its_expectation(self) -> None:
        for name, path in _cases("invalid"):
            with self.subTest(case=name):
                expect = path.with_name(f"{name}.expect.json")
                self.assertTrue(expect.is_file(), f"{name} has no .expect.json")
                body = json.loads(expect.read_text(encoding="utf-8"))
                self.assertIn("expectedKeyword", body)
                self.assertIn("expectedCode", body)

    def test_annotations_live_outside_the_instance(self) -> None:
        """GV-6: instances are pure data; notes go in a sibling .note.txt."""
        for kind in ("valid", "invalid"):
            for name, path in _cases(kind):
                with self.subTest(case=f"{kind}/{name}"):
                    body = json.loads(path.read_text(encoding="utf-8"))
                    self.assertNotIn("$comment", body)
                    self.assertNotIn("note", body)

    def test_corpus_covers_every_command(self) -> None:
        """GV-1 generalised: no command may be frozen without a positive vector."""
        from vanguard.packages.runtime.service.contract import COMMAND_RUN_SCOPE

        seen = {
            json.loads(p.read_text(encoding="utf-8"))["command"]["name"]
            for _, p in _cases("valid")
        }
        self.assertEqual(seen, set(COMMAND_RUN_SCOPE))


class RuntimeServiceVectorsPythonReader(unittest.TestCase):
    """Every vector produces the outcome the corpus declares."""

    def test_valid_vectors_are_accepted(self) -> None:
        for name, path in _cases("valid"):
            with self.subTest(case=name):
                frame = json.loads(path.read_text(encoding="utf-8"))
                try:
                    _ingest(frame)
                except ContractError as exc:
                    self.fail(f"golden vector {name} rejected: [{exc.code}] {exc}")

    def test_invalid_vectors_are_rejected_with_the_declared_code(self) -> None:
        for name, path in _cases("invalid"):
            with self.subTest(case=name):
                frame = json.loads(path.read_text(encoding="utf-8"))
                expect = json.loads(
                    path.with_name(f"{name}.expect.json").read_text(encoding="utf-8")
                )
                with self.assertRaises(ContractError, msg=f"{name} was accepted") as ctx:
                    _ingest(frame)
                self.assertEqual(
                    ctx.exception.code,
                    expect["expectedCode"],
                    f"{name}: wrong canonical error code",
                )


class RuntimeServiceVectorsJsonSchema(unittest.TestCase):
    """The same corpus, replayed through the schema that is the authority."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            import jsonschema  # noqa: F401
            import referencing  # noqa: F401
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise unittest.SkipTest(f"JSON-Schema engine unavailable: {exc}")

    def _validator(self):
        import jsonschema
        from referencing import Registry, Resource

        schema_dir = _REPO_ROOT / "schemas" / "v4"
        registry = Registry()
        for path in schema_dir.glob("*.schema.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            resource = Resource.from_contents(doc)
            registry = registry.with_resource(uri=path.name, resource=resource)
            if "$id" in doc:
                registry = registry.with_resource(uri=doc["$id"], resource=resource)
        root = json.loads((schema_dir / "runtime-service.schema.json").read_text("utf-8"))
        return jsonschema.Draft202012Validator(root, registry=registry)

    def test_valid_vectors_validate(self) -> None:
        validator = self._validator()
        for name, path in _cases("valid"):
            with self.subTest(case=name):
                errors = list(validator.iter_errors(json.loads(path.read_text("utf-8"))))
                self.assertEqual(errors, [], f"{name}: {[e.message for e in errors]}")

    def test_invalid_vectors_do_not_validate(self) -> None:
        validator = self._validator()
        for name, path in _cases("invalid"):
            with self.subTest(case=name):
                self.assertTrue(
                    list(validator.iter_errors(json.loads(path.read_text("utf-8")))),
                    f"{name} validated against the schema but must not",
                )


if __name__ == "__main__":
    unittest.main()

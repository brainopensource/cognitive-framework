"""SemVer and tool JSON Schema validation at composition time."""

from __future__ import annotations

import unittest

from layer0.registry.validator import (
    ManifestValidationError,
    compatible,
    parse_semver,
    satisfies,
    validate_manifest,
    validate_tool_schema,
)


class SemVerTests(unittest.TestCase):
    def test_parse_three_part(self) -> None:
        self.assertEqual(parse_semver("2.1.0"), (2, 1, 0))

    def test_caret_compat_same_major(self) -> None:
        self.assertTrue(satisfies("2.1.0", "^2.0.0"))
        self.assertTrue(satisfies("2.9.9", "^2.1.0"))
        self.assertFalse(satisfies("3.0.0", "^2.1.0"))
        self.assertFalse(satisfies("2.0.9", "^2.1.0"))

    def test_spi_range(self) -> None:
        self.assertTrue(satisfies("1.4.0", ">=1.0,<2"))
        self.assertFalse(satisfies("2.0.0", ">=1.0,<2"))
        self.assertTrue(satisfies("1.0.0", ">=1"))

    def test_plugin_requires_caret(self) -> None:
        self.assertTrue(compatible("mhf.index.tree-sitter", "1.2.0", ">=1"))
        self.assertFalse(compatible("mhf.index.tree-sitter", "0.9.0", ">=1"))


class ToolSchemaTests(unittest.TestCase):
    def test_valid_object_schema(self) -> None:
        validate_tool_schema(
            {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            }
        )

    def test_invalid_type_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            validate_tool_schema({"type": "widget"})

    def test_required_must_be_listed_properties(self) -> None:
        with self.assertRaises(ManifestValidationError):
            validate_tool_schema(
                {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["missing"],
                }
            )


class ManifestTests(unittest.TestCase):
    def _valid(self) -> dict:
        return {
            "api": "mhf.plugin/1",
            "id": "mhf.toolkit.echo",
            "version": "1.0.0",
            "provides": [{"spi": "IToolkit", "spi_version": ">=1.0,<2"}],
            "requires": [],
            "isolation": "subprocess",
            "capabilities": [{"verb": "echo", "selector": {"kind": "fs", "root": "/workspace"}}],
            "entry": "layer0.registry.worker:EchoToolkit",
            "tools": {
                "echo": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                }
            },
        }

    def test_valid_manifest(self) -> None:
        validate_manifest(self._valid())

    def test_bad_version(self) -> None:
        data = self._valid()
        data["version"] = "v1"
        with self.assertRaises(ManifestValidationError):
            validate_manifest(data)

    def test_unknown_isolation(self) -> None:
        data = self._valid()
        data["isolation"] = "chroot"
        with self.assertRaises(ManifestValidationError):
            validate_manifest(data)

    def test_spi_range_must_cover_v1(self) -> None:
        data = self._valid()
        data["provides"] = [{"spi": "IToolkit", "spi_version": ">=2"}]
        with self.assertRaises(ManifestValidationError):
            validate_manifest(data, hosted_spi_version="1.0")

    def test_bad_tool_schema_fails_at_composition(self) -> None:
        data = self._valid()
        data["tools"]["echo"] = {"type": "nope"}
        with self.assertRaises(ManifestValidationError):
            validate_manifest(data)


if __name__ == "__main__":
    unittest.main()

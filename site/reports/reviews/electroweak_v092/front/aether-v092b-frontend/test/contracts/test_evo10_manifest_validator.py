"""Contract test for EVO-10: Native Manifest Logical Validator & Linter.

Owning contract: EVO-10, GTS-13C §7.3, REQ-HARN-001.
Invariants:
- All built-in manifests pass logical validation.
- Verbs, sinks, risk tiers, selectors, budgets, constraints, and schemas fail closed on invalid values.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.agency.manifests.validator import (
    ManifestValidationError,
    validate_manifest,
    validate_manifest_dict,
    validate_manifest_pack,
)

MANIFESTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "vanguard"
    / "packages"
    / "agency"
    / "manifests"
)


class TestEvo10ManifestValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = ManifestLoader(manifests_base_dir=MANIFESTS_DIR)

    def test_all_builtin_manifest_packs_pass_validation(self) -> None:
        """Verify all production agent manifest packs pass logical validation."""
        builtin_packs = [
            "vg-code-default",
            "vg-code-explain",
            "vg-code-lex",
            "vg-code-claude-shaped",
            "vg-code-opencode-shaped",
        ]
        for pack_name in builtin_packs:
            with self.subTest(pack=pack_name):
                pack = self.loader.load_pack(pack_name)
                validate_manifest_pack(pack)
                validate_manifest(pack)

    def test_negative_budget_fails_closed(self) -> None:
        """Verify negative budget allocation fails validation."""
        valid_raw = {
            "harness": "test-agent",
            "capabilities": [
                {"verb": "fs.read", "sink": "observation", "risk": "low", "selector": {"kind": "fs"}}
            ],
            "budget": {
                "tokens": -100,
                "micros": 5000,
            },
        }
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(valid_raw)

        # Nested budget
        valid_raw["budget"] = {"limits": {"tokens": -1}}
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(valid_raw)

    def test_invalid_max_depth_fails_closed(self) -> None:
        """Verify constraints.max_depth outside [1, 16] fails validation."""
        raw = {
            "harness": "test-agent",
            "capabilities": [
                {"verb": "fs.read", "sink": "observation", "risk": "low", "selector": {"kind": "fs"}}
            ],
            "constraints": {"max_depth": 0},
        }
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(raw)

        raw["constraints"] = {"max_depth": 17}
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(raw)

        raw["constraints"] = {"max_depth": "unlimited"}
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(raw)

        # Valid depth (e.g. 4)
        raw["constraints"] = {"max_depth": 4}
        validate_manifest_dict(raw)

    def test_invalid_sink_and_risk_tier_fail_closed(self) -> None:
        """Verify invalid capability sinks and risk tiers fail closed."""
        raw_invalid_sink = {
            "harness": "test-agent",
            "capabilities": [
                {"verb": "fs.read", "sink": "arbitrary_backdoor_sink", "risk": "low", "selector": {}}
            ],
        }
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(raw_invalid_sink)

        raw_invalid_risk = {
            "harness": "test-agent",
            "capabilities": [
                {"verb": "fs.read", "sink": "observation", "risk": "super_extreme", "selector": {}}
            ],
        }
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(raw_invalid_risk)

    def test_invalid_tool_json_schema_fails_closed(self) -> None:
        """Verify invalid tool parameter schemas fail closed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            manifest_file = tmp_path / "manifest.json"
            tool_file = tmp_path / "bad-tool.json"

            tool_file.write_text(
                json.dumps({
                    "name": "bad_tool",
                    "verb": "fs.read",
                    "schema": {"type": "not_a_valid_json_type", "properties": {}},
                }),
                encoding="utf-8",
            )

            manifest_file.write_text(
                json.dumps({
                    "harness": "test-pack",
                    "capabilities": [{"verb": "fs.read", "sink": "observation", "risk": "low", "selector": {}}],
                    "components": {"tools": ["bad-tool.json"]},
                }),
                encoding="utf-8",
            )

            with self.assertRaises(ManifestValidationError):
                validate_manifest(manifest_file, base_dir=tmp_path)

    def test_scope_undeclared_action_fails_closed(self) -> None:
        """Verify scope actions referencing undeclared capabilities fail validation."""
        raw = {
            "harness": "test-agent",
            "capabilities": [
                {"verb": "fs.read", "sink": "observation", "risk": "low", "selector": {}}
            ],
            "scope": {
                "actions": ["fs.read", "undeclared.nuke_everything"]
            },
        }
        with self.assertRaises(ManifestValidationError):
            validate_manifest_dict(raw)


if __name__ == "__main__":
    unittest.main()

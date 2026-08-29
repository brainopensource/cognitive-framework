"""Contract test for EVO-02: Hierarchical Profile Configuration Model.

Owning contract: EVO-02, ADR-0089 §Decision 1,5, ADR-0096 §14.5.
Invariants:
- Profile overrides can be loaded from YAML, JSON, or dict.
- Overrides merge cleanly on top of system presets without violating layer boundaries.
- Attempts to widen access, containment, or weaken fail-closed invariants fail closed with ExecutionProfileError.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.profiles import (
    ExecutionProfile,
    ExecutionProfileError,
    PRESETS,
    load_custom_profile,
)


class TestEvo02ProfileConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_load_custom_profile_from_dict(self) -> None:
        """Verify profile loaded from dictionary overrides preset defaults."""
        profile = load_custom_profile(
            {"approval_default": "deny", "capture_required": True},
            base_preset="local",
        )
        self.assertIsInstance(profile, ExecutionProfile)
        self.assertEqual(profile.approval_default, "deny")
        self.assertEqual(profile.capture_required, True)
        self.assertEqual(profile.workspace_access, "workspace-write")  # inherited from local

    def test_load_custom_profile_from_json(self) -> None:
        """Verify profile loaded from JSON file."""
        json_file = self.tmp_path / "profile.json"
        json_file.write_text(
            json.dumps({
                "base": "product",
                "workspace": {"access": "read-only"},
                "approval": {"default": "deny"},
            }),
            encoding="utf-8",
        )

        profile = load_custom_profile(json_file)
        self.assertIsInstance(profile, ExecutionProfile)
        self.assertEqual(profile.workspace_access, "read-only")
        self.assertEqual(profile.approval_default, "deny")
        self.assertEqual(profile.retention, "standard")  # inherited from product

    def test_load_custom_profile_from_yaml(self) -> None:
        """Verify profile loaded from YAML file."""
        yaml_file = self.tmp_path / "vanguard.yaml"
        yaml_file.write_text(
            """
base: local
workspace:
  access: workspace-write
approval:
  default: ask
capture:
  required: true
""",
            encoding="utf-8",
        )

        profile = load_custom_profile(yaml_file)
        self.assertIsInstance(profile, ExecutionProfile)
        self.assertEqual(profile.approval_default, "ask")
        self.assertEqual(profile.capture_required, True)

    def test_widening_containment_or_access_fails_closed(self) -> None:
        """Verify attempts to widen containment or weaken constraints fail closed."""
        # Attempt to widen process containment from platform-sandbox to host
        with self.assertRaises(ExecutionProfileError):
            load_custom_profile(
                {"process_backend": "host"},
                base_preset="sandboxed",
            )

        # Attempt to weaken capture on product preset
        with self.assertRaises(ExecutionProfileError):
            load_custom_profile(
                {"capture_required": False},
                base_preset="product",
            )

    def test_invalid_syntax_and_missing_file_fail_closed(self) -> None:
        """Verify missing files or malformed data raise ExecutionProfileError."""
        with self.assertRaises(ExecutionProfileError):
            load_custom_profile(self.tmp_path / "nonexistent.json")

        bad_json = self.tmp_path / "bad.json"
        bad_json.write_text("not { json : valid", encoding="utf-8")
        with self.assertRaises(ExecutionProfileError):
            load_custom_profile(bad_json)


if __name__ == "__main__":
    unittest.main()

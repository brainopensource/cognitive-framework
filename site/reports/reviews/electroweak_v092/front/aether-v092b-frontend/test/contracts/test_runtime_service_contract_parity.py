"""B-O2-01: the handwritten vg.4 mirror may not drift from the JSON Schema.

``vanguard/packages/runtime/service/contract.py`` re-states the RuntimeService
wire contract in Python so ingress can fail closed without a ``$ref``-resolving
JSON-Schema engine. That mirror is only trustworthy while it is provably equal
to ``schemas/v4/runtime-service.schema.json``, which is the authority.

Every assertion below derives its expectation *from the schema file* rather
than restating it, so a schema change that the mirror does not follow (or a
mirror change the schema does not sanction) fails here instead of silently
widening or narrowing what the service accepts.

Owning contract: ADR-0101, ADR-0103; guidelines.md §9.2 "vg.4 field shape".
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.runtime.service.contract import (
    APPROVAL_DECISION_ALLOWED_FIELDS,
    APPROVAL_DECISION_REQUIRED_FIELDS,
    COMMAND_ALLOWED_PAYLOAD_FIELDS,
    COMMAND_REQUIRED_PAYLOAD_FIELDS,
    COMMAND_RUN_SCOPE,
    ERROR_CODES,
    RUN_SCOPE_FORBIDDEN,
    RUN_SCOPE_OPTIONAL,
    RUN_SCOPE_REQUIRED,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA = _REPO_ROOT / "schemas" / "v4" / "runtime-service.schema.json"


def _defs() -> dict:
    return json.loads(_SCHEMA.read_text(encoding="utf-8"))["$defs"]


class RuntimeServiceContractParity(unittest.TestCase):
    """The Python mirror equals the frozen vg.4 schema, field for field."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.defs = _defs()
        cls.commands = {
            name[: -len("Command")]: body
            for name, body in cls.defs.items()
            if name.endswith("Command") and name != "Command"
        }

    # -- command roster ----------------------------------------------------

    def test_command_roster_matches_schema_oneof(self) -> None:
        """No command exists in one half of the contract and not the other."""
        union = {
            ref["$ref"].rsplit("/", 1)[-1][: -len("Command")]
            for ref in self.defs["Command"]["oneOf"]
        }
        self.assertEqual(union, set(self.commands))
        self.assertEqual(set(COMMAND_RUN_SCOPE), union)
        self.assertEqual(set(COMMAND_REQUIRED_PAYLOAD_FIELDS), union)
        self.assertEqual(set(COMMAND_ALLOWED_PAYLOAD_FIELDS), union)

    # -- payload field algebra --------------------------------------------

    def test_allowed_payload_fields_match_schema(self) -> None:
        for name, body in self.commands.items():
            with self.subTest(command=name):
                payload = body["properties"]["payload"]
                self.assertIs(
                    payload.get("additionalProperties"),
                    False,
                    "every command payload must reject unknown fields",
                )
                self.assertEqual(
                    set(payload.get("properties", {})),
                    set(COMMAND_ALLOWED_PAYLOAD_FIELDS[name]),
                )

    def test_required_payload_fields_match_schema(self) -> None:
        for name, body in self.commands.items():
            with self.subTest(command=name):
                payload = body["properties"]["payload"]
                self.assertEqual(
                    set(payload.get("required", [])),
                    set(COMMAND_REQUIRED_PAYLOAD_FIELDS[name]),
                )

    def test_required_payload_fields_are_a_subset_of_allowed(self) -> None:
        for name in self.commands:
            with self.subTest(command=name):
                self.assertLessEqual(
                    set(COMMAND_REQUIRED_PAYLOAD_FIELDS[name]),
                    set(COMMAND_ALLOWED_PAYLOAD_FIELDS[name]),
                )

    # -- run scoping -------------------------------------------------------

    def test_run_scope_matches_schema_runid_shape(self) -> None:
        """`runId: {"const": ""}` means forbidden; required-list membership means required."""
        for name, body in self.commands.items():
            with self.subTest(command=name):
                run_id = body["properties"]["runId"]
                required = "runId" in body.get("required", [])
                if run_id.get("const") == "":
                    expected = RUN_SCOPE_FORBIDDEN
                elif required:
                    expected = RUN_SCOPE_REQUIRED
                else:
                    expected = RUN_SCOPE_OPTIONAL
                self.assertEqual(COMMAND_RUN_SCOPE[name], expected)

    def test_command_objects_reject_unknown_top_level_fields(self) -> None:
        for name, body in self.commands.items():
            with self.subTest(command=name):
                self.assertIs(body.get("additionalProperties"), False)

    # -- shared vocabularies ----------------------------------------------

    def test_error_codes_match_schema_enum(self) -> None:
        self.assertEqual(set(self.defs["ErrorCode"]["enum"]), set(ERROR_CODES))

    def test_approval_decision_is_a_reference_not_a_copy(self) -> None:
        """One definition of the signed decision body, not two that can drift."""
        slot = self.defs["ApprovalDecision"]
        self.assertEqual(slot.get("$ref"), "approval-decision.schema.json")
        self.assertNotIn("properties", slot)

    def test_approval_decision_signature_shape_is_not_weakened(self) -> None:
        """Ingress must demand the 128-hex Ed25519 form both signers emit."""
        from vanguard.packages.runtime.service import contract as mod

        decision = self._approval_decision()
        self.assertEqual(
            decision["properties"]["signature"]["pattern"],
            mod._SIGNATURE_RE.pattern,
        )

    def _approval_decision(self) -> dict:
        return json.loads(
            (_REPO_ROOT / "schemas" / "v4" / "approval-decision.schema.json").read_text("utf-8")
        )

    def test_approval_decision_fields_match_schema(self) -> None:
        decision = self._approval_decision()
        self.assertIs(decision.get("additionalProperties"), False)
        self.assertEqual(set(decision["properties"]), set(APPROVAL_DECISION_ALLOWED_FIELDS))
        self.assertEqual(set(decision["required"]), set(APPROVAL_DECISION_REQUIRED_FIELDS))

    def test_command_frame_shell_matches_schema(self) -> None:
        from vanguard.packages.runtime.service import contract as mod

        frame = self.defs["CommandFrame"]
        self.assertIs(frame.get("additionalProperties"), False)
        self.assertEqual(set(frame["properties"]), set(mod._FRAME_TOP_LEVEL_FIELDS))
        self.assertEqual(frame["properties"]["version"]["const"], "vg.4")

    def test_command_top_level_fields_match_schema(self) -> None:
        from vanguard.packages.runtime.service import contract as mod

        for name, body in self.commands.items():
            with self.subTest(command=name):
                self.assertEqual(
                    set(body["properties"]), set(mod._COMMAND_TOP_LEVEL_FIELDS)
                )


if __name__ == "__main__":
    unittest.main()

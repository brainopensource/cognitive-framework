"""M-5a semantic payload schemas and frozen JCS vectors."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.canonicalisation.jcs import canonicalise

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_BY_KIND = {
    "GoalDeclared": "goal_declared.schema.json",
    "PlanRevised": "plan_revised.schema.json",
    "StrategyChanged": "strategy_changed.schema.json",
    "ProgressAssessed": "progress_assessed.schema.json",
    "ContextCompacted": "context_compacted.schema.json",
}


class SemanticVectors(unittest.TestCase):
    def test_all_five_payloads_validate_and_have_pinned_jcs_bytes(self) -> None:
        vectors = json.loads((ROOT / "test/fixtures/m5a_semantic_vectors.json").read_text())
        self.assertEqual({item["payload"]["kind"] for item in vectors}, set(SCHEMA_BY_KIND))
        for vector in vectors:
            kind = vector["payload"]["kind"]
            schema = json.loads((ROOT / "schemas/mhf" / SCHEMA_BY_KIND[kind]).read_text())
            payload_fields = {
                key: value for key, value in vector["payload"].items() if key != "kind"
            }
            errors = sorted(Draft202012Validator(schema).iter_errors(payload_fields), key=str)
            self.assertEqual(errors, [], kind)
            self.assertEqual(canonicalise(vector["payload"]), vector["canonical"], kind)
            self.assertEqual(digest_of(vector["payload"]), vector["digest"], kind)


if __name__ == "__main__":
    unittest.main()

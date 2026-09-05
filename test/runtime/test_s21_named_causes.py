"""S21: a zero-turn run must name its cause (`REQ-TRUST-001`).

`instrument_error` alone is a category, not a finding. The provider never
answering, a daemon timing out, and a model emitting a shape the translator
refuses are three different facts that all reduced to one word — and every one
of them read like the model scoring zero.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch
from pathlib import Path

from vanguard.packages.runtime.lab_driver import run_lab_task
from vanguard.packages.runtime.model_selection import ModelUnavailable, select_model
from vanguard.packages.runtime.outcome_labels import classify_instrument_error
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.scoring import score_arm

ROOT = Path(__file__).resolve().parents[2]
GREENFIELD = ROOT / "benchmarks" / "greenfield" / "greenfield-api-html"
DOGFOOD_01 = ROOT / "benchmarks" / "greenfield" / "dogfood-01-multi-turn-file-rollback"


def _daemon() -> bool:
    try:
        select_model("ollama", model_name="llama3.2:3b")
        return True
    except ModelUnavailable:
        return False


class CausesAreNamed(unittest.TestCase):
    def test_each_known_failure_gets_its_own_label(self) -> None:
        cases = {
            "multiple actions in one proposal are unsupported":
                "instrument_error:multi_action_proposal",
            "Ollama request failed: timed out": "instrument_error:provider_timeout",
            "'x' is not pulled; installed: y": "instrument_error:model_tag_absent",
            "no daemon answering at http://h": "instrument_error:provider_unreachable",
            "OPENROUTER_API_KEY is not set": "instrument_error:provider_key_missing",
            "'m' is not in the free band; refusing to spend":
                "instrument_error:paid_model_refused",
            "model_not_invoked": "instrument_error:model_not_invoked",
        }
        for detail, expected in cases.items():
            with self.subTest(detail=detail):
                self.assertEqual(classify_instrument_error(detail), expected)

    def test_an_unseen_message_is_unclassified_not_invented(self) -> None:
        """Inventing a category for a message nobody has seen is how a
        taxonomy starts lying."""

        self.assertEqual(classify_instrument_error("a brand new failure"),
                         "instrument_error:unclassified")

    def test_an_empty_detail_is_unclassified(self) -> None:
        self.assertEqual(classify_instrument_error(""),
                         "instrument_error:unclassified")
        self.assertEqual(classify_instrument_error(None),
                         "instrument_error:unclassified")

    def test_model_not_invoked_does_not_shadow_a_specific_cause(self) -> None:
        """It sits last on purpose: it is the shape, not the cause."""

        detail = "model_not_invoked after Ollama request failed: timed out"
        self.assertEqual(classify_instrument_error(detail),
                         "instrument_error:provider_timeout")


class TheDriverEmitsTheLabel(unittest.TestCase):
    def test_a_missing_workspace_keeps_its_own_label(self) -> None:
        result = run_lab_task("vg-code-default", "/nowhere/at/all")
        self.assertEqual(result["outcome"], "inconclusive:workspace_missing")

    def test_an_absent_tag_is_labelled_not_soup(self) -> None:
        with patch(
            "vanguard.packages.runtime.model_selection._ollama_tags",
            return_value=("installed:tag",),
        ):
            result = run_lab_task(
                "vg-code-default", DOGFOOD_01, model_port="ollama",
                model_name="definitely-not-a-pulled-tag",
            )
        self.assertEqual(result["outcome"], "instrument_error:model_tag_absent")
        self.assertNotEqual(result["outcome"], StopReason.INSTRUMENT_ERROR)

    def test_every_labelled_cause_stays_in_the_denominator(self) -> None:
        """A named instrument error is still a counted task."""

        score = score_arm("live", [
            {"taskId": "a", "outcome": "instrument_error:multi_action_proposal"},
            {"taskId": "b", "outcome": "instrument_error:provider_timeout"},
            {"taskId": "c", "outcome": StopReason.ORACLE_GREEN},
        ])
        self.assertEqual(score.denominator, 3)
        self.assertEqual(score.resolved, 1)
        self.assertEqual(set(score.inconclusive), {"a", "b"})


class GreenfieldIsAValidWorkspace(unittest.TestCase):
    """S21-A-02. An empty tree is a greenfield task, not a broken one."""

    def test_the_workspace_exists_and_carries_its_brief(self) -> None:
        self.assertTrue(GREENFIELD.is_dir())
        self.assertTrue((GREENFIELD / "TASK.md").is_file())

    def test_it_has_no_source_tree_yet_which_is_the_point(self) -> None:
        self.assertFalse((GREENFIELD / "src").exists())

    def test_compose_does_not_refuse_it(self) -> None:
        """Falsified hypothesis: compose refusing an empty tree."""

        from vanguard.packages.runtime.root import Runtime

        harness = Runtime.compose("vg-code-default", episode_id="e")
        self.assertEqual(len(harness.verbs), 5)
        self.assertGreater(len(harness.tool_schemas), 0)

    def test_declared_index_accepts_an_empty_tree(self) -> None:
        """The default tamper/index component accepts an empty tree."""

        from vanguard.packages.runtime.root import Runtime

        self.assertIsNotNone(
            Runtime.compose("vg-code-default", episode_id="e").index_component)

    def test_the_mock_runs_an_episode_on_it(self) -> None:
        """The loop is not skipped for an empty workspace."""

        result = run_lab_task("vg-code-default", GREENFIELD, max_attempts=1)
        self.assertGreater(result["turns"], 0)


@unittest.skipUnless(_daemon(), "ollama daemon or llama3.2:3b absent — "
                                "skipped closed, not passed")
class ALiveModelTakesAToolCallingTurn(unittest.TestCase):
    """S21-A-03. Skip-closed when the daemon is down; never a fake green."""

    #: `llama3.2:3b` tool-calls intermittently: measured 4/6 single-shot runs
    #: against this pack. The claim under test is "this model *can* drive the
    #: loop", so it is given a small budget of independent runs rather than one
    #: -- and if none of them tool-calls, that is a real finding and the test
    #: fails. Retrying until green would be padding; not retrying at all would
    #: assert determinism the model does not have.
    TOOL_CALL_BUDGET = 3

    def test_dogfood_01_records_a_proposal_with_a_verb(self) -> None:
        outcomes = []
        for _ in range(self.TOOL_CALL_BUDGET):
            result = run_lab_task("vg-code-default", DOGFOOD_01,
                                  model_port="ollama", model_name="llama3.2:3b",
                                  max_turns=4, max_attempts=1)
            verbs = [entry["verb"] for entry in result["session"] if entry["verb"]]
            outcomes.append(result["outcome"])
            if verbs:
                self.assertTrue(all(isinstance(verb, str) for verb in verbs))
                return
        self.fail(f"no tool-calling turn in {self.TOOL_CALL_BUDGET} runs; "
                  f"outcomes={outcomes}")

    def test_the_run_is_labelled_with_its_port(self) -> None:
        result = run_lab_task("vg-code-default", DOGFOOD_01, model_port="ollama",
                              model_name="llama3.2:3b", max_turns=2,
                              max_attempts=1)
        self.assertEqual(result["modelPort"], "ollama")
        self.assertNotEqual(result["modelPort"], "mock")

    def test_no_live_run_is_ever_reported_green_here(self) -> None:
        """Nothing in this suite may assert a resolved task."""

        result = run_lab_task("vg-code-default", DOGFOOD_01, model_port="ollama",
                              model_name="llama3.2:3b", max_turns=2,
                              max_attempts=1)
        self.assertNotEqual(result["outcome"], StopReason.ORACLE_GREEN)


if __name__ == "__main__":
    unittest.main()

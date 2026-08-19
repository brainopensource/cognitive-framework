from __future__ import annotations

import unittest

from dataclasses import replace

from layer0.kernel.model import FailurePath
from layer0.spi.types_gen import EffectContext, EventKind, SinkClass
from test.layer0.support import build_kernel, echo_request, parent_scope


class DispatchTests(unittest.TestCase):
    def test_happy_path_records_effect_and_budget(self) -> None:
        kernel, store = build_kernel()
        result = kernel.dispatch(
            echo_request(),
            EffectContext(principal="episode", run_id="run-1"),
            requested_scope=parent_scope(),
        )
        self.assertTrue(result.ok)
        kinds = [event.kind for event in result.events]
        self.assertIn(EventKind.AUTHORIZATION_REQUESTED.value, kinds)
        self.assertIn(EventKind.EFFECT_STARTED.value, kinds)
        self.assertIn(EventKind.EFFECT_COMPLETED.value, kinds)
        self.assertEqual(len(store.envelopes), len(result.events))

    def test_unknown_verb_rejects_before_lease(self) -> None:
        kernel, _store = build_kernel()
        missing = replace(echo_request(), verb="missing", sink=SinkClass.PRIVILEGED)
        result = kernel.dispatch(
            missing,
            EffectContext(principal="episode", run_id="run-1"),
            requested_scope=parent_scope(),
        )
        self.assertEqual(result.failure, FailurePath.UNKNOWN_ACTION)
        self.assertEqual(kernel._governor.remaining("tokens"), 10**6)

    def test_intent_append_failure_alarms_and_skips_effect(self) -> None:
        kernel, store = build_kernel()

        class Boom:
            def append_intent(self, event: object) -> None:
                raise RuntimeError("wal")

        kernel._ledger = Boom()  # type: ignore[method-assign]
        result = kernel.dispatch(
            echo_request(),
            EffectContext(principal="episode", run_id="run-1"),
            requested_scope=parent_scope(),
        )
        self.assertEqual(result.failure, FailurePath.INTENT_APPEND_FAILED)
        kinds = [event.kind for event in result.events]
        self.assertIn(EventKind.KERNEL_ALARM.value, kinds)
        _ = store

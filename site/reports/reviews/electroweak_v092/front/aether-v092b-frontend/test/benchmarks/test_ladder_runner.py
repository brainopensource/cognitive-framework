from __future__ import annotations

import unittest

from benchmarks.ladder_runner import LiveBudget, LiveBudgetExceeded


class _CostedModel:
    def __init__(self, costs: list[float]) -> None:
        self.costs = list(costs)
        self.calls = 0

    def propose(self, context, tools, sampling):
        cost = self.costs[self.calls]
        self.calls += 1
        return {"kind": "finish", "cost_usd": cost}


class TestLiveBudget(unittest.TestCase):
    def test_request_cap_refuses_before_an_extra_provider_call(self) -> None:
        delegate = _CostedModel([0.01, 0.01])
        guarded = LiveBudget(max_cost_usd=1.0, max_calls=1).guard(delegate)

        guarded.propose({}, (), {})
        with self.assertRaises(LiveBudgetExceeded):
            guarded.propose({}, (), {})

        self.assertEqual(delegate.calls, 1)

    def test_cost_cap_refuses_before_the_next_provider_call(self) -> None:
        delegate = _CostedModel([0.05, 0.01])
        budget = LiveBudget(max_cost_usd=0.05, max_calls=10)
        guarded = budget.guard(delegate)

        guarded.propose({}, (), {})
        with self.assertRaises(LiveBudgetExceeded):
            guarded.propose({}, (), {})

        self.assertEqual(delegate.calls, 1)
        self.assertEqual(budget.calls, 1)
        self.assertAlmostEqual(budget.cost_usd, 0.05)


if __name__ == "__main__":
    unittest.main()

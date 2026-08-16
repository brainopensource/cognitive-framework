"""Phase 3 Frontier Coding Challenges for Vanguard Agentic Harness.

Defines challenging Tier 3-5 real coding tasks covering algorithmic logic,
concurrency, resource management, and stateful protocols.
"""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class CodingChallenge:
    challenge_id: str
    tier: int
    title: str
    description: str
    initial_files: Mapping[str, str]
    test_oracle_code: str


CHALLENGES = {
    "task-p3-01-token-bucket": CodingChallenge(
        challenge_id="task-p3-01-token-bucket",
        tier=3,
        title="Thread-Safe Token Bucket Rate Limiter with Monotonic Refill",
        description=(
            "Fix the concurrency and refill drift bug in TokenBucketRateLimiter. "
            "The limiter must replenish tokens accurately based on monotonic elapsed time, "
            "clamp to max_burst, and prevent race conditions when consumed concurrently."
        ),
        initial_files={
            "limiter.py": (
                "import time\n"
                "import threading\n\n"
                "class TokenBucket:\n"
                "    def __init__(self, rate_per_sec: float, max_burst: int):\n"
                "        self.rate = rate_per_sec\n"
                "        self.max_burst = max_burst\n"
                "        self.tokens = float(max_burst)\n"
                "        self.last_update = time.time()\n\n"
                "    def consume(self, tokens: int = 1) -> bool:\n"
                "        # Bug: fails to lock and uses non-monotonic time\n"
                "        now = time.time()\n"
                "        elapsed = now - self.last_update\n"
                "        self.tokens += elapsed * self.rate\n"
                "        if self.tokens > self.max_burst:\n"
                "            self.tokens = float(self.max_burst)\n"
                "        self.last_update = now\n"
                "        if self.tokens >= tokens:\n"
                "            self.tokens -= tokens\n"
                "            return True\n"
                "        return False\n"
            ),
        },
        test_oracle_code=(
            "import unittest\n"
            "import time\n"
            "import threading\n"
            "from limiter import TokenBucket\n\n"
            "class TestTokenBucket(unittest.TestCase):\n"
            "    def test_burst_and_refill(self):\n"
            "        tb = TokenBucket(rate_per_sec=10.0, max_burst=5)\n"
            "        for _ in range(5):\n"
            "            self.assertTrue(tb.consume(1))\n"
            "        self.assertFalse(tb.consume(1))\n"
            "        time.sleep(0.25)\n"
            "        self.assertTrue(tb.consume(2))\n\n"
            "    def test_concurrent_consumption(self):\n"
            "        tb = TokenBucket(rate_per_sec=0.0, max_burst=100)\n"
            "        consumed = []\n"
            "        def worker():\n"
            "            for _ in range(10):\n"
            "                if tb.consume(1):\n"
            "                    consumed.append(1)\n"
            "        threads = [threading.Thread(target=worker) for _ in range(10)]\n"
            "        for t in threads: t.start()\n"
            "        for t in threads: t.join()\n"
            "        self.assertEqual(len(consumed), 100)\n"
            "        self.assertEqual(tb.tokens, 0.0)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),
    "task-p3-02-dag-topo-resolver": CodingChallenge(
        challenge_id="task-p3-02-dag-topo-resolver",
        tier=4,
        title="Deterministic DAG Dependency Resolver with Cycle Detection",
        description=(
            "Fix topological sorting in DependencyResolver. "
            "Must return deterministic stable ordering and raise CircularDependencyError "
            "with the exact cycle path on circular dependencies."
        ),
        initial_files={
            "resolver.py": (
                "class CircularDependencyError(Exception):\n"
                "    pass\n\n"
                "class DependencyResolver:\n"
                "    def __init__(self, graph: dict[str, list[str]]):\n"
                "        self.graph = graph\n\n"
                "    def resolve(self) -> list[str]:\n"
                "        # Bug: Infinite recursion on cycles and unstable order\n"
                "        order = []\n"
                "        for node in self.graph:\n"
                "            if node not in order:\n"
                "                order.append(node)\n"
                "        return order\n"
            ),
        },
        test_oracle_code=(
            "import unittest\n"
            "from resolver import DependencyResolver, CircularDependencyError\n\n"
            "class TestResolver(unittest.TestCase):\n"
            "    def test_linear_dag(self):\n"
            "        r = DependencyResolver({'a': ['b'], 'b': ['c'], 'c': []})\n"
            "        res = r.resolve()\n"
            "        self.assertEqual(res, ['c', 'b', 'a'])\n\n"
            "    def test_cycle_detected(self):\n"
            "        r = DependencyResolver({'a': ['b'], 'b': ['c'], 'c': ['a']})\n"
            "        with self.assertRaises(CircularDependencyError):\n"
            "            r.resolve()\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),
}

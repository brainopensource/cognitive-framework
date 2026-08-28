"""Standalone benchmark challenges for 006_LLM_INT_MACHINE.

Includes Tier 1, Tier 3, and Tier 5 SWE-bench challenges with zero hints in the brief
and isolated verification oracles.
"""

from __future__ import annotations
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class BenchmarkChallenge:
    challenge_id: str
    tier: int
    title: str
    brief: str
    files: Mapping[str, str]
    oracle_test_code: str


CHALLENGES: dict[str, BenchmarkChallenge] = {
    "tier1_lru_cache": BenchmarkChallenge(
        challenge_id="tier1_lru_cache",
        tier=1,
        title="Thread-Safe LRU Cache with Monotonic TTL",
        brief=(
            "Fix the LRUCache in `lru/cache.py` and `lru/entry.py`. Stale items must be purged upon `get()` "
            "and `put()`. The cache must respect capacity limits and use monotonic time."
        ),
        files={
            "lru/__init__.py": "from .cache import LRUCache\n__all__ = ['LRUCache']\n",
            "lru/entry.py": (
                "import time\n"
                "from dataclasses import dataclass\n"
                "from typing import Any, Optional\n\n"
                "@dataclass\n"
                "class CacheEntry:\n"
                "    key: str\n"
                "    value: Any\n"
                "    ttl_seconds: Optional[float]\n"
                "    created_at: float\n\n"
                "    def is_expired(self, current_time: float) -> bool:\n"
                "        # BUG: Returns False unconditionally\n"
                "        if self.ttl_seconds is None:\n"
                "            return False\n"
                "        return False\n"
            ),
            "lru/cache.py": (
                "import time\n"
                "import threading\n"
                "from collections import OrderedDict\n"
                "from typing import Any, Optional\n"
                "from .entry import CacheEntry\n\n"
                "class LRUCache:\n"
                "    def __init__(self, capacity: int, default_ttl: Optional[float] = None):\n"
                "        if capacity <= 0:\n"
                "            raise ValueError('Capacity must be positive')\n"
                "        self.capacity = capacity\n"
                "        self.default_ttl = default_ttl\n"
                "        self._store: OrderedDict[str, CacheEntry] = OrderedDict()\n"
                "        self._lock = threading.RLock()\n\n"
                "    def get(self, key: str) -> Optional[Any]:\n"
                "        with self._lock:\n"
                "            if key not in self._store:\n"
                "                return None\n"
                "            entry = self._store[key]\n"
                "            now = time.monotonic()\n"
                "            if entry.is_expired(now):\n"
                "                del self._store[key]\n"
                "                return None\n"
                "            self._store.move_to_end(key)\n"
                "            return entry.value\n\n"
                "    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:\n"
                "        with self._lock:\n"
                "            now = time.monotonic()\n"
                "            effective_ttl = ttl if ttl is not None else self.default_ttl\n"
                "            if key in self._store:\n"
                "                self._store.move_to_end(key)\n"
                "            self._store[key] = CacheEntry(key, value, effective_ttl, now)\n"
                "            if len(self._store) > self.capacity:\n"
                "                self._store.popitem(last=False)\n"
            ),
        },
        oracle_test_code=(
            "import unittest, time\n"
            "from lru.cache import LRUCache\n\n"
            "class TestLRUTTLCache(unittest.TestCase):\n"
            "    def test_eviction_and_expiry(self):\n"
            "        c = LRUCache(2, default_ttl=0.1)\n"
            "        c.put('a', 1)\n"
            "        c.put('b', 2)\n"
            "        self.assertEqual(c.get('a'), 1)\n"
            "        c.put('c', 3)\n"
            "        self.assertIsNone(c.get('b'), 'b should be evicted due to capacity 2')\n"
            "        time.sleep(0.15)\n"
            "        self.assertIsNone(c.get('a'), 'a should be expired after 0.15s')\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),

    "tier5_datalog_engine": BenchmarkChallenge(
        challenge_id="tier5_datalog_engine",
        tier=5,
        title="Datalog Deductive Inference Engine with Stratified Evaluation",
        brief=(
            "Fix the Datalog unification and rule evaluation in `datalog/evaluator.py` and `datalog/engine.py`. "
            "Recursive rules must evaluate to fixpoint, and variable substitutions must bind "
            "correctly across multi-clause rule bodies without cross-clause binding leakage."
        ),
        files={
            "datalog/__init__.py": "from .engine import DatalogEngine\n__all__ = ['DatalogEngine']\n",
            "datalog/ast.py": (
                "from dataclasses import dataclass\n"
                "from typing import Sequence\n\n"
                "@dataclass(frozen=True)\n"
                "class Term:\n"
                "    name: str\n"
                "    is_var: bool\n\n"
                "@dataclass(frozen=True)\n"
                "class Atom:\n"
                "    predicate: str\n"
                "    args: tuple[Term, ...]\n\n"
                "@dataclass(frozen=True)\n"
                "class Rule:\n"
                "    head: Atom\n"
                "    body: tuple[Atom, ...]\n"
            ),
            "datalog/unify.py": (
                "from typing import Optional, Mapping\n"
                "from .ast import Atom, Term\n\n"
                "def unify_atom(pattern: Atom, fact: Atom, env: Mapping[str, str]) -> Optional[dict[str, str]]:\n"
                "    if pattern.predicate != fact.predicate or len(pattern.args) != len(fact.args):\n"
                "        return None\n"
                "    new_env = dict(env)\n"
                "    for p_arg, f_arg in zip(pattern.args, fact.args):\n"
                "        if p_arg.is_var:\n"
                "            var_name = p_arg.name\n"
                "            if var_name in new_env:\n"
                "                if new_env[var_name] != f_arg.name:\n"
                "                    return None\n"
                "            else:\n"
                "                new_env[var_name] = f_arg.name\n"
                "        else:\n"
                "            if p_arg.name != f_arg.name:\n"
                "                return None\n"
                "    return new_env\n"
            ),
            "datalog/engine.py": (
                "from typing import Set, Sequence\n"
                "from .ast import Atom, Rule, Term\n"
                "from .unify import unify_atom\n\n"
                "class DatalogEngine:\n"
                "    def __init__(self):\n"
                "        self.facts: Set[Atom] = set()\n"
                "        self.rules: list[Rule] = []\n\n"
                "    def add_fact(self, fact: Atom) -> None:\n"
                "        self.facts.add(fact)\n\n"
                "    def add_rule(self, rule: Rule) -> None:\n"
                "        self.rules.append(rule)\n\n"
                "    def evaluate(self) -> Set[Atom]:\n"
                "        derived = set(self.facts)\n"
                "        changed = True\n"
                "        while changed:\n"
                "            changed = False\n"
                "            for rule in self.rules:\n"
                "                matches = self._eval_body(rule.body, derived, {})\n"
                "                for env in matches:\n"
                "                    head_args = []\n"
                "                    for arg in rule.head.args:\n"
                "                        if arg.is_var and arg.name in env:\n"
                "                            head_args.append(Term(env[arg.name], is_var=False))\n"
                "                        else:\n"
                "                            head_args.append(arg)\n"
                "                    new_fact = Atom(rule.head.predicate, tuple(head_args))\n"
                "                    if new_fact not in derived:\n"
                "                        derived.add(new_fact)\n"
                "                        changed = True\n"
                "        return derived\n\n"
                "    def _eval_body(self, body: Sequence[Atom], facts: Set[Atom], env: dict[str, str]) -> list[dict[str, str]]:\n"
                "        if not body:\n"
                "            return [env]\n"
                "        first = body[0]\n"
                "        rest = body[1:]\n"
                "        results = []\n"
                "        for fact in facts:\n"
                "            unified = unify_atom(first, fact, env)\n"
                "            if unified is not None:\n"
                "                # BUG: Passes original 'env' instead of new 'unified' bindings\n"
                "                results.extend(self._eval_body(rest, facts, env))\n"
                "        return results\n"
            ),
        },
        oracle_test_code=(
            "import unittest\n"
            "from datalog.ast import Atom, Rule, Term\n"
            "from datalog.engine import DatalogEngine\n\n"
            "class TestDatalogEngine(unittest.TestCase):\n"
            "    def test_transitive_closure_multi_clause(self):\n"
            "        engine = DatalogEngine()\n"
            "        # Facts: parent(alice, bob), parent(bob, charlie), parent(charlie, david)\n"
            "        engine.add_fact(Atom('parent', (Term('alice', False), Term('bob', False))))\n"
            "        engine.add_fact(Atom('parent', (Term('bob', False), Term('charlie', False))))\n"
            "        engine.add_fact(Atom('parent', (Term('charlie', False), Term('david', False))))\n"
            "        \n"
            "        # Rule 1: ancestor(X, Y) :- parent(X, Y)\n"
            "        engine.add_rule(Rule(\n"
            "            head=Atom('ancestor', (Term('X', True), Term('Y', True))),\n"
            "            body=(Atom('parent', (Term('X', True), Term('Y', True))),)\n"
            "        ))\n"
            "        # Rule 2: ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z)\n"
            "        engine.add_rule(Rule(\n"
            "            head=Atom('ancestor', (Term('X', True), Term('Z', True))),\n"
            "            body=(\n"
            "                Atom('parent', (Term('X', True), Term('Y', True))),\n"
            "                Atom('ancestor', (Term('Y', True), Term('Z', True)))\n"
            "            )\n"
            "        ))\n"
            "        derived = engine.evaluate()\n"
            "        expected_ancestor = Atom('ancestor', (Term('alice', False), Term('david', False)))\n"
            "        self.assertIn(expected_ancestor, derived, 'Should deduce ancestor(alice, david)')\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),
}


def setup_challenge_workspace(challenge_id: str, dest_dir: Path) -> BenchmarkChallenge:
    challenge = CHALLENGES[challenge_id]
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for rel_path, content in challenge.files.items():
        p = dest_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        
    (dest_dir / "TASK.md").write_text(f"# {challenge.title}\n\n{challenge.brief}\n", encoding="utf-8")

    subprocess.run(["git", "init"], cwd=dest_dir, capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=dest_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial commit"],
        cwd=dest_dir,
        capture_output=True,
        check=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "Bench",
            "GIT_AUTHOR_EMAIL": "bench@test.local",
            "GIT_COMMITTER_NAME": "Bench",
            "GIT_COMMITTER_EMAIL": "bench@test.local",
        }
    )
    return challenge


def evaluate_challenge_oracle(challenge_id: str, workspace_dir: Path) -> bool:
    challenge = CHALLENGES[challenge_id]
    oracle_file = workspace_dir / "oracle_eval_test.py"
    oracle_file.write_text(challenge.oracle_test_code, encoding="utf-8")
    
    res = subprocess.run(
        [sys.executable, str(oracle_file)],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
    )
    if oracle_file.is_file():
        try:
            oracle_file.unlink()
        except Exception:
            pass
    return res.returncode == 0

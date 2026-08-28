"""Standalone multi-tier benchmark challenges for 006_LLM_INT_MACHINE.

Includes Tier 1 through Tier 8 SWE-bench challenges with zero hints in the brief
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

    "tier2_semver_parser": BenchmarkChallenge(
        challenge_id="tier2_semver_parser",
        tier=2,
        title="Strict Semantic Versioning 2.0 Parser & Numeric Identifier Comparator",
        brief=(
            "Fix the SemVer comparator in `semver/parser.py` and `semver/version.py`. "
            "According to SemVer 2.0.0 specification (Clause 11), pre-release identifiers consisting of only digits "
            "must be compared numerically rather than as lexical strings (e.g., `1.0.0-alpha.2` < `1.0.0-alpha.10`). "
            "Build metadata (`+build.1`) must be parsed but ignored during version precedence comparisons."
        ),
        files={
            "semver/__init__.py": "from .version import Version\n__all__ = ['Version']\n",
            "semver/version.py": (
                "from dataclasses import dataclass\n"
                "from typing import Tuple, Optional\n\n"
                "@dataclass(frozen=True)\n"
                "class Version:\n"
                "    major: int\n"
                "    minor: int\n"
                "    patch: int\n"
                "    prerelease: Tuple[str, ...] = ()\n"
                "    build: Tuple[str, ...] = ()\n\n"
                "    def __lt__(self, other: 'Version') -> bool:\n"
                "        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):\n"
                "            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)\n"
                "        if not self.prerelease and other.prerelease:\n"
                "            return False\n"
                "        if self.prerelease and not other.prerelease:\n"
                "            return True\n"
                "        # BUG: Lexical string comparison on prerelease tuples fails numeric ordering\n"
                "        return self.prerelease < other.prerelease\n\n"
                "    def __eq__(self, other: object) -> bool:\n"
                "        if not isinstance(other, Version):\n"
                "            return False\n"
                "        return (self.major, self.minor, self.patch, self.prerelease) == (other.major, other.minor, other.patch, other.prerelease)\n"
            ),
            "semver/parser.py": (
                "import re\n"
                "from .version import Version\n\n"
                "def parse_version(v_str: str) -> Version:\n"
                "    pattern = r'^(\\d+)\\.(\\d+)\\.(\\d+)(?:-([0-9A-Za-z.-]+))?(?:\\+([0-9A-Za-z.-]+))?$'\n"
                "    m = re.match(pattern, v_str.strip())\n"
                "    if not m:\n"
                "        raise ValueError(f'Invalid SemVer: {v_str}')\n"
                "    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))\n"
                "    prerelease = tuple(m.group(4).split('.')) if m.group(4) else ()\n"
                "    build = tuple(m.group(5).split('.')) if m.group(5) else ()\n"
                "    return Version(major, minor, patch, prerelease, build)\n"
            ),
        },
        oracle_test_code=(
            "import unittest\n"
            "from semver.parser import parse_version\n\n"
            "class TestSemVerComparator(unittest.TestCase):\n"
            "    def test_numeric_prerelease_and_build_metadata(self):\n"
            "        v_alpha2 = parse_version('1.0.0-alpha.2')\n"
            "        v_alpha10 = parse_version('1.0.0-alpha.10')\n"
            "        self.assertTrue(v_alpha2 < v_alpha10, 'alpha.2 must be strictly less than alpha.10 numerically')\n"
            "        \n"
            "        v1 = parse_version('1.0.0-alpha+001')\n"
            "        v2 = parse_version('1.0.0-alpha+002')\n"
            "        self.assertEqual(v1, v2, 'Build metadata must not affect version equality')\n"
            "        self.assertFalse(v1 < v2)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),

    "tier3_token_bucket": BenchmarkChallenge(
        challenge_id="tier3_token_bucket",
        tier=3,
        title="Thread-Safe Distributed Token Bucket Rate Limiter",
        brief=(
            "Fix the token refill calculation in `ratelimit/bucket.py`. "
            "Tokens must replenish smoothly using floating-point fractional time elapsed instead of integer truncation. "
            "`consume()` must be thread-safe and return True only when sufficient tokens are available."
        ),
        files={
            "ratelimit/__init__.py": "from .bucket import TokenBucket\n__all__ = ['TokenBucket']\n",
            "ratelimit/bucket.py": (
                "import time\n"
                "import threading\n\n"
                "class TokenBucket:\n"
                "    def __init__(self, capacity: float, refill_rate_per_sec: float):\n"
                "        self.capacity = float(capacity)\n"
                "        self.rate = float(refill_rate_per_sec)\n"
                "        self.tokens = float(capacity)\n"
                "        self.last_refill = time.monotonic()\n"
                "        self._lock = threading.Lock()\n\n"
                "    def _refill(self, now: float) -> None:\n"
                "        elapsed = now - self.last_refill\n"
                "        # BUG: Truncates elapsed time to int, starving fast sub-second consumers\n"
                "        added_tokens = int(elapsed) * self.rate\n"
                "        self.tokens = min(self.capacity, self.tokens + added_tokens)\n"
                "        self.last_refill = now\n\n"
                "    def consume(self, amount: float = 1.0) -> bool:\n"
                "        with self._lock:\n"
                "            now = time.monotonic()\n"
                "            self._refill(now)\n"
                "            if self.tokens >= amount:\n"
                "                self.tokens -= amount\n"
                "                return True\n"
                "            return False\n"
            ),
        },
        oracle_test_code=(
            "import unittest, time\n"
            "from ratelimit.bucket import TokenBucket\n\n"
            "class TestTokenBucket(unittest.TestCase):\n"
            "    def test_smooth_fractional_refill(self):\n"
            "        bucket = TokenBucket(capacity=10.0, refill_rate_per_sec=20.0)\n"
            "        self.assertTrue(bucket.consume(10.0), 'Initial burst should succeed')\n"
            "        self.assertFalse(bucket.consume(1.0), 'Empty bucket should reject immediate request')\n"
            "        time.sleep(0.06)\n"
            "        self.assertTrue(bucket.consume(1.0), 'Fractional refill should permit 1 token after 60ms')\n\n"
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
            "        engine.add_fact(Atom('parent', (Term('alice', False), Term('bob', False))))\n"
            "        engine.add_fact(Atom('parent', (Term('bob', False), Term('charlie', False))))\n"
            "        engine.add_fact(Atom('parent', (Term('charlie', False), Term('david', False))))\n"
            "        \n"
            "        engine.add_rule(Rule(\n"
            "            head=Atom('ancestor', (Term('X', True), Term('Y', True))),\n"
            "            body=(Atom('parent', (Term('X', True), Term('Y', True))),)\n"
            "        ))\n"
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

    "tier6_raft_consensus": BenchmarkChallenge(
        challenge_id="tier6_raft_consensus",
        tier=6,
        title="Distributed Raft Consensus Protocol: Split-Vote & Term Election State Machine",
        brief=(
            "Fix the Raft election term management and vote tallying in `raft/node.py` and `raft/election.py`. "
            "When starting an election, a candidate must increment `current_term`, vote for itself, and collect votes. "
            "If a node receives an RPC with `term > current_term`, it must transition to Follower and update its term."
        ),
        files={
            "raft/__init__.py": "from .node import RaftNode, NodeRole\n__all__ = ['RaftNode', 'NodeRole']\n",
            "raft/election.py": (
                "from dataclasses import dataclass\n"
                "from typing import Optional\n\n"
                "@dataclass\n"
                "class RequestVoteArgs:\n"
                "    term: int\n"
                "    candidate_id: str\n"
                "    last_log_index: int\n"
                "    last_log_term: int\n\n"
                "@dataclass\n"
                "class RequestVoteReply:\n"
                "    term: int\n"
                "    vote_granted: bool\n"
            ),
            "raft/node.py": (
                "from enum import Enum\n"
                "from typing import Optional, Set\n"
                "from .election import RequestVoteArgs, RequestVoteReply\n\n"
                "class NodeRole(Enum):\n"
                "    FOLLOWER = 'follower'\n"
                "    CANDIDATE = 'candidate'\n"
                "    LEADER = 'leader'\n\n"
                "class RaftNode:\n"
                "    def __init__(self, node_id: str, peers: list[str]):\n"
                "        self.node_id = node_id\n"
                "        self.peers = peers\n"
                "        self.current_term = 0\n"
                "        self.voted_for: Optional[str] = None\n"
                "        self.role = NodeRole.FOLLOWER\n"
                "        self.votes_received: Set[str] = set()\n\n"
                "    def start_election(self) -> None:\n"
                "        self.role = NodeRole.CANDIDATE\n"
                "        # BUG: Fails to increment current_term before requesting votes\n"
                "        self.voted_for = self.node_id\n"
                "        self.votes_received = {self.node_id}\n\n"
                "    def handle_request_vote(self, args: RequestVoteArgs) -> RequestVoteReply:\n"
                "        if args.term > self.current_term:\n"
                "            self.current_term = args.term\n"
                "            self.role = NodeRole.FOLLOWER\n"
                "            self.voted_for = None\n\n"
                "        can_vote = (self.voted_for is None or self.voted_for == args.candidate_id)\n"
                "        if args.term == self.current_term and can_vote:\n"
                "            self.voted_for = args.candidate_id\n"
                "            return RequestVoteReply(term=self.current_term, vote_granted=True)\n"
                "        return RequestVoteReply(term=self.current_term, vote_granted=False)\n\n"
                "    def check_election_quorum(self) -> bool:\n"
                "        total_nodes = len(self.peers) + 1\n"
                "        quorum = (total_nodes // 2) + 1\n"
                "        if len(self.votes_received) >= quorum and self.role == NodeRole.CANDIDATE:\n"
                "            self.role = NodeRole.LEADER\n"
                "            return True\n"
                "        return False\n"
            ),
        },
        oracle_test_code=(
            "import unittest\n"
            "from raft.node import RaftNode, NodeRole\n"
            "from raft.election import RequestVoteArgs\n\n"
            "class TestRaftConsensus(unittest.TestCase):\n"
            "    def test_election_term_increment_and_quorum(self):\n"
            "        n1 = RaftNode('n1', peers=['n2', 'n3'])\n"
            "        self.assertEqual(n1.current_term, 0)\n"
            "        n1.start_election()\n"
            "        self.assertEqual(n1.current_term, 1, 'Starting election must increment current_term to 1')\n"
            "        self.assertEqual(n1.role, NodeRole.CANDIDATE)\n"
            "        \n"
            "        # n2 votes for n1\n"
            "        n1.votes_received.add('n2')\n"
            "        self.assertTrue(n1.check_election_quorum(), '2/3 votes must achieve quorum and elect leader')\n"
            "        self.assertEqual(n1.role, NodeRole.LEADER)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),

    "tier7_mvcc_storage": BenchmarkChallenge(
        challenge_id="tier7_mvcc_storage",
        tier=7,
        title="Multi-Version Concurrency Control (MVCC) Transactional Storage Engine",
        brief=(
            "Fix the snapshot isolation and version chain traversal in `mvcc/engine.py` and `mvcc/transaction.py`. "
            "A transaction must only read the latest version of a record committed before its `read_timestamp`."
        ),
        files={
            "mvcc/__init__.py": "from .engine import MVCCStorage\n__all__ = ['MVCCStorage']\n",
            "mvcc/version.py": (
                "from dataclasses import dataclass\n"
                "from typing import Any, Optional\n\n"
                "@dataclass\n"
                "class RecordVersion:\n"
                "    value: Any\n"
                "    created_txn_id: int\n"
                "    deleted_txn_id: Optional[int] = None\n"
                "    prev: Optional['RecordVersion'] = None\n"
            ),
            "mvcc/engine.py": (
                "from typing import Dict, Optional, Any\n"
                "from .version import RecordVersion\n\n"
                "class MVCCStorage:\n"
                "    def __init__(self):\n"
                "        self._records: Dict[str, RecordVersion] = {}\n"
                "        self._txn_counter = 0\n"
                "        self._committed_txns: set[int] = set()\n\n"
                "    def begin_transaction(self) -> int:\n"
                "        self._txn_counter += 1\n"
                "        return self._txn_counter\n\n"
                "    def commit_transaction(self, txn_id: int) -> None:\n"
                "        self._committed_txns.add(txn_id)\n\n"
                "    def write(self, key: str, value: Any, txn_id: int) -> None:\n"
                "        prev_ver = self._records.get(key)\n"
                "        new_ver = RecordVersion(value=value, created_txn_id=txn_id, prev=prev_ver)\n"
                "        self._records[key] = new_ver\n\n"
                "    def read(self, key: str, txn_read_ts: int) -> Optional[Any]:\n"
                "        ver = self._records.get(key)\n"
                "        while ver is not None:\n"
                "            # BUG: Reads uncommitted version if created_txn_id <= txn_read_ts\n"
                "            if ver.created_txn_id <= txn_read_ts:\n"
                "                return ver.value\n"
                "            ver = ver.prev\n"
                "        return None\n"
            ),
        },
        oracle_test_code=(
            "import unittest\n"
            "from mvcc.engine import MVCCStorage\n\n"
            "class TestMVCCSnapshotIsolation(unittest.TestCase):\n"
            "    def test_uncommitted_read_isolation(self):\n"
            "        store = MVCCStorage()\n"
            "        t1 = store.begin_transaction()\n"
            "        store.write('balance', 100, t1)\n"
            "        store.commit_transaction(t1)\n"
            "        \n"
            "        t2 = store.begin_transaction()\n"
            "        store.write('balance', 200, t2) # Uncommitted write in t2\n"
            "        \n"
            "        t3 = store.begin_transaction() # t3 reads snapshot\n"
            "        val = store.read('balance', txn_read_ts=t3)\n"
            "        self.assertEqual(val, 100, 't3 must read committed version 100, not uncommitted 200 from t2')\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),

    "tier8_ast_compiler": BenchmarkChallenge(
        challenge_id="tier8_ast_compiler",
        tier=8,
        title="Multi-Pass AST Optimizing Compiler: Common Subexpression Elimination (CSE)",
        brief=(
            "Fix the Common Subexpression Elimination pass in `compiler/optimizer.py`. "
            "Expressions containing side-effecting function calls (e.g. `print()`, `rand()`) must not be eliminated or cached."
        ),
        files={
            "compiler/__init__.py": "from .optimizer import ASTOptimizer\n__all__ = ['ASTOptimizer']\n",
            "compiler/ast_nodes.py": (
                "from dataclasses import dataclass\n"
                "from typing import Sequence\n\n"
                "@dataclass\n"
                "class ExprNode:\n"
                "    op: str\n"
                "    args: tuple[str, ...]\n"
                "    is_pure: bool = True\n"
            ),
            "compiler/optimizer.py": (
                "from typing import Dict, List\n"
                "from .ast_nodes import ExprNode\n\n"
                "class ASTOptimizer:\n"
                "    def optimize_cse(self, instructions: List[ExprNode]) -> List[ExprNode]:\n"
                "        seen_exprs: Dict[tuple[str, tuple[str, ...]], ExprNode] = {}\n"
                "        optimized: List[ExprNode] = []\n"
                "        for expr in instructions:\n"
                "            key = (expr.op, expr.args)\n"
                "            # BUG: Eliminates non-pure expressions indiscriminately\n"
                "            if key in seen_exprs:\n"
                "                continue\n"
                "            seen_exprs[key] = expr\n"
                "            optimized.append(expr)\n"
                "        return optimized\n"
            ),
        },
        oracle_test_code=(
            "import unittest\n"
            "from compiler.ast_nodes import ExprNode\n"
            "from compiler.optimizer import ASTOptimizer\n\n"
            "class TestASTOptimizer(unittest.TestCase):\n"
            "    def test_cse_preserves_side_effects(self):\n"
            "        opt = ASTOptimizer()\n"
            "        pure_1 = ExprNode(op='add', args=('x', 'y'), is_pure=True)\n"
            "        pure_2 = ExprNode(op='add', args=('x', 'y'), is_pure=True)\n"
            "        impure_1 = ExprNode(op='call', args=('rand',), is_pure=False)\n"
            "        impure_2 = ExprNode(op='call', args=('rand',), is_pure=False)\n"
            "        \n"
            "        result = opt.optimize_cse([pure_1, pure_2, impure_1, impure_2])\n"
            "        self.assertEqual(len(result), 3, 'Pure duplicate should be removed, but impure duplicate preserved')\n"
            "        self.assertEqual([r.op for r in result], ['add', 'call', 'call'])\n\n"
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

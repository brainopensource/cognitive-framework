"""SWE Verified Pro Multi-Tier Benchmark Challenges (Tiers 1 to 7 — 20 Challenges).

Real multi-file coding projects and greenfield tasks with realistic architectures.
Zero hints, zero test oracles leaked in the task brief.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SWEProChallenge:
    challenge_id: str
    tier: int
    title: str
    kind: str  # "bugfix" | "feature" | "greenfield"
    brief: str
    files: Mapping[str, str]
    oracle_code: str


CHALLENGES: dict[str, SWEProChallenge] = {
    # =============================================================
    # Tier 1: Core Algorithms & Elementary Data Structures
    # =============================================================
    "tier1_lru_ttl_cache": SWEProChallenge(
        challenge_id="tier1_lru_ttl_cache",
        tier=1,
        title="Thread-Safe LRU Cache with Monotonic TTL",
        kind="bugfix",
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
                "        # BUG: Fails to check expiration properly\n"
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
        oracle_code=(
            "import unittest, time\n"
            "from lru.cache import LRUCache\n\n"
            "class TestLRUTTLCache(unittest.TestCase):\n"
            "    def test_eviction_and_expiry(self):\n"
            "        c = LRUCache(2, default_ttl=0.1)\n"
            "        c.put('a', 1)\n"
            "        c.put('b', 2)\n"
            "        self.assertEqual(c.get('a'), 1)\n"
            "        c.put('c', 3)\n"
            "        self.assertIsNone(c.get('b'))\n"
            "        time.sleep(0.15)\n"
            "        self.assertIsNone(c.get('a'))\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier1_ring_buffer_stream": SWEProChallenge(
        challenge_id="tier1_ring_buffer_stream",
        tier=1,
        title="Circular Ring Buffer with Read Pointers",
        kind="bugfix",
        brief=(
            "Fix the circular ring buffer in `ring/buffer.py`. Writing when full must overwrite oldest data, "
            "and `read(n)` must advance the read pointer without reading past the write pointer."
        ),
        files={
            "ring/__init__.py": "from .buffer import RingBuffer\n__all__ = ['RingBuffer']\n",
            "ring/buffer.py": (
                "class RingBuffer:\n"
                "    def __init__(self, capacity: int):\n"
                "        if capacity <= 0:\n"
                "            raise ValueError('Capacity must be > 0')\n"
                "        self.capacity = capacity\n"
                "        self._buf = [None] * capacity\n"
                "        self._head = 0\n"
                "        self._tail = 0\n"
                "        self._size = 0\n\n"
                "    def write(self, item) -> None:\n"
                "        self._buf[self._tail] = item\n"
                "        self._tail = (self._tail + 1) % self.capacity\n"
                "        if self._size < self.capacity:\n"
                "            self._size += 1\n"
                "        else:\n"
                "            self._head = (self._head + 1) % self.capacity\n\n"
                "    def read(self, count: int = 1) -> list:\n"
                "        items = []\n"
                "        to_read = min(count, self._size)\n"
                "        for _ in range(to_read):\n"
                "            items.append(self._buf[self._head])\n"
                "            self._head = (self._head + 1) % self.capacity\n"
                "            self._size -= 1\n"
                "        return items\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from ring.buffer import RingBuffer\n\n"
            "class TestRingBuffer(unittest.TestCase):\n"
            "    def test_overwrite_and_read(self):\n"
            "        rb = RingBuffer(3)\n"
            "        rb.write('a'); rb.write('b'); rb.write('c')\n"
            "        rb.write('d')  # overwrites 'a'\n"
            "        self.assertEqual(rb.read(2), ['b', 'c'])\n"
            "        self.assertEqual(rb.read(2), ['d'])\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier1_version_semver_parser": SWEProChallenge(
        challenge_id="tier1_version_semver_parser",
        tier=1,
        title="SemVer Version Range and Caret/Tilde Matcher",
        kind="bugfix",
        brief=(
            "Fix SemVer range matching in `semver/parser.py` and `semver/version.py`. "
            "Caret (`^1.2.3`) matches `>=1.2.3 <2.0.0` and tilde (`~1.2.3`) matches `>=1.2.3 <1.3.0`."
        ),
        files={
            "semver/__init__.py": "from .version import Version, match_range\n__all__ = ['Version', 'match_range']\n",
            "semver/version.py": (
                "from dataclasses import dataclass\n\n"
                "@dataclass(order=True, frozen=True)\n"
                "class Version:\n"
                "    major: int\n"
                "    minor: int\n"
                "    patch: int\n\n"
                "    @classmethod\n"
                "    def parse(cls, s: str) -> 'Version':\n"
                "        parts = [int(p) for p in s.strip().lstrip('v').split('.')]\n"
                "        return cls(parts[0], parts[1], parts[2])\n\n"
                "def match_range(v_str: str, constraint: str) -> bool:\n"
                "    v = Version.parse(v_str)\n"
                "    if constraint.startswith('^'):\n"
                "        base = Version.parse(constraint[1:])\n"
                "        return v >= base and v.major == base.major\n"
                "    elif constraint.startswith('~'):\n"
                "        base = Version.parse(constraint[1:])\n"
                "        return v >= base and v.major == base.major and v.minor == base.minor\n"
                "    return v == Version.parse(constraint)\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from semver import Version, match_range\n\n"
            "class TestSemVer(unittest.TestCase):\n"
            "    def test_caret_and_tilde(self):\n"
            "        self.assertTrue(match_range('1.4.0', '^1.2.3'))\n"
            "        self.assertFalse(match_range('2.0.0', '^1.2.3'))\n"
            "        self.assertTrue(match_range('1.2.9', '~1.2.3'))\n"
            "        self.assertFalse(match_range('1.3.0', '~1.2.3'))\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    # =============================================================
    # Tier 2: Multi-File State Machines & Event Systems
    # =============================================================
    "tier2_event_bus": SWEProChallenge(
        challenge_id="tier2_event_bus",
        tier=2,
        title="Hierarchical Wildcard Event Emitter",
        kind="bugfix",
        brief=(
            "Fix wildcard pattern matching and subscription unsubscribe leaks in `events/bus.py` "
            "and `events/matcher.py`."
        ),
        files={
            "events/__init__.py": "from .bus import EventBus\n__all__ = ['EventBus']\n",
            "events/matcher.py": (
                "import re\n\n"
                "def topic_matches(pattern: str, topic: str) -> bool:\n"
                "    if pattern == topic or pattern == '**': return True\n"
                "    parts = pattern.split('.')\n"
                "    rx = []\n"
                "    for p in parts:\n"
                "        if p == '*': rx.append(r'[^.]+')\n"
                "        elif p == '**': rx.append(r'.*')\n"
                "        else: rx.append(re.escape(p))\n"
                "    return bool(re.match('^' + r'\\.'.join(rx) + '$', topic))\n"
            ),
            "events/bus.py": (
                "from typing import Callable, Any\n"
                "from .matcher import topic_matches\n\n"
                "class Subscription:\n"
                "    def __init__(self, bus: 'EventBus', pattern: str, callback: Callable[[str, Any], None]):\n"
                "        self.bus = bus\n"
                "        self.pattern = pattern\n"
                "        self.callback = callback\n"
                "        self.active = True\n\n"
                "    def unsubscribe(self) -> None:\n"
                "        self.active = False\n"
                "        self.bus._subs = [s for s in self.bus._subs if s is not self]\n\n"
                "class EventBus:\n"
                "    def __init__(self):\n"
                "        self._subs: list[Subscription] = []\n\n"
                "    def subscribe(self, pattern: str, cb: Callable[[str, Any], None]) -> Subscription:\n"
                "        s = Subscription(self, pattern, cb)\n"
                "        self._subs.append(s)\n"
                "        return s\n\n"
                "    def publish(self, topic: str, payload: Any = None) -> int:\n"
                "        count = 0\n"
                "        for s in list(self._subs):\n"
                "            if s.active and topic_matches(s.pattern, topic):\n"
                "                s.callback(topic, payload)\n"
                "                count += 1\n"
                "        return count\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from events.bus import EventBus\n\n"
            "class TestEventBus(unittest.TestCase):\n"
            "    def test_pub_sub(self):\n"
            "        bus = EventBus()\n"
            "        res = []\n"
            "        s1 = bus.subscribe('order.**.created', lambda t, p: res.append(p))\n"
            "        bus.publish('order.created', 10)\n"
            "        bus.publish('order.us.east.created', 20)\n"
            "        self.assertEqual(res, [10, 20])\n"
            "        single = bus.subscribe('order.*.created', lambda t, p: res.append(p))\n"
            "        bus.publish('order.us.created', 25)\n"
            "        bus.publish('order.us.east.created', 26)\n"
            "        self.assertEqual(res, [10, 20, 25, 25])\n"
            "        single.unsubscribe()\n"
            "        s1.unsubscribe()\n"
            "        self.assertEqual(len(bus._subs), 0)\n"
            "        bus.publish('order.created', 30)\n"
            "        self.assertEqual(res, [10, 20])\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier2_fsm_workflow_engine": SWEProChallenge(
        challenge_id="tier2_fsm_workflow_engine",
        tier=2,
        title="Hierarchical State Machine with Rollback",
        kind="feature",
        brief=(
            "Implement a finite state machine in `fsm/machine.py` supporting states, transitions, "
            "guard conditions, and transaction rollback on failed transition hooks."
        ),
        files={
            "fsm/__init__.py": "from .machine import StateMachine, StateError\n__all__ = ['StateMachine', 'StateError']\n",
            "fsm/machine.py": (
                "class StateError(Exception):\n"
                "    pass\n\n"
                "class StateMachine:\n"
                "    def __init__(self, initial_state: str):\n"
                "        self.current_state = initial_state\n"
                "        self.transitions = {}\n\n"
                "    def add_transition(self, event: str, source: str, target: str, guard=None) -> None:\n"
                "        self.transitions[(event, source)] = (target, guard)\n\n"
                "    def trigger(self, event: str) -> str:\n"
                "        key = (event, self.current_state)\n"
                "        if key not in self.transitions:\n"
                "            raise StateError(f'Invalid transition {event} from {self.current_state}')\n"
                "        target, guard = self.transitions[key]\n"
                "        if guard and not guard():\n"
                "            raise StateError('Guard rejected')\n"
                "        self.current_state = target\n"
                "        return self.current_state\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from fsm.machine import StateMachine, StateError\n\n"
            "class TestFSM(unittest.TestCase):\n"
            "    def test_fsm(self):\n"
            "        fsm = StateMachine('idle')\n"
            "        fsm.add_transition('start', 'idle', 'running')\n"
            "        self.assertEqual(fsm.trigger('start'), 'running')\n"
            "        with self.assertRaises(StateError):\n"
            "            fsm.trigger('start')\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier2_retry_exponential_backoff": SWEProChallenge(
        challenge_id="tier2_retry_exponential_backoff",
        tier=2,
        title="Jittered Exponential Backoff Retry Policy",
        kind="bugfix",
        brief=(
            "Fix the retry mechanism in `retry/policy.py`. Calculate jittered exponential backoff delays, "
            "honor max_retries, and raise `MaxRetriesExceededError` when attempts fail."
        ),
        files={
            "retry/__init__.py": "from .policy import retry_call, MaxRetriesExceededError\n__all__ = ['retry_call', 'MaxRetriesExceededError']\n",
            "retry/policy.py": (
                "import time\n\n"
                "class MaxRetriesExceededError(Exception):\n"
                "    pass\n\n"
                "def retry_call(fn, max_retries=3, base_delay=0.01, backoff=2.0):\n"
                "    attempts = 0\n"
                "    while True:\n"
                "        try:\n"
                "            return fn()\n"
                "        except Exception as exc:\n"
                "            attempts += 1\n"
                "            if attempts >= max_retries:\n"
                "                raise MaxRetriesExceededError(f'Exceeded {max_retries} attempts') from exc\n"
                "            time.sleep(base_delay * (backoff ** (attempts - 1)))\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from retry.policy import retry_call, MaxRetriesExceededError\n\n"
            "class TestRetry(unittest.TestCase):\n"
            "    def test_retry_success(self):\n"
            "        cnt = [0]\n"
            "        def flaky():\n"
            "            cnt[0] += 1\n"
            "            if cnt[0] < 2: raise ValueError('boom')\n"
            "            return 42\n"
            "        self.assertEqual(retry_call(flaky, max_retries=3), 42)\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    # =============================================================
    # Tier 3: Concurrency, Invariants & Resource Synchronization
    # =============================================================
    "tier3_token_bucket": SWEProChallenge(
        challenge_id="tier3_token_bucket",
        tier=3,
        title="Token Bucket Limiter with Monotonic Refill",
        kind="bugfix",
        brief=(
            "Fix the concurrency and refill drift bug in `ratelimit/bucket.py`. Replenish tokens "
            "using monotonic elapsed time, clamp to max_burst, raise ValueError on non-positive tokens, and prevent race conditions."
        ),
        files={
            "ratelimit/__init__.py": "from .bucket import TokenBucket\n__all__ = ['TokenBucket']\n",
            "ratelimit/bucket.py": (
                "import time, threading\n\n"
                "class TokenBucket:\n"
                "    def __init__(self, rate_per_sec: float, max_burst: int):\n"
                "        self.rate = rate_per_sec\n"
                "        self.max_burst = max_burst\n"
                "        self.tokens = float(max_burst)\n"
                "        self.last_update = time.monotonic()\n"
                "        self._lock = threading.Lock()\n\n"
                "    def consume(self, tokens: float = 1) -> bool:\n"
                "        with self._lock:\n"
                "            now = time.monotonic()\n"
                "            elapsed = now - self.last_update\n"
                "            self.tokens = min(float(self.max_burst), self.tokens + elapsed * self.rate)\n"
                "            self.last_update = now\n"
                "            if self.tokens >= tokens:\n"
                "                self.tokens -= tokens\n"
                "                return True\n"
                "            return False\n"
            ),
        },
        oracle_code=(
            "import unittest, time\n"
            "from ratelimit.bucket import TokenBucket\n\n"
            "class TestTokenBucket(unittest.TestCase):\n"
            "    def test_bucket(self):\n"
            "        tb = TokenBucket(10.0, 2)\n"
            "        self.assertTrue(tb.consume(1.5))\n"
            "        self.assertFalse(tb.consume(1.0))\n"
            "        with self.assertRaises(ValueError):\n"
            "            tb.consume(0)\n"
            "        time.sleep(0.06)\n"
            "        self.assertTrue(tb.consume(0.5))\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier3_rw_lock_priority": SWEProChallenge(
        challenge_id="tier3_rw_lock_priority",
        tier=3,
        title="Writer-Priority Reader-Writer Lock",
        kind="feature",
        brief=(
            "Implement a reader-writer lock in `sync/rwlock.py` giving writers priority over new readers "
            "to prevent writer starvation under continuous read loads."
        ),
        files={
            "sync/__init__.py": "from .rwlock import ReadWriteLock\n__all__ = ['ReadWriteLock']\n",
            "sync/rwlock.py": (
                "import threading\n\n"
                "class ReadWriteLock:\n"
                "    def __init__(self):\n"
                "        self._lock = threading.Lock()\n"
                "        self._readers_ok = threading.Condition(self._lock)\n"
                "        self._writers_ok = threading.Condition(self._lock)\n"
                "        self._readers = 0\n"
                "        self._writers_waiting = 0\n"
                "        self._writer_active = False\n\n"
                "    def acquire_read(self):\n"
                "        with self._lock:\n"
                "            while self._writer_active or self._writers_waiting > 0:\n"
                "                self._readers_ok.wait()\n"
                "            self._readers += 1\n\n"
                "    def release_read(self):\n"
                "        with self._lock:\n"
                "            self._readers -= 1\n"
                "            if self._readers == 0:\n"
                "                self._writers_ok.notify()\n\n"
                "    def acquire_write(self):\n"
                "        with self._lock:\n"
                "            self._writers_waiting += 1\n"
                "            while self._writer_active or self._readers > 0:\n"
                "                self._writers_ok.wait()\n"
                "            self._writers_waiting -= 1\n"
                "            self._writer_active = True\n\n"
                "    def release_write(self):\n"
                "        with self._lock:\n"
                "            self._writer_active = False\n"
                "            if self._writers_waiting > 0:\n"
                "                self._writers_ok.notify()\n"
                "            else:\n"
                "                self._readers_ok.notify_all()\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from sync.rwlock import ReadWriteLock\n\n"
            "class TestRWLock(unittest.TestCase):\n"
            "    def test_rw(self):\n"
            "        rw = ReadWriteLock()\n"
            "        rw.acquire_read()\n"
            "        rw.acquire_read()\n"
            "        rw.release_read()\n"
            "        rw.release_read()\n"
            "        rw.acquire_write()\n"
            "        rw.release_write()\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier3_connection_pool": SWEProChallenge(
        challenge_id="tier3_connection_pool",
        tier=3,
        title="Async Connection Pool with Health Checking",
        kind="feature",
        brief=(
            "Implement a thread-safe connection pool in `pool/connection.py` that leases connections, "
            "enforces maximum pool capacity, and discards unhealthy connections."
        ),
        files={
            "pool/__init__.py": "from .connection import ConnectionPool\n__all__ = ['ConnectionPool']\n",
            "pool/connection.py": (
                "import queue\n\n"
                "class ConnectionPool:\n"
                "    def __init__(self, factory, max_size=5):\n"
                "        self.factory = factory\n"
                "        self.max_size = max_size\n"
                "        self._pool = queue.Queue(maxsize=max_size)\n"
                "        for _ in range(max_size):\n"
                "            self._pool.put(self.factory())\n\n"
                "    def acquire(self, timeout=1.0):\n"
                "        return self._pool.get(timeout=timeout)\n\n"
                "    def release(self, conn):\n"
                "        self._pool.put(conn)\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from pool.connection import ConnectionPool\n\n"
            "class TestPool(unittest.TestCase):\n"
            "    def test_pool(self):\n"
            "        p = ConnectionPool(lambda: object(), max_size=2)\n"
            "        c1 = p.acquire()\n"
            "        c2 = p.acquire()\n"
            "        p.release(c1)\n"
            "        c3 = p.acquire()\n"
            "        self.assertEqual(c1, c3)\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    # =============================================================
    # Tier 4: Graph Algorithms & Data Pipelines
    # =============================================================
    "tier4_dag_resolver": SWEProChallenge(
        challenge_id="tier4_dag_resolver",
        tier=4,
        title="DAG Dependency Topological Sorter with Cycle Trace",
        kind="bugfix",
        brief=(
            "Fix topological sorting and cycle detection in `dag/resolver.py` and `dag/cycle.py`. "
            "Must return deterministic order and raise `CircularDependencyError` with a `.cycle` list attribute containing the detected cycle."
        ),
        files={
            "dag/__init__.py": "from .resolver import DependencyResolver, CircularDependencyError\n__all__ = ['DependencyResolver', 'CircularDependencyError']\n",
            "dag/cycle.py": "class CircularDependencyError(ValueError): pass\n",
            "dag/resolver.py": (
                "from .cycle import CircularDependencyError\n\n"
                "class DependencyResolver:\n"
                "    def __init__(self, deps: dict[str, list[str]]):\n"
                "        self.deps = deps\n\n"
                "    def resolve(self) -> list[str]:\n"
                "        # In-degree computation for Kahn's algorithm\n"
                "        nodes = set(self.deps.keys())\n"
                "        for targets in self.deps.values(): nodes.update(targets)\n"
                "        in_degree = {n: 0 for n in nodes}\n"
                "        for targets in self.deps.values():\n"
                "            for t in targets: in_degree[t] += 1\n"
                "        queue = sorted([n for n, deg in in_degree.items() if deg == 0])\n"
                "        res = []\n"
                "        while queue:\n"
                "            curr = queue.pop(0)\n"
                "            res.append(curr)\n"
                "            for nxt in sorted(self.deps.get(curr, [])):\n"
                "                in_degree[nxt] -= 1\n"
                "                if in_degree[nxt] == 0: queue.append(nxt)\n"
                "        if len(res) < len(nodes):\n"
                "            raise CircularDependencyError('Cycle detected')\n"
                "        return res\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from dag.resolver import DependencyResolver, CircularDependencyError\n\n"
            "class TestDAG(unittest.TestCase):\n"
            "    def test_dag_ordering(self):\n"
            "        deps = {'a': ['b'], 'b': ['c'], 'c': []}\n"
            "        r = DependencyResolver(deps).resolve()\n"
            "        self.assertEqual(r, ['a', 'b', 'c'])\n\n"
            "    def test_cycle_trace(self):\n"
            "        deps = {'a': ['b'], 'b': ['c'], 'c': ['a']}\n"
            "        with self.assertRaises(CircularDependencyError) as ctx:\n"
            "            DependencyResolver(deps).resolve()\n"
            "        self.assertTrue(hasattr(ctx.exception, 'cycle'))\n"
            "        self.assertTrue(len(ctx.exception.cycle) >= 3)\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier4_trie_prefix_router": SWEProChallenge(
        challenge_id="tier4_trie_prefix_router",
        tier=4,
        title="Radix Trie HTTP URL Path Pattern Matcher",
        kind="feature",
        brief=(
            "Implement a Radix Trie path router in `router/trie.py` supporting parameterized segments "
            "such as `/users/:id/profile` and catch-all wildcards `*path`."
        ),
        files={
            "router/__init__.py": "from .trie import PathRouter\n__all__ = ['PathRouter']\n",
            "router/trie.py": (
                "class PathRouter:\n"
                "    def __init__(self):\n"
                "        self.routes = []\n\n"
                "    def add(self, pattern: str, handler) -> None:\n"
                "        self.routes.append((pattern.strip('/').split('/'), handler))\n\n"
                "    def match(self, path: str):\n"
                "        segments = path.strip('/').split('/')\n"
                "        for pattern_segs, handler in self.routes:\n"
                "            if len(pattern_segs) != len(segments): continue\n"
                "            params = {}\n"
                "            match = True\n"
                "            for p_seg, seg in zip(pattern_segs, segments):\n"
                "                if p_seg.startswith(':'):\n"
                "                    params[p_seg[1:]] = seg\n"
                "                elif p_seg != seg:\n"
                "                    match = False\n"
                "                    break\n"
                "            if match:\n"
                "                return handler, params\n"
                "        return None, {}\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from router.trie import PathRouter\n\n"
            "class TestRouter(unittest.TestCase):\n"
            "    def test_param_match(self):\n"
            "        r = PathRouter()\n"
            "        r.add('/users/:id/profile', 'h_user')\n"
            "        h, p = r.match('/users/42/profile')\n"
            "        self.assertEqual(h, 'h_user')\n"
            "        self.assertEqual(p, {'id': '42'})\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier4_stream_window_aggregator": SWEProChallenge(
        challenge_id="tier4_stream_window_aggregator",
        tier=4,
        title="Sliding Time-Window Metrics Aggregator",
        kind="feature",
        brief=(
            "Implement a sliding time-window aggregator in `metrics/window.py` calculating moving average, "
            "percentiles, and counts over a rolling interval."
        ),
        files={
            "metrics/__init__.py": "from .window import SlidingWindow\n__all__ = ['SlidingWindow']\n",
            "metrics/window.py": (
                "import time\n\n"
                "class SlidingWindow:\n"
                "    def __init__(self, window_seconds: float):\n"
                "        self.window = window_seconds\n"
                "        self._entries: list[tuple[float, float]] = []\n\n"
                "    def record(self, val: float, ts: float | None = None) -> None:\n"
                "        now = ts if ts is not None else time.monotonic()\n"
                "        self._entries.append((now, val))\n"
                "        self._purge(now)\n\n"
                "    def _purge(self, now: float) -> None:\n"
                "        cutoff = now - self.window\n"
                "        self._entries = [e for e in self._entries if e[0] >= cutoff]\n\n"
                "    def mean(self, now: float | None = None) -> float:\n"
                "        self._purge(now if now is not None else time.monotonic())\n"
                "        if not self._entries: return 0.0\n"
                "        return sum(e[1] for e in self._entries) / len(self._entries)\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from metrics.window import SlidingWindow\n\n"
            "class TestWindow(unittest.TestCase):\n"
            "    def test_sliding(self):\n"
            "        sw = SlidingWindow(10.0)\n"
            "        sw.record(10.0, ts=1.0)\n"
            "        sw.record(20.0, ts=5.0)\n"
            "        self.assertEqual(sw.mean(ts := 6.0), 15.0)\n"
            "        self.assertEqual(sw.mean(ts := 12.0), 20.0)\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    # =============================================================
    # Tier 5: Domain Languages, ASTs & Query Engines
    # =============================================================
    "tier5_datalog_engine": SWEProChallenge(
        challenge_id="tier5_datalog_engine",
        tier=5,
        title="Datalog Engine Unifier and Recursive Relation Evaluator",
        kind="bugfix",
        brief=(
            "Fix rule evaluation and variable unification in `datalog/unifier.py` and `datalog/engine.py`. "
            "Compute fixpoint closures for recursive rules without infinite loops."
        ),
        files={
            "datalog/__init__.py": "from .engine import DatalogEngine\n__all__ = ['DatalogEngine']\n",
            "datalog/unifier.py": (
                "def unify(pattern: tuple, fact: tuple, env: dict) -> dict | None:\n"
                "    if len(pattern) != len(fact): return None\n"
                "    res = dict(env)\n"
                "    for p, f in zip(pattern, fact):\n"
                "        if p.startswith('?'):\n"
                "            if p in res and res[p] != f: return None\n"
                "            res[p] = f\n"
                "        elif p != f: return None\n"
                "    return res\n"
            ),
            "datalog/engine.py": (
                "from .unifier import unify\n\n"
                "class DatalogEngine:\n"
                "    def __init__(self):\n"
                "        self.facts = set()\n\n"
                "    def add_fact(self, *terms) -> None:\n"
                "        self.facts.add(terms)\n\n"
                "    def query(self, *pattern) -> list[dict]:\n"
                "        res = []\n"
                "        for f in sorted(self.facts):\n"
                "            e = unify(pattern, f, {})\n"
                "            if e is not None: res.append(e)\n"
                "        return res\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from datalog.engine import DatalogEngine\n\n"
            "class TestDatalog(unittest.TestCase):\n"
            "    def test_query(self):\n"
            "        e = DatalogEngine()\n"
            "        e.add_fact('edge', 'a', 'b')\n"
            "        self.assertEqual(e.query('edge', '?x', 'b'), [{'?x': 'a'}])\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier5_jsonpath_query_compiler": SWEProChallenge(
        challenge_id="tier5_jsonpath_query_compiler",
        tier=5,
        title="JSONPath AST Parser and Filter Query Evaluator",
        kind="feature",
        brief=(
            "Implement a JSONPath query evaluator in `jsonpath/eval.py` supporting root `$`, "
            "wildcard `*`, child key `.key`, and array index `[i]`."
        ),
        files={
            "jsonpath/__init__.py": "from .eval import jsonpath_eval\n__all__ = ['jsonpath_eval']\n",
            "jsonpath/eval.py": (
                "def jsonpath_eval(expr: str, data: dict | list) -> list:\n"
                "    tokens = expr.strip('$').strip('.').split('.')\n"
                "    current = [data]\n"
                "    for tok in tokens:\n"
                "        if not tok: continue\n"
                "        nxt = []\n"
                "        for item in current:\n"
                "            if tok == '*':\n"
                "                if isinstance(item, dict): nxt.extend(item.values())\n"
                "                elif isinstance(item, list): nxt.extend(item)\n"
                "            elif isinstance(item, dict) and tok in item:\n"
                "                nxt.append(item[tok])\n"
                "        current = nxt\n"
                "    return current\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from jsonpath.eval import jsonpath_eval\n\n"
            "class TestJSONPath(unittest.TestCase):\n"
            "    def test_eval(self):\n"
            "        d = {'store': {'book': [{'price': 10}, {'price': 20}]}}\n"
            "        self.assertEqual(jsonpath_eval('$.store.book', d), [[{'price': 10}, {'price': 20}]])\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier5_sql_micro_planner": SWEProChallenge(
        challenge_id="tier5_sql_micro_planner",
        tier=5,
        title="Micro SQL Query Planner and Execution Engine",
        kind="feature",
        brief=(
            "Implement an in-memory SQL select query planner in `sql/planner.py` supporting "
            "WHERE equality filtering and projection."
        ),
        files={
            "sql/__init__.py": "from .planner import Table\n__all__ = ['Table']\n",
            "sql/planner.py": (
                "class Table:\n"
                "    def __init__(self, name: str, schema: list[str]):\n"
                "        self.name = name\n"
                "        self.schema = schema\n"
                "        self.rows: list[dict] = []\n\n"
                "    def insert(self, **kwargs) -> None:\n"
                "        self.rows.append(kwargs)\n\n"
                "    def select(self, fields: list[str], where: dict | None = None) -> list[dict]:\n"
                "        matched = []\n"
                "        for r in self.rows:\n"
                "            if where and any(r.get(k) != v for k, v in where.items()):\n"
                "                continue\n"
                "            matched.append({f: r.get(f) for f in fields})\n"
                "        return matched\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from sql.planner import Table\n\n"
            "class TestSQL(unittest.TestCase):\n"
            "    def test_select(self):\n"
            "        t = Table('users', ['id', 'name', 'age'])\n"
            "        t.insert(id=1, name='Alice', age=30)\n"
            "        t.insert(id=2, name='Bob', age=25)\n"
            "        res = t.select(['name'], where={'id': 2})\n"
            "        self.assertEqual(res, [{'name': 'Bob'}])\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    # =============================================================
    # Tier 6: Distributed Systems, Protocols & Consensus
    # =============================================================
    "tier6_raft_state_machine": SWEProChallenge(
        challenge_id="tier6_raft_state_machine",
        tier=6,
        title="Raft Log Replication State Machine",
        kind="bugfix",
        brief=(
            "Fix commit index advancement and log conflict truncation in `raft/log.py` and `raft/state.py`."
        ),
        files={
            "raft/__init__.py": "from .state import RaftNode\n__all__ = ['RaftNode']\n",
            "raft/log.py": (
                "class ReplicatedLog:\n"
                "    def __init__(self):\n"
                "        self.entries = []\n"
                "        self.commit_index = 0\n"
            ),
            "raft/state.py": (
                "from .log import ReplicatedLog\n\n"
                "class RaftNode:\n"
                "    def __init__(self, node_id: str):\n"
                "        self.node_id = node_id\n"
                "        self.current_term = 0\n"
                "        self.log = ReplicatedLog()\n\n"
                "    def handle_append_entries(self, term: int, leader_commit: int) -> tuple[bool, int]:\n"
                "        if term < self.current_term:\n"
                "            return False, self.current_term\n"
                "        self.current_term = term\n"
                "        self.log.commit_index = leader_commit\n"
                "        return True, self.current_term\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from raft.state import RaftNode\n\n"
            "class TestRaft(unittest.TestCase):\n"
            "    def test_raft(self):\n"
            "        n = RaftNode('n1')\n"
            "        n.current_term = 3\n"
            "        ok, t = n.handle_append_entries(term=1, leader_commit=0)\n"
            "        self.assertFalse(ok)\n"
            "        ok2, t2 = n.handle_append_entries(term=4, leader_commit=2)\n"
            "        self.assertTrue(ok2)\n"
            "        self.assertEqual(n.log.commit_index, 2)\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier6_vector_clock_causality": SWEProChallenge(
        challenge_id="tier6_vector_clock_causality",
        tier=6,
        title="Vector Clock Distributed Causality Ordering",
        kind="feature",
        brief=(
            "Implement a vector clock causality tracker in `vclock/clock.py` detecting happened-before, "
            "concurrent, and identical distributed event states."
        ),
        files={
            "vclock/__init__.py": "from .clock import VectorClock\n__all__ = ['VectorClock']\n",
            "vclock/clock.py": (
                "class VectorClock:\n"
                "    def __init__(self, node_id: str):\n"
                "        self.node_id = node_id\n"
                "        self.clock: dict[str, int] = {node_id: 0}\n\n"
                "    def tick(self) -> None:\n"
                "        self.clock[self.node_id] += 1\n\n"
                "    def merge(self, other: dict[str, int]) -> None:\n"
                "        for k, v in other.items():\n"
                "            self.clock[k] = max(self.clock.get(k, 0), v)\n"
                "        self.tick()\n\n"
                "    def happens_before(self, other: 'VectorClock') -> bool:\n"
                "        less_or_equal = all(self.clock.get(k, 0) <= other.clock.get(k, 0) for k in self.clock)\n"
                "        strict_less = any(self.clock.get(k, 0) < other.clock.get(k, 0) for k in other.clock)\n"
                "        return less_or_equal and strict_less\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from vclock.clock import VectorClock\n\n"
            "class TestVClock(unittest.TestCase):\n"
            "    def test_causality(self):\n"
            "        c1 = VectorClock('a'); c1.tick()\n"
            "        c2 = VectorClock('b'); c2.merge(c1.clock)\n"
            "        self.assertTrue(c1.happens_before(c2))\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier6_gossip_membership": SWEProChallenge(
        challenge_id="tier6_gossip_membership",
        tier=6,
        title="SWIM Gossip Membership and Heartbeat Table",
        kind="feature",
        brief=(
            "Implement a decentralized gossip membership protocol in `gossip/member.py` tracking node status "
            "(`alive`, `suspect`, `dead`) and heartbeat sequence counters."
        ),
        files={
            "gossip/__init__.py": "from .member import MembershipTable\n__all__ = ['MembershipTable']\n",
            "gossip/member.py": (
                "class MembershipTable:\n"
                "    def __init__(self, local_node_id: str):\n"
                "        self.local_id = local_node_id\n"
                "        self.members = {local_node_id: {'heartbeat': 0, 'status': 'alive'}}\n\n"
                "    def heartbeat(self) -> None:\n"
                "        self.members[self.local_id]['heartbeat'] += 1\n\n"
                "    def update(self, node_id: str, heartbeat: int, status: str) -> None:\n"
                "        if node_id not in self.members or heartbeat > self.members[node_id]['heartbeat']:\n"
                "            self.members[node_id] = {'heartbeat': heartbeat, 'status': status}\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from gossip.member import MembershipTable\n\n"
            "class TestGossip(unittest.TestCase):\n"
            "    def test_member_update(self):\n"
            "        m = MembershipTable('n1')\n"
            "        m.update('n2', 5, 'alive')\n"
            "        self.assertEqual(m.members['n2']['status'], 'alive')\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    # =============================================================
    # Tier 7: Greenfield Autonomous Architectures
    # =============================================================
    "tier7_greenfield_kv_lsm_tree": SWEProChallenge(
        challenge_id="tier7_greenfield_kv_lsm_tree",
        tier=7,
        title="Greenfield Log-Structured Merge (LSM) Tree Key-Value Engine",
        kind="greenfield",
        brief=(
            "Build a lightweight in-memory LSM storage engine in `lsm/engine.py` with in-memory MemTable, "
            "flush threshold, immutable SSTables, and tombstone key deletion."
        ),
        files={
            "lsm/__init__.py": "from .engine import LSMTree\n__all__ = ['LSMTree']\n",
            "lsm/engine.py": (
                "class LSMTree:\n"
                "    def __init__(self, memtable_threshold: int = 3):\n"
                "        self.threshold = memtable_threshold\n"
                "        self.memtable = {}\n"
                "        self.sstables: list[dict] = []\n\n"
                "    def put(self, key: str, value: str) -> None:\n"
                "        self.memtable[key] = value\n"
                "        if len(self.memtable) >= self.threshold:\n"
                "            self.sstables.insert(0, dict(self.memtable))\n"
                "            self.memtable.clear()\n\n"
                "    def get(self, key: str) -> str | None:\n"
                "        if key in self.memtable:\n"
                "            val = self.memtable[key]\n"
                "            return None if val == '__DELETED__' else val\n"
                "        for sst in self.sstables:\n"
                "            if key in sst:\n"
                "                val = sst[key]\n"
                "                return None if val == '__DELETED__' else val\n"
                "        return None\n\n"
                "    def delete(self, key: str) -> None:\n"
                "        self.put(key, '__DELETED__')\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from lsm.engine import LSMTree\n\n"
            "class TestLSM(unittest.TestCase):\n"
            "    def test_lsm_ops(self):\n"
            "        tree = LSMTree(memtable_threshold=2)\n"
            "        tree.put('k1', 'v1')\n"
            "        tree.put('k2', 'v2')  # triggers flush\n"
            "        self.assertEqual(tree.get('k1'), 'v1')\n"
            "        tree.delete('k1')\n"
            "        self.assertIsNone(tree.get('k1'))\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),

    "tier7_greenfield_bytecode_vm": SWEProChallenge(
        challenge_id="tier7_greenfield_bytecode_vm",
        tier=7,
        title="Greenfield Stack-Based Bytecode Virtual Machine",
        kind="greenfield",
        brief=(
            "Build a stack-based virtual machine interpreter in `vm/interpreter.py` supporting "
            "PUSH, POP, ADD, SUB, MUL, JUMP, JUMP_IF_ZERO, and HALT opcodes."
        ),
        files={
            "vm/__init__.py": "from .interpreter import BytecodeVM\n__all__ = ['BytecodeVM']\n",
            "vm/interpreter.py": (
                "class BytecodeVM:\n"
                "    def __init__(self):\n"
                "        self.stack = []\n\n"
                "    def execute(self, bytecode: list[tuple[str, ...]]) -> int:\n"
                "        pc = 0\n"
                "        while pc < len(bytecode):\n"
                "            op = bytecode[pc]\n"
                "            cmd = op[0]\n"
                "            if cmd == 'PUSH':\n"
                "                self.stack.append(op[1])\n"
                "            elif cmd == 'POP':\n"
                "                self.stack.pop()\n"
                "            elif cmd == 'ADD':\n"
                "                b, a = self.stack.pop(), self.stack.pop()\n"
                "                self.stack.append(a + b)\n"
                "            elif cmd == 'SUB':\n"
                "                b, a = self.stack.pop(), self.stack.pop()\n"
                "                self.stack.append(a - b)\n"
                "            elif cmd == 'MUL':\n"
                "                b, a = self.stack.pop(), self.stack.pop()\n"
                "                self.stack.append(a * b)\n"
                "            elif cmd == 'HALT':\n"
                "                break\n"
                "            pc += 1\n"
                "        return self.stack[-1] if self.stack else 0\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from vm.interpreter import BytecodeVM\n\n"
            "class TestVM(unittest.TestCase):\n"
            "    def test_arithmetic(self):\n"
            "        vm = BytecodeVM()\n"
            "        # (3 + 4) * 2 = 14\n"
            "        prog = [('PUSH', 3), ('PUSH', 4), ('ADD',), ('PUSH', 2), ('MUL',), ('HALT',)]\n"
            "        self.assertEqual(vm.execute(prog), 14)\n\n"
            "if __name__ == '__main__': unittest.main()\n"
        ),
    ),
}

try:
    from .domain_challenges import DOMAIN_CHALLENGES
    CHALLENGES.update(DOMAIN_CHALLENGES)
except ImportError:
    pass

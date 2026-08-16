"""Generator script to produce 30 guaranteed 100% valid JSON gold scenarios."""

import json
from pathlib import Path

SCENARIOS_DIR = Path(__file__).resolve().parent

DATA = [
    # Tier 1
    {
        "id": "t1-flatten-list",
        "tier": 1,
        "title": "Flatten nested list maintaining element order",
        "workspace": {
            "utils.py": "def flatten(nested: list) -> list:\n    return nested\n",
            "test_flatten.py": "from utils import flatten\n\ndef test_flatten():\n    assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]\n",
        },
        "target": "    return nested",
        "replacement": "    res = []\n    for x in nested:\n        if isinstance(x, list):\n            res.extend(flatten(x))\n        else:\n            res.append(x)\n    return res",
        "file": "utils.py",
    },
    {
        "id": "t1-clamp-number",
        "tier": 1,
        "title": "Clamp value within min and max boundaries",
        "workspace": {
            "math_utils.py": "def clamp(val: float, min_val: float, max_val: float) -> float:\n    return min(val, max_val)\n",
            "test_clamp.py": "from math_utils import clamp\n\ndef test_clamp():\n    assert clamp(5, 0, 10) == 5\n    assert clamp(-5, 0, 10) == 0\n    assert clamp(15, 0, 10) == 10\n",
        },
        "target": "    return min(val, max_val)",
        "replacement": "    return max(min_val, min(val, max_val))",
        "file": "math_utils.py",
    },
    {
        "id": "t1-palindrome-check",
        "tier": 1,
        "title": "Check if string is a valid palindrome ignoring non-alphanumeric",
        "workspace": {
            "str_utils.py": "def is_palindrome(s: str) -> bool:\n    return s == s[::-1]\n",
            "test_palindrome.py": "from str_utils import is_palindrome\n\ndef test_is_palindrome():\n    assert is_palindrome('A man, a plan, a canal: Panama') is True\n    assert is_palindrome('race a car') is False\n",
        },
        "target": "    return s == s[::-1]",
        "replacement": "    cleaned = [ch.lower() for ch in s if ch.isalnum()]\n    return cleaned == cleaned[::-1]",
        "file": "str_utils.py",
    },
    {
        "id": "t1-title-case",
        "tier": 1,
        "title": "Title case string maintaining minor word lowercase rules",
        "workspace": {
            "text.py": "def to_title_case(text: str) -> str:\n    return text.title()\n",
            "test_text.py": "from text import to_title_case\n\ndef test_title_case():\n    assert to_title_case('the lord of the rings') == 'The Lord of the Rings'\n",
        },
        "target": "    return text.title()",
        "replacement": "    minors = {'of', 'the', 'and', 'in', 'on', 'a', 'an'}\n    words = text.split()\n    res = []\n    for idx, w in enumerate(words):\n        if idx == 0 or w.lower() not in minors:\n            res.append(w.capitalize())\n        else:\n            res.append(w.lower())\n    return ' '.join(res)",
        "file": "text.py",
    },
    # Tier 2
    {
        "id": "t2-config-override",
        "tier": 2,
        "title": "Merge nested configuration dictionary overrides",
        "workspace": {
            "config.py": "def merge_config(base: dict, override: dict) -> dict:\n    res = base.copy()\n    res.update(override)\n    return res\n",
            "test_config.py": "from config import merge_config\n\ndef test_merge_config():\n    base = {'db': {'host': 'localhost', 'port': 5432}, 'debug': False}\n    over = {'db': {'port': 5433}}\n    merged = merge_config(base, over)\n    assert merged['db']['host'] == 'localhost'\n    assert merged['db']['port'] == 5433\n",
        },
        "target": "    res = base.copy()\n    res.update(override)\n    return res",
        "replacement": "    res = base.copy()\n    for k, v in override.items():\n        if k in res and isinstance(res[k], dict) and isinstance(v, dict):\n            res[k] = merge_config(res[k], v)\n        else:\n            res[k] = v\n    return res",
        "file": "config.py",
    },
    {
        "id": "t2-retry-exponential",
        "tier": 2,
        "title": "Exponential backoff retry decorator",
        "workspace": {
            "retry.py": "import time\n\ndef retry_backoff(retries=3, delay=0.01):\n    def decorator(func):\n        def wrapper(*args, **kwargs):\n            return func(*args, **kwargs)\n        return wrapper\n    return decorator\n",
            "test_retry.py": "from retry import retry_backoff\n\nattempts = 0\n@retry_backoff(retries=3, delay=0.01)\ndef flaky():\n    global attempts\n    attempts += 1\n    if attempts < 3:\n        raise ValueError('temp fail')\n    return 'ok'\n\ndef test_flaky():\n    assert flaky() == 'ok'\n",
        },
        "target": "            return func(*args, **kwargs)",
        "replacement": "            current_delay = delay\n            for i in range(retries):\n                try:\n                    return func(*args, **kwargs)\n                except Exception:\n                    if i == retries - 1:\n                        raise\n                    time.sleep(current_delay)\n                    current_delay *= 2",
        "file": "retry.py",
    },
    {
        "id": "t2-cache-lru",
        "tier": 2,
        "title": "LRU Cache eviction policy",
        "workspace": {
            "lru.py": "from collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity: int):\n        self.capacity = capacity\n        self.cache = OrderedDict()\n\n    def get(self, key: int) -> int:\n        if key not in self.cache: return -1\n        return self.cache[key]\n\n    def put(self, key: int, value: int) -> None:\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        if len(self.cache) > self.capacity:\n            self.cache.popitem(last=False)\n",
            "test_lru.py": "from lru import LRUCache\n\ndef test_lru():\n    c = LRUCache(2)\n    c.put(1, 1); c.put(2, 2)\n    assert c.get(1) == 1\n    c.put(3, 3)\n    assert c.get(2) == -1\n",
        },
        "target": "        return self.cache[key]",
        "replacement": "        self.cache.move_to_end(key)\n        return self.cache[key]",
        "file": "lru.py",
    },
    {
        "id": "t2-version-comparator",
        "tier": 2,
        "title": "Semantic version string comparison",
        "workspace": {
            "version.py": "def compare_versions(v1: str, v2: str) -> int:\n    if v1 == v2: return 0\n    return 1 if v1 > v2 else -1\n",
            "test_version.py": "from version import compare_versions\n\ndef test_compare():\n    assert compare_versions('1.2.0', '1.10.0') == -1\n    assert compare_versions('2.0.0', '2.0.0') == 0\n",
        },
        "target": "    if v1 == v2: return 0\n    return 1 if v1 > v2 else -1",
        "replacement": "    p1 = [int(x) for x in v1.split('.')]\n    p2 = [int(x) for x in v2.split('.')]\n    length = max(len(p1), len(p2))\n    p1 += [0] * (length - len(p1))\n    p2 += [0] * (length - len(p2))\n    if p1 == p2: return 0\n    return 1 if p1 > p2 else -1",
        "file": "version.py",
    },
    # Tier 3
    {
        "id": "t3-event-bus",
        "tier": 3,
        "title": "Decoupled pub-sub event bus dispatcher",
        "workspace": {
            "bus.py": "from collections import defaultdict\n\nclass EventBus:\n    def __init__(self):\n        self.subscribers = defaultdict(list)\n\n    def subscribe(self, event_name: str, handler):\n        self.subscribers[event_name].append(handler)\n\n    def publish(self, event_name: str, payload):\n        pass\n",
            "test_bus.py": "from bus import EventBus\n\ndef test_bus():\n    b = EventBus()\n    received = []\n    b.subscribe('user_created', lambda data: received.append(data))\n    b.publish('user_created', {'id': 42})\n    assert received == [{'id': 42}]\n",
        },
        "target": "        pass",
        "replacement": "        for handler in self.subscribers.get(event_name, []):\n            handler(payload)",
        "file": "bus.py",
    },
    {
        "id": "t3-middleware-stack",
        "tier": 3,
        "title": "Compositional HTTP request middleware pipeline",
        "workspace": {
            "pipeline.py": "class Pipeline:\n    def __init__(self):\n        self.middlewares = []\n\n    def use(self, fn):\n        self.middlewares.append(fn)\n\n    def execute(self, req: dict) -> dict:\n        return req\n",
            "test_pipeline.py": "from pipeline import Pipeline\n\ndef test_pipeline():\n    p = Pipeline()\n    p.use(lambda r: {**r, 'a': 1})\n    p.use(lambda r: {**r, 'b': 2})\n    assert p.execute({}) == {'a': 1, 'b': 2}\n",
        },
        "target": "        return req",
        "replacement": "        curr = req\n        for fn in self.middlewares:\n            curr = fn(curr)\n        return curr",
        "file": "pipeline.py",
    },
    {
        "id": "t3-json-patch",
        "tier": 3,
        "title": "Apply RFC 6902 JSON patch operations",
        "workspace": {
            "patcher.py": "def apply_patch(doc: dict, patch: list) -> dict:\n    return doc\n",
            "test_patcher.py": "from patcher import apply_patch\n\ndef test_patch():\n    doc = {'foo': 'bar'}\n    p = [{'op': 'replace', 'path': '/foo', 'value': 'baz'}]\n    assert apply_patch(doc, p) == {'foo': 'baz'}\n",
        },
        "target": "def apply_patch(doc: dict, patch: list) -> dict:\n    return doc",
        "replacement": "def apply_patch(doc: dict, patch: list) -> dict:\n    res = doc.copy()\n    for item in patch:\n        if item.get('op') == 'replace':\n            k = item['path'].lstrip('/')\n            res[k] = item['value']\n    return res",
        "file": "patcher.py",
    },
    {
        "id": "t3-file-rotator",
        "tier": 3,
        "title": "Log file rotation with maximum backup files count",
        "workspace": {
            "rotator.py": "class LogRotator:\n    def __init__(self, max_files=2):\n        self.max_files = max_files\n        self.logs = []\n\n    def write(self, msg: str):\n        self.logs.append(msg)\n",
            "test_rotator.py": "from rotator import LogRotator\n\ndef test_rotator():\n    lr = LogRotator(max_files=2)\n    lr.write('l1'); lr.write('l2'); lr.write('l3')\n    assert len(lr.logs) == 2\n    assert lr.logs == ['l2', 'l3']\n",
        },
        "target": "        self.logs.append(msg)",
        "replacement": "        self.logs.append(msg)\n        if len(self.logs) > self.max_files:\n            self.logs.pop(0)",
        "file": "rotator.py",
    },
    # Tier 4
    {
        "id": "t4-circuit-breaker",
        "tier": 4,
        "title": "Stateful service circuit breaker pattern",
        "workspace": {
            "circuit.py": "class CircuitBreaker:\n    def __init__(self, threshold=2):\n        self.threshold = threshold\n        self.failures = 0\n        self.state = 'CLOSED'\n\n    def call(self, func):\n        if self.state == 'OPEN':\n            raise RuntimeError('Circuit is OPEN')\n        try:\n            res = func()\n            self.failures = 0\n            return res\n        except Exception:\n            raise\n",
            "test_circuit.py": "from circuit import CircuitBreaker\nimport pytest\n\ndef test_circuit():\n    cb = CircuitBreaker(threshold=2)\n    def fail(): raise ValueError('err')\n    with pytest.raises(ValueError):\n        cb.call(fail)\n    with pytest.raises(ValueError):\n        cb.call(fail)\n    assert cb.state == 'OPEN'\n    with pytest.raises(RuntimeError):\n        cb.call(fail)\n",
        },
        "target": "        except Exception:\n            raise",
        "replacement": "        except Exception:\n            self.failures += 1\n            if self.failures >= self.threshold:\n                self.state = 'OPEN'\n            raise",
        "file": "circuit.py",
    },
    {
        "id": "t4-rate-limiter",
        "tier": 4,
        "title": "Sliding window rate limiter algorithm",
        "workspace": {
            "limiter.py": "class RateLimiter:\n    def __init__(self, limit=2):\n        self.limit = limit\n        self.requests = []\n\n    def allow(self, now: float) -> bool:\n        if len(self.requests) < self.limit:\n            self.requests.append(now)\n            return True\n        return False\n",
            "test_limiter.py": "from limiter import RateLimiter\n\ndef test_limiter():\n    rl = RateLimiter(limit=2)\n    assert rl.allow(0.0) is True\n    assert rl.allow(0.5) is True\n    assert rl.allow(0.8) is False\n    assert rl.allow(1.2) is True\n",
        },
        "target": "        if len(self.requests) < self.limit:\n            self.requests.append(now)\n            return True\n        return False",
        "replacement": "        self.requests = [t for t in self.requests if now - t < 1.0]\n        if len(self.requests) < self.limit:\n            self.requests.append(now)\n            return True\n        return False",
        "file": "limiter.py",
    },
    {
        "id": "t4-saga-orchestration",
        "tier": 4,
        "title": "Distributed Saga compensation workflow on failure",
        "workspace": {
            "saga.py": "class Saga:\n    def __init__(self):\n        self.steps = []\n        self.compensated = []\n\n    def add_step(self, action, compensate):\n        self.steps.append((action, compensate))\n\n    def execute(self):\n        for act, _ in self.steps:\n            act()\n",
            "test_saga.py": "from saga import Saga\nimport pytest\n\ndef test_saga():\n    s = Saga()\n    comp = []\n    s.add_step(lambda: None, lambda: comp.append('s1'))\n    def fail(): raise RuntimeError('err')\n    s.add_step(fail, lambda: comp.append('s2'))\n    with pytest.raises(RuntimeError):\n        s.execute()\n    assert comp == ['s1']\n",
        },
        "target": "        for act, _ in self.steps:\n            act()",
        "replacement": "        executed = []\n        for act, comp in self.steps:\n            try:\n                act()\n                executed.append(comp)\n            except Exception:\n                for rollback in reversed(executed):\n                    rollback()\n                raise",
        "file": "saga.py",
    },
    {
        "id": "t4-token-bucket",
        "tier": 4,
        "title": "Token bucket rate limiter with automatic refill",
        "workspace": {
            "bucket.py": "class TokenBucket:\n    def __init__(self, capacity: int, fill_rate: float):\n        self.capacity = capacity\n        self.fill_rate = fill_rate\n        self.tokens = capacity\n        self.last_time = 0.0\n\n    def consume(self, tokens: int, now: float) -> bool:\n        if self.tokens >= tokens:\n            self.tokens -= tokens\n            return True\n        return False\n",
            "test_bucket.py": "from bucket import TokenBucket\n\ndef test_bucket():\n    tb = TokenBucket(capacity=10, fill_rate=1.0)\n    assert tb.consume(10, 0.0) is True\n    assert tb.consume(1, 0.0) is False\n    assert tb.consume(2, 2.0) is True\n",
        },
        "target": "        if self.tokens >= tokens:\n            self.tokens -= tokens\n            return True\n        return False",
        "replacement": "        delta = now - self.last_time\n        self.tokens = min(self.capacity, self.tokens + delta * self.fill_rate)\n        self.last_time = now\n        if self.tokens >= tokens:\n            self.tokens -= tokens\n            return True\n        return False",
        "file": "bucket.py",
    },
    # Tier 5
    {
        "id": "t5-immutable-trie",
        "tier": 5,
        "title": "Persistent immutable prefix trie data structure",
        "workspace": {
            "trie.py": "from dataclasses import dataclass, field\nfrom typing import Dict\n\n@dataclass(frozen=True)\nclass TrieNode:\n    is_end: bool = False\n    children: Dict[str, 'TrieNode'] = field(default_factory=dict)\n\ndef insert(root: TrieNode, word: str) -> TrieNode:\n    return root\n",
            "test_trie.py": "from trie import TrieNode, insert\n\ndef test_trie():\n    root0 = TrieNode()\n    root1 = insert(root0, 'cat')\n    assert root0.children == {}\n    assert 'c' in root1.children\n",
        },
        "target": "def insert(root: TrieNode, word: str) -> TrieNode:\n    return root",
        "replacement": "def insert(root: TrieNode, word: str) -> TrieNode:\n    if not word:\n        return TrieNode(is_end=True, children=root.children)\n    ch = word[0]\n    child = root.children.get(ch, TrieNode())\n    new_child = insert(child, word[1:])\n    new_children = dict(root.children)\n    new_children[ch] = new_child\n    return TrieNode(is_end=root.is_end, children=new_children)",
        "file": "trie.py",
    },
    {
        "id": "t5-persistent-b-tree",
        "tier": 5,
        "title": "Immutable persistent B-tree node lookup and insertion",
        "workspace": {
            "btree.py": "from dataclasses import dataclass\nfrom typing import Tuple\n\n@dataclass(frozen=True)\nclass BTreeNode:\n    keys: Tuple[int, ...]\n    children: Tuple['BTreeNode', ...]\n\ndef search_key(node: BTreeNode, key: int) -> bool:\n    return False\n",
            "test_btree.py": "from btree import BTreeNode, search_key\n\ndef test_btree():\n    child = BTreeNode(keys=(10, 20), children=())\n    root = BTreeNode(keys=(30,), children=(child,))\n    assert search_key(root, 10) is True\n    assert search_key(root, 40) is False\n",
        },
        "target": "def search_key(node: BTreeNode, key: int) -> bool:\n    return False",
        "replacement": "def search_key(node: BTreeNode, key: int) -> bool:\n    i = 0\n    while i < len(node.keys) and key > node.keys[i]:\n        i += 1\n    if i < len(node.keys) and key == node.keys[i]:\n        return True\n    if not node.children:\n        return False\n    return search_key(node.children[i], key)",
        "file": "btree.py",
    },
    {
        "id": "t5-async-event-loop",
        "tier": 5,
        "title": "Deterministic cooperative async event loop scheduler",
        "workspace": {
            "loop.py": "from collections import deque\n\nclass EventLoop:\n    def __init__(self):\n        self.tasks = deque()\n\n    def spawn(self, coro):\n        self.tasks.append(coro)\n\n    def run(self):\n        pass\n",
            "test_loop.py": "from loop import EventLoop\n\ndef test_loop():\n    results = []\n    def task(val):\n        results.append(val)\n        yield\n        results.append(val + 10)\n    el = EventLoop()\n    el.spawn(task(1))\n    el.run()\n    assert results == [1, 11]\n",
        },
        "target": "        pass",
        "replacement": "        while self.tasks:\n            task = self.tasks.popleft()\n            try:\n                next(task)\n                self.tasks.append(task)\n            except StopIteration:\n                pass",
        "file": "loop.py",
    },
]


def generate():
    for item in DATA:
        sc = {
            "id": item["id"],
            "tier": item["tier"],
            "title": item["title"],
            "workspace": item["workspace"],
            "turns": [
                {
                    "tool_messages_seen": 0,
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": "view_file",
                                "arguments": json.dumps({"path": item["file"]}),
                            },
                        }
                    ],
                    "finish_reason": "tool_calls",
                },
                {
                    "tool_messages_seen": 1,
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": "edit_file",
                                "arguments": json.dumps(
                                    {
                                        "path": item["file"],
                                        "target": item["target"],
                                        "replacement": item["replacement"],
                                    }
                                ),
                            },
                        }
                    ],
                    "finish_reason": "tool_calls",
                },
                {
                    "tool_messages_seen": 2,
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": "run_command",
                                "arguments": json.dumps({"command": "pytest"}),
                            },
                        }
                    ],
                    "finish_reason": "tool_calls",
                },
                {"tool_messages_seen": 3, "tool_calls": [], "finish_reason": "stop"},
            ],
        }

        path = SCENARIOS_DIR / f"{item['id']}.json"
        path.write_text(json.dumps(sc, indent=2), encoding="utf-8")
        print(f"Generated {path.name}")


if __name__ == "__main__":
    generate()

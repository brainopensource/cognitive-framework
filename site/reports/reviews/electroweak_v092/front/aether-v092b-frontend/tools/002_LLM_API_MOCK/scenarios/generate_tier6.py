"""Generator script for Tier 6 (SWE-bench Pro & Opus-Level SOTA) scenarios."""

import json
from pathlib import Path

SCENARIOS_DIR = Path(__file__).resolve().parent

TIER6_DATA = [
    {
        "id": "t6-persistent-avl-tree",
        "tier": 6,
        "title": "Immutable persistent AVL tree with path copying and range queries",
        "workspace": {
            "avl.py": """from dataclasses import dataclass
from typing import Optional, Tuple, List

@dataclass(frozen=True)
class AVLNode:
    key: int
    val: str
    height: int = 1
    left: Optional['AVLNode'] = None
    right: Optional['AVLNode'] = None

def insert(node: Optional[AVLNode], key: int, val: str) -> AVLNode:
    # Bug: returns simple non-balancing node without path copying or rotations
    if not node:
        return AVLNode(key=key, val=val)
    return node

def range_query(node: Optional[AVLNode], low: int, high: int) -> List[Tuple[int, str]]:
    # Bug: returns empty list
    return []
""",
            "test_avl.py": """from avl import AVLNode, insert, range_query

def test_persistent_avl():
    r0 = None
    r1 = insert(r0, 10, 'ten')
    r2 = insert(r1, 20, 'twenty')
    r3 = insert(r2, 5, 'five')
    r4 = insert(r3, 15, 'fifteen')
    
    assert range_query(r4, 5, 15) == [(5, 'five'), (10, 'ten'), (15, 'fifteen')]
    assert r1.right is None  # Immutability check
""",
        },
        "file": "avl.py",
        "target": "def insert(node: Optional[AVLNode], key: int, val: str) -> AVLNode:\n    # Bug: returns simple non-balancing node without path copying or rotations\n    if not node:\n        return AVLNode(key=key, val=val)\n    return node\n\ndef range_query(node: Optional[AVLNode], low: int, high: int) -> List[Tuple[int, str]]:\n    # Bug: returns empty list\n    return []",
        "replacement": """def _h(n: Optional[AVLNode]) -> int:
    return n.height if n else 0

def _b(n: Optional[AVLNode]) -> int:
    return _h(n.left) - _h(n.right) if n else 0

def _make_node(key: int, val: str, left: Optional[AVLNode], right: Optional[AVLNode]) -> AVLNode:
    h = 1 + max(_h(left), _h(right))
    return AVLNode(key=key, val=val, height=h, left=left, right=right)

def _rot_right(y: AVLNode) -> AVLNode:
    x = y.left
    assert x is not None
    return _make_node(x.key, x.val, x.left, _make_node(y.key, y.val, x.right, y.right))

def _rot_left(x: AVLNode) -> AVLNode:
    y = x.right
    assert y is not None
    return _make_node(y.key, y.val, _make_node(x.key, x.val, x.left, y.left), y.right)

def insert(node: Optional[AVLNode], key: int, val: str) -> AVLNode:
    if not node:
        return AVLNode(key=key, val=val)
    if key < node.key:
        new_left = insert(node.left, key, val)
        n = _make_node(node.key, node.val, new_left, node.right)
    elif key > node.key:
        new_right = insert(node.right, key, val)
        n = _make_node(node.key, node.val, node.left, new_right)
    else:
        return _make_node(key, val, node.left, node.right)

    bal = _b(n)
    if bal > 1 and key < n.left.key:
        return _rot_right(n)
    if bal < -1 and key > n.right.key:
        return _rot_left(n)
    if bal > 1 and key > n.left.key:
        return _rot_right(_make_node(n.key, n.val, _rot_left(n.left), n.right))
    if bal < -1 and key < n.right.key:
        return _rot_left(_make_node(n.key, n.val, n.left, _rot_right(n.right)))
    return n

def range_query(node: Optional[AVLNode], low: int, high: int) -> List[Tuple[int, str]]:
    res = []
    def dfs(n):
        if not n: return
        if n.key > low: dfs(n.left)
        if low <= n.key <= high: res.append((n.key, n.val))
        if n.key < high: dfs(n.right)
    dfs(node)
    return res""",
    },
    {
        "id": "t6-async-actor-engine",
        "tier": 6,
        "title": "Deterministic actor event loop with mailbox queueing",
        "workspace": {
            "actor.py": """from collections import deque
from typing import Dict, Any, Callable

class Actor:
    def __init__(self, name: str, handler: Callable):
        self.name = name
        self.handler = handler
        self.mailbox = deque()

    def send(self, msg: Any):
        self.mailbox.append(msg)

    def step(self) -> bool:
        # Bug: fails to process queued mailbox messages
        return False
""",
            "test_actor.py": """from actor import Actor

def test_actor():
    received = []
    a = Actor('worker', lambda m: received.append(m))
    a.send('job1')
    a.send('job2')
    while a.step():
        pass
    assert received == ['job1', 'job2']
""",
        },
        "file": "actor.py",
        "target": "    def step(self) -> bool:\n        # Bug: fails to process queued mailbox messages\n        return False",
        "replacement": """    def step(self) -> bool:
        if not self.mailbox:
            return False
        msg = self.mailbox.popleft()
        self.handler(msg)
        return True""",
    },
    {
        "id": "t6-distributed-raft-consensus",
        "tier": 6,
        "title": "Raft leader election and log replication state machine",
        "workspace": {
            "raft.py": """class RaftNode:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.current_term = 0
        self.state = 'FOLLOWER'
        self.voted_for = None

    def request_vote(self, term: int, candidate_id: int) -> bool:
        # Bug: fails to update term and grant vote
        return False
""",
            "test_raft.py": """from raft import RaftNode

def test_raft():
    n = RaftNode(1)
    granted = n.request_vote(term=1, candidate_id=2)
    assert granted is True
    assert n.current_term == 1
    assert n.voted_for == 2
""",
        },
        "file": "raft.py",
        "target": "    def request_vote(self, term: int, candidate_id: int) -> bool:\n        # Bug: fails to update term and grant vote\n        return False",
        "replacement": """    def request_vote(self, term: int, candidate_id: int) -> bool:
        if term > self.current_term:
            self.current_term = term
            self.state = 'FOLLOWER'
            self.voted_for = None
        if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
            self.voted_for = candidate_id
            return True
        return False""",
    },
    {
        "id": "t6-compiler-ast-optimizer",
        "tier": 6,
        "title": "Multi-pass AST transformation for constant folding",
        "workspace": {
            "ast_opt.py": """class ASTOptimizer:
    def fold_constants(self, expr: tuple) -> Any:
        # Bug: returns expression as is without folding arithmetic
        return expr
""",
            "test_ast_opt.py": """from ast_opt import ASTOptimizer

def test_fold():
    opt = ASTOptimizer()
    assert opt.fold_constants(('+', 2, 3)) == 5
    assert opt.fold_constants(('+', ('*', 2, 4), 5)) == 13
""",
        },
        "file": "ast_opt.py",
        "target": "    def fold_constants(self, expr: tuple) -> Any:\n        # Bug: returns expression as is without folding arithmetic\n        return expr",
        "replacement": """    def fold_constants(self, expr: Any) -> Any:
        if not isinstance(expr, tuple):
            return expr
        op, left, right = expr[0], self.fold_constants(expr[1]), self.fold_constants(expr[2])
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if op == '+': return left + right
            if op == '*': return left * right
            if op == '-': return left - right
        return (op, left, right)""",
    },
    {
        "id": "t6-transactional-mvcc-db",
        "tier": 6,
        "title": "Multi-version concurrency control in-memory database with snapshot isolation",
        "workspace": {
            "mvcc.py": """class MVCCStore:
    def __init__(self):
        self.store = {}

    def put(self, key: str, val: str, tx_id: int):
        # Bug: overwrites key without snapshot versioning
        self.store[key] = val

    def get(self, key: str, tx_id: int) -> str:
        return self.store.get(key, '')
""",
            "test_mvcc.py": """from mvcc import MVCCStore

def test_mvcc():
    db = MVCCStore()
    db.put('k1', 'v1', tx_id=10)
    db.put('k1', 'v2', tx_id=20)
    assert db.get('k1', tx_id=15) == 'v1'
    assert db.get('k1', tx_id=25) == 'v2'
""",
        },
        "file": "mvcc.py",
        "target": "    def put(self, key: str, val: str, tx_id: int):\n        # Bug: overwrites key without snapshot versioning\n        self.store[key] = val\n\n    def get(self, key: str, tx_id: int) -> str:\n        return self.store.get(key, '')",
        "replacement": """    def put(self, key: str, val: str, tx_id: int):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((tx_id, val))

    def get(self, key: str, tx_id: int) -> str:
        versions = self.store.get(key, [])
        valid = [v for ver_tx, v in versions if ver_tx <= tx_id]
        return valid[-1] if valid else ''""",
    },
]

def generate_tier6():
    for item in TIER6_DATA:
        sc = {
            "id": item["id"],
            "tier": item["tier"],
            "title": item["title"],
            "workspace": item["workspace"],
            "turns": [
                {
                    "tool_messages_seen": 0,
                    "tool_calls": [{"type": "function", "function": {"name": "view_file", "arguments": json.dumps({"path": item["file"]})}}],
                    "finish_reason": "tool_calls",
                },
                {
                    "tool_messages_seen": 1,
                    "tool_calls": [{"type": "function", "function": {"name": "edit_file", "arguments": json.dumps({"path": item["file"], "target": item["target"], "replacement": item["replacement"]})}}],
                    "finish_reason": "tool_calls",
                },
                {
                    "tool_messages_seen": 2,
                    "tool_calls": [{"type": "function", "function": {"name": "run_command", "arguments": json.dumps({"command": "pytest"})}}],
                    "finish_reason": "tool_calls",
                },
                {"tool_messages_seen": 3, "tool_calls": [], "finish_reason": "stop"},
            ],
        }
        path = SCENARIOS_DIR / f"{item['id']}.json"
        path.write_text(json.dumps(sc, indent=2), encoding="utf-8")
        print(f"Generated Tier 6 scenario {path.name}")

if __name__ == "__main__":
    generate_tier6()

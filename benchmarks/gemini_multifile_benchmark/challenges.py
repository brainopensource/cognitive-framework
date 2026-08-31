"""Gemini Multi-File & Large-Context Benchmark Challenges.

These challenges test agentic coding harnesses on complex multi-file engineering problems:
1. Sharded Consistent Hash Ring with Rebalancing & Virtual Nodes (Multi-file: ring.py, node.py, partition.py).
2. Distributed 2PC Transaction Coordinator with WAL Recovery (Multi-file: coordinator.py, participant.py, wal.py).
3. Merkle Radix Trie with Cryptographic Inclusion Proofs (Multi-file: trie.py, proof.py, serializer.py).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class MultifileChallenge:
    challenge_id: str
    tier: int
    title: str
    brief: str
    files: Mapping[str, str]
    oracle_code: str


GEMINI_CHALLENGES: dict[str, MultifileChallenge] = {
    "g1_sharded_hash_ring": MultifileChallenge(
        challenge_id="g1_sharded_hash_ring",
        tier=3,
        title="Distributed Sharded Consistent Hash Ring with Dynamic Rebalancing",
        brief=(
            "Fix the consistent hash ring implementation across `cluster/ring.py`, `cluster/node.py`, and `cluster/partition.py`.\n"
            "Requirements:\n"
            "1. `node.py`: Virtual nodes must generate deterministic MD5/SHA256 tokens using format f'{node_id}#vnode_{i}'.\n"
            "2. `ring.py`: When adding/removing nodes, ring keys must map clockwise to the next available token in O(log N) bisect lookup.\n"
            "3. `partition.py`: Keys must rebalance strictly only for the keys belonging to the affected partitions upon node addition/removal."
        ),
        files={
            "cluster/__init__.py": "from .ring import HashRing\nfrom .node import Node\nfrom .partition import PartitionManager\n",
            "cluster/node.py": (
                "import hashlib\n"
                "from dataclasses import dataclass\n"
                "from typing import List\n\n"
                "@dataclass\n"
                "class Node:\n"
                "    node_id: str\n"
                "    vnode_count: int = 3\n\n"
                "    def generate_tokens(self) -> List[int]:\n"
                "        tokens = []\n"
                "        for i in range(self.vnode_count):\n"
                "            # BUG: Missing virtual node index in token generation string\n"
                "            h = hashlib.sha256(self.node_id.encode()).hexdigest()\n"
                "            tokens.append(int(h[:16], 16))\n"
                "        return tokens\n"
            ),
            "cluster/ring.py": (
                "import bisect\n"
                "from typing import Dict, Optional, List\n"
                "import hashlib\n"
                "from .node import Node\n\n"
                "class HashRing:\n"
                "    def __init__(self):\n"
                "        self._ring: List[int] = []\n"
                "        self._token_to_node: Dict[int, str] = {}\n"
                "        self._nodes: Dict[str, Node] = {}\n\n"
                "    def add_node(self, node: Node) -> None:\n"
                "        self._nodes[node.node_id] = node\n"
                "        for token in node.generate_tokens():\n"
                "            bisect.insort(self._ring, token)\n"
                "            self._token_to_node[token] = node.node_id\n\n"
                "    def remove_node(self, node_id: str) -> None:\n"
                "        if node_id not in self._nodes:\n"
                "            return\n"
                "        node = self._nodes.pop(node_id)\n"
                "        for token in node.generate_tokens():\n"
                "            if token in self._token_to_node:\n"
                "                del self._token_to_node[token]\n"
                "                self._ring.remove(token)\n\n"
                "    def get_node(self, key: str) -> Optional[str]:\n"
                "        if not self._ring:\n"
                "            return None\n"
                "        h = int(hashlib.sha256(key.encode()).hexdigest()[:16], 16)\n"
                "        idx = bisect.bisect_right(self._ring, h)\n"
                "        # BUG: Fails to wrap around when key hash is greater than last token\n"
                "        if idx == len(self._ring):\n"
                "            return None\n"
                "        return self._token_to_node[self._ring[idx]]\n"
            ),
            "cluster/partition.py": (
                "from typing import Dict, List, Set\n"
                "from .ring import HashRing\n\n"
                "class PartitionManager:\n"
                "    def __init__(self, ring: HashRing):\n"
                "        self.ring = ring\n"
                "        self.key_store: Dict[str, str] = {}\n\n"
                "    def put(self, key: str, value: str) -> str:\n"
                "        node_id = self.ring.get_node(key)\n"
                "        if not node_id:\n"
                "            raise RuntimeError('No node available')\n"
                "        self.key_store[key] = value\n"
                "        return node_id\n\n"
                "    def rebalanced_keys_for_new_node(self, old_ring_mapping: Dict[str, str]) -> Set[str]:\n"
                "        moved = set()\n"
                "        for k in self.key_store:\n"
                "            current_node = self.ring.get_node(k)\n"
                "            if old_ring_mapping.get(k) != current_node:\n"
                "                moved.add(k)\n"
                "        return moved\n"
            ),
        },
        oracle_code=(
            "import unittest\n"
            "from cluster.node import Node\n"
            "from cluster.ring import HashRing\n"
            "from cluster.partition import PartitionManager\n\n"
            "class TestHashRingOracle(unittest.TestCase):\n"
            "    def test_vnode_distinct_tokens(self):\n"
            "        n = Node('node-A', vnode_count=5)\n"
            "        tokens = n.generate_tokens()\n"
            "        self.assertEqual(len(set(tokens)), 5)\n\n"
            "    def test_ring_wraparound_and_distribution(self):\n"
            "        ring = HashRing()\n"
            "        ring.add_node(Node('node-1', vnode_count=5))\n"
            "        ring.add_node(Node('node-2', vnode_count=5))\n"
            "        # Assert wrap-around works for all keys\n"
            "        for i in range(50):\n"
            "            node = ring.get_node(f'test-key-{i}')\n"
            "            self.assertIn(node, ('node-1', 'node-2'))\n\n"
            "    def test_partition_rebalance(self):\n"
            "        ring = HashRing()\n"
            "        ring.add_node(Node('node-1', vnode_count=5))\n"
            "        pm = PartitionManager(ring)\n"
            "        old_map = {}\n"
            "        for i in range(20):\n"
            "            k = f'k-{i}'\n"
            "            old_map[k] = pm.put(k, f'v-{i}')\n"
            "        ring.add_node(Node('node-2', vnode_count=5))\n"
            "        moved = pm.rebalanced_keys_for_new_node(old_map)\n"
            "        # Some keys should move, but not all (consistent hashing invariant)\n"
            "        self.assertTrue(0 < len(moved) < 20)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),
    "g2_distributed_2pc_wal": MultifileChallenge(
        challenge_id="g2_distributed_2pc_wal",
        tier=4,
        title="Distributed Two-Phase Commit Coordinator with Crash-Safe WAL Replay",
        brief=(
            "Repair the distributed 2PC engine across `two_phase/coordinator.py`, `two_phase/participant.py`, and `two_phase/wal.py`.\n"
            "1. `wal.py`: Append-only log must correctly encode/decode transaction status ('PREPARED', 'COMMITTED', 'ABORTED').\n"
            "2. `coordinator.py`: If ANY participant votes False during PREPARE, coordinator MUST issue ABORT to ALL participants and log ABORTED.\n"
            "3. `coordinator.py`: On recovery, replay uncommitted transactions from WAL and resolve in-doubt transactions."
        ),
        files={
            "two_phase/__init__.py": "from .coordinator import Coordinator\nfrom .participant import Participant\nfrom .wal import WriteAheadLog\n",
            "two_phase/wal.py": (
                "import json\n"
                "from pathlib import Path\n"
                "from typing import List, Dict, Any\n\n"
                "class WriteAheadLog:\n"
                "    def __init__(self, filepath: Path):\n"
                "        self.filepath = Path(filepath)\n"
                "        self.filepath.parent.mkdir(parents=True, exist_ok=True)\n\n"
                "    def log(self, tx_id: str, state: str, payload: Dict[str, Any]) -> None:\n"
                "        entry = json.dumps({'tx_id': tx_id, 'state': state, 'payload': payload}) + '\\n'\n"
                "        with open(self.filepath, 'a', encoding='utf-8') as f:\n"
                "            f.write(entry)\n\n"
                "    def read_all(self) -> List[Dict[str, Any]]:\n"
                "        if not self.filepath.exists():\n"
                "            return []\n"
                "        entries = []\n"
                "        with open(self.filepath, 'r', encoding='utf-8') as f:\n"
                "            for line in f:\n"
                "                if line.strip():\n"
                "                    entries.append(json.loads(line.strip()))\n"
                "        return entries\n"
            ),
            "two_phase/participant.py": (
                "from typing import Dict, Any\n\n"
                "class Participant:\n"
                "    def __init__(self, pid: str, can_commit: bool = True):\n"
                "        self.pid = pid\n"
                "        self.can_commit = can_commit\n"
                "        self.committed_data: Dict[str, Any] = {}\n"
                "        self.prepared_data: Dict[str, Any] = {}\n\n"
                "    def prepare(self, tx_id: str, payload: Dict[str, Any]) -> bool:\n"
                "        if not self.can_commit:\n"
                "            return False\n"
                "        self.prepared_data[tx_id] = payload\n"
                "        return True\n\n"
                "    def commit(self, tx_id: str) -> None:\n"
                "        if tx_id in self.prepared_data:\n"
                "            self.committed_data.update(self.prepared_data.pop(tx_id))\n\n"
                "    def abort(self, tx_id: str) -> None:\n"
                "        self.prepared_data.pop(tx_id, None)\n"
            ),
            "two_phase/coordinator.py": (
                "from typing import List, Dict, Any\n"
                "from pathlib import Path\n"
                "from .participant import Participant\n"
                "from .wal import WriteAheadLog\n\n"
                "class Coordinator:\n"
                "    def __init__(self, wal_path: Path, participants: List[Participant]):\n"
                "        self.wal = WriteAheadLog(wal_path)\n"
                "        self.participants = participants\n\n"
                "    def execute_transaction(self, tx_id: str, payload: Dict[str, Any]) -> bool:\n"
                "        self.wal.log(tx_id, 'PREPARE_REQUESTED', payload)\n"
                "        votes = [p.prepare(tx_id, payload) for p in self.participants]\n"
                "        # BUG: Commits even if some participants voted False!\n"
                "        if any(votes):\n"
                "            self.wal.log(tx_id, 'COMMITTED', payload)\n"
                "            for p in self.participants:\n"
                "                p.commit(tx_id)\n"
                "            return True\n"
                "        else:\n"
                "            self.wal.log(tx_id, 'ABORTED', payload)\n"
                "            for p in self.participants:\n"
                "                p.abort(tx_id)\n"
                "            return False\n"
            ),
        },
        oracle_code=(
            "import unittest, tempfile\n"
            "from pathlib import Path\n"
            "from two_phase.coordinator import Coordinator\n"
            "from two_phase.participant import Participant\n\n"
            "class Test2PCOracle(unittest.TestCase):\n"
            "    def setUp(self):\n"
            "        self.tmp = tempfile.TemporaryDirectory()\n"
            "        self.wal_file = Path(self.tmp.name) / 'wal.log'\n\n"
            "    def tearDown(self):\n"
            "        self.tmp.cleanup()\n\n"
            "    def test_unanimous_commit(self):\n"
            "        p1 = Participant('p1', True)\n"
            "        p2 = Participant('p2', True)\n"
            "        coord = Coordinator(self.wal_file, [p1, p2])\n"
            "        res = coord.execute_transaction('tx-1', {'key': 'val1'})\n"
            "        self.assertTrue(res)\n"
            "        self.assertEqual(p1.committed_data.get('key'), 'val1')\n"
            "        self.assertEqual(p2.committed_data.get('key'), 'val1')\n\n"
            "    def test_single_failure_causes_global_abort(self):\n"
            "        p1 = Participant('p1', True)\n"
            "        p2 = Participant('p2', False)  # Refuses\n"
            "        coord = Coordinator(self.wal_file, [p1, p2])\n"
            "        res = coord.execute_transaction('tx-2', {'key': 'val2'})\n"
            "        self.assertFalse(res)\n"
            "        self.assertNotIn('key', p1.committed_data)\n"
            "        self.assertNotIn('key', p2.committed_data)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
    ),
}

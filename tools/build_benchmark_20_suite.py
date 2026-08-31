#!/usr/bin/env python3
"""Generator and Builder for Benchmark 20 Suite.

Constructs 10 Brownfield and 10 Greenfield challenges with:
- Multi-file source and tests
- Precise specifications (SPEC.md / README.md)
- Initial falsifiers that fail in the initial state
- Cryptographic SHA-256 state manifests
"""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = ROOT / "benchmarks" / "benchmark_20_suite"


def sha256_file(path: Path) -> str:
    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()


# ==============================================================================
# 10 BROWNFIELD CHALLENGES DEFINITIONS
# ==============================================================================

BROWNFIELD_CHALLENGES = {
    # 01: Rate Limiter Lease Recovery
    "01_rate_limiter_lease_recovery": {
        "files": {
            "src/rate_limiter.py": """import time
from typing import Dict, Any, Optional

class RateLimiter:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.available = capacity
        self.active_leases: Dict[str, Dict[str, Any]] = {}

    def acquire(self, lease_id: str, tokens: int, ttl_seconds: float = 30.0) -> bool:
        if tokens > self.available:
            return False
        self.available -= tokens
        self.active_leases[lease_id] = {
            "tokens": tokens,
            "expires_at": time.time() + ttl_seconds
        }
        return True

    def release(self, lease_id: str) -> bool:
        if lease_id in self.active_leases:
            data = self.active_leases.pop(lease_id)
            self.available += data["tokens"]
            return True
        return False

    def clean_expired(self, current_time: float) -> int:
        # BUG: Expired leases are popped from active_leases,
        # but self.available is NOT refunded with the expired tokens!
        expired = [lid for lid, data in self.active_leases.items() if data["expires_at"] <= current_time]
        for lid in expired:
            self.active_leases.pop(lid, None)
        return len(expired)
""",
            "src/governor.py": """from typing import Callable, Any
from .rate_limiter import RateLimiter

class ConcurrencyGovernor:
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    def execute_with_lease(self, lease_id: str, tokens: int, fn: Callable[[], Any]) -> Any:
        if not self.limiter.acquire(lease_id, tokens):
            raise RuntimeError(f"Insufficient capacity for lease {lease_id}")
        try:
            return fn()
        finally:
            self.limiter.release(lease_id)
""",
            "test/test_limiter.py": """import unittest
import time
from src.rate_limiter import RateLimiter
from src.governor import ConcurrencyGovernor

class TestRateLimiter(unittest.TestCase):
    def test_acquire_and_release(self):
        limiter = RateLimiter(capacity=100)
        self.assertTrue(limiter.acquire("lease-1", 40))
        self.assertEqual(limiter.available, 60)
        self.assertTrue(limiter.release("lease-1"))
        self.assertEqual(limiter.available, 100)

    def test_clean_expired_refunds_tokens(self):
        limiter = RateLimiter(capacity=100)
        self.assertTrue(limiter.acquire("lease-exp", 40, ttl_seconds=1.0))
        self.assertEqual(limiter.available, 60)
        
        # Fast forward time to expire lease
        future_time = time.time() + 10.0
        cleaned = limiter.clean_expired(future_time)
        self.assertEqual(cleaned, 1)
        # Falsifier Assertion: available capacity MUST be refunded back to 100
        self.assertEqual(limiter.available, 100, f"Leakage detected: expected 100 available, got {limiter.available}")

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: Rate Limiter Token Conservation (Invariant K-09)

The `RateLimiter` must maintain the invariant:
`self.available + sum(lease['tokens'] for lease in self.active_leases.values()) == self.capacity`

When `clean_expired(current_time)` is invoked:
1. All leases where `expires_at <= current_time` MUST be removed from `active_leases`.
2. The tokens allocated to each expired lease MUST be returned to `self.available`.
3. The method must return the integer count of cleaned leases.
""",
        }
    },

    # 02: Ed25519 Signature Replay
    "02_ed25519_signature_replay": {
        "files": {
            "src/signer.py": """import hashlib
import json
import time
from cryptography.hazmat.primitives.asymmetric import ed25519

class OperatorSigner:
    def __init__(self, private_key: ed25519.Ed25519PrivateKey):
        self._private_key = private_key
        self.public_key = private_key.public_key()

    def sign_approval(self, payload: dict, nonce: str, timestamp: float) -> bytes:
        doc = {
            "payload": payload,
            "nonce": nonce,
            "timestamp": timestamp
        }
        raw = json.dumps(doc, sort_keys=True).encode("utf-8")
        return self._private_key.sign(raw)
""",
            "src/verifier.py": """import json
from typing import Set
from cryptography.hazmat.primitives.asymmetric import ed25519

class ApprovalVerifier:
    def __init__(self, public_key: ed25519.Ed25519PublicKey, max_drift_seconds: float = 60.0):
        self.public_key = public_key
        self.max_drift_seconds = max_drift_seconds
        self.seen_nonces: Set[str] = set()

    def verify_approval(self, payload: dict, nonce: str, timestamp: float, signature: bytes, current_time: float) -> bool:
        doc = {
            "payload": payload,
            "nonce": nonce,
            "timestamp": timestamp
        }
        raw = json.dumps(doc, sort_keys=True).encode("utf-8")
        try:
            self.public_key.verify(signature, raw)
        except Exception:
            return False

        # BUG: The verifier checks cryptographic validity, but completely ignores
        # timestamp freshness verification and fails to reject or record seen nonces!
        return True
""",
            "test/test_verifier.py": """import unittest
import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from src.signer import OperatorSigner
from src.verifier import ApprovalVerifier

class TestApprovalVerifier(unittest.TestCase):
    def setUp(self):
        self.priv_key = ed25519.Ed25519PrivateKey.generate()
        self.signer = OperatorSigner(self.priv_key)
        self.verifier = ApprovalVerifier(self.signer.public_key, max_drift_seconds=30.0)

    def test_valid_approval_accepted(self):
        now = time.time()
        payload = {"action": "deploy", "target": "prod"}
        sig = self.signer.sign_approval(payload, "nonce-1", now)
        self.assertTrue(self.verifier.verify_approval(payload, "nonce-1", now, sig, now))

    def test_expired_timestamp_rejected(self):
        now = time.time()
        old_time = now - 100.0  # 100 seconds in the past (> 30s max drift)
        payload = {"action": "transfer", "amount": 1000}
        sig = self.signer.sign_approval(payload, "nonce-old", old_time)
        self.assertFalse(
            self.verifier.verify_approval(payload, "nonce-old", old_time, sig, now),
            "FALSIFIER: Expired approval timestamp must be rejected"
        )

    def test_duplicate_nonce_rejected(self):
        now = time.time()
        payload = {"action": "delete_db"}
        sig = self.signer.sign_approval(payload, "nonce-dup", now)
        # First verification must succeed
        self.assertTrue(self.verifier.verify_approval(payload, "nonce-dup", now, sig, now))
        # Replay with same nonce must fail
        self.assertFalse(
            self.verifier.verify_approval(payload, "nonce-dup", now, sig, now + 1.0),
            "FALSIFIER: Replayed nonce must be rejected"
        )

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: Ed25519 Approval Anti-Replay Verification (SEC-02)

The `ApprovalVerifier` MUST satisfy two anti-replay security invariants:
1. **Timestamp Freshness**: `abs(current_time - timestamp) <= max_drift_seconds`. Any request outside this window MUST be rejected.
2. **Nonce Uniqueness**: Every accepted `nonce` MUST be recorded in `self.seen_nonces`. Any repeated `nonce` MUST be rejected immediately.
""",
        }
    },

    # 03: Trait Attenuation Escalation
    "03_trait_attenuation_escalation": {
        "files": {
            "src/traits.py": """from dataclasses import dataclass
from typing import Set, List

@dataclass(frozen=True)
class Capability:
    verb: str
    resource: str
    scopes: frozenset[str]

class TraitAttenuator:
    @staticmethod
    def attenuate(parent_caps: List[Capability], requested_caps: List[Capability]) -> List[Capability]:
        \"\"\"Attenuates requested capabilities against parent capabilities.\"\"\"
        parent_by_key = {(c.verb, c.resource): c for c in parent_caps}
        attenuated = []

        for req in requested_caps:
            key = (req.verb, req.resource)
            if key not in parent_by_key:
                continue
            parent = parent_by_key[key]
            # BUG: Performs set union instead of intersection, allowing child
            # to escalate scopes beyond parent!
            granted_scopes = parent.scopes | req.scopes
            attenuated.append(Capability(verb=req.verb, resource=req.resource, scopes=frozenset(granted_scopes)))

        return attenuated
""",
            "src/agent_node.py": """from typing import List
from .traits import Capability, TraitAttenuator

class AgentNode:
    def __init__(self, name: str, capabilities: List[Capability]):
        self.name = name
        self.capabilities = capabilities

    def spawn_child(self, child_name: str, requested_caps: List[Capability]) -> "AgentNode":
        effective_caps = TraitAttenuator.attenuate(self.capabilities, requested_caps)
        return AgentNode(child_name, effective_caps)
""",
            "test/test_attenuation.py": """import unittest
from src.traits import Capability, TraitAttenuator
from src.agent_node import AgentNode

class TestTraitAttenuation(unittest.TestCase):
    def test_child_cannot_escalate_capabilities(self):
        parent_caps = [
            Capability("fs.read", "/workspace", frozenset(["read:view"]))
        ]
        parent = AgentNode("parent-agent", parent_caps)

        # Child requests write and admin scopes
        requested = [
            Capability("fs.read", "/workspace", frozenset(["read:view", "write:modify", "admin:all"]))
        ]
        child = parent.spawn_child("child-agent", requested)

        self.assertEqual(len(child.capabilities), 1)
        child_cap = child.capabilities[0]
        # Falsifier Assertion: Child MUST ONLY have the intersection (read:view)
        self.assertEqual(
            child_cap.scopes,
            frozenset(["read:view"]),
            f"Escalation detected: child scopes {child_cap.scopes} exceed parent scopes {parent_caps[0].scopes}"
        )

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: Monotonic Capability Attenuation (TCB-03)

In accordance with the Principle of Least Privilege and Invariant I-5:
1. When a child agent is spawned, its effective scopes for any capability MUST be the strict intersection:
   `effective_scopes = parent_cap.scopes & requested_cap.scopes`
2. A child agent MUST NEVER acquire permissions or scopes absent from the parent's capability set.
""",
        }
    },

    # 04: SQLite WAL Checkpoint Lock
    "04_sqlite_wal_checkpoint_lock": {
        "files": {
            "src/event_store.py": """import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List

class SqliteEventStore:
    def __init__(self, db_path: Path | str):
        self.db_path = str(db_path)
        # BUG: Missing timeout parameter and PRAGMA busy_timeout configuration,
        # leading to immediate lock contention failure under concurrent transactions.
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self._conn.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
        \"\"\")
        self._conn.commit()

    def append_event(self, run_id: str, event_type: str, payload: Dict[str, Any]):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO events (run_id, event_type, payload_json) VALUES (?, ?, ?)",
            (run_id, event_type, json.dumps(payload))
        )
        self._conn.commit()

    def checkpoint(self):
        self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        self._conn.commit()

    def close(self):
        self._conn.close()
""",
            "src/db_pool.py": """from pathlib import Path
from .event_store import SqliteEventStore

def get_store(path: Path | str) -> SqliteEventStore:
    return SqliteEventStore(path)
""",
            "test/test_concurrent_store.py": """import unittest
import tempfile
import threading
from pathlib import Path
from src.event_store import SqliteEventStore

class TestConcurrentEventStore(unittest.TestCase):
    def test_concurrent_append_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "events.db"
            store1 = SqliteEventStore(db_path)
            store2 = SqliteEventStore(db_path)

            errors = []

            def worker_write():
                try:
                    for i in range(50):
                        store2.append_event("run-1", "Step", {"i": i})
                except Exception as e:
                    errors.append(e)

            def worker_checkpoint():
                try:
                    for _ in range(10):
                        store1.checkpoint()
                except Exception as e:
                    errors.append(e)

            t1 = threading.Thread(target=worker_write)
            t2 = threading.Thread(target=worker_checkpoint)
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            store1.close()
            store2.close()

            self.assertEqual(len(errors), 0, f"Concurrency failure occurred: {errors}")

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: SQLite WAL Concurrency & Lock Resilience (STO-04)

The `SqliteEventStore` MUST:
1. Enable `timeout=30.0` on connection creation.
2. Execute `PRAGMA busy_timeout = 30000;` during initialization.
3. Handle concurrent writes and checkpoints gracefully without raising `sqlite3.OperationalError: database is locked`.
""",
        }
    },

    # 05: Token Budget Clamping Drift
    "05_token_budget_clamping_drift": {
        "files": {
            "src/budget.py": """from typing import Optional

class BudgetGovernor:
    def __init__(self, initial_usd: float = 10.0):
        # BUG: Storing and computing balance in native float causes arithmetic
        # precision drift over repeated micro-transactions (e.g. 0.0001 reserve/refund).
        self.initial_usd = initial_usd
        self.available_usd = initial_usd

    def reserve(self, amount_usd: float) -> bool:
        if amount_usd > self.available_usd:
            return False
        self.available_usd -= amount_usd
        return True

    def refund(self, amount_usd: float) -> None:
        self.available_usd += amount_usd

    def commit(self, amount_usd: float) -> None:
        pass

    def remaining_balance(self) -> float:
        return self.available_usd
""",
            "src/pricing.py": """def calculate_cost_usd(tokens: int, rate_per_million: float) -> float:
    return (tokens / 1_000_000.0) * rate_per_million
""",
            "test/test_budget_falsifier.py": """import unittest
from src.budget import BudgetGovernor

class TestBudgetGovernorDrift(unittest.TestCase):
    def test_repeated_micro_transactions_zero_drift(self):
        gov = BudgetGovernor(initial_usd=1.0)
        micro_amount = 0.00001  # 10 micro-USD

        for _ in range(1000):
            self.assertTrue(gov.reserve(micro_amount))
            gov.refund(micro_amount)

        # Falsifier Assertion: After 1000 equal reserves and refunds, balance must be EXACTLY initial
        self.assertEqual(
            gov.remaining_balance(),
            1.0,
            f"Float drift detected: expected 1.0, got {gov.remaining_balance()}"
        )

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: TCB Monetary Budget Exact Conservation (TCB-05)

Monetary budgets in the TCB must be calculated using integer micro-units (`usd_micros` where 1 USD = 1,000,000 micros) or exact `Decimal` representation:
1. Float arithmetic drift MUST NOT occur during reserve and refund operations.
2. `remaining_balance()` must return exact results without precision loss.
""",
        }
    },

    # 06: FTS5 Stale Index Rebuild
    "06_fts5_stale_index_rebuild": {
        "files": {
            "src/symbol_indexer.py": """import sqlite3
from typing import List, Dict, Any

class SymbolIndexer:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL
            );
        \"\"\")
        self.conn.execute(\"\"\"
            CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5 (
                file_path,
                symbol_name,
                docstring
            );
        \"\"\")
        self.conn.commit()

    def index_file(self, path: str, symbols: List[Dict[str, str]]):
        self.conn.execute("INSERT OR REPLACE INTO files (path) VALUES (?)", (path,))
        for s in symbols:
            self.conn.execute(
                "INSERT INTO symbols_fts (file_path, symbol_name, docstring) VALUES (?, ?, ?)",
                (path, s["name"], s.get("docstring", ""))
            )
        self.conn.commit()

    def delete_file(self, path: str):
        # BUG: Deletes file from files table, but forgets to purge
        # matching records from symbols_fts table!
        self.conn.execute("DELETE FROM files WHERE path = ?", (path,))
        self.conn.commit()

    def search(self, query: str) -> List[Dict[str, str]]:
        cur = self.conn.execute(
            "SELECT file_path, symbol_name, docstring FROM symbols_fts WHERE symbols_fts MATCH ?",
            (query,)
        )
        return [{"file_path": r[0], "symbol_name": r[1], "docstring": r[2]} for r in cur.fetchall()]
""",
            "test/test_indexer_falsifier.py": """import unittest
from src.symbol_indexer import SymbolIndexer

class TestSymbolIndexer(unittest.TestCase):
    def test_delete_file_purges_fts_symbols(self):
        indexer = SymbolIndexer()
        indexer.index_file("kernel/dispatch.py", [
            {"name": "DispatchPipeline", "docstring": "Core 13-stage dispatch pipeline"}
        ])

        # Verify symbol found
        res = indexer.search("DispatchPipeline")
        self.assertEqual(len(res), 1)

        # Delete file
        indexer.delete_file("kernel/dispatch.py")

        # Falsifier Assertion: Search for deleted symbol must yield 0 results
        res_after = indexer.search("DispatchPipeline")
        self.assertEqual(
            len(res_after),
            0,
            f"FTS Zombie Hit: Deleted file symbols still present in search results: {res_after}"
        )

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: AST Symbol Index Deletion Invariant (IDX-06)

When `delete_file(path)` is executed on `SymbolIndexer`:
1. The record in `files` MUST be removed.
2. All entries in `symbols_fts` associated with `path` MUST be purged completely (`DELETE FROM symbols_fts WHERE file_path = ?`).
3. Subsequent FTS search queries MUST NOT return symbols from the deleted file.
""",
        }
    },

    # 07: Context Lost in Middle Prune
    "07_context_lost_in_middle_prune": {
        "files": {
            "src/context_allocator.py": """from typing import List, Dict

class ContextAllocator:
    @staticmethod
    def prune_section(header: str, docstring: str, body_lines: List[str], max_lines: int) -> str:
        \"\"\"Prunes content using lost-in-the-middle strategy, preserving header and docstring.\"\"\"
        if len(body_lines) <= max_lines:
            return f"{header}\\n{docstring}\\n" + "\\n".join(body_lines)

        # BUG: Slices from start and drops the header/docstring when truncating!
        pruned_body = body_lines[:max_lines // 2] + ["# ... [pruned] ..."] + body_lines[-(max_lines // 2):]
        # Buggy implementation drops header and docstring from returned output:
        return "\\n".join(pruned_body)
""",
            "test/test_context_allocator.py": """import unittest
from src.context_allocator import ContextAllocator

class TestContextAllocator(unittest.TestCase):
    def test_preserves_module_docstring_and_top_signatures(self):
        header = "class KernelDispatch:"
        docstring = '    \"\"\"Trusted Computing Base 13-stage pipeline.\"\"\"'
        body = [f"    def step_{i}(self): pass" for i in range(50)]

        pruned = ContextAllocator.prune_section(header, docstring, body, max_lines=10)

        # Falsifier Assertion: header and docstring MUST be preserved at top of pruned output
        self.assertIn("class KernelDispatch:", pruned)
        self.assertIn('\"\"\"Trusted Computing Base 13-stage pipeline.\"\"\"', pruned)
        self.assertIn("# ... [pruned] ...", pruned)

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: Lost-in-the-Middle Context Pruning (CTX-07)

When `ContextAllocator.prune_section(header, docstring, body_lines, max_lines)` is called:
1. `header` and `docstring` MUST always be anchored at the beginning of the returned string.
2. The middle of `body_lines` is compressed with `# ... [pruned] ...`.
3. The top and bottom slices of `body_lines` are preserved up to `max_lines`.
""",
        }
    },

    # 08: Evaluator Oracle Timeout
    "08_evaluator_oracle_timeout": {
        "files": {
            "src/sandbox_runner.py": """import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ExecutionResult:
    status: str  # "OK" | "TIMEOUT" | "ERROR"
    return_code: int
    stdout: str
    stderr: str

class SandboxRunner:
    @staticmethod
    def run_command(cmd: List[str], timeout_seconds: float = 2.0) -> ExecutionResult:
        try:
            # BUG: Does not set start_new_session=True and swallows TimeoutExpired without
            # reporting status='TIMEOUT'
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            return ExecutionResult(status="OK" if proc.returncode == 0 else "ERROR", return_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        except subprocess.TimeoutExpired as exc:
            # BUG: Returns status="ERROR" with return_code=0 instead of status="TIMEOUT" and return_code=-1
            return ExecutionResult(status="ERROR", return_code=0, stdout="", stderr="timed out")
""",
            "test/test_sandbox_timeout.py": """import unittest
import sys
from src.sandbox_runner import SandboxRunner

class TestSandboxTimeout(unittest.TestCase):
    def test_timeout_reports_proper_status_and_code(self):
        # Run a command that sleeps for 5 seconds with 0.5s timeout
        cmd = [sys.executable, "-c", "import time; time.sleep(5.0)"]
        result = SandboxRunner.run_command(cmd, timeout_seconds=0.5)

        # Falsifier Assertion: status MUST be TIMEOUT and return_code MUST be -1
        self.assertEqual(
            result.status,
            "TIMEOUT",
            f"Falsifier failed: Expected status TIMEOUT, got {result.status}"
        )
        self.assertEqual(
            result.return_code,
            -1,
            f"Falsifier failed: Expected return_code -1, got {result.return_code}"
        )

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: Sandbox Evaluator Timeout Termination (EVL-08)

The `SandboxRunner` must:
1. Enforce process execution timeout strictly.
2. When a timeout occurs, return `ExecutionResult(status="TIMEOUT", return_code=-1, stdout=..., stderr=...)`.
""",
        }
    },

    # 09: Model Port Streaming Chunk Drop
    "09_model_port_streaming_chunk_drop": {
        "files": {
            "src/sse_decoder.py": """import json
from typing import List, Dict, Any

class SSEDecoder:
    def __init__(self):
        self._buffer = ""

    def feed(self, chunk: bytes) -> List[Dict[str, Any]]:
        self._buffer += chunk.decode("utf-8")
        lines = self._buffer.split("\\n")
        self._buffer = lines[-1]  # Keep incomplete line in buffer

        events = []
        for line in lines[:-1]:
            line = line.strip()
            if line.startswith("data: "):
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    events.append({"done": True})
                else:
                    try:
                        events.append(json.loads(data_str))
                    except Exception:
                        pass
        return events

    def close(self) -> List[Dict[str, Any]]:
        # BUG: When close() is called at EOF, the remaining buffer in self._buffer
        # is discarded without being parsed, dropping the final event chunk!
        self._buffer = ""
        return []
""",
            "test/test_streaming_falsifier.py": """import unittest
from src.sse_decoder import SSEDecoder

class TestSSEDecoder(unittest.TestCase):
    def test_flushes_final_chunk_on_close(self):
        decoder = SSEDecoder()
        chunk1 = b'data: {"choices": [{"delta": {"content": "Hello"}}]}'
        # chunk2 does not have a trailing newline
        chunk2 = b'\\ndata: {"choices": [{"delta": {"content": " World"}}]}'

        ev1 = decoder.feed(chunk1)
        ev2 = decoder.feed(chunk2)
        ev_final = decoder.close()

        all_events = ev1 + ev2 + ev_final
        # Falsifier Assertion: Both events must be decoded without dropping the trailing chunk
        self.assertEqual(
            len(all_events),
            2,
            f"Chunk dropped: expected 2 events, got {len(all_events)} ({all_events})"
        )
        self.assertEqual(all_events[1]["choices"][0]["delta"]["content"], " World")

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: SSE Stream Event Decoding and Flush (MOD-09)

The `SSEDecoder` MUST:
1. Decode incoming SSE chunks into JSON data events.
2. When `close()` is called at stream termination, process any pending `data: ` line in `self._buffer` and yield the final event before resetting.
""",
        }
    },

    # 10: Graph PPR Dangling Node Sink
    "10_graph_ppr_dangling_node_sink": {
        "files": {
            "src/ppr.py": """from typing import Dict, List, Set

class PersonalizedPageRank:
    @staticmethod
    def compute(adjacency: Dict[str, List[str]], seed_node: str, alpha: float = 0.85, max_iter: int = 50) -> Dict[str, float]:
        nodes = list(adjacency.keys())
        n = len(nodes)
        if n == 0:
            return {}

        p = {node: 1.0 / n for node in nodes}
        teleport = {node: (1.0 if node == seed_node else 0.0) for node in nodes}

        for _ in range(max_iter):
            next_p = {node: (1.0 - alpha) * teleport[node] for node in nodes}
            for u, neighbors in adjacency.items():
                if neighbors:
                    out_weight = alpha * (p[u] / len(neighbors))
                    for v in neighbors:
                        if v in next_p:
                            next_p[v] += out_weight
                # BUG: Dangling nodes (neighbors == []) absorb probability mass!
                # Their mass alpha * p[u] is not redistributed to the teleport distribution.
            p = next_p

        return p
""",
            "test/test_ppr_falsifier.py": """import unittest
from src.ppr import PersonalizedPageRank

class TestPPR(unittest.TestCase):
    def test_ppr_conserves_probability_with_dangling_nodes(self):
        # Node 'C' has no outgoing edges (dangling sink)
        adj = {
            "A": ["B", "C"],
            "B": ["A"],
            "C": []
        }
        scores = PersonalizedPageRank.compute(adj, seed_node="A", alpha=0.85, max_iter=30)
        total_mass = sum(scores.values())

        # Falsifier Assertion: Total probability mass MUST sum to 1.0 (+- 0.001)
        self.assertAlmostEqual(
            total_mass,
            1.0,
            places=3,
            msg=f"Probability mass lost: sum is {total_mass}, expected 1.0"
        )

if __name__ == "__main__":
    unittest.main()
""",
            "docs/SPEC.md": """# Specification: Personalized PageRank Probability Conservation (GRA-10)

The `PersonalizedPageRank` computation MUST:
1. Conserve total probability mass: \\sum_{v} p(v) = 1.0 \\pm 10^{-4}.
2. When encountering dangling nodes (nodes with out-degree 0), redistribute their retained mass \\alpha \\cdot p(u) to the teleport distribution.
""",
        }
    }
}


# ==============================================================================
# 10 GREENFIELD CHALLENGES DEFINITIONS
# ==============================================================================

GREENFIELD_CHALLENGES = {
    # 11: KV LRU TTL Store
    "11_kv_lru_ttl_store": {
        "readme": """# Greenfield PRD: Thread-Safe In-Memory KV Store with LRU and TTL

## Objective
Implement `LRUTTLStore` in `src/store.py`.

## Requirements
- `LRUTTLStore(capacity: int, default_ttl: float | None = None)`
- `put(key: str, value: Any, ttl: float | None = None) -> None`: Inserts or updates a key. If size exceeds `capacity`, evicts the least recently used item.
- `get(key: str) -> Any | None`: Retrieves value. Returns `None` if key does not exist or has expired. Updates LRU order on hit.
- `delete(key: str) -> bool`: Deletes a key, returning `True` if found.
- `size() -> int`: Returns current count of unexpired keys.
- `clear() -> None`: Clears all entries.
- Thread-safe using `threading.RLock`.
- Monotonic time calculation using `time.monotonic()`.
""",
        "test": """import unittest
import time
from src.store import LRUTTLStore

class TestLRUTTLStore(unittest.TestCase):
    def test_lru_eviction(self):
        store = LRUTTLStore(capacity=2)
        store.put("a", 1)
        store.put("b", 2)
        self.assertEqual(store.get("a"), 1)
        store.put("c", 3)  # Evicts "b"
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("a"), 1)
        self.assertEqual(store.get("c"), 3)

    def test_ttl_expiration(self):
        store = LRUTTLStore(capacity=5, default_ttl=0.1)
        store.put("temp", "val")
        self.assertEqual(store.get("temp"), "val")
        time.sleep(0.15)
        self.assertIsNone(store.get("temp"))

    def test_delete_and_size(self):
        store = LRUTTLStore(capacity=3)
        store.put("x", 10)
        store.put("y", 20)
        self.assertEqual(store.size(), 2)
        self.assertTrue(store.delete("x"))
        self.assertFalse(store.delete("nonexistent"))
        self.assertEqual(store.size(), 1)

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 12: Finite State Machine Workflow
    "12_finite_state_machine_workflow": {
        "readme": """# Greenfield PRD: Deterministic Finite State Machine (FSM)

## Objective
Implement `StateMachine` and `InvalidTransitionError` in `src/fsm.py`.

## Requirements
- `StateMachine(initial_state: str)`
- `add_transition(source: str, event: str, target: str, guard: Callable[..., bool] | None = None)`
- `trigger(event: str, **kwargs) -> str`: Transitions state. Raises `InvalidTransitionError` if no transition matches or guard returns `False`. Returns new state.
- `current_state: str` property.
- `history: list[dict]` property: Returns history of transitions `[{"from": ..., "event": ..., "to": ...}]`.
""",
        "test": """import unittest
from src.fsm import StateMachine, InvalidTransitionError

class TestStateMachine(unittest.TestCase):
    def test_valid_transitions(self):
        fsm = StateMachine(initial_state="draft")
        fsm.add_transition("draft", "submit", "in_review")
        fsm.add_transition("in_review", "approve", "published")

        self.assertEqual(fsm.trigger("submit"), "in_review")
        self.assertEqual(fsm.trigger("approve"), "published")
        self.assertEqual(fsm.current_state, "published")
        self.assertEqual(len(fsm.history), 2)

    def test_guard_condition(self):
        fsm = StateMachine(initial_state="draft")
        fsm.add_transition("draft", "submit", "in_review", guard=lambda user: user == "admin")

        with self.assertRaises(InvalidTransitionError):
            fsm.trigger("submit", user="guest")

        self.assertEqual(fsm.trigger("submit", user="admin"), "in_review")

    def test_invalid_event_raises(self):
        fsm = StateMachine(initial_state="draft")
        with self.assertRaises(InvalidTransitionError):
            fsm.trigger("unknown_event")

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 13: Semver Dependency Resolver
    "13_semver_dependency_resolver": {
        "readme": """# Greenfield PRD: SemVer Dependency Resolver

## Objective
Implement `SemverResolver` and `ConflictError` in `src/resolver.py`.

## Requirements
- `SemverResolver()`
- `add_package(name: str, version: str, dependencies: dict[str, str] | None = None) -> None`: Registers package version with constraints (e.g. `{"depA": "^1.0.0"}`).
- `resolve(root_name: str, root_constraint: str) -> dict[str, str]`: Resolves package dependency tree, returning a dictionary `{pkg_name: selected_version}`.
- Constraints support exact (`1.0.0`), caret (`^1.2.0` matches `>=1.2.0, <2.0.0`), and range (`>=1.0.0, <2.0.0`).
- Raises `ConflictError` when no valid version combination satisfies all requirements.
""",
        "test": """import unittest
from src.resolver import SemverResolver, ConflictError

class TestSemverResolver(unittest.TestCase):
    def test_diamond_dependency_resolution(self):
        resolver = SemverResolver()
        resolver.add_package("app", "1.0.0", {"libA": "^1.0.0", "libB": "^1.0.0"})
        resolver.add_package("libA", "1.0.0", {"shared": "^1.0.0"})
        resolver.add_package("libB", "1.0.0", {"shared": "^1.2.0"})
        resolver.add_package("shared", "1.0.0", {})
        resolver.add_package("shared", "1.2.0", {})
        resolver.add_package("shared", "1.3.0", {})

        plan = resolver.resolve("app", "1.0.0")
        self.assertEqual(plan["app"], "1.0.0")
        self.assertEqual(plan["shared"], "1.3.0")

    def test_conflict_error_raised(self):
        resolver = SemverResolver()
        resolver.add_package("app", "1.0.0", {"libA": "^1.0.0", "libB": "^1.0.0"})
        resolver.add_package("libA", "1.0.0", {"shared": "^1.0.0"})
        resolver.add_package("libB", "1.0.0", {"shared": "^2.0.0"})
        resolver.add_package("shared", "1.0.0", {})
        resolver.add_package("shared", "2.0.0", {})

        with self.assertRaises(ConflictError):
            resolver.resolve("app", "1.0.0")

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 14: Merkle Tree Ledger
    "14_merkle_tree_ledger": {
        "readme": """# Greenfield PRD: Cryptographic Merkle Tree Ledger

## Objective
Implement `MerkleTree` in `src/merkle.py`.

## Requirements
- `MerkleTree()`
- `append(data: bytes) -> int`: Appends a leaf and returns leaf index.
- `get_root_hash() -> str`: Computes SHA-256 root hash of the tree. If empty, returns empty string.
- `get_proof(leaf_index: int) -> list[dict]`: Generates audit inclusion proof `[{"position": "left"|"right", "hash": str}]`.
- `verify_proof(leaf_data: bytes, leaf_index: int, proof: list[dict], root_hash: str) -> bool`: Static/class method verifying inclusion against root.
""",
        "test": """import unittest
from src.merkle import MerkleTree

class TestMerkleTree(unittest.TestCase):
    def test_inclusion_proof_and_verification(self):
        tree = MerkleTree()
        idx0 = tree.append(b"event-0-init")
        idx1 = tree.append(b"event-1-action")
        idx2 = tree.append(b"event-2-commit")
        idx3 = tree.append(b"event-3-close")

        root = tree.get_root_hash()
        self.assertEqual(len(root), 64)

        proof = tree.get_proof(idx1)
        self.assertTrue(MerkleTree.verify_proof(b"event-1-action", idx1, proof, root))

        # Tampering with leaf data must fail
        self.assertFalse(MerkleTree.verify_proof(b"event-1-tampered", idx1, proof, root))

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 15: Circuit Breaker Proxy
    "15_circuit_breaker_proxy": {
        "readme": """# Greenfield PRD: Resilient Circuit Breaker Middleware

## Objective
Implement `CircuitBreaker`, `CircuitState`, and `CircuitBreakerOpenException` in `src/circuit_breaker.py`.

## Requirements
- `CircuitState` enum: `CLOSED`, `OPEN`, `HALF_OPEN`.
- `CircuitBreaker(failure_threshold: int = 3, recovery_timeout: float = 0.5, half_open_success_threshold: int = 2)`
- `call(func: Callable, *args, **kwargs) -> Any`: Executes `func`.
  - When `CLOSED`: Failure increments count. Reaching `failure_threshold` trips state to `OPEN`.
  - When `OPEN`: Raises `CircuitBreakerOpenException` immediately without calling `func`. If `recovery_timeout` has elapsed, transitions to `HALF_OPEN`.
  - When `HALF_OPEN`: Allows trial calls. If `half_open_success_threshold` consecutive calls succeed, transitions to `CLOSED`. Any failure reverts to `OPEN`.
- `state` property returning current `CircuitState`.
""",
        "test": """import unittest
import time
from src.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenException

class TestCircuitBreaker(unittest.TestCase):
    def test_circuit_trips_and_recovers(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, half_open_success_threshold=1)
        
        def failing_call():
            raise ValueError("service error")

        # 2 failures trip to OPEN
        for _ in range(2):
            with self.assertRaises(ValueError):
                cb.call(failing_call)

        self.assertEqual(cb.state, CircuitState.OPEN)

        # Fast failure while OPEN
        with self.assertRaises(CircuitBreakerOpenException):
            cb.call(lambda: "success")

        time.sleep(0.15)
        # Recovers to HALF_OPEN -> CLOSED on successful trial
        res = cb.call(lambda: "success")
        self.assertEqual(res, "success")
        self.assertEqual(cb.state, CircuitState.CLOSED)

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 16: Submodular Greedy Packer
    "16_submodular_greedy_packer": {
        "readme": """# Greenfield PRD: Submodular Greedy Knapsack Packer

## Objective
Implement `SubmodularPacker` and `PackItem` in `src/packer.py`.

## Requirements
- `PackItem(id: str, cost: int, features: set[str])`
- `SubmodularPacker.pack(items: list[PackItem], budget: int) -> list[PackItem]`
- The utility function is the total count of unique features covered: $f(S) = |\\bigcup_{i \\in S} i.features|$.
- Algorithm: Greedy marginal gain $\\Delta(e \\mid S) = f(S \\cup \\{e\\}) - f(S)$. At each step, select item maximizing $\\Delta(e \\mid S) / cost(e)$ that fits in the remaining budget.
- Total cost of returned items MUST not exceed `budget`.
""",
        "test": """import unittest
from src.packer import SubmodularPacker, PackItem

class TestSubmodularPacker(unittest.TestCase):
    def test_greedy_coverage_under_budget(self):
        items = [
            PackItem("item1", cost=10, features={"python", "ast", "indexer"}),
            PackItem("item2", cost=10, features={"python", "ast"}),  # redundant
            PackItem("item3", cost=10, features={"sqlite", "fts5"}),
            PackItem("item4", cost=30, features={"python", "ast", "sqlite", "fts5", "kernel"})
        ]

        # Budget 20: Should pick item1 and item3 (5 unique features for cost 20)
        selected = SubmodularPacker.pack(items, budget=20)
        ids = {i.id for i in selected}
        total_cost = sum(i.cost for i in selected)

        self.assertLessEqual(total_cost, 20)
        self.assertIn("item1", ids)
        self.assertIn("item3", ids)
        self.assertNotIn("item2", ids)

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 17: JSON Canonicalizer (JCS RFC-8785)
    "17_json_canonicalizer_jcs": {
        "readme": """# Greenfield PRD: Deterministic RFC-8785 JSON Canonicalizer (JCS)

## Objective
Implement `canonicalize(data: Any) -> bytes` and `canonical_digest(data: Any) -> str` in `src/jcs.py`.

## Requirements
- Sort dictionary keys deterministically by UTF-16 code units (Unicode code point order).
- Serialize without extraneous whitespace (e.g. `{"a":1,"b":2}`).
- Floats without fractional parts formatted with standard representation (e.g. `1.0` -> `1.0` or integer rules).
- Return exact deterministic UTF-8 encoded bytes.
- `canonical_digest` returns SHA-256 hexadecimal string of canonical bytes.
""",
        "test": """import unittest
from src.jcs import canonicalize, canonical_digest

class TestJCS(unittest.TestCase):
    def test_canonical_ordering_and_digest(self):
        obj = {"z": 100, "a": [3, 2, 1], "m": {"b": True, "a": None}}
        canon_bytes = canonicalize(obj)
        expected = b'{"a":[3,2,1],"m":{"a":null,"b":true},"z":100}'
        self.assertEqual(canon_bytes, expected)

        digest = canonical_digest(obj)
        self.assertEqual(len(digest), 64)

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 18: Hierarchical Token Bucket
    "18_token_bucket_hierarchical": {
        "readme": """# Greenfield PRD: Hierarchical Token Bucket Rate Limiter

## Objective
Implement `HierarchicalTokenBucket` in `src/token_bucket.py`.

## Requirements
- `HierarchicalTokenBucket(capacity: float, refill_rate: float, parent: Optional[HierarchicalTokenBucket] = None)`
- `acquire(tokens: float) -> bool`: Consumes tokens from this bucket AND all ancestor parent buckets. If any bucket in the hierarchy lacks sufficient tokens, no tokens are consumed from any bucket (atomic) and returns `False`.
- Refills tokens continuously based on `refill_rate` (tokens per second) up to `capacity`.
- Thread-safe.
""",
        "test": """import unittest
import time
from src.token_bucket import HierarchicalTokenBucket

class TestHierarchicalTokenBucket(unittest.TestCase):
    def test_parent_child_atomicity(self):
        parent = HierarchicalTokenBucket(capacity=10.0, refill_rate=5.0)
        child1 = HierarchicalTokenBucket(capacity=10.0, refill_rate=5.0, parent=parent)
        child2 = HierarchicalTokenBucket(capacity=10.0, refill_rate=5.0, parent=parent)

        # Child1 acquires 8 tokens (parent now has 2)
        self.assertTrue(child1.acquire(8.0))

        # Child2 wants 5 tokens. Child2 has 10, but parent only has 2 -> must fail
        self.assertFalse(child2.acquire(5.0))

        # Wait for refill (0.8s * 5 tokens/s = 4 tokens)
        time.sleep(0.8)
        self.assertTrue(child2.acquire(5.0))

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 19: Markdown Section Splitter
    "19_markdown_section_splitter": {
        "readme": """# Greenfield PRD: Structured Markdown Section Chunker

## Objective
Implement `MarkdownSectionSplitter` and `MarkdownChunk` in `src/splitter.py`.

## Requirements
- `MarkdownChunk(title: str, level: int, breadcrumbs: list[str], content: str, token_estimate: int)`
- `MarkdownSectionSplitter.split(markdown_text: str, max_tokens: int = 500) -> list[MarkdownChunk]`
- Splits along headers (`#`, `##`, `###`), tracking `breadcrumbs` (e.g. `["Architecture", "Kernel", "Dispatch"]`).
- Ignores `#` characters inside fenced code blocks (` ```...``` `).
- Preserves headers and section bodies.
""",
        "test": """import unittest
from src.splitter import MarkdownSectionSplitter

class TestMarkdownSplitter(unittest.TestCase):
    def test_header_hierarchy_and_code_blocks(self):
        doc = \"\"\"# Architecture
System overview.

## Kernel
TCB details.

```python
# This is a comment inside code, not a header!
x = 10
```

### Dispatch
13-stage dispatch pipeline.
\"\"\"
        chunks = MarkdownSectionSplitter.split(doc)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].title, "Architecture")
        self.assertEqual(chunks[1].title, "Kernel")
        self.assertEqual(chunks[1].breadcrumbs, ["Architecture", "Kernel"])
        self.assertIn("# This is a comment inside code", chunks[1].content)
        self.assertEqual(chunks[2].title, "Dispatch")
        self.assertEqual(chunks[2].breadcrumbs, ["Architecture", "Kernel", "Dispatch"])

if __name__ == "__main__":
    unittest.main()
""",
    },

    # 20: Event Bus PubSub Channel
    "20_event_bus_pubsub_channel": {
        "readme": """# Greenfield PRD: In-Memory Event Bus with Wildcard Routing and DLQ

## Objective
Implement `EventBus` and `DeadLetterItem` in `src/event_bus.py`.

## Requirements
- `EventBus()`
- `subscribe(pattern: str, handler: Callable[[str, Any], None]) -> str`: Returns subscription ID.
  - Supports exact matching (`"order.created"`).
  - Supports single-word wildcard `*` (`"order.*"` matches `"order.created"`, `"order.cancelled"`).
  - Supports multi-word wildcard `#` (`"order.#"` matches `"order.us.created"`).
- `unsubscribe(sub_id: str) -> bool`
- `publish(topic: str, data: Any) -> int`: Dispatches to all matching handlers. If a handler raises an exception, the error and event are captured into Dead-Letter Queue (DLQ) without breaking other handlers. Returns count of successful dispatches.
- `get_dlq() -> list[DeadLetterItem]`
""",
        "test": """import unittest
from src.event_bus import EventBus, DeadLetterItem

class TestEventBus(unittest.TestCase):
    def test_wildcard_dispatch_and_dlq(self):
        bus = EventBus()
        received = []

        bus.subscribe("telemetry.*", lambda topic, data: received.append((topic, data)))

        def failing_handler(topic, data):
            raise RuntimeError("handler failed")

        bus.subscribe("telemetry.errors", failing_handler)

        success_count = bus.publish("telemetry.cpu", {"usage": 80})
        self.assertEqual(success_count, 1)
        self.assertEqual(len(received), 1)

        # Publish to error topic (1 succeeds, 1 fails into DLQ)
        bus.publish("telemetry.errors", {"error": "OOM"})
        dlq = bus.get_dlq()
        self.assertEqual(len(dlq), 1)
        self.assertEqual(dlq[0].topic, "telemetry.errors")

if __name__ == "__main__":
    unittest.main()
""",
    }
}


def build_suite():
    SUITE_ROOT.mkdir(parents=True, exist_ok=True)

    # 1. Build Brownfield Challenges
    for cname, cdata in BROWNFIELD_CHALLENGES.items():
        cdir = SUITE_ROOT / cname
        cdir.mkdir(parents=True, exist_ok=True)

        sha_manifest = []
        for rel_path, content in sorted(cdata["files"].items()):
            fpath = cdir / rel_path
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")
            sha_manifest.append(f"{sha256_file(fpath)}  {rel_path}")

        (cdir / "initial_state.sha256").write_text("\n".join(sha_manifest) + "\n", encoding="utf-8")
        print(f"Created Brownfield challenge: {cname} ({len(cdata['files'])} files)")

    # 2. Build Greenfield Challenges
    for cname, cdata in GREENFIELD_CHALLENGES.items():
        cdir = SUITE_ROOT / cname
        cdir.mkdir(parents=True, exist_ok=True)

        (cdir / "README.md").write_text(cdata["readme"], encoding="utf-8")
        test_dir = cdir / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "test_suite.py").write_text(cdata["test"], encoding="utf-8")

        # Greenfield challenges don't have src/ initially, or empty src/
        src_dir = cdir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("", encoding="utf-8")

        print(f"Created Greenfield challenge: {cname}")

    print(f"\nSuccessfully built all 20 benchmark challenges in {SUITE_ROOT}")


if __name__ == "__main__":
    build_suite()

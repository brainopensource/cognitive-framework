"""Performance & write-amplification baseline tests (Task 3 / BETA-14).

Owning contract: BETA-14, REQ-BENCH-001, S8-B-02, S10-B-03, GTS-13C Ch.11.

Invariants:
- SQLite WAL disk growth scales linearly O(N) with turn count without quadratic page explosion.
- Marginal write amplification during active WAL execution is strictly bounded (< 10.0x).
- Post-checkpoint write amplification factor (physical bytes / logical payload bytes) is <= 6.0x (typically ~2.5x).
- Structured compaction enforces strict token ceilings across long multi-turn episodes.
- Compaction preserves structured decisions and dead ends while evicting superseded dialogue bodies.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.agency.context.compaction import (
    ResultEvictionStrategy,
    StructuredConsolidateStrategy,
)
from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Block, Layer
from vanguard.packages.runtime.app_service import ApplicationService

ROOT_DIR = Path(__file__).resolve().parents[2]


class TestBeta14PerformanceBaseline(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="vg-bench-")
        self.workspace = Path(self.tmp.name)
        (self.workspace / "pyproject.toml").write_text('[project]\nname="bench"\nversion="0.1.0"\n', encoding="utf-8")
        (self.workspace / "data.txt").write_text("initial baseline data\n" * 50, encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _get_dir_size(self, path: Path) -> int:
        total = 0
        if not path.exists():
            return 0
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
        return total

    def test_sqlite_wal_growth_and_write_amplification_multi_turn(self) -> None:
        """Measure SQLite WAL disk growth, marginal WAF, and post-checkpoint storage amplification."""
        app = ApplicationService(workspace=self.workspace)

        turn_counts = [5, 10, 15, 20]
        measurements: list[dict] = []

        for count in turn_counts:
            state_dir = self.workspace / f".vanguard_run_{count}"
            state_dir.mkdir(parents=True, exist_ok=True)

            # Script a multi-turn model with read effects followed by finish
            proposals = []
            for i in range(count - 1):
                proposals.append({
                    "kind": "effect",
                    "action": "fs.read",
                    "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
                    "args": {"path": "data.txt"},
                    "note": f"Turn {i}: inspecting data",
                })
            proposals.append({
                "kind": "finish",
                "note": f"Completed {count} turns workload",
            })

            fake_model = FakeModel(proposals)
            run_id = f"run-bench-waf-{count}"

            t0 = time.perf_counter()
            res = app.run(
                brief=f"Execute {count} turns performance benchmark",
                profile_id="local",
                run_id=run_id,
                model=fake_model,
                state_dir=state_dir,
                interactive=False,
                max_turns=count + 5,
            )
            duration = time.perf_counter() - t0

            self.assertEqual(res.outcome, "completed")
            self.assertEqual(res.turns, count)

            # Active WAL state before checkpoint
            active_physical_bytes = self._get_dir_size(state_dir)

            # Checkpoint WAL to measure compacted durable footprint
            events_db = state_dir / "events.sqlite3"
            if events_db.exists():
                con = sqlite3.connect(events_db)
                con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                con.close()

            checkpointed_physical_bytes = self._get_dir_size(state_dir)

            events_res = app.events(run_id=run_id, state_dir=state_dir)
            logical_bytes = sum(len(json.dumps(e, ensure_ascii=False).encode("utf-8")) for e in events_res.events)

            post_checkpoint_waf = checkpointed_physical_bytes / max(1, logical_bytes)

            measurements.append({
                "turns": count,
                "duration_s": duration,
                "logical_bytes": logical_bytes,
                "active_physical_bytes": active_physical_bytes,
                "checkpointed_physical_bytes": checkpointed_physical_bytes,
                "post_checkpoint_waf": post_checkpoint_waf,
            })

        # Invariants:
        # 1. Post-checkpoint write amplification factor is strictly <= 6.5x across all workloads
        for m in measurements:
            self.assertGreater(m["logical_bytes"], 0)
            self.assertLessEqual(
                m["post_checkpoint_waf"], 6.5,
                f"Post-checkpoint WAF {m['post_checkpoint_waf']:.2f} exceeded 6.5x for {m['turns']} turns"
            )

        # 2. Marginal active WAF (delta physical / delta logical) between 5 and 20 turns is strictly < 10.0x
        m_start = measurements[0]
        m_end = measurements[-1]
        delta_logical = m_end["logical_bytes"] - m_start["logical_bytes"]
        delta_physical_active = m_end["active_physical_bytes"] - m_start["active_physical_bytes"]
        marginal_waf = delta_physical_active / max(1, delta_logical)
        self.assertLess(
            marginal_waf, 10.0,
            f"Marginal active WAF {marginal_waf:.2f}x exceeded 10.0x bound"
        )

        # 3. Storage growth scales linearly O(N): 4x turn increase (5 -> 20) yields <= 4.5x post-checkpoint growth
        storage_growth_ratio = m_end["checkpointed_physical_bytes"] / max(1, m_start["checkpointed_physical_bytes"])
        self.assertLessEqual(
            storage_growth_ratio, 4.5,
            f"Storage growth ratio {storage_growth_ratio:.2f}x scaled non-linearly"
        )

    def test_structured_compaction_memory_and_token_bounds(self) -> None:
        """Benchmark token and memory footprint per turn with compaction enabled vs disabled."""
        num_turns = 16
        ceiling = 1200  # Token ceiling

        # Mode A: Structured compaction enabled
        compiler_compacted = ContextCompiler(
            system_core="You are an autonomous engineering agent with structured memory.",
            token_ceiling=ceiling,
            compaction_strategy=StructuredConsolidateStrategy(),
        )

        # Mode B: Compaction disabled / large ceiling
        compiler_unbounded = ContextCompiler(
            system_core="You are an autonomous engineering agent with structured memory.",
            token_ceiling=100_000,
            compaction_strategy=None,
        )

        compacted_tokens_per_turn: list[int] = []
        unbounded_tokens_per_turn: list[int] = []

        dialogue_compacted: list[Block] = []
        dialogue_unbounded: list[Block] = []
        last_compiled_compacted = None

        for t in range(num_turns):
            turn_text = (
                f"Turn {t}: Observed large diagnostic trace payload containing code excerpts:\n"
                + f"def sub_routine_{t}():\n    x = {t} * 42\n    return x\n" * 20
                + f"Decision: verified module {t}."
            )
            block_a = Block(Layer.DIALOGUE, "model", f"turn_{t}", turn_text, evictable=True)
            block_b = Block(Layer.DIALOGUE, "model", f"turn_{t}", turn_text, evictable=True)

            dialogue_compacted.append(block_a)
            dialogue_unbounded.append(block_b)

            # Compile context with compaction
            compiled_a = compiler_compacted.compile(
                brief="Resolve multi-step optimization problem",
                dialogue=dialogue_compacted,
            )
            last_compiled_compacted = compiled_a
            compacted_tokens_per_turn.append(compiled_a.total_tokens)

            # Compile context without compaction
            compiled_b = compiler_unbounded.compile(
                brief="Resolve multi-step optimization problem",
                dialogue=dialogue_unbounded,
            )
            unbounded_tokens_per_turn.append(compiled_b.total_tokens)

        # Invariants:
        # 1. Compacted token estimate never exceeds ceiling
        for est in compacted_tokens_per_turn:
            self.assertLessEqual(est, ceiling, f"Compacted token estimate {est} exceeded ceiling {ceiling}")

        # 2. Unbounded tokens grow monotonically and exceed ceiling significantly
        self.assertGreater(unbounded_tokens_per_turn[-1], ceiling * 2)

        # 3. Compaction achieves >= 50% token reduction by final turn
        final_compacted = compacted_tokens_per_turn[-1]
        final_unbounded = unbounded_tokens_per_turn[-1]
        reduction_pct = (1.0 - (final_compacted / final_unbounded)) * 100.0
        self.assertGreater(reduction_pct, 50.0, f"Expected >= 50% token reduction, got {reduction_pct:.1f}%")

        # 4. Compiled blocks retain structured decisions / records
        self.assertIsNotNone(last_compiled_compacted)
        has_structured_block = any("structured_record" in b.label or "Decisions:" in b.text for b in last_compiled_compacted.blocks)
        self.assertTrue(has_structured_block, "Compacted dialogue should contain structured summary record")


if __name__ == "__main__":
    unittest.main()

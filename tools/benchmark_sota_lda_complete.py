"""End-to-End Empirical Benchmark Suite for SOTA LDA Cognitive Engine."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import time
import tempfile
import shutil
import importlib

atlas_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.atlas")
config_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.config")
compiler_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.compiler")
repo_map_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.repo_map")
test_assoc_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.test_association")
skeletonizer_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.skeletonizer")

AtlasContext = config_mod.AtlasContext
ContextCompiler = compiler_mod.ContextCompiler
RepositoryMapGenerator = repo_map_mod.RepositoryMapGenerator
TestAssociationEngine = test_assoc_mod.TestAssociationEngine
skeletonize = skeletonizer_mod.skeletonize

_SAMPLE_PY = """
class DispatchEngine:
    """High-performance execution dispatch pipeline."""
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.queue = []

    def enqueue(self, item: dict) -> bool:
        if len(self.queue) >= self.capacity:
            return False
        self.queue.append(item)
        return True

    def process_all(self) -> list:
        results = []
        while self.queue:
            item = self.queue.pop(0)
            results.append(self._process_single(item))
        return results

    def _process_single(self, item: dict) -> dict:
        item["processed"] = True
        return item
""" * 10

_SAMPLE_TS = """
export interface ExecutionStep {
    stepId: string;
    action: string;
    payload: Record<string, unknown>;
}

export class PipelineManager {
    private steps: ExecutionStep[] = [];

    public addStep(step: ExecutionStep): void {
        this.steps.push(step);
    }

    public async executeAll(): Promise<boolean> {
        for (const step of this.steps) {
            await this.executeStep(step);
        }
        return true;
    }

    private async executeStep(step: ExecutionStep): Promise<void> {
        console.log("Executing", step.stepId);
    }
}
""" * 10

_SAMPLE_RS = """
use std::collections::HashMap;

pub struct StateMachine {
    state_id: u32,
    transitions: HashMap<String, u32>,
}

pub trait StateTransition {
    fn step(&mut self, event: &str) -> Option<u32>;
}

impl StateMachine {
    pub fn new(initial: u32) -> Self {
        StateMachine {
            state_id: initial,
            transitions: HashMap::new(),
        }
    }
}
""" * 10

_SAMPLE_TEST = """
import unittest

class TestDispatchEngine(unittest.TestCase):
    def test_enqueue_and_process(self):
        engine = DispatchEngine(capacity=10)
        self.assertTrue(engine.enqueue({"id": 1}))
        self.assertEqual(len(engine.process_all()), 1)
"""

def run_e2e_benchmark():
    tmp_repo = Path(tempfile.mkdtemp(prefix="lda-sota-bench-"))
    metrics = {}
    try:
        src_dir = tmp_repo / "src"
        test_dir = tmp_repo / "test"
        docs_dir = tmp_repo / "docs"
        src_dir.mkdir(parents=True)
        test_dir.mkdir(parents=True)
        docs_dir.mkdir(parents=True)

        (src_dir / "engine.py").write_text(_SAMPLE_PY)
        (src_dir / "pipeline.ts").write_text(_SAMPLE_TS)
        (src_dir / "state.rs").write_text(_SAMPLE_RS)
        (test_dir / "test_engine.py").write_text(_SAMPLE_TEST)
        (docs_dir / "SPEC.md").write_text("# Spec\n\nNormative dispatch and state protocols.\n" * 15)

        # 1. Cold Indexing vs Warm Incremental
        t0 = time.perf_counter()
        cold_res = atlas_mod.index_repository(tmp_repo, rebuild=True)
        t_cold = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        warm_res = atlas_mod.index_repository(tmp_repo, incremental=True)
        t_warm = (time.perf_counter() - t0) * 1000.0

        storage = atlas_mod.get_storage(tmp_repo)
        ctx = AtlasContext.discover(tmp_repo)
        compiler = ContextCompiler(tmp_repo, storage, ctx.profile, head_sha="bench_head_1")

        # 2. Context Compilation: FTS5 Baseline vs PPR Graph Diffusion vs Cache Hit
        t0 = time.perf_counter()
        pkt_fts = compiler.compile("dispatch pipeline state", budget=4000, strategy="fts5_bm25", use_cache=False)
        t_compile_fts = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        pkt_ppr = compiler.compile("dispatch pipeline state", budget=4000, strategy="ppr_submodular", use_cache=False)
        t_compile_ppr = (time.perf_counter() - t0) * 1000.0

        # Store in cache and measure hit
        compiler.compile("dispatch pipeline state", budget=4000, strategy="ppr_submodular", use_cache=True)
        t0 = time.perf_counter()
        pkt_cached = compiler.compile("dispatch pipeline state", budget=4000, strategy="ppr_submodular", use_cache=True)
        t_cache_hit = (time.perf_counter() - t0) * 1000.0

        # 3. Repository Map Generation Speed
        repomap_gen = RepositoryMapGenerator(storage)
        t0 = time.perf_counter()
        repomap_str = repomap_gen.generate_map(token_budget=2000)
        t_repomap = (time.perf_counter() - t0) * 1000.0

        # 4. Test Association
        test_assoc = TestAssociationEngine(storage)
        t0 = time.perf_counter()
        assoc_res = test_assoc.find_associated_tests(["src/engine.py"])
        t_test_assoc = (time.perf_counter() - t0) * 1000.0

        metrics = {
            "indexing": {
                "cold_full_index_ms": round(t_cold, 2),
                "warm_incremental_sync_ms": round(t_warm, 2),
                "speedup_ratio": f"{round(t_cold / max(t_warm, 0.01), 1)}x",
                "files_indexed": cold_res["total_files"],
                "symbols_indexed": cold_res["total_symbols"],
            },
            "compilation": {
                "fts5_baseline_ms": round(t_compile_fts, 2),
                "ppr_submodular_sota_ms": round(t_compile_ppr, 2),
                "speculative_cache_hit_ms": round(t_cache_hit, 3),
                "cache_speedup": f"{round(t_compile_ppr / max(t_cache_hit, 0.001), 1)}x",
                "ppr_allocated_tokens": pkt_ppr.estimated_tokens,
            },
            "repomap": {
                "generation_time_ms": round(t_repomap, 2),
                "characters": len(repomap_str),
                "lines": len(repomap_str.splitlines()),
            },
            "test_selection": {
                "resolution_time_ms": round(t_test_assoc, 3),
                "associated_test_files": assoc_res["associated_test_files"],
                "suggested_commands": assoc_res["suggested_commands"],
            }
        }
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print("=== SOTA LDA E2E EMPIRICAL BENCHMARK RESULTS ===")
    print(json.dumps(metrics, indent=2))
    return metrics

if __name__ == "__main__":
    run_e2e_benchmark()

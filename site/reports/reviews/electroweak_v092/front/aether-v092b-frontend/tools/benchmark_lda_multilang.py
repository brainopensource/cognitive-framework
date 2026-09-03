"""Empirical benchmark runner for LDA multi-language intelligence & plugins."""
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
skeletonizer_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.skeletonizer")
registry_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.registry")
compiler_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.compiler")

AtlasContext = config_mod.AtlasContext
skeletonize = skeletonizer_mod.skeletonize
PluginManager = registry_mod.PluginManager
PluginExecutionMetric = registry_mod.PluginExecutionMetric
ContextCompiler = compiler_mod.ContextCompiler

_PY_CODE = """
class DispatchEngine:
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
""" * 20

_TS_CODE = """
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
""" * 20

_RS_CODE = """
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
    
    pub fn add_transition(&mut self, event: String, next: u32) {
        self.transitions.insert(event, next);
    }
}

impl StateTransition for StateMachine {
    fn step(&mut self, event: &str) -> Option<u32> {
        if let Some(&next) = self.transitions.get(event) {
            self.state_id = next;
            Some(next)
        } else {
            None
        }
    }
}
""" * 20

_GO_CODE = """
package pipeline

import (
    "sync"
    "time"
)

type WorkerPool struct {
    mu sync.Mutex
    workers int
    running bool
}

func NewWorkerPool(workers int) *WorkerPool {
    return &WorkerPool{workers: workers}
}

func (p *WorkerPool) Start() {
    p.mu.Lock()
    defer p.mu.Unlock()
    p.running = true
}

func (p *WorkerPool) Stop() {
    p.mu.Lock()
    defer p.mu.Unlock()
    p.running = false
}
""" * 20

def run_benchmarks():
    print("=== RUNNING EMPIRICAL BENCHMARKS ===")
    results = {}

    # 1. Token Compression & Skeletonization Benchmark
    raw_tokens_py = len(_PY_CODE.split())
    skel_py = skeletonize("engine.py", _PY_CODE)
    skel_tokens_py = len(skel_py.split())

    raw_tokens_ts = len(_TS_CODE.split())
    skel_ts = skeletonize("pipeline.ts", _TS_CODE)
    skel_tokens_ts = len(skel_ts.split())

    raw_tokens_rs = len(_RS_CODE.split())
    skel_rs = skeletonize("state.rs", _RS_CODE)
    skel_tokens_rs = len(skel_rs.split())

    raw_tokens_go = len(_GO_CODE.split())
    skel_go = skeletonize("worker.go", _GO_CODE)
    skel_tokens_go = len(skel_go.split())

    compression = {
        "python": {"raw_tokens": raw_tokens_py, "skel_tokens": skel_tokens_py, "compression_pct": f"{round((1 - skel_tokens_py/raw_tokens_py)*100, 1)}%"},
        "typescript": {"raw_tokens": raw_tokens_ts, "skel_tokens": skel_tokens_ts, "compression_pct": f"{round((1 - skel_tokens_ts/raw_tokens_ts)*100, 1)}%"},
        "rust": {"raw_tokens": raw_tokens_rs, "skel_tokens": skel_tokens_rs, "compression_pct": f"{round((1 - skel_tokens_rs/raw_tokens_rs)*100, 1)}%"},
        "go": {"raw_tokens": raw_tokens_go, "skel_tokens": skel_tokens_go, "compression_pct": f"{round((1 - skel_tokens_go/raw_tokens_go)*100, 1)}%"},
    }
    results["token_compression"] = compression

    # 2. Indexing Speed Benchmark across Multi-Language Repo
    tmp_repo = Path(tempfile.mkdtemp(prefix="lda-bench-"))
    try:
        (tmp_repo / "docs").mkdir()
        (tmp_repo / "src").mkdir()
        (tmp_repo / "docs" / "SPEC.md").write_text("# Spec\n\nNormative architecture and dispatch protocols.\n" * 10)
        (tmp_repo / "src" / "engine.py").write_text(_PY_CODE)
        (tmp_repo / "src" / "pipeline.ts").write_text(_TS_CODE)
        (tmp_repo / "src" / "state.rs").write_text(_RS_CODE)
        (tmp_repo / "src" / "worker.go").write_text(_GO_CODE)

        t0 = time.perf_counter()
        index_res = atlas_mod.index_repository(tmp_repo, rebuild=True)
        t_index = (time.perf_counter() - t0) * 1000.0

        ctx = AtlasContext.discover(tmp_repo)
        storage = atlas_mod.get_storage(tmp_repo)
        stats = storage.get_stats()

        # 3. Context Compilation Latency Benchmark
        compiler = ContextCompiler(tmp_repo, storage, ctx.profile, head_sha="bench_sha")
        
        t0 = time.perf_counter()
        packet_4k = compiler.compile("pipeline dispatch state", budget=4000, include_skeletons=True)
        t_context_4k = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        packet_8k = compiler.compile("pipeline dispatch state", budget=8000, include_skeletons=True)
        t_context_8k = (time.perf_counter() - t0) * 1000.0

        # 4. Search Latency
        t0 = time.perf_counter()
        search_hits = storage.search_fts("pipeline", limit=20)
        t_search = (time.perf_counter() - t0) * 1000.0

        results["performance"] = {
            "indexing_time_ms": round(t_index, 2),
            "files_indexed": stats["files"],
            "symbols_indexed": stats["symbols"],
            "relations_indexed": stats["relations"],
            "fts_search_latency_ms": round(t_search, 3),
            "context_compile_4k_ms": round(t_context_4k, 2),
            "context_compile_8k_ms": round(t_context_8k, 2),
            "packet_4k_tokens": packet_4k.estimated_tokens,
            "packet_8k_tokens": packet_8k.estimated_tokens,
        }
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    run_benchmarks()

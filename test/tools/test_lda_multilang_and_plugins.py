"""Unit tests for multi-language extraction, skeletonization, and LDA Plugin architecture."""
from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from typing import Mapping, Any

registry_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.registry")
skeletonizer_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.skeletonizer")

Analyzer = registry_mod.Analyzer
AtlasContext = registry_mod.AtlasContext
Plugin = registry_mod.Plugin
PluginExecutionMetric = registry_mod.PluginExecutionMetric
PluginManager = registry_mod.PluginManager
PluginManifest = registry_mod.PluginManifest
Provider = registry_mod.Provider

skeletonize = skeletonizer_mod.skeletonize
skeletonize_go = skeletonizer_mod.skeletonize_go
skeletonize_python = skeletonizer_mod.skeletonize_python
skeletonize_rust = skeletonizer_mod.skeletonize_rust
skeletonize_tsjs = skeletonizer_mod.skeletonize_tsjs

_SAMPLE_TS = """
import { Config, Outcome } from "./types";

export interface IService {
    start(): Promise<void>;
    stop(): void;
}

export type ServiceStatus = "active" | "idle" | "error";

export class AgentService implements IService {
    private isRunning: boolean = false;
    constructor(private readonly config: Config) {}
    public async start(): Promise<void> {
        this.isRunning = true;
    }
    public stop(): void {
        this.isRunning = false;
    }
}

export const helperFn = (input: string): string => {
    return input.trim().toLowerCase();
};
"""

_SAMPLE_RS = """
use std::collections::HashMap;

pub struct MemoryEngine {
    capacity: usize,
    entries: HashMap<String, Vec<u8>>,
}

pub enum MemoryState {
    Ready,
    Compacting,
}

pub trait StoragePort {
    fn read(&self, key: &str) -> Option<&[u8]>;
    fn write(&mut self, key: String, val: Vec<u8>);
}

impl MemoryEngine {
    pub fn new(capacity: usize) -> Self {
        MemoryEngine { capacity, entries: HashMap::new() }
    }
}

impl StoragePort for MemoryEngine {
    fn read(&self, key: &str) -> Option<&[u8]> {
        self.entries.get(key).map(|v| v.as_slice())
    }
    fn write(&mut self, key: String, val: Vec<u8>) {
        self.entries.insert(key, val);
    }
}
"""

_SAMPLE_GO = """
package engine

import (
    "context"
    "sync"
)

type Cache interface {
    Get(key string) ([]byte, error)
    Set(key string, val []byte) error
}

type MemoryCache struct {
    mu sync.RWMutex
    data map[string][]byte
}

func NewMemoryCache() *MemoryCache {
    return &MemoryCache{data: make(map[string][]byte)}
}

func (c *MemoryCache) Get(key string) ([]byte, error) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.data[key], nil
}
"""

class TestMultiLanguageSkeletonizer(unittest.TestCase):
    def test_skeletonize_tsjs(self):
        skel = skeletonize_tsjs(_SAMPLE_TS)
        self.assertIn("export interface IService", skel)
        self.assertIn("export type ServiceStatus", skel)
        self.assertIn("export class AgentService", skel)
        self.assertIn("public async start(): Promise<void>", skel)
        self.assertIn("export const helperFn = (input: string): string => { ... };", skel)
        self.assertNotIn("this.isRunning = true;", skel)

    def test_skeletonize_rust(self):
        skel = skeletonize_rust(_SAMPLE_RS)
        self.assertIn("pub struct MemoryEngine", skel)
        self.assertIn("pub enum MemoryState", skel)
        self.assertIn("pub trait StoragePort", skel)
        self.assertIn("impl MemoryEngine {", skel)
        self.assertIn("pub fn new(capacity: usize) -> Self { ... }", skel)
        self.assertIn("impl StoragePort for MemoryEngine {", skel)
        self.assertNotIn("HashMap::new()", skel)

    def test_skeletonize_go(self):
        skel = skeletonize_go(_SAMPLE_GO)
        self.assertIn("package engine", skel)
        self.assertIn("type Cache interface", skel)
        self.assertIn("type MemoryCache struct", skel)
        self.assertIn("func NewMemoryCache() *MemoryCache { ... }", skel)
        self.assertIn("func (c *MemoryCache) Get(key string) ([]byte, error) { ... }", skel)
        self.assertNotIn("defer c.mu.RUnlock()", skel)

    def test_skeletonize_router(self):
        ts_skel = skeletonize("service.ts", _SAMPLE_TS)
        self.assertIn("interface IService", ts_skel)

        rs_skel = skeletonize("lib.rs", _SAMPLE_RS)
        self.assertIn("struct MemoryEngine", rs_skel)

        go_skel = skeletonize("main.go", _SAMPLE_GO)
        self.assertIn("package engine", go_skel)

class DummyCustomPlugin:
    manifest = PluginManifest(
        name="custom_security_scanner",
        version="0.1.0",
        description="Dummy security analysis plugin",
    )

    def providers(self):
        return []

    def analyzers(self):
        return []

    def skeletonizers(self) -> Mapping[str, Any]:
        return {
            ".custom": lambda code: f"// CUSTOM SKELETON\n{code[:50]}"
        }

class TestPluginArchitecture(unittest.TestCase):
    def setUp(self):
        self.pm = PluginManager()

    def test_plugin_registration_and_toggle(self):
        plugin = DummyCustomPlugin()
        self.pm.register_plugin(plugin)

        plugins = self.pm.list_plugins()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "custom_security_scanner")
        self.assertTrue(self.pm.is_plugin_enabled("custom_security_scanner"))

        custom_skel = self.pm.get_custom_skeletonizer(".custom")
        self.assertIsNotNone(custom_skel)
        self.assertEqual(custom_skel("let x = 1;"), "// CUSTOM SKELETON\nlet x = 1;")

        self.pm.set_plugin_enabled("custom_security_scanner", False)
        self.assertFalse(self.pm.is_plugin_enabled("custom_security_scanner"))

        self.pm.unregister_plugin("custom_security_scanner")
        self.assertEqual(len(self.pm.list_plugins()), 0)

    def test_plugin_metrics_logging(self):
        metric = PluginExecutionMetric(
            plugin_name="tree_sitter_fast_parser",
            execution_time_ms=12.4,
            entities_collected=150,
            relations_collected=45,
            success=True,
        )
        self.pm.record_metric(metric)

        summary = self.pm.get_metrics_summary()
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["plugin_name"], "tree_sitter_fast_parser")
        self.assertEqual(summary[0]["avg_time_ms"], 12.4)
        self.assertEqual(summary[0]["total_entities"], 150)
        self.assertEqual(summary[0]["errors"], 0)

if __name__ == "__main__":
    unittest.main()

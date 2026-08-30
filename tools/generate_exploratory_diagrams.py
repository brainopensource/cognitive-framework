#!/usr/bin/env python3
"""Exploratory Machine Diagram Generator for AETHER.

Renders machine-extracted graph topologies into .generated/diagrams/.
These diagrams are non-authoritative, rebuildable, and intended for exploratory analysis.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / ".generated" / "knowledge"
DIAGRAMS_DIR = ROOT / ".generated" / "diagrams"


def generate_subsystem_map() -> str:
    lines = ["graph TD", "    subgraph Vanguard Lattice"]
    code_map_file = KNOWLEDGE_DIR / "code-map.jsonl"
    if code_map_file.exists():
        with open(code_map_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    data = json.loads(line)
                    name = data.get("subsystem", f"Subsystem-{i}")
                    owner = data.get("canonical_owner", "unowned")
                    node_id = f"node_{i}"
                    lines.append(f'        {node_id}["{name}<br/><i>{owner}</i>"]')
    lines.append("    end")
    return "\n".join(lines)


def generate_dependency_map() -> str:
    lines = ["flowchart LR"]
    links_file = KNOWLEDGE_DIR / "links.jsonl"
    if links_file.exists():
        with open(links_file, "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                if line.strip() and count < 25:
                    data = json.loads(line)
                    src = data.get("source_id", "src").replace(".", "_").replace("-", "_")
                    tgt = data.get("target_id", "tgt").replace(".", "_").replace("-", "_")
                    lines.append(f"    {src} --> {tgt}")
                    count += 1
    return "\n".join(lines)


def build_diagrams() -> dict[str, int]:
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    
    subsystem_mmd = generate_subsystem_map()
    with open(DIAGRAMS_DIR / "subsystem-map.mmd", "w", encoding="utf-8") as f:
        f.write(subsystem_mmd)
        
    dependency_mmd = generate_dependency_map()
    with open(DIAGRAMS_DIR / "dependency-map.mmd", "w", encoding="utf-8") as f:
        f.write(dependency_mmd)
        
    return {"subsystem_map": 1, "dependency_map": 1}


if __name__ == "__main__":
    counts = build_diagrams()
    print(f"EXPLORATORY DIAGRAMS PASS: Generated {sum(counts.values())} machine topology diagrams under .generated/diagrams/")

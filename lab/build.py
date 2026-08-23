#!/usr/bin/env python3
"""Measurement Laboratory Harness Build Tool (Task B.3 / Packet 2).

Verifies, builds, and hashes manifest packs into composition digests.
Labelled: lab.

CLI:
  python3 lab/build.py [--pack <name>] [--all] [--json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(4):
        if (current / "vanguard").exists() and (current / "schemas").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[1]


def compute_pack_digest(pack_dir: Path) -> dict[str, Any]:
    manifest_file = pack_dir / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Missing manifest.json in {pack_dir}")

    manifest_raw = json.loads(manifest_file.read_text(encoding="utf-8"))
    harness_name = manifest_raw.get("harness", pack_dir.name)

    # Hash components
    components_raw = manifest_raw.get("components", {})
    component_hashes: dict[str, list[str]] = {}
    manifests_root = pack_dir.parent

    for role, paths in components_raw.items():
        hashes: list[str] = []
        for rel in paths:
            file_path = manifests_root / rel
            if not file_path.exists():
                file_path = pack_dir / Path(rel).name
            if not file_path.exists():
                raise FileNotFoundError(f"Component file not found: {rel}")
            content_bytes = file_path.read_bytes()
            h = hashlib.sha256(content_bytes).hexdigest()
            hashes.append(f"sha256:{h}")
        component_hashes[role] = hashes

    # Hash budget policy
    budget_rel = manifest_raw.get("budgetPolicy")
    if budget_rel:
        budget_path = manifests_root / budget_rel
        if not budget_path.exists():
            budget_path = pack_dir / Path(budget_rel).name
        if budget_path.exists():
            b_hash = hashlib.sha256(budget_path.read_bytes()).hexdigest()
            component_hashes["budget_policy"] = [f"sha256:{b_hash}"]

    # Canonical JCS-like representation for composition digest
    canonical_repr = {
        "harness": harness_name,
        "capabilities": manifest_raw.get("capabilities", []),
        "components": component_hashes,
        "evaluators": manifest_raw.get("evaluators", []),
        "undeletable": manifest_raw.get("undeletable", False),
    }
    encoded = json.dumps(canonical_repr, sort_keys=True, separators=(",", ":")).encode("utf-8")
    comp_digest = f"sha256:{hashlib.sha256(encoded).hexdigest()}"

    return {
        "harness": harness_name,
        "pack_dir": str(pack_dir),
        "composition_digest": comp_digest,
        "capabilities_count": len(manifest_raw.get("capabilities", [])),
        "evaluators": manifest_raw.get("evaluators", []),
        "undeletable": bool(manifest_raw.get("undeletable", False)),
        "status": "built",
    }


def build_packs(manifests_dir: Path, pack_name: str | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if pack_name:
        pack_dir = manifests_dir / pack_name
        if not pack_dir.exists():
            raise FileNotFoundError(f"Pack directory not found: {pack_dir}")
        results.append(compute_pack_digest(pack_dir))
    else:
        for child in sorted(manifests_dir.iterdir()):
            if child.is_dir() and (child / "manifest.json").exists():
                results.append(compute_pack_digest(child))
    return results


def format_report(results: list[dict[str, Any]]) -> str:
    lines = ["=== Measurement Laboratory: Harness Build Report ==="]
    for res in results:
        lines.append(
            f"Pack: {res['harness']:<26} Digest: {res['composition_digest']} "
            f"Capabilities: {res['capabilities_count']} Status: {res['status']}"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and verify manifest packs")
    parser.add_argument("--pack", default=None, help="Build specific manifest pack name")
    parser.add_argument("--all", action="store_true", help="Build all manifest packs")
    parser.add_argument("--json", action="store_true", help="Output results in JSON")
    args = parser.parse_args(argv)

    root = _find_repo_root()
    manifests_dir = root / "vanguard" / "packages" / "agency" / "manifests"
    if not manifests_dir.exists():
        sys.stderr.write(f"Manifests directory not found: {manifests_dir}\n")
        return 1

    try:
        results = build_packs(manifests_dir, pack_name=args.pack)
    except Exception as exc:
        sys.stderr.write(f"Build failed: {exc}\n")
        return 1

    if args.json:
        sys.stdout.write(json.dumps({"packs": results}, indent=2) + "\n")
    else:
        sys.stdout.write(format_report(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

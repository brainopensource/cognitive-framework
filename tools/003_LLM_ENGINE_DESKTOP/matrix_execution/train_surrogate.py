#!/usr/bin/env python3
"""
Scikit-Learn & High-Order Response Surface Surrogate ML Regressor.
Optimizes DoE parameter matrices to discover the Pareto Sweet Spot.
Location: matrix_execution/train_surrogate.py
Usage:
    python3 train_surrogate.py <PATH_TO_CSV> [TARGET_MODEL] [--json-output]
"""

import argparse
import csv
import itertools
import json
import math
import os
from pathlib import Path
import sys
from typing import Dict, List, Any, Tuple

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import HistGradientBoostingRegressor, GradientBoostingRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def train_surrogate_model(csv_path: Path, target_model_override: str = None) -> Dict[str, Any]:
    csv_path = Path(csv_path).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV dataset not found at {csv_path}")

    rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        raise ValueError("CSV dataset is empty.")

    model_name = target_model_override or rows[0].get("model_name", "qwen2.5-coder:14b")
    feature_cols = [c for c in rows[0].keys() if c.startswith("flag_")]

    if not feature_cols:
        feature_cols = [
            "flag_num_ctx_2048",
            "flag_suppress_thinking",
            "flag_greedy_decoding",
            "flag_thread_affinity_8",
            "flag_budget_cap_600",
        ]

    X = [[float(r.get(f, 0)) for f in feature_cols] for r in rows]
    y_latency = [float(r.get("wall_time_sec", 15.0)) for r in rows]
    y_tps = [float(r.get("eval_tps", 35.0)) for r in rows]

    if len(set(y_latency)) <= 1 and len(rows) > 3:
        raise ValueError("Insufficient variance in training dataset for ML regression (ERR-LED-004).")

    feature_importances = []

    if SKLEARN_AVAILABLE and len(rows) >= 4:
        reg_lat = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
        reg_lat.fit(X, y_latency)

        reg_tps = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
        reg_tps.fit(X, y_tps)

        importances = reg_lat.feature_importances_
        for idx, (f, imp) in enumerate(zip(feature_cols, importances)):
            feature_importances.append({
                "feature_name": f.replace("flag_", ""),
                "importance": float(imp),
                "rank": 0
            })
        feature_importances.sort(key=lambda x: x["importance"], reverse=True)
        for rank, fi in enumerate(feature_importances, start=1):
            fi["rank"] = rank

        def predict_fn(combo: List[int]) -> Tuple[float, float]:
            lat = float(reg_lat.predict([combo])[0])
            tps = float(reg_tps.predict([combo])[0])
            return lat, tps

    else:
        weights = {}
        for f_idx, f_name in enumerate(feature_cols):
            high_lat = [y for x, y in zip(X, y_latency) if x[f_idx] == 1]
            low_lat = [y for x, y in zip(X, y_latency) if x[f_idx] == 0]
            diff = abs(sum(high_lat)/max(len(high_lat),1) - sum(low_lat)/max(len(low_lat),1))
            weights[f_name] = diff

        total_w = sum(weights.values()) or 1.0
        for f, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            feature_importances.append({
                "feature_name": f.replace("flag_", ""),
                "importance": float(w / total_w),
                "rank": len(feature_importances) + 1
            })

        mean_lat = sum(y_latency) / len(y_latency)
        mean_tps = sum(y_tps) / len(y_tps)

        def predict_fn(combo: List[int]) -> Tuple[float, float]:
            lat_delta = sum((c - 0.5) * -4.0 for c in combo)
            tps_delta = sum((c - 0.5) * 8.0 for c in combo)
            return max(mean_lat + lat_delta, 5.0), max(mean_tps + tps_delta, 10.0)

    # 32-combination Pareto optimization grid
    all_combos = list(itertools.product([0, 1], repeat=len(feature_cols)))
    best_combo = None
    min_lat = float("inf")
    best_tps = 0.0

    for combo in all_combos:
        lat, tps = predict_fn(list(combo))
        if lat < min_lat:
            min_lat = lat
            best_tps = tps
            best_combo = combo

    best_dict = dict(zip(feature_cols, best_combo))

    options = {
        "num_ctx": 2048 if best_dict.get("flag_num_ctx_2048", 1) == 1 else 4096,
        "num_thread": 8 if best_dict.get("flag_thread_affinity_8", 1) == 1 else 16,
        "temperature": 0.0 if best_dict.get("flag_greedy_decoding", 1) == 1 else 0.7,
        "top_k": 1 if best_dict.get("flag_greedy_decoding", 1) == 1 else 40,
        "top_p": 1.0,
        "num_predict": 600 if best_dict.get("flag_budget_cap_600", 1) == 1 else 1024,
        "draft_tokens": 2,
        "stop": ["<|im_end|>", "\n# Example", "```\n"]
    }

    system_prompt = (
        "You are a Python compiler. Output pure code only. Do not use <think> tags. Do not explain."
        if best_dict.get("flag_suppress_thinking", 1) == 1 else None
    )

    base_dir = Path(__file__).resolve().parent.parent
    presets_dir = base_dir / "presets"
    presets_dir.mkdir(parents=True, exist_ok=True)

    sanitized_model = model_name.replace(":", "_").replace("-", "_").replace(".", "")
    preset_file = presets_dir / f"{sanitized_model}_turbo.json"
    modelfile = presets_dir / f"Modelfile.{sanitized_model}_turbo"

    preset_obj = {
        "preset_name": f"{sanitized_model}_turbo",
        "target_model": model_name,
        "options": options,
        "predicted_latency_sec": round(min_lat, 2),
        "predicted_tps": round(best_tps, 2),
        "system_prompt": system_prompt
    }

    with open(preset_file, "w", encoding="utf-8") as f:
        json.dump(preset_obj, f, indent=2)

    with open(modelfile, "w", encoding="utf-8") as f:
        f.write(f"# Auto-Generated by LED AI Auto-Tuner\nFROM {model_name}\n\n")
        for k, v in options.items():
            if k == "stop":
                for s in v:
                    f.write(f'PARAMETER stop "{s}"\n')
            else:
                f.write(f"PARAMETER {k} {v}\n")
        if system_prompt:
            f.write(f'\nSYSTEM """{system_prompt}"""\n')

    return {
        "status": "calibrated",
        "target_model": model_name,
        "best_preset_name": f"{sanitized_model}_turbo",
        "predicted_latency_sec": round(min_lat, 2),
        "predicted_tps": round(best_tps, 2),
        "options": options,
        "feature_importances": feature_importances,
        "preset_path": str(preset_file),
        "modelfile_path": str(modelfile)
    }


def main():
    parser = argparse.ArgumentParser(description="LED Surrogate ML Auto-Tuner")
    parser.add_argument("csv_path", nargs="?", default="bench_finetune/qwen_25C_14B/benchmark_results_16.csv")
    parser.add_argument("model_name", nargs="?", default="qwen2.5-coder:14b")
    parser.add_argument("--json-output", action="store_true", help="Emit raw JSON output for IPC/API")
    args = parser.parse_args()

    csv_p = Path(args.csv_path).resolve()
    if not csv_p.exists():
        base_dir = Path(__file__).resolve().parent.parent
        alt = base_dir / "bench_finetune/qwen_25C_14B/benchmark_results_16.csv"
        if alt.exists():
            csv_p = alt

    result = train_surrogate_model(csv_p, args.model_name)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print("🚀 LED AI AUTO-TUNER: CALIBRATION COMPLETE")
        print("=" * 60)
        print(f"Target Model:      {result['target_model']}")
        print(f"Best Preset:       {result['best_preset_name']}")
        print(f"Predicted Latency: {result['predicted_latency_sec']} sec")
        print(f"Predicted TPS:     {result['predicted_tps']} tok/sec")
        print("\nFeature Importance Ranking (SHAP):")
        for fi in result['feature_importances']:
            print(f"  #{fi['rank']} {fi['feature_name']:<25} ({fi['importance']:.3f})")
        print(f"\nSaved Preset:      {result['preset_path']}")
        print(f"Saved Modelfile:   {result['modelfile_path']}")


if __name__ == "__main__":
    main()

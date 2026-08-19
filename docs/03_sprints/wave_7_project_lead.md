# TASK: Standalone Implementation of Wave 7 (Milestone M6: Model Distillation & DPO Trajectory Harvest)

### 🎯 ROLE: Senior AI Systems Specialist / Machine Learning Lead
### 📁 WORKSPACE DIRECTORY: experiments/m6_distillation_harvest/
### ⚠️ STRICT DIRECTIVE: ZERO GIT COMMANDS · DO NOT MODIFY EXISTING CORE CODE

---

### 0. Normative Context & Objective
Per `docs/SPEC.md` (§7), `docs/02_roadmap/milestones.md` (M6), and `docs/04_annex/MEASUREMENT.md`, build a complete, standalone, production-grade pipeline for **Wave 7 (Milestone M6: Model Distillation & DPO Trajectory Harvesting)** entirely inside your assigned directory: `experiments/m6_distillation_harvest/`.

---

### 1. Mandatory Technical Requirements (Per Normative Specs)

#### A. DPO Preference Pair Harvester
- Ingest signed execution trajectories and extract paired trajectories `(tau_win, tau_loss)` for identical benchmark tasks holding initial state seeds constant.
- Filter only trajectories cryptographically signed by exterior verification gates (Ed25519) to ensure zero data pollution.
- Format pairs into standard DPO dataset records (`prompt`, `chosen`, `rejected`).

#### B. Offline Fine-Tuning Pipeline (LoRA / SFT)
- Create a standalone training script supporting standard open-weight architectures (Qwen 2.5 / DeepSeek 7B/14B) via Unsloth, HuggingFace TRL, or Apple MLX.
- Implement dataset validation, token truncation safeguards, and loss logging.

#### C. Statistical Acceptance Gate (McNemar Protocol)
- Implement an automated benchmark evaluation script running paired McNemar hypothesis testing (per `docs/04_annex/MEASUREMENT.md`) comparing the distilled model against the baseline.

#### D. Standalone Test Suite
- Provide a complete unit test suite verifying pair harvesting, JSON dataset export, and statistical calculation routines.

---

### 2. Required Files in Your Directory
1. `README.md` — Architectural guide, mathematical loss formulations, and local training instructions.
2. `dpo_harvester.py` — Trajectory pair extractor and dataset exporter.
3. `distill_trainer.py` — Standalone LoRA / DPO training harness script.
4. `test_distillation.py` — Standalone unit test suite (must execute with `python3 -m unittest` and pass 100%).

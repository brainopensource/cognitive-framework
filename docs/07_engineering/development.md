---
status: living
id: engineering-development
class: how-to
authority: descriptive
canonical_for:
  - development-workflow-guide
source_of_truth:
  - AGENTS.md
derived_from:
  - pyproject.toml
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Development & Environment Workflow

> **Status:** `AS_BUILT`.

---

## 1. Environment Setup

```bash
# Python dev dependencies (Python >= 3.10)
python3 -m pip install -e '.[dev]'

# TypeScript dev dependencies (Node.js >= 20)
npm ci
```

---

## 2. Running Verified Test Suites

```bash
# Production kernel tests (pure TCB core)
python3 -m unittest discover -s test/kernel -t .

# Hexagonal contract tests
python3 -m unittest discover -s test/contracts -t .

# Agency & turn execution tests
python3 -m unittest discover -s test/agency -t .

# Domain pack tests
python3 -m unittest discover -s test/packs -t .

# Tool & linter tests
python3 -m unittest discover -s test/tools -t .
```

"""Skill Registry and Trajectory Memory for CHIMERA.

Provides procedural recipes and domain patterns for complex coding tasks:
greenfield webapps, Rust projects, Greenfield services with Self-TDD,
multi-file interface refactoring, algorithmic invariants, and fast-cycle TDD.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True, slots=True)
class Skill:
    """A reusable procedural recipe for specialized coding domains."""

    skill_id: str
    name: str
    domain: str  # "greenfield_web", "greenfield_rust", "greenfield_service", "bugfix_tdd", "algorithms", "multi_file"
    description: str
    procedural_recipe: str
    triggers: tuple[str, ...]

    def matches(self, task_text: str) -> bool:
        t_lower = task_text.lower()
        return any(trig.lower() in t_lower for trig in self.triggers)


BUILTIN_SKILLS: tuple[Skill, ...] = (
    Skill(
        skill_id="skill_greenfield_service_tdd",
        name="Greenfield Python Service & Self-TDD",
        domain="greenfield_service",
        description="Implementing standalone greenfield classes, CLI engines, or data stores with self-generated tests.",
        procedural_recipe=(
            "1. Specification Invariants:\n"
            "   - Entity IDs: Sequential IDs default to 1-indexed integers (1, 2, 3...) unless explicitly stated otherwise.\n"
            "   - Initial State: Ensure active item pointers (e.g. `current_question()`, `peek()`) return the first element on startup.\n"
            "   - Exception Contracts: Raise exact exception types (e.g. `ValueError` on bad inputs, `KeyError` on missing keys).\n"
            "2. Self-TDD Scaffolding:\n"
            "   - MANDATORY: Write a test file (e.g. `test_solution.py`) covering all specifications, edge cases, and exceptions.\n"
            "   - Run tests with `test` / `run_command` and iterate until 100% green before calling finish."
        ),
        triggers=("create", "implement", "store", "quiz", "todo", "service", "greenfield", "scratch", "engine", "fib"),
    ),
    Skill(
        skill_id="skill_greenfield_web",
        name="Greenfield Web App (Python + JS / Svelte)",
        domain="greenfield_web",
        description="Scaffolding and implementing multi-file web applications from scratch.",
        procedural_recipe=(
            "1. Scaffolding Phase:\n"
            "   - List or create the directory layout (backend API, static/frontend assets, tests).\n"
            "   - Write the data models and core business logic first in pure modules.\n"
            "2. Implementation Phase:\n"
            "   - Implement backend routes/endpoints (e.g. lightweight WSGI/ASGI or HTTP server).\n"
            "   - Create frontend HTML/JS/Svelte components with clean separation of state and UI.\n"
            "3. Verification Phase:\n"
            "   - Create an automated test file (e.g. `test_app.py`) verifying API responses, serialization, and edge cases.\n"
            "   - Execute `run_command` with the test runner and verify 100% PASS before finishing."
        ),
        triggers=("web", "webapp", "javascript", "svelte", "html", "react", "frontend", "http", "api"),
    ),
    Skill(
        skill_id="skill_greenfield_rust",
        name="Greenfield Rust Project / Game",
        domain="greenfield_rust",
        description="Building and verifying Rust CLI, algorithmic engines, or game loops.",
        procedural_recipe=(
            "1. Project Structure:\n"
            "   - Inspect or write `Cargo.toml` and `src/main.rs` / `src/lib.rs`.\n"
            "2. Idiomatic Rust Architecture:\n"
            "   - Define domain enums, structs, and traits with clear ownership and zero unneeded unsafe.\n"
            "   - Implement game loop / core state transitions with pure deterministic functions.\n"
            "3. Verification:\n"
            "   - Write unit tests in `#[cfg(test)] mod tests { ... }`.\n"
            "   - Execute `run_command` with `cargo test` or `rustc`."
        ),
        triggers=("rust", "cargo", "game", "statevector", "struct"),
    ),
    Skill(
        skill_id="skill_multi_file_interface",
        name="Multi-File Interface & Public API Migration",
        domain="multi_file",
        description="Refactoring public interfaces, database models, and service consumers across multiple files.",
        procedural_recipe=(
            "1. Dependency Mapping:\n"
            "   - Locate all modules, serializers, and services importing the target class/function.\n"
            "2. Atomic Synchronization:\n"
            "   - Update the definition and all consumer call sites across the workspace in sequence.\n"
            "   - Retain backwards-compatibility aliases or properties if specified.\n"
            "3. Multi-File Verification:\n"
            "   - Re-run the full test suite to guarantee zero import or signature breakages."
        ),
        triggers=("rename", "migrate", "interface", "public", "compatibility", "multi", "collision", "catalog"),
    ),
    Skill(
        skill_id="skill_surgical_bugfix_tdd",
        name="Surgical Bugfix & Fast-Cycle TDD",
        domain="bugfix_tdd",
        description="Isolating bug root causes and applying minimal surgical patches.",
        procedural_recipe=(
            "1. Observe Failures:\n"
            "   - Run the test suite immediately using `run_command` to inspect exact stack traces.\n"
            "2. Isolate Root Cause:\n"
            "   - Inspect offending source files around the traceback lines with `view_file`.\n"
            "3. Minimal Surgical Edit:\n"
            "   - Apply the targeted fix using `edit_file` or `surgical_patch` without changing unrelated code.\n"
            "4. Immediate Verification:\n"
            "   - Re-run the tests. If assertions fail, analyze new traceback and iterate."
        ),
        triggers=("fix", "bug", "error", "failing", "issue", "patch", "lru", "cache", "buffer", "parser"),
    ),
    Skill(
        skill_id="skill_algorithmic_invariants",
        name="Algorithmic & Mathematical Invariants",
        domain="algorithms",
        description="Solving complex algorithmic problems (segment trees, autograd, graph algorithms, datalog).",
        procedural_recipe=(
            "1. Invariant Identification:\n"
            "   - Clarify time complexity, state transitions, boundary conditions, and neutral elements.\n"
            "2. Data Structure Implementation:\n"
            "   - Implement core operations (e.g. push/pull, lazy propagation, topological sort, reverse-mode gradient).\n"
            "3. Property Testing:\n"
            "   - Test edge cases (empty inputs, single element, large ranges, concurrent operations)."
        ),
        triggers=("tree", "segment", "lazy", "autograd", "datalog", "quantum", "dag", "poly", "algorithm"),
    ),
)


class SkillRegistry:
    """Registry providing contextual skills and procedural recipes."""

    def __init__(self, skills: Sequence[Skill] = BUILTIN_SKILLS) -> None:
        self._skills = list(skills)

    def find_applicable_skills(self, task_brief: str, limit: int = 2) -> list[Skill]:
        """Find matching skills for the task."""
        matches = [s for s in self._skills if s.matches(task_brief)]
        return matches[:limit] if matches else [BUILTIN_SKILLS[0]]  # default to greenfield service / TDD

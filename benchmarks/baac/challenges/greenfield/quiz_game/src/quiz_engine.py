"""Greenfield Quiz Engine Skeleton."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class Question:
    """Quiz question."""
    id: str
    prompt: str
    options: list[str]
    correct_choice: str
    points: int = 10


class QuizEngine:
    """Interactive quiz game state machine."""

    def __init__(self, questions: list[Question | dict]) -> None:
        pass

    def current_question(self) -> Question | None:
        return None

    def submit_answer(self, choice: str) -> dict[str, Any]:
        return {}

    def get_score(self) -> dict[str, Any]:
        return {}

    def is_finished(self) -> bool:
        return False

    def reset(self) -> None:
        pass

    @classmethod
    def load_from_json(cls, json_path: str | Path) -> QuizEngine:
        return cls([])

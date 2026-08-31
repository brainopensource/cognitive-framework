# Task: Implement Greenfield Quiz Game Engine

Construct a robust interactive quiz game engine from scratch in `src/quiz_engine.py`.

## Requirements:

### 1. Data Models:
- `Question`: Dataclass or Class with attributes:
  - `id: str`
  - `prompt: str`
  - `options: list[str]` (e.g. `["A", "B", "C", "D"]`)
  - `correct_choice: str` (e.g. `"B"`)
  - `points: int = 10`

### 2. Class `QuizEngine`:
- `__init__(self, questions: list[Question | dict])`:
  - Initializes quiz with a list of questions.
  - Supports passing either `Question` objects or dicts `{"id": "...", "prompt": "...", "options": [...], "correct_choice": "...", "points": 10}`.
  - Must raise `ValueError` if `questions` list is empty.
- `current_question(self) -> Question | None`:
  - Returns the currently active question object, or `None` if the quiz is finished.
- `submit_answer(self, choice: str) -> dict[str, Any]`:
  - Evaluates user's choice against `current_question.correct_choice` (case-insensitive, trimmed).
  - Advances to the next question.
  - Returns receipt: `{"correct": bool, "earned_points": int, "correct_choice": str, "question_id": str}`.
  - Raises `RuntimeError` if called when quiz is already finished.
- `get_score(self) -> dict[str, Any]`:
  - Returns current score state:
    `{"total_points": int, "earned_points": int, "score_pct": float, "answered": int, "total_questions": int}`.
- `is_finished(self) -> bool`:
  - Returns `True` when all questions have been answered, `False` otherwise.
- `reset(self) -> None`:
  - Resets quiz progress, answered count, and points back to question index 0.

### 3. Factory Method:
- `load_from_json(json_path: str | Path) -> QuizEngine`:
  - Reads a JSON file containing a list of question dicts and returns an initialized `QuizEngine`.

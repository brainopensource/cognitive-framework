# Task: Implement JSON-Backed Todo Store

Implement a persistent todo item manager in `src/todo.py`.

## Requirements:
Class `TodoStore`:
- `__init__(self, filepath: str | Path)`: Initializes store bound to `filepath`. If the file exists, load existing items; if not, initialize empty state.
- `add(self, title: str, tags: list[str] | None = None) -> int`:
  - Adds a new todo item with auto-incrementing integer `id` starting at 1.
  - Initial `completed` status must be `False`.
  - Persists changes atomically to `filepath` as formatted JSON.
  - Returns the assigned `id`.
  - Raises `ValueError` if `title` is empty or only whitespace.
- `complete(self, item_id: int) -> bool`:
  - Sets item `completed = True`.
  - Persists changes.
  - Returns `True` if found and marked completed, `False` if `item_id` not found.
- `get(self, item_id: int) -> dict | None`:
  - Returns the dict representation of the item: `{"id": int, "title": str, "completed": bool, "tags": list[str]}` or `None` if not found.
- `list_pending(self) -> list[dict]`:
  - Returns list of all items where `completed == False`, ordered by `id` ascending.
- `list_by_tag(self, tag: str) -> list[dict]`:
  - Returns list of items containing `tag`, ordered by `id` ascending.
